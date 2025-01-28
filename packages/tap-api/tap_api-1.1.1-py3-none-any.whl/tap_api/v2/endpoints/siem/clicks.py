"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.v2.endpoints.siem.blocked import Blocked
from tap_api.v2.endpoints.siem.permitted import Permitted
from tap_api.web import Resource


class Clicks(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)
        self.__blocked = Blocked(self, 'blocked')
        self.__permitted = Permitted(self, 'permitted')

    @property
    def blocked(self) -> Blocked:
        return self.__blocked

    @property
    def permitted(self) -> Permitted:
        return self.__permitted
