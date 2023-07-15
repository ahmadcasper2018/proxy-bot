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


# class Client:
#     def __init__(self, url):
#         self.url = url
#
#     def fetch_data(self):
#         response = requests.get(self.url)
#         if response.status_code == 200:
#             return response.content
#         else:
#             print('Error: Failed to fetch data from API')
#             return 0
#
#     def get_response_dict(self):
#         data = self.fetch_data()
#         if data == 0:
#             return {}
#         response_dict = json.loads(data)
#         return response_dict
