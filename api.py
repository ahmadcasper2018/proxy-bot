import requests
import json


class TrueSocksClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.truesocks.net/"

    def list_search(self):
        params = {
            "key": self.api_key,
            "cmd": "ListOnline",
        }
        headers = {"Accept-Encoding": "gzip"}
        response = requests.get(self.base_url, params=params, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print("Error: Failed to fetch data from API")
            return None

    def get_response_dict(self):
        data = self.list_search()
        if not data:
            return {}
        response_dict = json.loads(data)
        return response_dict


class PremSocksClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://premsocks.com/api/v1/socks/"

    def get_country_proxies(self, country):
        if not isinstance(country, str) or not country.strip():
            raise ValueError("Country must be a non-empty string")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"country": country}

        try:
            response = requests.get(
                self.base_url + "list", params=params, headers=headers
            )
            response.raise_for_status()  # Raise an exception for non-2xx responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch data from API: {e}")

    def get_usa(self):
        return self.get_country_proxies("US")

    def get_german(self):
        return self.get_country_proxies("DE")

    def get_uk(self):
        return self.get_country_proxies("GB")

    def get_canada(self):
        return self.get_country_proxies("CA")

    def get_spain(self):
        return self.get_country_proxies("ES")
