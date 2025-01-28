import json

from tap_api.v2 import *

if __name__ == "__main__":
    # Load API key
    with open("../tap.api_key", "r") as api_key_file:
        api_key_data = json.load(api_key_file)
    api_key = api_key_data.get("demous")

    client = Client(api_key.get("PRINCIPAL"), api_key.get("SECRET"))

    # URI Modeling
    print(client.forensics._uri)

    # Fetch forensic data. Note, client.forensics.campaign is not an object, the nature of the API made it simpler
    # to just have a function called campaign() and threat() accepting the correct arguments. This may change in the
    # future with backward compatability
    aggregate_data = client.forensics.campaign("<campaign_id_here>")
    print("\nForensic Data:")
    print("HTTP Status:", aggregate_data.get_status())
    print("HTTP Reason:", aggregate_data.get_reason())

    for report in aggregate_data.reports:
        print("\nReport:")
        print(f"  Scope: {report.scope}")
        print(f"  ID: {report.id}")
        print(f"  Name: {report.name}")
        print(f"  Threat Status: {report.threat_status}")

        for forensic in report.forensics:
            print("\n  Forensic:")
            print(f"    Type: {forensic.type}")
            print(f"    Display: {forensic.display}")
            print(f"    Engine: {forensic.engine}")
            print(f"    Malicious: {forensic.malicious}")
            print(f"    Time: {forensic.time}")
            print(f"    Note: {forensic.note or 'N/A'}")

            # Dump the `what` object
            print("    What ({}):".format(type(forensic.what).__name__))
            print(json.dumps(forensic.what, indent=4))

            if forensic.platforms:
                print("    Platforms:")
                for platform in forensic.platforms:
                    print(f"      Name: {platform.name}")
                    print(f"      OS: {platform.os}")
                    print(f"      Version: {platform.version}")
