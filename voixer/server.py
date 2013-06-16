#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The server object.

"""
import select
import socket
import sys
import Queue

from client import Client


class Server(object):
    """
    Connections that we expect to read from will be kept in the 
    self.inputs list, whereas the ones we expect to write to 
    will be kept in self.outputs.
    
    """
    
    def __init__(self, port=10000):
        """Set up the instance variables, and the servers own socket connection."""
        super(Server, self).__init__()
        self.sock = self.setup_socket(port)
        self.inputs = [self.sock]
        self.outputs = []
    
    def setup_socket(self, port):
        """
        Creates a non-blocking TCP socket, binds it to localhost, 
        and the specified port.
        
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setblocking(0)
        server.bind(('localhost', port))
        return server
        
    def handle_connections(self):
        """
        Handle the readable, writable and exceptional sockets by using
        the systems select() function, and taking care of the sockets 
        appropriately thereafter.
        
        """
        while self.inputs:
            r, w, e = select.select(self.inputs, self.outputs, self.inputs)
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
            if sock is self.sock:
                # We're ready to accept a connection
                connection, address = sock.accept()
                client = Client(sock.accept())
                self.inputs.append(client)
            else:
                client = self.get_client(sock)
                data = sock.recv(1024)
                if data:
                    client.add_message(data)
                    if client not in self.outputs:
                        self.outputs.append(client)
                else:
                    if client in self.outputs:
                        self.outputs.remove(client)
                    self.inputs.remove(client)
                    client.close()
    
    def writeables(self, writeables):
        """Write the queued messages to the sockets that are writeable."""
        for sock in writeables:
            client = self.get_client(sock)
            try:
                msg = client.get_message()
            except Queue.Empty:
                self.outputs.remove(sock)
            else:
                client.send(msg)
    
    def exceptionals(self, exceptionals):
        """Handle if there is an error in the socket by removing it."""
        for sock in exceptionals:
            client = self.get_client(sock)
            if client in self.outputs:
                self.outputs.remove(client)
            self.inputs.remove(client)
    
    def get_client(self, sock):
        """
        Get the client object by comparing it to the socket. A client will
        always be found in the self.inputs list, if it's before it's removed.
        
        """
        for client in self.inputs:
            if client is sock:
                return client
    
    def close(self):
        for client in self.inputs:
            client.close()
                