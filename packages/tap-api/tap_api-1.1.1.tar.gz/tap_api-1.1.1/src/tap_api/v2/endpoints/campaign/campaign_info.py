"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class CampaignInfo(Dict):
    def __init__(self, data: Dict):
        super().__init__(data)

    @property
    def id(self) -> str:
        return self.get('id', "")

    @property
    def last_updated_at(self) -> str:
        return self.get('lastUpdatedAt', "")
