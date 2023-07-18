import json
import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from threading import Thread
from bot import start_bot
from api import TrueSocksClient
from utils import *

load_dotenv()

# Create Flask application
app = Flask(__name__)


@app.route("/api/data", methods=["GET"])
def get_data():
    client = TrueSocksClient(api_key="b03a14b7128ec274b4abb70e164399b3")
    # Define your data or retrieve it from a source
    response_dict = client.get_response_dict()
    proxy_list = response_dict["result"]["ProxyList"]
    # each country and it's states
    country_region_dict = bind_country_state(proxy_list)

    return jsonify(country_region_dict)


if __name__ == "__main__":
    # flask_thread = Thread(target=app.run(port=8000))
    # flask_thread.start()
    # flask_thread.join()
    start_bot()
