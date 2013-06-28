#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start the server.

"""
import threading
import logging

from voixer.tcp_server import TCPServer
from voixer.udp_server import UDPServer


def main(detailed_logging=True):
    if detailed_logging:
        FORMAT = "%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s"
    else:
        FORMAT = "%(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    tcp_server = TCPServer(port=10000)
    udp_server = UDPServer(port=10001)
    try:
        tcp_thread = threading.Thread(target=tcp_server.run)
        udp_thread = threading.Thread(target=udp_server.run)
        tcp_thread.start()
        udp_thread.start()
        tcp_thread.join()
        udp_thread.join()
    except KeyboardInterrupt:
        tcp_server.close()
        udp_server.close()
        logging.debug("Shutting down")
    except Exception, e:
        logging.exception("Uncaught exception!")
        tcp_server.close()
        udp_server.close()
        logging.debug("Shutting down")

if __name__ == "__main__":
    main(detailed_logging=True)