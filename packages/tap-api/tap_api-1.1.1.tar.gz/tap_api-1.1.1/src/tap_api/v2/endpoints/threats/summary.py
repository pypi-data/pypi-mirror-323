"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.web import DictionaryResource
from .threat_summary import ThreatSummary


class Summary(DictionaryResource[ThreatSummary]):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri, ThreatSummary)
