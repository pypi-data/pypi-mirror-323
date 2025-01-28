"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class ThreatFamily(Dict):
    @property
    def name(self) -> str:
        return self.get("name", "")

    @property
    def score(self) -> int:
        return self.get("score", 0)
