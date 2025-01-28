"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List

from tap_api.web import Dictionary
from .campaign_info import CampaignInfo


class CampaignMetadata(Dictionary):
    @property
    def campaigns(self) -> List[CampaignInfo]:
        return [CampaignInfo(r) for r in self.get("campaigns", [])]
