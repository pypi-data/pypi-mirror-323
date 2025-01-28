"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from datetime import datetime
from typing import List

from requests import Response

from tap_api.web import Dictionary
from .actor import Actor
from .brand import Brand
from .family import Family
from .malware import Malware
from .technique import Technique


class ThreatSummary(Dictionary):
    def __init__(self, response: Response):
        super().__init__(response)

    @property
    def id(self) -> str:
        return self.get('id', "")

    @property
    def identified_at(self) -> datetime:
        return self.get('identifiedAt', None)

    @property
    def name(self) -> str:
        return self.get('name', "")

    @property
    def type(self) -> str:
        return self.get('type', "")

    @property
    def category(self) -> str:
        return self.get('category', "")

    @property
    def status(self) -> str:
        return self.get('status', "")

    @property
    def detection_type(self) -> str:
        return self.get('detectionType', "")

    @property
    def severity(self) -> int:
        return self.get('severity', 0)

    @property
    def attack_spread(self) -> int:
        return self.get('attackSpread', 0)

    @property
    def notable(self) -> bool:
        return self.get('notable', False)

    @property
    def verticals(self) -> bool:
        return self.get('verticals', False)

    @property
    def geographies(self) -> bool:
        return self.get('geographies', False)

    @property
    def actors(self) -> List[Actor]:
        return [Actor(actor) for actor in self.get("actors", [])]

    @property
    def families(self) -> List[Family]:
        return [Family(family) for family in self.get("families", [])]

    @property
    def malware(self) -> List[Malware]:
        return [Malware(m) for m in self.get("malware", [])]

    @property
    def techniques(self) -> List[Technique]:
        return [Technique(t) for t in self.get("techniques", [])]

    @property
    def brands(self) -> List[Brand]:
        return [Brand(b) for b in self.get("brands", [])]
