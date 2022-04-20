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
from flask import render_template,Response,request,flash,redirect,url_for,send_file,after_this_request
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

class Robots(Resource):
    def get (self):
        path = "robots.txt"
        return send_file(path, as_attachment=True)

class DownloadTemplate(Resource):
    def get (self,file):
        path = f"files/{file}.xls"
        return send_file(path, as_attachment=True)

class ViewReceipt(Resource):
    def get (self,ri):
        path = f"temp/receipt_{ri}.pdf"

        if len(ri) < 10:
            co = CompanyOp.fetch_company_by_name("KiotaPay")
            return Response(render_template(
                    'user_nolink_receipt.html',
                    company=co,
                    logopath=logo(co)[0]
                ))
        payment_obj = PaymentOp.fetch_payment_by_rand_id(ri)
        if not payment_obj:
            co = CompanyOp.fetch_company_by_name("KiotaPay")
            return Response(render_template(
                    'user_no_receipt.html',
                    company=co,
                    logopath=logo(co)[0]
                ))

        if payment_obj.voided:
            disp = ""
        else:
            disp = "dispnone"

        prop = payment_obj.apartment
        co = prop.company

        p = inflect.engine()
        int_amount = int(payment_obj.amount)
        str_amount = p.number_to_words(int_amount)
        stramount = str_amount.capitalize()

        paydate = payment_obj.pay_date if payment_obj.pay_date else payment_obj.date
        payperiod = payment_obj.pay_period if payment_obj.pay_period else payment_obj.date


        if payment_obj.charged_amount < 1:
            bill = 0.0
        else:
            bill = f"{payment_obj.charged_amount:,.0f}"

        paid = f'Kes {payment_obj.amount:,.0f}'

        if payment_obj.balance > -1:
            baltitle = "Balance"
            outline = "text-danger"
            bal = f"KES {payment_obj.balance:,.0f}"
        else:
            baltitle = "Advance"
            outline = "text-success"
            bal = f"KES {payment_obj.balance*-1:,.0f}"

        server = fname_extracter(UserOp.fetch_user_by_id(payment_obj.user_id).name)

        if payment_obj.receipt_num:
            receiptno = payment_obj.receipt_num
        else:
            receiptno = payment_obj.id

        return Response(render_template(
            'user_receipt.html',
            voided = disp,
            tenant = payment_obj.tenant.name,
            house= payment_obj.house.name,
            amount=paid,
            str_amount=stramount,
            str_month=get_str_month(payperiod.month),
            paydate=paydate.strftime("%d/%b/%y"),
            paytime=paydate.strftime("%X"),
            bill=bill,
            baltitle=baltitle,
            outline=outline,
            balance=bal,
            chargetype=payment_obj.payment_name,
            receiptno=receiptno,
            refnum=payment_obj.ref_number,
            paymode=payment_obj.paymode,
            logopath=logo(co)[0],
            company=co,
            user=server,
            prop= prop,
            randid=ri
        ))

class UserActivation(Resource):
    def get (self,ri):
        
        user = UserOp.fetch_user_by_link(ri)
        if not user:
            print("chekererere")
        else:
            UserOp.update_status(user,True)
            login_user(user, remember=False)
            return redirect(url_for("api.index"))

class DemoAccess(Resource):
    def get (self,ri):
        
        user = UserOp.fetch_user_by_link(ri)
        if ri != "zjdqjpvnkgblhfweikkiloukrqcwijaofdf":
            print("zhekererere")
        else:
            return redirect(url_for("api.demo"))

