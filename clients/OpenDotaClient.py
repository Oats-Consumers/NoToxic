from my_secrets import OPENDOTA_API_KEY
import requests


class OpenDotaClient:
    __api_key = ""
    def __init__(self, api_key = OPENDOTA_API_KEY):
        self.__api_key = api_key

    PARSED_MATCHES_URL = "https://api.opendota.com/api/parsedMatches"
    RANDOM_MATCHES_URL = "https://api.opendota.com/api/publicMatches"
    MATCH_DETAILS_URL = "https://api.opendota.com/api/matches/{}"
    REPARSE_MATCH_URL = "https://api.opendota.com/api/request/{}"

    DEFAULT_ENGLISH_REGIONS = [1, 2, 3, 5, 6, 7, 11]
    HEADERS = {"Authorization": f"Bearer {__api_key}"} if __api_key else {}


    def get_public_matches(self, less_than_match_id, parsed_matches = True):
        url = self.PARSED_MATCHES_URL if parsed_matches else self.RANDOM_MATCHES_URL
        response = requests.get(url, params = {"less_than_match_id": less_than_match_id}, headers=self.HEADERS)
        response.raise_for_status()
        return response.json()


    def get_match_details(self, match_id):
        response = requests.get(self.MATCH_DETAILS_URL.format(match_id), headers=self.HEADERS)
        response.raise_for_status()
        return response.json()

    def reparse_match(self, match_id):
        url = self.REPARSE_MATCH_URL.format(match_id)
        return requests.post(url, headers=self.HEADERS)






