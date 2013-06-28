#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The UDP server keeps track of all UDP connections.

"""
import threading
import socket
import logging

from talk import Talk
from talk_action import TalkAction
from talk_data import TalkData


class UDPServer(threading.Thread):
    """UDP Server."""

    def __init__(self, port=10001):
        """Set up the instance variables."""
        super(UDPServer, self).__init__()
        self.udp_server = None
        self.port = port
        self.udp_connections = {}

    def run(self):
        """Initiate the UDP server."""
        self.udp_server = self.setup_udp_server(self.port)
        self.handle_connections()

    def setup_udp_server(self, port):
        """
        Creates a blocking UDP socket, binds it to the specified port.

        """
        # 0.0.0.0 (or an empty string) means that we accept all
        # incoming connections (if an IP is typed, it'll restrict it
        # to connections from said IP).
        address = ('0.0.0.0', port)
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug(">>> Starting udp server on %s on port %s" % address)
        server.bind(address)
        return server

    def handle_connections(self):
        """Handle the UDP connections."""
        while True:
            rawdata, address = self.udp_server.recvfrom(2048)
            if rawdata.startswith("TALKSESSION"):
                session_key = rawdata.split(":")[1].strip()
                self.talk_session(session_key, address)
            elif address in self.udp_connections:
                for data in rawdata.split("\r\n"):
                    if data == "":
                        continue
                    logging.debug(">>> Creating TalkData for '%s'" % data)
                    talk = self.udp_connections[address]
                    talk_data = TalkData(address, data)
                    talk.talk_queue.put(talk_data)

    def talk_session(self, session_key, address):
        """Put the UDP client into a talk session."""
        logging.debug(
            ">>> Putting %s into session with key '%s'" % (address, session_key)
        )
        try:
            session_key = int(session_key)
        except ValueError:
            pass
        else:
            if session_key in Talk.talk_sessions:
                logging.debug(">>> Session found with session key '%s'" % session_key)
                talk = Talk.talk_sessions[session_key]
                talk.participants.append(address)
                self.udp_connections[address] = talk
                talk.udp_server = self.udp_server
                talk_action = TalkAction(None, "INITIATE")
                talk.add_action(talk_action)

    def close(self):
        """Close down the UDP server."""
        if self.udp_server is not None:
            self.udp_server.close()