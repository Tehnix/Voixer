#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Start the server.

"""

import logging

from voixer.server import Server


def main(detailed_logging=True):
    if detailed_logging:
        FORMAT = "%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s"
    else:
        FORMAT = "%(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        server.close()
        logging.debug("Shutting down")
    except Exception, e:
        logging.exception("Uncaught exception!")
        server.close()
        logging.debug("Shutting down")

if __name__ == "__main__":
    main(detailed_logging=True)