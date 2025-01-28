"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import List

from requests import Response

from tap_api.web import Dictionary
from .user import User


class VapSummary(Dictionary):
    def __init__(self, response: Response):
        super().__init__(response)

    @property
    def users(self) -> List[User]:
        return [User(user) for user in self.get("users", [])]

    @property
    def total_vap_users(self) -> int:
        return self.get('totalVapUsers', 0)

    @property
    def interval(self) -> str:
        return self.get('interval', "")

    @property
    def average_attack_index(self) -> int:
        return self.get('averageAttackIndex', 0)

    @property
    def vap_attack_index_threshold(self) -> int:
        return self.get('vapAttackIndexThreshold', 0)
