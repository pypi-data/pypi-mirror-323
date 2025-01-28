"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class CampaignMember(Dict):
    @property
    def id(self) -> str:
        return self.get("id", "")

    @property
    def name(self) -> str:
        return self.get("name", "")

    @property
    def type(self) -> str:
        return self.get("type", "")

    @property
    def sub_type(self) -> str:
        return self.get("subType", "")

    @property
    def threat_time(self) -> str:
        return self.get("threatTime", "")