class DownloadReceipt(Resource):
    """class"""
    def get(self,ri):

        rand_id = request.args.get('randid')

        print("AWESOME HERE",rand_id)

        if not rand_id:
            rand_id = ri

        payment_obj = PaymentOp.fetch_payment_by_rand_id(rand_id)

        if payment_obj:
            prop = payment_obj.apartment

            tenant = payment_obj.tenant
            co = prop.company

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
                bal = f"KES {payment_obj.balance:,.0f}"
            else:
                baltitle = "Advance"
                outline = "text-success"
                bal = f"KES {payment_obj.balance*-1:,.0f}"

            server = fname_extracter(UserOp.fetch_user_by_id(payment_obj.user_id).name)

            if payment_obj.voided:
                disp = ""
            else:
                disp = "dispnone"

            mail_logo = "../" + logo(co)[0]

            if payment_obj.receipt_num:
                receiptno = payment_obj.receipt_num
            else:
                receiptno = payment_obj.id

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
                "receiptno":receiptno,
                "refnum":payment_obj.ref_number,
                "paymode":payment_obj.paymode,
                "logopath":mail_logo,
                "company":co,
                "user":server,
                "prop":prop
            }

            html_out = template.render(template_vars)
            filename = f"app/temp/receipt_{rand_id}.pdf"
            HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/myfonts.css","app/static/eapartment-min.css","app/static/kiotapay.css","app/static/receipt.css"])

            path = f"temp/receipt_{rand_id}.pdf"

            @after_this_request
            def remove_file(response):
                try:
                    filename = f"app/{path}"
                    os.remove(filename)
                except Exception as error:
                    print ("Error removing or closing downloaded file handle", error)
                return response

            try:
                return send_file(path, as_attachment=True)
            except Exception as e:
                return "This receipt is longer available on our server "+ str(e)

class DownloadInvoice(Resource):
    """class"""
    def get(self,ri):

        rand_id = request.args.get('randid')

        print("INVOICE IS BEING ACCESSSSSSSSSSSSSSSSEEEEEEEEEDDDDD",rand_id)

        if not rand_id:
            rand_id = ri

        bill = MonthlyChargeOp.fetch_specific_bill(rand_id)

        if bill:

            co = bill.apartment.company
    
            invnum = bill.id + 13285

            house = bill.house

            tenant = bill.tenant

            sibling_water_bill = fetch_current_billing_period_readings(bill.apartment.billing_period,bill.house.meter_readings)

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
                smsbill = (f"Kes {amount:,.2f} ")

                wmessage = f"Last reading: {smslastreading} Current reading: {smscurrentreading} Units: {smsunits} {smsstd} Water: {smsbill}"
            else:
                wmessage = ""
                smsbill = "Kes 0.0"

            arrears = bill.arrears
            
            calculated_total = 0.0
            if bill.paid_amount and arrears > 0:
                if arrears <= bill.paid_amount:
                    calculated_total = bill.total_bill - arrears
                    arrears = 0.0
                else:
                    arrears = bill.arrears - bill.paid_amount
                    calculated_total = bill.total_bill - bill.paid_amount

            smsrent = f"Rent:{bill.rent:,}," if bill.rent else ""

            if wmessage:
                smswater = wmessage
            else:
                smswater = f"KES {bill.water}," if bill.water else ""


            smsgarb = f"Garbage:{bill.garbage}," if bill.garbage else ""
            smssec = f"Security:{bill.security}," if bill.security else ""
            smselec = f"Electricity:{bill.electricity}," if bill.electricity else ""
            smsdep = f"Deposit:{bill.deposit}" if bill.deposit else ""
            smsarrears = f"Arrears:{arrears}" if arrears else ""
            smstotal = (f"{bill.total_bill:,.1f}") if not calculated_total else (f"{calculated_total:,.1f}")


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

            mail_logo = "../" + logo(co)[0]
            # mail_2 = maillogo(co)[0]
            mail_slogo = "../" + logo(kiotapay)[1]

            print(mail_logo,"<<<<<<<<<<<<<<<<<<<<<<<<<<<",mail_logo)

            template_vars = {
                "bill":bill,
                "readings" : wbill,
                "waterbill":smsbill,
                "house":house,
                "total":f"{bill.total_bill:,.2f}",
                "invdate":inv_date,
                "invdue":inv_due,
                "client":tenant,
                "company":co,
                "invnum":invnum,
                "logo":mail_logo,
                "slogo":mail_slogo
            }

            html_out = template.render(template_vars)
            filename = f"app/temp/inv_{rand_id}.pdf"
            HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/myfonts.css","app/static/eapartment-min.css","app/static/kiotapay.css"])

            path = f"temp/inv_{rand_id}.pdf"

            @after_this_request
            def remove_file(response):
                try:
                    filename = f"app/{path}"
                    os.remove(filename)
                except Exception as error:
                    print ("Error removing or closing downloaded file handle", error)
                return response

            try:
                return send_file(path, as_attachment=True)
            except Exception as e:
                return "This receipt is longer available on our server "+ str(e)

