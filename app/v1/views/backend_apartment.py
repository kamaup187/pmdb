# from app.v1.models import datamodel
from re import S
import time
import os
from dateutil.parser import parse

import cloudinary as Cloud
from sqlalchemy.sql.expression import except_
# from sqlalchemy import inspect
from werkzeug.utils import secure_filename

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from flask_mail import Message
from flask_login import login_required, current_user
from flask_restful import Resource, abort
from flask import render_template,Response,request,flash,redirect,url_for,make_response,jsonify
from dateutil.relativedelta import relativedelta
from sqlalchemy import exc
from app.v1.models.operations import *
from .helperfuncs import *
from .advanta import *
from operator import add
from app import sms
from app import mail

from flask_cors import cross_origin
# from rq import Queue
# from rq.job import Job
# from worker import conn
# q = Queue(connection=conn)

Cloud.config.update = ({
    'cloud_name':os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
})



class BComStats(Resource):
    @cross_origin()
    @login_required
    def get(self):
        data = request.get_json()
        if data:
            com= data.get('com')
        else:
            com="All clients"
        
        com = request.args.get('com')

        time = datetime.datetime.now()
       

        present_month = time.month
        present_year = time.year

            
        monthly_collection=[] #list of amounts from all payment objs
        client_balances=[]
        monthly_bill_members=[] #list of monthlybill amounts from monthly charge objs

        clientlist = CompanyOp.fetch_all_companies()

        print("ALL CLIENTS LISTED:")
        for cl in clientlist:
            print("COMPANY"," ",cl.id," ",cl.name," ","ACTIVE?",cl.active)

        com_obj = CompanyOp.fetch_company_by_name(com)

        clients = []

        if com == "All clients":
            comonfocus = "All Clients"
            clients = clientlist
        elif com_obj:
            if com_obj in clientlist:
                comonfocus = fname_extracter(str(com_obj))
                clients.append(com_obj)
            else:
                comonfocus = fname_extracter(str(clientlist[0]))
                clients.append(clientlist[0])
        else:
            comonfocus = fname_extracter(str(clientlist[0]))
            clients = clientlist

        dashboard_coms = []

        for i in clientlist:
            dashboard_coms.append(i.name)

        for client in clients:
            
            db.session.expire(client)

            bal_item = client.balance
            if bal_item:
                client_balances.append(bal_item)

            #######################################
            monthly_bills = client.bills
            for item in monthly_bills:
                if item.month == present_month and item.year == present_year:
                    sum_member = item.total
                    monthly_bill_members.append(sum_member)

            payment_collection = client.payments
            for item in payment_collection:
                if item.pay_period.month == present_month and item.pay_period.year == present_year:
                    sum_member = item.amount
                    monthly_collection.append(sum_member)             


        ############################################################
        monthly_bill_total = sum_positive_values(monthly_bill_members)
        monthly_total = sum_positive_values(monthly_collection)
        monthlybal_total = sum_positive_values(client_balances)
        ############################################################    
        formatted_monthly_bill_total = (f"{monthly_bill_total:,.1f}")    
        formatted_monthly_total = (f"{monthly_total:,}")
        formatted_monthlybal_total = (f"{monthlybal_total:,}")
        ############################################################


        data = {
            "month_string":get_str_mnth(present_month),
            "monthly_bills":formatted_monthly_bill_total,
            "monthly_rent_collection":formatted_monthly_total,
            "monthly_bal":formatted_monthlybal_total,
            "comonfocus":comonfocus,
            "clients" : dashboard_coms
        }
        usergroup = current_user.user_group
        user_group = str(usergroup)

        if user_group != "Admin":
            pass

        else:
            dashboard_coms.append("All clients")       
            
        return make_response(jsonify({
                "message": "Success",
                "data":data
            }), 200)    

