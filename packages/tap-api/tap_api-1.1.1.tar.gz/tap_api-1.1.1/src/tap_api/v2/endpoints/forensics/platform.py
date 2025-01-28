"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class Platform(Dict):
    @property
    def name(self) -> str:
        return self.get("name", "")

    @property
    def os(self) -> str:
        return self.get("os", "")

    @property
    def version(self) -> str:
        return self.get("version", "")