class DeleteReceipt(Resource):
    def get(self,propid):
        deleted = False
        try:
            prop_id = int(propid)
        except:
            return "Wrong prop id"

        prop = ApartmentOp.fetch_apartment_by_id(prop_id)
        payments = prop.payment_data
        for i in payments:
            if i.rand_id:
                filename = f"app/temp/receipt_{i.rand_id}.pdf"
                try:
                    # os.remove(filename)
                    # deleted = True
                    pass
                except:
                    print("File does not exist for payment no.",i.id)

        if deleted:
            return "Deleted some"
        else:
            return "Non deleted"

class AllProperties(Resource):
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

            return render_template("ajax_prop_form.html",prop=prop,commission=commission,commtype=commtype,colltype=colltype)

        raw_props = fetch_all_apartments_by_user(current_user)
        if target != "tenants" and target != "tenant list":
            new_props = ApartmentOp.fetch_all_apartments_createdby_user_id(current_user.id)
            for i in new_props:
                raw_props.append(i)

        props = remove_dups(raw_props)

        items = []
        prop_ids = []
        prop_names = []

        template = "ajax_allprops_detail.html"
        
        for prop in props:
            tenants = len(tenantauto(prop.id))
            houses = len(prop.houses)
            try:
                occupancy = tenants/houses * 100
            except:
                occupancy = 0
                
            occ = f"{occupancy:,.0f}"
            agent_user = UserOp.fetch_user_by_username(prop.agent_id)
            agent = agent_user.company if agent_user else "N/A"

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
                    'agent':agent,
                    'houses':houses,
                    'tenants':tenants,
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


        return render_template(template,propids=propids,props=props,prop=None,items=items,access=access,company=current_user.company)
    
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
            bank = request.form.get("bank")
            accname = request.form.get("accname")
            accno = request.form.get("accno")

            paybill_no = request.form.get("paybill")


            ApartmentOp.update_tenant_account_payment(prop,"PayBill",prop.name,paybill_no)
            ApartmentOp.update_landlord_bank_details(prop,bank,accname,accno)

            return "Updated successfully" + proceed


class AllOwners(Resource):
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

        return render_template("ajax_owners.html",propids=propids,items=items,company=current_user.company)


