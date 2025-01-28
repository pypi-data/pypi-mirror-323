"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict, Optional, List


class Identity(Dict):
    @property
    def guid(self) -> Optional[str]:
        return self.get("guid")

    @property
    def customer_user_id(self) -> Optional[str]:
        return self.get("customerUserId")

    @property
    def emails(self) -> List[str]:
        return self.get("emails", [])

    @property
    def name(self) -> Optional[str]:
        return self.get("name")

    @property
    def department(self) -> Optional[str]:
        return self.get("department")

    @property
    def location(self) -> Optional[str]:
        return self.get("location")

    @property
    def title(self) -> Optional[str]:
        return self.get("title")

    @property
    def vip(self) -> bool:
        return self.get("vip", False)
