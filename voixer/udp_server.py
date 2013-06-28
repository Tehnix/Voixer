#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The UDP server keeps track of all UDP connections.

"""
import threading
import socket
import logging

from parser import Parser


class UDPServer(threading.Thread):
    """UDP Server."""

    def __init__(self, port=10001):
        """Set up the instance variables."""
        super(UDPServer, self).__init__()
        self.udp_server = None
        self.port = port

    def run(self):
        """Initiate the UDP server."""
        self.udp_server = self.setup_udp_server(self.port)
        self.handle_connections()

    def setup_udp_server(self, port):
        """
        Creates a blocking UDP socket, binds it to the specified port.

        """
        # 0.0.0.0 (or an empty string) means that we accept all
        # incoming connections (if an IP is typed, it'll restrict it
        # to connections from said IP).
        address = ('0.0.0.0', port)
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Starting udp server on %s on port %s" % address)
        server.bind(address)
        return server

    def handle_connections(self):
        """Handle the UDP connections."""
        while True:
            data, address = self.udp_server.recvfrom(2048)
            logging.debug(">>> Sender: %s. Msg: %s." % (address, data))

    def close(self):
        """Close down the UDP server."""
        if self.udp_server is not None:
            self.udp_server.close()