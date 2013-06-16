#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start the server.

"""

from voixer.server import Server


def main():
    server = Server()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.close()
        print ""
        print "Shutting down..."

if __name__ == "__main__":
    main()