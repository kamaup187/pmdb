"""Helper methods for views"""
import os
# from africastalking import initialize
import re
import xlrd
import inflect
import requests
from natsort import natsorted
try:
    from weasyprint import HTML
except:
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
from .advanta import *
from app import mail
from app import sms

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn,default_timeout=10800)

sender = os.getenv("SENDER_ID")

kiotapay_api_key = "f16edddd5e53dc3242f9fb9ad904ee5e"
kiotapay_partner_id = 3886

lesama_api_key = "cfc7c4382ae6d4277d8c09419a897c9e"
lesama_partner_id = 3895

merit_api_key = "fad3000bcfdfb541291ebc018bcc7868"
merit_partner_id = 2627

kiotanum = "+254716674695"

mailsender = "kiotapay@gmail.com" if os.getenv("TARGET") != "lasshouse" else os.getenv("G_ACCOUNT")


# from ..stkpush.access_token import register_url

configuration = os.getenv('APP_SETTINGS')

proceed = '<i class="fas fa-fw fa-check-circle text-success mr-1"></i>'
err = '<i class="fas fa-fw fa-times-circle text-danger mr-1"></i>'

flatten = lambda l: [item for sublist in l for item in sublist]
get_initials = lambda xx: ''.join(i[0] for i in xx.split())


def mbogi():
    print("Hi there")
    # from app import create_app
    # app = create_app(configuration)
    # app.app_context().push()

    # tenant = TenantOp.fetch_tenant_by_id(1)
    # bal = tenant.balance
    # print(bal)
    # TenantOp.update_balance(tenant,bal+1.0)

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
        try:
            total += i
        except:
            continue

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
            logopath = "../static/img/logos/nairuti/l-logoo.png"
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

        else:
            if os.getenv("TARGET") != "lasshouse":
                ##################################################
                logopath = "../static/img/logos/kiotapay/l-logo.png"
                mobilelogopath = "../static/img/logos/kiotapay/s-logo.png"
                fulllogopath = "../static/img/logos/kiotapay/full-logo.jpg"
                letterhead = "../static/img/logos/kiotapay/letterhead.jpg"
                sign = ""
            else:
                ##################################################
                logopath = "../static/img/logos/spry/l-logo.png"
                mobilelogopath = "../static/img/logos/spry/s-logo.png"
                fulllogopath = "../static/img/logos/spry/full-logo.jpg"
                letterhead = "../static/img/logos/spry/letterhead.jpg"
                sign = ""

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
        parent = "Kodimann"
        
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

