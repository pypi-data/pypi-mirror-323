"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List

from requests import Response

from tap_api.v2.endpoints.siem.click_event import ClickEvent
from tap_api.v2.endpoints.siem.message_event import MessageEvent
from tap_api.web import Dictionary


class SIEMData(Dictionary):
    def __init__(self, response: Response):
        super().__init__(response)

    @property
    def query_end_time(self) -> str:
        return self.get('queryEndTime', "")

    @property
    def messages_delivered(self) -> List[MessageEvent]:
        return [MessageEvent(me) for me in self.get("messagesDelivered", [])]

    @property
    def messages_blocked(self) -> List[MessageEvent]:
        return [MessageEvent(me) for me in self.get("messagesBlocked", [])]

    @property
    def clicks_permitted(self) -> List[ClickEvent]:
        return [ClickEvent(ce) for ce in self.get("clicksPermitted", [])]

    @property
    def clicks_blocked(self) -> List[ClickEvent]:
        return [ClickEvent(ce) for ce in self.get("clicksBlocked", [])]
