#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The TalkAction object holds the address and data of the user.

"""

import threading
import Queue
import time


class TalkAction(object):

    def __init__(self, instigator, target, action):
        self.instigator = instigator
        self.target = target
        self.action = action