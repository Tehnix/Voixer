#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The parser will handle translating messages into protocol
instances, and taking action accordingly.

"""

import logging
import time
import random
import threading

from user import User
from talk import Talk
from talk_action import TalkAction


## START OF TESTING ##
Talk(631720830760049)
## END OF TESTING ##


class Parser(object):
    """Parse messages received from the clients."""

    def __init__(self, server, sender_socket, data):
        """Setup instance variables."""
        super(Parser, self).__init__()
        self.server = server
        self.sender_socket = sender_socket
        self.sender_client = server.tcp_connections[sender_socket]
        self.data = data
        self.protocol = {
            "DISCONNECT": self.client_disconnecting,
            "MSG": self.msg,
            "PONG": self.pong,
            "JOIN": self.join,
            "TALK": self.talk
        }
        self.parse(data)

    def starts(self, s):
        """Shorter syntax for the startswith."""
        return self.data.startswith(s)

    def parse(self, data):
        """
        Handle the message according to the protocol, making sure the client is
        connected before being able to do anything else.
        
        """
        action = data.split(":")[0].split()[0]
        try:
            logging.debug("Executing action '%s'" % action)
            if self.starts("CONNECT"):
                self.client_connecting()
            elif self.starts("TALKSESSION"):
                self.talk_session()
            elif self.sender_client.connection_accepted:
                self.protocol[action]()
            else:
                self.server.queue_message(
                    "NOTACCEPTED: Please send or resend the CONNECT request\r\n",
                    self.sender_socket
                )
        except KeyError:
            logging.exception(
                "Unknown protocol action '{0}', or an error occurred".format(action)
            )
        except IndexError:
            logging.exception(
                "An error occurred during execution of '{0}'".format(action)
            )

    def initial_connect(self):
        """
        Notify the client that it has been accepted, and invite the new
        client to the default channel.

        """
        self.server.queue_message(
            "ACCEPTED: %s\r\n" % self.server.hostname, self.sender_socket
        )
        chan = self.server.default_channel
        if chan:
            self.sender_client.join_channel(chan)

    def client_connecting(self):
        """Handle a connection request from a new connection."""
        try:
            information = self.data.split(":")[1:][0]
            nickname = information.split('"')[1]
            real_name = information.split('"')[3]
            version = information.split('"')[4].strip()
        except IndexError:
            self.server.queue_message(
                "NOTACCEPTED: Syntax error, please resend the CONNECT request\r\n",
                self.sender_socket
            )
            pass
        else:
            try:
                user = User(self.sender_client, nickname, real_name)
            except NameError:
                self.server.queue_message(
                    "NICKNAMEINUSE: The nickname '%s' is already taken\r\n" % nickname,
                    self.sender_socket
                )
            else:
                self.sender_client.user = user
                self.sender_client.connection_accepted = True
                logging.debug(
                    "TCPClient has been accepted with nickname %s" % user.nickname
                )
                self.initial_connect()

    def client_disconnecting(self):
        """Close a clients connection and remove him."""
        logging.debug(
            "TCPClient %s disconnecting" % (self.sender_socket.getpeername(), )
        )
        self.server.remove_client(self.sender_socket)

    def msg(self):
        """Send out a message to either a channel or user."""
        recipient = self.data.split()[1].split(":")[0].lower()
        message = ':'.join(self.data.split(":")[1:]).strip()
        sender = self.sender_client.user.nickname
        data = "MSG %s %s: %s\r\n" % (sender, recipient, message)
        if recipient.startswith("#"):
            self.server.queue_message_to_channel(data, recipient, self.sender_socket)
        else:
            self.server.queue_message_to_client(data, recipient, self.sender_socket)

    def pong(self):
        """Check if the PONG received matches the PING sent out."""
        number = int(self.data.split(":")[1].strip())
        if number == self.sender_client.ping_random_number:
            logging.debug(
                "PONG received from %s" % (self.sender_socket.getpeername(), )
            )
            self.sender_client.last_ping = int(time.time())
            self.sender_client.ready_for_ping = True

    def join(self):
        """Join a channel."""
        channels = self.data.split(":")[1].strip().split()
        for channel in channels:
            channel = channel.lower()
            if not channel.startswith("#"):
                channel = "#" + channel
            self.sender_client.join_channel(channel)

    def talk_session(self):
        """Put the UDP client into a talk session."""
        session_key = int(self.data.split(":")[1].strip())
        try:
            session_key = int(session_key)
        except ValueError:
            self.server.queue_message(
                "SESSIONERROR: Invalid session key '%s'\r\n" % session_key,
                self.sender_socket
            )
        else:
            if session_key in Talk.talk_sessions:
                talk = Talk.talk_sessions[session_key]
                talk_action = TalkAction(None, "INITIATE")
                talk.add_action(talk_action)
            else:
                self.server.queue_message(
                    "SESSIONERROR: Invalid session key '%s'\r\n" % session_key,
                    self.sender_socket
                )

    def talk(self):
        """
        Handle VoIP talking.

        The client sends a target client, and a randomly generated
        number (session key). The targeted client then responds with
        the number and an action based on what the client wants to do.

        The actions are:
            REQUEST - request a conversation
            ACCEPT  - accept a request for a conversation
            DENY    - deny a request for a conversation
            END     - end a conversation

        """
        talk = None
        action = self.data.split(":")[1].strip()
        target = self.data.split(":")[0].split()[1]
        logging.debug("Talk action '%s'" % action)
        if action == "REQUEST":
            session_key = random.randint(100000000000000, 999999999999999)
            while session_key in Talk.talk_sessions:
                session_key = random.randint(100000000000000, 999999999999999)
            talk = Talk(session_key)
        else:
            session_key = self.data.split(":")[0].split()[2]
            try:
                talk = Talk.talk_sessions[session_key]
            except KeyError:
                self.server.queue_message(
                    "TALK: BADSESSIONKEY\r\n", self.sender_socket
                )
        if talk is not None:
            talk_action = TalkAction(target, action)
            talk.add_action(talk_action)
            thread = threading.Thread(target=talk.run)
            thread.start()

