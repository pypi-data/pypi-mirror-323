import json

from tap_api.v2 import *


def print_click_data(clicks):
    for click in clicks:
        print(f"  Campaign ID: {click.campaign_id}")
        print(f"  Classification: {click.classification}")
        print(f"  Click IP: {click.click_ip}")
        print(f"  Click Time: {click.click_time}")
        print(f"  GUID: {click.guid}")
        print(f"  ID: {click.id}")
        print(f"  Recipient: {click.recipient}")
        print(f"  Sender: {click.sender}")
        print(f"  Sender IP: {click.sender_ip}")
        print(f"  Threat ID: {click.threat_id}")
        print(f"  Threat Time: {click.threat_time}")
        print(f"  Threat URL: {click.threat_url}")
        print(f"  Threat Status: {click.threat_status}")
        print(f"  URL: {click.url}")
        print(f"  User Agent: {click.user_agent}")


def print_actors_data(actors):
    for actor in actors:
        print(f"      Actor ID: {actor.id}")
        print(f"      Actor Name: {actor.name}")
        print(f"      Actor Name: {actor.type}")


def print_threat_info_map_data(threat_info_map):
    for threat in threat_info_map:
        print(f"    Detection Type: {threat.detection_type}")
        print(f"    Campaign ID: {threat.disposition}")
        print(f"    Classification: {threat.filename}")
        print(f"    Threat: {threat.threat}")
        print(f"    Threat ID: {threat.threat_id}")
        print(f"    Threat Status: {threat.threat_status}")
        print(f"    Threat Time: {threat.threat_time}")
        print(f"    Threat Type: {threat.threat_type}")
        print(f"    Threat URL: {threat.threat_url}")
        print(f"    Actors:")


def print_message_parts_data(message_parts):
    for mp in message_parts:
        print(f"    Content Type: {mp.content_type}")
        print(f"    Disposition: {mp.disposition}")
        print(f"    Filename: {mp.filename}")
        print(f"    MD5: {mp.md5}")
        print(f"    Original Content Type: {mp.o_content_type}")
        print(f"    Sandbox Status: {mp.sandbox_status}")
        print(f"    SHA256: {mp.sha256}")


def print_message_data(messages):
    for message in messages:
        print(f"  Message ID: {message.message_id}")
        print(f"  Subject: {message.subject}")
        print(f"  From Address: {message.from_address}")
        print(f"  Sender IP: {message.sender_ip}")
        print(f"  Recipient: {message.recipient}")
        print(f"  QID: {message.qid}")
        print(f"  Phish Score: {message.phish_score}")
        print(f"  Spam Score: {message.spam_score}")
        print(f"  Impostor Score: {message.impostor_score}")
        print(f"  Malware Score: {message.malware_score}")
        print(f"  To Addresses: {message.to_addresses}")
        print(f"  CC Addresses: {message.cc_addresses}")
        print(f"  Cluster ID: {message.cluster_id}")
        print(f"  Completely Rewritten: {message.completely_rewritten}")
        print(f"  Threats Info Map:")
        print_threat_info_map_data(message.threats_info_map)
        print(f"  Quarantine Folder: {message.quarantine_folder}")
        print(f"  Quarantine Rule: {message.quarantine_rule}")
        print(f"  Header From: {message.header_from}")
        print(f"  Header Reply-To: {message.header_reply_to}")
        print(f"  Reply-To Address: {message.reply_to_address}")
        print(f"  Modules Run: {message.modules_run}")
        print(f"  Policy Routes: {message.policy_routes}")
        print(f"  Message Parts:")
        print_message_parts_data(message.message_parts)


def print_siem_data_summary(siem_data):
    """
    Prints all properties and nested data from an SIEMData instance using its property accessors.

    Args:
        siem_data (SIEMData): The SIEMData object to be printed.
    """
    print("\nSIEM Data:")
    print("HTTP Status:", siem_data.get_status())
    print("HTTP Reason:", siem_data.get_reason())
    print("Query End Time:", siem_data.query_end_time)

    print("\nClicks Permitted:")
    print_click_data(siem_data.clicks_permitted)
    print("\nClicks Blocked:")
    print_click_data(siem_data.clicks_blocked)
    print("\nMessages Delivered:")
    print_message_data(siem_data.messages_delivered)
    print("\nMessages Blocked:")
    print_message_data(siem_data.messages_blocked)


if __name__ == "__main__":
    # Load API key
    with open("../tap.api_key", "r") as api_key_file:
        api_key_data = json.load(api_key_file)
    api_key = api_key_data.get("demous")

    client = Client(api_key.get("PRINCIPAL"), api_key.get("SECRET"))

    # URI Modeling
    print(client.siem._uri)
    print(client.siem.clicks._uri)
    print(client.siem.clicks.blocked._uri)
    print(client.siem.clicks.permitted._uri)
    print(client.siem.messages._uri)
    print(client.siem.messages.blocked._uri)
    print(client.siem.messages.delivered._uri)
    print(client.siem.issues._uri)
    print(client.siem.all._uri)

    # Dump the data for all endpoints, TimeRange is handled by SinceSeconds, SinceDateTime, StartEndInterval
    print_siem_data_summary(client.siem.clicks.blocked(SinceSeconds(3600)))
    print_siem_data_summary(client.siem.clicks.permitted(SinceSeconds(3600)))
    print_siem_data_summary(client.siem.messages.blocked(SinceSeconds(3600)))
    print_siem_data_summary(client.siem.messages.delivered(SinceSeconds(3600)))
    print_siem_data_summary(client.siem.issues(SinceSeconds(3600)))
    print_siem_data_summary(client.siem.all(SinceSeconds(3600)))
