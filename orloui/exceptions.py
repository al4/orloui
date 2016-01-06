from __future__ import print_function

__author__ = 'alforbes'


class OrloConnectionError(Exception):
    """
    For errors connecting to upstream services
    """
    status_code = 502

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
