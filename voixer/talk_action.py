#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The talk object takes handles the UDP VoIP connections, and takes
care of directing them to the correct client connections.

"""

import threading
import Queue
import time


class TalkAction(object):

    def __init__(self, target, action):
        self.target = target
        self.action = action