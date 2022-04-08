
import os
import base64
import requests
import datetime
from requests.auth import HTTPBasicAuth

#4089507

def generate_access_token():
    """Generates access token"""

    consumer_key = "3KdxBRnYExGYNpPOBgpn6J9QjOp0KCWo"
    consumer_secret = "4Of5iIe0GjbGu2O3"

    api_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    except:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret), verify=False)

    json_response = (r.json())
    my_access_token = json_response["access_token"]
    return my_access_token

def register_url():

    my_access_token = generate_access_token()

    api_url = "https://api.safaricom.co.ke/mpesa/c2b/v2/registerurl"

    headers = {"Authorization": "Bearer %s" % my_access_token}

    request = {
        "ShortCode": "4089507",
        "ResponseType": "Completed",
        "ConfirmationURL": "https://kiotapay.com/vintage/payment",
        "ValidationURL":   "https://kiotapay.com/vintage/validation",
    }

    try:
        response = requests.post(api_url, json=request, headers=headers)
    except:
        response = requests.post(api_url, json=request, headers=headers, verify=False)

    print(response.text)

register_url()





