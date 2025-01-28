"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List

from tap_api.web import Dictionary
from .report import Report


class AggregateForensics(Dictionary):
    @property
    def generated(self) -> str:
        return self.get("generated", "")

    @property
    def reports(self) -> List[Report]:
        return [Report(r) for r in self.get("reports", [])]
