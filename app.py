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


def bind_country_state(proxy_list):
    country_region_dict = defaultdict(list)
    for proxy in proxy_list:
        country_region_dict[proxy['Country']].extend(
            region for region in [proxy['Region']] if region not in country_region_dict[proxy['Country']]
        )
    return dict(country_region_dict)


@app.route("/api/data", methods=["GET"])
def get_data():
    client = TrueSocksClient(api_key="b03a14b7128ec274b4abb70e164399b3")
    # Define your data or retrieve it from a source
    response_dict = client.get_response_dict()
    proxy_list = response_dict["result"][
        "ProxyList"
    ]
    # each country and it's states
    country_region_dict = bind_country_state(proxy_list)

    return jsonify(country_region_dict)


if __name__ == "__main__":
    # Start the Flask application in a separate thread
    flask_thread = Thread(target=app.run(port=8000))
    flask_thread.start()

    # Start the Telegram bot

    # Wait for the Flask thread to finish
    flask_thread.join()
