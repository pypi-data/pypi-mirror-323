"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.web import Resource
from .vap import Vap


class People(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)
        self.__vap = Vap(self, "vap")

    @property
    def vap(self) -> Vap:
        return self.__vap
