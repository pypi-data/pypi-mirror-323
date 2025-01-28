"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List, Dict

from .evidence_types import EvidenceType, create_evidence_type
from .platform import Platform


class Evidence(Dict):
    @property
    def type(self) -> str:
        return self.get("type", "")

    @property
    def display(self) -> str:
        return self.get("display", "")

    @property
    def engine(self) -> str:
        return self.get("engine", "")

    @property
    def note(self) -> str:
        return self.get("note", "")

    @property
    def time(self) -> str:
        return self.get("time", "")

    @property
    def malicious(self) -> bool:
        return self.get("malicious", False)

    @property
    def what(self) -> EvidenceType:
        """
        Returns the appropriate WhatInfo object based on the type field.
        """
        return create_evidence_type(self.get("what", {}), self.type)

    @property
    def platforms(self) -> List[Platform]:
        return [Platform(p) for p in self.get("platforms", [])]
