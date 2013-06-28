#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The talk object takes handles the UDP VoIP connections, and takes
care of directing them to the correct client connections.

"""

import threading
import Queue
import logging


class Talk(threading.Thread):
    """Talk object."""

    # {session_key : Talk Object} - Keeps track of Talk sessions going on
    talk_sessions = {}
    
    def __init__(self, session_key):
        """Set up the instance variables."""
        super(Talk, self).__init__()
        self.session_key = session_key
        self.tcp_clients = []
        self.participants = []
        if self.session_key in Talk.talk_sessions:
            raise NameError("There already exists a session with that number")
        Talk.talk_sessions[self.session_key] = self
        self.action_queue = Queue.Queue()
        self.talk_queue = Queue.Queue()
        self.udp_server = None

    def run(self):
        """
        Wait for an action to be ready an do something accordingly. If
        there is no action in 30 seconds, stop the thread, and consider
        it dead.

        """
        while True:
            try:
                logging.debug(">>> Waiting for action")
                talk_action = self.action_queue.get(True, 150)
            except Queue.Empty:
                break
            else:
                self.handle(talk_action)
        self.close()

    def handle(self, talk_action):
        """Handle the TalkAction object."""
        target = talk_action.target
        action = talk_action.action
        logging.debug(
            "Target: %s. Action: %s. Connections: %s" % (target, action, len(self.tcp_clients))
        )
        if action == "INITIATE":
            logging.debug(
                ">>> Starting VoIP conversation for '%s'" % self.session_key
            )
            self.voip()
        elif action == "DENY":
            for client in self.tcp_clients:
                if client is not talk_action.instigator:
                    client.server.queue_message(
                        "TALK %s: DENIED" % self.session_key,
                        client.sock
                    )
        elif action == "ACCEPT":
            for client in self.tcp_clients:
                if client is not talk_action.instigator:
                    client.server.queue_message(
                        "TALK %s: ACCEPTED" % self.session_key,
                        client.sock
                    )

    def voip(self):
        """Initiate the VoIP conversation."""
        logging.debug(
            ">>> VoIP started for '%s'" % self.session_key
        )
        while True:
            try:
                talk_data = self.talk_queue.get(True)
            except Queue.Empty:
                pass
            else:
                if not self.participants:
                    logging.debug(
                        ">>> Data present, but nobody is listening: '%s'" % talk_data.data
                    )
                for conn in self.participants:
                    if conn != talk_data.address:
                        logging.debug(">>> Sending data '%s' from %s to %s" % (talk_data.data, talk_data.address, conn))
                        try:
                            self.udp_server.sendto(talk_data.data, conn)
                        except TypeError:
                            logging.exception(">>> Invalid data?: '%s'" % talk_data.data)
        logging.debug(
            ">>> VoIP ended for '%s'" % self.session_key
        )


    def add_action(self, talk_action):
        """Add a TalkAction object to the action queue."""
        self.action_queue.put(talk_action)

    def close(self):
        """Close down the talk session."""
        logging.debug("Closing down Talk Object with session '%s'" % self.session_key)
        for client in self.tcp_clients:
            client.server.queue_message(
                "TALK %s: END" % self.session_key,
                client.sock
            )