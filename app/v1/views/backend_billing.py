import os
from dateutil.parser import parse
import datetime 
import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy import exc
try:
    from weasyprint import HTML
except:
    HTML = None
    
from jinja2 import Environment, FileSystemLoader, Template

import inflect

from flask_login import login_required, current_user
from flask_restful import Resource, abort
from flask_mail import Message
from flask import render_template,Response,request,flash,redirect,url_for,json,jsonify,make_response
from ..forms.forms import PaymentForm,AmendChargeForm
from ..stkpush.access_token import lipa_na_mpesa_online,lipa_na_mpesa_online2,stkquery
from app.v1.models.operations import *
from .helperfuncs import *
from app import mail
from app import sms


class BClientBilling(Resource):
    def get(self):
        rawbills = []
        timenow = datetime.datetime.now()
        clients = CompanyOp.fetch_all_active_companies()
        for c in clients:
            current_month_bill = fetch_current_billing_period_bills(timenow,c.bills)

            if current_month_bill:
                # ClientBillOp.delete(current_month_bill)
                # continue
                pass

            if not current_month_bill:
                try:
                    total = c.balance + c.subscription
                except:
                    total = 0
                bill = ClientBillOp(timenow.year,timenow.month,c.subscription,0.0,0.0,0.0,c.balance,total,c.id)
                bill.save()
                rawbills.append([bill])
                # continue
            else:
                rawbills.append(current_month_bill)

        bills = flatten(rawbills)
        items = bill_details_alt(bills)
        billids = get_obj_ids(items)

        return make_response(jsonify({
                'message': 'Success',
                # 'bills':items[0],
            'billids':billids

        }), 200)
        
        
