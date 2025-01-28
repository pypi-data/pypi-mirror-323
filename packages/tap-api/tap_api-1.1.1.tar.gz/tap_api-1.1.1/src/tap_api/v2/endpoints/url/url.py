"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.v2.endpoints.url.decode import Decode
from tap_api.web import Resource


class Url(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)
        self.__decode = Decode(self, 'decode')

    @property
    def decode(self) -> Decode:
        return self.__decode
