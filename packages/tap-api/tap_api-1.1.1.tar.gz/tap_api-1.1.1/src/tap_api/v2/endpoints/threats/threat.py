"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.web import Resource, Resources
from .summary import Summary


class Threat(Resource):
    __summary: Resources[Summary]

    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)
        self.__summary = Resources[Summary](self, "summary", Summary)

    @property
    def summary(self) -> Resources[Summary]:
        return self.__summary