class AddProp(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")
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

        if target == "regions":
            regions = LocationOp.fetch_all_locations()
            return render_template('ajax_datalist.html',items=regions,placeholder="select region")


    @login_required
    def post(self):

        target = request.form.get('target')

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



        prop = request.form.get("prop")
        agency = request.form.get("agency")

        present = ApartmentOp.fetch_apartment_by_name(prop.title())
        if present:
            print("SIMILAR PROP EXISTS >> ",present.name)
            abort(403)
            # return f'<span class="text-danger">Similar apartment exists</span>'

        owner = request.form.get("landlord")
        if not owner:
            owner = current_user.company.name.title()
        

        tel = request.form.get("tel")
        if not tel:
            tel = "N/A"
            landlord = OwnerOp(owner,tel,None,"N/A",current_user.id)
            landlord.save()

        else:
            landlord  = OwnerOp.fetch_owner_by_phone(tel)
            if not landlord:
                landlord = OwnerOp(owner,tel,None,"N/A",current_user.id)
                landlord.save()

        region = request.form.get("region")
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
            return f'<span class="text-danger">Proprty name missing</span>'
    
        
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

        return f'<span class="text-success">{prop} added successfully</span>'

class AddOwner(Resource):
    @login_required
    def get(self):
        pass
    def post(self):

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        phone = request.form.get('tel')

        created_by = current_user.id

        name = fname+" "+lname

        if not phone or not fname or not lname:
            return f'<span class="text-danger">Please fill all the fields before submitting</span>'
        

        uniquename = uniquename_generator(name,phone)
        is_present  = OwnerOp.fetch_owner_by_uniquename(uniquename)
        is_present2  = OwnerOp.fetch_owner_by_phone(phone)
        
        
        if is_present:
            return f'<span class="text-danger">Record exists in the database already</span>'

        if is_present2:
            return f'<span class="text-danger">Record exists in the database already</span>'

        owner = OwnerOp(name,phone,None,uniquename,created_by)
        owner.save()

        owner_user = UserOp.fetch_user_by_phone(phone)
        
        if owner_user:
            natid = owner_user.national_id
            OwnerOp.update_natid(owner,natid)
            UserOp.update_status(owner_user,True)

        return f'<span class="text-success">Success</span>'

class AddRegion(Resource):
    @login_required
    def get(self):
        pass
    def post(self):
        name = request.form.get("name")
        loc_obj = LocationOp.fetch_location(name)
        if not loc_obj:
            region_obj = LocationOp(name,None)
            region_obj.save()
        else:
            print("Location exists already")

        return f'<span class="text-success">Success</span>'


class LinkProperty(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")

        if target == "link":
            if current_user.id == 1:
                companies = CompanyOp.fetch_all_companies()
            else:
                companies = [current_user.company]
            return render_template('ajax_multivariable.html',items=companies,placeholder="select company")
        else:
            companies = []
            return render_template('ajax_multivariable.html',items=companies,placeholder="ready to unlink")

    def post(self):
        propid = request.form.get("propid")
        co = request.form.get("company")
        target = request.form.get("target")

        prop = ApartmentOp.fetch_apartment_by_id(propid)

        if target == "link":
            company = CompanyOp.fetch_company_by_name(co)

            agent_obj = None

            co_users = company.users
            for user in co_users:
                if user.user_group_id == 3:
                    agent_obj = user
                    break

            if agent_obj:
                ApartmentOp.relate(prop,agent_obj)
                print(agent_obj," given access to ",prop)
                UserOp.update_status(agent_obj,True)
                ApartmentOp.update_agent(prop,agent_obj.username)
                if prop.agency_managed:
                    ApartmentOp.update_company(prop,company.id)

                    company_users = company.users
                    for i in company_users:
                        if i.user_group_id == 4:
                            ApartmentOp.relate(prop,i)
                            print("user added to ",str(prop))

            else:
                print(prop.agency_managed)
                if not prop.agency_managed:
                    ApartmentOp.update_company(prop,company.id)
                    company_users = company.users
                    for i in company_users:
                        if i.user_group_id == 4:
                            ApartmentOp.relate(prop,i)
                            print("user added to ",str(prop))

        else:
            access = True
            # if current_user.id == 1:
            if access:
                if prop.agency_managed:
                    agent_obj = UserOp.fetch_user_by_username(prop.agent_id)

                    ApartmentOp.terminate(prop,agent_obj)
                    print("Agent terminated from ",prop)
                    ApartmentOp.update_agent(prop,None)

                    agent_co = agent_obj.company
                    ApartmentOp.update_company(prop,None)

                    company_users = agent_co.users
                    for i in company_users:
                        print("These are users",company_users)
                        if i.user_group_id == 4:
                            current_user_apartments = fetch_all_apartments_by_user(i)
                            if prop in current_user_apartments:
                                ApartmentOp.terminate(prop,i)
                                print("user removed from ",prop)
                            else:
                                print("User did not have access to", prop)
                    msg = "Operation complete"
                    return msg
                else:
                    prop_co = CompanyOp.fetch_company_by_id(prop.company_id)
                    ApartmentOp.update_company(prop,None)
                    company_users = prop_co.users
                    for i in company_users:
                        print("These are users",company_users)
                        if i.user_group_id == 4:
                            current_user_apartments = fetch_all_apartments_by_user(i)
                            if prop in current_user_apartments:
                                ApartmentOp.terminate(prop,i)
                                print("user removed from ",prop)
                            else:
                                print("User did not have access to", prop)
            else:
                msg = "You do not have permission to terminate"
                print(msg)
                return msg

class EditProp(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")

        if target == "delete":
            raw_propid = request.args.get("delid")
            propid = get_identifier(raw_propid)
        else:
            raw_propid = request.args.get("editid")
            propid = get_identifier(raw_propid)

        prop = ApartmentOp.fetch_apartment_by_id(propid)
        return f"Name: {prop}"

    @login_required
    def post(self):
        target = request.form.get("target")

        if target == "delete":
            raw_propid = request.form.get("delid")
            propid = get_identifier(raw_propid)
        else:
            raw_propid = request.form.get("editid")
            propid = get_identifier(raw_propid)

        if current_user.username.startswith("qc") or current_user.name == "Test Agent":
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            ApartmentOp.delete(prop)
            return "Property removed successfully"
        else:
            return "You are not allowed to perform this operation"
