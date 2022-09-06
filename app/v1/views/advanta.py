import requests
# from app.v1.models.operations import *
# from .helperfuncs import *

# try:
#     from do_secrets import *
# except ImportError:
#     APP_SETTINGS = None

# configuration = os.getenv('APP_SETTINGS') or APP_SETTINGS



# def advanta_sms(txt,tel):

#     url = "https://quicksms.advantasms.com/api/services/sendsms/"
#     # url = "https://quicksms.advantasms.com/api/services/sendbulk/"



#     payload = {
#     "apikey":api_key,
#     "partnerID":partner_id,
#     "message":txt,
#     "shortcode":"LESAMA",
#     "mobile":tel
#     }

#     # payload = {
#     #     "count": 3,
#     #     "smslist": [
#     #         {
#     #             "apikey":api_key,
#     #             "partnerID":partner_id,
#     #             "mobile":tel,
#     #             "pass_type": "plain",
#     #             "clientsmsid": 1234,
#     #             "message":txt,
#     #             "message": "This is a test message 1 \n Kiotapay Team",
#     #             "shortcode": "Advanta"
#     #         },
#     #         {
#     #             "apikey":api_key,
#     #             "partnerID":partner_id,
#     #             "mobile":tel,
#     #             "clientsmsid": 1235,
#     #             "message":txt,
#     #             "shortcode": "Advanta",
#     #             "pass_type": "plain"
#     #         },
#     #         {
#     #             "apikey":api_key,
#     #             "partnerID":partner_id,
#     #             "mobile":tel,
#     #             "clientsmsid": 1236,
#     #             "message":txt,
#     #             "shortcode": "Advanta",
#     #             "pass_type": "plain"
#     #         }
#     #     ]
#     # }

#     try:

#         response = requests.post(url, json=payload)
#         print(response.json())
#     except Exception as e:
#         print("SmS sending failed",e)


# def advanta_balance():

#     api_key = "cfc7c4382ae6d4277d8c09419a897c9e"
#     partner_id = 3895

#     payload = {
#     "apikey":api_key,
#     "partnerID":partner_id
#     }

#     url = "https://quicksms.advantasms.com/api/services/getbalance/"
#     try:
#         response = requests.get(url, json=payload)
#         # print("LESAMA SMS BALANCE: ",response.json())
#         bal = response.json()["credit"]

#     except Exception as e:
#         bal = 0
#         print (e)
        
#     try:
#         balance = float(bal)
#     except Exception as e:
#         balance = 0
#         print(e)

#     return f"{balance:,.0f}"


def advanta_send_sms(txt,tel,apikey,partnerid,shortcode):

    url = "https://quicksms.advantasms.com/api/services/sendsms/"

    payload = {
    "apikey":apikey,
    "partnerID":partnerid,
    "message":txt,
    "shortcode":shortcode,
    "mobile":tel
    }

    try:
        response = requests.post(url, json=payload)
        print("ADVANTA sms sending successful")
    except Exception as e:
        response = ""
        print("ADVANTA sms sending failed",e)

    try:
        print(response.json())
        print(response.json()["responses"])
        print(response.json()["responses"][0])
        print(response.json()["responses"][0]["messageid"])

        msgid = response.json()["responses"][0]["messageid"]
        print("ADVANTA sms response success")
    except Exception as e:
        print("ADVANTA sms response error",e)
        msgid = ""

    if msgid:
        respdict = {
        "apikey":apikey,
        "partnerID":partnerid,
        "msgid":msgid
        }
    else:
        respdict = None

    return respdict

def advanta_sms_balance(apikey,partnerid):

    payload = {
    "apikey":apikey,
    "partnerID":partnerid
    }

    url = "https://quicksms.advantasms.com/api/services/getbalance/"

    response = requests.get(url, json=payload)

    try:
        response = requests.get(url, json=payload)
        bal = response.json()["credit"]

    except Exception as e:
        bal = 0
        print (e)
        
    try:
        balance = float(bal)
    except Exception as e:
        balance = 0
        print(e)

    return f"{balance:,.0f}"

def afrinet_sms_balance(apikey,partnerid):

    payload = {
    "partnerID":partnerid,
    "apikey":apikey
    }

    url = "https://quicksms.advantasms.com/api/services/getbalance/"

    # url = "https://bulksms.afrinettelecom.co.ke/api/services/getbalance/"

    # response = requests.get(url, json=payload)

    try:
        response = requests.get(url, json=payload)

        print("this is the response",response.json())

        bal = response.json()["credit"]

    except Exception as e:
        bal = 0
        print (e)
        
    try:
        balance = float(bal)
    except Exception as e:
        balance = 0
        print(e)

    return f"{balance:,.0f}"



# advanta_sms_delivery("fad3000bcfdfb541291ebc018bcc7868",2627,"ZAgSmYcHm5c1cfq5")

def afrinet_send_sms(txt,tel,apikey,partnerid,shortcode):

    url = "https://quicksms.advantasms.com/api/services/sendsms/"

    # url = "https://bulksms.afrinettelecom.co.ke/api/services/sendsms/"

    payload = {
    "apikey":apikey,
    "partnerID":partnerid,
    "message":txt,
    "shortcode":shortcode,
    "mobile":tel
    }

    try:
        response = requests.post(url, json=payload)
        print("ADVANTA sms sending successful")
    except Exception as e:
        response = ""
        print("ADVANTA sms sending failed",e)

    try:
        print(response.json())
        print(response.json()["responses"])
        print(response.json()["responses"][0])
        print(response.json()["responses"][0]["messageid"])

        msgid = response.json()["responses"][0]["messageid"]
        print("ADVANTA sms response success")
    except Exception as e:
        print("ADVANTA sms response error",e)
        msgid = ""

    if msgid:
        respdict = {
        "apikey":apikey,
        "partnerID":partnerid,
        "msgid":msgid
        }
    else:
        respdict = None

    return respdict