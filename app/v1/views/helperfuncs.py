"""Helper methods for views"""


    # app = Flask(__name__)
    # app.register_blueprint(v1)

    # return app
    
# from ast import Pass
# from mimetypes import init
# from multiprocessing import allow_connection_pickling
import os
import base64
# from pickle import TRUE
# from africastalking import initialize

# import sys
import datetime

import re
import xlrd
import inflect
# import requests
from natsort import natsorted
from dateutil.parser import parse

# from .secrets import SENDER_ID, TARGET

# import app
try:
    from weasyprint import HTML
except Exception as e:
    print("Cannot import weasyprint",e)
    HTML = None

from flask import render_template
from jinja2 import Environment, FileSystemLoader, Template
from dateutil.relativedelta import relativedelta
from datetime import timedelta

from werkzeug.utils import secure_filename

# import logging
# logger = logging.getLogger('weasyprint')
# logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))

import random
from flask_mail import Message
# from flask import render_template,Response,request,flash,redirect,url_for,json
from app.v1.models.operations import *
from global_functions import *

from app import mail
from app import sms

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn,default_timeout=10800)

try:
    from do_secrets import *
except ImportError:
    APP_SETTINGS = None
    SENDER_ID = None
    TARGET = None
    G_ACCOUNT = None
    HOMEPAGE = None
    INDEX = None
    SMS_USERNAME = None
    SMS_API_KEY = None
    KW_USER = ""
    SECRETNAME = None
    SECRETNUM = None

    SECRETNAM = None
    SECRETNU = None

    VAR_ITEMS = None

sender = os.getenv("SENDER_ID") or SENDER_ID
mailsender = os.getenv('G_ACCOUNT') or G_ACCOUNT
configuration = os.getenv('APP_SETTINGS') or APP_SETTINGS

from .advanta import *


kiotapay_api_key = "f16edddd5e53dc3242f9fb9ad904ee5e"
kiotapay_partner_id = 3886

lesama_api_key = "cfc7c4382ae6d4277d8c09419a897c9e"
lesama_partner_id = 3895

merit_api_key = "fad3000bcfdfb541291ebc018bcc7868"
merit_partner_id = 2627

greatwall_api_key = "045abd0ed75b563eb186b2a61d686a83"
greatwall_partner_id = 321

kiotanum = "+254716674695"


if configuration == "development":
    localenv = True
else:
    localenv = False

typing = '<i class="fas fa-fw fa-pen text-primary mr-1"></i>'
proceed = '<i class="fas fa-fw fa-check-circle text-success mr-1"></i>'
err = '<i class="fas fa-fw fa-times-circle text-danger mr-1"></i>'
success = '<div id="snackbar" class="success"> <i class="fas fa-check"></i> Operation successful<div>'
failure = '<div id="snackbar" class="error"><i class="fas fa-times"></i> Failed! operation unsuccessful<div>'

flatten = lambda l: [item for sublist in l for item in sublist]
get_initials = lambda xx: ''.join(i[0] for i in xx.split())

from functools import wraps
from timeit import default_timer

def generate_hash(ckey,skey):
    passphrase = ckey + ':' + skey
    encoded_p = base64.b64encode(passphrase.encode()).decode()
    return encoded_p

def generate_coop_token(ckey,skey):
    hash = generate_hash(ckey,skey)
    headers = {"Authorization" : "Basic %s" % hash}
    data = {'grant_type': 'client_credentials'}
    r=requests.post("https://openapi-sit.co-opbank.co.ke/token",headers=headers,data=data)

    try:
        token = r.json()["access_token"]
        print("TOKEN GENERATED SUCCESSFULLY")
        return token
    except:
        print("NOT AUTHORIZED")
        return ""


def account_validation(ckey,skey,account):
    
    token = generate_coop_token(ckey,skey)

    if token:
        headers = {"Authorization" : "Bearer %s" % token}

        data = {'MessageReference': '40ca18c6765086089a1',
                "AccountNumber": account}

        r=requests.post("https://openapi-sit.co-opbank.co.ke/Enquiry/Validation/Account/1.0.0/",headers=headers,data=data)

        print("RESPONSE:",r.json())
    else:
        print("Invalid token passed")


def ins_api_account_subscription(ckey,skey,account,password):
    
    token = generate_coop_token(ckey,skey)

    if token:
        headers = {"Authorization" : "Bearer %s" % token}

        data = {
            "AccountNumber": account,
            "EventType": "ALL",
            "MinimumLimit": "1",
            "MaximumLimit": "1000000",
            "NotificationEndpoint": "https://kiotapay.com/les/45",
            "AuthRequired": "TRUE",
            "AuthUsername": "Lesamma",
            "AuthPassword": password
        }

        r=requests.post("https://openapi-sit.co-opbank.co.ke/Subscription/INS/Transactions/New/1.0.0/",headers=headers,data=data)

        try:
            print("RESPONSE:",r.json())
        except:
            print("ERROR RESPONSE:",r.text)

    else:
        print("Invalid token passed")


def account_pesalink_transfer(ckey,skey,account,account2):
    token = generate_coop_token(ckey,skey)
    if token:
        headers = {
            "Authorization" : "Bearer %s" % token,
            "accept": "application/json",
            "Content-Type": "application/json" 
        }
        data = {
            "MessageReference": "40ca18c6765086089u1",
            "CallBackUrl": "https://kiotapay.com/les/45",
            "Source": {
                "AccountNumber": account,
                "Amount": 777,
                "TransactionCurrency": "KES",
                "Narration": "Supplier Payment"
                },
            "Destinations": [{
                    "ReferenceNumber": "40ca18c6765086089a1_1",
                    "AccountNumber": account2,
                    "BankCode": "11",
                    "Amount": 777,
                    "TransactionCurrency": "KES",
                    "Narration": "Electricity Payment"
                    }]
                }

        r=requests.post(
            "https://openapi-sit.co-opbank.co.ke/FundsTransfer/External/A2A/PesaLink/1.0.0/",
            headers=headers,
            data=data)

        # import pdb; pdb.set_trace()

        try:
            print("RESPONSE:",r.json())
        except:
            print("ERROR RESPONSE:",r)

    else:
        print("Invalid token passed")

