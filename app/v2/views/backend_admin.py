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
from flask_cors import cross_origin
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

class BAllProperties(Resource):
    @cross_origin()
    @login_required
    def get(self):
        target =  request.args.get("target")
        if target == "prop update":
            propid = request.args.get("propid")
            prop_id = get_identifier(propid)
            prop = ApartmentOp.fetch_apartment_by_id(prop_id)
          

            if prop.commission:
                commission = prop.commission
                commtype = "percent"
            else:
                commission = prop.int_commission
                commtype = "static"

            if prop.commission_type:
                if prop.commission_type == "collected":
                    colltype = "collected"
                else:
                    colltype = "projected"
            else:
                colltype = "not set"

            try:
                if prop.paymentdetails.nartype == 'hsenum':
                    nartype = "#HX"
                elif prop.paymentdetails.nartype == "tntnum":
                    nartype = "#TNTXXX"
                else:
                    nartype = ""
            except:
                nartype = ""

            data ={
                "prop":prop,
                "commission":commission,
                "commtype":commtype,
            "colltype":colltype,
            "nartype":nartype

            }
            return make_response(jsonify({
                'message': 'Success',
                'data':data
               
            }), 200)
         
         

        if current_user.username.startswith("xqc"):
            raw_props = ApartmentOp.fetch_all_apartments()
        else:
            raw_props = fetch_all_apartments_by_user(current_user)


        if target != "tenants" and target != "tenant list":
            new_props = ApartmentOp.fetch_all_apartments_createdby_user_id(current_user.id)
            for i in new_props:
                raw_props.append(i)

        props = remove_dups(raw_props)

        items = []
        prop_ids = []
        prop_names = []
        tnt_disp = "dispnone"


        for prop in props:
            tenants = len(tenantauto(prop.id))
            ptnts =len(prop.ptenants)

            if tenants:
                tnt_disp = ""
            houses = len(prop.houses)
            try:
                occupancy = tenants/houses * 100
            except:
                occupancy = 0
                
            occ = f"{occupancy:,.0f}"
            agent_user = UserOp.fetch_user_by_username(prop.agent_id)
    
            if agent_user:
                agent = agent_user.company 
                agent_digest = {
                    'phone':agent.phone, 
                    'remainingsms': agent.remainingsms,
                    'sphone': agent.sphone, 
                    'quotamonth': agent.quotamonth,
                    'id': agent.id, 
                    'description': agent.description,
                    'sms_provider': agent.sms_provider, 
                    'name': agent.name, 
                    'receipt_num': agent.receipt_num,
                    'city': agent.city,
                    'balance': agent.balance, 
                    'region': agent.region, 
                    'subscription': agent.subscription, 
                    'street_address': agent.street_address,
                    'active': agent.active, 
                    'mail_box': agent.mail_box,
                    'billing_period':agent.billing_period, 
                    'email': agent.email,
                    'smsquota': agent.smsquota
                }
            else:"N/A"

            if target == "tenants":
                template = "ajax_prop_tenants.html" 
                dict_obj = {
                    'id':prop.id,
                    'identity':"prp"+str(prop.id),
                    'editid':"edit"+str(prop.id),
                    'delid':"del"+str(prop.id),
                    'name':prop.name,
                    'houses':houses,
                    'tenants':tenants,
                    'ptenants':ptnts,
                    'vacant':houses - tenants,
                    'reminders':f'<span class="text-success font-weight-bold">{prop.reminder_status}</span>' if prop.reminder_status == "sent" else f'<span class="text-danger font-weight-bold">{prop.reminder_status}</span>',
                    'occupancy':occ,
                    'createdby':prop.user_id,
                }

            elif target == "tenant list":
                template = "ajax_prop_tenant_list.html" 
                dict_obj = {
                    'id':prop.id,
                    'identity':"prp"+str(prop.id),
                    'editid':"edit"+str(prop.id),
                    'delid':"del"+str(prop.id),
                    'name':prop.name,
                    'houses':houses,
                    'tenants':tenants,
                    'ptenants':ptnts,
                    'vacant':houses - tenants,
                    'reminders':f'<span class="text-success font-weight-bold">Sent</span>' if prop.reminder_status else '<span class="text-danger font-weight-bold">Not yet</span>',
                    'occupancy':occ,
                    'createdby':prop.user_id,
                }

            else:
                template = "ajax_allprops_detail.html"
                dict_obj = {
                    'id':prop.id,
                    'identity':"prp"+str(prop.id),
                    'editid':"edit"+str(prop.id),
                    'delid':"del"+str(prop.id),
                    'name':prop.name,
                    'owner':prop.owner.name,
                    # 'agent':agent_digest,
                    'houses':houses,
                    'tenants':tenants,
                    'ptenants':ptnts,
                    'reminders':f'<span class="text-success font-weight-bold">{prop.reminder_status}</span>' if prop.reminder_status else '<span class="text-danger font-weight-bold">not yet</span>',
                    'occupancy':occ,
                    'status':"active",
                    'link':'<i class="fas fa-share-alt mr-1 text-success"></i><span class="text-gray-900">link</span>' if not prop.company_id else '<i class="fas fa-sign-out-alt mr-1 text-danger"></i><span class="text-gray-900">unlink</span>',
                    'link-target':"btn-outline-success" if not prop.company_id else "btn-outline-danger",
                    'client-disp':"" if current_user.id == 1 else "dispnone",
                    # 'unlink-disp':"dispnone" if not prop.company_id else "",
                    'createdby':prop.user_id,
                }

            # prop_name_dict = {
            #     "prp"+str(prop.id):prop.name
            # }


            items.append(dict_obj)
            # prop_names.append(prop_name_dict)
            prop_ids.append(prop.id)
            prop_ids.append("prp"+str(prop.id))
            prop_ids.append("edit"+str(prop.id))
            prop_ids.append("del"+str(prop.id))

        propids = ','.join(map(str, prop_ids))

        access = {
            'client-disp':"" if current_user.id == 1 else "dispnone"
        }

        user_company ={

            'sphone': current_user.company.sphone,
            'sms_provider': current_user.company.sms_provider,
            'id': current_user.company.id, 
            'description': current_user.company.description,
                'name': current_user.company.name, 
                'balance': current_user.company.balance,
                'city': current_user.company.city,
                'subscription': current_user.company.subscription,
                'region': current_user.company.region, 
                'active': current_user.company.active, 
                'street_address': current_user.company.street_address,
                'billing_period':current_user.company.billing_period, 
                'mail_box': current_user.company.mail_box, 
                'smsquota': current_user.company.smsquota,
                    'email': current_user.company.email, 
                    'remainingsms': current_user.company.remainingsms,
                    'phone': current_user.company.phone, 
                    'quotamonth': current_user.company.quotamonth
         }
      
  
        return make_response(jsonify({
                'message': 'Success',
                "propids":propids,
                "props":stringify_list_items(props),
                "prop":None,
                "items":items,
                "tnt_disp":tnt_disp,
                "access":access,
                "company":user_company

        }), 200)
        
    
    
    def post(self):
        target = request.form.get("target")
        prop_id = request.form.get("propid")

        prop = ApartmentOp.fetch_apartment_by_id(get_identifier(prop_id))

        if target == "update prop":
            propname = request.form.get("name")
            colltype = request.form.get("colltype")
            commtype = request.form.get("commtype")
            commission = request.form.get("commission")

            valid_commission = validate_input(commission)

            if propname:
                prop_name = propname.title()
                existing_prop = ApartmentOp.fetch_apartment_by_name(propname)
                if existing_prop and prop.name != propname:
                    return err + "name already taken"

            if commtype == "percent":
                ApartmentOp.update_commission(prop,valid_commission)
            else:
                ApartmentOp.update_int_commission(prop,valid_commission)

            ApartmentOp.update_details(prop,prop_name,colltype)

            return "Updated successfully" + proceed

        if target == "update prop billing info":
            props = []
            if prop.company.name == "Latitude Properties":
                props = prop.company.props

            if not props:
                props.append(prop)
            
            for p in props:

                bankbranch = request.form.get("bankbranch")
                bankname = request.form.get("bankname")
                bankaccountname = request.form.get("bankaccountname")
                bankaccountnumber = request.form.get("bankaccountnumber")
                bankpaybill = request.form.get("bankpaybill")

                mpesapaybill = request.form.get("mpesapaybill")

                nartype = request.form.get("nartype")
                paytype = request.form.get("paytype")

                print("heeeeeey",nartype,paytype)

                payment_details_obj = p.paymentdetails
                if not payment_details_obj:
                    print("noooooonnnoonooo",p.paymentdetails)
                    p = PaymentDetailOp(paytype,nartype,mpesapaybill,bankname,bankbranch,bankaccountname,bankaccountnumber,bankpaybill,p.id)
                    p.save()
                else:
                    PaymentDetailOp.update_details(payment_details_obj,paytype,nartype,mpesapaybill,bankname,bankbranch,bankaccountname,bankaccountnumber,bankpaybill)
                    print("herereeeeeeeeeeeeee",p.paymentdetails,nartype)

            # ApartmentOp.update_tenant_account_payment(prop,"PayBill",prop.name,paybill_no)
            # ApartmentOp.update_landlord_bank_details(prop,bank,accname,accno)

            return "Updated successfully" + proceed






