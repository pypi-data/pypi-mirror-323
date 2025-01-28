"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class MessageParts(Dict):
    @property
    def content_type(self) -> str:
        return self.get("contentType", "")

    @property
    def disposition(self) -> str:
        return self.get("disposition", "")

    @property
    def filename(self) -> str:
        return self.get("filename", "")

    @property
    def md5(self) -> str:
        return self.get("md5", "")

    @property
    def o_content_type(self) -> str:
        return self.get("oContentType", "")

    @property
    def sandbox_status(self) -> str:
        return self.get("sandboxStatus", "")

    @property
    def sha256(self) -> str:
        return self.get("sha256", "")
