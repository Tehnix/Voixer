#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Object to hold the user data.

"""


class User(object):
    """Container to user data."""
    
    used_nicknames = []
    
    def __init__(self, client, nickname, real_name):
        """
        Setup instance variables. If a nickname is already taken, it 
        throws a NameError exception.
        
        """
        super(User, self).__init__()
        self.client = client
        self.nickname = nickname
        self.real_name = real_name
        self.channels = []
        self.connected = True
        if self.nickname in User.used_nicknames:
            raise NameError("User nickname already exists")
        User.used_nicknames.append(nickname)

    def add_channel(self, chan_obj):
        """Takes in a channel object and stores it in the self.channels list."""
        if chan_obj not in self.channels:
            self.channels.append(chan_obj)

    def leave_channel(self, chan_obj):
        """Takes in a channel object and removes it from the self.channels list."""
        if chan_obj in self.channels:
            self.channels.remove(chan_obj)
    
    def clean_up_user(self):
        """Clean up the user object."""
        self.connected = False
        for channel in self.channels:
            channel.clean_up_channel()
        self.channels = []
        User.used_nicknames.remove(self.nickname)

