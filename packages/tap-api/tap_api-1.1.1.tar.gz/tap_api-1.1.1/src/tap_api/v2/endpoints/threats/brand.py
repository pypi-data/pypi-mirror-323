"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class Brand(Dict):
    @property
    def id(self) -> str:
        return self.get("id", "")

    @property
    def name(self) -> str:
        return self.get("name", "")
