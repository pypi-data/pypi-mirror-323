"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.web import Resources
from .campaign_id import CampaignId
from .ids import Ids


class Campaign(Resources[CampaignId]):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri, CampaignId)
        self.__ids = Ids(self, "ids")

    @property
    def ids(self) -> Ids:
        return self.__ids
