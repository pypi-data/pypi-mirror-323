"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List

from requests import Response

from tap_api.web import Dictionary
from .actor import Actor
from .campaign_family import CampaignFamily
from .campaign_member import CampaignMember
from .malware import Malware
from .technique import Technique


class CampaignSummary(Dictionary):
    def __init__(self, response: Response):
        super().__init__(response)

    @property
    def id(self) -> str:
        return self.get('id', "")

    @property
    def name(self) -> str:
        return self.get('name', "")

    @property
    def description(self) -> str:
        return self.get('description', "")

    @property
    def start_date(self) -> str:
        return self.get('startDate', "")

    @property
    def campaign_members(self) -> List[CampaignMember]:
        return [CampaignMember(cm) for cm in self.get("campaignMembers", [])]

    @property
    def actors(self) -> List[Actor]:
        return [Actor(a) for a in self.get("actors", [])]

    @property
    def malware(self) -> List[Malware]:
        return [Malware(m) for m in self.get("malware", [])]

    @property
    def techniques(self) -> List[Technique]:
        return [Technique(t) for t in self.get("techniques", [])]

    @property
    def families(self) -> List[CampaignFamily]:
        return [CampaignFamily(f) for f in self.get("families", [])]
