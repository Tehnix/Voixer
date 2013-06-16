#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The client object holds the connection information, and methods.

"""

import Queue


class Client(object):
    """Client object."""
    
    def __init__(self, connection, address):
        """
        Set up the instance variables, and create a message queue,
        along with setting the socket to non blocking.
        
        """
        super(Client, self).__init__()
        self.user = None
        self.address = address
        self.sock = connection
        self.message_queue = Queue.Queue()
        self.sock.setblocking(0)
        self.connection_accepted = False
    
    def add_message(self, data):
        """Add a message to the queue."""
        return self.message_queue.put(data)
        
    def get_message(self):
        """Get the next message out from the queue."""
        return self.message_queue.get_nowait()
    
    def close(self):
        """Wrapper for the sockets close function."""
        return self.sock.close()

