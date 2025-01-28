"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class UrlInfo(Dict):
    def __init__(self, data: Dict):
        super().__init__(data)

    @property
    def encoded_url(self) -> str:
        return self.get('encodedUrl', "")

    @property
    def decoded_url(self) -> str:
        return self.get('decodedUrl', "")

    @property
    def message_guid(self) -> str:
        return self.get('messageGuid', "")

    @property
    def cluster_name(self) -> str:
        return self.get('clusterName', "")

    @property
    def recipient_email(self) -> str:
        return self.get('recipientEmail', "")

    @property
    def success(self) -> bool:
        return self.get('success', False)

    @property
    def error(self) -> str:
        return self.get('error', "")
