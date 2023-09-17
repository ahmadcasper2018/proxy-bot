import requests


def rotate_country_mapper(original_list):
    new_list = [{country_dict["country_name"]: country_dict["id"]} for country_dict in original_list]
    return new_list


def rotate_city_mapper(original_list):
    new_list = [{"city": {"name": city_dict["city_name"], "country_id": city_dict["country_id"],
                          "city_name": city_dict["city_name"]}} for city_dict in original_list]
    return new_list


def extract_country_names(country_list):
    return [country["country_name"] for country in country_list]


class RotateClient:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.access_token = None
        self.email = email
        self.password = password
        self._login()

    def _update_headers(self):
        if self.access_token:
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            self.headers = {}

    def _login(self):
        url = f"{self.base_url}login"
        data = {"email": self.email, "password": self.password}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            login_response = response.json()
            self.access_token = login_response.get("token")
            self._update_headers()
            print('updated')

    def list_all_countries(self):
        url = f"{self.base_url}countries"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def list_all_cities_in_country(self, country_id):
        url = f"{self.base_url}cities"
        params = {"country_id": country_id}
        response = requests.get(url, params=params, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def list_all_service_providers_in_city(self, city_id):
        url = f"{self.base_url}service-providers"
        params = {"city_id": city_id}
        response = requests.get(url, params=params, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def list_all_parent_proxies(self, service_provider_city_id):
        url = f"{self.base_url}parent-proxies"
        params = {"service_provider_city_id": service_provider_city_id}
        response = requests.get(url, params=params, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_customer_balance(self):
        url = f"{self.base_url}balance"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_proxies_prices(self):
        url = f"{self.base_url}prices"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def get_proxy_account_details(self, id):
        url = f"{self.base_url}proxies/{id}"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def create_proxy_account(self, parent_proxy_id, protocol, username, password, duration):
        url = f"{self.base_url}proxies"
        data = {
            "parent_proxy_id": parent_proxy_id,
            "protocol": protocol,
            "username": username,
            "password": password,
            "duration": duration
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def renew_proxy_account(self, id, duration):
        url = f"{self.base_url}proxies/{id}/renew"
        data = {"duration": duration}
        response = requests.post(url, json=data, headers=self.headers)
        return response.json() if response.status_code == 200 else None

    def modify_proxy_account(self, id, parent_proxy_id=None, protocol=None, password=None):
        url = f"{self.base_url}proxies/{id}"
        data = {}
        if parent_proxy_id:
            data["parent_proxy_id"] = parent_proxy_id
        if protocol:
            data["protocol"] = protocol
        if password:
            data["password"] = password
        response = requests.put(url, json=data, headers=self.headers)
        return response.json() if response.status_code == 200 else None
