"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict, List

from tap_api.v2.endpoints.siem.actor import Actor


class ThreatsInfoMap(Dict):
    @property
    def detection_type(self) -> str:
        return self.get("detectionType", "")

    @property
    def disposition(self) -> str:
        return self.get("campaignId", "")

    @property
    def filename(self) -> str:
        return self.get("classification", "")

    @property
    def threat(self) -> str:
        return self.get("threat", "")

    @property
    def threat_id(self) -> str:
        return self.get("threatId", "")

    @property
    def threat_status(self) -> str:
        return self.get("threatStatus", "")

    @property
    def threat_time(self) -> str:
        return self.get("threatTime", "")

    @property
    def threat_type(self) -> str:
        return self.get("threatType", "")

    @property
    def threat_url(self) -> str:
        return self.get("threatUrl", "")

    @property
    def actors(self) -> List[Actor]:
        return [Actor(a) for a in self.get("actors", [])]
