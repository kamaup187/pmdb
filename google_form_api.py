
# from __future__ import print_function

# from apiclient import discovery
# from httplib2 import Http
# from oauth2client import client, file, tools

# SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
# DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

# store = file.Storage('token.json')
# creds = None

# if not creds or creds.invalid:
#     flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
#     creds = tools.run_flow(flow, store)
# service = discovery.build('forms', 'v1', http=creds.authorize(
#     Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

# # Prints the title of the sample form:
# form_id = "1UIpdGHUQ_t1tZR2690E6jjOVI_KdNQ_AQeCWomHe5Co"

# result = service.forms().responses().list(formId=form_id).execute()
# print(result)

# import pdb; pdb.set_trace()








# from httplib2 import Http
# import os

# from apiclient import discovery
# from oauth2client import service_account

# SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
# DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

# creds = {
#   "type": "service_account",
#   "project_id": "kiotapay-384101",
#   "private_key_id": "665d39a4c98515f7393f7f84a03cca168d46d53e",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDfeOvYpeWnjKTk\nzbFCZoMNeR2qHJYGU9cU2xTy7PEczRVcyNiIGkkm5KEygQvR+TQp+w30qxMCXWLe\nVL8aV4kjHCihLsFifPeJNPdemy9OKyGYbsqQaJl/vGK61PRY2Nlz15xsq8Kr4cJo\nD8Z8YhdLVQlgapxGiQa4L+o/D3cOvcMVlTMPwa2J9/h9Y5zoczIgm4UBts4bCeQu\nRZTE2XqFlwzMlBv3FOmM/4rK7TFmOkXfV0Q2GJeGpl5Cqz7ck3TEalFao1IzM035\nwYeBIQe8m/WXcMcDCFe8jbqjg/UmNGGwh9jeAaeV2rFzNa5evA1XdGau66Uqy9c4\nV6QTFZ2hAgMBAAECggEAE8VwxlbtId0DZLvfFDMaIqnFylxjmJU32QBGEvUMIwJx\nAqfBYo9CzBZbvaplp5Le/tzXn/83vBSTj/ya+MNoXmsaHCKVGPfZ9bFyNlRQA+A0\nhXY95Tdf50l9Sa7YHHk5CfL4Q7QRkd/0MX090BjkmzVfkkB0aZgreEXC+YfOfob4\nnZOz2YqLhp1UriU2bfRXlVt0xqI56BDd/WQCITgXMALDLsofWd17JXmITwiz9TH6\nQ5jkhS2lW7ao2JKIA3uZCZcelr4MC7jS01oY0DDgLYQWWhttkFBpUnNDTzJtrfH4\n6jkwHjfRJorXZmN4TLjB/RzXLbgNUreijCsoU3OvzQKBgQD42MHpZaWgGFqOz7tD\npZY5gjsiLjOBPvOW+pqpmRVGniMM6ZQTDjFv3NI70kc7LYu66Q9/810vRY8K7NVt\n0lX5UD6rJfHUoMQVgsVAP9J0GapeUQKvOIKM6qiOWgxjiYFjz8mJuwQtVGjGWcbe\n06l+hOyvA4PbZ5W/9vE9NhIXZQKBgQDl5W+bxmpJG3AfZ+zpikQNN6r8F+Rdb8h1\n4DX4291wdtB/uXC5g+k5vK+bv1QSl9Si2DTXt5qoDEkSANaj/nrfqGT+akPOW19h\nE4FMfEBmHxAxjZbqDP5RtUU5P0THOnS4+KK+YUHfp7uWV0Lqgt5tlQvId2sNsDpl\nGlEtJEufjQKBgH2UXZ9cRY4aXDDv0jAcM0iIWTExoZpa23DYvQ5Ti7IcgdG1Wp2X\nLwmlpY682meZ34cOsFzAwsjlUH+R709Bs1Ni1I1oU7ca/nlgigyXaKxge2KnfTRR\nz0gv76oO9WuR6/Mj3DAeacg6bbmTetHefQ21JQBZRMSHbMH4a9uZGt4lAoGBALbU\nuOYR7gUmJQ1VATzaETTRyNGjzqHgfHQCU+oOMRV36GkreVKQbbLVNHOQvbPru9em\nSqAkDIMJAjOnJwxVHjMxIOCUckhysm/pqzLAvhZ5Lc+64wJQQxGIL/1PK8ul2Z4h\nXow5nMHaC32M+FK4sVxE5JIRJrpEJKyzOUvFSb8hAoGAeKbrKWrM/W8/Up5XN385\nfxKBBvPUD4L6tqPGpi/i9y69bgxUJszqqpFDWWLIeE9RjT451seCTDJS1z8v0Wo+\nNL8ioXv89Klk4OJTXmjfQaMyG7OdyeC3D7EAeoqy+pxj0VyXxu5WmI7QKm8pRe9e\nJROlsGNB+U7Nr/vZMrYp5p4=\n-----END PRIVATE KEY-----\n",
#   "client_email": "kiotapay-service@kiotapay-384101.iam.gserviceaccount.com",
#   "client_id": "115995701657570013032",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kiotapay-service%40kiotapay-384101.iam.gserviceaccount.com"
# }


