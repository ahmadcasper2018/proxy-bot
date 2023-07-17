import json
import os
from collections import defaultdict

from dotenv import load_dotenv
from flask import Flask, jsonify
from threading import Thread
from bot import start_bot
from api import TrueSocksClient

load_dotenv()

# Create Flask application
app = Flask(__name__)


def filter_by_state(proxy_list, state):
    filtered_proxies = [proxy for proxy in proxy_list if proxy["Region"] == state]
    return filtered_proxies


def filter_proxy_by_isp(proxy_list, target_isp):
    filtered_proxy_list = [proxy for proxy in proxy_list if proxy["ISP"] == target_isp]
    return filtered_proxy_list


def bind_country_state(proxy_list):
    country_region_dict = defaultdict(list)
    for proxy in proxy_list:
        country_region_dict[proxy["Country"]].extend(
            region
            for region in [proxy["Region"]]
            if region not in country_region_dict[proxy["Country"]]
        )
    return dict(country_region_dict)


def bind_country_isp(proxy_list):
    country_isp_dict = defaultdict(set)
    for proxy in proxy_list:
        country_isp_dict[proxy["Country"]].add(proxy["ISP"])
    return {country: list(isps) for country, isps in country_isp_dict.items()}


@app.route("/api/data", methods=["GET"])
def get_data():
    client = TrueSocksClient(api_key="b03a14b7128ec274b4abb70e164399b3")
    # Define your data or retrieve it from a source
    response_dict = client.get_response_dict()
    proxy_list = response_dict["result"]["ProxyList"]
    # each country and it's states
    country_region_dict = bind_country_isp(proxy_list)

    return jsonify(country_region_dict)


if __name__ == "__main__":
    flask_thread = Thread(target=app.run(port=8000))
    flask_thread.start()

    # Start the Telegram bot

    # Wait for the Flask thread to finish
    flask_thread.join()

