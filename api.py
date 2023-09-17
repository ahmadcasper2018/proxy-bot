import random
import time

import requests
import json
import os
from decouple import config


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

    def order(self, proxy):
        params = {"key": self.api_key, "cmd": "RegularProxyBuy", "proxyid": proxy}
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()
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
        self.max_retries = 12  # Maximum number of retries
        self.retry_delay = 10  # Delay between retries in seconds

    def get_country_proxies(self, country, isp):
        if not isinstance(country, str) or not country.strip():
            raise ValueError("Country must be a non-empty string")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"country": country}
        if isp:
            params.update({"isp": isp})

        for _ in range(self.max_retries):
            try:
                response = requests.get(
                    self.base_url + "list", params=params, headers=headers
                )
                response.raise_for_status()  # Raise an exception for non-2xx responses
                return response.json()
            except requests.exceptions.RequestException as e:
                if response.status_code == 429:
                    print("Rate limit exceeded. Retrying after a delay...")
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"Failed to fetch data from API: {e}")

        raise Exception("Failed to fetch data from API after multiple retries")

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

    @classmethod
    def get_isp_for_country(self, country):
        if country == "UNITED STATES":
            return [
                "AT&T Services",
                "CenturyLink",
                "Spectrum",
                "Comcast Cable",
                "Cox Communications",
                "T-Mobile USA",
                "verizon",
            ]
        elif country == "GERMANY":
            return [
                "Alibaba",
                "Vodafone Germany",
                "Oracle Cloud",
                "Contabo GmbH",
                "1&1 Internet AG",
                "Microsoft Azure",
                "servinga GmbH",
            ]
        elif country == "UNITED KINGDOM":
            return [
                "Giganet Limited",
                "Digital Ocean",
                "BT",
                "TalkTalk",
                "EE",
                "Oracle Cloud",
                "Wireless Logic Limited",
                "Sky Broadband",
            ]
        elif country == "CANADA":
            return [
                "EBOX",
                "OVH SAS",
                "Cogeco Connexion Inc.",
                "Telus Communications",
                "Videotron Ltee",
                "Rogers Cable",
                "Shaw Communications",
            ]
        else:
            return [
                "Vodafone Spain",
                "Telefonica de Espana",
                "Orange Espana",
                "Starlink",
                "Aire Networks",
                "Cloudwifi, Sl",
                "Ibercom Telecom",
            ]

    def get_final_proxies(self, country, isp):
        return self.get_country_proxies(country, isp)

    def get_random_proxy(self, country, isp):
        proxies = self.get_final_proxies(country, isp)["data"]
        if proxies:
            return random.choice(proxies)["id"]
        else:
            return None

    def order_proxy(self, country, isp):
        proxy_id = self.get_random_proxy(country, isp)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(self.base_url + str(proxy_id), headers=headers)
        return response.json()

