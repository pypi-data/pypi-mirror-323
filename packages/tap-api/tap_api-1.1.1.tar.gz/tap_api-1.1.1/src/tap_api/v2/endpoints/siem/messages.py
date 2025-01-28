"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.v2.endpoints.siem.blocked import Blocked
from tap_api.v2.endpoints.siem.delivered import Delivered
from tap_api.web import Resource


class Messages(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)
        self.__blocked = Blocked(self, 'blocked')
        self.__delivered = Delivered(self, 'delivered')

    @property
    def blocked(self) -> Blocked:
        return self.__blocked

    @property
    def delivered(self) -> Delivered:
        return self.__delivered
