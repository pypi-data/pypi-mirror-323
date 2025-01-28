"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List, Dict

from .evidence import Evidence


class Report(Dict):
    @property
    def scope(self) -> str:
        return self.get("scope", "")

    @property
    def id(self) -> str:
        return self.get("id", "")

    @property
    def name(self) -> str:
        return self.get("name", "")

    @property
    def threat_status(self) -> str:
        return self.get("threatStatus", "")

    @property
    def forensics(self) -> List[Evidence]:
        return [Evidence(f) for f in self.get("forensics", [])]
