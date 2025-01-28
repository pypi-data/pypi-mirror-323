import json
from datetime import timedelta, datetime, timezone

from tap_api.v2 import *

if __name__ == "__main__":
    # Load API key
    with open("../tap.api_key", "r") as api_key_file:
        api_key_data = json.load(api_key_file)
    api_key = api_key_data.get("demous")

    client = Client(api_key.get("PRINCIPAL"), api_key.get("SECRET"))

    # URI Modeling
    print(client.campaign._uri)
    print(client.campaign.ids._uri)
    print(client.campaign["<campaign_id_here>"]._uri)

    # Retrieve campaign data
    campaign_data = client.campaign.ids(
        StartEndInterval(datetime.now(timezone.utc) - timedelta(hours=24), datetime.now(timezone.utc))
    )

    print("Campaign Data Status:", campaign_data.get_status())
    print("Reason:", campaign_data.get_reason())

    for info in campaign_data.campaigns:
        print("\nCampaigns:")
        print(f"  ID: {info.id}")
        print(f"  Last Updated At: {info.last_updated_at}")

    # Fetch campaign summary
    campaign_summary = client.campaign["<campaign_id_here>"]()
    print("\nCampaign Summary:")
    print("HTTP Status:", campaign_summary.get_status())
    print("HTTP Reason:", campaign_summary.get_reason())

    print("\nCampaign:")
    print(f"  ID: {campaign_summary.id}")
    print(f"  Name: {campaign_summary.name}")
    print(f"  Description: {campaign_summary.description}")
    print(f"  Start Date: {campaign_summary.start_date}")

    for campaign_member in campaign_summary.campaign_members:
        print("\n  Campaign Member:")
        print(f"    ID: {campaign_member.id}")
        print(f"    Name: {campaign_member.name}")
        print(f"    Type: {campaign_member.type}")
        print(f"    Sub Type: {campaign_member.sub_type}")
        print(f"    Threat Time: {campaign_member.threat_time}")

    for actor in campaign_summary.actors:
        print("\n  Campaign Actor:")
        print(f"    ID: {actor.id}")
        print(f"    Name: {actor.name}")

    for malware in campaign_summary.malware:
        print("\n  Malware:")
        print(f"    ID: {malware.id}")
        print(f"    Name: {malware.name}")

    for technique in campaign_summary.techniques:
        print("\n  Technique:")
        print(f"    ID: {technique.id}")
        print(f"    Name: {technique.name}")

    for family in campaign_summary.families:
        print("\n  Family:")
        print(f"    ID: {family.id}")
        print(f"    Name: {family.name}")
