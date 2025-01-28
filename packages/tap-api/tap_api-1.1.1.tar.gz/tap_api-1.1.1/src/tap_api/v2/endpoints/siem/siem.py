"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.v2.endpoints.siem.all import All
from tap_api.v2.endpoints.siem.clicks import Clicks
from tap_api.v2.endpoints.siem.issues import Issues
from tap_api.v2.endpoints.siem.messages import Messages
from tap_api.web.resource import Resource


class Siem(Resource):

    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)
        self.__clicks = Clicks(self, "clicks")
        self.__messages = Messages(self, "messages")
        self.__issues = Issues(self, "issues")
        self.__all = All(self, "all")

    @property
    def clicks(self) -> Clicks:
        return self.__clicks

    @property
    def messages(self) -> Messages:
        return self.__messages

    @property
    def issues(self) -> Issues:
        return self.__issues

    @property
    def all(self) -> All:
        return self.__all