class BAddProp(Resource):
    @login_required
    def get(self):
        # target = request.args.get("target")
        # if target == "owners":
        #     owners = []
        #     props = fetch_all_apartments_by_user(current_user)
        #     for prop in props:
        #         owners.append(prop.owner)
        #     all_owners = OwnerOp.fetch_all_owners()
        #     for owner in all_owners:
        #         if owner.user_id == current_user.id:
        #             owners.append(owner)
            
        #     filtered_owners = remove_dups(owners)
        #     return render_template('ajax_multivariable.html',items=filtered_owners,placeholder="select owner")

        # if target == "regions":
        #     regions = LocationOp.fetch_all_locations()
        regions = LocationOp.fetch_all_locations()

        return make_response(jsonify({"items":stringify_list_items(regions)}), 200)
        

            

    @login_required
    def post(self):
        
        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400

     
        target = data.get('target')

        if target == "excelupload":
            file = request.files.get('file')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            if sheet:
                if len(sheet.row_values(1)) != 4:
                    data_format_error = True

            try:
                if data_format_error:
                    
                    nonexistent_item = sheet.row_values(1)[1000000]

                for row in rows:
                    prop = sheet.row_values(row)[0]
                    region = sheet.row_values(row)[1]
                    owner = sheet.row_values(row)[2] if sheet.row_values(row)[2] else ""
                    if sheet.row_values(row)[3]:
                        tel = "0" + str(int(sheet.row_values(row)[3])) if not str(int(sheet.row_values(row)[3])).startswith("0") else str(int(sheet.row_values(row)[3]))
                    else:
                        tel = "N/A"

                    agency = "True"

                    
                    print("VALUES",prop,region,owner,tel,agency)

                    housecode = prop.title()
                    code_obj = ApartmentOp.fetch_apartment_by_name(housecode)


                    if code_obj:
                        print("Skipping ",housecode)
                        continue
                        
                    else:
                        if not owner:
                            owner = current_user.company.name.title()
                        
                        # tel = request.form.get("tel")
                        if not tel or tel == "N/A":
                            tel = "N/A"
                            landlord = OwnerOp(owner.title(),tel,None,"N/A",current_user.id)
                            landlord.save()

                        else:
                            landlord  = OwnerOp.fetch_owner_by_phone(tel)
                            if not landlord:
                                landlord = OwnerOp(owner.title(),tel,None,"N/A",current_user.id)
                                landlord.save()

                        if not region:
                            region = "Nairobi"

                        location = LocationOp.fetch_location(region.title())
                        if not location:
                            location = LocationOp(region.title(),None)
                            location.save()


                        if not agency:
                            agency = "False"

                        bool_value = return_bool(agency)

                        if not prop:
                            print("Property name blank")
                            continue
                    
                        
                        apartment_obj = ApartmentOp(prop.title(),None,location.id,landlord.id,bool_value,current_user.id)
                        apartment_obj.save()


                return '<span class="text-success">Upload successful</span>'

            except Exception as e:
                if not sheet:
                    print("FILE FORMAT UPLOADED NOT SUPPORTED")
                    return '<span class="text-danger">File format not supported</span>'
                elif type(e) == IndexError:
                    print("FILE DATA FIELDS INCORRECT")
                    return '<span class="text-danger">File data fields incorrect</span>'
                else:
                    print("RARE FATAL CASE: Error occured while saving item: ",e)
                    abort(403)



        prop = data.get("prop")
        if not prop:
             return jsonify({'msg': 'Missing Property Name'})
        agency = True
       

        present = ApartmentOp.fetch_apartment_by_name(prop.title())
        if present:
            print("SIMILAR PROP EXISTS >> ",present.name)
            return make_response(jsonify({'msg':'similar apartments exists'}))
            # abort(403)
            # return f'<span class="text-danger">Similar apartment exists</span>'

        owner = data.get("landlord")
        if not owner:
            owner = current_user.company.name.title()
        

        tel = request.form.get("tel") #TO DO, UPDATE APARTMENT OWNER IN THE APARTMENT TABLE
        if not tel:
            print("###############################################")
            tel = "N/A"
            landlord = OwnerOp(owner,tel,None,"N/A",current_user.id)
            landlord.save()
            print("###############################################")


        else:
            landlord  = OwnerOp.fetch_owner_by_phone(tel)
            if not landlord:
                print("###############################################")
                landlord = OwnerOp(owner,tel,None,"N/A",current_user.id)
                landlord.save()
                print("###############################################")

        region = data.get("region")
        if not region:
            region = "Nairobi"

        location = LocationOp.fetch_location(region.title())
        if not location:

            print("###############################################")
            location = LocationOp(region.title(),None)
            location.save()
            print("###############################################")



        if not agency:
            agency = "False"

        bool_value = return_bool(agency)

        if not prop:
            return make_response(jsonify({'msg': 'property name missing'}))
           
    
        
        apartment_obj = ApartmentOp(prop.title(),None,location.id,landlord.id,bool_value,current_user.id)
        apartment_obj.save()

        # owner_obj = OwnerOp.fetch_owner_by_uniquename(owner)
        # # OwnerOp.update_natid(owner_obj,"33150408") 
        # owner_natid = owner_obj.national_id
        # if owner_natid:
        #     owner_user = UserOp.fetch_user_by_national_id(owner_natid)
        #     ApartmentOp.relate(apartment_obj,owner_user)
        #     UserOp.update_status(owner_user,True)

        #     if not bool_value:
        #         owner_co_id = owner_user.company_id
        #         ApartmentOp.update_company(apartment_obj,owner_co_id)

        return make_response(jsonify({'msg': 'property added succesfully','property':prop }))
