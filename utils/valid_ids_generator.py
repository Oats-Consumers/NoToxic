import requests
import time

from clients import OPEN_DOTA_CLIENT

DEFAULT_ENGLISH_REGIONS = [1, 2, 3, 5, 6, 7, 11 ]

def fetch_valid_ids(target_count=10, valid_regions=None, delay=1.2, after_match_id=None):

    if valid_regions is None:
        valid_regions = DEFAULT_ENGLISH_REGIONS

    match_ids = []
    last_match_id = after_match_id or 8252323701

    while len(match_ids) < target_count:
        try:
            public_matches = OPEN_DOTA_CLIENT.get_public_matches(last_match_id)
        except requests.RequestException as e:
            print(f"Error fetching public matches: {e}")
            break

        if not public_matches:
            print("No matches found.")
            break

        for match in public_matches:
            match_id = match.get("match_id")
            if not match_id:
                continue

            try:
                match_detail = OPEN_DOTA_CLIENT.get_match_details(match_id)
                region = match_detail.get("region")
                if region in valid_regions:
                    match_ids.append(match_id)
                    print(f"✔ Match {match_id} accepted (region: {region})")
                else:
                    print(f"✘ Match {match_id} skipped (region: {region})")

                if len(match_ids) >= target_count:
                    break

                time.sleep(delay)

            except requests.RequestException as e:
                print(f"Error fetching match {match_id}: {e}")

        last_match_id = public_matches[-1].get("match_id")
        time.sleep(delay)

    return match_ids, last_match_id

if __name__ == "__main__":
    desired_count = int(input("How many match IDs would you like? "))
    ids = fetch_valid_ids(target_count=desired_count)
    print("\nValid match IDs:")
    print(ids)