# # try:

#     # credentials = service_account.Credentials.from_service_account_file("service_account.json", scopes=SCOPES)

# service_account_email = creds.get("service_account_email")
# signer = creds.get("signer")
# private_key_id = creds.get("private_key")
# client_id = creds.get("client_id")
# token_uri = creds.get("token_uri",)
# revoke_uri = creds.get("revoke_uri")

# credentials = service_account.ServiceAccountCredentials(service_account_email, signer, private_key_id, client_id, token_uri, revoke_uri,SCOPES)

# # import pdb; pdb.set_trace()

# # secret_file = os.path.join(os.getcwd(), "service_account.json")
# # credentials = service_account.client.Credentials.from_service_account_file(secret_file, scopes=SCOPES)
# service = discovery.build('forms', 'v1', http=credentials.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

# # except Exception as e:
# #     # print("Exception: " + str(e))
# #     # service = None

# if service:
#     # Prints the title of the sample form:
#     form_id = "1UIpdGHUQ_t1tZR2690E6jjOVI_KdNQ_AQeCWomHe5Co"

#     result = service.forms().responses().list(formId=form_id).execute()
#     print(result)
# else:
#     print("Service was not found")








from __future__ import print_function
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime


# from app.v1.models.datamodel import *


'''
To generate service-account credentials, or to view the public credentials that you've already generated, do the following:
 - Open the Service accounts page. If prompted, select a project.
 - Click Create service account.
 - In the Create service account window, type a name for the service account, and select Furnish a new private key. If you want to grant G Suite domain-wide authority to the service account, also select Enable G Suite Domain-wide Delegation. Then click Create.
 - Your new public/private key pair is generated and downloaded to your machine; it serves as the only copy of this key. You are responsible for storing it securely.
'''

SCOPES = "https://www.googleapis.com/auth/forms.responses.readonly"
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'], scopes=SCOPES)
## Any calendar you want to read from must be configured to grant access to the following email
print('Service account email is',credentials.service_account_email)

# import pdb; pdb.set_trace()

service = discovery.build('forms', 'v1', http=credentials.authorize(Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)

if service:
    # Prints the title of the sample form:
    form_id = "1UIpdGHUQ_t1tZR2690E6jjOVI_KdNQ_AQeCWomHe5Co"

    result = service.forms().responses().list(formId=form_id).execute()
    print(result)

    responses = result["responses"]

    for res in responses:
        email = res.get('respondentEmail')
        print("EMAIL: >>",email)
        ans1 = res["answers"]["38e28f5c"]["textAnswers"]["answers"][0]["value"]
        print("ANSWER 1: >>",ans1)
        ans2 = res["answers"]["656525ae"]["textAnswers"]["answers"][0]["value"]
        print("ANSWER 2: >>",ans2)



    # import pdb; pdb.set_trace()

else:
    print("Service was not found")