def timer(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = default_timer()
        response = f(*args, **kwargs)
        total_elapsed_time = default_timer() - start_time
        response += f'<h6>Results in: Database:{(total_elapsed_time*1000):,.1f}, Overall: <span id ="domtimeload"></span> milliseconds</h6>'
        # print(response)
        return response

    return wrapper

def crm(user):
    if user.company.ctype == "crm":
        return "crm"
    else:
        return ""

def mbogi():
    print("Hi there")
    # from app import create_app
    # app = create_app(configuration)
    # app.app_context().push()

    # tenant = TenantOp.fetch_tenant_by_id(1)
    # bal = tenant.balance
    # print(bal)
    # TenantOp.update_balance(tenant,bal+1.0)

def show_me(txt,user_id):
    print(txt)
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    mtu = UserOp.fetch_user_by_id(user_id)
    print("normal printing...>> message : ",txt,"myu >>",mtu.name)
    lfile("WORKER DOING MAGIC message...>> message :",txt," mtu >> ",mtu.name)

# original_stdout = sys.stdout # Save a reference to the original standard output

# def lfile(*args):
#     with open('logfile.txt', 'a') as f:
#         sys.stdout = f # Change the standard output to the file we created.
#         full_str = ""
#         for i in locals()['args']:
#             str_print = str(i)
#             full_str += str_print
#         print(datetime.datetime.now(),":", full_str)
#         sys.stdout = original_stdout # Reset the standard output to its original value

def run_scripts(user):
    """scripts to be performed once before any other operation is done"""
    print("Executing all statements below...")

    props = fetch_all_apartments_by_user(user)

    allbills = []

    for prop in props:
        tbills = prop.monthlybills
        allbills.append(tbills)

        target_dd = generate_date(1,2021)

        # all_expenses = fetch_current_billing_period_data(target_dd,prop.expenses)
        # for a in all_expenses:
        #     InternalExpenseOp.update_date(a,generate_date(1,2022))
            

    all_bills = flatten(allbills)

    if len(all_bills) == 0:
        print("NO BILLS TO ITERATE")

    # for bill in all_bills:
    #     if bill.month == 2 and bill.year == 2022 and not bill.rent_paid and bill.arrears > 0 and not bill.paid_amount:
    #         print("PROPLEMATIC BILL>>>>>",bill.apartment,bill.house,bill.total_bill,bill.paid_amount,"rent",bill.rent,"rent arrears",bill.rent_balance,"rentpaid",bill.rent_paid,"bal",bill.rent_due)
    #         MonthlyChargeOp.update_rent_balance(bill,bill.arrears)
    #         due = bill.rent + bill.arrears
    #         MonthlyChargeOp.update_rent_due(bill,due)




    # jendi = ApartmentOp.fetch_apartment_by_id(228)
    # codes = jendi.housecodes

    

    # for c in codes:
    #     print("CODE",c)
    #     HouseCodeOp.update_rates(c,"null","null",100,"null","null","null","null","null","null","null","null",current_user.id)

    # jendi = ApartmentOp.fetch_apartment_by_name("Vintage Phase I")

    # billing_period = jendi.billing_period

    # charges = jendi.charges

    # for charge in charges:
    #     if str(charge) == "Water" and charge.date.month == billing_period.month and charge.date.year == billing_period.year and charge.reading_id:
    #         ChargeOp.delete(charge)


    # prop = ApartmentOp.fetch_apartment_by_id(6)
    # bills = prop.houses
    # for bill in bills:
    #     HouseOp.update_billable(bill,True)
    ##################################################################################################################################################
    # house_obj = HouseOp.fetch_house_by_id(45)
    # HouseOp.update_name(house_obj,"B1")
    ##################################################################################################################################################
    # user = UserOp.fetch_user_by_id(11)
    # company = user.company
    # # CompanyOp.set_quota_month(company,12)
    # # CompanyOp.set_smsquota(company,320)
    # company_properties = company.props
    # for prop in company_properties:
    #     new_user = UserOp.fetch_user_by_id(13)
    #     UserOp.relate(new_user,prop)
    ##################################################################################################################################################
    # prop_obj = ApartmentOp.fetch_apartment_by_name("Jendi Heights")
    # expenses = prop_obj.expenses
    # for exp in expenses:
    #     if exp.id == 52:
    #         # InternalExpenseOp.update_cost(exp,4050)
    #         InternalExpenseOp.update_name(exp,"Paint & Labour #4s2 & #6S1")
    ##################################################################################################################################################
    # prop = ApartmentOp.fetch_apartment_by_id(4)
    # tenants = tenantauto(prop.id)

    # for i in tenants:
    #     TenantOp.update_initial_arrears(i,0.0)
    #     TenantOp.update_balance(i,0.0)
    #     TenantOp.update_deposit(i,0.0)

    # for charge in bills:
    #     if charge.tenant_id == 74:
    #         update_water = 0.0

    #         update_rent = 8000

    #         update_garbage = charge.garbage

    #         update_electricity = charge.electricity

    #         update_security = charge.security
 
    #         update_maintenance = charge.maintenance

    #         const_arrears = charge.arrears
    #         total_amount = update_water+update_rent+update_garbage+update_electricity+update_security+update_maintenance+const_arrears #total amount is incremented only by updates
    #         MonthlyChargeOp.update_monthly_charge(charge,update_water,update_rent,update_garbage,update_electricity,update_security,update_maintenance,total_amount,1)

    #         tenant_obj = TenantOp.fetch_tenant_by_id(74)
    #         running_bal = tenant_obj.balance
    #         running_bal = running_bal - 900 #these are updates, if one has update, the rest are zeros
    #         TenantOp.update_balance(tenant_obj,running_bal)

    #         bal = charge.balance
    #         bal = bal - 900 #these are updates, if one has update, the rest are zeros
    #         MonthlyChargeOp.update_balance(charge,bal)
    #         print("Update Done")
    #         #Send the SMS
    #         tele = tenant_obj.phone
    #         phonenum = sms_phone_number_formatter(tele)
    #         try:
    #             recipient = [phonenum]
    #             message = f"Dear tenant, We have amended rent amount as follows, Rent: Kshs 8,000. Water Kshs 0. Total: Kshs 8,400. Balance: Kshs 2,900 Sorry for any inconvenience that may have been caused by earlier misinformation - {prop}"
    #             message2 =  f"Dear tenant, your Rent for {str_month} is {smsrent} Water: {smswater} Garbage & Sec: {smsgarbsec} Total: {smstotal} - {prop}"
    #             #Once this is done, that's it! We'll handle the rest
    #             # response = sms.send(message, recipient)
    #             # print(response)
    #         except Exception as e:
    #             print(f"Houston, we have a problem {e}")
    #####################################################################################################################################################
    ##################################################################################################################################################
    # prop_obj = ApartmentOp.fetch_apartment_by_name("Jendi Heights")
    # readings = prop_obj.meter_readings
    # for reading in readings:
    #     if reading.id == 128:
    #         MeterReadingOp.update_prev(reading,"221")
    #         MeterReadingOp.update_units(reading,6)
        # last_month = datetime.datetime.now() - relativedelta(months=1)
        # date = last_month
        # MeterReadingOp.update_date(reading,date)
    #####################################################################################################################################################
    # register_url()
    # com = CompanyOp.fetch_company_by_name("Chase N Rainbow Properties Ltd")
    # CompanyOp.update_details(com,"Chase N Rainbow Properties Ltd","Kasarani Biashara Center","PO BOX 45150-00100, Nairobi","chasenrainbow@gmail.com","0720496063/0757924550")
    
    # meters = MeterOp.fetch_all_meters()
    # for meter in meters:
    #     allocs = meter.house_allocated
    #     for alloc in allocs:
    #         AllocateMeterOp.update_status(alloc,True,"qc")

    
    # prop = "Jendi Heights"
    # prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
    # charges = prop_obj.monthlybills
    # dec_charges = []
    # for charge in charges:
    #     if charge.month == 12 and charge.year == 2020:
    #         dec_charges.append(charge)

    # target_charge = None
    # for item in dec_charges:
    #     if item.tenant_id == 23:
    #         target_charge = item

    # current_month_charge = target_charge #specific current month charge for a particular house/tenant found
    # print("specific charge found")
    # # update_water = charge.water
    # update_water = 400.0

    # # update_rent = charge.rent
    # update_rent = 6800.0

    # update_garbage = charge.garbage
    # update_garbage += 0.0

    # update_electricity = charge.electricity
    # update_electricity += 0.0

    # update_security = charge.security
    # update_security += 0.0

    # update_maintenance = charge.maintenance
    # update_maintenance += 0.0

    # const_arrears = charge.arrears
    # created_by = 6
    # total_amount = update_water+update_rent+update_garbage+update_electricity+update_security+const_arrears #total amount is incremented only by updates

    # MonthlyChargeOp.update_monthly_charge(current_month_charge,update_water,update_rent,update_garbage,update_electricity,update_security,update_maintenance,total_amount,created_by)

    # tenant_id = 23
    # tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
    # # running_bal = tenant_obj.balance
    # running_bal = 7600.0 #these are updates, if one has update, the rest are zeros
    # TenantOp.update_balance(tenant_obj,running_bal)

    # # bal = current_month_charge.balance
    # # bal = bal + 200.0 #these are updates, if one has update, the rest are zeros
    # # MonthlyChargeOp.update_balance(current_month_charge,bal)
    
def example_func(param):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()
    user_obj = UserOp.fetch_user_by_national_id("00000000")
    # UserOp.update_user(user_obj,phone="777666999")
    # email_addr = "emmp45@gmail.com"
    # txt = Message('Rent Invoice', sender = mailsender, recipients = [email_addr])
    # txt.body = param
    # # txt.body = "Dear Tenant;" "\nThis is acknowledge that we have received payment of Kshs " + paid + "\nIn case of any query, feel free to contact us. \nThank you."
    # # txt.html = render_template('billinvoice.html',tenant=tenant,mailrent=mailrent,mailwater=mailwater,mailgarbage=mailgarbage,mailsecurity=mailsecurity,mailarrears=mailarrears,mailtotal=mailtotal)
    # mail.send(txt)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",param,">>>>",user_obj.name)

def send_internal_email_notifications(company,param):
    job = q.enqueue_call(
        func=send_mail_notifications, args=(company,param,), result_ttl=5000
    )

def format_month(num):
    if num < 9:
        return f"0{num}"
    else:
        return f'{num}'

def send_mail_notifications(company,param):

    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    try:
        email_addr = "notifications.kiotapay@gmail.com" if os.getenv("TARGET") != "lasshouse" else os.getenv("G_ACCOUNT_ALERTS")
        
        txt = Message(company, sender = mailsender, recipients = [email_addr])
        txt.body = param
        mail.send(txt)
    except:
        pass

def good_print(arr):
    import json
    print(json.dumps(arr, indent=4, sort_keys=True))

def page(arr):
    count=len(arr)
    if count >= 20:
        page_orientation = "portrait"
    else:
        page_orientation = "landscape"

    return page_orientation

def sum_positive_values(arr):
    total = 0.0
    for i in arr:
        if i > 0.0:
            total += i
            
    return total

def sum_values(arr):
    total = 0.0
    for i in arr:

        # print("starttttttttttttttttttttttttttttt",i)

        failed = False

        try:
            # print("trying to do normal summation")
            total += i
        except:
            # print("failed to sum",i)
            failed = True

        if failed:
            try:
                # print("trying to sum strfloat",i)
                ii = i.replace(",","")
                total += float(ii)
            except:
                # print("failed to sum in second trial",i)
                continue

        # print("enddddddddddddddddddddddddddddddddd",i)


    return total

def set_sphone(companyname,arr,sphone,sub):
    co = CompanyOp.fetch_company_by_name(companyname)
    if co:
        print("ACTIVE COMPANY >> ",co.name)
        CompanyOp.update_status(co,True)
        CompanyOp.update_balance(co,arr)

        # if not co.sphone:
        print("Updating company contact number for ",companyname)
        CompanyOp.update_sphone(co,sphone)

        if not co.subscription:
            print("Updating subscription fee for ", companyname)
            CompanyOp.update_subscription(co,sub)
    else:
        print("COMPANY NAME IS INCORRECT >> ",companyname)

def run_company_data():

    print("Setting company data...")

    set_sphone("Rikena Property Solutions",0.0,"0717121612",0.0) #4

    set_sphone("Nairuti & Associates",4500.0,"0717121612",4500.0) #6
    set_sphone("Chaise River Properties",0.0,"0721465478",3000.0) #1
    set_sphone("KIGAKA ENTERPRISES",0.0,"0768333904",0.0) #12
    set_sphone("MULTIDIME AGENCIES",0.0,"0112036366",2500.0) #2
    set_sphone("MojaMbili Homes",2000.0,"0729009009",2000.0) #3
    set_sphone("Grashar Property Care",0.0,"0723798023",1500.0) #5
    set_sphone("Rightway Properties Agency",0.0,"0745828127",1500.0) #9
    set_sphone("Courtland Realtors Limited",0.0,"0703759351",1000.0) #8

    set_sphone("Premier Realty",4000.0,"0790001035",4000.0) #10
    set_sphone("S & P Realtors",0.0,"070742404839",0.0) #13
    set_sphone("Lesama Ltd",3000.0,"0710250350",3000.0) #11
    set_sphone("KEVMA REAL ESTATE",0.0,"0716674695",2500.0) #7

    set_sphone("Ramata Greens Management Ltd",0.0,"0716674695",0.0) #14
    set_sphone("Stan-G Properties",0.0,"0716674695",1000.0) #15
    set_sphone("Supersite Ltd",0.0,"0716674695",1000.0) #16
    set_sphone("Bulpark Square",0.0,"0716674695",0.0) #17
    set_sphone("7EDGE DEVELOPERS & MANAGERS",0.0,"0702666480",2000.0) #18
    set_sphone("THE OAKS",0.0,"0740570117",2000.0) #20
    set_sphone("SIAN REALTORS",0.0,"0716674695",0.0) #19



def logo(co):
    """set appropriate logos to respective companies"""
    str_name_company = str(co)
    sign = ""
    try:
        if str_name_company == "Chaise River Properties":
            coc = CompanyOp.fetch_company_by_name("Chaise River Properties")
            CompanyOp.update_sms_provider(coc,"KIOTAPAY")
            ##################################################
            logopath = "../static/img/logos/chase/l-logo.png"
            mobilelogopath = "../static/img/logos/chase/s-logo.png"
            fulllogopath = "../static/img/logos/chase/full-logo.png"
            letterhead = "../static/img/logos/chase/letterhead.jpg"

        elif str_name_company == "MULTIDIME AGENCIES":
            ##################################################
            logopath = "../static/img/logos/multidime/l-logo.png"
            mobilelogopath = "../static/img/logos/multidime/s-logo.png"
            fulllogopath = "../static/img/logos/multidime/full-logo.png"
            letterhead = "../static/img/logos/multidime/letterhead.jpg"

        elif str_name_company == "MojaMbili Homes":
            ##################################################
            logopath = "../static/img/logos/mojambili/l-logo.png"
            mobilelogopath = "../static/img/logos/mojambili/s-logo.png"
            fulllogopath = "../static/img/logos/mojambili/full-logo.png"
            letterhead = "../static/img/logos/mojambili/letterhead.jpg"

        elif str_name_company == "Rikena Property Solutions":
            ##################################################
            logopath = "../static/img/logos/rikena/l-logo.png"
            mobilelogopath = "../static/img/logos/rikena/s-logo.png"
            fulllogopath = "../static/img/logos/rikena/full-logo.png"
            letterhead = "../static/img/logos/rikena/letterhead.jpg"

        elif str_name_company == "SIFALINK ENTERPRISES":
            ##################################################
            logopath = "../static/img/logos/sifalink/l-logo.png"
            mobilelogopath = "../static/img/logos/sifalink/s-logo.png"
            fulllogopath = "../static/img/logos/sifalink/full-logo.png"
            letterhead = "../static/img/logos/sifalink/letterhead.jpg"

        elif str_name_company == "Thara Enterprises":
            ####################################################
            logopath = "../static/img/logos/thara/l-logo.png"
            mobilelogopath = "../static/img/logos/thara/s-logo.png"
            fulllogopath = "../static/img/logos/thara/full-logo.png"
            letterhead = "../static/img/logos/thara/letterhead.jpg"

        elif str_name_company == "Grashar Property Care":
            ##################################################
            logopath = "../static/img/logos/grashar/l-logoo.png"
            mobilelogopath = "../static/img/logos/grashar/s-logo.png"
            fulllogopath = "../static/img/logos/grashar/full-logo.png"
            letterhead = "../static/img/logos/grashar/letterhead.jpg"

        elif str_name_company == "Greystar Properties":
            #######################################################
            logopath = "../static/img/logos/greystar/l-logo.png"
            mobilelogopath = "../static/img/logos/greystar/s-logo.png"
            fulllogopath = "../static/img/logos/greystar/full-logo.png"
            letterhead = "../static/img/logos/greystar/letterhead.jpg"

        elif str_name_company == "Nairuti & Associates":
            ##################################################
            logopath = "../static/img/logos/nairuti/l-logo.png"
            mobilelogopath = "../static/img/logos/nairuti/s-logo.png"
            fulllogopath = "../static/img/logos/nairuti/full-logo.png"
            letterhead = "../static/img/logos/nairuti/letterhead.jpg"

        elif str_name_company == "Ramata Greens Management Ltd":
            ##################################################
            logopath = "../static/img/logos/ramata/l-logo.png"
            mobilelogopath = "../static/img/logos/ramata/s-logo.png"
            fulllogopath = "../static/img/logos/ramata/full-logo.png"
            letterhead = "../static/img/logos/ramata/letterhead.jpg"

        elif str_name_company == "Supersite Ltd":
            ##################################################
            logopath = "../static/img/logos/supersite/l-logo.png"
            mobilelogopath = "../static/img/logos/supersite/s-logo.png"
            fulllogopath = "../static/img/logos/supersite/full-logo.png"
            letterhead = "../static/img/logos/supersite/letterhead.jpg"
        
        elif str_name_company == "Latitude Properties":
            #####################################################
            coc = CompanyOp.fetch_company_by_name("Latitude Properties")
            CompanyOp.update_sms_provider(coc,"Advanta")
            ##################################################
            logopath = "../static/img/logos/latitude/l-logo.png"
            mobilelogopath = "../static/img/logos/latitude/s-logo.png"
            fulllogopath = "../static/img/logos/latitude/full-logo.png"
            letterhead = "../static/img/logos/latitude/letterhead.jpg"

        elif str_name_company == "Merit Properties Limited":
            coc = CompanyOp.fetch_company_by_name("Merit Properties Limited")
            CompanyOp.update_sms_provider(coc,"Advanta")
            ##################################################
            logopath = "../static/img/logos/merit/l-logo.png"
            mobilelogopath = "../static/img/logos/merit/s-logo.png"
            fulllogopath = "../static/img/logos/merit/full-logo.png"
            letterhead = "../static/img/logos/merit/letterhead.jpg"

        elif str_name_company == "KEVMA REAL ESTATE":
            coc = CompanyOp.fetch_company_by_name("KEVMA REAL ESTATE")
            CompanyOp.update_sms_provider(coc,"Advanta")
            ##################################################
            logopath = "../static/img/logos/kevma/l-logo.png"
            mobilelogopath = "../static/img/logos/kevma/s-logo.png"
            fulllogopath = "../static/img/logos/kevma/full-logo.png"
            letterhead = "../static/img/logos/kevma/letterhead.jpg"
            sign = "../static/img/logos/kevma/sign.png"

        elif str_name_company == "Courtland Realtors Limited":
            ##################################################
            logopath = "../static/img/logos/courtland/l-logo.png"
            mobilelogopath = "../static/img/logos/courtland/s-logo.png"
            fulllogopath = "../static/img/logos/courtland/full-logo.png"
            letterhead = "../static/img/logos/courtland/letterhead.jpg"

        elif str_name_company == "Sentom Investment":
            ##################################################
            logopath = "../static/img/logos/sentom/l-logo.png"
            mobilelogopath = "../static/img/logos/sentom/s-logo.png"
            fulllogopath = "../static/img/logos/sentom/full-logo.png"
            letterhead = "../static/img/logos/sentom/letterhead.jpg"

        elif str_name_company == "Rowam Properties Limited":
            ##################################################
            logopath = "../static/img/logos/rowam/l-logo.png"
            mobilelogopath = "../static/img/logos/rowam/s-logo.png"
            fulllogopath = "../static/img/logos/rowam/full-logo.png"
            letterhead = "../static/img/logos/rowam/letterhead.jpg"

        elif str_name_company == "Rightway Properties Agency":
            ##################################################
            logopath = "../static/img/logos/rightway/l-logo.png"
            mobilelogopath = "../static/img/logos/rightway/s-logo.png"
            fulllogopath = "../static/img/logos/rightway/full-logo.png"
            letterhead = "../static/img/logos/rightway/letterhead.jpg"

        elif str_name_company == "Premier Realty":
            ##################################################
            logopath = "../static/img/logos/premier/l-logo.png"
            mobilelogopath = "../static/img/logos/premier/s-logo.png"
            fulllogopath = "../static/img/logos/premier/full-logo.png"
            letterhead = "../static/img/logos/premier/letterhead.jpg"

        elif str_name_company == "Lesama Ltd":
            coc = CompanyOp.fetch_company_by_name("Lesama Ltd")
            CompanyOp.update_sms_provider(coc,"Advanta")
            ##################################################
            logopath = "../static/img/logos/lesama/l-logo.png"
            mobilelogopath = "../static/img/logos/lesama/s-logo.png"
            fulllogopath = "../static/img/logos/lesama/full-logo.png"
            letterhead = "../static/img/logos/lesama/letterhead.jpg"

        elif str_name_company == "KIGAKA ENTERPRISES":
            ##################################################
            logopath = "../static/img/logos/kigaka/l-logo.png"
            mobilelogopath = "../static/img/logos/kigaka/s-logo.png"
            fulllogopath = "../static/img/logos/kigaka/full-logo.png"
            letterhead = "../static/img/logos/kigaka/letterhead.jpg"

        elif str_name_company == "S & P Realtors":
            ##################################################
            logopath = "../static/img/logos/sprealtors/l-logo.png"
            mobilelogopath = "../static/img/logos/sprealtors/s-logo.png"
            fulllogopath = "../static/img/logos/kigaka/full-logo.png"
            letterhead = "../static/img/logos/kigaka/letterhead.jpg"

        elif str_name_company == "7EDGE DEVELOPERS & MANAGERS":
            ##################################################
            logopath = "../static/img/logos/seven/l-logo.png"
            mobilelogopath = "../static/img/logos/seven/s-logo.png"
            fulllogopath = "../static/img/logos/kiotapay/full-logo.jpg"
            letterhead = "../static/img/logos/kiotapay/letterhead.jpg"

        elif str_name_company == "SIAN REALTORS":
            ##################################################
            logopath = "../static/img/logos/sian/l-logo.png"
            mobilelogopath = "../static/img/logos/sian/s-logo.png"
            fulllogopath = "../static/img/logos/kiotapay/full-logo.jpg"
            letterhead = "../static/img/logos/kiotapay/letterhead.jpg"

        elif str_name_company == "Vintage Residence Limited":
            ##################################################
            logopath = "../static/img/logos/vintage/l-logo.png"
            mobilelogopath = "../static/img/logos/vintage/s-logo.png"
            fulllogopath = "../static/img/logos/vintage/full-logo.jpg"
            letterhead = "../static/img/logos/vintage/letterhead.jpg"

        elif str_name_company == "Cherah Properties":
            ##################################################
            logopath = "../static/img/logos/cherah/l-logo.png"
            mobilelogopath = "../static/img/logos/cherah/s-logo.png"
            fulllogopath = "../static/img/logos/cherah/full-logo.jpg"
            letterhead = "../static/img/logos/cherah/letterhead.jpg"

        elif str_name_company == "LaCasa":
            coc = CompanyOp.fetch_company_by_name("LaCasa")
            CompanyOp.update_sms_provider(coc,"Advanta")
            ##################################################
            logopath = "../static/img/logos/lacasa/l-logo.png"
            mobilelogopath = "../static/img/logos/lacasa/s-logo.png"
            fulllogopath = "../static/img/logos/vintage/full-logo.jpg"
            letterhead = "../static/img/logos/vintage/letterhead.jpg"

        elif str_name_company == "Rever Front Limited":
            ##################################################
            logopath = "../static/img/logos/rever/l-logo.png"
            mobilelogopath = "../static/img/logos/rever/s-logo.png"
            fulllogopath = "../static/img/logos/rever/full-logo.jpg"
            letterhead = "../static/img/logos/rever/letterhead.jpg"

        elif str_name_company.title() == "Rever Mwimuto Limited" and not localenv:
            ##################################################
            logopath = "../static/img/logos/aviv/l-logo.png"
            mobilelogopath = "../static/img/logos/aviv/s-logo.png"
            fulllogopath = "../static/img/logos/aviv/full-logo.jpg"
            letterhead = "../static/img/logos/aviv/letterhead.jpg"

        elif str_name_company == "AMC REALTORS":
            ##################################################
            logopath = "../static/img/logos/amc/l-logo.png"
            mobilelogopath = "../static/img/logos/amc/s-logo.png"
            fulllogopath = "../static/img/logos/amc/full-logo.jpg"
            letterhead = "../static/img/logos/amc/letterhead.jpg"

        elif str_name_company == "ASTROL":
            ##################################################
            logopath = "../static/img/logos/astrol/l-logo.png"
            mobilelogopath = "../static/img/logos/astrol/s-logo.png"
            fulllogopath = "../static/img/logos/astrol/full-logo.jpg"
            letterhead = "../static/img/logos/astrol/letterhead.jpg"

        elif str_name_company == "Denvic Property Managers":
            coc = CompanyOp.fetch_company_by_name("Denvic Property Managers")
            CompanyOp.update_sms_provider(coc,"Advanta")
            ##################################################
            logopath = "../static/img/logos/denvic/l-logo.png"
            mobilelogopath = "../static/img/logos/denvic/s-logo.png"
            fulllogopath = "../static/img/logos/denvic/full-logo.jpg"
            letterhead = "../static/img/logos/denvic/letterhead.jpg"

        elif str_name_company == "Lymax Properties":
            ##################################################
            logopath = "../static/img/logos/lymax/l-logo.png"
            mobilelogopath = "../static/img/logos/lymax/s-logo.png"
            fulllogopath = "../static/img/logos/lymax/full-logo.jpg"
            letterhead = "../static/img/logos/lymax/letterhead.jpg"

        elif str_name_company == "Litala":
            ##################################################
            logopath = "../static/img/logos/litala/l-logo.png"
            mobilelogopath = "../static/img/logos/litala/s-logo.png"
            fulllogopath = "../static/img/logos/litala/full-logo.jpg"
            letterhead = "../static/img/logos/litala/letterhead.jpg"

        elif str_name_company == "National Bank":
            ##################################################
            logopath = "../static/img/logos/nbk/l-logo.png"
            mobilelogopath = "../static/img/logos/nbk/s-logo.png"
            fulllogopath = "../static/img/logos/nbk/full-logo.jpg"
            letterhead = "../static/img/logos/nbk/letterhead.jpg"

        elif str_name_company == "Developer" or str_name_company == "Demo Company Two":
            ##################################################
            logopath = "../static/img/logos/maisha/l-logo.png"
            mobilelogopath = "../static/img/logos/maisha/l-logo.png"
            fulllogopath = "../static/img/logos/nbk/full-logo.jpg"
            letterhead = "../static/img/logos/nbk/letterhead.jpg"

        else:
            if os.getenv("TARGET") == "lasshouse" or TARGET == "lasshouse":
                ##################################################
                logopath = "../static/img/logos/inva/l-logo.png"
                mobilelogopath = "../static/img/logos/inva/s-logo.png"
                fulllogopath = "../static/img/logos/inva/full-logo.jpg"
                letterhead = "../static/img/logos/inva/letterhead.jpg"
                sign = ""
            else:
                ##################################################
                logopath = "../static/img/logos/kiotapay/l-logo.png"
                mobilelogopath = "../static/img/logos/kiotapay/s-logo.png"
                fulllogopath = "../static/img/logos/kiotapay/full-logo.jpg"
                letterhead = "../static/img/logos/kiotapay/letterhead.jpg"
                sign = "../static/img/logos/kiotapay/sign.png"

    except Exception as e:
        print("failing big time",e)
        if os.getenv("TARGET") != "lasshouse":
            logopath = "../static/img/logos/kiotapay/l-logo.png"
            mobilelogopath = "../static/img/logos/kiotapay/s-logo.png"
            fulllogopath = "../static/img/logos/kiotapay/full-logo.png"
            letterhead = "../static/img/logos/kiotapay/letterhead.jpg"
        else:
            logopath = "../static/img/logos/spry/l-logo.png"
            mobilelogopath = "../static/img/logos/spry/s-logo.png"
            fulllogopath = "../static/img/logos/spry/full-logo.png"
            letterhead = "../static/img/logos/spry/letterhead.jpg"

    if os.getenv("TARGET") != "lasshouse":
        parent = "KiotaPay"
    else:
        parent = ""
        
    return logopath,mobilelogopath,fulllogopath,letterhead,sign,parent

def update_login_history(location,user):
    logins = user.logins

    time = datetime.datetime.now()

    todays_login = False

    for login in logins:
        if login.logged_on.day == time.day and login.logged_on.month == time.month and login.logged_on.year == time.year:

            freq = login.frequency + 1

            if location == "reports":
                reportfreq = login.report_frequency + 1
                UserLoginDataOp.update_report_frequency(login,reportfreq,freq)
            elif location == "search":
                searchfreq = login.search_frequency + 1
                UserLoginDataOp.update_search_frequency(login,searchfreq,freq)
            elif location == "invoice":
                invoicefreq = login.invoice_frequency + 1
                UserLoginDataOp.update_invoice_frequency(login,invoicefreq,freq)
            elif location == "payment":
                paymentfreq = login.payment_frequency + 1
                UserLoginDataOp.update_payment_frequency(login,paymentfreq,freq)
            else:
                UserLoginDataOp.update_frequency(login,freq)

            todays_login = True
            break
        else:
            continue

    if not todays_login:
        new_login = UserLoginDataOp(user.id)
        new_login.save()
        title = f'{(new_login.logged_on + relativedelta(hours=3)).strftime("%d/%b")} logins'
        try:
            txt = f"{user.name} of {user.company.name} has logged in at {(new_login.logged_on + relativedelta(hours=3)).strftime('%H:%M %p')}"
            send_internal_email_notifications(title,txt)
        except:
            pass

def advanta_sms_delivery(apikey,partnerid,msgid):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    payload = {
    "apikey":apikey,
    "partnerID":partnerid,
    "messageID":msgid
    }

    url = "https://quicksms.advantasms.com/api/services/getdlr/"

    response = requests.get(url, json=payload)

    try:
        resp = response.json()["delivery-description"]
        print("DELIVERY REPORT:", resp)
    except:
        resp = "unknown error"

    if resp == "DeliveredToTerminal":
        resp1 = "Success"
    else:
        resp1 = "blocked"

    if resp1 == "unknown error":
        pass
    else:
        payment_obj = PaymentOp.fetch_payment_by_smsid(msgid)
        if payment_obj:
            print("DELIVERY STATUS! PAYMENT FOUND")
            PaymentOp.update_sms_status(payment_obj,resp1)

        bill_obj = MonthlyChargeOp.fetch_monthlycharge_by_smsid(msgid)
        if bill_obj:
            MonthlyChargeOp.update_sms_status(bill_obj,resp1)
            print("DELIVERY STATUS! INVOICE FOUND")
        else:
            print("DELIVERY STATUS UNAVAILABLE FOR THAT MESSAGE")

def sms_sender(company,sms_text,phonenum):
    if company.title() == "Lesama Ltd":
        report = advanta_send_sms(sms_text,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")

    elif company.title() == "Merit Properties Limited":
        report = advanta_send_sms(sms_text,phonenum,merit_api_key,merit_partner_id,"MERIT_LTD")

    elif company.title() == "Denvic Property Managers":
        report = afrinet_send_sms(sms_text,phonenum,greatwall_api_key,greatwall_partner_id,"GREATWALL")

    ################################## OWN SENDER IDS ##################################

    elif company.upper() == "KEVMA REAL ESTATE":
        report = advanta_send_sms(sms_text,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")

    elif company.title() == "Latitude Properties":
        report = advanta_send_sms(sms_text,phonenum,kiotapay_api_key,kiotapay_partner_id,"LATITUDE")

    elif company.title() == "Lacasa":
        report = advanta_send_sms(sms_text,phonenum,kiotapay_api_key,kiotapay_partner_id,"Bizline")

    elif company.title() == "Lymax Properties":
        report = advanta_send_sms(sms_text,phonenum,kiotapay_api_key,kiotapay_partner_id,"LYMAXPROPER")

    #########################################################################################
    else:
        # report = None
        report = advanta_send_sms(sms_text,phonenum,kiotapay_api_key,kiotapay_partner_id,"Bizline")
        
    if report:
        param1 = report["apikey"]
        param2 = report["partnerID"]
        param3 = report["msgid"]

        co = CompanyOp.fetch_company_by_name(company)
        raw_rem_sms =co.remainingsms
        rem_sms = calculate_sms_cost_alt(raw_rem_sms,sms_text)

        CompanyOp.set_rem_quota(co,rem_sms)

        jb = q.enqueue_in(timedelta(seconds=300), advanta_sms_delivery, args=(param1,param2,param3,))
        return param3
    else:
        print("NO REPORT TO CHECK")
        return None


        
     
def remove_dups(x):
    return list(dict.fromkeys(x))

def phone_number_formatter(phone):
    str_phone = str(phone)
    step1 = str_phone.lstrip("0")
    step2 = "254"
    step4 = step2+step1
    return step4

def phone_number_formatter_url(phone):
    step1 = phone_number_formatter(phone)
    step2 = "tel:+"
    step3 = step2+step1
    return step3

def sms_phone_number_formatter(phone):
    str_phone = str(phone)
    step1 = str_phone.lstrip("0")
    step2 = "+254"
    step4 = step2+step1
    return step4

def sms_phone_number_formatter_mpesa(phone):
    step1 = str(phone)
    step2 = "+"
    step4 = step2+step1
    return step4

def phone_number_formatter_r(phone):
    str_phone = str(phone)
    step1 = str_phone[3:]
    step2 = "0"
    step3 = step2+step1
    return step3

def phone_number_formatter_excel(phone):
    str_phone = str(phone)
    step2 = "0"
    step3 = step2+str_phone
    return step3

def url_security(url):
    if url:
        step1 = url[4:]
        step2 = "https"
        step3 = step2+step1
        return step3
    return ""

def divide_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def sum_lists(*args):
    return list(map(sum, zip(*args)))

def stringify_list_items(array):
    new_list = []
    for arr in array:
        str_arr = str(arr)
        new_list.append(str_arr)
    return new_list

def greetings_generator(cur_time):
    if cur_time < 12:
        greeting = 'Good morning,'
    elif 12 <= cur_time < 17:
        greeting = 'Good afternoon,'
    else:
        greeting = 'Good evening,'

    return greeting

def get_next_month(month):
    if month == 12:
        next_month = 1
    else:
        next_month = month + 1
    return next_month

def get_next_year(month,year):
    if month == 12:
        target_year = year +1 
    else:
        target_year = year

    return target_year

def get_prev_month(month):
    if month == 1:
        prev_month = 12
    else:
        prev_month = month - 1
    return prev_month

def get_prev_year(month,year):
    if month == 1:
        target_year = year -1 
    else:
        target_year = year

    return target_year

def get_prev_month_year(month,year):
    if month == 1:
        prev_month = 12
        target_year = year -1 
    else:
        prev_month = month - 1
        target_year = year

    return prev_month,target_year

def filter_in_recent_data(arr):
    
    time = datetime.datetime.now()
    if time.month == 1:
        second_prev_month = {
            'month':11,
            'year':time.year-1
        }
        prev_month = {
            'month':12,
            'year':time.year-1
        }
        current_month = {
            'month':time.month,
            'year':time.year
        }

    elif time.month == 2:
        second_prev_month = {
            'month':12,
            'year':time.year-1
        }
        prev_month = {
            'month':1,
            'year':time.year
        }
        current_month = {
            'month':time.month,
            'year':time.year
        }
    else:
        second_prev_month = {
            'month':time.month-2,
            'year':time.year
        }
        prev_month = {
            'month':time.month-1,
            'year':time.year
        }
        current_month = {
            'month':time.month,
            'year':time.year
        }

    second_prev_month_data = []
    prev_month_data = []
    current_month_data = []

    for i in arr:
        if i.date.month == second_prev_month['month'] and i.date.year == second_prev_month['year']:
            second_prev_month_data.append(i)
        if i.date.month == prev_month['month'] and i.date.year == prev_month['year']:
            prev_month_data.append(i)
        if i.date.month == current_month['month'] and i.date.year == current_month['year']:
            current_month_data.append(i)
            
    return second_prev_month_data + prev_month_data + current_month_data

def fetch_current_billing_period_data(billing_period,arr):
    current_billling_period_data = []
    for i in arr:
        if i.date.month == billing_period.month and i.date.year == billing_period.year:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_current_billing_period_data_alt(billing_period,arr):
    current_billling_period_data = []
    for i in arr:
        if i.pay_period.month == billing_period.month and i.pay_period.year == billing_period.year:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_prev_billing_period_data(billing_period,arr):
    current_billling_period_data = []
    prev_month = get_prev_month(billing_period.month)
    prev_year = get_prev_year(billing_period.month,billing_period.year)

    for i in arr:
        if i.date.month == prev_month and i.date.year == prev_year:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_current_billing_period_readings(billing_period,arr):
    """water"""
    current_billling_period_data = []
    for i in arr:
        if i.reading_period:
            if i.reading_period.month == billing_period.month and i.reading_period.year == billing_period.year and i.description == "actual water reading":
                current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_current_billing_period_readings_alt(billing_period,arr):
    """elec"""
    current_billling_period_data = []
    for i in arr:
        if i.reading_period:
            if i.reading_period.month == billing_period.month and i.reading_period.year == billing_period.year and i.description == "actual electricity reading":
                current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_current_billing_period_payments(billing_period,arr):
    current_billling_period_data = []
    for i in arr:
        if i.pay_period.month == billing_period.month and i.pay_period.year == billing_period.year and not i.voided:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_specific_period_payments(month,year,arr):
    current_billling_period_data = []
    for i in arr:
        if i.pay_period.month == month and i.pay_period.year == year and not i.voided:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_specific_period_payments2(month,year,arr,tid):
    current_billling_period_data = []
    for i in arr:
        if i.pay_period.month == month and i.pay_period.year == year and not i.voided and i.tenant_id == tid:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_specific_period_payments3(month,year,arr,ptid):
    current_billling_period_data = []
    for i in arr:
        if i.pay_period.month == month and i.pay_period.year == year and not i.voided and i.ptenant_id == ptid:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_prev_billing_period_payments(billing_period,arr):
    prev_billling_period_data = []
    prev_month = get_prev_month(billing_period.month)
    prev_year = get_prev_year(billing_period.month,billing_period.year)
    for i in arr:
        if i.pay_period.month == prev_month and i.pay_period.year == prev_year and not i.voided:
            prev_billling_period_data.append(i)
    return prev_billling_period_data

def fetch_current_billing_period_voided_payments(billing_period,arr):
    current_billling_period_data = []
    for i in arr:
        if i.pay_period.month == billing_period.month and i.pay_period.year == billing_period.year and i.voided:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_last_months_payments(month,year,arr):
    # TODO Function Repetion
    last_month_data = []
    for i in arr:
        if i.pay_period.month == month and i.pay_period.year == year and not i.voided:
            last_month_data.append(i)
    return last_month_data

def fetch_current_billing_period_bills(billing_period,arr):
    current_billling_period_data = []
    for i in arr:
        if i.month == billing_period.month and i.year == billing_period.year:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_recent_bills(billing_period,arr):
    current_billling_period_data = []

    intlastmonth = billing_period.month - 1 if billing_period.month != 1 else 12
    intyear = billing_period.year - 1 if billing_period.month == 1 else billing_period.year

    for i in arr:
        if i.month == billing_period.month and i.year == billing_period.year:
            current_billling_period_data.append(i)
        if i.month == intlastmonth and i.year == intyear:
            current_billling_period_data.append(i)
    return current_billling_period_data

def fetch_prev_billing_period_bills(billing_period,arr):
    prev_billling_period_data = []
    prev_month = get_prev_month(billing_period.month)
    prev_year = get_prev_year(billing_period.month,billing_period.year)
    for i in arr:
        if i.month == prev_month and i.year == prev_year:
            prev_billling_period_data.append(i)
    return prev_billling_period_data

def fetch_next_billing_period_bills(billing_period,arr):
    prev_billling_period_data = []
    prev_month = get_next_month(billing_period.month)
    prev_year = get_next_year(billing_period.month,billing_period.year)
    for i in arr:
        if i.month == prev_month and i.year == prev_year:
            prev_billling_period_data.append(i)
    return prev_billling_period_data

def fetch_tnt_prev_billing_period_bills_alt(month,year,arr,tnt):
    prev_billling_period_data = []
    prev_month = get_prev_month(month)
    prev_year = get_prev_year(month,year)
    for i in arr:
        if i.month == prev_month and i.year == prev_year and i.tenant_id == tnt:
            prev_billling_period_data.append(i)
    return prev_billling_period_data

def fetch_pt_prev_billing_period_bills(month,year,arr,ptid):
    prev_billling_period_data = []
    prev_month = get_prev_month(month)
    prev_year = get_prev_year(month,year)
    for i in arr:
        if i.month == prev_month and i.year == prev_year and i.ptenant_id == ptid:
            prev_billling_period_data.append(i)
    return prev_billling_period_data

def fetch_prev_schedule(month,year,arr,ptid):
    prev_billling_period_data = []
    prev_month = get_prev_month(month)
    prev_year = get_prev_year(month,year)
    for i in arr:
        if i.schedule_date.month == prev_month and i.schedule_date.year == prev_year and i.ptenant_id == ptid:
            prev_billling_period_data.append(i)
    return prev_billling_period_data

def fetch_actual_payments(arr):
    actual_payment_data = []
    for i in arr:
        if not i.voided:
            actual_payment_data.append(i)
    return actual_payment_data

class ValidatePass():
    """Helper class to validate passwords"""
    @classmethod
    def validate_password(cls,pass1,pass2):
        if pass1 == "":
            return None
        elif pass1 != pass2:
            return "no match"
        return "match"

# class CreateCompany():
#     """temporary class to create companies for existing orphaned users"""
#     def create_companies(self):
#         users = UserOp.fetch_all_users()
#         for user in users:
#             company_name = user.company_name
#             if user.user_group_id == 2:
#                 presento = CompanyOp.fetch_usergroup_by_name(company_name)
#                 if not presento:
#                     company_obj = CompanyOp(company_name,None,None)
#                     company_obj.save()

#             if user.user_group_id == 3:
#                 presento2 = CompanyOp.fetch_usergroup_by_name(company_name)
#                 if not presento2:
#                     company_obj = CompanyOp(company_name,None,None)
#                     company_obj.save()

class CreateGroups():
    """Helper class to create object/user"""
    def create_groups(self):

        present1 = UserGroupOp.fetch_usergroup_by_name("Admin")
        if not present1:
            group1 = UserGroupOp("Admin","administrator")
            group1.save()
            

        present2 = UserGroupOp.fetch_usergroup_by_name("Owner")
        if not present2:
            group2 = UserGroupOp("Owner","apartment owner")
            group2.save()
            

        present3 = UserGroupOp.fetch_usergroup_by_name("Agent")
        if not present3:
            group3 = UserGroupOp("Agent","apartment manager")
            group3.save()


        present4 = UserGroupOp.fetch_usergroup_by_name("User")
        if not present4:
            group4 = UserGroupOp("User","Company employee")
            group4.save()

        present5 = UserGroupOp.fetch_usergroup_by_name("Tenant")
        if not present5:
            group5 = UserGroupOp("Tenant","apartment resident")
            group5.save()

        present6 = UserGroupOp.fetch_usergroup_by_name("Caretaker")
        if not present6:
            group6 = UserGroupOp("Caretaker","Property caretaker")
            group6.save()

            print("......................................")
            print("Adding groups.........................Admin,Owner,Agent,User,Tenant and Caretaker groups created")

        print("Groups................................OK")

# class CreateCompanyGroups():
#     """Temporary class to create essential company usergroups"""
#     def create_groups(self):

#         group1 = CompanyUserGroupOp("Manager","administrator",1) #VARYING Refctor for all created companies except admin company
#         group1.save()


#         group2 = CompanyUserGroupOp("Accounts","accounting officer",1)
#         group2.save()


#         group3 = CompanyUserGroupOp("Caretaker","property caretaker",1)
#         group3.save()


#         group4 = CompanyUserGroupOp("Tenant","property client",1)
#         group4.save()

# class UpdateUserCompany():
#     """temporary class"""
#     def update_user_company(self):
#         users = UserOp.fetch_all_users()
#         for user in users:
#             company_name = user.company_name
#             if user.user_group_id == 1: #VARYING
#                 company_id = CompanyOp.fetch_usergroup_by_name("KiotaPay").id
#                 UserOp.update_user(user,company_id=company_id)


class CreateAdmin():
    """Helper class to create object/user"""
    def create_admin_user(self):

        present = CompanyOp.fetch_company_by_name("KiotaPay")
        if not present:
            company_obj = CompanyOp("KiotaPay",None,None,None,None,None)
            company_obj.save()

            group1 = CompanyUserGroupOp("Administrator","administrator",company_obj.id)
            group1.save()

            present = UserOp.fetch_user_by_name("Admin")
            if not present:
                admin_user = UserOp("Admin","0000","admin","00000000",+254700100100,"admin@admin","0",1,group1.id,company_obj.id,1)
                admin_user.save()
                print("Admin added")

        print("Admin.................................OK")

class CreateRoles():
    def create_roles(self):

        present1 = GroupRoleOp.fetch_role_by_name("add_user")
        if not present1:
            role1 = GroupRoleOp("add_user")
            role1.save()

        present2 = GroupRoleOp.fetch_role_by_name("update_user")
        if not present2:
            role2 = GroupRoleOp("update_user")
            role2.save()         

        present3 = GroupRoleOp.fetch_role_by_name("create_owner")
        if not present3:
            role3 = GroupRoleOp("create_owner")
            role3.save()

        present4 = GroupRoleOp.fetch_role_by_name("add_apartment")
        if not present4:
            role4 = GroupRoleOp("add_apartment")
            role4.save()

        present5 = GroupRoleOp.fetch_role_by_name("add_house")
        if not present5:
            role5 = GroupRoleOp("add_house")
            role5.save()

        present6 = GroupRoleOp.fetch_role_by_name("register_meter")
        if not present6:
            role6 = GroupRoleOp("register_meter")
            role6.save()

        present7 = GroupRoleOp.fetch_role_by_name("add_tenant")
        if not present5:
            role7 = GroupRoleOp("add_tenant")
            role7.save()

        present8 = GroupRoleOp.fetch_role_by_name("allocate_meter")
        if not present8:
            role8 = GroupRoleOp("allocate_meter")
            role8.save()

        present9 = GroupRoleOp.fetch_role_by_name("allocate_tenant")
        if not present9:
            role9 = GroupRoleOp("allocate_tenant")
            role9.save()

        present10 = GroupRoleOp.fetch_role_by_name("read_meter")
        if not present10:
            role10 = GroupRoleOp("read_meter")
            role10.save()     

        present11 = GroupRoleOp.fetch_role_by_name("define_charge")
        if not present11:
            role11 = GroupRoleOp("define_charge")
            role11.save()

        present12 = GroupRoleOp.fetch_role_by_name("bill_tenant")
        if not present12:
            role12 = GroupRoleOp("bill_tenant")
            role12.save()

        present13 = GroupRoleOp.fetch_role_by_name("amend_charge")
        if not present13:
            role13 = GroupRoleOp("amend_charge")
            role13.save()

        present14 = GroupRoleOp.fetch_role_by_name("grant_rights")
        if not present14:
            role14 = GroupRoleOp("grant_rights")
            role14.save()  

        present15 = GroupRoleOp.fetch_role_by_name("receive_payment")
        if not present15:
            role15 = GroupRoleOp("receive_payment")
            role15.save()         

        present16 = GroupRoleOp.fetch_role_by_name("handle_expenses")
        if not present16:
            role16 = GroupRoleOp("handle_expenses")
            role16.save()  
            print("New roles added")

        present17 = GroupRoleOp.fetch_role_by_name("handle_requests")
        if not present17:
            role17 = GroupRoleOp("handle_requests")
            role17.save()  
            print("New roles added")

        present18 = GroupRoleOp.fetch_role_by_name("view_reports")
        if not present18:
            role18 = GroupRoleOp("view_reports")
            role18.save()  
            print("New roles added")

        print("Roles.................................OK")

    def auto_assign_admin_roles(self):
        company = CompanyOp.fetch_company_by_name("KiotaPay")
        groups = company.groups
        for group in groups:
            group_id = group.id
        
            user_id = 1

            role_objs = GroupRoleOp.fetch_all_roles()
            roles = stringify_list_items(role_objs)
            roles.sort()
            for role in roles:
                # rolestr = str(role)
                roleid = GroupRoleOp.fetch_role_by_name(role).id
                present = get_group_role_assgn_obj(group,role)
                if not present:
                    assign_obj = AssignGroupRoleOp(group_id,roleid,user_id,True)
                    assign_obj.save()
                    print(role + " assigned")
                else:
                    print("Roles already auto assigned")


    # def auto_assign_roles(self):
    #     company = CompanyOp.fetch_company_by_name("Prominance")
    #     groups = company.groups
    #     for group in groups:
    #         group_id = group.id
    #         user_id = 1
    #         role_objs = GroupRoleOp.fetch_all_roles()
    #         roles = stringify_list_items(role_objs)
    #         roles.sort()
    #         for role in roles:
    #             rolestr = str(role)
    #             if rolestr == "create_owner":
    #                 continue
    #             elif rolestr == "add_apartment":
    #                 continue
    #             else:
    #                 roleid = GroupRoleOp.fetch_role_by_name(role).id
    #                 present = get_group_role_assgn_obj(group,role)
    #                 if not present:
    #                     if group.name == "Manager":
    #                         assign_obj = AssignGroupRoleOp(group_id,roleid,user_id,True)
    #                         assign_obj.save()
    #                     else:
    #                         assign_obj = AssignGroupRoleOp(group_id,roleid,user_id,False)
    #                         assign_obj.save()
    #                     print(role + " assigned")
    #                 else:
    #                     print("Roles already auto assigned")


    # def auto_assign_tenant_roles(self):
    #     usergroup1_id = UserGroupOp.fetch_usergroup_by_name("Tenant").id

    #     role_objs = GroupRoleOp.fetch_all_roles()
    #     roles = stringify_list_items(role_objs)
    #     roles.sort()
    #     for role in roles:
    #         rolestr = str(role)

    #         if rolestr == "create_owner":
    #             continue
    #         elif rolestr == "add_apartment":
    #             continue
    #         else:
    #             roleid = GroupRoleOp.fetch_role_by_name(role).id
    #             present = get_group_role_assgn_obj("Tenant",role)
    #             if not present:
    #                 assign_obj = AssignGroupRoleOp(usergroup1_id,roleid,user_id)
    #                 assign_obj.save()
    #                 print(role + " assigned")
    #             else:
    #                 print("Roles already auto assigned")

class MakeRegions():
    def make_regions(self):
        present1 = LocationOp.fetch_location("Ruiru")
        if not present1:
            region1 = LocationOp("Ruiru","Kiambu County")
            region1.save()       

        present2 = LocationOp.fetch_location("Kasarani")
        if not present2:
            region2 = LocationOp("Kasarani","Nairobi County")
            region2.save()

        present3 = LocationOp.fetch_location("Juja")
        if not present3:
            region3 = LocationOp("Juja","Kiambu County")
            region3.save()

        present4 = LocationOp.fetch_location("Thika")
        if not present4:
            region4 = LocationOp("Thika","Kiambu County")
            region4.save()

        present5 = LocationOp.fetch_location("Rongai")
        if not present5:
            region5 = LocationOp("Rongai","Nairobi County")
            region5.save()

        present6 = LocationOp.fetch_location("Ruaka")
        if not present6:
            region6 = LocationOp("Ruaka","Kiambu County")
            region6.save()

        present7 = LocationOp.fetch_location("Roysambu")
        if not present7:
            region7 = LocationOp("Roysambu","Nairobi County")
            region7.save()

        present8 = LocationOp.fetch_location("Kahawa West")
        if not present8:
            region8 = LocationOp("Kahawa West","Kiambu County")
            region8.save()

            print("regions added")
        print("Regions...............................OK")

class CreateChargeTypes():
    """Helper class to create chargetype object"""
    def create_charge_types(self):
        present4 = ChargeTypeOp.fetch_charge_type("All")
        if not present4:
            chargetype_obj = ChargeTypeOp("All")
            chargetype_obj.save()
            print("Chargetype added")
        present = ChargeTypeOp.fetch_charge_type("Water")
        if not present:
            chargetype_obj = ChargeTypeOp("Water")
            chargetype_obj.save()
            print("Chargetype added")
        present2 = ChargeTypeOp.fetch_charge_type("Rent")
        if not present2:
            chargetype_obj = ChargeTypeOp("Rent")
            chargetype_obj.save()
            print("Chargetype added")
        present3 = ChargeTypeOp.fetch_charge_type("Garbage")
        if not present3:
            chargetype_obj = ChargeTypeOp("Garbage")
            chargetype_obj.save()
            print("Chargetype added")

        present5 = ChargeTypeOp.fetch_charge_type("Electricity")
        if not present5:
            chargetype_obj = ChargeTypeOp("Electricity")
            chargetype_obj.save()
            print("Chargetype added")

        present6 = ChargeTypeOp.fetch_charge_type("Security")
        if not present6:
            chargetype_obj = ChargeTypeOp("Security")
            chargetype_obj.save()
            print("Chargetype added")

        present7 = ChargeTypeOp.fetch_charge_type("Maintenance")
        if not present7:
            chargetype_obj = ChargeTypeOp("Maintenance")
            chargetype_obj.save()
            print("Chargetype added")

        print("Charge types..........................OK")


def auto_assign_company_group_roles(company_name):
    company = CompanyOp.fetch_company_by_name(company_name)
    groups = company.groups
    for group in groups:
        if str(group) == "Tenant":
            continue
        group_id = group.id
        user_id = 1
        role_objs = GroupRoleOp.fetch_all_roles()
        roles = stringify_list_items(role_objs)
        roles.sort()
        for role in roles:
            rolestr = str(role)
            if rolestr == "create_owner":
                continue
            elif rolestr == "add_apartment":
                continue
            else:
                roleid = GroupRoleOp.fetch_role_by_name(role).id
                present = get_group_role_assgn_obj(group,role)
                if not present:
                    if group.name == "Manager" or group.name == "Owner":
                        assign_obj = AssignGroupRoleOp(group_id,roleid,user_id,True)
                        assign_obj.save()
                    else:
                        assign_obj = AssignGroupRoleOp(group_id,roleid,user_id,False)
                        assign_obj.save()
                    print(role + " assigned")
                else:
                    print("Roles already auto assigned")

def random_num():
    code = random.randint(101,999)
    return str(code)

def fname_extracter(name):
    try:
        prop = ''
        splitted = name.split()

        one = splitted[0]
        two = splitted[1] if len(splitted) > 1 else ""
        three = splitted[2] if len(splitted) > 2 else ""

        return one + " "+ two + " " + three
    except:
        return ""
    
def lname_extracter(name):
    return name.split()[1]

def username_extracter(name):
    username = name.split()[0]
    return username.lower()

def tenant_extracter(identifier):
    house_name = identifier.split()[0]
    house = house_name.lstrip("#")
    tenant_name = identifier.split()[1]
    return house,tenant_name

def username_extracternum(name):
    rand = random_num()
    lname = name.lower() #lowercase
    username = lname+rand
    return username
    
def username_exctractermail(email):
    username = email.split('@')[0]
    return username

def date_formatter(dd):
    date = dd.split('-')[0]
    month = dd.split('-')[1]
    year = dd.split('-')[2]
    return month + "-" + date + "-" + year

def date_formatter_upload(dd):
    date = dd.split('/')[0]
    month = dd.split('/')[1]
    year = dd.split('/')[2]
    return month + "-" + date + "-" + "20"+year

def date_formatter_alt(dd):
    date = "1"
    month = dd.split('-')[0]
    year = dd.split('-')[1]
    return month + "-" + date + "-" + year

def db_date_formatter(dd):
    year = dd.split('-')[0]
    month = dd.split('-')[1]
    date = dd.split('-')[2]
    return month + "-" + date + "-" + year

def date_formatter_weekday(dd):
    target_part = dd.split(' ')[1]
    date = target_part.split('-')[0]
    month = target_part.split('-')[1]
    year = target_part.split('-')[2]
    return month + "-" + date + "-" + year

def floatHourToTime(fh):
    hours, hourSeconds = divmod(fh, 1)
    minutes, seconds = divmod(hourSeconds * 60, 1)
    return (
        int(hours),
        int(minutes),
        int(seconds * 60),
    )

def uniquename_generator(name,phone):
    str_phone = phone_number_formatter(phone)
    step1 = str_phone[9:]
    step2 = "_"
    step3 = name+step2+step1
    return step3

def parse_for_admin(name):
    if username_extracter(name) == "admin":
        return 1
    else:
        return None

def fetch_user(varying_id):
    first_try = UserOp.fetch_user_by_usercode(varying_id)
    if not first_try:
        second_try = UserOp.fetch_user_by_username(varying_id)
        if not second_try:
            third_try = UserOp.fetch_user_by_national_id(varying_id)
            if not third_try:
                fourth_try = UserOp.fetch_user_by_email(varying_id)
                if not fourth_try:
                    fifth_try = UserOp.fetch_user_by_phone(varying_id)
                    if not fifth_try:
                        return None
                    return fifth_try
                return fourth_try
            return third_try
        return second_try
    return first_try

def usercode_generator():
    code = random.randint(1001,9999)
    return str(code)

def nationalid_generator():
    code = random.randint(8000001,99999999)
    return str(code)

def string_formatter(item):
    return (f"{item:,}") if item > 0 else ""

def string_formatter_alt(item):
    return (f"{item}") if item else ""

def get_numeric_month(month):
    switcher = {
        "January":1,
        "February":2,
        "March":3,
        "April":4,
        "May":5,
        "June":6,
        "July":7,
        "August":8,
        "September":9,
        "October":10,
        "November":11,
        "December":12
        }
    return switcher.get(month)

def get_str_weekday(day):
    switcher = {
        0:"Monday",
        1:"Tuesday",
        2:"Wednesday",
        3:"Thursday",
        4:"Friday",
        5:"Saturday",
        6:"Sunday"
        }
    return switcher.get(day)

def get_str_month(month):
    switcher = {
        1:"January",
        2:"February",
        3:"March",
        4:"April",
        5:"May",
        6:"June",
        7:"July",
        8:"August",
        9:"September",
        10:"October",
        11:"November",
        12:"December"
        }
    return switcher.get(month)

def get_month_year(period):
    switcher = {
        1:"Jan",
        2:"Feb",
        3:"Mar",
        4:"Apr",
        5:"May",
        6:"Jun",
        7:"Jul",
        8:"Aug",
        9:"Sep",
        10:"Oct",
        11:"Nov",
        12:"Dec"
        }
    return f"{switcher.get(period.month)}-{period.year}"

def get_str_mnth(month):
    switcher = {
        1:"Jan",
        2:"Feb",
        3:"Mar",
        4:"Apr",
        5:"May",
        6:"Jun",
        7:"Jul",
        8:"Aug",
        9:"Sep",
        10:"Oct",
        11:"Nov",
        12:"Dec"
        }
    return switcher.get(month)

def get_schedule(param):

    switcher = {
        None:"Monthly'",
        1:"Monthly",
        3:"Quarterly",
        6:"Semi-annually",
        12:"Annually",
        }
    return f'{switcher.get(param)}'

def get_usergroup_id(name):
    #lets fetch the object first
    user_group_name = UserGroupOp.fetch_usergroup_by_name(name)
    user_group_id=user_group_name.id
    return user_group_id

def get_company_usergroup_id(name,co):
    #lets fetch the object first
    groups = co.groups
    user_group_id=None
    for group in groups:
        if str(group) == name:
            user_group_id=group.id
            print(user_group_id)
            break

    return user_group_id

def get_group_name(id):
    group_obj = UserGroupOp.fetch_usergroup_by_id(id)
    return group_obj.name

def get_location_id(name):
    location_name = LocationOp.fetch_location(name)
    location_id=location_name.id
    return location_id

def get_apartment_id(selected_apartment):
    apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
    apartment_id = apartment_obj.id
    return apartment_id

def get_house_id(name):
    #lets fetch the object first
    house_obj = HouseOp.fetch_house(name)# this needs refactoring so as to capture ids of a particular apartment only
    #lets get the id now
    house_id = house_obj.id
    return house_id

def get_meter_id(serial):
    #lets fetch the object first
    meter_obj = MeterOp.fetch_meter_by_serial(serial)
    #lets get the id now
    meter_id = meter_obj.id
    return meter_id

def get_decitype(meter_id):
    meter_obj = MeterOp.fetch_meter_by_id(meter_id)
    decitype = meter_obj.decitype
    if decitype == "0":
        deci = 1.0
    elif decitype == "1":
        deci = 0.1
    elif decitype == "2":
        deci = 0.01
    elif decitype == "3":
        deci = 0.001
    elif decitype == "4":
        deci = 0.0001
    elif decitype == "5":
        deci = 0.00001
    else:
        deci = 1.0
    return deci

def get_str_decitype(meter_id):
    meter_obj = MeterOp.fetch_meter_by_id(meter_id)
    decitype = meter_obj.decitype
    return decitype

def get_tenant_id(name):
    tenant_obj = TenantOp.fetch_tenant_by_name(name)
    return tenant_obj.id
    

def get_owner_id(name):
    owner_obj = OwnerOp.fetch_owner_by_uniquename(name)
    return owner_obj.id

def get_charge_type_id(chargetype):
    chargetype_obj = ChargeTypeOp.fetch_charge_type(chargetype)
    charge_type_id = chargetype_obj.id
    return charge_type_id

def get_specific_house_obj(apartment_id,hse):
    house_list_compare = houseauto(apartment_id)
    house_obj = None
    str_hse = hse.replace(" ","")
    good_hse = str_hse.upper()
    for house in house_list_compare:
        str_house = str(house)
        good_str_house = str_house.upper()
        hh = good_str_house.replace(" ", "")
        # print("looping",hh,hse)
        # print(len(hh),"vs",len(hse))

        if hh == good_hse:
            # print("never happen",str(house),hse)
            house_obj = house
    return house_obj

def get_specific_house_obj_from_house_tenant(apartment_id,raw_hse):
    hse = raw_hse.split(' ')[0]
    house_list_compare = houseauto(apartment_id)
    house_obj = None
    for house in house_list_compare:
        if str(house) == hse:
            house_obj = house
    return house_obj

def get_specific_house_obj_from_house_tenant_alt(apartment_id,raw_hses):
    target_item = raw_hses.split(' ')[0]
    # target_item = hses[0]
    improper_houselist = target_item.lstrip("[").rstrip("]")
    str_houses = improper_houselist.replace(",","")
    proper_houselist = list(str_houses.split(" "))
    target_hse = proper_houselist[0]
    # import pdb
    # pdb.set_trace()

    # print("okerrrrrrroooooooo",raw_hses,target_item,improper_houselist,str_houses,proper_houselist,target_hse)

    house_list_compare = houseauto(apartment_id)
    house_obj = None
    for house in house_list_compare:
        if str(house) == target_hse:
            house_obj = house
    return house_obj

def get_specific_house_obj_from_house_tenant_alt_alt(apartment_id,raw_hses):
    target_item = raw_hses.split('#')[0]
    owner = False
    if raw_hses.endswith(")"):
        owner = True
    # target_item = hses[0]
    improper_houselist = target_item.lstrip("[").rstrip("]")
    str_houses = improper_houselist.replace(",","")
    str_houses2 = str_houses.replace(" ","")
    proper_houselist = list(str_houses2.split(" "))
    target_hse = proper_houselist[0]

    # import pdb
    # pdb.set_trace()

    # print("okerrrrrrroooooooo",raw_hses,target_item,improper_houselist,str_houses,proper_houselist,target_hse)

    house_list_compare = houseauto(apartment_id)
    house_obj = None
    for house in house_list_compare:
        str_hse = str(house)
        if str_hse.replace(" ","") == target_hse:
            house_obj = house

    if house_obj:
        if owner:
            return house_obj,house_obj.owner
    return house_obj,None

def extract_tenant(expr):
    id_part = expr.split(' ')[1]
    id_num = id_part[1:] 
    return TenantOp.fetch_tenant_by_id(id_num)
    
def get_specific_house_obj_alt(option_arr,hse):
    house_obj = None
    for house in option_arr:
        if str(house) == hse:
            house_obj = house
    return house_obj

def get_specific_meter_obj(apartment_id,mtr):
    meter_list_compare = meterauto(apartment_id)
    meter_obj = None
    for meter in meter_list_compare:
        if str(meter) == mtr:
            meter_obj = meter
    return meter_obj

def get_specific_code_obj(apartment_id,housecode):
    prop_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
    code_list_compare = prop_obj.housecodes
    code_obj = None
    for code in code_list_compare:
        if str(code) == housecode:
            code_obj = code
    return code_obj
    
def get_specific_monthly_charge_obj(arr,month,year):
    specific_charge = None
    for item in arr:
        if item.month == month and item.year == year:
            specific_charge = item
            break
    return specific_charge

def get_specific_month_payments(arr,month):
    payments = []
    for item in arr:
        if item.date.month == month:
            payments.append(item)

    return payments

def get_specific_monthly_charge_amount(specific_charge,chargetype):

    if specific_charge:      
        if chargetype == "Water":
            return specific_charge.water
        else:
            return 0.0
    else:
        return 0.0

def fetch_all_usergroups():
    usergroup_list = UserGroupOp.fetch_all_usergroups()
    # #we have list of groups, lets get individual names
    # if usergroup_list:
    #     for group in group_list:
    #         group_obj = UserGroupOp.__repr__(group)
    #         # group_obj = UserGroupOp.view_name(group)
    #         usergroup_list.append(group_obj)
    return usergroup_list
    
def fetch_meter_by_id(meter_id):
    return MeterOp.fetch_meter_by_id(meter_id)

def fetch_all_users():
    user_list = UserOp.fetch_all_users()
    return user_list

def fetch_all_agents():
    # implement less memory consuming fetch in future
    users = fetch_all_users()
    agent_list = []
    for user in users:
        if user.user_group_id == 3:
            agent_list.append(user)
    return agent_list

def fetch_all_roles():
    role_list = GroupRoleOp.fetch_all_roles()
    return role_list

def fetch_all_assigned_roles(user_group_id):
    role_list = AssignGroupRoleOp.fetch_assigned_roles_by_usergroup_id(user_group_id)
    return role_list

def fetch_all_locations():
    location_list = LocationOp.fetch_all_locations()
    return location_list

def fetch_all_apartments_by_owner(owner_id):
    apartment_list = ApartmentOp.fetch_all_apartments_by_owner(owner_id)
    return apartment_list

def fetch_all_apartments_by_user(current_user):
    if current_user.username == "admin":
        apartment_list = ApartmentOp.fetch_all_apartments()
    else:
        apartment_list = ApartmentOp.fetch_all_apartments_by_user(current_user.id)
        
    return apartment_list

def fetch_all_houses_by_user(current_user):
    if current_user.username == "admin":
        house_list = HouseOp.fetch_houses()
    else:
        house_list = HouseOp.fetch_all_houses_by_user(current_user.id)
        
    return house_list

# def fetch_all_apartments():
#     apartment_list = ApartmentOp.fetch_all_apartments()
#     return apartment_list

def houseauto(apartment_id):
    house_list = HouseOp.fetch_houses_by_apartment(apartment_id)
    return house_list

def meterauto(apartment_id):
    meter_list = MeterOp.fetch_meters_by_apartment(apartment_id)
    return meter_list

def readingsauto(period,prop):
    readinglist = []

    db.session.expire(prop)
    readings = prop.meter_readings
    
    month = period.month
    year = period.year

    for reading in readings:
        if reading.reading_period:
            if reading.reading_period.month == month and reading.reading_period.year == year and reading.description != "initial reading":
                readinglist.append(reading)
    
    return readinglist

def readingsauto_new(period,prop):
    readinglist = []

    db.session.expire(prop)
    readings = prop.meter_readings
    
    month_period = period.month
    year = datetime.datetime.now().year
    
    if month_period != 12:
        month_period += 1
        year = datetime.datetime.now().year
    else:
        month_period = 1
        # year = datetime.datetime.now().year + 1
        year = 2022 #URGENT TODO
  
    for reading in readings:
        if reading.reading_period:
            if reading.reading_period.month == month_period and reading.reading_period.year == year and reading.description != "initial reading":
                readinglist.append(reading)
    
    return readinglist

def tenantauto(apartment_id):
    """returns active tenants in a particular apartment"""
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
    db.session.expire(apartment_obj)
    actual_tenant_allocs = []
    tenant_alloc_obj_list = apartment_obj.tenants_allocated
    for alloc in tenant_alloc_obj_list:
        if alloc.active == True:
            actual_tenant_allocs.append(alloc)
    tenant_list = []
    if actual_tenant_allocs:
        for alloc in actual_tenant_allocs:
            tenant_obj = alloc.tenant
            tenant_list.append(tenant_obj)

    new_tenant_list = remove_dups(tenant_list)
    return new_tenant_list

def tenantauto_alt(apartment_id,status):
    """returns active tenants in a particular apartment"""
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
    db.session.expire(apartment_obj)
    ptenants = apartment_obj.ptenants
    client_list = []
    
    for alloc in ptenants:
        ptnt = alloc if alloc.status == status else None
        if ptnt:
            client_list.append(ptnt)

    new_client_list = remove_dups(client_list)
    return new_client_list

def get_clients_by_status(arr,status):
    client_list = []
    for client in arr:
        if client.status == status:
            client_list.append(client)
    return client_list

def get_units_by_status(arr,status):
    client_list = []
    for client in arr:
        if client.status == status:
            client_list.append(client)
    return client_list

def xtenantauto(apartment_id):
    x_tenants = []

    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
    db.session.expire(apartment_obj)
    
    tenant_alloc_obj_list = apartment_obj.tenants_allocated
    for alloc in tenant_alloc_obj_list:
        if alloc.active == False:
            x_tenants.append(alloc.tenant)

    new_list = remove_dups(x_tenants)
    return new_list

def newtenantsauto(apartment_id):
    new_tenants = []
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
    db.session.expire(apartment_obj)
    
    tenant_obj_list = apartment_obj.tenants
    for i in tenant_obj_list:
        if not i.house_allocated:
            new_tenants.append(i)

    return new_tenants

def tenantauto_reverse(apartment_id):
    x_tenant_allocs = []

    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
    db.session.expire(apartment_obj)
    
    tenant_alloc_obj_list = apartment_obj.tenants_allocated
    for alloc in tenant_alloc_obj_list:
        if alloc.active == False:
            x_tenant_allocs.append(alloc)
    print(len(x_tenant_allocs))
    return x_tenant_allocs

def tenantauto_name_gen(prop):
    propid = ApartmentOp.fetch_apartment_by_name(prop).id
    prop_tenants = tenantauto(propid)
    new_list = []
    for tenant in prop_tenants:
        tenant_name = tenant.name
        house = check_house_occupied(tenant)[1]
        identifier = f"#{house} {tenant_name}"
        new_list.append(identifier)
    return new_list

def last_month_vacation_injector(apartment_id):

    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
    period_month = prop.billing_period.month
    period_year = prop.billing_period.year
    target_month = get_prev_month_year(period_month,period_year)[0]
    target_year = get_prev_month_year(period_month,period_year)[1]
    list_of_all_vacations = tenantauto_reverse(apartment_id)
    list_of_recent_vacations = []
    for x_tenant in list_of_all_vacations:
        if x_tenant.vacate_period:
            if x_tenant.vacate_period.month == target_month and x_tenant.vacate_period.year == target_year:
                list_of_recent_vacations.append(x_tenant)

    return list_of_recent_vacations

def recent_vacation_injector(apartment_id):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    list_of_all_vacations = tenantauto_reverse(apartment_id)
    list_of_recent_vacations = []
    for x_tenant in list_of_all_vacations:
        if x_tenant.vacate_date.month == month and x_tenant.vacate_date.year == year:
            list_of_recent_vacations.append(x_tenant)

    return list_of_recent_vacations

def new_tenants_injector(apartment_id,month,year):
    new_list=[]

    tenants = filter_in_tenant_allocs(apartment_id)
    for alloc in tenants:
        if alloc.date.month == month and alloc.date.year == year and alloc.tenant.residency == "New":
            new_list.append(alloc.tenant)
    return new_list

def recent_tenants_injector(apartment_id):
    filtered_allocs = filter_in_tenant_allocs(apartment_id)
    recent_allocs = filter_in_recent_data(filtered_allocs)
    data = []
    for i in recent_allocs:
        data.append(i.tenant)
    return data

def extract_tenant_objects(arr):
    tenant_list = []
    for i in arr:
        tenant_obj = i.tenant
        tenant_list.append(tenant_obj)

    return tenant_list

def user_details(arr):
    tenantdetails = []
    for i in arr:
        new_i = UserOp.view(i)
        tenantdetails.append(new_i)

    return tenantdetails

def tenant_details(arr):
    tenantdetails = []
    for i in arr:
        new_i = TenantOp.view(i)
        tenantdetails.append(new_i)

    return tenantdetails

def lead_details(arr):
    tenantdetails = []
    for i in arr:
        new_i = LeadOp.view(i)
        tenantdetails.append(new_i)

    return tenantdetails

def ptenant_details(arr):
    tenantdetails = []
    for i in arr:
        new_i = PermanentTenantOp.view(i)
        tenantdetails.append(new_i)

    return tenantdetails

def payment_details(arr):
    detailed_payments = []
    for i in arr:
        pay_item = PaymentOp.view(i)
        detailed_payments.append(pay_item)
    return detailed_payments

def ctb_payment_details(arr):
    detailed_payments = []
    for i in arr:
        pay_item = CtoBop.view(i)
        detailed_payments.append(pay_item)
    return detailed_payments


def login_details(arr):
    detailed_payments = []
    for i in arr:
        if i.user.username.startswith("qc"):
            continue
        pay_item = UserLoginDataOp.view(i)
        detailed_payments.append(pay_item)
    return detailed_payments

def submission_details(arr):
    detailed_submissions = []
    for i in arr:
        pay_item = SubmissionOp.view(i)
        detailed_submissions.append(pay_item)
    return detailed_submissions

def bill_details(arr):
    detailed_bills = []
    for i in arr:
        # print("item date and item id", i.month, i.year, "id", i.id)
        bill_item = MonthlyChargeOp.view_detail(i)
        detailed_bills.append(bill_item)

    return detailed_bills

def bill_details_alt(arr):
    detailed_bills = []
    for i in arr:
        bill_item = ClientBillOp.view_detail(i)
        detailed_bills.append(bill_item)

    return detailed_bills

def reading_details(arr):
    readinglist = []
    for i in arr:
        new_i = MeterReadingOp.view(i)
        readinglist.append(new_i)

    return readinglist

def att_details(arr):
    houselist = []
    for i in arr:
        new_i = SalesRepOp.view(i)
        houselist.append(new_i)

    return houselist

def house_details(arr):
    houselist = []
    for i in arr:
        new_i = HouseOp.view(i)
        houselist.append(new_i)

    return houselist

def group_details(arr):
    grouplist = []
    for i in arr:
        new_i = HouseCodeOp.view(i)
        grouplist.append(new_i)

    return grouplist

def meter_details(arr):
    meterlist = []
    for i in arr:
        db.session.expire(i)
        new_i = MeterOp.view(i)
        meterlist.append(new_i)

    return meterlist

def filter_out_metered_houses(selected_apartment):
    apartment_id = get_apartment_id(selected_apartment)
    house_list = houseauto(apartment_id)
    new_list = []

    for house in house_list:
        if not house.meter_allocated:
            new_list.append(house)
        else:
            meter_allocs = house.meter_allocated
            found = False
            for meter_alloc in meter_allocs:
                if meter_alloc.active == True and meter_alloc.meter.metertype == "water":
                    found = True
                    break
            if not found:
                new_list.append(house)

    return new_list


def filter_out_metered_houses_alt(selected_apartment):
    apartment_id = get_apartment_id(selected_apartment)
    house_list = houseauto(apartment_id)
    new_list = []

    for house in house_list:
        if not house.meter_allocated:
            new_list.append(house)
        else:
            meter_allocs = house.meter_allocated
            found = False
            for meter_alloc in meter_allocs:
                if meter_alloc.active == True and meter_alloc.meter.metertype == "electricity":
                    found = True
                    break
            if not found:
                new_list.append(house)

    return new_list
 

def filter_in_metered_houses(selected_apartment):
    apartment_id = get_apartment_id(selected_apartment)
    house_list = houseauto(apartment_id)
    new_list = []
    for house in house_list:
        if house.meter_allocated:
            found = False
            meter_allocs = house.meter_allocated

            for meter_alloc in meter_allocs:
                if meter_alloc.active == True and meter_alloc.meter.metertype == "water":
                    found = True
                    break
            if found:
                new_list.append(house)

    return new_list

def filter_in_metered_houses_alt(selected_apartment):
    apartment_id = get_apartment_id(selected_apartment)
    house_list = houseauto(apartment_id)
    new_list = []
    for house in house_list:
        if house.meter_allocated:
            found = False
            meter_allocs = house.meter_allocated

            for meter_alloc in meter_allocs:
                if meter_alloc.active == True and meter_alloc.meter.metertype == "electricity":
                    found = True
                    break
            if found:
                new_list.append(house)

    return new_list

def filter_out_occupied_houses(selected_apartment):
    apartment_id = get_apartment_id(selected_apartment)
    house_list = houseauto(apartment_id)
    new_list = []
    for house in house_list:
        if not house.tenant_allocated:
            new_list.append(house)

        else:
            found = False
            allocs = house.tenant_allocated
            for alloc in allocs:
                if alloc.active == True:
                    found = True
                    break
            if not found:
                new_list.append(house)

    return new_list

def filter_out_owned_houses(selected_apartment):
    apartment_id = get_apartment_id(selected_apartment)
    house_list = houseauto(apartment_id)
    new_list = []
    for house in house_list:
        if not house.owner:
            new_list.append(house)

    return new_list

def filter_in_occupied_houses(selected_apartment):
    """list of occupied houses ready for tenant clearance/payment"""
    apartment_id = get_apartment_id(selected_apartment)
    house_list = houseauto(apartment_id)
    new_list = []
    for house in house_list:        
        if house.tenant_allocated:
            found = False
            tenant_allocs = house.tenant_allocated
            
            for tenant_alloc in tenant_allocs:
                if tenant_alloc.active == True:
                    found = True
                    break
            if found:
                new_list.append(house)

    return new_list

def check_occupancy(house_obj):
    """check whether house is occupied or not before allocation""" 
    if house_obj.tenant_allocated:
        found = False
        tenant_allocs = house_obj.tenant_allocated
        
        for tenant_alloc in tenant_allocs:
            if tenant_alloc.active == True:
                tenant = tenant_alloc.tenant
                db.session.expire(tenant)
                found = True
                break
        if found:
            return "occupied",tenant
        else:
            return "empty","vacant"

    return "empty","vacant"

def check_house_occupied(tenant_obj):
    """check whether tenant is a resident or alien""" 
    if tenant_obj.house_allocated:
        found = False
        house_allocs = tenant_obj.house_allocated
        
        for house_alloc in house_allocs:
            if house_alloc.active == True:
                house = house_alloc.house
                active_alloc = house_alloc
                found = True
                break
        if found:
            return "Resident",house,active_alloc
        else:
            return "Vacated",None,next(reversed(house_allocs))

    return "booked",None,"bar"

def get_active_houses(tenant_obj):
    """check whether tenant is a resident or alien""" 
    if tenant_obj.house_allocated:
        found = False
        house_allocs = tenant_obj.house_allocated

        houses = []
        
        for house_alloc in house_allocs:
            if house_alloc.active == True:
                house = house_alloc.house
                houses.append(house)
                found = True

        if found:
            if len(houses) > 15:
                return "Resident","Multiple"
            return "Resident",houses
        else:
            return "Vacated",None

    return "booked",None,

def get_owners(hse):
    """check whether tenant is a resident or alien""" 
    if hse.owner:
        return "owned",hse.owner.name
    else:
        return "not owned",None
    

def fetch_active_meter(house_obj):
    """returns active meter""" 
    if house_obj.meter_allocated:
        found = False
        meter_allocs = house_obj.meter_allocated
        
        for meter_alloc in meter_allocs:
            if meter_alloc.active == True and meter_alloc.meter.metertype == "water":
                meter = meter_alloc.meter
                found = True
                break
        if found:
            return meter
        else:
            return None

    return None

def fetch_active_meter_alt(house_obj):
    """returns active meter""" 
    if house_obj.meter_allocated:
        found = False
        meter_allocs = house_obj.meter_allocated
        
        for meter_alloc in meter_allocs:
            if meter_alloc.active == True and meter_alloc.meter.metertype == "electricity":
                meter = meter_alloc.meter
                found = True
                break
        if found:
            return meter
        else:
            return None

    return None


def fetch_specific_metered_house(meter_obj):
    """returns active meter""" 
    if meter_obj.house_allocated:
        found = False
        house_allocs = meter_obj.house_allocated
        
        for house_alloc in house_allocs:
            if house_alloc.active == True:
                active_alloc = house_alloc
                house = house_alloc.house
                found = True
                break
        if found:
            return house, active_alloc
        else:
            return None

    return None

# def filter_out_housed_meters(apartment_id):

#     apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
#     meter_list = apartment_obj.meters
#     new_list = []

#     for meter in meter_list:
#         if not meter.house_allocated:
#             new_list.append(meter)

#         if meter.house_allocated:
#             found = False
#             allocs = meter.house_allocated
#             for alloc in allocs:
#                 if alloc.active == True:
#                     found = True
#                     break
#             if not found:
#                 new_list.append(meter)
#     return new_list

def sort_items(arr):
    try:
        str_arr = []
        for i in arr:
            str_arr.append(str(i))
        if str_arr:
            sorted_items = natsorted(str_arr, key=lambda y: y.lower())
        else:
            sorted_items = []
        return sorted_items
    except:
        return []

def sort_items_by_id(arr):
    try:
        str_arr = []
        for i in arr:
            str_arr.append(str(i.id))
        if str_arr:
            sorted_items = natsorted(str_arr, key=lambda y: y.lower())
        else:
            sorted_items = []

        return [int(i) for i in sorted_items]
    except:
        return []

def generate_house_tenants(arr):
    """combine house and tenant"""
    new_arr = []
    for i in arr:
        hses = get_active_houses(i)[1]

        new_arr.append(f'{hses} #{i.name}')
    return new_arr

def generate_house_ownertenants(arr,propid):
    """combine house and tenant"""
    new_arr = []
    for i in arr:
        if len(get_active_houses(i)[1]) > 1:
            for item in get_active_houses(i)[1]:
                new_arr.append(f'{item}#{i.name}')
        else:
            hses = get_active_houses(i)[1][0]
            new_arr.append(f'{hses}#{i.name}')

    allhses = houseauto(propid)
    for ii in allhses:
        owner = get_owners(ii)[1]
        if owner:
            new_arr.append(f'{ii}#{owner}(owner)')

    return new_arr

def generate_house_owners(propid):
    new_arr = []
    allhses = houseauto(propid)
    for ii in allhses:
        owner = get_owners(ii)[1]
        if owner:
            new_arr.append(f'{ii}#{owner}(owner)')

    return new_arr
    
def generate_house_tenants_alt(arr,arr2):
    """combine house and tenant"""
    new_arr = []

    for i in arr:
        hses = get_active_houses(i)[1]

        new_arr.append(f'{hses} #{i.name}')

    for i in arr2:
        xt_name = i.tenant.name
        xt_id = i.tenant.id
        new_arr.append(f'Vac #{xt_id} {xt_name}')

    return new_arr

def generate_house_tenants_alt2(arr,arr2):
    """combine house and tenant"""
    new_arr = []

    for i in arr:
        # hses = get_active_houses(i)[1]
        tt = check_occupancy(i)
        if tt[0] == "occupied":
            tenant = tt[1]
        else:
            tenant = "Vacant"

        new_arr.append(f'{i} #{tenant}')

    for i in arr2:
        xt_name = i.tenant.name
        xt_id = i.tenant.id
        new_arr.append(f'Vac #{xt_id} {xt_name}')

    return new_arr

def generate_tenant_houses(arr):
    """combine house and tenant"""
    new_arr = []
    for i in arr:
        hses = get_active_houses(i)[1]

        new_arr.append(f'{i.name} #{hses}')
    return new_arr

def generate_tenant_houses_alt(arr,arr2):
    """combine house and tenant"""
    new_arr = []

    for i in arr:
        hses = get_active_houses(i)[1]

        new_arr.append(f'{i.name}#{hses}')

    for i in arr2:
        xt_name = i.tenant.name
        xt_id = i.tenant.id
        new_arr.append(f'Vac #{xt_id} {xt_name}')

    return new_arr

def filter_in_tenant_allocs(apartment_id):
    """filter in housed/residents tenant allocs"""
    alloc_list = AllocateTenantOp.fetch_all_allocs_by_apartment(apartment_id)
    new_list = []
    for alloc in alloc_list:
        if alloc.active:
            new_list.append(alloc)
    return new_list

def filtertenants(apartment_id):
    """filter out housed/residents tenants"""

    tenant_list = TenantOp.fetch_all_tenants_by_apartment(apartment_id)
    new_list = []
    for tenant in tenant_list:
        if not tenant.house_allocated:
            new_list.append(tenant)
        else:
            found = False
            tenant_allocs = tenant.house_allocated
            for tenant_alloc in tenant_allocs:
                # print("wolololololololoo",tenant_alloc,"errror <<<<<<<chuuuuu >>>>>",tenant_allocs)
                if tenant_alloc.active == True:
                    found = True
                    break
            if not found:
                new_list.append(tenant)
    return new_list

def compile_active_requests(apartment_id):
    active_requests = []
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)
    requests = apartment_obj.tenantrequests
    transfers = apartment_obj.transferrequests
    clearances = apartment_obj.clearrequests
    for r in requests:
        if r.status == "pending":
            active_requests.append(r)

    for r in transfers:
        if r.status == "pending":
            active_requests.append(r)

    for r in clearances:
        if r.status == "pending":
            active_requests.append(r)

    return active_requests

def fetch_active_requests(tenant_obj):
    active_requests = []
    requests = tenant_obj.tenantrequests
    for r in requests:
        if r.state == True:
            active_requests.append(r)
    return active_requests

def fetch_reqdata(prop_arr):
    raw_hse_maint = []
    raw_transferreqs = []
    raw_clearreqs = []

    h_pending_reqs = []
    h_queued_reqs = []
    h_running_reqs = []
    h_completed_reqs = []
    h_rejected_reqs = []

    t_pending_reqs = []
    t_completed_reqs = []
    t_rejected_reqs = []

    c_pending_reqs = []
    c_running_reqs = []
    c_completed_reqs = []
    c_rejected_reqs = []

    for prop in prop_arr:
        reqs = prop.tenantrequests
        transferreqs = prop.transferrequests
        clearreqs = prop.clearrequests

        raw_hse_maint.append(reqs)
        raw_transferreqs.append(transferreqs)
        raw_clearreqs.append(clearreqs)

    hse_maint = flatten(raw_hse_maint)
    clear_reqs = flatten(raw_clearreqs)
    transfer_reqs = flatten(raw_transferreqs)

    for obj in hse_maint:
        if obj.status == "pending":
            h_pending_reqs.append(obj)
        if obj.status == "queued":
            h_queued_reqs.append(obj)
        if obj.status == "running":
            h_running_reqs.append(obj)
        if obj.status == "completed":
            h_completed_reqs.append(obj)
        if obj.status == "rejected":
            h_rejected_reqs.append(obj)

    len_h_qued = len(h_queued_reqs)

    reqdata1 = {
        "type":"Maintenance",
        "pending":len(h_pending_reqs),
        "queued":len_h_qued,
        "running":len(h_running_reqs),
        "completed":len(h_completed_reqs),
        "rejected":len(h_rejected_reqs)
    }

    for obj in transfer_reqs:
        if obj.status == "pending":
            t_pending_reqs.append(obj)
        if obj.status == "completed":
            t_completed_reqs.append(obj)
        if obj.status == "rejected":
            t_rejected_reqs.append(obj)

    reqdata2 = {
        "type":"Transfer",
        "pending":len(t_pending_reqs),
        "queued":"N/A",
        "running":"N/A",
        "completed":len(t_completed_reqs),
        "rejected":len(t_rejected_reqs)
    }

    for obj in clear_reqs:
        if obj.status == "pending":
            c_pending_reqs.append(obj)
        if obj.status == "running":
            c_running_reqs.append(obj)
        if obj.status == "completed":
            c_completed_reqs.append(obj)
        if obj.status == "rejected":
            c_rejected_reqs.append(obj)

    reqdata3 = {
        "type":"Clearance",
        "pending":len(c_pending_reqs),
        "queued":"N/A",
        "running":len(c_running_reqs),
        "completed":len(c_completed_reqs),
        "rejected":len(c_rejected_reqs)
    }
    
    reqdata_list = []
    reqdata_list.append(reqdata1)
    reqdata_list.append(reqdata2)
    reqdata_list.append(reqdata3)

    return reqdata_list

def display_reqs(arr,category):
    dispreqs = []
    if category == "Pending":
        for req in arr:
            if req.status == "pending":#no action done on them, new requests
                dispreqs.append(req)
    elif category == "Queued":
        for req in arr:
            if req.status == "queued":#on queue
                dispreqs.append(req)

    elif category == "In progress":
        for req in arr:
            if req.status == "running":#on queue
                dispreqs.append(req)

    elif category == "Completed":
        for req in arr:
            if req.status == "completed":
                dispreqs.append(req)

    else:
        for req in arr:
            if req.status == "rejected":
                dispreqs.append(req)

    return dispreqs

def fetch_current_month_bill(tenant_obj):
 
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month

    bills = tenant_obj.monthly_charges
    for item in bills:
        if item.date.year == year:
            if item.date.month == month:
                return item.total_bill
            continue
        continue
    return 0.0

def fetch_current_invoice(house_obj):

    bills = house_obj.monthlybills
    for item in bills:
        if item.year == house_obj.apartment.billing_period.year and item.month == house_obj.apartment.billing_period.month and item.tenant:
            return item
        continue
    return None

def fetch_target_period_invoice(house_obj,period):

    bills = house_obj.monthlybills
    for item in bills:
        if item.year == period.year and item.month == period.month and item.tenant:
            return item
        continue
    return None

def fetch_current_owner_invoice(house_obj):

    bills = house_obj.monthlybills
    for item in bills:
        if item.year == house_obj.apartment.billing_period.year and item.month == house_obj.apartment.billing_period.month and item.ptenant:
            return item
        continue
    return None

def fetch_target_period_owner_invoice(house_obj,period):

    bills = house_obj.monthlybills
    for item in bills:
        if item.year == period.year and item.month == period.month and item.ptenant:
            return item
        continue
    return None

def fetch_current_month_payments(tenant_obj):
    payment_list = []
    members = []
    total = 0.0

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month

    payments = tenant_obj.payments
    for payment in payments:
        if payment.date.year == year:
            if payment.date.month == month:
                payment_list.append(payment)
    
    for item in payment_list:
        sum_member = item.amount
        members.append(sum_member)

    for member in members:
        total  += member

    return total

def fetch_assigned_roles(usergroup):
    user_group_obj = CompanyUserGroupOp.fetch_usergroup_by_name(usergroup)
    roles = user_group_obj.roles_assigned
    return roles

def filterroles(usergroup):
    roles = fetch_assigned_roles(usergroup)
    role_list = fetch_all_roles()
    str_roles = stringify_list_items(roles)
    str_role_list = stringify_list_items(role_list)

    new_list=[]
    for role in str_role_list:
        if role not in str_roles:
            new_list.append(role)
    new_list.sort()
    return new_list

def getlast_reading(meter_id):
    last_reading = MeterReadingOp.fetch_reading(meter_id)

    ############## HACK HACK HACK FOR DOUBLE READINGS #########################################
    # if last_reading.reading == 204 and str(last_reading.house) == "AUG-1":
    #     MeterReadingOp.delete(last_reading)
    ###########################################################################################

    return last_reading.reading

def fetch_last_reading(meter_id):
    return MeterReadingOp.fetch_reading(meter_id)

def generate_string(arg1,arg2,arg3,arg4,arg5,arg6,arg7):
    string1=""
    string2=""
    string3=""
    string4=""
    string5=""
    string6=""
    string7=""
    
    if isinstance(arg1,str):
        if arg1:
            string1 = "Rent "
    if isinstance(arg2,str):
        if arg2:
            string2 = "Water "
    if isinstance(arg3,str):
        if arg3:
            string3 = "Garbage "
    if isinstance(arg4,str):
        if arg4:
            string4 = "Security "
    if isinstance(arg5,str):
        if arg5:
            string5 = "Arrears "
    if isinstance(arg6,str):
        if arg6:
            string6 = "Deposit"
    if isinstance(arg7,str):
        if arg7:
            string7 = "Service"

    mystring = string1+string2+string3+string4+string5+string6+string7
    print(mystring)

    if mystring=="Rent Water Garbage Security Arrears Deposit":
        return "Rent, Water, Garbage, Security, Arrears & Deposit"

    elif mystring=="Rent Water Garbage Security Arrears ":
        return "Rent, Water, Garbage, Security & Arrears"

    elif mystring=="Rent Water Garbage Security ":
        return "Rent, Water, Garbage & Security"

    elif mystring=="Rent Water Garbage Arrears ":
        return "Rent, Water, Garbage & Arrears"

    elif mystring=="Rent Water Security Arrears ":
        return "Rent, Water, Security & Arrears"

    elif mystring=="Rent Water Security Deposit":
        return "Rent, Water, Security & Deposit"

    elif mystring=="Rent Water Garbage ":
        return "Rent, Water & Garbage"

    elif mystring=="Rent Water Deposit":
        return "Rent, Water & Deposit"

    elif mystring=="Rent Water Arrears ":
        return "Rent, Water & Arrears"

    elif mystring=="Rent Deposit":
        return "Rent & Deposit"

    elif mystring=="Rent Security ":
        return "Rent & Security"

    elif mystring=="Rent Water ":
        return "Rent & Water"

    elif mystring=="Rent Arrears ":
        return "Rent & Arrears"

    elif mystring=="Rent Garbage Security Arrears ":
        return "Rent, Garbage, Security & Arrears"

    elif mystring=="Rent Garbage Security ":
        return "Rent, Garbage & Security"

    elif mystring=="Rent Garbage ":
        return "Rent & Garbage"
    elif mystring=="":
        return "Rent & Utility bills"
    else:
        return mystring

def validate_input(arg):
    # print("VALIDATION STARTING....")
    # print("USER DATA >>> ",arg)

    amount = arg.replace(',', '')
    try:
        float_amount = float(amount)
    except:
        float_amount = 0.0

    # print("VALIDATION ENDING....")

    # print("VALIDATED DATA >>> ",float_amount)
        
    return float_amount

def validate_commission_input(arg):
    amount = arg.replace(',', '')
    try:
        float_amount = float(amount)
    except:
        float_amount = "null"
        
    return float_amount

def validate_tel_input(arg):
    tel = arg.replace(' ', '')       
    return tel

def validate_float_inputs(*args):
    print("Args>>>>>>>>",args)
    results = []
    for i in args:
        if i is None:
            results.append("null")
            continue

        ii = i.replace(',', '')
        print(len(ii))

        if len(ii) == 0:
            results.append("null")
        else:
            try:
                new_i = float(ii)
                results.append(new_i)
            except:
                results.append("null")
    return results

def validate_float_inputs_to_exclude_zeros(*args):
    print("INPUT", args)

    results = []
    for i in args:
        if not i:
            results.append(0.0)
        else:
            if isinstance(i,float):
                results.append(i)

            else:
                ii = i.replace(",","")

                if len(ii) == 0:
                    results.append(0.0)
                else:
                    try:
                        new_i = float(ii)
                        results.append(new_i)
                    except:
                        results.append(0.0)

    print("OUTPUT",results)
    return results

def validate_float_inputs_to_include_percent(*args):
    print("Args>>>>>>>>",args)
    results = []
    for i in args:
        if i is None:
            results.append("null")
            continue
        ii = i.replace(',', '')
        iii = ii.replace('%','')

        if len(iii) == 0:
            results.append("null")
        else:
            try:
                new_i = float(iii)
                results.append(new_i)
            except:
                results.append("null")
    return results


def validate_float_inputs_to_exclude_zeros_alt(*args):

    print("INPUT", args)

    results = []
    for i in args:
        print("VALIDATING...",type(i),i)
        if not isinstance(i,float):
            ii = i.replace(",","")
            try:
                new_i = float(ii)
                results.append(new_i)
            except:
                results.append(0.0)

        else:
            results.append(i)

    print("OUTPUT",results)

    return results
    

def generate_month_list():
    return ["January","February","March","April","May","June","July","August","September","October","November","December"]

def generate_array(houses,prop_obj):

    target_houses = []
    house_list_compare = houseauto(prop_obj.id)
    house_list = houses.split(',')

    for i in house_list_compare:
        for x in house_list:
            if str(i) == x.upper():
                target_houses.append(i)

    print("xxxxxxxxxxxxxxxxxxxx>>>>>>>>>>>>",target_houses)

    return target_houses
       
def check_accessright(user_group,grouprole):
    # print(user_group.id)
    # print(user_group.company.name)
    role_list_compare= user_group.roles_assigned # list of assignment objs
    assignment_obj = None
    for assgn in role_list_compare:
        if str(assgn) == grouprole:
            assignment_obj = assgn
            break
    if assignment_obj:
        accessright = assignment_obj.accessright
        return accessright
    return False

def return_bool(accessright):
    if accessright == "null":
        return "null"
    elif accessright != "False":
        return True
    else:
        return False

def return_bool_alt(param):
    if param == "null":
        return False
    elif param == "False":
        return False
    else:
        return True

def return_bool_alt_alt(param):
    if param == "null":
        return "null"
    elif param == "False":
        return False
    else:
        return True

def get_billing_period(prop):
    period = prop.billing_period
    return period

def get_identifier(str):
    try:
        for i in str:
            if i.isdigit():
                target_index = str.index(i)
                break

        identifier = str[target_index:]
    except:
        identifier = "1000000000"
    
    return identifier

def get_affirmative(accessbool):
    if accessbool == True:
        return "yes"
    else:
        return "no"

def get_bool(arg):
    try:
        if arg == "True":
            return True
        else:
            return False
    except:
        return False

def get_group_role_assgn_obj(user_group,grouprole):
    role_list_compare= user_group.roles_assigned # list of assignment objs
    assignment_obj = None
    for assgn in role_list_compare:
        if str(assgn) == grouprole:
            assignment_obj = assgn
    if assignment_obj:
        return assignment_obj
    return None

def fetch_total_deposit(hse_obj,billable):

    print(">>>>>>>>>>>>>>>>>>>>>>>>>> Billing?",billable)
    
    if not billable:
        dep = 0.0
    else:
        rent = hse_obj.housecode.rentrate
        water = hse_obj.housecode.waterdep
        electricity = hse_obj.housecode.elecdep
        dep = rent+water+electricity

    return dep

def generate_date(month,year):
    # print("Month",month,"Year",year)
    # if month == 2:
    #     day = datetime.datetime.now()
    
    # day = datetime.datetime.now()
    # .day if month != 2 else datetime.datetime.now().day - 3
    return datetime.datetime(year, month, 15)

def generate_exact_date(day,month,year):
    # print("Month",month,"Year",year)
    # if month == 2:
    #     day = datetime.datetime.now()
    
    # day = datetime.datetime.now()
    # .day if month != 2 else datetime.datetime.now().day - 3
    return datetime.datetime(year, month, day)

def generate_start_date(month,year):
    # if month == 2:
    #     day = datetime.datetime.now()
    
    # day = datetime.datetime.now()
    # .day if month != 2 else datetime.datetime.now().day - 3
    return datetime.datetime(year, month, 1)

def generate_end_date(month,year):
    if month == 2:
        return datetime.datetime(year, month, 28)
    return datetime.datetime(year, month, 30)

def calculate_sms_cost(sms,cost):
    try:
        cost = float(cost[4:])
        if cost < 0.9:
            sms -= 1
        elif cost < 1.7:
            sms -= 2
        elif cost < 2.5:
            sms -= 3
        elif cost < 3.3:
            sms -= 4
        else:
            sms -= 5
        
    except Exception as e:
        print("There was an error",e,"in remaining sms calculation")

    return sms

def calculate_sms_cost_alt(sms,smstext):
    try:
        sms_len = len(smstext)

        if sms_len < 140:
            sms -= 1
        elif sms_len < 280:
            sms -= 2
        else:
            sms -= 3
        
    except Exception as e:
        print("There was an error",e,"in remaining sms calculation")

    return sms

# def specific_water_bill(apartment_id,chargetype,user_id):
#     charge_type_id = get_charge_type_id(chargetype)
#     apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)#get apartment obj first
#     meter_readings = ApartmentOp.view_meterreadings(apartment_obj) #meter_readings list objects in a particular apartment
#     for meter_reading in meter_readings:
#         units = meter_reading.units
#         reading_id= meter_reading.id
#         apartment_id = meter_reading.apartment_id
#         house_id = meter_reading.house_id
#         meter_id = meter_reading.meter_id
#         meter = MeterOp.fetch_meter_by_id(meter_id)
#         unitcost = meter.unit_cost
#         bill_amount = units*unitcost

#         existing_charge_obj=ChargeOp.fetch_charge_by_reading_id(reading_id)
#         if not existing_charge_obj:
#             house_obj = HouseOp.fetch_house_by_id(house_id)
#             if house_obj:
#                 if not house_obj.billable:
#                     charge_obj =  ChargeOp(charge_type_id,0.0,apartment_id,house_id,user_id,meter_id,reading_id)#REFACTOR meter can be left out for rent,garbage and security
#                     charge_obj.save()
#                     charge_status = True

#                     MeterReadingOp.update_charge_status(meter_reading,charge_status)
#                 else:
#                     charge_obj =  ChargeOp(charge_type_id,bill_amount,apartment_id,house_id,user_id,meter_id,reading_id)#REFACTOR meter can be left out for rent,garbage and security
#                     charge_obj.save()
#                     charge_status = True

#                     MeterReadingOp.update_charge_status(meter_reading,charge_status)


def send_statement(tenantid):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    tid = get_identifier(tenantid)
    ptenant = PermanentTenantOp.fetch_tenant_by_id(tid)

    statement_url = f"https://kiotapay.com/account/statement?target=direct&uuid={ptenant.id}"

    prop = ptenant.apartment
    co = prop.company
    str_co = co.name

    raw_rem_sms =co.remainingsms


    #Send the SMS
    # tele = ptenant.phone
    tele = "0716444750"
    name = ptenant.name
    fname = fname_extracter(name)
    if not fname:
        fname = name
    phonenum = sms_phone_number_formatter(tele)

    try:
        # temp_txt = "This a friendly reminder that your rent for June was due on or by 5/6/2021. We thank you for timely payment. \nPlease note: \nIf rent is received after 5/6/2021,please add a late fee 10% of your rent."

        recipient = [phonenum]
        message = f"Dear {fname}, \nClick on the link below to find your statement of accounts. \n{statement_url}.\n\n~{str_co}."

        char_count = len(message)
        if char_count <= 160:
            cost = 1
        elif char_count <= 320:
            cost = 2
        else:
            cost = 3
        
        sms_obj = SentMessagesOp(message,char_count,cost,None,ptenant.id,prop.id,co.id)
        sms_obj.save()


        if co.sms_provider == "Advanta" or prop.name == "Greatwall Gardens 2":
            sms_sender(co.name,message,phonenum)

        # if co.name == "Lesama Ltd":
        #     advanta_send_sms(message,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")
        # elif co.name == "KEVMA REAL ESTATE":
        #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
        else:
            #Once this is done, that's it! We'll handle the rest
            response = sms.send(message, recipient, sender)
            print(response)
            resp = response["SMSMessageData"]["Recipients"][0]
                                            
            code = resp["statusCode"]

            if code == 101: # SMS WAS SENT
                raw_cost = resp["cost"]
                rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                CompanyOp.set_rem_quota(co,rem_sms)
                print("EVERYTHING IS SMOOTH")
                
            elif code == 403:
                print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                
            elif code == 405:
                response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
                print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                
            elif code == 406:
                raw_cost = resp["cost"]
                rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                CompanyOp.set_rem_quota(co,rem_sms)
                print("SMS BLOCKED BY ",ptenant,prop)
            else:
                print("ALAAAAAAAA")

    except Exception as e:
        print(f"Houston, we have a problem {e}")



def send_bulk_sms(propid,temp_txt):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    tenants1 = tenantauto(propid)
    tenants2 = ApartmentOp.fetch_apartment_by_id(propid).ptenants
    tenants = tenants1 + tenants2

    for tenant_obj in tenants:

        prop = tenant_obj.apartment
        co = prop.company
        # str_co = co.name
        str_co = ""


        if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
            ptenant_id = tenant_obj.id
            tenant_id = None
        else:
            tenant_id = tenant_obj.id
            ptenant_id = None

        own_shortcode = False

        if co.name == "Lesama Ltd" or co.name == "Merit Properties Limited" or prop.name == "Greatwall Gardens 2":
            own_shortcode = True


        raw_rem_sms = co.remainingsms
        if own_shortcode:
            raw_rem_sms = 5000
        if tenant_obj.sms:

            if raw_rem_sms > 0 or own_shortcode:

                #Send the SMS
                tele = tenant_obj.phone
                name = tenant_obj.name
                fname = fname_extracter(name)
                if not fname:
                    fname = name
                phonenum = sms_phone_number_formatter(tele)

                try:
                    # temp_txt = "This a friendly reminder that your rent for June was due on or by 5/6/2021. We thank you for timely payment. \nPlease note: \nIf rent is received after 5/6/2021,please add a late fee 10% of your rent."

                    recipient = [phonenum]
                    message = f"Dear {fname}, \n{temp_txt}.\n\n~{str_co}."

                    char_count = len(message)
                    if char_count <= 160:
                        cost = 1
                    elif char_count <= 320:
                        cost = 2
                    else:
                        cost = 3
                    
                    sms_obj = SentMessagesOp(message,char_count,cost,tenant_id,ptenant_id,prop.id,co.id)
                    sms_obj.save()

                    # allowed = True
                    # if allowed:
                    if co.sms_provider == "Advanta" or prop.name == "Greatwall Gardens 2":
                        sms_sender(co.name,message,phonenum)

                    # if co.name == "Lesama Ltd":
                    #     advanta_send_sms(message,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")
                    # elif co.name == "KEVMA REAL ESTATE":
                    #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
                    else:
                        #Once this is done, that's it! We'll handle the rest
                        response = sms.send(message, recipient, sender)
                        print(response)
                        resp = response["SMSMessageData"]["Recipients"][0]
                                                        
                        code = resp["statusCode"]

                        if code == 101: # SMS WAS SENT
                            raw_cost = resp["cost"]
                            rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                            CompanyOp.set_rem_quota(co,rem_sms)
                            print("EVERYTHING IS SMOOTH")
                            
                        elif code == 403:
                            print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            
                        elif code == 405:
                            response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
                            print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            
                        elif code == 406:
                            raw_cost = resp["cost"]
                            rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                            CompanyOp.set_rem_quota(co,rem_sms)
                            print("SMS BLOCKED BY ",tenant_obj,prop)
                        else:
                            print("ALAAAAAAAA")

                except Exception as e:
                    print(f"Houston, we have a problem {e}")
            else:
                txt = f"{co} has depleted sms"
                response = sms.send(txt, ["+254716674695"],sender)
                print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN CLIENT HAS DEPLETED SMS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                break
        else:
            print("XXXXXXXXXXXXXXXXXXXXXXXXXX Tenant sms disabled",tenant_obj,prop, "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

def send_reminder_sms(propid,temp_txt,rem_bal):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    tenants1 = tenantauto(propid)
    tenants2 = ApartmentOp.fetch_apartment_by_id(propid).ptenants
    tenants = tenants1 + tenants2

    for tenant_obj in tenants:

        prop = tenant_obj.apartment
        co = prop.company
        str_co = co.name

        if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
            ptenant_id = tenant_obj.id
            tenant_id = None
        else:
            tenant_id = tenant_obj.id
            ptenant_id = None

        own_shortcode = False

        if co.name == "Lesama Ltd" or co.name == "Merit Properties Limited" or prop.name == "Greatwall Gardens 2":
            own_shortcode = True

        raw_rem_sms =co.remainingsms

        if own_shortcode:
            raw_rem_sms = 5000

        if tenant_obj.sms:

            if raw_rem_sms > 0 or own_shortcode:

                if tenant_obj.balance > 0.0:
                    pass
                else:
                    continue

                #Send the SMS
                tele = tenant_obj.phone
                name = tenant_obj.name
                fname = fname_extracter(name)
                if not fname:
                    fname = name
                phonenum = sms_phone_number_formatter(tele)

                try:
                    # temp_txt = "This a friendly reminder that your rent for June was due on or by 5/6/2021. We thank you for timely payment. \nPlease note: \nIf rent is received after 5/6/2021,please add a late fee 10% of your rent."

                    recipient = [phonenum]
                    message = f"Dear {fname}, \n{temp_txt}. \nBalance: Kshs. {tenant_obj.balance} \n\n~{str_co}."

                    char_count = len(message)
                    if char_count <= 160:
                        cost = 1
                    elif char_count <= 320:
                        cost = 2
                    else:
                        cost = 3
                    
                    sms_obj = SentMessagesOp(message,char_count,cost,tenant_id,ptenant_id,prop.id,co.id)
                    sms_obj.save()


                    if co.sms_provider == "Advanta":
                    # allowed = True
                    # if allowed:
                        sms_sender(co.name,message,phonenum)

                    # if co.name == "Lesama Ltd":
                    #     advanta_send_sms(message,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")
                    # elif co.name == "KEVMA REAL ESTATE":
                    #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
                    else:
                        #Once this is done, that's it! We'll handle the rest
                        response = sms.send(message, recipient, sender)
                        print(response)
                        resp = response["SMSMessageData"]["Recipients"][0]
                                                        
                        code = resp["statusCode"]

                        if code == 101: # SMS WAS SENT
                            raw_cost = resp["cost"]
                            rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                            CompanyOp.set_rem_quota(co,rem_sms)
                            print("EVERYTHING IS SMOOTH")
                            
                        elif code == 403:
                            print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            
                        elif code == 405:
                            response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
                            print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            
                        elif code == 406:
                            raw_cost = resp["cost"]
                            rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                            CompanyOp.set_rem_quota(co,rem_sms)
                            print("SMS BLOCKED BY ",tenant_obj,prop)
                        else:
                            print("ALAAAAAAAA")

                except Exception as e:
                    print(f"Houston, we have a problem {e}")
            else:
                txt = f"{co} has depleted sms"
                response = sms.send(txt, ["+254716674695"],sender)
                print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN CLIENT HAS DEPLETED SMS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                break
        else:
            print("XXXXXXXXXXXXXXXXXXXXXXXXXX Tenant sms disabled",tenant_obj,prop, "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


def autosend_pending_smsreceipts(payids):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    for payment_id in payids:
        payment_obj = PaymentOp.fetch_payment_by_id(payment_id)
        db.session.expire(payment_obj)
        if payment_obj.sms_status != "pending":
            print("Skipping ahead>>>>>>>>>>>>>>>>>>>>")
            continue

        if payment_obj.ref_number != "N/A" and payment_obj.ref_number:
            reference = f'#{payment_obj.ref_number}'
        else:
            reference = f'#{payment_obj.id}'

        serv = False
        if payment_obj.ptenant:
            serv = True
            tenant_obj = payment_obj.ptenant
            ptenant_id = tenant_obj.id
            tenant_id =  None
        else:
            tenant_obj = payment_obj.tenant
            tenant_id = tenant_obj.id
            ptenant_id =  None

        if tenant_obj.balance < 0:
            bal = tenant_obj.balance * -1
            running_bal = (f"Advance: KES {bal:,}")
        else:
            running_bal = (f"Balance: KES {tenant_obj.balance:,}")

        amount = f'Kes {payment_obj.amount:,.0f}'

        receipt = f"Receipt: https://kiotapay.com/r/{payment_obj.rand_id}"

        co = payment_obj.apartment.company
        str_co = co.name
        str_prop = payment_obj.apartment.name
        end = str_co if payment_obj.apartment.company.name != "LaCasa" else str_prop 
        raw_rem_sms =co.remainingsms

        own_shortcode = False

        if co.name == "Lesama Ltd" or co.name == "Merit Properties Limited" or payment_obj.apartment.name == "Greatwall Gardens 2":
            own_shortcode = True

        if own_shortcode:
            raw_rem_sms = 5000

        tele = tenant_obj.phone
        # name = tenant_obj.name
        # fname = fname_extracter(name)
        # if not fname:
        #     fname = name
        phonenum = sms_phone_number_formatter(tele)
        salutation = "Service Charge & Utility" if serv else "Rental"

        message = f"{salutation} payment Ref {reference}, sum of {amount} confirmed. \n{running_bal} \n\n{receipt} \n\n~{end}."

        if tenant_obj.sms:

            char_count = len(message)
            if char_count <= 160:
                cost = 1
            elif char_count <= 320:
                cost = 2
            else:
                cost = 3
            
            sms_obj = SentMessagesOp(message,char_count,cost,tenant_id,ptenant_id,payment_obj.apartment.id,co.id)
            sms_obj.save()
            
            # own_shortcode = False

            # if co.name == "Lesama Ltd" or co.name == "Merit Properties Limited" or payment_obj.apartment.name == "Greatwall Gardens 2":
            #     own_shortcode = True

            # if payment_obj.apartment.company.name == "Lesama Ltd":
            #     advanta_send_sms(message,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")
            #     PaymentOp.update_sms_status(payment_obj,"sent")
            # elif payment_obj.apartment.company.name == "KEVMA REAL ESTATE":
            #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
            #     PaymentOp.update_sms_status(payment_obj,"sent")

            if raw_rem_sms > 0 or own_shortcode:
                #Send the SMS

                try:
                    print("Payment sms sending initiated")
                    recipient = [phonenum]

                    if co.sms_provider == "Advanta":
                        smsid = sms_sender(co.name,message,phonenum)
                        if smsid:
                            PaymentOp.update_smsid(payment_obj,smsid)
                    else:
                        #Once this is done, that's it! We'll handle the rest
                        response = sms.send(message, recipient,sender)
                        print(response)
                        resp = response["SMSMessageData"]["Recipients"][0]

                        code = resp["statusCode"]
                        smsid = resp["messageId"]
                        if smsid:
                            PaymentOp.update_smsid(payment_obj,smsid)

                        if code == 101: # SMS WAS SENT

                            PaymentOp.update_sms_status(payment_obj,"sent")
                            raw_cost = resp["cost"]
                            rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                            CompanyOp.set_rem_quota(co,rem_sms)

                        elif code == 403:
                            print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            PaymentOp.update_sms_status(payment_obj,"fail")
                        elif code == 405:
                            print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            txt = f"{co} has depleted sms"
                            response = sms.send(txt, ["+254716674695"],"KIOTAPAY")
                        elif code == 406:
                            PaymentOp.update_sms_status(payment_obj,"blocked")
                            print("SMS BLOCKED BY ",tenant_obj,payment_obj.house,payment_obj.apartment)
                            raw_cost = resp["cost"]
                            rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                            CompanyOp.set_rem_quota(co,rem_sms)
                    
                except Exception as e:
                    print(f"Houston, we have a problem {e}")
                    PaymentOp.update_sms_status(payment_obj,"fail")
            else:
                print("CLIENT HAS DEPLETED SMS",str_co)
        else:
            PaymentOp.update_sms_status(payment_obj,"off")

def send_out_email_invoices(prop,houses,override,charge,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    try:
        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
        update = False

        if prop_obj and charge == "all":

            billing_period = get_billing_period(prop_obj)

            target_bills = []

            multitenant_target_bills = []

            multitenants = []

            if houses and houses != "ALL":
                # if  override:
                """Specified houses for all charges invoices"""
                update = True
                house_list = generate_array(houses,prop_obj)

                for house in house_list:
                    bills = fetch_current_billing_period_bills(billing_period,house.monthlybills)
                    for bill in bills:
                        target_bills.append(bill)
                    

            else:
                if houses:
                    """Entire houses in a property (ALL)"""
                    update = True
                    house_list = houseauto(prop_obj.id)
                    for house in house_list:
                        bills = fetch_current_billing_period_bills(billing_period,house.monthlybills)
                        for bill in bills:
                            target_bills.append(bill)
                else:
                    """Normal message sending, doesnt allow double sending"""
                    house_list = houseauto(prop_obj.id)
                    for house in house_list:
                        bills = fetch_current_billing_period_bills(billing_period,house.monthlybills)
                        for bill in bills:
                            if bill.email_invoice != "sent":
                                if bill.tenant.multiple_houses:
                                    multitenant_target_bills.append(bill)
                                    multitenants.append(bill.tenant)
                                else:
                                    target_bills.append(bill)
                            else:
                                target_bills.append(bill)



            try:
                with mail.connect() as conn:

                    non_duplicate_multitenants = remove_dups(multitenants)

                    for tenant in non_duplicate_multitenants:
                        print("TENANTS LENGTH>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",len(non_duplicate_multitenants))

                        email_addr = tenant.email
                        if not email_addr:
                            print("Email address not found for tenant ",tenant.name,"-",prop)
                            continue

                        multitenant_specific_bills = []
                        invoices = []

                        for bill in multitenant_target_bills:
                            if bill.tenant == tenant:
                                multitenant_specific_bills.append(bill)

                        for bill in multitenant_specific_bills:
                            print("MULTITENANT INVOICE IS BEING PREPARED", bill.email_invoice)

                            print("TENANTS BILLS LENGTH>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FOR",tenant,"ARE>>>>>>>",len(multitenant_specific_bills))


                            co = bill.apartment.company
                    
                            invnum = bill.id + 13285

                            house = bill.house



                            sibling_water_bill = fetch_current_billing_period_readings(bill.apartment.billing_period,bill.house.meter_readings)
                            sibling_electricity_bill = fetch_current_billing_period_readings_alt(bill.apartment.billing_period,bill.house.meter_readings)

                            try:
                                wbill = sibling_water_bill[0]
                                w_edited = "dispnone" if wbill.units == float(wbill.reading) - float(wbill.last_reading) else ""
                            except:
                                wbill = None
                                w_edited = "dispnone"

                            try:
                                ebill = sibling_electricity_bill[0]
                                e_edited = "dispnone" if ebill.units == float(ebill.reading) - float(ebill.last_reading) else ""
                            except:
                                ebill = None
                                e_edited = "dispnone"



                            if wbill or ebill:
                                visibility = ""
                            else:
                                visibility = "hide"

                            arrears = bill.arrears
                            
                            if bill.paid_amount:
                                billpaid = f"{bill.paid_amount:,.2f}"
                                billbal = f"{bill.balance:,.2f}"

                            else:
                                billpaid = 0.0
                                billbal = 0.0

                            if arrears < 0.0:
                                arrtitle = "Advance"
                                bbfhighlight = "text-success"

                                arrears = f"{arrears*-1}"
                            elif arrears > 0.0:
                                arrtitle = "Arrears"
                                bbfhighlight = "text-danger"
                            else:
                                arrtitle = ""
                                bbfhighlight = ""


                            timenow = datetime.datetime.now()
                            # diff = timenow.day - 2
                            diff = 0
                            invdate = bill.date - relativedelta(days = diff)

                            inv_date = invdate.strftime("%d/%b/%y")
                            invdue = invdate + relativedelta(days=11)
                            inv_due = invdue.strftime("%d/%b/%y")

                            kiotapay = CompanyOp.fetch_company_by_name("KiotaPay")

                            ###################################################################################

                            templateLoader = FileSystemLoader(searchpath="app/templates")
                            templateEnv = Environment(loader=templateLoader)
                            TEMPLATE_FILE = "ajax_tenant_invoice_mail.html"
                            template = templateEnv.get_template(TEMPLATE_FILE)

                            template_vars = {
                                "bill":bill,
                                "readings": wbill,
                                "w_edited": w_edited,
                                "ereadings": ebill,
                                "e_edited": e_edited,
                                "visibility":visibility,
                                "arrears":arrears,
                                "bbfhighlight ": bbfhighlight,
                                "arrtitle":arrtitle,
                                "billpaid":billpaid,
                                "billbal":billbal,
                                "house":house,
                                "total":f"{bill.total_bill:,.2f}",
                                "invdate":inv_date,
                                "invdue":inv_due,
                                "client":tenant,
                                "company":co,
                                "invnum":invnum,
                                "logo":logo(co)[2],
                                "slogo":logo(kiotapay)[1]
                            }

                            html_out = template.render(template_vars)
                            filename = f"app/temp/inv_{bill.id}.pdf"
                            HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/myfonts.css","app/static/eapartment-min.css","app/static/kiotapay.css"])
                            invoices.append(filename)
                            #####################################################################################################################################

                        ###################################################################################
                        # LETS SEND EMAIL
                        # mail_filename = f"inv_{bill.id}"
                        # with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
                        
                            # print (fh)
                        try:
                            try:
                                tname = tenant.name.split('and')[0]
                            except:
                                tname = tenant.name

                            thouses = get_active_houses(tenant)[1]
                            str_thouses = ','.join(map(str, thouses))

                            period = f"{get_str_month(bill.month)} invoices"

                            filename_ext = f"{get_str_month(bill.month)}invoice.pdf"

                            txt = Message(period, sender = mailsender, recipients = [email_addr])
                            txt.body = f"Dear {tname}  \nYour invoice(s) are now available for {str_thouses}. Kindly find the attached invoices. \n\n{co.name}"
                            for inv in invoices:
                                with open(inv,'rb') as fh:
                                    billid = inv.split("_")[1].rstrip(".pdf")
                                    tbill = MonthlyChargeOp.fetch_specific_bill(billid)
                                    txt.attach(filename=f"{tbill.house.name} {filename_ext}",disposition="attachment",content_type="application/pdf",data=fh.read())
                                    # mail.send(txt)
                                    MonthlyChargeOp.update_email_status(tbill,"sent")
                                os.remove(inv)
                            conn.send(txt)
                            #########################################################################################
                        except Exception as e:
                            print(str(e))
                            
                    for bill in target_bills:
                        if bill.ptenant:
                            tenant=bill.ptenant
                            current_target = "owner"
                            print("OWNER INVOICE IS BEING PREPARED FOR" ,bill.ptenant.name)
                        else:
                            current_target = "tenant"
                            tenant=bill.tenant
                            print("TENANT INVOICE IS BEING PREPARED FOR" ,bill.tenant.name)

                        co = bill.apartment.company
                
                        invnum = bill.id + 13285

                        house = bill.house

                        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",tenant.name)

                        #start here
                        sibling_water_bill = fetch_current_billing_period_readings(bill.apartment.billing_period,bill.house.meter_readings)
                        sibling_electricity_bill = fetch_current_billing_period_readings_alt(bill.apartment.billing_period,bill.house.meter_readings)

                        try:
                            wbill = sibling_water_bill[0]
                            w_edited = "dispnone" if wbill.units == float(wbill.reading) - float(wbill.last_reading) else ""
                        except:
                            wbill = None
                            w_edited = "dispnone"

                        try:
                            ebill = sibling_electricity_bill[0]
                            e_edited = "dispnone" if ebill.units == float(ebill.reading) - float(ebill.last_reading) else ""
                        except:
                            ebill = None
                            e_edited = "dispnone"


                        kiotapay = CompanyOp.fetch_company_by_name("KiotaPay")
                        invdate = bill.date - relativedelta(days = 0)
                        inv_date = invdate.strftime("%d/%b/%y")
                        invdue = invdate + relativedelta(days=6)
                        inv_due = invdue.strftime("%d/%b/%y")

                    
                        email_addr = tenant.email
                        if email_addr:
                            if wbill or ebill:
                                visibility = ""
                            else:
                                visibility = "hide"

                            arrears = bill.arrears
                            
                            if bill.paid_amount:
                                billpaid = f"{bill.paid_amount:,.2f}"
                                billbal = f"{bill.balance:,.2f}"

                            else:
                                billpaid = 0.0
                                billbal = 0.0

                            if arrears < 0.0:
                                arrtitle = "Previous balance"
                                bbfhighlight = "text-success"

                                arrears = f"{arrears*-1}"
                            elif arrears > 0.0:
                                arrtitle = "Previous balance"
                                bbfhighlight = "text-danger"
                            else:
                                arrtitle = ""
                                bbfhighlight = ""

                            if current_target == "owner":
                                if bill.house.watertarget == "owner":
                                    watertarget = True
                                else:
                                    watertarget = False
                            else:
                                if bill.house.watertarget == "tenant":
                                    watertarget = True
                                else:
                                    watertarget = False

                            print("WATERTAGET ############################",watertarget)

                            if bill.apartment_id == 398:
                                paymentacc = f"Paybill No. {bill.apartment.payment_bank}, Acc: {bill.apartment.name.upper()[:3]} {bill.house.name}"
                            else:
                                paymentacc = ""

                            template_vars = {
                                "bill":bill,
                                "servicevisibility":"",
                                "readings": wbill,
                                "w_edited": w_edited,
                                "ereadings": ebill,
                                "e_edited": e_edited,
                                "visibility":visibility,
                                "watertarget":watertarget,
                                "arrears":arrears,
                                "bbfhighlight ": bbfhighlight,
                                "arrtitle":arrtitle,
                                "billpaid":billpaid,
                                "billbal":billbal,
                                "house":house,
                                "total":f"{bill.total_bill:,.2f}",
                                "invdate":inv_date,
                                "invdue":inv_due,
                                "client":tenant,
                                "paymentacc":paymentacc,
                                "company":co,
                                "invnum":invnum,
                                "logo":logo(co)[2],
                                "slogo":logo(kiotapay)[1]
                            }

                            mail_sender(conn,tenant,bill,template_vars,email_addr,co)
                        else:
                            print("Email address not found for tenant ",tenant.name,"-",prop)                             

            except Exception as e:
                print("Mail failed to connect >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",e)
    except Exception as e:
        print("WORKING HAS STOPPED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",e)



def send_out_single_email_invoice(billid):

    print("printing to console")

    # print("configgggs",configuration)
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    try:
        bill = MonthlyChargeOp.fetch_specific_bill(billid)

        print("BILL IS HERE >>>>",bill)

        with mail.connect() as conn:

            if bill.ptenant:
                tenant=bill.ptenant
                current_target = "owner"
                print("OWNER INVOICE IS BEING PREPARED FOR" ,bill.ptenant.name)
            else:
                current_target = "tenant"
                tenant=bill.tenant
                print("TENANT INVOICE IS BEING PREPARED FOR" ,bill.tenant.name)

            co = bill.apartment.company

            invnum = bill.id + 13285

            house = bill.house

            #start here
            sibling_water_bill = fetch_current_billing_period_readings(bill.apartment.billing_period,bill.house.meter_readings)
            sibling_electricity_bill = fetch_current_billing_period_readings_alt(bill.apartment.billing_period,bill.house.meter_readings)

            try:
                wbill = sibling_water_bill[0]
                w_edited = "dispnone" if wbill.units == float(wbill.reading) - float(wbill.last_reading) else ""
            except:
                wbill = None
                w_edited = "dispnone"

            try:
                ebill = sibling_electricity_bill[0]
                e_edited = "dispnone" if ebill.units == float(ebill.reading) - float(ebill.last_reading) else ""
            except:
                ebill = None
                e_edited = "dispnone"


            kiotapay = CompanyOp.fetch_company_by_name("KiotaPay")
            invdate = bill.date - relativedelta(days = 0)
            inv_date = invdate.strftime("%d/%b/%y")
            invdue = invdate + relativedelta(days=5)
            inv_due = invdue.strftime("%d/%b/%y")

            print("got here so far")

        
            email_addr = tenant.email
            if email_addr:
                if wbill or ebill:
                    visibility = ""
                else:
                    visibility = "hide"

                arrears = bill.arrears
                
                if bill.paid_amount:
                    billpaid = f"{bill.paid_amount:,.2f}"
                    billbal = f"{bill.balance:,.2f}"

                else:
                    billpaid = 0.0
                    billbal = 0.0

                if arrears < 0.0:
                    arrtitle = "Previous balance"
                    bbfhighlight = "text-success"

                    arrears = f"{arrears*-1}"
                elif arrears > 0.0:
                    arrtitle = "Previous balance"
                    bbfhighlight = "text-danger"
                else:
                    arrtitle = ""
                    bbfhighlight = ""

                try:
                    if current_target == "owner":
                        if bill.house.watertarget == "owner":
                            watertarget = True
                        else:
                            watertarget = False
                    else:
                        if bill.house.watertarget == "tenant":
                            watertarget = True
                        else:
                            watertarget = False
                except:
                    watertarget = True

                try:
                    if bill.apartment.paymentdetails.nartype == 'hsenum':
                        narration = bill.house.name
                    else:
                        if bill.ptenant:
                            narration = "WN"+str(tenant.id)
                        else:
                            narration = "TNT"+str(tenant.id)
                except:
                    narration = bill.house.name

                template_vars = {
                    "bill":bill,
                    "p":bill.apartment.paymentdetails,
                    "narration":narration,
                    "servicevisibility":"",
                    "readings": wbill,
                    "w_edited": w_edited,
                    "ereadings": ebill,
                    "e_edited": e_edited,
                    "visibility":visibility,
                    "watertarget":watertarget,
                    "arrears":arrears,
                    "bbfhighlight ": bbfhighlight,
                    "arrtitle":arrtitle,
                    "billpaid":billpaid,
                    "billbal":billbal,
                    "house":house,
                    "total":f"{bill.total_bill:,.2f}",
                    "invdate":inv_date,
                    "invdue":inv_due,
                    "client":tenant,
                    "company":co,
                    "invnum":invnum,
                    "logo":logo(co)[2],
                    "slogo":logo(kiotapay)[1]
                }

                print("going to mail sender")
                mail_sender(conn,tenant,bill,template_vars,email_addr,co)
            else:
                print("Email address not found for tenant ",tenant.name,"-",bill.apartment.name)                             

    except Exception as e:
         print("WORKING HAS STOPPED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",e)


def mail_sender(conn,recepient,bill,template_vars,email_addr,co):

    templateLoader = FileSystemLoader(searchpath="app/templates")
    templateEnv = Environment(loader=templateLoader)
    TEMPLATE_FILE = "ajax_tenant_invoice_mail.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    print("CURRENTLY SENDING>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",recepient.name)
    print("WEASYPRINT???? >>>>",HTML)

    html_out = template.render(template_vars)
    filename = f"app/temp/inv_{bill.id}.pdf"
    HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/myfonts.css","app/static/eapartment-min.css","app/static/kiotapay.css"])

    ###################################################################################
    # LETS SEND EMAIL
    mail_filename = f"inv_{bill.id}"
    with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
        # print (fh)
        try:
            try:
                tname = recepient.name.split('and')[0]
            except:
                tname = recepient.name

            if bill.house.housecode.billfrequency == 3:
                billfrequency = "quarterly"
                period = f"July, August, September service charge"
            else:
                period = f"{co.name.title()}: {get_str_month(bill.month)} invoice"
                billfrequency = "monthly"

            filename_ext = f"{get_str_month(bill.month)}invoice.pdf"

            txt = Message(period, sender = mailsender, recipients = [email_addr])
            txt.body = f"Dear {tname}  \nyour {billfrequency} invoice is now available. Kindly find the attached invoice below. \n\n{co.name}"
            # txt.html = render_template('ajax_payment_receipt.html',tenant=tenant_name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno,prop=stored_apartment)
            txt.attach(filename=filename_ext,disposition="attachment",content_type="application/pdf",data=fh.read())
            # mail.send(txt)
            conn.send(txt)
            MonthlyChargeOp.update_email_status(bill,"sent")

        except Exception as e:
            print(str(e))
    #########################################################################################
    os.remove(filename)
    #########################################################################################


def send_out_single_email_crm_invoice(ptenantid):

    print("printing to console")

    # print("configgggs",configuration)
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    try:
        tenant_obj = PermanentTenantOp.fetch_tenant_by_id(ptenantid)
        with mail.connect() as conn:
            if tenant_obj:
                schtotal = 0.0
                schpaid = 0.0

                bills = tenant_obj.schedules

                formatted_bills = []

                for bill in bills:
                    schtotal += bill.schedule_amount
                    schpaid += bill.paid
                    formatted_bills.append(PaymentScheduleOp.view_detail(bill))

                prop = tenant_obj.apartment
                if tenant_obj.email:
                    email_addr = tenant_obj.email

                    template_vars = {
                        "statementdate":datetime.datetime.now().strftime("%d %B %Y"),
                        "bills":formatted_bills,
                        "paging":page(formatted_bills),
                        "schtotal":f"{schtotal:,.1f}",
                        "schpaid":f"{schpaid:,.1f}",
                        "prop_obj":prop,
                        "prop ": tenant_obj.apartment.name,
                        "tenant_obj":tenant_obj,
                        "tenant_name":tenant_obj.name,
                        "name":prop.name,
                        "logopath":logo(prop.company)[0],
                        "mobilelogopath":logo(prop.company)[1],
                        "fulllogopath":logo(prop.company)[2],
                        "letterhead":logo(prop.company)[3],
                        "co":prop.company
                    }

                    print("going to mail sender")
                    crm_mail_sender(conn,tenant_obj,template_vars,email_addr,tenant_obj.apartment)
                else:
                    print("Email address not found for tenant ",tenant_obj.name,"-",tenant_obj.apartment.name)  
            else:
                print("PTenant not founnd")  
                                           

    except Exception as e:
         print("WORKING HAS STOPPED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",e)


def crm_mail_sender(conn,recepient,template_vars,email_addr,co):

    templateLoader = FileSystemLoader(searchpath="app/templates")
    templateEnv = Environment(loader=templateLoader)
    TEMPLATE_FILE = "ajax_tenant_crm_invoice.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    print("CURRENTLY SENDING>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",recepient.name)
    print("WEASYPRINT???? >>>>",HTML)

    html_out = template.render(template_vars)
    filename = f"app/temp/statement_{recepient.id}.pdf"
    HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/myfonts.css","app/static/eapartment-min.css","app/static/kiotapay.css"])

    ###################################################################################
    # LETS SEND EMAIL
    mail_filename = f"statement_{recepient.id}"
    with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
        # print (fh)
        try:
            try:
                tname = recepient.name.split('and')[0]
            except:
                tname = recepient.name

            filename_ext = f"{recepient.house.name}_statement.pdf"

            sal = f"{recepient.apartment.company.name}: Payment Reminder"

            txt = Message(sal, sender = mailsender, recipients = [email_addr])
            txt.body = f"Dear {tname}  \nKindly find the attached statement of account below. \n\n{co.name}"
            # txt.html = render_template('ajax_payment_receipt.html',tenant=tenant_name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno,prop=stored_apartment)
            txt.attach(filename=filename_ext,disposition="attachment",content_type="application/pdf",data=fh.read())
            # mail.send(txt)
            conn.send(txt)
            # MonthlyChargeOp.update_email_status(bill,"sent")

        except Exception as e:
            print(str(e))
    #########################################################################################
    os.remove(filename)
    #########################################################################################




def discard_bills(props):
    # props > array of apartment ids
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    for prop in props:
        prop_obj = ApartmentOp.fetch_apartment_by_id(prop)

        all_bills = prop_obj.monthlybills

        bills = fetch_current_billing_period_bills(prop_obj.billing_period,all_bills)

        for bill in bills:

            original_amount = bill.total_bill - bill.arrears

            all_charges = bill.house.charges

            for charge in all_charges:
                # if charge.date.month == bill.apartment.billing_period.month and charge.date.year == bill.apartment.billing_period.year and not charge.reading_id:
                if charge.date.month == bill.apartment.billing_period.month and charge.date.year == bill.apartment.billing_period.year:
                    ChargeOp.delete(charge)

            if bill.apartment.billing_period.month == bill.month:
            
                tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                print("ORIGINAL AMOUNT:",original_amount)
                if tenant_obj:
                    running_bal = tenant_obj.balance
                    print("CURRENT TENANT BALANCE:",running_bal)
                    running_bal = running_bal - original_amount
                    print("FINAL:",running_bal)

                    TenantOp.update_balance(tenant_obj,running_bal)

                MonthlyChargeOp.delete(bill)

def send_out_sms_invoices(prop,houses,billid,charge,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
    update = False

    if prop_obj and charge == "all":

        billing_period = get_billing_period(prop_obj)

        target_bills = []

        if billid:
            identifier = get_identifier(billid)
            targetbill = MonthlyChargeOp.fetch_specific_bill(identifier)
            target_bills.append(targetbill)

        elif houses and houses != "ALL":
            # if  override:
            """Specified houses for all charges invoices"""
            update = True
            house_list = generate_array(houses,prop_obj)

            for house in house_list:
                bill = fetch_current_billing_period_bills(billing_period,house.monthlybills)
                if bill:
                    target_bills.append(bill[0])
                  

        else:
            if houses:
                """Entire houses in a property (ALL)"""
                update = True
                house_list = houseauto(prop_obj.id)
                for house in house_list:
                    bill = fetch_current_billing_period_bills(billing_period,house.monthlybills)
                    if bill:
                        target_bills.append(bill[0])
            else:
                """Normal message sending, doesnt allow double sending"""
                house_list = houseauto(prop_obj.id)
                for house in house_list:
                    bill = fetch_current_billing_period_bills(billing_period,house.monthlybills)
                    if bill:
                        if bill[0].sms_invoice != "sent" and bill[0].sms_invoice != "Success" and bill[0].sms_invoice != "success-alt" and not bill[0].paid_amount:
                            target_bills.append(bill[0])                                                                                                                                        

        for bill in target_bills:

            sibling_water_bill = fetch_current_billing_period_readings(prop_obj.billing_period,bill.house.meter_readings)
            sibling_electricity_bill = fetch_current_billing_period_readings_alt(bill.apartment.billing_period,bill.house.meter_readings)


            try:
                wbill = sibling_water_bill[0]
            except:
                wbill = None

            try:
                ebill = sibling_electricity_bill[0]
            except:
                ebill = None

            if wbill:
                amount = 0.0
                standing_charge = 0.0

                if wbill.charged:
                    charge_obj = ChargeOp.fetch_charge_by_reading_id(wbill.id)
                    amount = charge_obj.amount

                    standing_charge = bill.house.housecode.watercharge
                    if standing_charge:
                        amount += standing_charge

                smslastreading = (f"{wbill.last_reading} ")
                smscurrentreading = (f"{wbill.reading} ")
                smsunits = (f"{wbill.units} ")
                smsstd = f"Standing charge: Kes {standing_charge}" if bill.house.housecode.watercharge else ""
                smsbill = (f"Kes {amount:,.2f} ")

                wmessage = f"\n\nWater, \nLR: {smslastreading} \nCR: {smscurrentreading} \nUnits: {smsunits} \n{smsstd} \nBill: {smsbill}"
            else:
                wmessage = ""
                smsbill = "Kes 0.0"

            if ebill:
                eamount = 0.0

                if ebill.charged:
                    charge_obj = ChargeOp.fetch_charge_by_reading_id(ebill.id)
                    eamount = charge_obj.amount

                smselastreading = (f"{ebill.last_reading} ")
                smsecurrentreading = (f"{ebill.reading} ")
                smseunits = (f"{ebill.units} ")
                smsebill = (f"Kes {eamount:,.2f} ")
                emessage = f"\n\nElectricity, \nLR: {smselastreading} \nCR: {smsecurrentreading} \nUnits: {smseunits} \nBill: {smsebill}"
            else:
                emessage = ""
                smsebill = "Kes 0.0"

            tenant2 = None

            if bill.ptenant:
                tenant = bill.ptenant
                print("SENDING OWNER INVOICE")

                if bill.tenant:
                    print("SENDING OWNER AND NORMAL TENANT INVOICE")
                    tenant2 = bill.tenant
            else:
                print("SENDING NORMAL TENANT INVOICE")
                tenant = None
                tenant2 = bill.tenant
                
            arrears = bill.arrears
            
            calculated_total = 0.0
            if bill.paid_amount and arrears > 0:
                if arrears <= bill.paid_amount:
                    calculated_total = bill.total_bill - arrears
                    arrears = 0.0
                else:
                    arrears = bill.arrears - bill.paid_amount
                    calculated_total = bill.total_bill - bill.paid_amount


            # if bill.house.housecode.vatrate:
            #     smsrent = f"\n\nRent:{bill.house.housecode.rentrate:,}," if bill.rent else ""
            # else:
            #     smsrent = f"\n\nRent:{bill.rent:,}," if bill.rent else ""

            # smsvat = f"\nVAT(16%) on rent:{bill.house.housecode.rentrate * 0.16}" if bill.house.housecode.vatrate else ""




            if bill.rent:
                if bill.house.housecode.vatrate:
                    if bill.house.housecode.discount:
                        smsrent = f"\n\nRent{ (bill.house.housecode.rentrate - bill.house.housecode.discount) - ((bill.house.housecode.rentrate - bill.house.housecode.discount) * bill.house.housecode.vatrate * 0.01 / ((bill.house.housecode.vatrate * 0.01) + 1.0)):,.0f}"
                    else:
                        smsrent = f"\n\nRent{ bill.house.housecode.rentrate - (bill.house.housecode.rentrate * bill.house.housecode.vatrate * 0.01 / ((bill.house.housecode.vatrate * 0.01) + 1.0)):,.0f}"
                else:
                    smsrent = f"\n\nRent:{bill.rent:,},"
            else:
                smsrent = ""
             
             
            if bill.house.housecode.vatrate:
                if bill.house.housecode.discount:
                    smsvat = f"\n16% VAT on rent: {  (bill.house.housecode.rentrate - bill.house.housecode.discount) * bill.house.housecode.vatrate * 0.01 / ((bill.house.housecode.vatrate * 0.01) + 1.0):,.0f}"
                else:
                    smsvat = f"\n16% VAT on rent: {  (bill.house.housecode.rentrate * bill.house.housecode.vatrate * 0.01 / ((bill.house.housecode.vatrate * 0.01) + 1.0)):,.0f}"
            else:
                smsvat = ""
             

            if bill.house.housecode.discount:
                smsdisc = f"\nDiscount: -{ bill.house.housecode.discount}"
            else:
                smsdisc = ""
             

            if bill.house.housecode.vatrate or bill.house.housecode.discount:
                smsrentsub = f"\nRent subtotal:  {bill.rent}"
            else:
                smsrentsub = ""

             
            if wmessage:
                smswater = wmessage
            else:
                smswater = f"\nCurrent bill:{bill.water}," if bill.water else ""

            if emessage:
                smselec = emessage
            else:
                smselec = f"\nCurrent electricity bill:{bill.electricity}," if bill.electricity else ""


            try:
                if bill.apartment.paymentdetails.nartype == 'hsenum':
                    narration = bill.house.name
                elif bill.apartment.paymentdetails.nartype == 'tntnum':
                    if tenant:
                        narration = "WN"+str(tenant.id)
                    else:
                        narration = "TNT"+str(tenant2.id)

                else: narration = ""
            except:
                narration = ""

            p = bill.apartment.paymentdetails

            if bill.house.payment_bankacc:
                bankdetails = f'\n\nBank: {bill.house.payment_bank} \nAcc: {bill.house.payment_bankacc}'

            elif p:
                if p.paytype == "mpesapay":
                    bankdetails = f'\n\nPaybill: {p.mpesapaybill} \nAcc: {narration}'
                elif p.bankpaybill:
                    if narration:
                        narration = "#"+narration
                    bankdetails = f'\n\nPaybill: {p.bankpaybill} \nAcc: {p.bankaccountnumber}{narration}'
                else:
                    bankdetails = f'\n\nBank: {p.bankname}, \nName: {p.bankaccountname} \nAcc: {p.bankaccountnumber}'
            else:
                bankdetails = ""


            smsgarb = f"\nGarbage:{bill.garbage}," if bill.garbage else ""
            smssec = f"\nSecurity:{bill.security}," if bill.security else ""
            smssev = f"\nService charge:{bill.maintenance}," if bill.maintenance else ""
            smsdep = f"\nDeposit:{bill.deposit}" if bill.deposit else ""
            smsarrears = f"\nPrevious balance:{arrears}" if arrears else ""
            smsfine = f"\nPenalty:{bill.penalty}" if bill.penalty else ""
            smstotal = (f"{bill.total_bill:,.1f}") if not calculated_total else (f"{calculated_total:,.1f}")
            paidd = f"\nPaid:{bill.paid_amount}" if bill.paid_amount else ""
            paidbal = f"{paidd} \nBal:{bill.balance}" if bill.paid_amount else ""
            bankdetails = bankdetails

            current_user = UserOp.fetch_user_by_id(user_id)

            co = current_user.company
            if co.name == "LaCasa":
                str_co = f"\n\n ~ {bill.apartment.name} (Tel: 0735267087)"
            else:
                str_co = f"\n\n ~ {bill.apartment.name} ({str(co)})"

            raw_rem_sms =co.remainingsms

            own_shortcode = False

            if co.name == "Lesama Ltd" or co.name == "Merit Properties Limited" or prop_obj.name == "Greatwall Gardens 2":
                own_shortcode = True

            if own_shortcode:
                raw_rem_sms = 5000

            if tenant:
                print("OWNER SENDING STARTED......")

                if tenant.sms:
                    if raw_rem_sms > 0 or own_shortcode:

                        tele = tenant.phone
                        phonenum = sms_phone_number_formatter(tele)

                        if bill.house.housecode.billfrequency == 3:
                            str_month = f"July, August, September"
                        else:
                            str_month = get_str_month(billing_period.month) if smsrent else get_str_month(billing_period.month-1) # URGENT TODO : TAKE CARE OF JANUARY
                            str_month = get_str_month(billing_period.month) if smssev else get_str_month(billing_period.month-1) # URGENT TODO : TAKE CARE OF JANUARY
                        tname = fname_extracter(tenant.name)

                        if bill.house.watertarget:
                            if bill.house.watertarget == "owner":
                                waterbill = "water consumption"
                            else:
                                smswater = ""
                                waterbill = ""
                        else:
                            waterbill = ""

                        if bill.house.servicetarget:
                            if bill.house.servicetarget == "owner":
                                servicecharge = "service charge"
                            else:
                                servicecharge = ""
                        else:
                            servicecharge = ""
                            

                        try:
                            recipient = [phonenum]
                            if update:
                                if arrears < 0.0:
                                    bbf = -1 * arrears
                                    sms_bbf = (f"{bbf:,.1f}")
                                    message = f"Dear {tname},({bill.house.name}), your {str_month} {servicecharge}{waterbill} bill is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} \nPrevious credit: {sms_bbf} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}."
                                else:
                                    message = f"Dear {tname},({bill.house.name}), your {str_month} {servicecharge}{waterbill} bill is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} {smsarrears} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}." 


                            else:

                                if arrears < 0.0:
                                    bbf = -1 * arrears
                                    sms_bbf = (f"{bbf:,.1f}")
                                    message = f"Dear {tname},({bill.house.name}), your {str_month} {servicecharge}{waterbill} bill is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} \nPrevious credit: {sms_bbf} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}."
                                else:
                                    message = f"Dear {tname},({bill.house.name}), your {str_month} {servicecharge}{waterbill} bill is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} {smsarrears} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}."


                            char_count = len(message)
                            if char_count <= 160:
                                cost = 1
                            elif char_count <= 320:
                                cost = 2
                            else:
                                cost = 3

                            sms_obj = SentMessagesOp(message,char_count,cost,None,tenant.id,prop_obj.id,co.id)
                            sms_obj.save()

                            if co.sms_provider == "Advanta":
                            # allowed = True
                            # if allowed:
                                smsid = sms_sender(co.name,message,phonenum)
                                if smsid:
                                    MonthlyChargeOp.update_smsid(bill,smsid)
                                MonthlyChargeOp.update_sms_status(bill,"sent")


                            else:
                                response = sms.send(message, recipient, sender)
                                print(response)
                                resp = response["SMSMessageData"]["Recipients"][0]

                                code = resp["statusCode"]
                                smsid = resp["messageId"]
                                MonthlyChargeOp.update_smsid(bill,smsid)

                                if code == 101: # SMS WAS SENT
                                    MonthlyChargeOp.update_sms_status(bill,"sent")
                                    raw_cost = resp["cost"]
                                    rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                                    CompanyOp.set_rem_quota(co,rem_sms)
                                    print("EVERYTHING IS SMOOTH")
                                    
                                elif code == 403:
                                    print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                    MonthlyChargeOp.update_sms_status(bill,"fail")
                                    
                                elif code == 405:
                                    MonthlyChargeOp.update_sms_status(bill,"waiting")
                                    # response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
                                    print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                    
                                elif code == 406:
                                    MonthlyChargeOp.update_sms_status(bill,"blocked")
                                    raw_cost = resp["cost"]
                                    rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                                    CompanyOp.set_rem_quota(co,rem_sms)
                                else:
                                    print("ALAAAAAAAA",code)

                        except Exception as e:
                            print(f"Houston, we have a problem {e}")
                            MonthlyChargeOp.update_sms_status(bill,"fail")
                    else:
                        txt = f"{co} has depleted sms"
                        # response = sms.send(txt, ["+254716674695"],"KIOTAPAY")
                        send_internal_email_notifications(co.name,txt)
                        print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN CLIENT HAS DEPLETED SMS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",txt)
                else:
                    MonthlyChargeOp.update_sms_status(bill,"off")
                    print("Tenant does not accept messages")

            #reset water
            if wmessage:
                smswater = wmessage
            else:
                smswater = f"\nWater:{bill.water}," if bill.water else ""

            #reset arrears
            arrears = bill.arrears

            if tenant2:
                print("TENANT SENDING STARTED......")
                if tenant2.sms:

                    if raw_rem_sms > 0 or own_shortcode:

                        tele = tenant2.phone
                        phonenum = sms_phone_number_formatter(tele)

                        if bill.house.housecode.billfrequency == 3:
                            str_month = f"July, August, September"
                        else:
                            str_month = get_str_month(billing_period.month) if smssev else get_str_month(billing_period.month-1) # URGENT TODO : TAKE CARE OF JANUARY
                            str_month = get_str_month(billing_period.month) if smsrent else get_str_month(billing_period.month-1) # URGENT TODO : TAKE CARE OF JANUARY

                        tname = fname_extracter(tenant2.name)


                        if bill.house.watertarget:
                            if bill.house.watertarget == "tenant":
                                waterbill = ""
                            else:
                                smswater = ""
                                waterbill = ""
                        else:
                            waterbill = ""

                        if bill.house.servicetarget:
                            if bill.house.servicetarget == "tenant":
                                servicecharge = "service charge"
                            else:
                                servicecharge = ""
                        else:
                            servicecharge = ""
                            

                        try:
                            recipient = [phonenum]
                            if update:
                                if arrears < 0.0:
                                    bbf = -1 * arrears
                                    sms_bbf = (f"{bbf:,.1f}")
                                    message = f"Dear {tname} ({bill.house.name}), your {str_month} {servicecharge}{waterbill} updated invoice (VAT inclusive) is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} \nPrevious credit: {sms_bbf} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}."
                                else:
                                    message = f"Dear {tname} ({bill.house.name}), your {str_month} {servicecharge}{waterbill} updated invoice (VAT inclusive) is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} {smsarrears} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}." 
                                #     message = f"Dear {tname}, the revised {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smselec} {smsdep} \nPaid: {sms_bbf} \n\nTotal due: {smstotal} {bankdetails} {str_co}."
                                # else:
                                #     message = f"Dear {tname}, the revised {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smselec} {smsdep} {smsarrears} \n\nTotal due: {smstotal} {bankdetails} {str_co}." 

                            else:

                                if arrears < 0.0:
                                    bbf = -1 * arrears
                                    sms_bbf = (f"{bbf:,.1f}")
                                    message = f"Dear {tname} ({bill.house.name}), your {str_month} {servicecharge}{waterbill} bill is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} \nPrevious credit: {sms_bbf} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}."
                                else:
                                    message = f"Dear {tname} ({bill.house.name}), your {str_month} {servicecharge}{waterbill} bill is as follows; {smsrent} {smsvat} {smsdisc} {smsrentsub} {smswater} \n {smselec} \n {smsgarb} {smssec} {smssev} {smsdep} {smsfine} {smsarrears} \n\nTotal due: {smstotal} {paidbal} {bankdetails} {str_co}."
                            # if prop_obj.company.name == "KIGAKA ENTERPRISES":
                            #     continue

                            char_count = len(message)
                            if char_count <= 160:
                                cost = 1
                            elif char_count <= 320:
                                cost = 2
                            else:
                                cost = 3


                            sms_obj = SentMessagesOp(message,char_count,cost,tenant2.id,None,prop_obj.id,co.id)
                            sms_obj.save()

                            if co.sms_provider == "Advanta":
                            # if co.name.lower() == "rhino park place" or co.name.lower() == "test agencies":
                            #     allowed = False
                            # else:
                            #     allowed = True

                            # if allowed:
                                smsid = sms_sender(co.name,message,phonenum)
                                if smsid:
                                    MonthlyChargeOp.update_smsid(bill,smsid)
                                MonthlyChargeOp.update_sms_status(bill,"sent")

                            else:
                                response = sms.send(message, recipient, sender)
                                print(response)
                                resp = response["SMSMessageData"]["Recipients"][0]

                                code = resp["statusCode"]
                                smsid = resp["messageId"]
                                MonthlyChargeOp.update_smsid(bill,smsid)

                                if code == 101: # SMS WAS SENT
                                    MonthlyChargeOp.update_sms_status(bill,"sent")
                                    raw_cost = resp["cost"]
                                    rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                                    CompanyOp.set_rem_quota(co,rem_sms)
                                    print("EVERYTHING IS SMOOTH")
                                    
                                elif code == 403:
                                    print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                    MonthlyChargeOp.update_sms_status(bill,"fail")
                                    
                                elif code == 405:
                                    MonthlyChargeOp.update_sms_status(bill,"waiting")
                                    # response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
                                    print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                    
                                elif code == 406:
                                    MonthlyChargeOp.update_sms_status(bill,"blocked")
                                    raw_cost = resp["cost"]
                                    rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                                    CompanyOp.set_rem_quota(co,rem_sms)
                                else:
                                    print("ALAAAAAAAA",code)

                        except Exception as e:
                            print(f"Houston, we have a problem {e}")
                            MonthlyChargeOp.update_sms_status(bill,"fail")
                    else:
                        txt = f"{co} has depleted sms"
                        # response = sms.send(txt, ["+254716674695"],"KIOTAPAY")
                        send_internal_email_notifications(co.name,txt)
                        print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN CLIENT HAS DEPLETED SMS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",txt)
                else:
                    MonthlyChargeOp.update_sms_status(bill,"off")
                    print("Tenant does not accept messages")


    elif prop_obj and charge == "water":

        target_readings = []

        if houses and houses != "ALL":
            """Specified houses for all charges invoices frequent use"""
            update = True
            house_list = generate_array(houses,prop_obj)

            for house in house_list:
                bill  = fetch_current_billing_period_readings(prop_obj.billing_period,house.meter_readings)
                if bill:
                    target_readings.append(bill[0])          

        else:
            if houses:
                """Entire houses in a property for update purposes- rarely used"""
                update = True
                house_list = houseauto(prop_obj.id)
                for house in house_list:
                    bill = fetch_current_billing_period_readings(prop_obj.billing_period,house.meter_readings)
                    if bill:
                        target_readings.append(bill[0])
            else:
                """Normal message sending, doesnt allow double sending"""
                house_list = houseauto(prop_obj.id)
                for house in house_list:
                    bill = fetch_current_billing_period_readings(prop_obj.billing_period,house.meter_readings)
                    for b in bill:
                        if b.sms_invoice != "sent" and b.sms_invoice != "Success" and b.sms_invoice != "success-alt":
                            target_readings.append(b)

        for bill in target_readings:
            house = bill.house
            tenant = check_occupancy(house)[1]
            amount = 0.0
            standing_charge = 0.0

            if bill.charged:
                charge_obj = ChargeOp.fetch_charge_by_reading_id(bill.id)
                amount = charge_obj.amount

                standing_charge = house.housecode.watercharge
                if standing_charge:
                    amount += standing_charge

            smslastreading = (f"{bill.last_reading} ")
            smscurrentreading = (f"{bill.reading} ")
            smsunits = (f"{bill.units} ")
            smsstd = f"Standing charge: Kes {standing_charge}" if house.housecode.watercharge else ""
            smsbill = (f"Kes {amount:,} ")

            current_user = UserOp.fetch_user_by_id(user_id)

            co = current_user.company
            str_co = str(co)
            raw_rem_sms =co.remainingsms

            if not isinstance(tenant, str): 
                if tenant.sms:
                    if raw_rem_sms > 0 and amount > 0.0:
                        #Send the SMS
                        tele = tenant.phone
                        phonenum = sms_phone_number_formatter(tele)
                        str_month = get_str_month(prop_obj.billing_period.month)
                        try:
                            recipient = [phonenum]

                            if update:
                                message = f"Dear {tenant.name}, \nYour updated {str_month} water bill reading is as follows: \n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \n{smsstd} \nBill: {smsbill} \n\n~{str_co}"
                            else:
                                message = f"Dear {tenant.name}, \nYour {str_month} water bill reading is as follows: \n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \n{smsstd} \nBill: {smsbill} \n\n~{str_co}"

                            response = sms.send(message, recipient, sender)
                            print(response)
                            resp = response["SMSMessageData"]["Recipients"][0]

                            code = resp["statusCode"]
                            smsid = resp["messageId"]
                            MeterReadingOp.update_smsid(bill,smsid)

                            if code == 101: # SMS WAS SENT
                                MeterReadingOp.update_sms_status(bill,"sent")
                                raw_cost = resp["cost"]
                                rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                                CompanyOp.set_rem_quota(co,rem_sms)
                                print("EVERYTHING IS SMOOTH")
                                
                            elif code == 403:
                                print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                MeterReadingOp.update_sms_status(bill,"fail")
                                
                            elif code == 405:
                                MeterReadingOp.update_sms_status(bill,"waiting")
                                # response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
                                print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                
                            elif code == 406:
                                MeterReadingOp.update_sms_status(bill,"blocked")
                                raw_cost = resp["cost"]
                                rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                                CompanyOp.set_rem_quota(co,rem_sms)
                            else:
                                print("ALAAAAAAAA",code)
                        except Exception as e:
                            MeterReadingOp.update_sms_status(bill,"fail")
                            print(f"Houston, we have a problem {bill.last_reading} {bill.id} {e}")
                    else:
                        print("sms quota depleted or bad bills XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                else:
                    MeterReadingOp.update_sms_status(bill,"off")
                    print("Tenant does not accept messages")
            else:
                MeterReadingOp.update_sms_status(bill,"off")
                print(">>>>>",house, "is vacant")

    elif prop_obj and charge == "electricity":
    
        target_readings = []

        if houses and houses != "ALL":
            """Specified houses for all charges invoices frequent use"""
            update = True
            house_list = generate_array(houses,prop_obj)

            for house in house_list:
                bill  = fetch_current_billing_period_readings_alt(prop_obj.billing_period,house.meter_readings)
                if bill:
                    target_readings.append(bill[0])          

        else:
            if houses:
                """Entire houses in a property for update purposes- rarely used"""
                update = True
                house_list = houseauto(prop_obj.id)
                for house in house_list:
                    bill = fetch_current_billing_period_readings_alt(prop_obj.billing_period,house.meter_readings)
                    if bill:
                        target_readings.append(bill[0])
            else:
                """Normal message sending, doesnt allow double sending"""
                house_list = houseauto(prop_obj.id)
                for house in house_list:
                    bill = fetch_current_billing_period_readings_alt(prop_obj.billing_period,house.meter_readings)
                    for b in bill:
                        if b.sms_invoice != "sent":
                            target_readings.append(b)

        for bill in target_readings:
            house = bill.house
            tenant = check_occupancy(house)[1]
            amount = 0.0

            if bill.charged:
                charge_obj = ChargeOp.fetch_charge_by_reading_id(bill.id)
                amount = charge_obj.amount

            smslastreading = (f"{bill.last_reading} ")
            smscurrentreading = (f"{bill.reading} ")
            smsunits = (f"{bill.units} ")
            smsbill = (f"Kes {amount:,} ")

            current_user = UserOp.fetch_user_by_id(user_id)

            co = current_user.company
            str_co = str(co)
            rem_sms =co.remainingsms
            if not isinstance(tenant, str): 
                if tenant.sms:
                    if rem_sms > 0 and amount > 0.0:
                        #Send the SMS
                        MeterReadingOp.update_sms_status(bill,"sent")
                        print("sending water bill sms",">>>>>>>>>>>>>>>>>>>>",prop_obj.name)
                        tele = tenant.phone
                        phonenum = sms_phone_number_formatter(tele)
                        str_month = get_str_month(prop_obj.billing_period.month)
                        try:
                            recipient = [phonenum]

                            if update:
                                message = f"Dear {tenant.name}, \nYour updated {str_month} electricity bill reading is as follows: \n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \nBill: {smsbill} \n\n~{str_co}"
                            else:
                                message = f"Dear {tenant.name}, \nYour {str_month} electricity bill reading is as follows: \n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \nBill: {smsbill} \n\n~{str_co}"
                                
                            response = sms.send(message, recipient, sender)
                            # response = sms.send(message, ["+254716674695","+254717121612"], "KIOTAPAY")
                            print(response)
                            rem_sms -= 1
                            CompanyOp.set_rem_quota(co,rem_sms)
                        except Exception as e:
                            MeterReadingOp.update_sms_status(bill,"?")
                            print(f"Houston, we have a problem {e}")
                    else:
                        print("sms quota depleted or bad bills XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                else:
                    print("Tenant does not accept messages")
            else:
                print(">>>>>",house, "is vacant")
    else:
        print("Apartment was not selected")


def send_activation_mail(email,name,url):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    print("goooiiing")

    txt = Message('Welcome! Please activate your account.', sender = mailsender, recipients = [email])
    txt.html = render_template('activation.html',name=name,target_url=url)
    mail.send(txt)

def send_demo_mail(email,name,url):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    txt = Message('Welcome! Demo account.', sender = mailsender, recipients = [email])
    txt.html = render_template('demo.html',name=name,target_url=url)
    mail.send(txt)

def auto_send_mail_receipt(payment_id,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    payment_obj = PaymentOp.fetch_payment_by_id(payment_id)
    current_user = UserOp.fetch_user_by_id(user_id)

    tenant = payment_obj.tenant
    company = current_user.company
    prop = ApartmentOp.fetch_apartment_by_id(payment_obj.apartment_id)

    p = inflect.engine()
    int_amount = int(payment_obj.amount)
    str_amount = p.number_to_words(int_amount)
    stramount = str_amount.capitalize()

    paydate = payment_obj.pay_date if payment_obj.pay_date else payment_obj.date
    payperiod = payment_obj.pay_period if payment_obj.pay_period else payment_obj.date
    ###################################################################################

    templateLoader = FileSystemLoader(searchpath="app/templates")
    templateEnv = Environment(loader=templateLoader)
    TEMPLATE_FILE = "ajax_pay_mail.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    # pay_time = datetime.datetime.now()
    # paydate = pay_time.strftime("%B %d, %Y")
    # paytime = pay_time.strftime("%H:%M:%S")
    # pdftime = paydate + " " + paytime

    if payment_obj.charged_amount < 1:
        bill = 0.0
    else:
        bill = f"{payment_obj.charged_amount:,.0f}"

    if payment_obj.balance > -1:
        baltitle = "Balance"
        outline = "text-danger"
        bal = f"Kes {payment_obj.balance:,.0f}"
    else:
        baltitle = "Advance"
        outline = "text-success"
        bal = f"Kes {payment_obj.balance*-1:,.0f}"

    if payment_obj.voided:
        disp = ""
    else:
        disp = "dispnone"

    mail_logo = "../" + logo(current_user.company)[0]
    
    template_vars = {
        "tenant":tenant.name,
        "voided" : disp,
        "house":payment_obj.house.name,
        "amount":f'Kes: {payment_obj.amount:,.0f}',
        "str_amount":stramount,
        "str_month":get_str_month(payperiod.month),
        "paydate":paydate.strftime("%d/%b/%y"),
        "paytime":paydate.strftime("%X"),
        "bill":bill,
        "baltitle":baltitle,
        "outline":outline,
        "balance":bal,
        "chargetype":payment_obj.payment_name,
        "receiptno":payment_obj.id,
        "refnum":payment_obj.ref_number,
        "paymode":payment_obj.paymode,
        "logopath":mail_logo,
        "company":company,
        "user":current_user.company if current_user.company == "MojaMbili Homes" else fname_extracter(current_user.name),
        "prop":prop
    }
    html_out = template.render(template_vars)
    filename = f"app/temp/report_{tenant.id}.pdf"
    HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/eapartment-min.css","app/static/kiotapay.css","app/static/receipt.css"])
    ###################################################################################
    # LETS SEND EMAIL
    mail_filename = f"report_{tenant.id}"
    with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
        # print (fh)
        try:
            email_addr = tenant.email
            if email_addr:
                txt = Message('Payment acknowledgement receipt', sender = mailsender, recipients = [email_addr])
                txt.body = "Dear Tenant;" "\nThis is acknowledging that we have received payment of " + stramount +" shillings only."+ "\nIn case of any query, feel free to contact us. \nThank you. \nKindly find the attached receipt. \n\nSender - " + company.name + ","+ "\nProperty managers."
                # txt.html = render_template('ajax_payment_receipt.html',tenant=tenant_name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno,prop=stored_apartment)
                txt.attach(filename="payment_receipt.pdf",disposition="attachment",content_type="application/pdf",data=fh.read())
                mail.send(txt)
                PaymentOp.update_email_status(payment_obj,"Sent")
            else:
                print("Email address not found for tenant ",tenant.name,"-",prop)
        except Exception as e:
            print(str(e))
    #########################################################################################

    os.remove(filename)

    #########################################################################################

def auto_send_sms_receipt(payment_id,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    payment_obj = PaymentOp.fetch_payment_by_id(payment_id)
    current_user = UserOp.fetch_user_by_id(user_id)

    tenant = payment_obj.tenant
    company = current_user.company
    prop = ApartmentOp.fetch_apartment_by_id(payment_obj.apartment_id)

    p = inflect.engine()
    int_amount = int(payment_obj.amount)
    str_amount = p.number_to_words(int_amount)
    stramount = str_amount.capitalize()

    paydate = payment_obj.pay_date if payment_obj.pay_date else payment_obj.date
    payperiod = payment_obj.pay_period if payment_obj.pay_period else payment_obj.date
    ###################################################################################

    templateLoader = FileSystemLoader(searchpath="app/templates")
    templateEnv = Environment(loader=templateLoader)
    TEMPLATE_FILE = "ajax_pay_mail.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    # pay_time = datetime.datetime.now()
    # paydate = pay_time.strftime("%B %d, %Y")
    # paytime = pay_time.strftime("%H:%M:%S")
    # pdftime = paydate + " " + paytime

    if payment_obj.charged_amount < 1:
        bill = 0.0
    else:
        bill = f"{payment_obj.charged_amount:,.0f}"

    running_bal = f"Balance: Kes {payment_obj.balance:,.0f}" if payment_obj.balance > -1 else f"Advance: Kes {payment_obj.balance*-1:,.0f}"

    if payment_obj.voided:
        disp = ""
    else:
        disp = "dispnone"

    mail_logo = "../" + logo(current_user.company)[0]
    
    template_vars = {
        "tenant":tenant.name,
        "voided" : disp,
        "house":payment_obj.house.name,
        "amount":f'Kes: {payment_obj.amount:,.0f}',
        "str_amount":stramount,
        "str_month":get_str_month(payperiod.month),
        "paydate":paydate.strftime("%d/%b/%y"),
        "paytime":paydate.strftime("%X"),
        "bill":bill,
        "balance":running_bal,
        "chargetype":payment_obj.payment_name,
        "receiptno":payment_obj.id,
        "refnum":payment_obj.ref_number,
        "paymode":payment_obj.paymode,
        "logopath":mail_logo,
        "company":company,
        "user":current_user.company if current_user.company == "MojaMbili Homes" else fname_extracter(current_user.name),
        "prop":prop
    }

    html_out = template.render(template_vars)
    filename = f"app/temp/receipt_{payment_obj.rand_id}.pdf"
    HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/eapartment-min.css","app/static/kiotapay.css","app/static/receipt.css"])

    ###################################################################################
    



    # # LETS SEND EMAIL
    # mail_filename = f"report_{tenant.id}"

    # with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
    #     # print (fh)
    #     try:
    #         email_addr = tenant.email
    #         if email_addr:
    #             txt = Message('Payment acknowledgement receipt', sender = mailsender, recipients = [email_addr])
    #             txt.body = "Dear Tenant;" "\nThis is acknowledging that we have received payment of " + stramount +" shillings only."+ "\nIn case of any query, feel free to contact us. \nThank you. \nKIndly find the attached receipt. \n\nSender - " + company + ","+ "\nProperty managers."
    #             # txt.html = render_template('ajax_payment_receipt.html',tenant=tenant_name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno,prop=stored_apartment)
    #             txt.attach(filename="payment_receipt.pdf",disposition="attachment",content_type="application/pdf",data=fh.read())
    #             mail.send(txt)
    #             PaymentOp.update_email_status(payment_obj,"Sent")
    #         else:
    #             print("Email address not found for tenant ",tenant.name,"-",prop)
    #     except Exception as e:
    #         print(str(e))
    #########################################################################################

    # os.remove(filename)

    ########################################################################################


import string
import random
def random_generator(size=10, chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))


def upload_handler(file,current_user):

    filename = secure_filename(file.filename)
    uniquefilename = f"{current_user.username}_{filename}"

    file.save(os.path.join("app/temp/", uniquefilename))

    try:
        loc = "app/temp/" + uniquefilename
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        # sheet.cell_value(0, 0)

        # Extracting number of rows
        num_of_rows =sheet.nrows
        print("ROWS: ",num_of_rows-1)
        rows = [*range(1, num_of_rows, 1)]

        os.remove(loc)
    except Exception as e:
        print("Error reading file ",e)
        rows=[1]
        sheet=None
        os.remove(loc)

    return [rows,sheet]

def read_deposits_excel(dict_array,apartment_id,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

    for item in dict_array:

        unit = item["unit"]
        rentdep = item["rentdep"]
        waterdep = item["waterdep"]
        elecdep = item["elecdep"]
        otherdep = item["otherdep"]
        datepaid = item["datepaid"]
        rstatus = item["status"]

        print("RSTATUS",rstatus)

        status = "unrefunded" if rstatus == "" else "refunded"

        print("STATUS",status)

        try:
            housename = str(int(unit) if unit else "" )
        except:
            housename = unit if unit else ""

        if housename == "":
            print("EMPTY CELL")

        try:
            house_name = housename.upper()
        except:
            house_name = housename

        house_obj = get_specific_house_obj(apartment_id,house_name)
        
        if not house_obj:
            print("Skipping ",house_name)
            continue
        else:
            check_tenant = check_occupancy(house_obj)
        if check_tenant[0] == "occupied":
            tenant = check_tenant[1]
        else:
            tenant = None

        if tenant:

            from datetime import datetime

            try:
                dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(datepaid) - 2)
                hour, minute, second = floatHourToTime(datepaid % 1)
                dt = dt.replace(hour=hour, minute=minute, second=second)
            except:
                dt = tenant.date

            values = validate_float_inputs_to_exclude_zeros_alt(rentdep,waterdep,elecdep,otherdep)
            if house_obj.housecode:
                rentdep = house_obj.housecode.rentrate if house_obj.housecode.rentrate else 0.0
                waterdep = house_obj.housecode.waterdep if house_obj.housecode.waterdep else 0.0
                elecdep = house_obj.housecode.elecdep if house_obj.housecode.elecdep else 0.0

                total = rentdep+waterdep+elecdep+values[3]

                if tenant.deposits:
                    print("TENANT DEPOSITS ALREADY UPLOADED FOR ....",house_obj,"UPDATING....WITH STATUS", status)
                    TenantDepositOp.update_deposits(tenant.deposits,rentdep,waterdep,elecdep,values[3],total,dt,status)
                    TenantOp.update_deposit(tenant,total)

                else:
                    print("CREATING tenant deposits...for >>",house_obj, "total: ", total, "STATUS: ", status)

                    dep = TenantDepositOp(rentdep,waterdep,elecdep,values[3],total,dt,status,tenant.id,None,house_obj.id,apartment_id)
                    dep.save()
                    TenantOp.update_deposit(tenant,total)
            else:
                total = values[0]+values[1]+values[2]+values[3]

                print("Updating tenant deposits...for >>",house_obj)
                if tenant.deposits:
                    print("TENANT DEPOSITS ALREADY UPDATED FOR ....",house_obj,"UPDATING....")
                    TenantDepositOp.update_deposits(tenant.deposits,values[0],values[1],values[2],values[3],total,status)
                    TenantOp.update_deposit(tenant,total)

                else:
                    dep = TenantDepositOp(values[0],values[1],values[2],values[3],total,status,tenant.id,None,house_obj.id,apartment_id)
                    dep.save()
                    TenantOp.update_deposit(tenant,total)

    return "completed"

def read_excel(dict_array,apartment_id,ttype,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

    for item in dict_array:

        unit = item["unit"]
        desc = item["desc"]
        group = item["group"]
        tenant = item["tenant"]
        raw_mobile = item["mobile"]
        email = item["email"]
        water = item["water"]

        natid = None

        if isinstance(group,float):
            if ttype == "ptenant":
                housecode = "S-" + str(int(group))
            else:
                housecode = "G-" + str(int(group))
        else:
            housecode = group

        housecode = housecode.upper()

        code_obj = get_specific_code_obj(apartment_id,housecode)


        if code_obj:
            print("Skipping ",housecode)
            lfile("Skipping ",housecode)
            
        elif group:
            valid_inputs = validate_float_inputs_to_exclude_zeros_alt(group,water)

            print("house & amount",housecode,valid_inputs[0])
            lfile("house & amount",housecode,valid_inputs[0])

            if ttype == "ptenant":
                print("creating service")
                code_obj = HouseCodeOp(housecode,0.0,valid_inputs[1],0.0,0.0,0.0,0.0,0.0,0.0,0.0,valid_inputs[0],0.0,0.0,0.0,apartment_id,user_id)
                code_obj.save()
            else:
                print("creating rent")
                lfile("creating rent")
                code_obj = HouseCodeOp(housecode,valid_inputs[0],valid_inputs[1],0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,apartment_id,user_id)
                code_obj.save()
        else:
            print("Entire row skipped>>","HOUSE",unit,"GROUP",group,"TENANT",tenant)
            lfile("Entire row skipped>>","HOUSE",unit,"GROUP",group,"TENANT",tenant)
            continue

        try:
            housename = str(int(unit) if unit else "" )
        except:
            housename = unit if unit else ""

        if housename == "":
            print("EMPTY CELL")

        try:
            house_name = housename.upper()
        except:
            house_name = housename

        house_obj = get_specific_house_obj(apartment_id,house_name)
        
        if house_obj:
            print("Skipping ",house_name)

        elif housename:
            house_obj = HouseOp(house_name,apartment_id,code_obj.id,user_id,desc)
            house_obj.save()
        else:
            pass


        print("STARTING...TELL:",raw_mobile,"Type:",type(raw_mobile))
        lfile("STARTING...TELL:",raw_mobile,"Type:",type(raw_mobile))

        try:
            if isinstance(raw_mobile,str):
                tel = raw_mobile
            else:
                tel = str(int(raw_mobile))
        except:
            print("Failed to stringify",raw_mobile)
            tel = ""

        if tel:

            if isinstance(tel,str):
                mobile0 = tel.replace(" ", "")
                mobile1 = mobile0.replace("`", "")
                mobile2 = mobile1.replace("'", "")

                if mobile2.startswith("0"):
                    mobile = mobile2.lstrip("0")

                elif mobile2.startswith("+254"):
                    mobile = mobile2.lstrip("+254")

                elif mobile2.startswith("254"):
                    mobile = mobile2.lstrip("254")

                else:
                    mobile = mobile2

            else:
                print("MOBILE HAS UNKNOWN FORMAT",tel,"its type is",type(tel))
                mobile = ""
        else:
            mobile = ""


        if mobile:
            rawstrtel = mobile.replace(" ", "")
            if len(rawstrtel) > 9:
                print(mobile,"is too long")
                strtel = ""
            else:
                strtel = rawstrtel
        else:
            print(mobile,"mobile does not exist")
            strtel = ""

        if strtel.startswith("0"):
            tenantphone = strtel
        else:
            tenantphone = "0" + strtel

        tenantemail = email.lower() if email else ""
        tenantnatid = str(int(natid) if natid else "" )

        if not tenantnatid:
            tenantnatid = nationalid_generator()
            check_dup = TenantOp.fetch_tenant_by_nat_id(tenantnatid)
            nat_id = nationalid_generator() if check_dup else tenantnatid
        else:
            nat_id = tenantnatid


        similar = False

        if tenant:
            if tenant.lower() == "vacant" or tenant.startswith("-") or tenant.startswith("_") or len(tenant) < 2:
                print(tenant,"name is not allowed")
                similar = True

            tenants = prop.tenants

            for t in tenants:
                if t.name.lower() == tenant.lower() and tenantphone == "0":
                    print("SIMILAR TENANT EXISTS: ",t.name,tenant)
                    similar = True

            present = TenantOp.fetch_tenant_by_nat_id(nat_id)
            if present:
                print("SIMILAR NATIONAL ID EXISTS: ",nat_id)
                similar = True

            if tenantemail:
                present2 = TenantOp.fetch_tenant_by_email(tenantemail)
                present3 = UserOp.fetch_user_by_email(tenantemail)
                if present2 or present3:
                    print("SIMILAR EMAIL EXISTS: ",tenantemail)
                    similar = True

            if tenantphone and tenantphone != "0":
                present4 = TenantOp.fetch_tenant_by_tel(tenantphone)
                if present4:
                    print("SIMILAR MOBILE NUMBER EXISTS: ",tenantphone,present4,"House",present4.house_allocated,"Apartment",present4.apartment)
                    similar = False

            if similar:
                pass
            else:
                if ttype == "ptenant":
                    ptenant_obj = PermanentTenantOp(tenant,tenantphone,nat_id,tenantemail,0.0,house_obj.id,apartment_id,user_id)
                    ptenant_obj.save()
                else:
                    tenant_obj = TenantOp(tenant,tenantphone,nat_id,tenantemail,0.0,apartment_id,user_id)
                    tenant_obj.save()

                    occupancy = check_occupancy(house_obj)

                    if occupancy[0] == "occupied":
                        print("Specified house occupied: ",house_obj)
                        pass

                    else:
                        house_id = house_obj.id
                        tenant_id = tenant_obj.id

                        allocate_tenant_obj = AllocateTenantOp(apartment_id,house_id,tenant_id,user_id,description=None)
                        allocate_tenant_obj.save()

                        TenantOp.update_status(tenant_obj,"Resident")
                        TenantOp.update_residency(tenant_obj,"Old")


    return "completed"


def read_water_excel(dict_array,apartment_id,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()


    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
    billing_period = prop.billing_period

    for item in dict_array:

        unit = item["house"]
        readings = item["reading"]

        try:
            housename = str(int(unit) if unit else "" )
        except:
            housename = unit if unit else ""

        try:
            rawreading = str(int(readings) if readings else "" )
        except:
            rawreading = readings if readings else ""


        str_reading = rawreading.replace(".","")



        if housename == "":
            print("SKIPPING EMPTY HOUSE CELL")
            continue

        if str_reading == "":
            print("SKIPPING EMPTY READING CELL")
            continue


        try:
            house_name = housename.upper()
        except:
            house_name = housename

        house_obj = get_specific_house_obj(apartment_id,house_name)
        
        if not house_obj:
            print("Skipping ",house_name, "not availble in apartment")
            continue

        house_list = filtered_house_list(apartment_id)

        if house_obj not in house_list:
            print("FAILED! HOUSE ALREADY READ", house_obj)
            continue
        else:
            reading = int(str_reading)
            meter = fetch_active_meter(house_obj)
        
            meter_id = meter.id
            last_reading = getlast_reading(meter_id)

            meter_num = meter.meter_number
            str_decitype = get_str_decitype(meter_id)
            prev_reading = f"Last reading: {last_reading}"
            meter = f"{meter_num}"
            mtype = f"Type: {str_decitype}"

            decitype = get_decitype(meter_id)
            try:
                float_current_reading = float(reading)*decitype
                float_last_reading = float(last_reading)*decitype
            except:
                float_current_reading = 0.0 * decitype
                float_last_reading = 0.0 * decitype

            calc_units = float_current_reading - float_last_reading
            units_consumed = round(calc_units,3)

            ###################################################################################################
            if last_reading > int(reading):
                print("FAILED! Check reaings for", house_obj)
                continue
            else:

                if datetime.datetime.now().day < 21 and datetime.datetime.now().month == billing_period.month:
                    #Only enters this block for readings taken after billing and are meant for the same period as the current bills. next month of billing
                    print("Reading left out captured")

                    month = billing_period.month
                    year = billing_period.year

                elif datetime.datetime.now().day >= 21:
                    #Only enters this block if readings are taken early before the next month of billing

                    if datetime.datetime.now().month != 12:
                        if datetime.datetime.now().month + 1 == billing_period.month:

                            #Only enters this block for readings taken early and are meant for early next current billing
                            print("Reading left out captured for next month")
                            month = billing_period.month
                            year = billing_period.year

                        else:
                            #Only enters this block for early billing COMMON PROCESS
                            print("Reading captured early and normally for next period")
                            month = billing_period.month + 1 if billing_period.month != 12 else 1
                            year = billing_period.year if billing_period.month != 12 else billing_period.year + 1
                    else:
                        if 1 == billing_period.month:
                            print("Reading left out captured for Jan ater early billing for Jan")
                            month = billing_period.month
                            year = billing_period.year
                        else:
                            #Only enters this block for early billing COMMON PROCESS
                            print("Reading captured early and normally for Jan")
                            month = 1
                            year = billing_period.year + 1
                else:
                    #Only enters this block if readings are taken early in the next month of billing
                    print("Reading captured late")
                    if billing_period.month == 12:
                        month = 1
                        year = billing_period.year + 1

                    else:
                        month = billing_period.month + 1 if billing_period.month != 12 else 1
                        year = billing_period.year if billing_period.month != 12 else billing_period.year + 1
                    

                reading_period = generate_date(month,year)

                reading_obj = MeterReadingOp("actual water reading",reading,last_reading,units_consumed,reading_period,apartment_id,house_obj.id,meter_id,user_id)
                reading_obj.save()
                
    return '<span class="text-success">Upload successful</span>'

def read_payments_excel(dict_array,payperiod,apartment_id,userid,cbid):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    # print(dict_array)

    # return ""

    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
    co = prop.company

    for item in dict_array:

        unit = item["housename"]
        amount = item["amount"]
        datepaid = item["date"]
        ref = item["ref"]
        desc = item["desc"]
        r_comment = item["comment"]

        if datepaid:
            # formatted_paydate = date_formatter_upload(datepaid)
            # pay_date = parse(formatted_paydate)
            pay_date = datepaid
        else:
            pay_date = datetime.datetime.now()

        try:
            house_name = unit.upper()
        except:
            house_name = unit

        house_obj = get_specific_house_obj(apartment_id,house_name)
        if house_obj:
            pass
        else:
            print("specified house does not exist")
            if cbid:
                ctob_obj = CtoBop.fetch_c2b_by_id(cbid)
                if ctob_obj:
                    CtoBop.update_status(ctob_obj,"unclaimed")

            continue

        # URGENT TO DO REVISIT FOR RESIDENT AND TENANTS
        tenant_obj = house_obj.owner
        if not tenant_obj:
            check = check_occupancy(house_obj)
            if check[0] == "occupied":
                tenant_obj = check[1]
            else:
                print("SKIPPING house>> ",house_obj,"because it is not occupied")
                continue

        bill= ""

        if payperiod:
            if isinstance(payperiod,datetime.date):
                pay_period_date = payperiod
            else:
                pay_period = date_formatter_alt(payperiod)
                pay_period_date = parse(pay_period)
        
        elif r_comment:
            rr_comment = r_comment.replace("Installment","Instalment")
            comment = rr_comment.replace("  "," ")
            if "Deposit" in comment:
                print("30%")
                pay_period_date = tenant_obj.checkin
            elif "Instalment 1" in comment:
                print("Inst 1")
                pay_period_date = tenant_obj.checkin + relativedelta(months=1)
            elif "Instalment 2" in comment:
                print("Inst 2")
                pay_period_date = tenant_obj.checkin + relativedelta(months=2)
            elif "Instalment 3" in comment:
                print("Inst 3")
                pay_period_date = tenant_obj.checkin + relativedelta(months=3)
            elif "Instalment 4" in comment:
                print("Inst 4")
                pay_period_date = tenant_obj.checkin + relativedelta(months=4)
            elif "Instalment 5" in comment:
                print("Inst 5")
                pay_period_date = tenant_obj.checkin + relativedelta(months=5)
            elif "Instalment 6" in comment:
                print("Inst 6")
                pay_period_date = tenant_obj.checkin + relativedelta(months=6)
            elif "Instalment 7" in comment:
                print("Inst 7")
                pay_period_date = tenant_obj.checkin + relativedelta(months=7)
            else:
                print("Inst 8",comment)
                pay_period_date = tenant_obj.checkin + relativedelta(months=8)

                #TODO FINISH ALL INSTALMENTS
            
        else:
            print("Instalment type or deposit not specified !!")
            pay_period_date = get_billing_period(prop)


        if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
            # if tenant_obj.apartment.company.name == "REVER MWIMUTO LIMITED":
            user_obj = UserOp.fetch_user_by_id(userid)
            if crm(user_obj):
                try:
                    bill = tenant_obj.monthly_charges[0]
                except:
                    print("BILLS FOR TENANT ",tenant_obj,"are not available")
                    continue
            else:
                bill = fetch_target_period_owner_invoice(house_obj,pay_period_date)
        else:
            bill = fetch_target_period_invoice(house_obj,pay_period_date)

        valid_amount = amount

        if not valid_amount:
            print("Invalid amount")
            continue

        if isinstance(amount,str):
            invalid_amount = valid_amount.replace(",","")
            amount = float(int(invalid_amount.split(".")[0]))
            valid_amount = float(int(invalid_amount.split(".")[0]))

        bal = amount

        bookingdue = bill.booking_due
        instalmentdue = bill.instalment_due
        addfeedue = bill.addfee_due

        rentdue = bill.rent_due
        waterdue = bill.water_due
        electricitydue = bill.electricity_due
        garbagedue = bill.garbage_due
        securitydue = bill.security_due
        servicedue = bill.maintenance_due

        penaltydue = bill.penalty_due
        depositdue = bill.deposit_due
        agreementdue = bill.agreement_due


        if bal >= depositdue:
            depositpaid = depositdue
            bal -= depositdue
        elif bal < depositdue and bal > 0:
            depositpaid = bal
            bal = 0
        else:
            depositpaid = 0.0

        if bal >= bookingdue:
            bookingpaid = bookingdue
            bal -= bookingdue
        elif bal < bookingdue and bal > 0:
            bookingpaid = bal
            bal = 0
        else:
            bookingpaid = 0.0

        if bal >= instalmentdue:
            instalmentpaid = instalmentdue
            bal -= instalmentdue
        elif bal < instalmentdue and bal > 0:
            instalmentpaid = bal
            bal = 0
        else:
            instalmentpaid = 0.0

        if bal >= addfeedue:
            addfeepaid = addfeedue
            bal -= addfeedue
        elif bal < addfeedue and bal > 0:
            addfeepaid = bal
            bal = 0
        else:
            addfeepaid = 0.0

        if bal >= rentdue:
            rentpaid = rentdue
            bal -= rentdue
        elif bal < rentdue and bal > 0:
            rentpaid = bal
            bal = 0
        else:
            rentpaid = 0.0

        if bal >= penaltydue:
            penaltypaid = penaltydue
            bal -= penaltydue
        elif bal < penaltydue and bal > 0:
            penaltypaid = bal
            bal = 0
        else:
            penaltypaid = 0.0

        if bal >= garbagedue:
            garbagepaid = garbagedue
            bal -= garbagedue
        elif bal < garbagedue and bal > 0:
            garbagepaid = bal
            bal = 0
        else:
            garbagepaid = 0.0

        if bal >= securitydue:
            securitypaid = securitydue
            bal -= securitydue
        elif bal < securitydue and bal > 0:
            securitypaid = bal
            bal = 0
        else:
            securitypaid = 0.0

        if bal >= servicedue:
            servicepaid = servicedue
            bal -= servicedue
        elif bal < servicedue and bal > 0:
            servicepaid = bal
            bal = 0
        else:
            servicepaid = 0.0

        if bal >= waterdue:
            waterpaid = waterdue
            bal -= waterdue
        elif bal < waterdue and bal > 0:
            waterpaid = bal
            bal = 0
        else:
            waterpaid = 0.0

        if bal >= electricitydue:
            electricitypaid = electricitydue
            bal -= electricitydue
        elif bal < electricitydue and bal > 0:
            electricitypaid = bal
            bal = 0
        else:
            electricitypaid = 0.0

        if bal >= agreementdue:
            agreementpaid = agreementdue
            bal -= agreementdue
        elif bal < agreementdue and bal > 0:
            agreementpaid = bal
            bal = 0
        else:
            agreementpaid = 0.0

        if bal:
            overpayment = bal
        else:
            overpayment = 0.0
 


        book = "Deposit_" if bookingpaid else ""
        inst = "Instalment" if instalmentpaid else ""
        addfee = "Additional fees" if addfeepaid else ""

        water = "Water" if waterpaid else ""
        rent = "Rent" if rentpaid else ""
        garbage = "Garbage" if garbagepaid else ""
        sec = "Security" if securitypaid else ""
        dep = "Deposit" if depositpaid else ""
        serv = "Service" if servicepaid else ""

        narration = f"{rent} {water} {garbage} {sec} {serv} {dep} {book} {inst} {addfee}"

        print("NARRATION: ",narration)

        paymode = "mpesa" if "mpesa" in desc else "Bank"
        raw_bill_ref = ref
        paytype = desc
        amount = amount

        if raw_bill_ref.upper() == "N/A":
            bill_ref = raw_bill_ref
        elif raw_bill_ref.upper() == "NA":
            bill_ref = "N/A"
        elif len(raw_bill_ref) < 5:
            bill_ref = raw_bill_ref
        else:
            bill_ref = raw_bill_ref
            payob = PaymentOp.fetch_payment_by_ref(raw_bill_ref)
            if payob:
                if payob.voided:
                    pass
                else:
                    print("REFERENCE (",raw_bill_ref,")EXISTS >>","MONTH:",payob.pay_period.month,"PROP:",payob.apartment,"TENANT & HOUSE:",payob.tenant,payob.ptenant,payob.house,"ID:",payob.id,"VOID:",payob.voided)
                    continue

        tenant_id = None

        if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
            payment_obj = PaymentOp(paymode,bill_ref,desc,narration,pay_date,pay_period_date,bal,valid_amount,apartment_id, house_obj.id,tenant_id,tenant_obj.id,userid)
            payment_obj.save()
        else:
            payment_obj = PaymentOp(paymode,bill_ref,desc,narration,pay_date,pay_period_date,bal,valid_amount,apartment_id, house_obj.id,tenant_obj.id,tenant_id,userid)
            payment_obj.save()


        if co.receipt_num:
            num = co.receipt_num
            num += 1

            CompanyOp.increment_receipt_num(co,num)
            PaymentOp.update_receipt_num(payment_obj,num)
        #################################################################################################

        rand_id = random_generator()
        if PaymentOp.fetch_payment_by_rand_id(rand_id):
            rand_id = random_generator(size=11)
            awe = sms.send("Ran random the second time !", ["+254716674695"],sender)
            if PaymentOp.fetch_payment_by_rand_id(rand_id):
                rand_id = random_generator(size=12)
                awe = sms.send("Ran random the third time !", ["+254716674695"],sender)
                if PaymentOp.fetch_payment_by_rand_id(rand_id):
                    rand_id = random_generator(size=13)
                    awe = sms.send("Ran random the fouth time !", ["+254716674695"],sender)
                    if PaymentOp.fetch_payment_by_rand_id(rand_id):
                        awe = sms.send("There is a problem with random, payment aborted !", ["+254716674695"],sender)
                        return "Payment could not be processed at this time! Try again later"

        tenant_bal = tenant_obj.balance
        tenant_bal -= valid_amount
        if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
            PermanentTenantOp.update_balance(tenant_obj,tenant_bal)
        else:
            TenantOp.update_balance(tenant_obj,tenant_bal)

        running_balance = bal
        running_balance-= valid_amount

        PaymentOp.update_balance(payment_obj,running_balance)
        PaymentOp.update_rand_id(payment_obj,rand_id)


        schedule_obj = None

        if co.ctype == "crm":
            print("GONE TO PAY AVIV")
            schedule_objs = tenant_obj.schedules
            for sch in schedule_objs:
                if sch.schedule_date.month == pay_period_date.month and sch.schedule_date.year == pay_period_date.year:
                    schedule_obj = sch
                    break

        if schedule_obj:
            print("SCHEDULE OBJI FOUND FOR UNIT",unit, "of month",schedule_obj.schedule_date.month, "and year",schedule_obj.schedule_date.year)

            print("#################################")
            print("DATE PASSED",pay_period_date.month,pay_period_date.year)
            print("SCHEDULE OBJ",schedule_obj.schedule_date.month,schedule_obj.schedule_date.year)
            print("#################################")
            sch_arrears = 0.0
            prev_sch = fetch_prev_schedule(pay_period_date.month,pay_period_date.year,tenant_obj.schedules,tenant_obj.id)
            if prev_sch:
                print("FOUND Previous scheduled of month",prev_sch[0].schedule_date.month, "and year", prev_sch[0].schedule_date.year)
                sch_arr = prev_sch[0].balance
                if sch_arr:
                    sch_arrears = sch_arr
            if sch_arrears:
                sch_total_amount = schedule_obj.schedule_amount + sch_arrears
            else:
                sch_total_amount = schedule_obj.schedule_amount

            schpaid = schedule_obj.paid + valid_amount
            
            sch_bal = sch_total_amount - schpaid

            print("values",sch_arrears,sch_total_amount,valid_amount,sch_bal)

            PaymentScheduleOp.update_details(schedule_obj,sch_arrears,sch_total_amount,schpaid,sch_bal,bill_ref,paytype,pay_date)
        
        specific_charge_obj = bill

        if specific_charge_obj:

            db.session.expire(specific_charge_obj)
            bala = specific_charge_obj.balance
            bala-=valid_amount
            MonthlyChargeOp.update_balance(specific_charge_obj,bala)

            paid_amount = specific_charge_obj.paid_amount
            cumulative_pay = paid_amount + valid_amount
            MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
            MonthlyChargeOp.update_payment_date(specific_charge_obj,pay_date)

            booking_paid = bookingpaid + specific_charge_obj.booking_paid if specific_charge_obj.booking_paid is not None else 0
            instalment_paid = instalmentpaid + specific_charge_obj.instalment_paid if specific_charge_obj.instalment_paid is not None else 0
            addfee_paid = addfeepaid + specific_charge_obj.addfee_paid if specific_charge_obj.addfee_paid is not None else 0

            rent_paid = rentpaid + specific_charge_obj.rent_paid if specific_charge_obj.rent_paid is not None else 0

            water_paid = waterpaid + specific_charge_obj.water_paid if specific_charge_obj.water_paid is not None else 0
            penalty_paid = penaltypaid + specific_charge_obj.penalty_paid if specific_charge_obj.penalty_paid is not None else 0
            electricity_paid = electricitypaid + specific_charge_obj.electricity_paid if specific_charge_obj.electricity_paid  is not None else 0
            garbage_paid = garbagepaid + specific_charge_obj.garbage_paid if specific_charge_obj.garbage_paid is not None else 0
            security_paid = securitypaid+ specific_charge_obj.security_paid if specific_charge_obj.security_paid is not None else 0
            service_paid = servicepaid + specific_charge_obj.maintenance_paid if specific_charge_obj.maintenance_paid is not None else 0

            if specific_charge_obj.tenant_id:
                if specific_charge_obj.house.housecode.rentrate:
                    rent_paid += overpayment
            else:
                if specific_charge_obj.ptenant_id:
                    if specific_charge_obj.house.housecode.servicerate:
                        service_paid += overpayment

            deposit_paid = depositpaid + specific_charge_obj.deposit_paid if specific_charge_obj.deposit_paid is not None else 0
            agreement_paid = agreementpaid + specific_charge_obj.agreement_paid if specific_charge_obj.agreement_paid is not None else 0

            MonthlyChargeOp.update_payments(specific_charge_obj,booking_paid,instalment_paid,addfee_paid,rent_paid,water_paid,electricity_paid,garbage_paid,security_paid,service_paid,penalty_paid,deposit_paid,agreement_paid)
            PaymentOp.update_payments(payment_obj,bookingpaid,instalmentpaid,addfeepaid,rentpaid,waterpaid,electricitypaid,garbagepaid,securitypaid,servicepaid,penaltypaid,depositpaid,agreementpaid)

            try:
                bookbal = specific_charge_obj.booking_due - bookingpaid
                instbal = specific_charge_obj.instalment_due - instalmentpaid
                addfeebal = specific_charge_obj.addfee_due - addfeepaid

                rentbal = specific_charge_obj.rent_due - rentpaid

                # rentbal -= overpayment
                waterbal = specific_charge_obj.water_due - waterpaid
                electricitybal = specific_charge_obj.electricity_due - electricitypaid
                servicebal = specific_charge_obj.maintenance_due - servicepaid
                penaltybal = specific_charge_obj.penalty_due - penaltypaid
                securitybal = specific_charge_obj.security_due - securitypaid
                garbagebal = specific_charge_obj.garbage_due - garbagepaid
                depositbal = specific_charge_obj.deposit_due - depositpaid
                agreementbal = specific_charge_obj.agreement_due - agreementpaid

                if specific_charge_obj.tenant_id:
                    if specific_charge_obj.house.housecode.rentrate:
                        rentbal -= overpayment
                else:
                    if specific_charge_obj.ptenant_id:
                        if specific_charge_obj.house.housecode.servicerate:
                            servicebal -= overpayment

                MonthlyChargeOp.update_dues(specific_charge_obj,bookbal,instbal,addfeebal,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)
            except:
                print("PAID TO LEGACY BILL")

def run_update(houseids,apartment_id,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

    # houses = [get_specific_house_obj(apartment_id,hs) for hs in houseids]
    houses = prop.houses
    billing_period = generate_date(7,2022)

    print("STARTING UPDATE")

    for hs in houses:
        print("ON HOUSE: ",hs)
        # bills = fetch_current_billing_period_bills(billing_period,hs.monthlybills)
        bills = hs.monthlybills

        for bill in bills:
            print("RUNNING BILL UPDATE FOR : ",bill.apartment.company.name,"HOUSE: ",bill.house," >> ",bill.month,"/",bill.year)
            original_amount = bill.total_bill
            # if bill.apartment.billing_period.month == bill.month:
            values = validate_float_inputs("","","","","","","","","","")

            #TODO -remove this block
            agreement = bill.agreement if bill.agreement else 0.0
            deposit = bill.deposit if bill.deposit else 0.0

            if bill.house.housecode.waterrate or bill.house.housecode.watercharge:
                # update_water = bill.water
                update_water = values[1] if values[1] != "null" else bill.water
            else:
                update_water = values[1] if values[1] != "null" else bill.water

            update_rent = values[0] if values[0] != "null" else bill.rent
            update_garbage = values[2] if values[2] != "null" else bill.garbage
            update_security = values[3] if values[3] != "null" else bill.security
            update_fine = values[4] if values[4] != "null" else bill.penalty
            update_agreement = values[7] if values[7] != "null" else agreement
            update_deposit = values[5] if values[5] != "null" else deposit
            update_arrears = values[6] if values[6] != "null" else bill.arrears
            update_maintenance = values[9] if values[9] != "null" else bill.maintenance

            total_amount = update_water+update_rent+update_garbage+update_security+update_fine+update_arrears+update_deposit+update_agreement+bill.electricity+update_maintenance
            MonthlyChargeOp.update_monthly_charge(bill,values[1],values[0],values[2],"null",values[3],values[5],values[7],values[9],values[4],values[6],total_amount,user_id)

            # if bill.rent_balance:

            # if bill.rent_balance:
            if bill.rent_paid:
                rentbal = bill.rent_balance + update_rent - bill.rent_paid
            else:
                try:
                    rentbal = bill.rent_balance + update_rent
                except:
                    rentbal = update_rent

            # # supplied arrears to effect rent only
            # rentarr = bill.rent_balance 
            # if values[6] != "null":
            #     rentarr = bill.rent_balance + values[6]
            #     rentbal += values[6]

            if bill.water_paid:
                waterbal = bill.water_balance + update_water - bill.water_paid
            else:
                waterbal = bill.water_balance + update_water if bill.water_balance else update_water

            if bill.electricity_paid:
                electricitybal = bill.electricity_balance + bill.electricity - bill.electricity_paid
            else:
                electricitybal = bill.electricity_balance + bill.electricity if bill.electricity_balance else bill.electricity

            if bill.maintenance_paid:
                servicebal = bill.maintenance_balance + update_maintenance - bill.maintenance_paid
            else:
                servicebal = bill.maintenance_balance + update_maintenance if bill.maintenance_balance else update_maintenance

            if bill.penalty_paid:
                penaltybal = bill.penalty_balance + update_fine - bill.penalty_paid
            else:
                penaltybal = bill.penalty_balance + update_fine if bill.penalty_balance else update_fine

            if bill.security_paid:
                securitybal = bill.security_balance + update_security - bill.security_paid
            else:
                securitybal = bill.security_balance + update_security if bill.security_balance else update_security

            if bill.garbage_paid:
                garbagebal = bill.garbage_balance + update_garbage - bill.garbage_paid
            else:
                garbagebal = bill.garbage_balance + update_garbage if bill.garbage_balance else update_garbage


            if bill.deposit_paid:
                depositbal = bill.deposit_balance + update_deposit - bill.deposit_paid
            else:
                depositbal = bill.deposit_balance + update_deposit if bill.deposit_balance else update_deposit

            if bill.agreement_paid:
                agreementbal = bill.agreement_balance + update_agreement - bill.agreement_paid
            else:
                agreementbal = bill.agreement_balance + update_agreement if bill.agreement_balance else update_agreement

            MonthlyChargeOp.update_dues(bill,0.0,0.0,0.0,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)
            # MonthlyChargeOp.update_rent_balance(bill,rentarr)


            diff = total_amount - original_amount

            if bill.apartment.billing_period.month == bill.month:

                if bill.tenant_id:

                    tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                    running_bal = tenant_obj.balance
                    running_bal = running_bal + diff
                    TenantOp.update_balance(tenant_obj,running_bal)

                if bill.ptenant_id:
                    tenant_obj = PermanentTenantOp.fetch_tenant_by_id(bill.ptenant_id)
                    running_bal = tenant_obj.balance
                    running_bal = running_bal + diff
                    PermanentTenantOp.update_balance(tenant_obj,running_bal)

            # bal = bill.balance
            # bal = bal + diff
            if bill.paid_amount:
                bal = total_amount - bill.paid_amount
            else:
                bal = total_amount

            MonthlyChargeOp.update_balance(bill,bal)


def read_arrears_excel(dict_array,option,apartment_id,userid):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()


    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

    for item in dict_array:

        housename = item["housename"]
        rentarr = item["rentarr"]
        servarr = item["servarr"]

        house_name = housename.upper()
        house_obj = get_specific_house_obj(apartment_id,house_name)
        
        if house_obj:
            items = house_obj.monthlybills
            target_items = fetch_current_billing_period_bills(prop.billing_period,items)
            if target_items:
                bill = target_items[0]
                if bill:
                    if bill.arrears_updated and option != "replace":
                        print("Skipping", house_name,"arrears uploaded already ARR:",bill.arrears)
                        continue


                    #start of arrears upload################################################################################

                    original_amount = bill.total_bill

                    #####################################################################################################################
                    if option == "add":
                        update_water = bill.water_balance
                        update_rent = rentarr if rentarr else bill.rent_balance
                        update_garbage = bill.garbage_balance
                        update_security = bill.security_balance
                        update_fine = bill.penalty_balance
                        update_agreement = bill.agreement_balance
                        update_deposit = bill.deposit_balance
                        update_electricity = bill.electricity_balance
                        update_maintenance = servarr if servarr else bill.maintenance_balance
                    else:
                        update_water = 0.0
                        update_rent = rentarr
                        update_garbage = 0.0
                        update_security = 0.0
                        update_fine = 0.0
                        update_agreement = 0.0
                        update_deposit = 0.0
                        update_electricity = 0.0
                        update_maintenance = servarr

                    update_arrears = update_water+update_rent+update_garbage+update_security+update_fine+update_deposit+update_agreement+update_electricity+update_maintenance

                    total_amount = original_amount - bill.arrears + update_arrears

                    MonthlyChargeOp.update_monthly_charge(bill,"null","null","null","null","null","null","null","null","null",update_arrears,total_amount,userid)

                    MonthlyChargeOp.update_balances(bill,0.0,0.0,0.0,update_rent,update_water,update_electricity,update_garbage,update_security,update_maintenance,update_fine,update_deposit,update_agreement)


                    # if bill.rent_balance:
                    if bill.rent_paid:
                        rentbal = bill.rent + update_rent - bill.rent_paid
                    else:
                        rentbal = bill.rent + update_rent

                    if bill.water_paid:
                        waterbal = bill.water + update_water - bill.water_paid 
                    else:
                        waterbal = bill.water + update_water

                    if bill.electricity_paid:
                        electricitybal = bill.electricity + update_electricity - bill.electricity_paid
                    else:
                        electricitybal = bill.electricity + update_electricity

                    if bill.maintenance_paid:
                        servicebal = bill.maintenance + update_maintenance - bill.maintenance_paid
                    else:
                        servicebal = bill.maintenance + update_maintenance

                    if bill.penalty_paid:
                        penaltybal = bill.penalty + update_fine - bill.penalty_paid
                    else:
                        penaltybal = bill.penalty + update_fine

                    if bill.security_paid:
                        securitybal = bill.security + update_security - bill.security_paid
                    else:
                        securitybal = bill.security + update_security

                    if bill.garbage_paid:
                        garbagebal = bill.garbage + update_garbage - bill.garbage_paid
                    else:
                        garbagebal = bill.garbage + update_garbage


                    if bill.deposit_paid:
                        depositbal = bill.deposit + update_deposit - bill.deposit_paid
                    else:
                        depositbal = bill.deposit + update_deposit

                    if bill.agreement_paid:
                        agreementbal = bill.agreement + update_agreement - bill.agreement_paid
                    else:
                        agreementbal = bill.agreement + update_agreement

                    MonthlyChargeOp.update_dues(bill,0.0,0.0,0.0,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)


                    diff = total_amount - original_amount

                    # if bill.tenant_id:

                    #     tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                    #     running_bal = tenant_obj.balance
                    #     running_bal = running_bal + diff
                    #     TenantOp.update_balance(tenant_obj,running_bal)

                    # if bill.ptenant_id:

                    #     tenant_obj = PermanentTenantOp.fetch_tenant_by_id(bill.ptenant_id)
                    #     running_bal = tenant_obj.balance
                    #     running_bal = running_bal + diff
                    #     PermanentTenantOp.update_balance(tenant_obj,running_bal)

                    # bal = bill.balance
                    # bal = bal + diff
                    if bill.paid_amount:
                        bal = total_amount - bill.paid_amount
                    else:
                        bal = total_amount

                    MonthlyChargeOp.update_balance(bill,bal)
                    MonthlyChargeOp.update_arrears_status(bill,True)

                    tenant_obj = bill.tenant if bill.tenant else bill.ptenant

                    if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
                        PermanentTenantOp.update_balance(tenant_obj,bal)
                    else:
                        TenantOp.update_balance(tenant_obj,bal)
                    #####################################################################################################################

                else:
                    print("No bill exists for ", house_name)
        else:
            print("House does not exist >>>>>>>>>>>>",house_name)

    return '<span class="text-success">Upload successful</span>'


def sendlogs(date):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    time = datetime.datetime.now() + relativedelta(hours=3)

    if date:
        all_logins = UserLoginDataOp.fetch_logins_by_day(date)
        sms_text = f"Date {date.day} logins [{len(all_logins)}]: "

    else:
        all_logins = UserLoginDataOp.fetch_logins_by_day(time)
        sms_text = f"Today's logins [{len(all_logins)}] as of {time.strftime('%X')}: "


    print("total logins: ",len(all_logins))
    start = 1
    for login in all_logins:
        new_line = f"\n {start}. {login.user.company.name}-{login.user.name} x{login.frequency}"
        start += 1
        sms_text += new_line

    try:
        notify = sms.send(sms_text, ["+254716674695"],sender)
        print(notify)
    except Exception as e:
        print("sending logs failed",e)

    

def penalty_calculator(param):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    prop_list = param
    
    print("initializing fine calculation")

    for n in prop_list:
        total_fines = 0.0
        prop = ApartmentOp.fetch_apartment_by_id(n)
        co = prop.company
        if not prop:
            return None
        billing_period = get_billing_period(prop)
        tenants = tenantauto(n)

        for tenant in tenants:
            latest_payment = fetch_current_billing_period_payments(billing_period,tenant.payments)
            qualify = False
            if latest_payment:
                if latest_payment[0].pay_date.day > 10:
                    qualify = True
            if tenant.balance > 1000 or qualify:
                print("Qualified")
                bills = tenant.monthly_charges
                bill = None
                for i in bills:
                    if i.month == billing_period.month and i.year == billing_period.year:
                        bill = i
                        break

                if bill:

                    #############################SPECIAL BLOCK TO UPDATE ERRONEOUS TOTAL #################################################
                    original_amount = bill.total_bill

                    #TODO -remove this block
                    agreement = bill.agreement if bill.agreement else 0.0
                    deposit = bill.deposit if bill.deposit else 0.0

                    total_amount = bill.water+bill.rent+bill.garbage+bill.security+bill.penalty+bill.arrears+bill.deposit+bill.agreement+bill.electricity+bill.maintenance
                    MonthlyChargeOp.update_monthly_charge(bill,"null","null","null","null","null","null","null","null","null","null",total_amount,None)

                    diff = total_amount - original_amount

                    tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                    running_bal = tenant_obj.balance
                    running_bal = running_bal + diff
                    TenantOp.update_balance(tenant_obj,running_bal)

                    # bal = bill.balance
                    # bal = bal + diff
                    if bill.paid_amount:
                        bal = total_amount - bill.paid_amount
                    else:
                        bal = total_amount

                    MonthlyChargeOp.update_balance(bill,bal)
                    #############################SPECIAL BLOCK TO UPDATE ERRONEOUS TOTAL #################################################

                    hse = check_house_occupied(tenant)[1]

                    if not bill.fine_date:
                        MonthlyChargeOp.update_fine_date(bill,1)             
                    
                    if bill.fine_date != datetime.datetime.now().day:
                        # fine_amnt = 0.0033333333 * hse.housecode.rentrate
                        fine_amnt = 0.10 * hse.housecode.rentrate

                        fines = round(fine_amnt,0)
                        total_fines += fines
                        printf = f"House {hse} before fining: STATUS>>{bill.fine_status} BILL>>>Kes{bill.total_bill} CALCULATED FINES>>>Kes{fines}"
                        print(printf)
                        
                        update_fines = bill.penalty + fines
                        update_total=bill.total_bill + fines

                        MonthlyChargeOp.update_monthly_charge(bill,"null","null","null","null","null","null","null","null",update_fines,"null",update_total,None)
                        MonthlyChargeOp.update_fine_status(bill,"fined")
                        MonthlyChargeOp.update_fine_date(bill,datetime.datetime.now().day)                    
                        printff = f"House {hse} after fining: STATUS>>{bill.fine_status} BILL>>>Kes{bill.total_bill}"
                        print(printff)

                        diff = fines

                        tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                        running_bal = tenant_obj.balance
                        running_bal = running_bal + diff
                        TenantOp.update_balance(tenant_obj,running_bal)

                        bal = bill.balance
                        bal = bal + diff
                        MonthlyChargeOp.update_balance(bill,bal)
                    else:
                        print("Fine status for", hse, "Fining failed >>>>> status>>>>>",bill.fine_status,">>>>DATE>>>>",bill.fine_date)
            else:
                print("did not qualify")

        if total_fines:
            txtx = f"Total calculated fines for {prop.name} as of today ({datetime.datetime.now().day}) are Shs. {total_fines:,.1f}"
            print(txtx)
            cophone = sms_phone_number_formatter(co.sphone) if co.sphone else "0"
            # try:
            #     notify = sms.send(txtx, ["+254716674695",cophone],"KIOTAPAY")
            # except:
            #     pass
        else:
            pass

def water_bill(apartment_id,houseids,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)#get apartment obj first
    # meter_readings = apartment_obj.meter_readings
    target_readings = []

    house_list = []

    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            house_list.append(hse)
    else:
        house_list = houseauto(apartment_id)

    for h in house_list:
        meter_readings = h.meter_readings

        for item in meter_readings:
            if item.reading_period:
                if item.reading_period.month == month and item.reading_period.year == year and item.description == "actual water reading":
                    target_readings.append(item)

    for i in target_readings:
        units = i.units
        reading_id= i.id
        apartment_id = i.apartment_id
        house_id = i.house_id
        meter_id = i.meter_id
        house_obj = HouseOp.fetch_house_by_id(house_id)
        if not house_obj.housecode:
            print("HOUSE GROUP MISSING FOR: ",house_obj,"of",house_obj.apartment)
            continue
        if not house_obj.housecode.waterrate and not house_obj.housecode.waterrate1:
            print("RATE MISSING FOR: ",house_obj,"of",house_obj.apartment)
            continue
        if house_obj.housecode.waterrate1:
            print("using graduated scale")
            if units < 7:
                bill_amount = house_obj.housecode.waterrate1
            elif units < 20:
                bill_amount = house_obj.housecode.waterrate2 * units
            else:
                bill_amount = house_obj.housecode.waterrate3 * units
        else:
    
            if house_obj.housecode.seweragerate:
                bill_amount = (house_obj.housecode.waterrate * units) + (house_obj.housecode.seweragerate * units)
            else:
                bill_amount = house_obj.housecode.waterrate * units
                
            print("using normal scale")


        existing_charge_obj=ChargeOp.fetch_charge_by_reading_id(reading_id)
        # if existing_charge_obj:
        #     ChargeOp.delete(existing_charge_obj)
        if not existing_charge_obj:
            date = generate_date(month,year)
            house_obj = HouseOp.fetch_house_by_id(house_id)
            if house_obj:
                if not house_obj.billable:
                    charge_obj =  ChargeOp(charge_type_id,0.0,apartment_id,house_id,user_id,date,meter_id,reading_id)#REFACTOR meter can be left out for rent,garbage and security
                    charge_obj.save()
                    charge_status = True

                    MeterReadingOp.update_charge_status(i,charge_status)
                else:
                    charge_obj =  ChargeOp(charge_type_id,bill_amount,apartment_id,house_id,user_id,date,meter_id,reading_id)#REFACTOR meter can be left out for rent,garbage and security
                    charge_obj.save()
                    charge_status = True
                    print("Billing water >>>",house_obj.name, "of",house_obj.apartment,"Amount >>>",bill_amount)

                    MeterReadingOp.update_charge_status(i,charge_status)

def rent_bill(apartment_id,houseids,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)

    house_list = []
    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            house_list.append(hse)
    else:
        house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        rent_charge = 0
        
        result = check_occupancy(house)
        if result[0] == "occupied" or house.owner:
            if not house.billable:
                rent_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue
                # if house.housecode.vatrate:
                #     raw_rent_charge = (house.housecode.vatrate * house.housecode.rentrate * 0.01) + house.housecode.rentrate
                #     rent_charge = round(raw_rent_charge,0) if raw_rent_charge else 0
                # else:
                #     rent_charge = house.housecode.rentrate
                rent_charge = house.housecode.rentrate

            all_charges = ChargeOp.fetch_charges_by_house_id(house.id)
            rent_charges = []
            for charge in all_charges:
                if str(charge) == "Rent" and charge.date.month == month and charge.date.year == year:
                    checker = "exists"
                    break


            if checker:
                print("Skipping",house.name, "of",house.apartment,"rent charging",rent_charge,"exists")
                continue

            else:
                print(">>>>>>>>> Charging",house.name, "of",house.apartment,"rent")
                date = generate_date(month,year)
                rent_charge_obj = ChargeOp(charge_type_id,rent_charge,apartment_id,house_id,user_id,date)
                rent_charge_obj.save()

def garbage_bill(apartment_id,houseids,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)

    house_list = []
    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            house_list.append(hse)
    else:
        house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        garbage_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied" or house.owner:
            if not house.billable:
                garbage_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue
                garbage_charge = house.housecode.garbagerate

            all_charges = ChargeOp.fetch_charges_by_house_id(house_id)
            for charge in all_charges:
                if str(charge) == "Garbage" and charge.date.month == month and charge.date.year == year:
                    if charge.amount == 0.0:
                        print("deleting zero charged garbage obj")
                        ChargeOp.delete(charge)
                    else:
                        checker = "exists"
                        break

            if checker:
                print("Skipping",house.name, "of",house.apartment,"garbage charging",garbage_charge,"exists")
                continue
            else:
                print(">>>>>>>>> Charging",house.name, "of",house.apartment,"garbage")
                date = generate_date(month,year)
                garbage_charge_obj = ChargeOp(charge_type_id,garbage_charge,apartment_id,house_id,user_id,date)
                garbage_charge_obj.save()

def fixed_water_bill(apartment_id,houseids,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)

    house_list = []
    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            house_list.append(hse)
    else:
        house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        fixed_water_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied" or house.owner:
            if not house.billable:
                fixed_water_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue

                fixed_water_charge = house.housecode.watercharge if house.housecode.watercharge else 0.0

            all_charges = ChargeOp.fetch_charges_by_house_id(house_id)

            for charge in all_charges:
                if str(charge) == "Water" and charge.date.month == month and charge.date.year == year and not charge.reading_id:
                    if charge.amount == 0.0:
                        print("deleting zero charged fixed water obj")
                        ChargeOp.delete(charge)
                    else:
                        checker = "exists"
                        break


            if checker:
                print("Skipping",house.name, "of",house.apartment,"fixed_water charging",fixed_water_charge,"exists")
                continue
            else:
                print(">>>>>>>>> Charging",house.name, "of",house.apartment,"fixed_water_charge")
                date = generate_date(month,year)
                water_charge_obj = ChargeOp(charge_type_id,fixed_water_charge,apartment_id,house_id,user_id,date)
                water_charge_obj.save()

def electricity_bill(apartment_id,houseids,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)#get apartment obj first
    # meter_readings = apartment_obj.meter_readings
    target_readings = []

    house_list = []

    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            house_list.append(hse)
    else:
        house_list = houseauto(apartment_id)

    for h in house_list:
        meter_readings = h.meter_readings

        for item in meter_readings:
            if item.reading_period:
                if item.reading_period.month == month and item.reading_period.year == year and item.description == "actual electricity reading":
                    target_readings.append(item)

    for i in target_readings:
        units = i.units
        reading_id= i.id
        apartment_id = i.apartment_id
        house_id = i.house_id
        meter_id = i.meter_id
        house_obj = HouseOp.fetch_house_by_id(house_id)
        if not house_obj.housecode:
            print("HOUSE GROUP MISSING FOR: ",house_obj,"of",house_obj.apartment)
            continue
        unitcost = house_obj.housecode.electricityrate if house_obj.housecode.electricityrate else 0.0
        bill_amount = units*unitcost

        existing_charge_obj=ChargeOp.fetch_charge_by_reading_id(reading_id)
        # if existing_charge_obj:
        #     ChargeOp.delete(existing_charge_obj)
        if not existing_charge_obj:
            date = generate_date(month,year)
            house_obj = HouseOp.fetch_house_by_id(house_id)
            if house_obj:
                if not house_obj.billable:
                    charge_obj =  ChargeOp(charge_type_id,0.0,apartment_id,house_id,user_id,date,meter_id,reading_id)#REFACTOR meter can be left out for rent,garbage and security
                    charge_obj.save()
                    charge_status = True

                    MeterReadingOp.update_charge_status(i,charge_status)
                else:
                    charge_obj =  ChargeOp(charge_type_id,bill_amount,apartment_id,house_id,user_id,date,meter_id,reading_id)#REFACTOR meter can be left out for rent,garbage and security
                    charge_obj.save()
                    charge_status = True
                    print("Billing electricity for >>>",house_obj.name, "of",house_obj.apartment,"Amount >>>",bill_amount)

                    MeterReadingOp.update_charge_status(i,charge_status)

def security_bill(apartment_id,houseids,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)

    house_list = []
    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            house_list.append(hse)
    else:
        house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        security_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied" or house.owner:

            if not house.billable:
                security_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue

                security_charge = house.housecode.securityrate

            all_charges = ChargeOp.fetch_charges_by_house_id(house_id)
            for charge in all_charges:
                if str(charge) == "Security" and charge.date.month == month and charge.date.year == year:
                    if charge.amount == 0.0:
                        print("deleting zero charged security obj")
                        ChargeOp.delete(charge)
                    else:
                        checker = "exists"
                        break

            if checker:
                print("Skipping",house.name, "of",house.apartment,"security charging",security_charge,"exists")
                continue
            else:
                print(">>>>>>>>> Charging",house.name, "of",house.apartment,"security")
                
                date = generate_date(month,year)
                security_charge_obj = ChargeOp(charge_type_id,security_charge,apartment_id,house_id,user_id,date)
                security_charge_obj.save()

def maintenance_bill(apartment_id,houseids,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)#get apartment obj first
    tenantrequests = apartment_obj.tenantrequests #meter_readings list objects in a particular apartment
    for req in tenantrequests:
        if req.state:
            if req.status == "completed":
                if req.cost > 0.0:
                    cost = req.cost
                    apartment_id = req.apartment_id
                    house_id = req.house_id
                    date = generate_date(month,year)
                    charge_obj =  ChargeOp(charge_type_id,cost,apartment_id,house_id,user_id,date)#REFACTOR meter can be left out for rent,garbage and security
                    charge_obj.save()

                    state = False
                    TenantRequestOp.update_state(req,state)

    house_list = []

    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            house_list.append(hse)
    else:
        house_list = houseauto(apartment_id)


    for house in house_list:
        house_id = house.id
        checker = None
        service_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied" or house.owner:

            if not house.billable:
                service_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue

                raw_service_charge = house.housecode.servicerate if house.housecode.servicerate else 0.0

                if house.housecode.billfrequency:
                    billfreq = house.housecode.billfrequency
                else:
                    billfreq = 1


                if billfreq == 12:
                    months_to_bill = [1]
                elif billfreq == 6:
                    months_to_bill = [1,7]
                elif billfreq == 3:
                    months_to_bill = [1,4,7,10]
                else:
                    months_to_bill = [1,2,3,4,5,6,7,8,9,10,11,12]

                if month in months_to_bill:
                    service_charge = raw_service_charge * billfreq
                else:
                    service_charge = 0.0

                
            all_charges = ChargeOp.fetch_charges_by_house_id(house_id)

            accepted = True
            if not accepted:
                pass
            else:
                for charge in all_charges:
                    if str(charge) == "Maintenance" and charge.date.month == month and charge.date.year == year:
                        if charge.amount == 0.0:
                            print("deleting zero charged service charge obj")
                            ChargeOp.delete(charge)
                        else:
                            checker = "exists"
                            break

                if checker:
                    print("Skipping",house.name, "of",house.apartment,"service charging",service_charge,"exists")
                    continue
                else:
                    print(">>>>>>>>> Charging",house.name, "of",house.apartment,"service")
                    date = generate_date(month,year)
                    service_charge_obj = ChargeOp(charge_type_id,service_charge,apartment_id,house_id,user_id,date)
                    service_charge_obj.save()

def total_bill(apartment_id,houseids,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    user = UserOp.fetch_user_by_id(user_id)
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)

    print("BILLING FOR",month,year)
    print("BILLING PROP",apartment_obj.name)
    print("Current billing period is",apartment_obj.billing_period.date())

    co = user.company
    if apartment_obj.billing_period.month != month or apartment_obj.billing_period.year != year: # TO DO
        print(">>>>>UPDATING BILLING PERIOD ONCE")
        billing_period = generate_date(month,year)
        CompanyOp.update_billing_period(co,billing_period)
        ApartmentOp.update_billing_period(apartment_obj,billing_period)
        print("AFTER billing period is",apartment_obj.billing_period.date())

    prop = apartment_obj.name
    houses = []

    if houseids:
        for i in houseids:
            hse = HouseOp.fetch_house_by_id(i)
            houses.append(hse)
    else:
        houses = apartment_obj.houses

    try:
        # with mail.connect() as conn:
        print ("Billing has started with mail connected successfully")
        for house in houses:

            if apartment_obj.company.ctype == "crm":
                project_end_date = house.owner.checkin + relativedelta(months=15)
                deposit1 = house.owner.deposit
                booking = house.owner.deposit
                checkin = house.owner.checkin
                instalment = house.owner.instalment * house.owner.num_instalment

                # if house.description.upper() == "STUDIO":
                #     addfee = 123380.0
                # else:
                #     addfee = 192380.0

                addfee = 0.0

                mi = house.owner.instalment
                months = house.owner.num_instalment
                negprice = house.owner.negotiated_price

                instalment_schedules = list(range(1,(months+1)))

                initial_deposit_schedule = PaymentScheduleOp("Deposit",0.0,deposit1,deposit1,negprice,checkin,apartment_id,house.id,house.owner.id)
                initial_deposit_schedule.save()

                for sch in instalment_schedules:
                    sch_date = checkin + relativedelta(months=sch)
                    sch = PaymentScheduleOp("Instalment" + str(sch),0.0,mi,mi,0.0,sch_date,apartment_id,house.id,house.owner.id)
                    sch.save()

                others = f"40% Legal fees,Stamp Duty,service charge etc.)"

                legal_fee_schedule = PaymentScheduleOp(others,0.0,addfee,addfee,0.0,project_end_date,apartment_id,house.id,house.owner.id)
                legal_fee_schedule.save()

            else:
                booking = 0.0
                instalment = 0.0
                addfee = 0.0

            all_charges = house.charges

            charges = []
            for charge in all_charges:
                if charge.date.month == month and charge.date.year == year:
                    charges.append(charge)

            water_total = 0
            temp_water_total = 0
            water_bal = 0
            water_due = 0

            rent = 0
            rent_bal = 0
            rent_due = 0

            garbage = 0
            garbage_bal = 0
            garbage_due = 0

            electricity = 0
            electricity_bal = 0
            electricity_due = 0

            security = 0
            security_bal = 0
            security_due = 0

            maintenance = 0
            temp_maintenance_total = 0
            maintenance_bal = 0
            maintenance_due = 0

            fines = 0
            fines_bal = 0
            fines_due = 0

            deposit = 0
            deposit_bal = 0
            deposit_due = 0

            agreement = 0
            agreement_bal = 0
            agreement_due = 0

            print("######################################### START OF HOUSE",prop,house,month,year,"BILLING ###############################################")
            for i in charges:
                if i.charge_type_id == 2 and not i.compiled:
                    water_total += i.amount
                    ChargeOp.update_compiled_status(i,True)

                elif i.charge_type_id == 3 and not i.compiled:
                    rent += i.amount 
                    ChargeOp.update_compiled_status(i,True)

                elif i.charge_type_id == 4 and not i.compiled:
                    garbage += i.amount
                    ChargeOp.update_compiled_status(i,True)

                elif i.charge_type_id == 5 and not i.compiled:
                    electricity += i.amount
                    ChargeOp.update_compiled_status(i,True)

                elif i.charge_type_id == 6 and not i.compiled:
                    security += i.amount
                    ChargeOp.update_compiled_status(i,True)

                elif i.charge_type_id == 7 and not i.compiled:
                    maintenance += i.amount
                    ChargeOp.update_compiled_status(i,True)
                
                print('>>>>>>>',i,i.house,i.amount, 'Consumed? ',i.compiled,)

            print("MAINTENANCE AT THE START:>>>",maintenance)

                
            house_id = house.id
            result = check_occupancy(house)
            tenant = None


            if result[0] == "occupied":
                tenant = result[1]

            if tenant or house.owner:
                print("OWNER:",house.owner)
                print("TENANT:",tenant)
            else:
                print("BILLING SKIPPED FOR VACANT UNIT TENANT:",tenant,"OWNER",house.owner)
                continue

            bills = house.monthlybills

            if tenant:
                print("starting tenant billing >>>>>",tenant.name)
                ptenant_id = None
                tenant_id = tenant.id

                prev_bill = fetch_tnt_prev_billing_period_bills_alt(month,year,bills,tenant.id)

                if prev_bill:
                    arrears = prev_bill[0].balance

                    if prev_bill[0].rent_due: #rent due of last period forms the base of arrears
                        rent_bal = prev_bill[0].rent_due
                        rent_due = rent_bal + rent
                    else:
                        rent_due = rent

                    if house.watertarget:
                        if house.watertarget == "tenant":
                            if prev_bill[0].water_due:
                                water_bal = prev_bill[0].water_due
                                water_due = water_bal + water_total
                            else:
                                water_due = water_total
                        else:
                            water_bal = 0.0
                            water_due = 0.0
                    else:
                        if prev_bill[0].water_due:
                            water_bal = prev_bill[0].water_due
                            water_due = water_bal + water_total
                        else:
                            water_due = water_total  


                    if house.servicetarget:
                        if house.servicetarget == "tenant":
                            if prev_bill[0].maintenance_due:
                                maintenance_bal = prev_bill[0].maintenance_due
                                maintenance_due = maintenance_bal + maintenance
                            else:
                                maintenance_due = maintenance
                        else:
                            maintenance_bal = 0.0
                            maintenance_due = 0.0
                    else:
                        if prev_bill[0].maintenance_due:
                            maintenance_bal = prev_bill[0].maintenance_due
                            maintenance_due = maintenance_bal + maintenance
                        else:
                            maintenance_due = maintenance


                    if prev_bill[0].garbage_due:
                        garbage_bal = prev_bill[0].garbage_due
                        garbage_due = garbage_bal + garbage
                    else:
                        garbage_due = garbage

                    if prev_bill[0].security_due:
                        security_bal = prev_bill[0].security_due
                        security_due = security_bal + security
                    else:
                        security_due = security

                    if prev_bill[0].electricity_due:
                        electricity_bal = prev_bill[0].electricity_due
                        electricity_due = electricity_bal + electricity
                    else:
                        electricity_due = electricity

                    if prev_bill[0].penalty_due:
                        penalty_bal = prev_bill[0].penalty_due
                        fines_due = penalty_bal + fines
                    else:
                        fines_due = fines

                    if prev_bill[0].deposit_due:
                        deposit_bal = prev_bill[0].deposit_due
                        deposit_due = deposit_bal + deposit
                    else:
                        deposit_due = deposit

                    if prev_bill[0].agreement_due:
                        agreement_bal = prev_bill[0].agreement_due
                        agreement_due = agreement_bal + agreement
                    else:
                        agreement_due = agreement

                else:
                    arrears = 0.0

                    if house.watertarget:
                        if house.watertarget == "tenant":
                            water_due = water_total
                        else:
                            water_due = 0.0
                    else:
                        water_due = water_total

                    if house.servicetarget:
                        if house.servicetarget == "tenant":    
                            maintenance_due = maintenance
                        else:
                            maintenance_due = 0.0
                    else:
                        maintenance_due = maintenance

                    rent_due = rent

                    garbage_due = garbage

                    electricity_due = electricity

                    security_due = security

                    fines_due = fines

                    deposit_due = deposit

                    agreement_due = agreement


                if tenant.accumulated_fine:
                    print("Calculating fines for ",house)
                    fines = tenant.accumulated_fine
                    TenantOp.update_fine(tenant,0.0)

                new_tenants = new_tenants_injector(apartment_obj.id,month,year)

                if tenant in new_tenants:
                    carddep = house.housecode.carddep if house.housecode.carddep else 0.0
                    nodiscount = house.housecode.discount if house.housecode.discount else 0.0
                    deposit = house.housecode.rentrate + house.housecode.waterdep + house.housecode.elecdep + carddep + nodiscount
                    agreement = apartment_obj.agreement_fee if apartment_obj.agreement_fee else 0.0 #TODO


                if house.watertarget:
                    if house.watertarget == "tenant":
                        temp_water_total = water_total
                    else:
                        temp_water_total = water_total
                        water_total = 0.0
                else:
                    temp_water_total = water_total


                if house.servicetarget:
                    if house.servicetarget == "tenant":
                        temp_maintenance_total = maintenance
                    else:
                        temp_maintenance_total = maintenance
                        maintenance = 0.0
                else:
                    temp_maintenance_total = maintenance


                total_amount = water_total+rent+garbage+electricity+security+fines+arrears+deposit+agreement+maintenance+booking+instalment

                c_charge = None
                
                for bill in bills:
                    if bill.month == month and bill.year == year and bill.tenant_id == tenant.id:
                        print("Retrieving current bill for month of :",bill.month,"/",bill.year)
                        c_charge = bill
                
                if c_charge:
                    print("specific charge found for HOUSE",house)

                    update_water = c_charge.water
                    update_water += water_total
                    update_water_due = c_charge.water_due if c_charge.water_due else 0.0
                    update_water_due += water_total

                    update_rent = c_charge.rent
                    update_rent += rent
                    update_rent_due = c_charge.rent_due if c_charge.rent_due else 0
                    update_rent_due += rent

                    update_garbage = c_charge.garbage
                    update_garbage += garbage
                    update_garbage_due = c_charge.garbage_due if c_charge.garbage_due else 0
                    update_garbage_due += garbage

                    update_electricity = c_charge.electricity
                    update_electricity += electricity
                    update_electricity_due = c_charge.electricity_due if c_charge.electricity_due else 0                          
                    update_electricity_due += electricity

                    update_security = c_charge.security
                    update_security += security
                    update_security_due = c_charge.security_due if c_charge.security_due else 0
                    update_security_due += security

                    update_maintenance = c_charge.maintenance
                    update_maintenance += maintenance
                    update_maintenance_due = c_charge.maintenance_due if c_charge.maintenance_due else 0
                    update_maintenance_due += maintenance

                    update_penalty = c_charge.penalty
                    update_penalty += fines
                    update_penalty_due = c_charge.penalty_due if c_charge.penalty_due else 0
                    update_penalty_due += fines

                    const_arrears = c_charge.arrears

                    const_deposit = c_charge.deposit if c_charge.deposit else 0.0
                    const_deposit_due = c_charge.deposit_due if c_charge.deposit_due else 0.0

                    const_agreement = c_charge.agreement if c_charge.agreement else 0.0
                    const_agreement_due = c_charge.agreement_due if c_charge.agreement_due else 0.0

                    total_amount = update_water+update_rent+update_garbage+update_electricity+update_security+update_maintenance+update_penalty+const_arrears + const_deposit + const_agreement #total amount is incremented only by updates

                    MonthlyChargeOp.update_monthly_charge(c_charge,update_water,update_rent,update_garbage,update_electricity,update_security,const_deposit,const_agreement,update_maintenance,update_penalty,const_arrears,total_amount,user_id)
                    MonthlyChargeOp.update_dues(c_charge,0.0,0.0,0.0,update_rent_due,update_water_due,update_electricity_due,update_garbage_due,update_security_due,update_maintenance_due,update_penalty_due,const_deposit_due,const_agreement_due)

                    running_bal = tenant.balance
                    running_bal = running_bal + water_total+rent+garbage+electricity+security+maintenance+fines #these are updates, if one has update, the rest are zeros
                    TenantOp.update_balance(tenant,running_bal)

                    bal = c_charge.balance
                    bal = bal + water_total+rent+garbage+electricity+security+maintenance+fines #these are updates, if one has update, the rest are zeros
                    MonthlyChargeOp.update_balance(c_charge,bal)

                    if c_charge.paid_amount:
                        if c_charge.paid_amount < 0:
                            MonthlyChargeOp.update_payment(c_charge,0.0)
                            bala = total_amount
                        else:
                            bala = total_amount - c_charge.paid_amount
                    else:
                        bala = total_amount

                    MonthlyChargeOp.update_balance(c_charge,bala)

                    db.session.expire(c_charge)
                    
                    bill_balance = c_charge.balance
                    print(c_charge.month,c_charge.year,"KES",c_charge.balance)

                    TenantOp.update_balance(tenant,bill_balance)
                    db.session.expire(tenant)
                    print("Balance updated! now",tenant.balance)

                else:
                    print("TENANT BILLING CREATED >>>>>>>> specific charge not found") #TODO

                    monthly_charge_obj = MonthlyChargeOp(year,month,booking,instalment,addfee,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,ptenant_id,user_id)
                    monthly_charge_obj.save()

                    # monthly_charge_obj_alt = MonthlyChargeHistoryOp(year,month,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,monthly_charge_obj.id,user_id)
                    # monthly_charge_obj_alt.save()

                    MonthlyChargeOp.update_balances(monthly_charge_obj,0.0,0.0,0.0,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                    MonthlyChargeOp.update_dues(monthly_charge_obj,0.0,0.0,0.0,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)

                    # MonthlyChargeHistoryOp.update_balances(monthly_charge_obj_alt,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                    # MonthlyChargeHistoryOp.update_dues(monthly_charge_obj_alt,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)
                    
                    running_bal = tenant.balance
                    running_bal += total_amount

                    if tenant.multiple_houses:
                        TenantOp.update_balance(tenant,running_bal)
                    else:
                        TenantOp.update_balance(tenant,total_amount)

                    bal = monthly_charge_obj.balance
                    bal += total_amount
                    MonthlyChargeOp.update_balance(monthly_charge_obj,bal)

                    if not house.billable:
                        print("House",house,"is not billablle")

            else:
                temp_water_total = water_total
                temp_maintenance_total = maintenance

            #reset to default values
            water_total = temp_water_total
            maintenance = temp_maintenance_total

            print("Printing stored data","SERVICE:",maintenance,"WATER:",water_total)

            if house.owner:
                print("Starting OWNER BILLING >>",house.owner.name)
                tenant = house.owner
                ptenant_id = tenant.id
                tenant_id = None

                prev_bill = fetch_pt_prev_billing_period_bills(month,year,bills,tenant.id)

                if prev_bill:
                    arrears = prev_bill[0].balance
                    print("FOUND PREVIOUS BILL WITH ARREARS OF: ",arrears)

                    if prev_bill[0].rent_due: #rent due of last period forms the base of arrears
                        rent_bal = prev_bill[0].rent_due
                        rent_due = rent_bal + rent
                    else:
                        rent_due = rent

                    # rent_bal = 0.0
                    # rent_due = 0.0

                    if house.watertarget:
                        if house.watertarget == "owner":
                            if prev_bill[0].water_due:
                                water_bal = prev_bill[0].water_due
                                water_due = water_bal + water_total
                            else:
                                water_due = water_total
                        else:
                            water_bal = 0.0
                            water_due = 0.0
                    else:
                        if prev_bill[0].water_due:
                            water_bal = prev_bill[0].water_due
                            water_due = water_bal + water_total
                        else:
                            water_due = water_total  


                    if house.servicetarget:
                        if house.servicetarget == "owner":
                            if prev_bill[0].maintenance_due:
                                maintenance_bal = prev_bill[0].maintenance_due
                                maintenance_due = maintenance_bal + maintenance
                            else:
                                maintenance_due = maintenance
                        else:
                            maintenance_bal = 0.0
                            maintenance_due = 0.0
                    else:
                        if prev_bill[0].maintenance_due:
                            maintenance_bal = prev_bill[0].maintenance_due
                            maintenance_due = maintenance_bal + maintenance
                        else:
                            maintenance_due = maintenance


                    if prev_bill[0].garbage_due:
                        garbage_bal = prev_bill[0].garbage_due
                        garbage_due = garbage_bal + garbage
                    else:
                        garbage_due = garbage

                    if prev_bill[0].security_due:
                        security_bal = prev_bill[0].security_due
                        security_due = security_bal + security
                    else:
                        security_due = security

                    if prev_bill[0].electricity_due:
                        electricity_bal = prev_bill[0].electricity_due
                        electricity_due = electricity_bal + electricity
                    else:
                        electricity_due = electricity

                    if prev_bill[0].penalty_due:
                        penalty_bal = prev_bill[0].penalty_due
                        fines_due = penalty_bal + fines
                    else:
                        fines_due = fines

                    if prev_bill[0].deposit_due:
                        deposit_bal = prev_bill[0].deposit_due
                        deposit_due = deposit_bal + deposit
                    else:
                        deposit_due = deposit

                    if prev_bill[0].agreement_due:
                        agreement_bal = prev_bill[0].agreement_due
                        agreement_due = agreement_bal + agreement
                    else:
                        agreement_due = agreement

                else:
                    arrears = 0.0

                    if house.watertarget:
                        if house.watertarget == "owner":
                            water_due = water_total
                        else:
                            water_due = 0.0
                    else:
                        water_due = water_total

                    print("at this point the service charge is:",maintenance)

                    if house.servicetarget:
                        if house.servicetarget == "owner":    
                            maintenance_due = maintenance
                        else:
                            maintenance_due = 0.0
                    else:
                        maintenance_due = maintenance

                    rent_due = rent

                    garbage_due = garbage

                    electricity_due = electricity

                    security_due = security

                    fines_due = fines

                    deposit_due = deposit

                    agreement_due = agreement


                if house.watertarget:
                    if house.watertarget == "owner":
                        pass
                    else:
                        water_total = 0.0
                else:
                    pass

                if house.servicetarget:
                    if house.servicetarget == "owner":
                        pass
                    else:
                        maintenance = 0.0
                else:
                    pass

                total_amount = water_total+garbage+electricity+security+fines+arrears+maintenance+booking+instalment+addfee

                c_charge = None
                
                for bill in bills:
                    if bill.month == month and bill.year == year and bill.ptenant_id == ptenant_id:
                        print("Retrieving current bill for month of :",bill.month,"/",bill.year)
                        c_charge = bill
                
                if c_charge:
                    # if apartment_obj.company.name == "REVER MWIMUTO LIMITED":
                    if apartment_obj.company.ctype == "crm":
                        continue
                    print("specific charge found for HOUSE",house)

                    update_water = c_charge.water
                    update_water += water_total
                    update_water_due = c_charge.water_due if c_charge.water_due else 0.0
                    update_water_due += water_total

                    update_rent = c_charge.rent
                    update_rent += rent
                    update_rent_due = c_charge.rent_due if c_charge.rent_due else 0
                    update_rent_due += rent

                    update_garbage = c_charge.garbage
                    update_garbage += garbage
                    update_garbage_due = c_charge.garbage_due if c_charge.garbage_due else 0
                    update_garbage_due += garbage

                    update_electricity = c_charge.electricity
                    update_electricity += electricity
                    update_electricity_due = c_charge.electricity_due if c_charge.electricity_due else 0                          
                    update_electricity_due += electricity

                    update_security = c_charge.security
                    update_security += security
                    update_security_due = c_charge.security_due if c_charge.security_due else 0
                    update_security_due += security

                    update_maintenance = c_charge.maintenance
                    update_maintenance += maintenance
                    update_maintenance_due = c_charge.maintenance_due if c_charge.maintenance_due else 0
                    update_maintenance_due += maintenance

                    update_penalty = c_charge.penalty
                    update_penalty += fines
                    update_penalty_due = c_charge.penalty_due if c_charge.penalty_due else 0
                    update_penalty_due += fines

                    const_arrears = c_charge.arrears

                    const_deposit = c_charge.deposit if c_charge.deposit else 0.0
                    const_deposit_due = c_charge.deposit_due if c_charge.deposit_due else 0.0

                    const_agreement = c_charge.agreement if c_charge.agreement else 0.0
                    const_agreement_due = c_charge.agreement_due if c_charge.agreement_due else 0.0

                    total_amount = update_water+update_rent+update_garbage+update_electricity+update_security+update_maintenance+update_penalty+const_arrears + const_deposit + const_agreement #total amount is incremented only by updates

                    MonthlyChargeOp.update_monthly_charge(c_charge,update_water,update_rent,update_garbage,update_electricity,update_security,const_deposit,const_agreement,update_maintenance,update_penalty,const_arrears,total_amount,user_id)
                    MonthlyChargeOp.update_dues(c_charge,0.0,0.0,0.0,update_rent_due,update_water_due,update_electricity_due,update_garbage_due,update_security_due,update_maintenance_due,update_penalty_due,const_deposit_due,const_agreement_due)

                    running_bal = tenant.balance
                    running_bal = running_bal + water_total+rent+garbage+electricity+security+maintenance+fines #these are updates, if one has update, the rest are zeros
                    PermanentTenantOp.update_balance(tenant,running_bal)

                    bal = c_charge.balance
                    bal = bal + water_total+rent+garbage+electricity+security+maintenance+fines #these are updates, if one has update, the rest are zeros
                    MonthlyChargeOp.update_balance(c_charge,bal)

                    if c_charge.paid_amount:
                        if c_charge.paid_amount < 0:
                            MonthlyChargeOp.update_payment(c_charge,0.0)
                            bala = total_amount
                        else:
                            bala = total_amount - c_charge.paid_amount
                    else:
                        bala = total_amount

                    MonthlyChargeOp.update_balance(c_charge,bala)

                    db.session.expire(c_charge)
                    
                    bill_balance = c_charge.balance
                    print(c_charge.month,c_charge.year,"KES",c_charge.balance)

                    PermanentTenantOp.update_balance(tenant,bill_balance)
                    db.session.expire(tenant)
                    print("Balance updated! now",tenant.balance)

                else:
                    print("RESIDENT BILLING CREATED >>>>>>>> specific charge not found") #TODO
                    monthly_charge_obj = MonthlyChargeOp(year,month,booking,instalment,addfee,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,ptenant_id,user_id)
                    monthly_charge_obj.save()

                    print("BILLLLL>>>",monthly_charge_obj.maintenance,"<<<<<<<<<",monthly_charge_obj)

                    # monthly_charge_obj_alt = MonthlyChargeHistoryOp(year,month,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,monthly_charge_obj.id,user_id)
                    # monthly_charge_obj_alt.save()

                    MonthlyChargeOp.update_balances(monthly_charge_obj,0.0,0.0,0.0,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                    MonthlyChargeOp.update_dues(monthly_charge_obj,booking,instalment,addfee,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)

                    # MonthlyChargeHistoryOp.update_balances(monthly_charge_obj_alt,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                    # MonthlyChargeHistoryOp.update_dues(monthly_charge_obj_alt,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)
                    
                    running_bal = tenant.balance
                    running_bal += total_amount


                    if tenant.multiple_houses:
                        PermanentTenantOp.update_balance(tenant,running_bal)
                    else:
                        PermanentTenantOp.update_balance(tenant,total_amount)

                    bal = monthly_charge_obj.balance
                    bal += total_amount
                    MonthlyChargeOp.update_balance(monthly_charge_obj,bal)

                    if not house.billable:
                        print("House",house,"is not billablle")

                    print("######################################### END OF HOUSE",prop,house,"BILLING ###############################################")

            else:
                print("BILLING SKIPPED FOR NEITHER OWNED NOR RENTED UNIT (VACANT)")

        ApartmentOp.update_billing_progress(apartment_obj,"completed")







    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Biling Failed >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        ApartmentOp.update_billing_progress(apartment_obj,"failed")


        
def filtered_house_list(apartment_id,readdate=None):
    """Filtering out read houses"""
    unread_houses = []
    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
    house_list = filter_in_metered_houses(prop.name)
    
    # period = current_user.company.billing_period.month
    billing_period = prop.billing_period
    
    if readdate:
        if readdate.month == billing_period.month and readdate.year == billing_period.year:
            month = billing_period.month
            year = billing_period.year
        else:
            month = billing_period.month + 1 if billing_period.month != 12 else 1
            year = billing_period.year if billing_period.month != 12 else billing_period.year + 1
    else: 
        if datetime.datetime.now().day < 21 and datetime.datetime.now().month == billing_period.month:
            #Only enters this block for readings taken after billing and are meant for the same period as the current bills. next month of billing
            print("Reading left out captured")

            month = billing_period.month
            year = billing_period.year

        elif datetime.datetime.now().day >= 21:
            #Only enters this block if readings are taken early before the next month of billing

            if datetime.datetime.now().month != 12:
                if datetime.datetime.now().month + 1 == billing_period.month:

                    #Only enters this block for readings taken early and are meant for early next current billing
                    print("Reading left out captured for next month")
                    month = billing_period.month
                    year = billing_period.year

                else:
                    #Only enters this block for early billing COMMON PROCESS
                    print("Reading captured early and normally for next period")
                    month = billing_period.month + 1 if billing_period.month != 12 else 1
                    year = billing_period.year if billing_period.month != 12 else billing_period.year + 1
            else:
                if 1 == billing_period.month:
                    print("Reading left out captured for Jan ater early billing for Jan")
                    month = billing_period.month
                    year = billing_period.year
                else:
                    #Only enters this block for early billing COMMON PROCESS
                    print("Reading captured early and normally for Jan")
                    month = 1
                    year = billing_period.year + 1
        else:
            #Only enters this block if readings are taken early in the next month of billing
            print("Reading captured late")
            if billing_period.month == 12:
                month = 1
                year = billing_period.year + 1

            else:
                month = billing_period.month + 1 if billing_period.month != 12 else 1
                year = billing_period.year if billing_period.month != 12 else billing_period.year + 1

    for house in house_list:
        active_meter = fetch_active_meter(house)
        prev_reading_obj = fetch_last_reading(active_meter.id)
        # print("Prev reading period",prev_reading_obj.reading_period.month,"")

        if prev_reading_obj.reading_period.month == month and prev_reading_obj.reading_period.year == year:
            if prev_reading_obj.description == "actual water reading":
                pass
            else:
                unread_houses.append(house)
        else:

            unread_houses.append(house)


        # if prev_reading_obj.reading_period and prev_reading_obj.description != "initial reading" and prev_reading_obj.description != "actual electricity reading":
        #     print("there",house,prev_reading_obj.reading_period)
        #     if prev_reading_obj:
        #         if prev_reading_obj.reading_period.month != period: #if diff value is compared against 0, reading will only be done once a month 
        #             unread_houses.append(house)
        # else:
        #     unread_houses.append(house)

    return unread_houses

def filtered_house_list_alt(apartment_id,readdate=None):
    """Filtering out read houses"""
    unread_houses = []
    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
    house_list = filter_in_metered_houses_alt(prop.name)
    
    period = prop.billing_period.month
    current_month = datetime.datetime.now().month

    if period != 12:
        if datetime.datetime.now().day < 21 and current_month == period:
            period = period
        else:
            period += 1
    else:
        if datetime.datetime.now().day < 21 and current_month == period:
            period = 12
        else:
            period = 1

    for house in house_list:
        active_meter = fetch_active_meter_alt(house)
        prev_reading_obj = fetch_last_reading(active_meter.id)
        # print("Prev reading period",prev_reading_obj.reading_period.month)
        
        if prev_reading_obj.reading_period.month == period:
            if prev_reading_obj.description == "actual electricity reading":
                pass
            else:
                unread_houses.append(house)
        else:
            unread_houses.append(house)

    return unread_houses

# def autoresolve_mpesa(ctob):
#     prop = ApartmentOp.fetch_apartment_by_shortcode(ctob.shortcode)

#     reference = ctob.trans_id
#     amountpaid = ctob.trans_amnt
#     narration = ctob.bill_ref_num.replace(" ","") if ctob.bill_ref_num else None

#     let bal = paid

#     let bookingdue = parseInt($("#bookingdue").val())
#     let instalmentdue = parseInt($("#instalmentdue").val())
#     let addfeedue = parseInt($("#addfeedue").val())

#     let rentdue = parseInt($("#rentdue").val())

#     let waterdue = parseInt($("#waterdue").val())
#     if (waterdue < 0){
#       waterdue = 0
#     }
#     let electricitydue = parseInt($("#electricitydue").val())
#     let garbagedue = parseInt($("#garbagedue").val())
#     let securitydue = parseInt($("#securitydue").val())
#     let servicedue = parseInt($("#servicedue").val())
#     let penaltydue = parseInt($("#penaltydue").val())
#     let depositdue = parseInt($("#depositdue").val())
#     let agreementdue = parseInt($("#agreementdue").val())


#     if (bal >= depositdue) {$("#depositpaid").val(depositdue);bal -= depositdue}else if (bal < depositdue && bal > 0) {$("#depositpaid").val(bal);bal = 0}else {$("#depositpaid").val(0.0)}

#     if (bal >= bookingdue) {$("#bookingpaid").val(bookingdue);bal -= bookingdue}else if (bal < bookingdue && bal > 0) {$("#bookingpaid").val(bal);bal = 0}else {$("#bookingpaid").val(0.0)}
#     if (bal >= instalmentdue) {$("#instalmentpaid").val(instalmentdue);bal -= instalmentdue}else if (bal < instalmentdue && bal > 0) {$("#instalmentpaid").val(bal);bal = 0}else {$("#instalmentpaid").val(0.0)}
#     if (bal >= addfeedue) {$("#addfeedue").val(addfeedue);bal -= addfeedue} else if (bal < addfeedue && bal > 0) {$("#addfeedue").val(bal);bal = 0}else {$("#addfeedue").val(0.0)}


#     if (bal >= rentdue) {$("#rentpaid").val(rentdue);bal -= rentdue}else if (bal < rentdue && bal > 0) {$("#rentpaid").val(bal);bal = 0}else {$("#rentpaid").val(0.0)}
#     if (bal >= penaltydue) {$("#penaltypaid").val(penaltydue);bal -= penaltydue}else if (bal < penaltydue && bal > 0) {$("#penaltypaid").val(bal);bal = 0}else {$("#penaltypaid").val(0.0)}

#     if (bal >= garbagedue) {$("#garbagepaid").val(garbagedue);bal -= garbagedue}else if (bal < garbagedue && bal > 0) {$("#garbagepaid").val(bal);bal = 0}else {$("#garbagepaid").val(0.0)}
#     if (bal >= securitydue) {$("#securitypaid").val(securitydue);bal -= securitydue}else if (bal < securitydue && bal > 0) {$("#securitypaid").val(bal);bal = 0}else {$("#securitypaid").val(0.0)}
#     if (bal >= servicedue) {$("#servicepaid").val(servicedue);bal -= servicedue}else if (bal < servicedue && bal > 0) {$("#servicepaid").val(bal);bal = 0}else {$("#servicepaid").val(0.0)}

#     if (bal >= waterdue) {$("#waterpaid").val(waterdue);bal -= waterdue}else if (bal < waterdue && bal > 0) {$("#waterpaid").val(bal);bal = 0}else {$("#waterpaid").val(0.0)}
#     if (bal >= electricitydue) {$("#electricitypaid").val(electricitydue);bal -= electricitydue}else if (bal < electricitydue && bal > 0) {$("#electricitypaid").val(bal);bal = 0}else {$("#electricitypaid").val(0.0)}

#     if (bal >= agreementdue) {$("#agreementpaid").val(agreementdue);bal -= agreementdue}else if (bal < agreementdue && bal > 0) {$("#agreementpaid").val(bal);bal = 0}else {$("#agreementpaid").val(0.0)}

#     if(bal){
#       $("#advancepay").removeClass("dispnone")
#       $("#advance_pay").val(bal)
#     }else{
#       $("#advancepay").addClass("dispnone")
#       $("#advance_pay").val(0.0)
#     }

#   })

#     bookingpaid = int(request.form.get('bookingpaid')) if request.form.get('bookingpaid') else 0
#     instalmentpaid = int(request.form.get('instalmentpaid')) if request.form.get('instalmentpaid') else 0
#     addfeepaid = int(request.form.get('addfeepaid')) if request.form.get('addfeepaid') else 0
#     rentpaid = int(request.form.get('rentpaid')) if request.form.get('rentpaid') else 0
#     waterpaid = int(request.form.get('waterpaid')) if request.form.get('waterpaid') else 0
#     electricitypaid = int(request.form.get('electricitypaid')) if request.form.get('electricitypaid') else 0
#     garbagepaid = int(request.form.get('garbagepaid')) if request.form.get('garbagepaid') else 0
#     securitypaid = int(request.form.get('securitypaid')) if request.form.get('securitypaid') else 0
#     servicepaid = int(request.form.get('servicepaid')) if request.form.get('servicepaid') else 0
#     penaltypaid = int(request.form.get('penaltypaid')) if request.form.get('penaltypaid') else 0
#     depositpaid = int(request.form.get('depositpaid')) if request.form.get('depositpaid') else 0
#     agreementpaid = int(request.form.get('agreementpaid')) if request.form.get('agreementpaid') else 0

#     cbid = request.form.get("cbid")

#     book = "Booking balance" if bookingpaid else ""
#     inst = "Instalment" if instalmentpaid else ""
#     addfee = "Additional fees" if addfeepaid else ""

#     water = "Water" if waterpaid else ""
#     rent = "Rent" if rentpaid else ""
#     garbage = "Garbage" if garbagepaid else ""
#     sec = "Security" if securitypaid else ""
#     arr = ""
#     dep = "Deposit" if depositpaid else ""
#     serv = "Service" if servicepaid else ""

#     narration = f"{rent} {water} {garbage} {sec} {serv} {dep} {book} {inst} {addfee}"

#     print(narration)

#     bank = request.form.get("bank")

#     payperiod = request.form.get("payperiod")
#     paydate = request.form.get("date")
#     paytime = request.form.get("time")

#     textsms = request.form.get("sms")
#     email = request.form.get("email")

#     sms_bool = get_bool(textsms)
#     email_bool = get_bool(email)

#     if payperiod:
#         pay_period = date_formatter_alt(payperiod)
#         pay_period_date = parse(pay_period)
#         current_period_payment = False
#     else:
#         current_period_payment = True
#         pay_period_date = get_billing_period(prop)

#     print("PAYPERIOOOOOOOD",pay_period_date)

#     if paydate:

#         formatted_paydate = date_formatter(paydate)

#         if paytime:
#             timestring = formatted_paydate + " " + paytime
#             pay_date = parse(timestring)
#         else:
#             pay_date = parse(formatted_paydate)

#     else:
#         pay_date = datetime.datetime.now()

#     paymode = request.form.get('paymode')#dropdown
#     raw_bill_ref = request.form.get('bill_ref')#typed
#     paytype = request.form.get('paytype')#typed
#     amount = request.form.get('paidamount')#typed
#     overpayment = int(request.form.get('overpayment')) if request.form.get('overpayment') else 0


#     valid_amount = validate_input(amount)

#     if not valid_amount:
#         return "<div class='center-btn text-danger text-xx'>Invalid amount !</div"

#     if raw_bill_ref.upper() == "N/A":
#         bill_ref = raw_bill_ref
#     elif raw_bill_ref.upper() == "NA":
#         bill_ref = "N/A"
#     elif len(raw_bill_ref) < 5:
#         bill_ref = raw_bill_ref
#     else:
#         bill_ref = raw_bill_ref
#         payob = PaymentOp.fetch_payment_by_ref(raw_bill_ref)
#         if payob:
#             if payob.voided:
#                 pass
#             else:
#                 print("REFERENCE EXISTS >>","MONTH:",payob.pay_period.month,"PROP:",payob.apartment,"TENANT & HOUSE:",payob.tenant,payob.house,"ID:",payob.id,"VOID:",payob.voided)
#                 return "<div class='center-btn text-danger text-xx'>Reference exists!</div"

#     ########################################################################################

#     skip = False

#     tenant_id = None
#     ptenant_id = None

#     period = pay_period_date

#     tenant_obj = None
#     co = prop.company
#     target_houses = []   

#     if cbid:
#         cb = CtoBop.fetch_record_by_id(cbid)

#         if cb.bill_ref_num:
#             # if cb.bill_ref_num.startswith("TNT"):
#             #     tenant_obj = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
#             #     house_obj = check_house_occupied(tenant_obj)[1]
#             #     target_houses.append(house_obj)
#             #     tenant_id = tenant_obj.id

#             #     print(">>>>> STARTING PAYMENT & TENANT TYPE")


#             # elif cb.bill_ref_num.startswith("WN"):
#             #     tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
#             #     house_obj = tenant_obj.house
#             #     target_houses.append(house_obj)
#             #     ptenant_id = tenant_obj.id

#             #     print(">>>>> STARTING PAYMENT & OWNER TYPE")

#             #######################################################################################
#             if cb.bill_ref_num.startswith("TNT"):
#                 tenant_obj = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
#                 if tenant_obj:
#                     house_obj = check_house_occupied(tenant_obj)[1]
#                     target_houses.append(house_obj)
#                     tenant_id = tenant_obj.id
#                     ptenant_id = None
#                 else:
#                     tenant_obj = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
#                     if tenant_obj:
#                         house_obj = check_house_occupied(tenant_obj)[1]
#                         target_houses.append(house_obj)
#                         tenant_id = tenant_obj.id
#                         ptenant_id = None
#                     else:
#                         print("TNT NOT FOUND")
#                         abort(404) 

#             elif cb.bill_ref_num.startswith("WN"):
#                 tenant_obj = PermanentTenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
#                 if tenant_obj:
#                     house_obj = tenant_obj.house
#                     target_houses.append(house_obj)
#                     ptenant_id = tenant_obj.id
#                     tenant_id = None
#                 else:
#                     tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
#                     if tenant_obj:
#                         house_obj = tenant_obj.house
#                         target_houses.append(house_obj)
#                         ptenant_id = tenant_obj.id
#                         tenant_id = None
#                     else:
#                         print("WN NOT FOUND")
#                         abort(404) 

#             ########################################################################################
#             elif prop.name == "Greatwall Gardens 2":
#                 hh = get_specific_house_obj(propid,cb.bill_ref_num)
#                 if hh:
#                     house_obj = hh
#                     target_houses.append(house_obj)
#                     tenant_obj = hh.owner
#                     tenant_id = None
#                     ptenant_id = tenant_obj.id
#                 else:
#                     print("HOUSE NOT FOUND")
#                     abort(404) 
#             elif prop.name == "Astrol Ridgeways":
#                 cbid_id = cb.bill_ref_num.replace(" ","")
#                 if "-" in cbid_id:
#                     cbid_id2 = cbid_id.split("-")[1]
#                 else:
#                     cbid_id2 = cbid_id
#                 tenant_obj = TenantOp.fetch_tenant_by_uid(cbid_id2.upper())
#                 if tenant_obj:
#                     house_obj = check_house_occupied(tenant_obj)[1]
#                     target_houses.append(house_obj)
#                     tenant_id = tenant_obj.id
#                     ptenant_id = None
#                 else:
#                     print("UID NOT FOUND")
#                     abort(404) 
#             ########################################################################################


#             else:
#                 skip = True
#     else:
#         skip = True



#     if skip:
#         print(">>>>> STARTING PAYMENT & SKIPPING")
#         if house_name:

#             if house_name2:

#                 if house_name2 == "none selected":
#                     return "<span class='text-danger text-xx'>Payment failed, please specify house!</span>"

#                 str_houses = house_name2.replace(","," ")
#                 houselist = list(str_houses.split(" "))

#                 for hse in houselist:
#                     hse_obj = get_specific_house_obj(propid,hse)
#                     target_houses.append(hse_obj)

#             else:
#                 hse_obj = get_specific_house_obj_from_house_tenant_alt_alt(propid,house_name)
#                 target_houses.append(hse_obj[0])

#             house_obj = target_houses[0]

#             try:
#                 if not house_name2:
#                     owner = get_specific_house_obj_from_house_tenant_alt_alt(propid,house_name)[1]
#                     if owner:
#                         tenant_obj = owner
#                         ptenant_id = tenant_obj.id

#                     else:
#                         tenant_obj = check_occupancy(house_obj)[1]
#                         tenant_id = tenant_obj.id
#                 else:
#                     tenant_obj = check_occupancy(house_obj)[1]
#                     tenant_id = tenant_obj.id

#             except:
#                 print("FORGOT TO SELECT HOUSE WHILE MAKING PAYMENT")
#                 abort(404) 


#             if not tenant_obj:
#                 print("FORGOT TO SELECT HOUSE WHILE MAKING PAYMENT")
#                 abort(404)

#         else:
#             print("FORGOT TO SELECT HOUSE WHILE MAKING PAYMENT")
#             abort(404)

#     tenant_name = tenant_obj.name

#     house_id = house_obj.id
#     created_by = current_user.id
#     chargetype_string = generate_string(water,rent,garbage,sec,arr,dep,serv)

#     if not narration:
#         narration = generate_string(water,rent,garbage,sec,arr,dep,serv)

#     # if aviv(current_user):
#     #     narration = get_str_month(period.month)

#     # monthly_charges = house_obj.monthlybills

#     if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
#         if tenant_obj.apartment.company.name == "REVER MWIMUTO LIMITED":
#             specific_charge_obj = tenant_obj.monthly_charges[0]
#         else:
#             specific_charge_obj = fetch_target_period_owner_invoice(house_obj,pay_period_date)
#     else:
#         specific_charge_obj = fetch_target_period_invoice(house_obj,pay_period_date)

#     schedule_obj = None

#     if tenant_obj.apartment.company.name == "REVER MWIMUTO LIMITED":
#         print("GONE TO PAY AVIV")
#         schedule_objs = tenant_obj.schedules
#         for sch in schedule_objs:
#             if sch.schedule_date.month == pay_period_date.month and sch.schedule_date.year == pay_period_date.year:
#                 schedule_obj = sch
#                 break

    
#     # if tenant_obj.tenant_type == "owner":
#     #     monthly_charges = tenant_obj.monthly_charges
#     # else:
#     #     monthly_charges = house_obj.monthlybills

#     # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,period.month,period.year)

#     # print("FOUND INV OF: ",specific_charge_obj.month,"/",specific_charge_obj.year,"amount due and bal:", specific_charge_obj.total_bill,"&",specific_charge_obj.balance)

#     bal = specific_charge_obj.balance

#     if tenant_obj.multiple_houses:
#         pass
#     else:
#         # monthly_charges = house_obj.monthlybills
#         # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,period.month)

#         if specific_charge_obj and current_period_payment and current_user.company.name != "MULTIDIME AGENCIES":
#             if specific_charge_obj.penalty:
#                 standard_pen = house_obj.housecode.rentrate*0.1
#                 accepted_balance = bal - 1000 - standard_pen
#                 if valid_amount > accepted_balance:
#                     if propid == 22:
#                         dday = 5
#                     else:
#                         dday = 11
#                     if pay_date.day < dday:
#                         print("Fine status for", house_obj, "before payment >>>>> ",specific_charge_obj.fine_status)
#                         bal -= specific_charge_obj.penalty
#                         TenantOp.update_balance(tenant_obj,bal)
#                         MonthlyChargeOp.update_balance(specific_charge_obj,bal)
#                         update_total = specific_charge_obj.total_bill - specific_charge_obj.penalty
#                         MonthlyChargeOp.update_monthly_charge(specific_charge_obj,"null","null","null","null","null","null","null","null",0.0,"null",update_total,None)
#                         MonthlyChargeOp.update_fine_status(specific_charge_obj,"nil")
#                         print("Fine status for", house_obj, "after payment >>>>> ",specific_charge_obj.fine_status)
#                     else:
#                         print("Paid late>>>>>>>>>>>")
#                 else:
#                     print("Paid little>>>>>>>>>>>")
#             else:
#                 print("No fines found>>>>>>>>>>>")
#         elif specific_charge_obj and not current_period_payment:
#             pass
#         else:
#             print("Not billed yet for ",get_str_month(period.month), ">>>>>>>>>>>")
            
#     if paymode == "mpesa":
#         description = "Manual Mpesa payment"
#     elif paymode == "bank":
#         description = bank if bank else None
#     else:
#         description = "Cash"
#         bill_ref = "N/A"
#     #######################################################################################
#     # pay_period = paid to which bills
#     # pay_date = alilipa lini?
    

#     payment_obj = PaymentOp(paymode,bill_ref,description,narration,pay_date,period,bal,valid_amount,propid, house_id,tenant_id,ptenant_id,created_by)
#     payment_obj.save()

#     if cbid:
#         cb = CtoBop.fetch_record_by_id(cbid)
#         CtoBop.update_status(cb,"claimed")

#     try:
#         cbdel = CtoBop.fetch_record_by_ref("QG63YENCLJ")
#         CtoBop.update_status(cbdel,"claimed")
#         cbdeel = CtoBop.fetch_record_by_ref("QG68YENDEU")
#         CtoBop.update_status(cbdeel,"claimed")
#     except:
#         pass

#     if co.receipt_num:
#         num = co.receipt_num
#         num += 1

#         CompanyOp.increment_receipt_num(co,num)
#         PaymentOp.update_receipt_num(payment_obj,num)
#     #################################################################################################

#     rand_id = random_generator()
#     if PaymentOp.fetch_payment_by_rand_id(rand_id):
#         rand_id = random_generator(size=11)
#         awe = sms.send("Ran random the second time !", ["+254716674695"],sender)
#         if PaymentOp.fetch_payment_by_rand_id(rand_id):
#             rand_id = random_generator(size=12)
#             awe = sms.send("Ran random the third time !", ["+254716674695"],sender)
#             if PaymentOp.fetch_payment_by_rand_id(rand_id):
#                 rand_id = random_generator(size=13)
#                 awe = sms.send("Ran random the fouth time !", ["+254716674695"],sender)
#                 if PaymentOp.fetch_payment_by_rand_id(rand_id):
#                     awe = sms.send("There is a problem with random, payment aborted !", ["+254716674695"],sender)
#                     return "Payment could not be processed at this time! Try again later"

#     tenant_bal = tenant_obj.balance
#     tenant_bal -= valid_amount
#     if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
#         PermanentTenantOp.update_balance(tenant_obj,tenant_bal)
#     else:
#         TenantOp.update_balance(tenant_obj,tenant_bal)

#     running_balance = bal
#     running_balance-= valid_amount

#     PaymentOp.update_balance(payment_obj,running_balance)
#     PaymentOp.update_rand_id(payment_obj,rand_id)

#     string_house = ""

#     for h in target_houses:

#         if schedule_obj:
#             print("SCHEDULE OBJI FOUND")
#             sch_arrears = 0.0
#             prev_sch = fetch_prev_schedule(pay_period_date.month,pay_period_date.year,tenant_obj.schedules,tenant_obj.id)
#             if prev_sch:
#                 print("FOUND Previous scheduled")
#                 sch_arr = prev_sch[0].balance
#                 if sch_arr:
#                     sch_arrears = sch_arr
#             if sch_arrears:
#                 sch_total_amount = schedule_obj.schedule_amount + sch_arrears
#             else:
#                 sch_total_amount = schedule_obj.schedule_amount

#             schpaid = schedule_obj.paid + valid_amount
            
#             sch_bal = sch_total_amount - schpaid

#             print("values",sch_arrears,sch_total_amount,valid_amount,sch_bal)

#             PaymentScheduleOp.update_details(schedule_obj,sch_arrears,sch_total_amount,schpaid,sch_bal,bill_ref,paytype,pay_date)
        


#         if specific_charge_obj:

#             db.session.expire(specific_charge_obj)
#             bala = specific_charge_obj.balance
#             bala-=valid_amount
#             MonthlyChargeOp.update_balance(specific_charge_obj,bala)

#             paid_amount = specific_charge_obj.paid_amount
#             cumulative_pay = paid_amount + valid_amount
#             MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
#             MonthlyChargeOp.update_payment_date(specific_charge_obj,pay_date)

#             booking_paid = bookingpaid + specific_charge_obj.booking_paid if specific_charge_obj.booking_paid is not None else 0
#             instalment_paid = instalmentpaid + specific_charge_obj.instalment_paid if specific_charge_obj.instalment_paid is not None else 0
#             addfee_paid = addfeepaid + specific_charge_obj.addfee_paid if specific_charge_obj.addfee_paid is not None else 0

#             rent_paid = rentpaid + specific_charge_obj.rent_paid if specific_charge_obj.rent_paid is not None else 0

#             water_paid = waterpaid + specific_charge_obj.water_paid if specific_charge_obj.water_paid is not None else 0
#             penalty_paid = penaltypaid + specific_charge_obj.penalty_paid if specific_charge_obj.penalty_paid is not None else 0
#             electricity_paid = electricitypaid + specific_charge_obj.electricity_paid if specific_charge_obj.electricity_paid  is not None else 0
#             garbage_paid = garbagepaid + specific_charge_obj.garbage_paid if specific_charge_obj.garbage_paid is not None else 0
#             security_paid = securitypaid+ specific_charge_obj.security_paid if specific_charge_obj.security_paid is not None else 0
#             service_paid = servicepaid + specific_charge_obj.maintenance_paid if specific_charge_obj.maintenance_paid is not None else 0

#             if specific_charge_obj.tenant_id:
#                 if specific_charge_obj.house.housecode.rentrate:
#                     rent_paid += overpayment
#             else:
#                 if specific_charge_obj.ptenant_id:
#                     if specific_charge_obj.house.housecode.servicerate:
#                         service_paid += overpayment

#             deposit_paid = depositpaid + specific_charge_obj.deposit_paid if specific_charge_obj.deposit_paid is not None else 0
#             agreement_paid = agreementpaid + specific_charge_obj.agreement_paid if specific_charge_obj.agreement_paid is not None else 0

#             MonthlyChargeOp.update_payments(specific_charge_obj,booking_paid,instalment_paid,addfee_paid,rent_paid,water_paid,electricity_paid,garbage_paid,security_paid,service_paid,penalty_paid,deposit_paid,agreement_paid)
#             PaymentOp.update_payments(payment_obj,bookingpaid,instalmentpaid,addfeepaid,rentpaid,waterpaid,electricitypaid,garbagepaid,securitypaid,servicepaid,penaltypaid,depositpaid,agreementpaid)

#             try:
#                 bookbal = specific_charge_obj.booking_due - bookingpaid
#                 instbal = specific_charge_obj.instalment_due - instalmentpaid
#                 addfeebal = specific_charge_obj.addfee_due - addfeepaid

#                 rentbal = specific_charge_obj.rent_due - rentpaid

#                 # rentbal -= overpayment
#                 waterbal = specific_charge_obj.water_due - waterpaid
#                 electricitybal = specific_charge_obj.electricity_due - electricitypaid
#                 servicebal = specific_charge_obj.maintenance_due - servicepaid
#                 penaltybal = specific_charge_obj.penalty_due - penaltypaid
#                 securitybal = specific_charge_obj.security_due - securitypaid
#                 garbagebal = specific_charge_obj.garbage_due - garbagepaid
#                 depositbal = specific_charge_obj.deposit_due - depositpaid
#                 agreementbal = specific_charge_obj.agreement_due - agreementpaid

#                 if specific_charge_obj.tenant_id:
#                     if specific_charge_obj.house.housecode.rentrate:
#                         rentbal -= overpayment
#                 else:
#                     if specific_charge_obj.ptenant_id:
#                         if specific_charge_obj.house.housecode.servicerate:
#                             servicebal -= overpayment

#                 MonthlyChargeOp.update_dues(specific_charge_obj,bookbal,instbal,addfeebal,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)
#             except:
#                 print("PAID TO LEGACY BILL")

#         # elif not specific_charge_obj and not current_period_payment:
#         #     subsequent_specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,billing_period.month,billing_period.year)

#         #     db.session.expire(specific_charge_obj)
#         #     bala = specific_charge_obj.balance
#         #     bala-=valid_amount
#         #     MonthlyChargeOp.update_balance(specific_charge_obj,bala)

#         #     paid_amount = specific_charge_obj.paid_amount
#         #     cumulative_pay = paid_amount + valid_amount
#         #     MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
#         #     MonthlyChargeOp.update_payment_date(specific_charge_obj,pay_date)

#         #     if subsequent_specific_charge_obj:
#         #         update_total = subsequent_specific_charge_obj.total_bill - valid_amount
#         #         update_arrears = subsequent_specific_charge_obj.arrears - valid_amount
#         #         update_balance = subsequent_specific_charge_obj.balance - valid_amount

#         #         MonthlyChargeOp.update_arrears(subsequent_specific_charge_obj,update_arrears)
#         #         MonthlyChargeOp.update_balance(subsequent_specific_charge_obj,update_balance)
#         #         MonthlyChargeOp.update_monthly_charge(subsequent_specific_charge_obj,"null","null","null","null","null","null","null","null","null","null",update_total,None)


#         stringname = h.name + " "

#         string_house += stringname

#     #################################################################################

#     str_houses = string_house.rstrip(" ")
#     house = list(str_houses.split(" "))

#     # house = house_obj.name

#     if payment_obj.receipt_num:
#         receiptno = payment_obj.receipt_num
#     else:
#         receiptno = payment_obj.id
    
#     paid = f'KES {payment_obj.amount:,.2f}'

#     if bal < 1:
#         bill = 0.0
#     else:
#         bill = (f"{bal:,.2f}")

#     payment_id = payment_obj.id

#     if email_bool and current_user.company_user_group.name != "User":
#         if tenant_obj.email:
#             try:
#                 job9 = q.enqueue_call(
#                     func=auto_send_mail_receipt, args=(payment_id,created_by,), result_ttl=5000
#                 )
#             except:
#                 print("Redis server is off")
#         else:
#             print("Email address not found for tenant ",tenant_obj.name,"-",prop.name)
#     else:
#         print("Email has been disabled for this payment")

#     # job11 = q.enqueue_call(
#     #     func=auto_send_sms_receipt, args=(payment_id,created_by,), result_ttl=5000
#     # )

#     if payment_obj.balance > -1:
#         baltitle = "Balance"
#         outline = "text-danger"
#         bal = f"KES {payment_obj.balance:,.0f}"
#     else:
#         baltitle = "Advance"
#         outline = "text-success"
#         bal = f"KES {payment_obj.balance*-1:,.0f}"

#     if os.getenv("TARGET") == "lasshouse":
#         receiptlink = f"https://cr.com/r/{rand_id}"
#     else:
#         receiptlink = f"https://kiotapay.com/r/{rand_id}"

#     receipt = f"Receipt: {receiptlink}"

#     if sms_bool and current_user.company_user_group.name != "Userrrrrr": #typo intentional

#         job101 = q.enqueue_call(
#             func=autosend_pending_smsreceipts, args=([payment_obj.id],), result_ttl=5000
#         )


def auto_consume_ctob(ctob_obj):
    prop = ApartmentOp.fetch_apartment_by_shortcode(ctob_obj.business_shortcode)
    try:
        agent = UserOp.fetch_user_by_username(prop.agent_id)
    except:
        agent = None

    billing_period = get_billing_period(prop)
    tenants = tenantauto(prop.id)

    tenant_obj = None
    tel = ctob_obj.msisdn
    formatted_tel = phone_number_formatter_r(tel)
    for tenant in tenants:
        if tenant.phone == formatted_tel:
            tenant_obj = tenant

    if tenant_obj:
        tenant_id = tenant_obj.id
        print(">>>>>>>>>>>>>>>>>>>",tenant_obj.name,"<<<<<<<<<<<<<<<<<<<<")
        paymode = "Mpesa payment"
        ref_number = ctob_obj.trans_id
        description = "C to B auto-payment"
        chargetype_string = "Rent payment"
        charged_amount = tenant_obj.balance
        amount = ctob_obj.trans_amnt
        apartment_id = check_house_occupied(tenant_obj)[2].apartment.id
        house_obj = check_house_occupied(tenant_obj)[1]
        house_id = house_obj.id
        created_by = 1
        ptenant_id=None
        payment_obj = PaymentOp(paymode,ref_number,description,chargetype_string,None,billing_period,charged_amount,amount,apartment_id,house_id,tenant_id,ptenant_id,created_by)
        payment_obj.save()

        rand_id = random_generator()
        if PaymentOp.fetch_payment_by_rand_id(rand_id):
            rand_id = random_generator(size=11)
            awe = sms.send("Ran random the second time !", ["+254716674695"],sender)
            if PaymentOp.fetch_payment_by_rand_id(rand_id):
                rand_id = random_generator(size=12)
                awe = sms.send("Ran random the third time !", ["+254716674695"],sender)
                if PaymentOp.fetch_payment_by_rand_id(rand_id):
                    rand_id = random_generator(size=13)
                    awe = sms.send("Ran random the fouth time !", ["+254716674695"],sender)
                    if PaymentOp.fetch_payment_by_rand_id(rand_id):
                        awe = sms.send("There is a problem with random, payment aborted !", ["+254716674695"],sender)
                        return "Payment could not be processed at this time! Try again later"

        PaymentOp.update_rand_id(payment_obj,rand_id)

        running_balance = tenant_obj.balance
        running_balance-=float(amount)
        TenantOp.update_balance(tenant_obj,running_balance)
        PaymentOp.update_balance(payment_obj,running_balance)

        month = datetime.datetime.now().month
        year = datetime.datetime.now().year

        monthly_charges = house_obj.monthlybills
        if monthly_charges:
            specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,month,year)
            try:
                bala = specific_charge_obj.balance
                bala-=float(amount)
                MonthlyChargeOp.update_balance(specific_charge_obj,bala)
            except:
                specific_charge_obj = monthly_charges[0]
                print(">>>>> no charges for current month,failover month",specific_charge_obj.month)
                bala = specific_charge_obj.balance
                bala-=float(amount)
                MonthlyChargeOp.update_balance(specific_charge_obj,bala)

            paid_amount = specific_charge_obj.paid_amount
            cumulative_pay = paid_amount + float(amount)
            MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
            MonthlyChargeOp.update_payment_date(specific_charge_obj,datetime.datetime.now())

        house = HouseOp.fetch_house_by_id(house_id).name
        paid = (f"{float(amount):,}")

        if charged_amount < 1:
            bill = 0.0
        else:
            bill = (f"{charged_amount:,}")

        if tenant_obj.balance < 0:
            bal = tenant_obj.balance * -1
            running_bal = (f"Advance: Kshs{bal:,}")
        else:
            running_bal = (f"Outstanding balance: Kshs{tenant_obj.balance:,}")
        receiptno = payment_obj.id


        # ###################################################################################
        # templateLoader = FileSystemLoader(searchpath="app/templates")
        # templateEnv = Environment(loader=templateLoader)
        # TEMPLATE_FILE = "ajax_payment_mailreceipt.html"
        # template = templateEnv.get_template(TEMPLATE_FILE)

        # pay_time = datetime.datetime.now()
        # paydate = pay_time.strftime("%B %d, %Y")
        # paytime = pay_time.strftime("%H:%M:%S")
        # pdftime = paydate + " " + paytime
        
        # template_vars = {
        #     "tenant":tenant_obj.name,
        #     "house":house,
        #     "amount":paid,
        #     "bill":bill,
        #     "balance":running_bal,
        #     "chargetype":chargetype_string,
        #     "receiptno":receiptno,
        #     "refnum":ref_number,
        #     "paymode":paymode,
        #     "pdftime":pdftime,
        #     "paytime":paydate,
        #     "logopath":logopath,
        #     "prop":prop
        # }
        # html_out = template.render(template_vars)
        # filename = f"app/temp/report_{tenant_id}.pdf"
        # HTML(string=html_out).write_pdf(filename,stylesheets=["app/static/eapartment-min.css","app/static/kiotapay.css"])
        # ###################################################################################
        # # LETS SEND EMAIL
        # mail_filename = f"report_{tenant_id}"
        # with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
        #     # print (fh)
        #     try:
        #         email_addr = tenant_obj.email
        #         txt = Message('Payment Acknowledgement', sender = mailsender, recipients = [email_addr])
        #         txt.body = "Dear Tenant;" "\nThis is acknowledging that we have received payment of Kshs " + paid + "\nIn case of any query, feel free to contact us. \nThank you. \nKIndly find the attached receipt."
        #         # txt.html = render_template('ajax_payment_receipt.html',tenant=tenant_name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno,prop=stored_apartment)
        #         txt.attach(filename="payment_receipt.pdf",disposition="attachment",content_type="application/pdf",data=fh.read())
        #         mail.send(txt)
        #     except Exception as e:
        #         print(str(e))
        # #########################################################################################
        # os.remove(filename)
        # ########################################################################################

        #Send the SMS


        if tenant.sms:
            receipt = f"Receipt: https://kiotapay.com/r/{payment_obj.rand_id}"
            ref = f'#{payment_obj.ref_number}'
            str_co = str(payment_obj.apartment.company)
            tele = tenant_obj.phone
            phonenum = sms_phone_number_formatter(tele)
            try:
                recipient = [phonenum]
                message = f"Rental payment Ref {ref}, sum of {paid} confirmed. \n{running_bal} \n\n{receipt} \n\n~{str_co}."

                # message = f"Rental payment #ref-{ref_number} Confirmed. We have received sum of Kshs {paid}. {running_bal}"

                #Once this is done, that's it! We'll handle the rest
                response = sms.send(message, recipient, sender)
                print(response)
            except Exception as e:
                print(f"Houston, we have a problem {e}")

def auto_consume_ctob2(ctob_obj):
    print("C2B C2B KIOTAPAY C2B C2B")

    print("REF>>>>",ctob_obj.bill_ref_num)

    code = ctob_obj.bill_ref_num.split('#')[1]

    valid_code = code.replace(" ","")

    print("CODE",code,"length: ",len(valid_code))

    co = CompanyOp.fetch_company_by_id(valid_code)

    if co:
        print("COMPANY",co)
    else:
        print("!!!!!!!!!!!!!!COMPANY NOT FOUND!!!!!!!!!!!!!")
        

    tele = ctob_obj.msisdn
    print("TELE",tele)
    phonenum = sms_phone_number_formatter_mpesa(tele)
    print("PHONENUM",phonenum)

    # units = ctob_obj.trans_amnt * 1.25

    units = ctob_obj.trans_amnt / 0.7

    old_units = co.remainingsms
    new_units = int(units) + old_units 

    CompanyOp.set_rem_quota(co,int(new_units))

    if co:

        message = f"Hi {ctob_obj.fname}, \n{co.name} has been successfully credited with {int(units)} sms units for payment of KES {ctob_obj.trans_amnt} (ref- {ctob_obj.trans_id}. \nAvailable sms units: {new_units}  \n\nThank you."

        if co.sms_provider == "Advanta":
            sms_sender(co.name,message,phonenum)
        else:
            try:
                recipient = [phonenum]                
                response = sms.send(message, recipient, sender)
                print(response)
            except Exception as e:
                print(f"Houston, we have a problem {e}")


def mpesa_response(ctob_obj):

    if "***" in ctob_obj.msisdn:
        tel = ""
    elif ctob_obj.company.name == "LaCasa" and ctob_obj.msisdn.endswith("087"):
        tel = "254722267087"
    else:
        tel = ctob_obj.msisdn

    try:
        phonenum = sms_phone_number_formatter_mpesa(tel)

        message = f"Dear {ctob_obj.fname} your transaction of {ctob_obj.trans_amnt} has been processed in favour of {ctob_obj.bill_ref_num} REFERENCE {ctob_obj.trans_id} Thank you."

        co = ctob_obj.company

        if co:
            if co.sms_provider == "Advanta":
                sms_sender(co.name,message,phonenum)
            else:
                try:
                    recipient = [phonenum]                
                    response = sms.send(message, recipient, sender)
                    print(response)
                except Exception as e:
                    print(f"Houston, we have a problem {e}")

    except Exception as e:
        print("ERROR",e)


def fetch_expenses(current_user):
    """will be deprecated in march 2021"""
    apartment_list = fetch_all_apartments_by_user(current_user)

    raw_expenses = []
    for prop in apartment_list:
        exp = prop.expenses
        raw_expenses.append(exp)
    
    return flatten(raw_expenses)

def get_obj_ids(arr):
    obj_id_list = []
    for req in arr:
        if req:
            req_id = req["id"]
            obj_id_list.append(req_id)
            editid = req.get("editid")
            obj_id_list.append(editid)
            delid = req["delid"]
            obj_id_list.append(delid)
            # tedit = req.get("tedit")
            # if tedit:
            #     obj_id_list.append(tedit)
            allocid=req.get("allocid")
            if allocid:
                obj_id_list.append(allocid)

    if not obj_id_list:
        obj_id_list.append("empty")

    str_ids = ','.join(map(str, obj_id_list))
    # print("IDS ARE HERE",str_ids)
    return str_ids

def get_obj_ids_alt(arr):
    obj_id_list = []
    for req in arr:
        if req:
            req_id = req["id"]
            obj_id_list.append(req_id)
            viewid = req["viewid"]
            obj_id_list.append(viewid)
            smsid = req["smsid"]
            obj_id_list.append(smsid)
            mailid = req["mailid"]
            obj_id_list.append(mailid)
            editid = req["editid"]
            obj_id_list.append(editid)
            balid = req.get("balid")
            obj_id_list.append(balid)
            payid = req["payid"]
            obj_id_list.append(payid)
            delid = req["delid"]
            obj_id_list.append(delid)

    if not obj_id_list:
        obj_id_list.append("empty")

    str_ids = ','.join(map(str, obj_id_list))
    # print("IDS ARE HERE",str_ids)
    return str_ids

def inject_tenants_ids(arr):
    newids = []
    for i in arr:
        someid = i["identity"]
        newids.append(someid)

    str_ids = ','.join(map(str, newids))
    
    return str_ids

def fetch_pending_expenses(current_user):
    apartment_list = fetch_all_apartments_by_user(current_user)

    raw_expenses = []
    pending_exps = []
    for prop in apartment_list:
        exp = prop.expenses
        raw_expenses.append(exp)
    
    all_expenses = flatten(raw_expenses)
    for item in all_expenses:
        if item.status == "pending":
            pending_exps.append(item)

    return pending_exps

def auto_generate_report(request,prop,logopath,rate,date):
    """generate reports and send them via email"""
    rent_collection = []
    water_collection = []

    #this only picks current month statement while param date is for scheduled job
    int_year = datetime.datetime.now().year
    int_month = datetime.datetime.now().month
    month = get_str_month(int_month)

    prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
    monthly_bills = prop_obj.monthlybills
    for bill in monthly_bills:
        if bill.year == int_year and bill.month == int_month:
            water_collection_member = bill.water
            rent_collection_member = bill.rent
            water_collection.append(water_collection_member)
            rent_collection.append(rent_collection_member)

    renttotal = 0.0
    watertotal = 0.0

    for item in rent_collection:
        renttotal += item
    ############################################################
    renttotal -=  3500.0
    ############################################################
    for item in water_collection:
        watertotal += item

    credittotal = renttotal + watertotal

    expenses = prop_obj.expenses
    current_month_expenses = []
    for exp in expenses:
        if exp.date.month == int_month and exp.status == "completed":
            current_month_expenses.append(exp)

    tokenamount = 0.0
    waterbillamount = 0.0
    securitybill = 0.0
    miscellaneous = 0.0
    electricityservice = 0.0

    for item in current_month_expenses:
        if item.expense_type == "token":
            tokenamount += item.amount
        elif item.expense_type == "water_bill":
            waterbillamount += item.amount
        elif item.expense_type == "security":
            securitybill += item.amount
        elif item.expense == "electricity_service":
            electricityservice += item.amount
        else:
            miscellaneous += item.amount

    management_fee = renttotal*0.07

    debittotal  = management_fee+tokenamount+waterbillamount+securitybill+electricityservice

    nettotal = credittotal-debittotal

    ###################################################################################
    templateLoader = FileSystemLoader(searchpath="app/templates")
    templateEnv = Environment(loader=templateLoader)
    TEMPLATE_FILE = "mail_statement_report.html"
    template = templateEnv.get_template(TEMPLATE_FILE)

    pay_time = datetime.datetime.now()
    paydate = pay_time.strftime("%B %d, %Y")
    paytime = pay_time.strftime("%H:%M:%S")
    pdftime = paydate + " " + paytime
    
    template_vars = {
        "prop":prop,
        "month":month,
        "fulllogopath":logopath,
        "watertotal":(f"{watertotal:,}"),
        "renttotal":(f"{renttotal:,}"),
        "credittotal":(f"{credittotal:,}"),
        "managementfee":(f"{management_fee:,}"),
        "tokenbill":(f"{tokenamount:,}"),
        "waterbill":(f"{waterbillamount:,}"),
        "securitybill":(f"{securitybill:,}"),
        "electricityservice":(f"{electricityservice:,}"),
        "debittotal":(f"{debittotal:,}"),
        "netamount":(f"{nettotal:,}"),
        "pdftime":pdftime,
        "paytime":paydate
    }
    html_out = template.render(template_vars)
    filename = f"app/temp/{prop}_{month}_statement.pdf"
    HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/eapartment-min.css","app/static/kiotapay.css"])
    ###################################################################################
    # LETS SEND EMAIL
    mail_filename = f"{prop}_{month}_statement"
    with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
        # print (fh)
        try:
            email_addr = "koechpetersn@gmail.com"
            txt = Message('Monthly Statememnt', sender = mailsender, recipients = [email_addr])
            txt.body = "Dear User; \nFind the attached " +month+ " report for "+prop+"."
            # txt.html = render_template('ajax_payment_receipt.html',tenant=tenant_name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno,prop=stored_apartment)
            txt.attach(filename=mail_filename+".pdf",disposition="attachment",content_type="application/pdf",data=fh.read())
            mail.send(txt)
        except Exception as e:
            print(str(e))
    #########################################################################################
    os.remove(filename)
    ########################################################################################

def smart_truncate(content, length=20, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

def remove_special_characters(mystr):
    trs = re.sub('[^A-Za-z0-9]+', '', mystr)
    return trs

def generate_suggestions(props):
    houses = []
    tenants = []
    for prop in props:
        house_list = prop.houses
        for item in house_list:
            houses.append(item) #iterating diff apartments to populate house list

        all_tenants = tenantauto(prop.id)
        for item in all_tenants:
            tenants.append(item) #iterating diff apartments to populate tenancy list

    suggestions_list = []
    # for prop_item in props:
    #     dict_item = {
    #         "name" : prop_item.name,
    #         "id" : "prop"+str(prop_item.id),
    #         "group" : "(property)",
    #         "prop" : ""
    #     }
    #     suggestions_list.append(dict_item)
    for house_item in houses:
        tenancy = check_occupancy(house_item)
        tenant = tenancy[1]
        vacancy = " (vacant)" if tenancy[1] == "vacant" else ""
        dict_item = {
            "name" : house_item.name + vacancy,
            "id" : "hse"+str(house_item.id),
            "group" : f"({smart_truncate(str(tenant))})",
            "prop" : f'-{ smart_truncate(house_item.apartment.name)}'
        }
        suggestions_list.append(dict_item)
    for tenant_item in tenants:
        house = check_house_occupied(tenant_item)[1]
        dict_item = {
            "name" : tenant_item.name,
            "id" : "tnt"+str(tenant_item.id),
            "group" : f"({smart_truncate(str(house),7)})",
            "prop" : f'-{ smart_truncate(tenant_item.apartment.name)}'
        }
        suggestions_list.append(dict_item)

    return suggestions_list

def build_search_unit(house_item):

    tenancy = check_occupancy(house_item)
    tenant = remove_special_characters(str(tenancy[1]))

    vacancy = " (vacant)" if tenancy[1] == "vacant" else ""
    dict_item = {
        "name" : remove_special_characters(house_item.name) + vacancy,
        "id" : "hse"+str(house_item.id),
        "group" : f"({smart_truncate(tenant)})",
        "prop" : f'-{ smart_truncate(house_item.apartment.name)}'
    }

    return dict_item

def build_search_tenant(tenant_item):
    house = get_active_houses(tenant_item)[1]

    dict_item = {
        "name" : remove_special_characters(tenant_item.name) + "(T)",
        "id" : "tnt"+str(tenant_item.id),
        "group" : f"({smart_truncate(remove_special_characters(str(house)),10)})",
        "prop" : f'-{ smart_truncate(tenant_item.apartment.name)}'
    }
    return dict_item

def build_search_ptenant(ptenant_item):
    house = ptenant_item.house

    dict_item = {
        "name" : remove_special_characters(ptenant_item.name) + "(R)",
        "id" : "ptnt"+str(ptenant_item.id),
        "group" : f"({smart_truncate(remove_special_characters(str(house)),10)})",
        "prop" : f'-{ smart_truncate(ptenant_item.apartment.name)}'
    }
    return dict_item

def build_search_phone(tenant_item):
    house = get_active_houses(tenant_item)[1]
    phone = tenant_item.phone
    if not phone:
        return None

    dict_item = {
        "name" : remove_special_characters(phone) + "(" + tenant_item.name + ")",
        "id" : "tphone"+str(tenant_item.id),
        "group" : f"({smart_truncate(remove_special_characters(str(house)),10)})",
        "prop" : f'-{ smart_truncate(tenant_item.apartment.name)}'
    }
    return dict_item

def generate_suggestions_alt(props,houses,tenants,ptenants):

    # for prop_item in props:
    #     dict_item = {
    #         "name" : prop_item.name,
    #         "id" : "prop"+str(prop_item.id),
    #         "group" : "(property)",
    #         "prop" : ""
    #     }
    #     suggestions_list.append(dict_item)




    suggestions_list1 = [build_search_unit(house) for house in houses]
    suggestions_list2 = [build_search_tenant(tenant) for tenant in tenants]
    suggestions_list3 = [build_search_ptenant(ptenant) for ptenant in ptenants]
    suggestions_list4 = [build_search_phone(tenant) for tenant in tenants if tenant.phone]

    # print("Monster>>>>>>>",len(suggestions_list))

    # from pprint import pprint
    # pprint(suggestions_list)
    
    # listToStr = ",".join([str(elem) for elem in suggestions_list])

    # return listToStr
    

    return suggestions_list1 + suggestions_list2 + suggestions_list3 + suggestions_list4
    

def access(current_user):
    if current_user.username.startswith('qc'):
        pass
    else:
        user_group = current_user.company_user_group
        accessright = check_accessright(user_group,"update_user")
        if accessright != True:
            return False
        
def permission(user,param):
    if user.username.startswith('qc') or user.user_group_id == 3 or user.user_group_id == 2:
        return True
    elif user.company_user_group.name == 'Director':
        return True
    else:
        if user.roles:
            # print("roles length",len(user.roles),"param",param)
            roles = user.roles.split(",")
            if param in roles:
                return True
            elif "admin" in roles:
                return True
            else:
                return False
        else:
            return True

def permission_alt(user,param):
    if user.username.startswith('qc'):
        return True
    else:
        if user.roles:
            # print("roles length",len(user.roles),"param",param)
            roles = user.roles.split(",")
            if "admin" in roles:
                return True
            else:
                return False
        else:
            return False

def run_props(prop,user):

    apartment_list = fetch_all_apartments_by_user(user)

    prop_obj = ApartmentOp.fetch_apartment_by_name(prop)

    props = []

    if prop == "All properties":
        props = apartment_list
    elif prop_obj:
        if prop_obj in apartment_list:
            props.append(prop_obj)
        else:
            props.append(apartment_list[0])
    else:
        try:
            props.append(apartment_list[0])
        except:
            pass

    return props


def get_sum(arr,mykey):
    totlist = [i.get(mykey) for i in arr]
    tot = sum_values(totlist)
    return tot
