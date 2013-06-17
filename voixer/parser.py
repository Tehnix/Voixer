#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The parser will handle translating messages into protocol
instances, and taking action accordingly.

"""

import logging

from user import User


class Parser(object):
    """Parse messages received from the clients."""
    
    def __init__(self, server, sender_socket, msg):
        """Setup instance variables."""
        super(Parser, self).__init__()
        self.server = server
        self.sender_socket = sender_socket
        self.sender_client = server.connections[sender_socket]
        self.msg = msg
        self.protocol = {
            "DISCONNECT": self.client_disconnecting(),
            "PRIVMSG": self.privmsg(),
            "PONG": self.pong(),
            "JOIN": self.join(),
            "TALK": self.talk()
        }
        self.parse(msg)
    
    def starts(self, s):
        """Shorter syntax for the startswith."""
        return self.msg.startswith(s)
    
    def parse(self, msg):
        msg = msg.split(":")[0].split()[0]
        try:
            if self.sender_client.connection_accepted:
                self.protocol[msg]
            elif self.starts("CONNECT"):
                self.client_connecting()
            else:
                # TODO: Inform the client that it needs to be accepted first
                # NOTACCEPTED: Please send or resend the CONNECT request
                pass
        except KeyError:
            logging.warning("Unkown protocol msg '{0}'".format(msg))
        
    def client_connecting(self):
        try:
            information = self.msg.split(":")[1:][0]
            nickname = information.split('"')[1]
            realname = information.split('"')[3]
            version = information.split('"')[4].strip()
        except IndexError:
            # TODO: Inform the client of error in syntax
            pass
        else:
            user = User(nickname, realname)
            self.sender_client.user = user
            self.sender_client.connection_accepted = True
            logging.debug("Client has been accepted with nickname %s" % nickname)
    
    def client_disconnecting(self):
        pass
    
    def privmsg(self):
        message = self.msg
        recipient = None
        #self.server.queue_message(message, recipient, self.sender_socket)
    
    def pong(self):
        pass
    
    def join(self):
        pass
    
    def talk(self):
        pass

