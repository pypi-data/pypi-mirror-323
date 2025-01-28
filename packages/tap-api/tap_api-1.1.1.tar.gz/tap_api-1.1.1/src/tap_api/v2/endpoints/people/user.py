"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict

from .identity import Identity
from .threat_statistics import ThreatStatistics


class User(Dict):
    @property
    def identity(self) -> Identity:
        return Identity(self.get("identity", {}))

    @property
    def threat_statistics(self) -> ThreatStatistics:
        return ThreatStatistics(self.get("threatStatistics", {}))
