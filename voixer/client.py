#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The client object holds the connection information, and methods.

"""

import Queue
import time
import logging

from channel import Channel


class Client(object):
    """Client object."""
    
    def __init__(self, server, connection, address):
        """
        Set up the instance variables, and create a message queue,
        along with setting the socket to non blocking.
        
        """
        super(Client, self).__init__()
        self.user = None
        self.address = address
        self.sock = connection
        self.server = server
        self.sock.setblocking(0)
        self.message_queue = Queue.Queue()
        self.connection_accepted = False
        self.ready_for_ping = True
        self.last_ping = int(time.time())
        self.ping_random_number = 0

    def ping(self, rand_num):
        """Take care of setting variables for when a client is pinged."""
        self.ping_random_number = rand_num
        self.ready_for_ping = False

    def time_since_pinged(self):
        """Return the time elapsed since the last ping."""
        return int(time.time()) - self.last_ping
    
    def add_message(self, data):
        """Add a message to the queue."""
        return self.message_queue.put(data)
        
    def get_message(self):
        """Get the next message out from the queue."""
        return self.message_queue.get_nowait()
    
    def join_channel(self, chan):
        """
        Notify the client that he has joined the channel, and supply the 
        client with a userlist.

        """
        try:
            chan = Channel(chan)
        except NameError:
            chan = Channel.channels[chan]
        if chan not in self.user.channels:
            logging.debug("Putting user '%s' in channel '%s'" % (self.user.nickname, chan.name))
            chan.add_user(self.user)
            self.user.add_channel(chan)
            self.server.queue_message("JOINED: %s\r\n" % chan.name, self.sock)
            self.server.queue_message("USERLIST %s: %s\r\n" % (chan.name, chan.userlist()), self.sock)
    
    def leave_channel(self, channel):
        """Leave a channel by removing it from the self.channels list."""
        if channel in self.user.channels:
            self.user.leave_channel(channel)
    
    def close(self):
        """Wrapper for the sockets close function."""
        return self.sock.close()

