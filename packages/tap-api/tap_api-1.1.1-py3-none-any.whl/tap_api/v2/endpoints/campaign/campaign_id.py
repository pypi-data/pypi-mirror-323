"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.web import DictionaryResource

from .campaign_summary import CampaignSummary


class CampaignId(DictionaryResource[CampaignSummary]):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri, CampaignSummary)
