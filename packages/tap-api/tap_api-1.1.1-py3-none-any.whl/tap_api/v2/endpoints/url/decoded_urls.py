"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List

from tap_api.v2.endpoints.url.url_info import UrlInfo
from tap_api.web import Dictionary


class DecodedUrls(Dictionary):
    """
    Represents the root object of the URL decoding response.
    """

    def urls(self) -> List[UrlInfo]:
        """
        Returns a list of UrlInfo objects representing the decoded URLs.
        """
        return [UrlInfo(url) for url in self.get("urls", [])]
