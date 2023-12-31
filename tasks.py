# tasks.py
from celery import Celery
from api import TrueSocksClient, PremSocksClient
from decouple import config
import os

app = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)
app.config_from_object("celery_config")


@app.task
def get_daily_socks_proxies():
    client = TrueSocksClient(api_key=config("SOCKS_API_KEY"))
    response_dict = client.get_response_dict()
    # Process the response data as needed
    return response_dict


# @app.task
# def get_perm_socks_usa():
#     client = PremSocksClient(api_key=config("SOCKS_PREM"))
#     response_dict = client.get_usa()
#     # Process the response data as needed
#     return response_dict
#
#
# @app.task
# def get_perm_socks_uk():
#     client = PremSocksClient(api_key=config("SOCKS_PREM"))
#     response_dict = client.get_uk()
#     # Process the response data as needed
#     return response_dict
#
#
# @app.task
# def get_perm_socks_spain():
#     client = PremSocksClient(api_key=config("SOCKS_PREM"))
#     response_dict = client.get_spain()
#     # Process the response data as needed
#     return response_dict
#
#
# @app.task
# def get_perm_socks_canada():
#     client = PremSocksClient(api_key=config("SOCKS_PREM"))
#     response_dict = client.get_canada()
#     # Process the response data as needed
#     return response_dict
#
#
# @app.task
# def get_perm_socks_germany():
#     client = PremSocksClient(api_key=config("SOCKS_PREM"))
#     response_dict = client.get_german()
#     # Process the response data as needed
#     return response_dict
