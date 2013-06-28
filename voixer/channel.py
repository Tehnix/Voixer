#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Object to hold the channel data.

"""


class Channel(object):
    """Container for the channel data."""

    # {channel_name : Channel Object} - Keeps track of channel names
    channels = {}

    def __init__(self, name):
        """
        Setup instance variables. It throws a NameError exception if the
        channel name is already in use.
        
        """
        super(Channel, self).__init__()
        self.name = name.lower()
        self.users_in_room = []
        if self.name in Channel.channels:
            raise NameError("Channel name already exists")
        Channel.channels[self.name] = self

    def add_user(self, user_obj):
        """Add a user to the self.users_in_room list."""
        self.users_in_room.append(user_obj)

    def remove_user(self, user_obj):
        """Remove a user from the self.users_in_room list."""
        self.users_in_room.remove(user_obj)

    def clean_up_channel(self):
        """Remove disconnected users."""
        for user in self.users_in_room:
            if not user.connected:
                self.users_in_room.remove(user)

    def userlist(self):
        """Return a comma separated userlist."""
        self.clean_up_channel()
        return ', '.join(u.nickname for u in self.users_in_room)

