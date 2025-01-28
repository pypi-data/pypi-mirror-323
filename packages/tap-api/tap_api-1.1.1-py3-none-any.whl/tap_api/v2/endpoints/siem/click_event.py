"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict


class ClickEvent(Dict):
    @property
    def campaign_id(self) -> str:
        return self.get("campaignId", "")

    @property
    def classification(self) -> str:
        return self.get("classification", "")

    @property
    def click_ip(self) -> str:
        return self.get("clickIP", "")

    @property
    def click_time(self) -> str:
        return self.get("clickTime", "")

    @property
    def guid(self) -> str:
        return self.get("GUID", "")

    @property
    def id(self) -> str:
        return self.get("id", "")

    @property
    def recipient(self) -> str:
        return self.get("recipient", "")

    @property
    def sender(self) -> str:
        return self.get("sender", "")

    @property
    def sender_ip(self) -> str:
        return self.get("senderIP", "")

    @property
    def threat_id(self) -> str:
        return self.get("threatID", "")

    @property
    def threat_time(self) -> str:
        return self.get("threatTime", "")

    @property
    def threat_url(self) -> str:
        return self.get("threatURL", "")

    @property
    def threat_status(self) -> str:
        return self.get("threatStatus", "")

    @property
    def url(self) -> str:
        return self.get("threatStatus", "")

    @property
    def user_agent(self) -> str:
        return self.get("userAgent", "")