def sms_sender(company,sms_text,phonenum):
    if company.title() == "Lesama Ltd":
        report = advanta_send_sms(sms_text,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")

    elif company.title() == "Merit Properties Limited":
        report = advanta_send_sms(sms_text,phonenum,merit_api_key,merit_partner_id,"MERIT_LTD")

    ################################## OWN SENDER IDS ##################################

    elif company.upper() == "KEVMA REAL ESTATE":
        report = advanta_send_sms(sms_text,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")

    elif company.title() == "Latitude Properties":
        report = advanta_send_sms(sms_text,phonenum,kiotapay_api_key,kiotapay_partner_id,"LATITUDE")

    #########################################################################################
    else:
        report = None
        
    if report:
        param1 = report["apikey"]
        param2 = report["partnerID"]
        param3 = report["msgid"]
        jb = q.enqueue_in(timedelta(seconds=60), advanta_sms_delivery, args=(param1,param2,param3,))
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

def fetch_prev_billing_period_bills_alt(month,year,arr):
    prev_billling_period_data = []
    prev_month = get_prev_month(month)
    prev_year = get_prev_year(month,year)
    for i in arr:
        if i.month == prev_month and i.year == prev_year:
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

def date_formatter_alt(dd):
    date = "15"
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
    for house in house_list_compare:
        # print("looping",str(house),hse)
        if str(house) == hse:
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

def payment_details(arr):
    detailed_payments = []
    for i in arr:
        pay_item = PaymentOp.view(i)
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
            return "Vacated",None,next(reversed(house_allocs)) #This returns last occupied house #really?

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

def generate_house_tenants(arr):
    """combine house and tenant"""
    new_arr = []
    for i in arr:
        hses = get_active_houses(i)[1]

        new_arr.append(f'{hses} #{i.name}')
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

def validate_tel_input(arg):
    tel = arg.replace(' ', '')       
    return tel

def validate_float_inputs(*args):
    print("Args>>>>>>>>",args)
    results = []
    for i in args:
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
    if arg == "True":
        return True
    else:
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

def generate_start_date(month,year):
    # if month == 2:
    #     day = datetime.datetime.now()
    
    # day = datetime.datetime.now()
    # .day if month != 2 else datetime.datetime.now().day - 3
    return datetime.datetime(year, month, 1)

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

def send_bulk_sms(propid,temp_txt,rem_bal,userid):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    tenants = tenantauto(propid)

    user_obj = UserOp.fetch_user_by_id(userid)

    # target_company = user_obj.company

    for tenant_obj in tenants:

        prop = tenant_obj.apartment
        co = prop.company
        str_co = co.name

        raw_rem_sms =co.remainingsms
        if tenant_obj.sms:

            if raw_rem_sms > 0:

                try:
                    target_bal = float(rem_bal)
                except:
                    target_bal = 0.0

                print("TAAAARGET BALLLLNACE",target_bal)

                if tenant_obj.balance > target_bal:
                    pass
                else:
                    print("HUYO AMELIPA LOL")
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
                    
                    sms_obj = SentMessagesOp(message,char_count,cost,tenant_obj.id,prop.id,co.id)
                    sms_obj.save()


                    if co.sms_provider == "Advanta":
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

        tenant_obj = payment_obj.tenant

        if tenant_obj.balance < 0:
            bal = tenant_obj.balance * -1
            running_bal = (f"Advance: KES {bal:,}")
        else:
            running_bal = (f"Balance: KES {tenant_obj.balance:,}")

        amount = f'Kes {payment_obj.amount:,.0f}'

        receipt = f"Receipt: https://kiotapay.com/r/{payment_obj.rand_id}"

        co = payment_obj.apartment.company
        str_co = co.name
        raw_rem_sms =co.remainingsms

        tele = tenant_obj.phone
        # name = tenant_obj.name
        # fname = fname_extracter(name)
        # if not fname:
        #     fname = name
        phonenum = sms_phone_number_formatter(tele)

        message = f"Rental payment Ref {reference}, sum of {amount} confirmed. \n{running_bal} \n\n{receipt} \n\n~{str_co}."

        if tenant_obj.sms:

            char_count = len(message)
            if char_count <= 160:
                cost = 1
            elif char_count <= 320:
                cost = 2
            else:
                cost = 3
            
            sms_obj = SentMessagesOp(message,char_count,cost,tenant_obj.id,payment_obj.apartment.id,co.id)
            sms_obj.save()

            if co.sms_provider == "Advanta":
                smsid = sms_sender(co.name,message,phonenum)
                if smsid:
                    PaymentOp.update_smsid(payment_obj,smsid)

            # if payment_obj.apartment.company.name == "Lesama Ltd":
            #     advanta_send_sms(message,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")
            #     PaymentOp.update_sms_status(payment_obj,"sent")
            # elif payment_obj.apartment.company.name == "KEVMA REAL ESTATE":
            #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
            #     PaymentOp.update_sms_status(payment_obj,"sent")
            else:
                if raw_rem_sms > 0:
                    #Send the SMS

                    try:
                        print("Payment sms sending initiated")
                        recipient = [phonenum]

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
                            if bill[0].email_invoice != "sent":
                                if bill[0].tenant.multiple_houses:
                                    multitenant_target_bills.append(bill[0])
                                    multitenants.append(bill[0].tenant)
                                else:
                                    target_bills.append(bill[0])

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
                            print("wa hara", bill.email_invoice)

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
                        print("wa hara", bill.email_invoice)

                        co = bill.apartment.company
                
                        invnum = bill.id + 13285

                        house = bill.house

                        tenant = bill.tenant

                        email_addr = tenant.email
                        if email_addr:

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
                            invdue = invdate + relativedelta(days=6)
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


                            ###################################################################################
                            # LETS SEND EMAIL
                            mail_filename = f"inv_{bill.id}"
                            with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
                                # print (fh)
                                try:
                                    try:
                                        tname = tenant.name.split('and')[0]
                                    except:
                                        tname = tenant.name

                                    period = f"{get_str_month(bill.month)} invoice"
                                    filename_ext = f"{get_str_month(bill.month)}invoice.pdf"

                                    txt = Message(period, sender = mailsender, recipients = [email_addr])
                                    txt.body = f"Dear {tname}  \nYour invoice is now available. Kindly find the attached invoice. \n\n{co.name}"
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
                        else:
                            print("Email address not found for tenant ",tenant.name,"-",prop)
            except Exception as e:
                print("Mail failed to connect >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",e)
    except Exception as e:
        print("WORKING HAS STOPPED >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",e)
            

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
                if charge.date.month == bill.apartment.billing_period.month and charge.date.year == bill.apartment.billing_period.year and not charge.reading_id:
                    ChargeOp.delete(charge)

            if bill.apartment.billing_period.month == bill.month:
            
                tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                print("ORIGINAL AMOUNT:",original_amount)
                running_bal = tenant_obj.balance
                print("CURRENT TENANT BALANCE:",running_bal)
                running_bal = running_bal - original_amount
                print("FINAL:",running_bal)

                TenantOp.update_balance(tenant_obj,running_bal)

                MonthlyChargeOp.delete(bill)

def send_out_sms_invoices(prop,houses,override,charge,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
    update = False

    if prop_obj and charge == "all":

        billing_period = get_billing_period(prop_obj)

        target_bills = []

        if houses and houses != "ALL":
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

            tenant = bill.tenant

            sibling_water_bill = fetch_current_billing_period_readings(prop_obj.billing_period,bill.house.meter_readings)

            try:
                wbill = sibling_water_bill[0]
            except:
                wbill = None

            if wbill:
                amount = 0.0
                standing_charge = 0.0

                if wbill.charged:
                    charge_obj = ChargeOp.fetch_charge_by_reading_id(wbill.id)
                    amount = charge_obj.amount

                    standing_charge = house.housecode.watercharge
                    if standing_charge:
                        amount += standing_charge

                smslastreading = (f"{wbill.last_reading} ")
                smscurrentreading = (f"{wbill.reading} ")
                smsunits = (f"{wbill.units} ")
                smsstd = f"Standing charge: Kes {standing_charge}" if house.housecode.watercharge else ""
                smsbill = (f"Kes {amount:,} ")

                wmessage = f"\n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \n{smsstd} \nWater: {smsbill}"
            else:
                wmessage = ""
                smsbill = "Kes 0.0"


            tenant = bill.tenant
            arrears = bill.arrears
            
            calculated_total = 0.0
            if bill.paid_amount and arrears > 0:
                if arrears <= bill.paid_amount:
                    calculated_total = bill.total_bill - arrears
                    arrears = 0.0
                else:
                    arrears = bill.arrears - bill.paid_amount
                    calculated_total = bill.total_bill - bill.paid_amount

            smsrent = f"\n\nRent:{bill.rent:,}," if bill.rent else ""

            if wmessage:
                smswater = wmessage
            else:
                smswater = f"\nWater:{bill.water}," if bill.water else ""

            if bill.house.payment_bankacc:
                bankdetails = f'\n\nBank: {bill.house.payment_bank} \nAcc: {bill.house.payment_bankacc}'
            elif prop_obj.payment_bank == "PayBill":
                prop_name = prop_obj.name.split(" ")[0]
                bankdetails = f'\n\n {prop_obj.payment_bank}: {prop_obj.payment_bankacc} \nAcc: {prop_name.lower()}/{bill.house.name}'
            elif prop_obj.payment_bank:
                bankdetails = f'\n\nBank: {prop_obj.payment_bank} \nAcc: {prop_obj.payment_bankacc}'
            else:
                bankdetails = ""

            smsgarb = f"\nGarbage:{bill.garbage}," if bill.garbage else ""
            smssec = f"\nSecurity:{bill.security}," if bill.security else ""
            smssev = f"\nService:{bill.maintenance}," if bill.maintenance else ""
            smselec = f"\nElectricity:{bill.electricity}," if bill.electricity else ""
            smsdep = f"\nDeposit:{bill.deposit}" if bill.deposit else ""
            smsarrears = f"\nArrears:{arrears}" if arrears else ""
            smsfine = f"\nPenalty:{bill.penalty}" if bill.penalty else ""
            smstotal = (f"{bill.total_bill:,.1f}") if not calculated_total else (f"{calculated_total:,.1f}")
            bankdetails = bankdetails

            current_user = UserOp.fetch_user_by_id(user_id)

            co = current_user.company
            str_co = f"\n\n ~ {str(co)}"
            raw_rem_sms =co.remainingsms
            if tenant.sms:
                if raw_rem_sms > 0:

                    tele = tenant.phone
                    phonenum = sms_phone_number_formatter(tele)
                    str_month = get_str_month(billing_period.month) if smsrent else get_str_month(billing_period.month-1) # URGENT TODO : TAKE CARE OF JANUARY
                    tname = fname_extracter(tenant.name)
                    try:
                        recipient = [phonenum]
                        if update:
                            if arrears < 0.0:
                                bbf = -1 * arrears
                                sms_bbf = (f"{bbf:,}")
                                message = f"Dear {tname}, your {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smssev} {smselec} {smsdep} {smsfine} \nPaid: {sms_bbf} \n\nTotal due: {smstotal} {bankdetails} {str_co}."
                            else:
                                message = f"Dear {tname}, your {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smssev} {smselec} {smsdep} {smsfine} {smsarrears} \n\nTotal due: {smstotal} {bankdetails} {str_co}." 
                            #     message = f"Dear {tname}, the revised {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smselec} {smsdep} \nPaid: {sms_bbf} \n\nTotal due: {smstotal} {bankdetails} {str_co}."
                            # else:
                            #     message = f"Dear {tname}, the revised {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smselec} {smsdep} {smsarrears} \n\nTotal due: {smstotal} {bankdetails} {str_co}." 

                        else:
                            if arrears < 0.0:
                                bbf = -1 * arrears
                                sms_bbf = (f"{bbf:,}")
                                message = f"Dear {tname}, your {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smssev} {smselec} {smsdep} {smsfine} \nPaid: {sms_bbf} \n\nTotal due: {smstotal} {bankdetails} {str_co}."
                            else:
                                message = f"Dear {tname}, your {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smssev} {smselec} {smsdep} {smsfine} {smsarrears} \n\nTotal due: {smstotal} {bankdetails} {str_co}."
                        # if prop_obj.company.name == "KIGAKA ENTERPRISES":
                        #     continue

                        char_count = len(message)
                        if char_count <= 160:
                            cost = 1
                        elif char_count <= 320:
                            cost = 2
                        else:
                            cost = 3
                        
                        sms_obj = SentMessagesOp(message,char_count,cost,tenant.id,prop_obj.id,co.id)
                        sms_obj.save()

                        if co.sms_provider == "Advanta":
                            sms_sender(co.name,message,phonenum)
                            MonthlyChargeOp.update_sms_status(bill,"sent")


                        # if co.name == "KEVMA REAL ESTATE":
                        #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
                        #     MonthlyChargeOp.update_sms_status(bill,"sent")
                        # elif co.name == "Lesama Ltd":
                        #     advanta_send_sms(message,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")
                        #     MonthlyChargeOp.update_sms_status(bill,"sent")


                        # if message:
                        #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
                        #     MonthlyChargeOp.update_sms_status(bill,"sent")
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

    txt = Message('Welcome to Kodimann! Please activate your account.', sender = mailsender, recipients = [email])
    txt.html = render_template('activation.html',name=name,target_url=url)
    mail.send(txt)

def send_demo_mail(email,name,url):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    print("goooiiing")

    txt = Message('Welcome to Kodimann! Demo account.', sender = mailsender, recipients = [email])
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


def read_excel(dict_array,apartment_id,user_id):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

    for item in dict_array:

        unit = item["unit"]
        desc = item["desc"]
        group = item["group"]
        tenant = item["tenant"]
        mobile = item["mobile"]
        email = item["email"]
        water = item["water"]
        garb = item["garb"]
        serv = item["serv"]
        sec = item["sec"]

        natid = None

        if isinstance(group,float):
            housecode = str(int(group))
        else:
            housecode = group

        housecode = housecode.upper()

        code_obj = get_specific_code_obj(apartment_id,housecode)


        if code_obj:
            print("Skipping ",housecode)
            
        elif group:
            valid_inputs = validate_float_inputs_to_exclude_zeros_alt(group,water,garb,sec,serv)

            print("house & amount",housecode,valid_inputs[0])

            code_obj = HouseCodeOp(housecode,valid_inputs[0],valid_inputs[1],valid_inputs[2],valid_inputs[3],0.0,0.0,0.0,0.0,0.0,valid_inputs[4],apartment_id,user_id)
            code_obj.save()
        else:
            pass

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

        try:
            tel = str(int(mobile))
        except:
            tel = ""

        if tel:
            rawstrtel = tel.replace(" ", "")
            if len(rawstrtel) > 9:
                strtel = ""
            else:
                strtel = rawstrtel
        else:
            strtel = ""

        if strtel.startswith("0"):
            tenantphone = strtel
        else:
            tenantphone = "0" + strtel

        tenantemail = email
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
                    similar = True

            if similar:
                pass
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
            if tenant.balance > 1000:
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
                        fine_amnt = 0.0033333333 * hse.housecode.rentrate
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

def water_bill(apartment_id,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)#get apartment obj first
    meter_readings = apartment_obj.meter_readings
    target_readings = []

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
            unitcost = house_obj.housecode.waterrate
            bill_amount = units*unitcost
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

def rent_bill(apartment_id,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    house_list = houseauto(apartment_id)
    
    for house in house_list:
        house_id = house.id
        checker = None
        rent_charge = 0
        
        result = check_occupancy(house)
        if result[0] == "occupied":
            if not house.billable:
                rent_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue
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

def garbage_bill(apartment_id,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        garbage_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied":
            if not house.billable:
                garbage_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue
                garbage_charge = house.housecode.garbagerate

            all_charges = ChargeOp.fetch_charges_by_house_id(house_id)
            garbage_charges = []
            for charge in all_charges:
                if str(charge) == "Garbage" and charge.date.month == month and charge.date.year == year:
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

def fixed_water_bill(apartment_id,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        fixed_water_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied":
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

def electricity_bill(apartment_id,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    apartment_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)#get apartment obj first
    meter_readings = apartment_obj.meter_readings
    target_readings = []

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

def security_bill(apartment_id,chargetype,user_id,month,year):
    from app import create_app
    app = create_app(configuration)
    app.app_context().push()

    charge_type_id = get_charge_type_id(chargetype)
    house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        security_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied":

            if not house.billable:
                security_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue

                security_charge = house.housecode.securityrate

            all_charges = ChargeOp.fetch_charges_by_house_id(house_id)
            security_charges = []
            for charge in all_charges:
                if str(charge) == "Security" and charge.date.month == month and charge.date.year == year:
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

def maintenance_bill(apartment_id,chargetype,user_id,month,year):
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

    house_list = houseauto(apartment_id)

    for house in house_list:
        house_id = house.id
        checker = None
        service_charge = 0

        result = check_occupancy(house)
        if result[0] == "occupied":

            if not house.billable:
                service_charge = 0.0
            else:
                if not house.housecode:
                    print("HOUSE GROUP MISSING FOR: ",house,"of",house.apartment)
                    continue

                service_charge = house.housecode.servicerate if house.housecode.servicerate else 0.0

            all_charges = ChargeOp.fetch_charges_by_house_id(house_id)

            accepted = True
            if not accepted:
                pass
            else:
                for charge in all_charges:
                    if str(charge) == "Maintenance" and charge.date.month == month and charge.date.year == year:
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

def total_bill(apartment_id,user_id,month,year):
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
    houses = apartment_obj.houses

    try:
        # with mail.connect() as conn:
        print ("Billing has started with mail connected successfully")
        for house in houses:
            all_charges = house.charges

            charges = []
            for charge in all_charges:
                if charge.date.month == month and charge.date.year == year:
                    charges.append(charge)

            water_total = 0
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

            print("######################################### END OF HOUSE",prop,house,"BILLING ###############################################")
                
            house_id = house.id
            result = check_occupancy(house)
            tenant = None
            if result[0] == "occupied":
                tenant = result[1]
            if tenant:
                tenant_id = tenant.id
                created_by = user_id

                tenant_obj = tenant

                bills = house.monthlybills
                current_billing_period_bills = fetch_current_billing_period_bills(apartment_obj.billing_period,tenant_obj.monthly_charges)


                prev_bill = fetch_prev_billing_period_bills_alt(month,year,bills)
                if prev_bill:
                    arrears = prev_bill[0].balance

                    if prev_bill[0].rent_due: #rent due of last period forms the base of arrears
                        rent_bal = prev_bill[0].rent_due
                        rent_due = rent_bal + rent
                    else:
                        rent_due = rent

                    if prev_bill[0].water_due:
                        water_bal = prev_bill[0].water_due
                        water_due = water_bal + water_total
                    else:
                        water_due = water_total

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

                    if prev_bill[0].maintenance_due:
                        maintenance_bal = prev_bill[0].maintenance_due
                        maintenance_due = maintenance_bal + maintenance
                    else:
                        maintenance_due = maintenance

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

                    water_due = water_total

                    rent_due = rent

                    garbage_due = garbage

                    electricity_due = electricity

                    security_due = security

                    maintenance_due = maintenance

                    fines_due = fines

                    deposit_due = deposit

                    agreement_due = agreement

                if tenant.initial_arrears:
                    print("Calculating arrears for ",house,"before",arrears)
                    arrears += tenant.initial_arrears
                    print("Calculated arrears for ",house, "being",arrears)
                    TenantOp.update_initial_arrears(tenant,0.0)

                if tenant.accumulated_fine:
                    print("Calculating fines for ",house)
                    fines = tenant.accumulated_fine
                    TenantOp.update_fine(tenant,0.0)

                new_tenants = new_tenants_injector(apartment_obj.id,month,year)
                if tenant_obj in new_tenants:
                    deposit = house.housecode.rentrate + house.housecode.waterdep + house.housecode.elecdep
                    agreement = apartment_obj.agreement_fee if apartment_obj.agreement_fee else 0.0 #TODO

                total_amount = water_total+rent+garbage+electricity+security+fines+arrears+deposit+agreement+maintenance

                current_month_charges = []
                all_monthlybills = house.monthlybills
                
                for bill in all_monthlybills: #TODO 
                    if bill.month == month and bill.year == year:
                        print("Appending",bill.month)
                        current_month_charges.append(bill)
                
                if current_month_charges:
                    current_month_charge = None
                    
                    for charge in current_month_charges:

                        if charge.house_id == house_id:
                            current_month_charge = charge #specific current month charge for a particular house/tenant found
                            print("specific charge found for HOUSE",house)

                            update_water = charge.water
                            update_water += water_total
                            update_water_due = charge.water_due if charge.water_due else 0.0
                            update_water_due += water_total

                            update_rent = charge.rent
                            update_rent += rent
                            update_rent_due = charge.rent_due if charge.rent_due else 0
                            update_rent_due += rent

                            update_garbage = charge.garbage
                            update_garbage += garbage
                            update_garbage_due = charge.garbage_due if charge.garbage_due else 0
                            update_garbage_due += garbage

                            update_electricity = charge.electricity
                            update_electricity += electricity
                            update_electricity_due = charge.electricity_due if charge.electricity_due else 0                          
                            update_electricity_due += electricity

                            update_security = charge.security
                            update_security += security
                            update_security_due = charge.security_due if charge.security_due else 0
                            update_security_due += security

                            update_maintenance = charge.maintenance
                            update_maintenance += maintenance
                            update_maintenance_due = charge.maintenance_due if charge.maintenance_due else 0
                            update_maintenance_due += maintenance

                            update_penalty = charge.penalty
                            update_penalty += fines
                            update_penalty_due = charge.penalty_due if charge.penalty_due else 0
                            update_penalty_due += fines

                            const_arrears = charge.arrears

                            const_deposit = charge.deposit if charge.deposit else 0.0
                            const_deposit_due = charge.deposit_due if charge.deposit_due else 0.0

                            const_agreement = charge.agreement if charge.agreement else 0.0
                            const_agreement_due = charge.agreement_due if charge.agreement_due else 0.0

                            total_amount = update_water+update_rent+update_garbage+update_electricity+update_security+update_maintenance+update_penalty+const_arrears + const_deposit + const_agreement #total amount is incremented only by updates

                            MonthlyChargeOp.update_monthly_charge(current_month_charge,update_water,update_rent,update_garbage,update_electricity,update_security,const_deposit,const_agreement,update_maintenance,update_penalty,const_arrears,total_amount,created_by)
                            MonthlyChargeOp.update_dues(current_month_charge,update_rent_due,update_water_due,update_electricity_due,update_garbage_due,update_security_due,update_maintenance_due,update_penalty_due,const_deposit_due,const_agreement_due)


                            tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
                            running_bal = tenant_obj.balance
                            running_bal = running_bal + water_total+rent+garbage+electricity+security+maintenance+fines #these are updates, if one has update, the rest are zeros
                            TenantOp.update_balance(tenant_obj,running_bal)

                            bal = current_month_charge.balance
                            bal = bal + water_total+rent+garbage+electricity+security+maintenance+fines #these are updates, if one has update, the rest are zeros
                            MonthlyChargeOp.update_balance(current_month_charge,bal)

                            if current_month_charge.paid_amount:
                                if current_month_charge.paid_amount < 0:
                                    MonthlyChargeOp.update_payment(current_month_charge,0.0)
                                    bala = total_amount
                                else:
                                    bala = total_amount - current_month_charge.paid_amount
                            else:
                                bala = total_amount

                            MonthlyChargeOp.update_balance(current_month_charge,bala)

                            db.session.expire(current_month_charge)
                            
                            bill_balance = current_month_charge.balance
                            print(current_month_charge.month,current_month_charge.year,"KES",current_month_charge.balance)
                            TenantOp.update_balance(tenant_obj,bill_balance)
                            db.session.expire(tenant_obj)
                            print("Balance updated! now",tenant_obj.balance)

                            break
                        else:
                            continue

                    if not current_month_charge: #specific current month charge wasnt found for a particular house/tenant
                        print("MIRACLE PART >>>>>>>> specific charge not found") #TODO
                        monthly_charge_obj = MonthlyChargeOp(year,month,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,created_by)
                        monthly_charge_obj.save()

                        monthly_charge_obj_alt = MonthlyChargeHistoryOp(year,month,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,monthly_charge_obj.id,created_by)
                        monthly_charge_obj_alt.save()

                        MonthlyChargeOp.update_balances(monthly_charge_obj,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                        MonthlyChargeOp.update_dues(monthly_charge_obj,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)

                        MonthlyChargeHistoryOp.update_balances(monthly_charge_obj_alt,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                        MonthlyChargeHistoryOp.update_dues(monthly_charge_obj_alt,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)

                        tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
                        running_bal = tenant_obj.balance
                        running_bal += total_amount

                        print("ARRAGAIK>>>Month of",month,current_billing_period_bills,"HOUSE =====>",house)


                        if tenant_obj.multiple_houses and current_billing_period_bills:
                            print("IT GOT HERE COZ ABOVE IS NOT EMPTY",house)
                            TenantOp.update_balance(tenant_obj,running_bal)
                        else:
                            TenantOp.update_balance(tenant_obj,total_amount)

                        bal = monthly_charge_obj.balance
                        bal += total_amount
                        MonthlyChargeOp.update_balance(monthly_charge_obj,bal)

                        if not house.billable:
                            print("House",house,"is not billablle") 


                else:
                    print("no charges found at all")
                    monthly_charge_obj = MonthlyChargeOp(year,month,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,created_by)
                    monthly_charge_obj.save()

                    monthly_charge_obj_alt = MonthlyChargeHistoryOp(year,month,water_total,rent,garbage,electricity,security,maintenance,fines,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,monthly_charge_obj.id,created_by)
                    monthly_charge_obj_alt.save()

                    MonthlyChargeOp.update_balances(monthly_charge_obj,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                    MonthlyChargeOp.update_dues(monthly_charge_obj,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)

                    MonthlyChargeHistoryOp.update_balances(monthly_charge_obj_alt,rent_bal,water_bal,electricity_bal,garbage_bal,security_bal,maintenance_bal,fines_bal,deposit_bal,agreement_bal)
                    MonthlyChargeHistoryOp.update_dues(monthly_charge_obj_alt,rent_due,water_due,electricity_due,garbage_due,security_due,maintenance_due,fines_due,deposit_due,agreement_due)

                    tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
                    running_bal = tenant_obj.balance
                    running_bal += total_amount

                    print("ARRAGAIK>>>Month of",month,current_billing_period_bills,"HOUSE =====>",house)
                    
                    if tenant_obj.multiple_houses and current_billing_period_bills:
                        print("IT GOT HERE COZ ABOVE IS NOT EMPTY",house)
                        TenantOp.update_balance(tenant_obj,running_bal)
                    else:
                        TenantOp.update_balance(tenant_obj,total_amount)

                    bal = monthly_charge_obj.balance
                    bal += total_amount
                    MonthlyChargeOp.update_balance(monthly_charge_obj,bal)

                    if not house.billable:
                        print("House",house,"is not billablle")

        ApartmentOp.update_billing_progress(apartment_obj,"completed")

    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Biling Failed >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print(e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        ApartmentOp.update_billing_progress(apartment_obj,"failed")


        
def filtered_house_list(apartment_id):
    """Filtering out read houses"""
    unread_houses = []
    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
    house_list = filter_in_metered_houses(prop.name)
    
    # period = current_user.company.billing_period.month
    billing_period = prop.billing_period

    if datetime.datetime.now().day < 20 and datetime.datetime.now().month == billing_period.month:
        #Only enters this block for readings taken after billing and are meant for the same period as the current bills. next month of billing
        print("Reading left out captured")

        month = billing_period.month
        year = billing_period.year

    elif datetime.datetime.now().day >= 20:
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
        print("Prev reading period",prev_reading_obj.reading_period.month,"")

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

def filtered_house_list_alt(apartment_id):
    """Filtering out read houses"""
    unread_houses = []
    prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
    house_list = filter_in_metered_houses_alt(prop.name)
    
    period = prop.billing_period.month
    current_month = datetime.datetime.now().month

    if period != 12:
        if datetime.datetime.now().day < 20 and current_month == period:
            period = period
        else:
            period += 1
    else:
        if datetime.datetime.now().day < 20 and current_month == period:
            period = 12
        else:
            period = 1

    for house in house_list:
        active_meter = fetch_active_meter_alt(house)
        prev_reading_obj = fetch_last_reading(active_meter.id)
        print("Prev reading period",prev_reading_obj.reading_period.month)
        
        if prev_reading_obj.reading_period.month == period:
            if prev_reading_obj.description == "actual electricity reading":
                pass
            else:
                unread_houses.append(house)
        else:
            unread_houses.append(house)

    return unread_houses


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
        payment_obj = PaymentOp(paymode,ref_number,description,chargetype_string,None,billing_period,charged_amount,amount,apartment_id,house_id,tenant_id,created_by)
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
            editid = req["editid"]
            obj_id_list.append(editid)
            delid = req["delid"]
            obj_id_list.append(delid)

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
        "name" : remove_special_characters(tenant_item.name),
        "id" : "tnt"+str(tenant_item.id),
        "group" : f"({smart_truncate(remove_special_characters(str(house)),10)})",
        "prop" : f'-{ smart_truncate(tenant_item.apartment.name)}'
    }
    return dict_item

def generate_suggestions_alt(props,houses,tenants):

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




    # print("Monster>>>>>>>",len(suggestions_list))

    # from pprint import pprint
    # pprint(suggestions_list)
    
    # listToStr = ",".join([str(elem) for elem in suggestions_list])

    # return listToStr
    

    return suggestions_list1 + suggestions_list2
    

def access(current_user):
    if current_user.username.startswith('qc'):
        pass
    else:
        user_group = current_user.company_user_group
        accessright = check_accessright(user_group,"update_user")
        if accessright != True:
            return False
        


    


