#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The server module is responsible for keeping track of the connections,
and send the messages to the parser.

"""
import threading
import select
import socket
import Queue
import logging
import random
import sys

from parser import Parser
from tcp_client import TCPClient
from channel import Channel


class TCPServer(threading.Thread):
    """
    Connections that we expect to read from will be kept in the 
    self.inputs list, whereas the ones we expect to write to 
    will be kept in self.outputs.
    
    """

    def __init__(self, port=10000, ping_time=150, chan="#lobby", hostname="ip.voice.org"):
        """Set up the instance variables."""
        super(TCPServer, self).__init__()
        self.tcp_server = None
        self.upd_server = None
        self.port = port
        self.tcp_connections = {}
        self.inputs = []
        self.outputs = []
        self.ping_time = ping_time
        self.default_channel = chan
        self.hostname = hostname
        self.r = []
        self.w = []
        self.e = []

    def run(self):
        """Launch the server."""
        self.tcp_server = self.setup_tcp_server(self.port)
        self.inputs.append(self.tcp_server)
        self.handle_connections()

    def setup_tcp_server(self, port):
        """
        Creates a non-blocking TCP socket, binds it to the specified port.
        
        """
        # 0.0.0.0 (or an empty string) means that we accept all
        # incoming connections (if an IP is typed, it'll restrict it
        # to connections from said IP).
        address = ('0.0.0.0', port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        logging.debug("Starting tcp server on %s on port %s" % address)
        server.bind(address)
        server.listen(5)
        return server

    def handle_connections(self):
        """
        Handle the readable, writable and exceptional sockets by using
        the systems select() function, and taking care of the sockets 
        appropriately thereafter.
        
        """
        already_waiting = False
        while self.inputs:
            if not already_waiting:
                logging.debug("Waiting for sockets to be ready...")
            self.r, self.w, self.e = select.select(self.inputs, self.outputs, self.inputs, 1)
            already_waiting = False
            if not (self.r or self.w or self.e):
                self.ping()
                already_waiting = True
                continue
            self.readables(self.r)
            self.writeables(self.w)
            self.exceptionals(self.e)

    def readables(self, readables):
        """
        Handle the readable sockets. If the server socket is readable, it is
        ready for a new connection.
        
        If it is a client socket, then it is checked if there is data available
        from the socket, and add it to the message queue and self.outputs list.
        
        If no data is received from a socket, it is considered closed, and is
        therefore removed.
        
        """
        for sock in readables:
            if sock is self.tcp_server:
                # We're ready to accept a connection
                connection, address = sock.accept()
                logging.debug("New connection from %s:%s" % address)
                client = TCPClient(self, connection, address)
                self.tcp_connections[connection] = client
                self.inputs.append(connection)
                logging.debug(connection.getaddrinfo())
            else:
                data = sock.recv(1024)
                if data:
                    for d in data.split("\r\n"):
                        if d == "":
                            continue
                        logging.debug(
                            "Received data '%s' from %s" % (
                                d, sock.getpeername()
                            )
                        )
                        Parser(self, sock, d)
                else:
                    self.remove_client(sock)

    def writeables(self, writeables):
        """Write the queued messages to the sockets that are writeable."""
        for sock in writeables:
            client = self.tcp_connections[sock]
            try:
                msg = client.get_message()
            except Queue.Empty:
                logging.debug(
                    "No messages queued for %s" % (sock.getpeername(), )
                )
                self.outputs.remove(sock)
            else:
                logging.debug("Sending '%s' to %s" % (msg, sock.getpeername()))
                sock.send(msg)

    def exceptionals(self, exceptionals):
        """Handle if there is an error in the socket by removing it."""
        for sock in exceptionals:
            logging.debug(
                "Handling exceptional condition for %s" % sock.getpeername()
            )
            client = self.tcp_connections[sock]
            if client in self.outputs:
                self.outputs.remove(client)
            self.inputs.remove(client)

    def queue_message(self, data, sock):
        """Put a message in the queue for a client."""
        client = self.tcp_connections[sock]
        client.add_message(data)
        if sock not in self.outputs:
            self.outputs.append(sock)

    def queue_message_to_channel(self, data, chan, sender):
        """Put a message in the queue of all the clients in a channel."""
        if chan in Channel.channels:
            for user in Channel.channels[chan].users_in_room:
                sock = user.client.sock
                if sock is not sender:
                    self.queue_message(data, sock)

    def queue_message_to_client(self, data, recipient, sender):
        """
        Put the message in the output queue for all the other connections,
        than the server and the sender.
        
        """
        for sock, client in self.tcp_connections.iteritems():
            if client.user.nickname.lower() == recipient.lower():
                self.queue_message(data, sock)

    def ping(self):
        """
        Periodically check if a client is still connected, by sending
        out a ping with a random number, and then expect the client
        to respond with a pong and the same number.
        
        """
        for sock in self.tcp_connections.keys():
            client = self.tcp_connections[sock]
            exceeded_ping = self.ping_time + (self.ping_time / 3)
            if client.time_since_pinged() >= exceeded_ping:
                client.ready_for_ping = False
                logging.debug(
                    "No ping received for %s" % (sock.getpeername(), )
                )
                self.remove_client(sock)
            elif client.ready_for_ping and client.time_since_pinged() >= self.ping_time:
                random_number = random.randint(100000000, 999999999)
                client.ping(random_number)
                logging.debug(
                    "Sending 'PING: %s' to %s" % (
                        random_number, sock.getpeername()
                    )
                )
                sock.send("PING: %s\r\n" % random_number)

    def remove_client(self, sock):
        """Close the connection to a client, and remove it entirely."""
        logging.debug("Closing connection to %s" % (sock.getpeername(), ))
        sock.close()
        client = self.tcp_connections[sock]
        if client.user is not None:
            logging.debug("Cleaning up after user '%s'" % client.user.nickname)
            client.user.clean_up_user()
        if sock in self.outputs:
            self.outputs.remove(sock)
        # If a socket gets cleaned up in readables, but is also found in the
        # writeables list, then it'll cause an error, so we make sure it's
        # removed.
        if sock in self.w:
            self.w.remove(sock)
        self.inputs.remove(sock)
        del self.tcp_connections[sock]

    def close(self):
        """Close all open connections, including the servers own socket."""
        logging.debug("Closing all connections...")
        for sock, client in self.tcp_connections.items():
            client.close()
            if client.user is not None:
                client.user.clean_up_user()
        if self.tcp_server is not None:
            self.tcp_server.close()
        sys.exit(0)

