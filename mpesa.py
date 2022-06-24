
import os
import base64
import requests
import datetime
from requests.auth import HTTPBasicAuth

#4089507

def generate_access_token():
    """Generates access token"""

    consumer_key = "dkjAjqY5uL8m9xWGcaY3B64phATdfZiS"
    consumer_secret = "IgymMzc9ie9IDSBe"

    api_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    except:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret), verify=False)

    json_response = (r.json())
    my_access_token = json_response["access_token"]
    return my_access_token

print(generate_access_token())

def register_url():

    my_access_token = generate_access_token()

    api_url = "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"

    headers = {"Authorization": "Bearer %s" % my_access_token}

    request = {
        "ShortCode": "4074689",
        "ResponseType": "Completed",
        "ConfirmationURL": "https://kiotapay.com/m/astrol/ins/payment",
        "ValidationURL":   "https://kiotapay.com/m/astrol/validate",
    }

    try:
        response = requests.post(api_url, json=request, headers=headers)
    except:
        response = requests.post(api_url, json=request, headers=headers, verify=False)

    print(response.text)

register_url()





