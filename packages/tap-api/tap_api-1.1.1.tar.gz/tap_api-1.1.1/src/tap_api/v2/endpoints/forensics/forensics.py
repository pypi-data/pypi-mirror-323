"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from tap_api.web import Resource, FilterOptions
from .aggregate import AggregateForensics


class Forensics(Resource):
    def __init__(self, parent, uri: str):
        super().__init__(parent, uri)

    def campaign(self, campaign_id: str) -> AggregateForensics:
        options = FilterOptions()
        options.add_option("campaignId", campaign_id)
        return AggregateForensics(self._session.get(self._uri, params=options.params))

    def threat(self, threat_id: str, campaign_forensics: bool = False) -> AggregateForensics:
        options = FilterOptions()
        options.add_option("threatId", threat_id)
        options.add_option("includecampaignforensics", campaign_forensics)
        return AggregateForensics(self._session.get(self._uri, params=options.params))
