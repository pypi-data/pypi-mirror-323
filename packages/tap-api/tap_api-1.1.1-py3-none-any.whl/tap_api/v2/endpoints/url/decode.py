"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List

from tap_api.v2.endpoints.url.decoded_urls import DecodedUrls
from tap_api.web.resource import Resource


class Decode(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)

    def __call__(self, urls: List[str]) -> DecodedUrls:
        return DecodedUrls(self._session.post(self._uri, json={"urls": urls}))
