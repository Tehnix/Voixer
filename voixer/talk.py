#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The talk object takes handles the UDP VoIP connections, and takes
care of directing them to the correct client connections.

"""

import threading
import Queue
import pyaudio


class Talk(threading.Thread):
    """Talk object."""

    # {session_key : Talk Object} - Keeps track of Talk sessions going on
    talk_sessions = {}
    
    def __init__(self, session_key):
        """Set up the instance variables."""
        super(Talk, self).__init__()
        self.session_key = session_key
        self.participants = []
        if self.session_key in Talk.talk_sessions:
            raise NameError("There already exists a session with that number")
        Talk.talk_sessions[self.session_key] = self
        self.action_queue = Queue.Queue()

    def run(self):
        """
        Wait for an action to be ready an do something accordingly. If
        there is no action in 30 seconds, stop the thread, and consider
        it dead.

        """
        while True:
            try:
                talk_action = self.action_queue.get(True, timeout=30)
            except Queue.Empty:
                break
            else:
                self.handle(talk_action)
        self.close()

    def handle(self, talk_action):
        """Handle the TalkAction object."""
        target = talk_action.target
        action = talk_action.action
        if target is None:
            if action == "INITIATE":
                self.voip()
                # TODO initiate the VoIP call with all the self.participants
                pass
        else:
            # TODO implement ACCEPT/DENY etc
            pass

    def voip(self):
        """Initiate the VoIP conversation."""
        pass

    def add_action(self, talk_action):
        """Add a TalkAction object to the action queue."""
        self.action_queue.put(talk_action)

    def close(self):
        """Close down the talk session."""
        for udp_client in self.participants:
            udp_client.close()