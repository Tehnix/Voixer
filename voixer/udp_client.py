#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The udp client object holds the connection information, and methods
of the client connected via UDP.

"""


class UDPClient(object):
    """TCPClient object."""
    
    def __init__(self, server, tcp_client, connection, address):
        """
        Set up the instance variables, and create a message queue,
        along with setting the socket to non blocking.
        
        """
        super(UDPClient, self).__init__()
        self.user = None
        self.address = address
        self.sock = connection
        self.server = server
        self.tcp_client = tcp_client
        self.talk = None

    def close(self):
        """Close down the UDP client object."""
        if self.talk is not None:
            self.server.queue_message(
                "TALK %s: END" % self.talk.session_key, self.tcp_client.sock
            )
        self.sock.close()