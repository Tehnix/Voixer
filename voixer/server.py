#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The server module is responsible for keeping track of the connections,
and send the messages to the parser.

"""
import select
import socket
import sys
import Queue
import logging

from parser import Parser
from client import Client


class Server(object):
    """
    Connections that we expect to read from will be kept in the 
    self.inputs list, whereas the ones we expect to write to 
    will be kept in self.outputs.
    
    """
    
    def __init__(self, port=10000):
        """Set up the instance variables."""
        super(Server, self).__init__()
        self.server = None
        self.port = port
        self.connections = {}
        self.inputs = []
        self.outputs = []
    
    def run(self):
        """Launch the server."""
        self.server = self.setup_socket(self.port)
        self.inputs.append(self.server)
        self.handle_connections()
    
    def setup_socket(self, port):
        """
        Creates a non-blocking TCP socket, binds it to localhost, 
        and the specified port.
        
        """
        address = ('localhost', port)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        logging.debug("Starting server on %s on port %s" % address)
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
                logging.debug("Wating for sockets to be ready...")
            r, w, e = select.select(self.inputs, self.outputs, self.inputs, 1)
            already_waiting = False
            if not (r or w or e):
                # TODO: check pings here !
                already_waiting = True
                continue
            self.readables(r)
            self.writeables(w)
            self.exceptionals(e)
    
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
            if sock is self.server:
                # We're ready to accept a connection
                connection, address = sock.accept()
                logging.debug("New connection from %s:%s" % address)
                client = Client(connection, address)
                self.connections[connection] = client
                self.inputs.append(connection)
            else:
                data = sock.recv(1024)
                if data:
                    logging.debug("Received data '%s' from %s" % (data, sock.getpeername()))
                    Parser(self, sock, data)
                else:
                    logging.debug("Closing connection to %s" % (sock.getpeername(), ))
                    if sock in self.outputs:
                        self.outputs.remove(sock)
                    self.inputs.remove(sock)
                    del self.connections[sock]
                    sock.close()
    
    def writeables(self, writeables):
        """Write the queued messages to the sockets that are writeable."""
        for sock in writeables:
            client = self.connections[sock]
            try:
                msg = client.get_message()
            except Queue.Empty:
                logging.debug("No messages queued for %s" % (sock.getpeername(), ))
                self.outputs.remove(sock)
            else:
                logging.debug("Sending '%s' to %s" % (msg, sock.getpeername()))
                sock.send(msg)
    
    def exceptionals(self, exceptionals):
        """Handle if there is an error in the socket by removing it."""
        for sock in exceptionals:
            logging.debug("Handling exceptional condition for %s" % sock.getpeername())
            client = self.connections[sock]
            if client in self.outputs:
                self.outputs.remove(client)
            self.inputs.remove(client)
    
    def queue_message(self, data, recipient, sender):
        """
        Put the message in the output queue for all the other connections,
        than the server and the sender.
        
        """
        for sock in self.inputs:
            client = self.connections[sock]
            if sock is not (sender or self.server) and sock in self.connections:
                client.add_message(data)
                if sock not in self.outputs:
                    self.outputs.append(sock)
    
    def close(self):
        """Close all open connections, including the servers own socket."""
        logging.debug("Closing all connections...")
        for sock, client in self.connections.iteritems():
            client.close()
                