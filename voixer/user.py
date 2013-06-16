#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Object to hold the user data.

"""


class User(object):
    """Container to user data."""
    
    used_nicknames = []
    
    def __init__(self, nickname, realname):
        """Setup instance variables."""
        super(User, self).__init__()
        self.nickname = nickname
        self.realname = realname