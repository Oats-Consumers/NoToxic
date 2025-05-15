from my_secrets import OPENDOTA_API_KEY
import requests


class OpenDotaClient:
    __api_key = ""
    def __init__(self, api_key = OPENDOTA_API_KEY):
        self.__api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.__api_key}"} if self.__api_key else {}

    PARSED_MATCHES_URL = "https://api.opendota.com/api/parsedMatches"
    RANDOM_MATCHES_URL = "https://api.opendota.com/api/publicMatches"
    MATCH_DETAILS_URL  = "https://api.opendota.com/api/matches/{}"
    REPARSE_MATCH_URL  = "https://api.opendota.com/api/request/{}"
    PLAYER_INFO_URL    = "https://api.opendota.com/api/players/{}"
    RECENT_MATCHES_URL = "https://api.opendota.com/api/players/{}/matches"
    WIN_LOSE_URL = "https://api.opendota.com/api/players/{}/wl"

    DEFAULT_ENGLISH_REGIONS = [1, 2, 3, 5, 6, 7, 11]
    INITIAL_STEAM_ID64 = 76561197960265728


    def get_public_matches(self, less_than_match_id, parsed_matches = True):
        url = self.PARSED_MATCHES_URL if parsed_matches else self.RANDOM_MATCHES_URL
        response = requests.get(url, params = {"less_than_match_id": less_than_match_id}, headers=self.headers)
        response.raise_for_status()
        return response.json()


    def get_match_details(self, match_id):
        response = requests.get(self.MATCH_DETAILS_URL.format(match_id), headers=self.headers)
        response.raise_for_status()
        return response.json()

    def reparse_match(self, match_id):
        url = self.REPARSE_MATCH_URL.format(match_id)
        return requests.post(url, headers=self.headers)

    def get_player_info(self, account_id):
        if account_id >= self.INITIAL_STEAM_ID64:
            account_id = account_id - self.INITIAL_STEAM_ID64
        response = requests.get(self.PLAYER_INFO_URL.format(account_id), headers=self.headers)
        response.raise_for_status()
        return response.json()


    def get_player_matches(self, account_id, limit = 20, offset = 0):
        if account_id >= self.INITIAL_STEAM_ID64:
            account_id = account_id - self.INITIAL_STEAM_ID64
        response = requests.get(self.RECENT_MATCHES_URL.format(account_id), params= {"limit": limit, "offset": offset}, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_player_win_lose(self, account_id):
        if account_id >= self.INITIAL_STEAM_ID64:
            account_id = account_id - self.INITIAL_STEAM_ID64
        response = requests.get(self.WIN_LOSE_URL.format(account_id), headers=self.headers)
        response.raise_for_status()
        return response.json()
