"""
Author: Ludvik Jerabek
Package: tap-api
License: MIT
"""
from typing import Dict, List

from tap_api.v2.endpoints.siem.message_parts import MessageParts
from tap_api.v2.endpoints.siem.threats_info_map import ThreatsInfoMap


class MessageEvent(Dict):
    @property
    def cc_addresses(self) -> List[str]:
        return self.get("ccAddresses", [])

    @property
    def cluster_id(self) -> str:
        return self.get("clusterId", "")

    @property
    def completely_rewritten(self) -> str:
        return self.get("completelyRewritten", "na")

    @property
    def from_address(self) -> str:
        return self.get("fromAddress", "")

    @property
    def guid(self) -> str:
        return self.get("guid", "")

    @property
    def header_from(self) -> str:
        return self.get("headerFrom", "")

    @property
    def header_reply_to(self) -> str:
        return self.get("headerReplyTo", "")

    @property
    def impostor_score(self) -> int:
        return self.get("impostorScore", 0)

    @property
    def malware_score(self) -> int:
        return self.get("malwareScore", 0)

    @property
    def message_id(self) -> str:
        return self.get("messageID", "")

    @property
    def message_parts(self) -> List[MessageParts]:
        return [MessageParts(mp) for mp in self.get("messageParts", [])]

    @property
    def message_size(self) -> int:
        return self.get("messageSize", 0)

    @property
    def modules_run(self) -> List[str]:
        return self.get("modulesRun", [])

    @property
    def phish_score(self) -> int:
        return self.get("phishScore", 0)

    @property
    def policy_routes(self) -> List[str]:
        return self.get("policyRoutes", [])

    @property
    def qid(self) -> str:
        return self.get("QID", "")

    @property
    def quarantine_folder(self) -> str:
        return self.get("quarantineFolder", "")

    @property
    def quarantine_rule(self) -> str:
        return self.get("quarantineRule", "")

    @property
    def recipient(self) -> str:
        return self.get("recipient", "")

    @property
    def reply_to_address(self) -> str:
        return self.get("replyToAddress", "")

    @property
    def sender(self) -> str:
        return self.get("sender", "")

    @property
    def sender_ip(self) -> str:
        return self.get("senderIP", "")

    @property
    def spam_score(self) -> int:
        return self.get("spamScore", 0)

    @property
    def subject(self) -> str:
        return self.get("subject", "")

    @property
    def threats_info_map(self) -> List[ThreatsInfoMap]:
        return [ThreatsInfoMap(tim) for tim in self.get("threatsInfoMap", [])]

    @property
    def to_addresses(self) -> List[str]:
        return self.get("toAddresses", [])

    @property
    def x_mailer(self) -> str:
        return self.get("xmailer", "")