class BComGraphStats(Resource):
    @cross_origin()
    @login_required
    def get(self):

        data = request.get_json()
        if data:
            com= data.get('com')
        else:
            com="All clients"

        time = datetime.datetime.now()
                   
        monthly_collection=[] #list of amounts from all payment objs

        clientlist = CompanyOp.fetch_all_companies()

        com_obj = CompanyOp.fetch_company_by_name(com)

        users = len(UserOp.fetch_all_users())

        clients = []
        active_clients = []
        props = []
        houses = []
        tenants = []
        active_tenants = []
        sms_spent = 0
        actual_cost = 0.0


        if com == "All clients":
            clients = clientlist
        elif com_obj:
            if com_obj in clientlist:
                clients.append(com_obj)
            else:
                clients.append(clientlist[0])
        else:

            clients.append(clientlist[0])


        for client in clients:
            # total_tenants = 0 #for setting sms quota only
            db.session.expire(client)

            props.append(client.props)

            if client.active:
                active_clients.append(client)
                       
            for prop in client.props:
                prop_tenants = tenantauto(prop.id)
                active_tenants.append(prop_tenants)
                # total_tenants += len(prop_tenants) #for setting sms quota only
                houses.append(prop.houses)
                tenants.append(prop.tenants)

            # CompanyOp.set_smsquota(client,total_tenants * 4) #for setting sms quota only

            try:
                co_smsspent = client.smsquota - client.remainingsms
                # co_smsspent += 50 #URGENT TODO REMOVE THIS 50
                sms_spent += co_smsspent
                actual_spent = co_smsspent * 0.8
                actual_cost += actual_spent
            except Exception as e:
                print("This company has", e ,"problems",client)

            payment_collection = client.payments
            for item in payment_collection:
                if item.pay_period.month == time.month and item.pay_period.year == time.year:
                    sum_member = item.amount
                    monthly_collection.append(sum_member) 
                    
        chart_string = ','.join(map(str, monthly_collection))   

        data = {
            "chartstring":chart_string,
            "clients" : len(clients),
            "active_clients" : len(active_clients),
            "registered_users": users,
            "props" : len(flatten(props)),
            "houses" : len(flatten(houses)),
            "tenants" : len(flatten(tenants)),
            "active_tenants" : len(flatten(active_tenants)),
            "smsestimate" : len(flatten(active_tenants))*3,
            "smssent" : sms_spent,
            "actualcosts" : f"Kshs {actual_cost:,.1f}"

        }

        return make_response(jsonify({
                "message": "Success",
                "data":data
            }), 200)    
            
    
            

class BRegisterOwner(Resource):
    """This class registers an owner."""
    @login_required
    def post(self):
        """ Handle POST request for this view. Url ---> /add/owner """
        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400
        
        email= data.get('email')
        fname= data.get('fname')
        lname= data.get('lname')
        ftel= data.get('ftel')
        ltel= data.get('ltel')


        created_by = current_user.id
        name = fname+" "+lname
        tel_validation = ValidatePass.validate_password(ftel,ltel)
        if not tel_validation:
            return make_response(jsonify({
                "message": "Please provide owners' mobile number"
            }), 400)    
        if tel_validation == "no match":
            return make_response(jsonify({
                "message": "Please check the mobile number and try again"     
            }), 400) 
        else:
            phone = ftel


        uniquename = uniquename_generator(name,phone)
        is_present  = OwnerOp.fetch_owner_by_uniquename(uniquename)
        is_present2  = OwnerOp.fetch_owner_by_phone(phone)
        
        
        if is_present:
          
            return make_response(jsonify({
                "message": "Record exists in the database already"
            }), 200)      


        if is_present2:
            return make_response(jsonify({
                "message": "Owner with similar mobile number already registered"
            }), 200)      


        owner = OwnerOp(name,phone,email,uniquename,created_by)
        owner.save()

        owner_user = UserOp.fetch_user_by_phone(phone)
        
        if owner_user:
            natid = owner_user.national_id
            OwnerOp.update_natid(owner,natid)
            UserOp.update_status(owner_user,True)

        msg='Success, add apartments below.'
        flash(msg,"success")
        return make_response(jsonify({
                "message": "Success, add apartments next",
                "data":data
            }), 200)      

