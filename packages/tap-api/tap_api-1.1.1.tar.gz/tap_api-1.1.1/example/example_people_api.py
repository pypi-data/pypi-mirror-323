import json

from tap_api.v2 import *

if __name__ == "__main__":
    # Load API key
    with open("../tap.api_key", "r") as api_key_file:
        api_key_data = json.load(api_key_file)
    api_key = api_key_data.get("demous")

    client = Client(api_key.get("PRINCIPAL"), api_key.get("SECRET"))

    # URI Modeling
    print(client.people._uri)
    print(client.people.vap._uri)

    # Dump VAP info
    vap_info = client.people.vap(TimeWindow.DAYS_90)
    print("\nVAP Info:")
    print("HTTP Status:", vap_info.get_status())
    print("HTTP Reason:", vap_info.get_reason())
    print("Total VAPs:", vap_info.total_vap_users)
    print("Interval:", vap_info.interval)
    print("Average Attack Index:", vap_info.average_attack_index)
    print("VAP Attack Threshold:", vap_info.vap_attack_index_threshold)

    for user in vap_info.users:
        identity = user.identity
        threat_statistics = user.threat_statistics

        print("\nUser Details:")
        print("  Email(s):", identity.emails)
        print("  Name:", identity.name or "N/A")
        print("  Department:", identity.department or "N/A")
        print("  Location:", identity.location or "N/A")
        print("  Title:", identity.title or "N/A")
        print("  VIP:", identity.vip)

        print("Threat Statistics:")
        print("  Attack Index:", threat_statistics.attack_index)
        print("  Threat Families:")
        for family in threat_statistics.families:
            print(f"    - {family.name}: {family.score}")