class BBilling(Resource):
    """class"""
    @login_required
    def post(self):
        msg = None
        user_id = current_user.id

        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400

        apartment_name =  data.get("apartment")
        houses =  data.get("houses")
        tenantid =  data.get("tenantid")
        # date =  data.get("date")
        year1 =  data.get("year")
        month1 =  data.get("month")
        date = year1+'/'+month1
        target =  data.get("target")

        try:
            billdate = date_formatter(date)
            bill_date = parse(billdate)
        except:
            bill_date = None

        try:
            houseids = [int(s) for s in houses.split(',')]
            print("HOUSEIDS",houseids)
        except:
            houseids = []

        if target == "single":
            try:
                billdate = date_formatter_weekday(date)
                bill_date = parse(billdate)
            except:
                bill_date = None

            residents = []
            resident = PermanentTenantOp.fetch_tenant_by_id(get_identifier(tenantid))
            residents.append(resident)
            houseids = [resident.house.id for resident in residents]


        if not apartment_name:
            propid = data.get("propid")
            print("APARTMENT ID TO BILL IS>>>>",propid)
            # apartment_id = propid[4:]
            apartment_id = get_identifier(propid)
            prop = ApartmentOp.fetch_apartment_by_id(get_identifier(propid))
            apartment_name = prop.name
        else:
            apartment_id = get_apartment_id(apartment_name)
            prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

        ApartmentOp.update_billing_progress(prop,"billing")
            
        chargetype = data.get("chargetype")

        try:
            yr = bill_date.year
            mnth = bill_date.month
        except:
            yr = None
            mnth = None

        if not yr:
            year = current_user.company.billing_period.year
        else:
            year = int(yr)

        if not mnth:
            month = current_user.company.billing_period.month
        else:
            month = int(mnth)

        if chargetype == "Water":
            job = q.enqueue_call(
                func=water_bill, args=(apartment_id,chargetype,user_id,month,year,), result_ttl=5000
            )
            job2 = q.enqueue_call(
                func=total_bill, args=(apartment_id,user_id,month,year,), result_ttl=5000
            )
            msg = "All unbilled readings billed successfully"

        elif chargetype == "Rent":
            job = q.enqueue_call(
                func=rent_bill, args=(apartment_id,chargetype,user_id,month,year,), result_ttl=5000
            )
            job2 = q.enqueue_call(
                func=total_bill, args=(apartment_id,user_id,month,year,), result_ttl=5000
            )
            msg = "Rent billed to all houses successfully"

        elif chargetype == "Garbage":
            job = q.enqueue_call(
                func=garbage_bill, args=(apartment_id,chargetype,user_id,month,year,), result_ttl=5000
            )
            job2 = q.enqueue_call(
                func=total_bill, args=(apartment_id,user_id,month,year,), result_ttl=5000
            )
            msg = "Garbage fee billed to all houses succesfully"

        elif chargetype == "Electricity":
            job = q.enqueue_call(
                func=electricity_bill, args=(apartment_id,chargetype,user_id,month,year,), result_ttl=5000
            )
            job2 = q.enqueue_call(
                func=total_bill, args=(apartment_id,user_id,month,year,), result_ttl=5000
            )
            msg = "Electricity fee billed to all houses succesfully"

        elif chargetype == "Security":
            job = q.enqueue_call(
                func=security_bill, args=(apartment_id,chargetype,user_id,month,year,), result_ttl=5000
            )
            job2 = q.enqueue_call(
                func=total_bill, args=(apartment_id,user_id,month,year,), result_ttl=5000
            )
            msg = "Security fee billed to all houses succesfully"

        else:

            job = q.enqueue_call(
                func=water_bill, args=(apartment_id,houseids,"Water",user_id,month,year,), result_ttl=5000
            )
            jobfixedwater = q.enqueue_call(
                func=fixed_water_bill, args=(apartment_id,houseids,"Water",user_id,month,year,), result_ttl=5000
            )
            job2 = q.enqueue_call(
                func=rent_bill, args=(apartment_id,houseids,"Rent",user_id,month,year,), result_ttl=5000
            )
            job3 = q.enqueue_call(
                func=garbage_bill, args=(apartment_id,houseids,"Garbage",user_id,month,year,), result_ttl=5000
            )
            job4 = q.enqueue_call(
                func=electricity_bill, args=(apartment_id,houseids,"Electricity",user_id,month,year,), result_ttl=5000
            )
            job5 = q.enqueue_call(
                func=security_bill, args=(apartment_id,houseids,"Security",user_id,month,year,), result_ttl=5000
            )
            job6 = q.enqueue_call(
                func=maintenance_bill, args=(apartment_id,houseids,"Maintenance",user_id,month,year,), result_ttl=5000
            )
            job7 = q.enqueue_call(
                func=total_bill, args=(apartment_id,houseids,user_id,month,year,), result_ttl=5000
            )
            
            str_month = get_str_month(month)

            txt = f"{current_user.company} has billed for {str_month} for {apartment_name}"
            send_internal_email_notifications(current_user.company.name,txt)



    @login_required
    def get(self):
        if current_user.username.startswith('qc'):
            pass
        else:
            user_group = current_user.company_user_group
            accessright = check_accessright(user_group,"bill_tenant")
            if accessright != True:
                return make_response(jsonify({
                'msg': 'You have insufficient rights to access this form!',
                "name":current_user.name
            }))
    

        apartment_list = fetch_all_apartments_by_user(current_user)
        # charge_type_list = ChargeType.query.all()

        return make_response(jsonify({
            'msg': 'You have insufficient rights to access this form!',
            'apartment_list':stringify_list_items(apartment_list),
            'year_list' : [2021,2022,2022,2024],
            'month_list' : generate_month_list(),
            'chargetypelist':["All"],
            'logopath':logo(current_user.company)[0],
            'mobilelogopath':logo(current_user.company)[1],
            'name':current_user.name
            }))
        
    
class BMpesa(Resource):
    """class"""

    def ac_token(self):
        consumer_key = os.getenv("saf_consumer_key")
        consumer_secret=os.getenv("saf_consumer_secret") 
        
        mpesa_auth_url ='https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        data = (requests.get(mpesa_auth_url,auth = HTTPBasicAuth(consumer_key,consumer_secret))).json()
        return data['access_token']

    def express_simulate(self):
        ts = datetime.datetime.now().timestamp()
        saf_password = os.getenv("saf_password")
        mpesa_endpoint = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization":"Bearer %s" % self.ac_token()}
        req_body = {
            "BusinessShortCode":174379,
            "password":saf_password,
            "Timestamp":ts,
            "TransactionType":"CustomerPayBillOnline",
            "Amount":1,
            "PartyA":+254708374149,
            "PartyB":+254708374149,
            "CallBackURL":"localhost:5000/bmpesa",
            "AccountReference":"CompanyXLTD",
            "TransactionDesc":"Payment of X"
        }

        response_data = requests.post(
            mpesa_endpoint,
            json=req_body,
            headers=headers
        )
        return response_data.json()

    @login_required
    def get(self):
        token = self.ac_token()
        express_simulate = self.express_simulate()
        print(express_simulate)
        return make_response(jsonify({
                'message': 'Success',
                'token':token,
                "express_simulate":express_simulate
        }), 200)


    @login_required
    def post(self):
        pass

        