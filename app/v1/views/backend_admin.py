# from app.v1.models import datamodel
# import time
import os

import cloudinary as Cloud
# from sqlalchemy import inspect
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from flask_mail import Message
from flask_login import login_required, current_user,login_user
from flask_restful import Resource, abort
from flask import render_template,Response,request,flash,make_response,jsonify,redirect,url_for,send_file,after_this_request
from dateutil.relativedelta import relativedelta
from sqlalchemy import exc

from app.v1.models.operations import *
from .helperfuncs import *
from operator import add

from app import sms
from app import mail

# import logging
# logger = logging.getLogger('weasyprint')
# logger.addHandler(logging.FileHandler('/tmp/weasyprint.log'))

# from rq import Queue
# from rq.job import Job
# from worker import conn
# q = Queue(connection=conn)

Cloud.config.update = ({
    'cloud_name':os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
})







class BAllOwners(Resource):
    def get(self):
        # propa = ApartmentOp.fetch_apartment_by_id(3)
        # print(propa)
        # print(propa.company)
        # print(propa.company_id)
        # com = CompanyOp.fetch_company_by_id(4)
        # print("test props",com.props)
        # print("*********************************************************")
        # ApartmentOp.update_company(propa,None)
        # print("*********************************************************")
        # print(propa.company)
        # print(propa.company_id)
        # com = CompanyOp.fetch_company_by_id(1)
        # print("kiotap props",com.props)

        props = OwnerOp.fetch_all_owners() #TODO URGENT > USE proper naming of owners not props

        items = []
        properties = []
        prop_ids = []
        
        for prop in props:
            properties = ApartmentOp.fetch_all_apartments_by_owner(prop.id)

            #################################################################

            # if prop.name == "Simon Mundati":
            #     user = UserOp.fetch_user_by_national_id(prop.national_id)
            #     propss = fetch_all_apartments_by_user(user)
            #     for item in properties:
            #         if item not in propss:
            #             ApartmentOp.relate(item,user)

            #################################################################

            prop_number = len(properties)
            user_obj = UserOp.fetch_user_by_phone(prop.phone)

            dict_obj = {
                'id':prop.id,
                'editid':"edit"+str(prop.id),
                'delid':"del"+str(prop.id),
                'name':prop.name,
                'natid':prop.national_id,
                'phone':prop.phone,
                'properties':prop_number,
                'acc':"Yes" if user_obj else "No",
                'createdby':prop.user_id,
            }

            items.append(dict_obj)
            prop_ids.append(prop.id)
            prop_ids.append("prp"+str(prop.id))
            prop_ids.append("edit"+str(prop.id))
            prop_ids.append("del"+str(prop.id))

        propids = ','.join(map(str, prop_ids))

        return make_response(jsonify({
                'message': 'Success',
                'data':items
            }), 200)
