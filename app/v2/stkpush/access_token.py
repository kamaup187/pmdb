
import os
import base64
import requests
import datetime
from requests.auth import HTTPBasicAuth

def generate_access_token2():
    """Generates access token"""

    #SandBox app keys
    # consumer_key = "Cp8hZIOFImG242bfmDlhxtiYE6phuew6"
    # consumer_secret = "jOo0CLfr3rdMD5GM"
    # api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"


    # #Production app keys
    consumer_key = "bfYClGX6NynbJJd4ZGuXZtQ3jMQ44ZQe"
    consumer_secret = "rq67j4audtr9injQ"


    api_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    except:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret), verify=False)

    json_response = (r.json())
    # json_response = r
    # import pdb; pdb.set_trace()
    my_access_token = json_response["access_token"]
    # print(my_access_token)
    return my_access_token

def generate_access_token():
    """Generates access token"""

    #SandBox app keys
    # consumer_key = "Cp8hZIOFImG242bfmDlhxtiYE6phuew6"
    # consumer_secret = "jOo0CLfr3rdMD5GM"
    # api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # #Production app keys
    consumer_key = "TwoysRhF1D0isV2EW0rhVLTPaKf8I0wA"
    consumer_secret = "CctpaldtiOnrGqDi"
    api_URL = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    except:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret), verify=False)

    json_response = (r.json())
    # json_response = r
    # import pdb; pdb.set_trace()
    my_access_token = json_response["access_token"]
    # print(my_access_token)
    return my_access_token

def register_url():

    my_access_token = generate_access_token()

    api_url = "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"

    headers = {"Authorization": "Bearer %s" % my_access_token}

    request = {
        "ShortCode": "4012401",
        "ResponseType": "Completed",
        "ConfirmationURL": "https://kiotapay.com/promitech/payment",
        "ValidationURL":   "https://kiotapay.com/promitech/validation",
    }

    try:
        response = requests.post(api_url, json=request, headers=headers)
    except:
        response = requests.post(api_url, json=request, headers=headers, verify=False)

    print(response.text)


def register_url2():

    my_access_token = generate_access_token2()

    api_url = "https://api.safaricom.co.ke/mpesa/c2b/v1/registerurl"

    headers = {"Authorization": "Bearer %s" % my_access_token}

    request = {
        "ShortCode": "4081687",
        "ResponseType": "Completed",
        "ConfirmationURL": "https://kiotapay.com/kiotapay/payment",
        "ValidationURL":   "https://kiotapay.com/kiotapay/validation",
    }

    try:
        response = requests.post(api_url, json=request, headers=headers)
    except:
        response = requests.post(api_url, json=request, headers=headers, verify=False)

    print(response.text)


class LipanaMpesaPassword:

    #Production vars
    business_short_code = "4012401"
    passkey = '29d271b12693dc1042f288445db35fd1f85cc659cd249cb3f925e57bda36eb5f'

    # #sandbox vars
    # business_short_code = "174379"
    # passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    lipa_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')

class LipanaMpesaPassword2:

    #Production vars
    business_short_code2 = "4081687"
    passkey2 = '29d271b12693dc1042f288445db35fd1f85cc659cd249cb3f925e57bda36eb5f'

    # #sandbox vars
    # business_short_code = "174379"
    # passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    lipa_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = business_short_code2 + passkey2 + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')


def lipa_na_mpesa_online(amount,tel):
    access_token = generate_access_token()

    request = {
    "BusinessShortCode": LipanaMpesaPassword.business_short_code,
    "Password": LipanaMpesaPassword.decode_password,
    "Timestamp": LipanaMpesaPassword.lipa_time,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": amount,
    "PartyA": tel,
    "PartyB": LipanaMpesaPassword.business_short_code,
    "PhoneNumber": tel,
    "CallBackURL": "https://kiotapay.com/datareceive",
    "AccountReference": "kiotapay",
    "TransactionDesc": "Account"
    }
 
    # api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {"Authorization": "Bearer %s" % access_token}
    response = requests.post(api_url, json=request, headers=headers)
    
    # print(response.text)
    # print(response.status_code)
    return response

def lipa_na_mpesa_online2(amount,tel):
    access_token = generate_access_token2()

    request = {
    "BusinessShortCode": LipanaMpesaPassword2.business_short_code,
    "Password": LipanaMpesaPassword2.decode_password,
    "Timestamp": LipanaMpesaPassword2.lipa_time,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": amount,
    "PartyA": tel,
    "PartyB": LipanaMpesaPassword2.business_short_code,
    "PhoneNumber": tel,
    "CallBackURL": "https://kiotapay.com/kiotapay/datareceive",
    "AccountReference": "kiotapay",
    "TransactionDesc": "Account"
    }
 
    # api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {"Authorization": "Bearer %s" % access_token}
    response = requests.post(api_url, json=request, headers=headers)
    
    # print(response.text)
    # print(response.status_code)
    return response

def stkquery(cri):
    access_token = generate_access_token()
    # api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    api_url = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = { 
        "BusinessShortCode": LipanaMpesaPassword.business_short_code,
        "Password": LipanaMpesaPassword.decode_password,
        "Timestamp": LipanaMpesaPassword.lipa_time,
        "CheckoutRequestID": cri
    }

    response = requests.post(api_url, json = request, headers=headers)

    return response

def stkquery2(cri):
    access_token = generate_access_token()
    # api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    api_url = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = { 
        "BusinessShortCode": LipanaMpesaPassword2.business_short_code,
        "Password": LipanaMpesaPassword2.decode_password,
        "Timestamp": LipanaMpesaPassword2.lipa_time,
        "CheckoutRequestID": cri
    }

    response = requests.post(api_url, json = request, headers=headers)

    return response

# register_url2()