import requests

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
        print(response.json())
    except Exception as e:
        print("SmS sending failed",e)

def advanta_sms_balance(apikey,partnerid):

    # api_key = "f16edddd5e53dc3242f9fb9ad904ee5e"
    # partner_id = 3886

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


