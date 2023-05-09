# from app.v1.models import datamodel
# import time
# from curses import raw
import os

import cloudinary as Cloud
# from sqlalchemy import inspect
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from flask_mail import Message
from flask_login import login_required, current_user,login_user
from flask_restful import Resource, abort
from flask import render_template,Response,request,flash,redirect,url_for,send_file,after_this_request,json,jsonify,make_response
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

class GetLeads(Resource):
    @login_required
    def get (self):
        leads = get_leads_api(current_user)
        resp = f"Leads retrieved : {leads[0]}, Leads saved to db : {leads[1]}",
        return resp

class DownloadTemplate(Resource):
    def get (self,file):
        path = f"files/{file}.xls"
        return send_file(path, as_attachment=True)

class QueryResident(Resource):
    def get(self,ri):
        print("QR RESULTS ...",ri)
        resident = PermanentTenantOp.fetch_tenant_by_id(get_identifier(ri))

        co = resident.apartment.company

        return Response(render_template(
            'resident_data.html',
            logopath=logo(co)[0],
            resident = resident,
        )) 
    
class SmsApi(Resource):
    def post(self):

        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        ww = f"{my_json},SMS has sent payload"
        response = sms.send(ww, ["+254716674695"],"KIOTAPAY")

        print("working")

        try:
            data = json.loads(my_json)

            txt = data['message']
            tel = data['mobile']
            username = data['username']
            password = data['password']

            smsid = None

            if username == "leah" and password == "q150c2bf1c4ee7da42yt":

                SMS_API_KEY = "cb63519051b77da317036fe951db1d48"
                SMS_PARTNER_ID = 7155
                SHORTCODE = "LeahDistLtd"

                # SMS_API_KEY = kiotapay_api_key
                # SMS_PARTNER_ID = kiotapay_partner_id
                # SHORTCODE = "Bizline"

                try:
                    report = advanta_send_sms(txt,tel,SMS_API_KEY,SMS_PARTNER_ID,SHORTCODE)
                    smsid = report.get("msgid")

                except Exception as e:
                    print("Error sending SMS" + str(e))
                    
                    response = {
                        "resultCode": 1,
                        "resultDesc": "Unsuccessful, API outage error",
                        "smsId": ""
                    }

                if smsid:

                    response = {
                        "resultCode": 0,
                        "resultDesc": "Successful",
                        "smsId": smsid
                    }
                else:
                    response = {
                        "resultCode": 1,
                        "resultDesc": "Unsuccessful, API outage error",
                        "smsId": ""
                    }
            else:
                response = {
                    "resultCode": 1,
                    "resultDesc": "Invalid credentials",
                    "smsId": ""
                }



        except Exception as e:
            # sms.send(f"SMS integration has error data Error >> {e}", ["+254716674695"],"KIOTAPAY")

            response = {
                "resultCode":1,
                "resultDesc":"Invalid payload",
                "smsId":""
            }                

        resp = jsonify(response)
        return make_response(resp)

class TopUpSms(Resource):
    @login_required
    def get (self,ri):
        co = current_user.company
        if ri:

            tele = current_user.phone
            phonenum = sms_phone_number_formatter(tele)

            # units = ctob_obj.trans_amnt * 1.25
            try:
                units = int(ri) / 0.75
            except:
                return None

            old_units = co.remainingsms
            new_units = int(units) + old_units 

            CompanyOp.set_rem_quota(co,int(new_units))

            if co:

                message = f"Hi {current_user.name}, \n{co.name} has been successfully credited with {int(units)} sms units for payment of KES {ri}. \nAvailable sms units: {new_units}  \n\nThank you."
                sresponse = sms.send(message, ["+254716674695"], sender)

                if co.sms_provider == "Advanta":
                    sms_sender(co.name,message,phonenum)
                else:
                    try:
                        recipient = [phonenum]                
                        response = sms.send(message, recipient, sender)
                        print(response)
                    except Exception as e:
                        print(f"Houston, we have a problem {e}")
            
        
  
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

        address = None

        if payment_obj.receipt_num:
            receiptno = payment_obj.receipt_num
        else:
            receiptno = payment_obj.id

        if payment_obj.ptenant:
            tenant = payment_obj.ptenant
        else:
            tenant = payment_obj.tenant

            address = None

        if payment_obj.apartment.company.name == "LaCasa":
            if prop.id == 419:
                address = {
                    "address": "Nairobi",
                    "tel": "0735267087",
                    "email": "goldlabelservices@gmail.com"
                }
            elif prop.id == 420:
                address = {
                    "address":"Ongata Rongai",
                    "tel":"0735267087",
                    "email":"bizlineinvestment@gmail.com"
                }
            elif prop.id == 421:
                address = {
                    "address":"Mwiki, Kasarani",
                    "tel":"0735267087",
                    "email":"bizlineinvestment@gmail.com"
                }
            elif prop.name == "Baraka House":
                address = {
                    "address":"Mwiki, Kasarani",
                    "tel":"0735267087",
                    "email":"bizlineinvestment@gmail.com"
                }

            else:
                address = {
                    "address":"Mwiki, Kasarani",
                    "tel":"0735267087",
                    "email":"bizlineinvestment@gmail.com"
                }

        return Response(render_template(
            'user_receipt.html',
            voided = "dispnone",
            tenant = tenant.name,
            house= payment_obj.house,
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
            address=address,
            user=server,
            prop=prop,
            randid=ri
        ))

        # return Response(render_template(
        #     'user_receipt.html',
        #     voided = disp,
        #     tenant = tenant.name,
        #     house= payment_obj.house.name,
        #     amount=paid,
        #     str_amount=stramount,
        #     str_month=get_str_month(payperiod.month),
        #     paydate=paydate.strftime("%d/%b/%y"),
        #     paytime=paydate.strftime("%X"),
        #     bill=bill,
        #     baltitle=baltitle,
        #     outline=outline,
        #     balance=bal,
        #     chargetype=payment_obj.payment_name,
        #     receiptno=receiptno,
        #     refnum=payment_obj.ref_number,
        #     paymode=payment_obj.paymode,
        #     logopath=logo(co)[0],
        #     company=co,
        #     user=server,
        #     prop= prop,
        #     randid=ri
        # ))

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

            if payment_obj.ptenant:
                tenant = payment_obj.ptenant
            else:
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

            if co.name == "LaCasa":
                if prop.id == 419:
                    address = {
                        "address": "Nairobi",
                        "tel": "0735267087",
                        "email": "goldlabelservices@gmail.com"
                    }
                elif prop.id == 420:
                    address = {
                        "address":"Ongata Rongai",
                        "tel":"0735267087",
                        "email":"bizlineinvestment@gmail.com"
                    }
                elif prop.id == 421:
                    address = {
                        "address":"Mwiki, Kasarani",
                        "tel":"0735267087",
                        "email":"bizlineinvestment@gmail.com"
                    }
                elif prop.name == "Baraka House":
                    address = {
                        "address":"Mwiki, Kasarani",
                        "tel":"0735267087",
                        "email":"bizlineinvestment@gmail.com"
                    }

                else:
                    address = {
                        "address":"Mwiki, Kasarani",
                        "tel":"0735267087",
                        "email":"bizlineinvestment@gmail.com"
                    }

            else:
                address = None


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
                "address":address,
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

            try:
                if prop.paymentdetails.nartype == 'hsenum':
                    nartype = "#HX"
                elif prop.paymentdetails.nartype == "tntnum":
                    nartype = "#TNTXXX"
                else:
                    nartype = ""
            except:
                nartype = ""

            template = "ajax_prop_form2.html" if crm(current_user) else "ajax_prop_form.html"

            return render_template(template,prop=prop,commission=commission,commtype=commtype,colltype=colltype,nartype=nartype)

        if current_user.username.startswith("qc") or localenv:
            # raw_props = ApartmentOp.fetch_all_unlinked_apartments()
            raw_props = []
        else:
            # raw_props = ApartmentOp.fetch_all_apartments_createdby_user_id(current_user.id)
            raw_props = []

        # raw_props2 = current_user.company.props

            if target != "tenants" and target != "units" and target != "tenant_list": #TODO push back this block
                raw_props = current_user.company.props
        
        if current_user.company_user_group.name == "Sales":
            if target == "tenants" or target == "units":
                raw_props2 = current_user.company.props
            else:
                raw_props2 = []
        else:
            raw_props2 = fetch_all_apartments_by_user(current_user)

        if localenv:
            # raw_props3 = ApartmentOp.fetch_all_apartments()
            raw_props3 = []
            raw_props4 = raw_props + raw_props2 + raw_props3
        else:
            raw_props4 = raw_props + raw_props2

        props = remove_dups(raw_props4)       
        
        items = []
        prop_ids = []
        tnt_disp = "dispnone"

        template = "crm_ajax_allprops_detail.html" if crm(current_user) else "ajax_allprops_detail.html"

        if not crm(current_user):
            if target == "tenants" or target == "tenant list":

                for prop in props:

                    houses = len(prop.houses)
                    tenants = len(tenantauto(prop.id))

                    template = "ajax_prop_tenants.html" if target == "tenants" else "ajax_prop_tenant_list.html"

                    dict_obj = {
                        'id':prop.id,
                        'identity':"prp"+str(prop.id),
                        'editid':"edit"+str(prop.id),
                        'delid':"del"+str(prop.id),
                        'name':prop.name,
                        'houses':houses,
                        'tenants':tenants,
                    }


                    items.append(dict_obj)
                    # prop_names.append(prop_name_dict)
                    prop_ids.append(prop.id)
                    prop_ids.append("prp"+str(prop.id))
                    prop_ids.append("edit"+str(prop.id))
                    prop_ids.append("del"+str(prop.id))

                propids = ','.join(map(str, prop_ids))

                access = {
                    'client-disp':"" if current_user.id == 1 else ""
                    }


                return render_template(template,propids=propids,props=props,prop=None,items=items,access=access,company=current_user.company)

       
        for prop in props:
            houses = len(prop.houses)
            tenants = len(tenantauto(prop.id))
            ptnts =len(prop.ptenants)

            occupancy = filter_in_occupied_houses(prop.name)
            occupancy_num = len(occupancy)

            vacants = houses - occupancy_num

            if tenants:
                tnt_disp = ""

            try:
                occupancy = occupancy_num/houses * 100
            except:
                occupancy = 0
                
            occ = f"{occupancy:,.0f}"

            if target == "tenants":
                template = "ajax_prop_tenants2.html" if crm(current_user) else "ajax_prop_tenants.html"

                dict_obj = {
                    'id':prop.id,
                    'identity':"prp"+str(prop.id),
                    'editid':"edit"+str(prop.id),
                    'delid':"del"+str(prop.id),
                    'name':prop.name,
                    'houses':houses,
                    'tenants':tenants,
                    'ptenants':ptnts,
                    'proposals':len(get_clients_by_status(prop.ptenants,"proposal")),
                    'prospective':len(get_clients_by_status(prop.ptenants,"negotiated")),
                    'invoiced':len(get_clients_by_status(prop.ptenants,"invoiced and contracts") + get_clients_by_status(prop.ptenants,"invoiced and missing contracts")),
                    'closed':len(get_clients_by_status(prop.ptenants,"closed")),
                    'vacant':vacants,
                    'reminders':f'<span class="text-success font-weight-bold">{prop.reminder_status}</span>' if prop.reminder_status == "sent" else f'<span class="text-danger font-weight-bold">{prop.reminder_status}</span>',
                    'occupancy':occ,
                    'createdby':prop.user_id,
                }

            elif target == "units":
                template = "ajax_prop_units2.html"

                dict_obj = {
                    'id':prop.id,
                    'identity':"prp"+str(prop.id),
                    'editid':"edit"+str(prop.id),
                    'delid':"del"+str(prop.id),
                    'name':prop.name,
                    'houses':houses,
                    'tenants':tenants,
                    'ptenants':ptnts,
                    'available':len(get_units_by_status(prop.houses,"available")),
                    'booked':len(get_units_by_status(prop.houses,"booked")),
                    'sold':len(get_units_by_status(prop.houses,"sold")),
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
                template = "crm_ajax_allprops_detail.html" if crm(current_user) else "ajax_allprops_detail.html"

                dict_obj = {
                    'id':prop.id,
                    'identity':"prp"+str(prop.id),
                    'editid':"edit"+str(prop.id),
                    'delid':"del"+str(prop.id),
                    'name':prop.name,
                    'owner':prop.landlord if prop.landlord else "not set",
                    'company':prop.company.name if prop.company else "N/A",
                    'houses':houses,
                    'tenants':tenants,
                    'ptenants':ptnts,
                    'reminders':f'<span class="text-success font-weight-bold">{prop.reminder_status}</span>' if prop.reminder_status else '<span class="text-danger font-weight-bold">not yet</span>',
                    'occupancy':occ,
                    'status':prop.property_type,
                    'link':'<i class="fas fa-share-alt mr-1 text-success"></i><span class="text-gray-900">link</span>' if not prop.company_id else '<i class="fas fa-sign-out-alt mr-1 text-danger"></i><span class="text-gray-900">unlink</span>',
                    'link-target':"btn-outline-success" if not prop.company_id else "btn-outline-danger",
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
            'client-disp':"" if current_user.id == 1 else ""
        }


        return render_template(template,propids=propids,props=props,prop=None,items=items,tnt_disp=tnt_disp,access=access,company=current_user.company)
    
    def post(self):
        target = request.form.get("target")
        prop_id = request.form.get("propid")

        prop = ApartmentOp.fetch_apartment_by_id(get_identifier(prop_id))

        if target == "update prop contact info":
            email = request.form.get("email")
            tel = request.form.get("tel")
            address = request.form.get("address")

            ApartmentOp.update_contact_info(prop, email, tel, address)

            return "Updated successfully" + proceed         

        if target == "update prop":
            propname = request.form.get("name")
            colltype = request.form.get("colltype")
            commtype = request.form.get("commtype")
            commission = request.form.get("commission")
            proptype = request.form.get("proptype")

            valid_commission = validate_commission_input(commission)

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
            if proptype:
                ApartmentOp.update_proptype(prop,proptype)

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

        if target == "update prop landlord info":
            landlord = request.form.get("landlord")
            region = request.form.get("region")

            bank = request.form.get("landlordbank")
            accname = request.form.get("landlordaccname")
            accno = request.form.get("landlordaccno")

            print(">>>>",bank,accname,accno)

            location = LocationOp.fetch_location(region.title())
            if region:
                if not location:
                    location = LocationOp(region.title(),None)
                    location.save()
                    location_id = location.id
                else:
                    location_id = location.id
            else:
                location_id = None

            ApartmentOp.update_landlord_and_estate(prop,landlord,location_id)
            ApartmentOp.update_landlord_bank_details(prop,bank,accname,accno)

            return "Updated successfully" + proceed




class AllOwners(Resource):
    def get(self):
        # propa = ApartmentOp.fetch_apartment_by_id(3)
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

                        ApartmentOp.update_company(apartment_obj,current_user.company.id)
                        company_users = current_user.company.users
                        for i in company_users:
                            ApartmentOp.relate(apartment_obj,i)
                            print(i,"user added to ",str(apartment_obj))


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

        region = request.form.get("region")
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
            return f'<span class="text-danger">Property name missing</span>'
    
        
        apartment_obj = ApartmentOp(prop.title(),None,location.id,landlord.id,bool_value,current_user.id)
        apartment_obj.save()

        company = current_user.company
        ApartmentOp.update_company(apartment_obj,company.id)
        company_users = company.users
        for i in company_users:
            ApartmentOp.relate(apartment_obj,i)
            print(i,"user added to ",str(apartment_obj))

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
            if current_user.id == 1 or current_user.username.startswith("qc"):
                companies = CompanyOp.fetch_all_companies()
                data = []
                for company in companies:
                    if company.name and company:
                        data.append(company.name)
                    # if not company.name or not company:
                    #     print(company.users)
                    #     companies.remove(company)
                        # return None
                        # CompanyOp.delete(company)
                return render_template('ajax_multivariable.html',items=data,placeholder="select company")

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
            ApartmentOp.update_company(prop,company.id)
            company_users = company.users
            for i in company_users:
                ApartmentOp.relate(prop,i)
                print(i,"user added to ",str(prop))


        else:
            access = True
            # if current_user.id == 1:
            if access:
                prop_co = CompanyOp.fetch_company_by_id(prop.company_id)
                ApartmentOp.update_company(prop,None)
                company_users = prop_co.users
                for i in company_users:
                    print("These are users",company_users)
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

        if current_user.username.startswith("qc") or current_user.name == "Test Agent" or current_user.username.startswith("quality") or localenv or permission_alt(current_user,""):
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            # if prop.company_id:
            #     return "You are not allowed to perform this operation"
            # else:
            if True:
                try:
                    prp = prop.name
                    ApartmentOp.delete(prop)
                    response = sms.send(f"{current_user.name} has deleted {prp}", ["+254716674695"],"KIOTAPAY")
                except Exception as e:
                    response = sms.send(f"{current_user.name} failed to delete {prp} due to {e}", ["+254716674695"],"KIOTAPAY")

                return "Property removed successfully"
        else:
            return "You are not allowed to perform this operation"

class FetchClients(Resource):
    def get(self):
        target = request.args.get("target")

        clients = CompanyOp.fetch_all_companies()

        if target == "clients":
            actual_clients = []

            items = os.getenv('VAR_ITEMS') or VAR_ITEMS

            lst_items = items.split(",")

            print("heeeeeeeeeeeeeeee",lst_items)

            for client in clients:
                if client.name:
                    if client.name.lower() in lst_items:
                        clients.remove(client)
                    else:
                        clr = CompanyOp.view(client)
                        actual_clients.append(clr)
                else:
                    # CompanyOp.delete(client)
                    clr = CompanyOp.view(client)
                    actual_clients.append(clr)

            return render_template("ajax_clients.html",items=actual_clients,clrs=len(actual_clients))

        return Response(render_template(
            'clientlist.html',
            clrs = len(clients)
        ))






class Properties(Resource):
    def get(self):

        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:
                pps = []

                try:
                    curr_user = UserOp.fetch_user_by_usercode("6753")
                    props = fetch_all_apartments_by_user(curr_user)
                    for prop in props:
                        vacs = filter_out_occupied_houses(prop.name)

                        pdict = {
                            "property_code":prop.id,
                            "name": prop.name,
                            "units_num":len(prop.houses),
                            "vacants_num":len(vacs),
                            "location":prop.location.name
                        }
                        pps.append(pdict)

                except Exception as e:
                    print("Error processing",e)

                res = paginator(request,pps)
                num_returned_items = len(res[1])
                page_range = f"page {res[2]} of {len(res[0])}"
                paged_items = res[1]

                fdict = {
                    "total_items":len(pps),
                    "page_size":num_returned_items,
                    "page":page_range,
                    "properties":paged_items
                }

                response = {
                    "resultCode":0,
                    "resultDesc":"Success",
                    "data":fdict
                }
            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)


class PropertiesByLocation(Resource):
    def get(self,location_name):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:
                pps = []
                curr_user = UserOp.fetch_user_by_usercode("6753")
                if location_name:
                    loca = location_name.title()
                else:
                    loca = ""
                loc = LocationOp.fetch_location(loca)
                if not loc:
                    response = {
                        "resultCode":0,
                        "resultDesc":"location not found on the server"
                    }
                else:
                    props = fetch_all_apartments_by_user(curr_user)
                    for prop in props:
                        if prop.location.name == loc.name:
                            vacs = filter_out_occupied_houses(prop.name)

                            pdict = {
                                "property_code":prop.id,
                                "name": prop.name,
                                "units_num":len(prop.houses),
                                "vacants_num":len(vacs),
                                "location":prop.location.name
                            }
                            pps.append(pdict)

                    res = paginator(request,pps)
                    num_returned_items = len(res[1])
                    page_range = f"page {res[2]} of {len(res[0])}"
                    paged_items = res[1]

                    fdict = {
                        "total_items":len(pps),
                        "page_size":num_returned_items,
                        "page":page_range,
                        "properties":paged_items
                    }

                    response = {
                        "resultCode":0,
                        "resultDesc":"Success",
                        "data":fdict
                    }

            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)

class Property(Resource):
    def get(self,property_code):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:
                curr_user = UserOp.fetch_user_by_usercode("6753")


                propid = get_identifier(property_code)
                prop = ApartmentOp.fetch_apartment_by_id(propid)
                if not prop:
                    response = {
                        "resultCode":1,
                        "resultDesc":"Failed to fetch property",
                        "error":"property does not exist"
                    }

                else:

                    if not prop in curr_user.company.props:

                        response = {
                            "resultCode":1,
                            "resultDesc":"Failed to fetch property",
                            "error":"property does not exist"
                        }

                    else:
                        try:
                            vacs = filter_out_occupied_houses(prop.name)

                            pdict = {
                                "property_code":prop.id,
                                "name": prop.name,
                                "units_num":len(prop.houses),
                                "vacants_num":len(vacs),
                                "location":prop.location.name
                            }
                                
                        except Exception as e:
                            print("Error processing",e)
                            pdict = {}

                        response = {
                            "resultCode":0,
                            "resultDesc":"Success",
                            "data":pdict
                        }

            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)
    

class Units(Resource):
    def get(self,property_code):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:

                propid = get_identifier(property_code)
                
                prop = ApartmentOp.fetch_apartment_by_id(propid)
                if not prop:
                    response = {
                        "resultCode":1,
                        "resultDesc":"Failed to fetch property",
                        "error":"property does not exist"
                    }

                else:
                    houses = []

                    curr_user = UserOp.fetch_user_by_usercode("6753")


                    if not prop in curr_user.company.props:

                        response = {
                            "resultCode":1,
                            "resultDesc":"Failed to fetch property",
                            "error":"property does not exist"
                        }

                    else:

                        try:
                            for unit in prop.houses:
                                tenant = check_occupancy(unit)[1]
                                if tenant == "vacant":
                                    tt = {}
                                else:
                                    tt = {
                                        "name": tenant.name,
                                        "phone": tenant.phone,
                                        "email": tenant.email,
                                        "lease_date": "-",
                                        "balance": tenant.balance
                                    }

                                    tenant = tenant.name

                                udict = {
                                    "unit_code": unit.id,
                                    "unit":unit.name,
                                    "rent":unit.housecode.rentrate,
                                    "tenant":tenant,
                                    "tenant_info":tt
                                }
                                houses.append(udict)


                            res = paginator(request,houses)
                            num_returned_items = len(res[1])
                            page_range = f"page {res[2]} of {len(res[0])}"
                            paged_items = res[1]

                            pdict = {
                                "total_items":len(houses),
                                "page_size":num_returned_items,
                                "page":page_range,
                                "units":paged_items
                            }
                                
                        except Exception as e:
                            print("Error processing all units",e)
                            pdict = {}

                        response = {
                            "resultCode":0,
                            "resultDesc":"Success",
                            "data":pdict
                        }
            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)

class Unit(Resource):
    def get(self,unit_code):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:

                unitid = get_identifier(unit_code)
                
                unit = HouseOp.fetch_house_by_id(unitid)
                if not unit:
                    response = {
                        "resultCode":1,
                        "resultDesc":"Failed to fetch unit",
                        "error":"unit does not exist"
                    }

                else:
                    curr_user = UserOp.fetch_user_by_usercode("6753")

                    props = fetch_all_apartments_by_user(curr_user)

                    ca = [uu.houses for uu in props]

                    caa = flatten(ca)

                    if not unit in caa:

                        response = {
                            "resultCode":1,
                            "resultDesc":"Failed to fetch unit",
                            "error":"unit does not exist"
                        }

                    else:

                        try:

                            tenant = check_occupancy(unit)[1]
                            if tenant == "vacant":
                                tt = {}
                            else:
                                tt = {
                                    "name": tenant.name,
                                    "phone": tenant.phone,
                                    "email": tenant.email,
                                    "lease_date": "-",
                                    "balance": tenant.balance
                                }
                                tenant = tenant.name

                            udict = {
                                "unit_code":unit.id,
                                "unit":unit.name,
                                "rent":unit.housecode.rentrate,
                                "tenant":tenant,
                                "tenant_info":tt
                            }

                            pdict = {
                                "property_code":unit.apartment_id,
                                "name": unit.apartment.name,
                                "units":udict,
                            }
                                
                        except Exception as e:
                            print("Error processing",e)
                            pdict = {}

                        response = {
                            "resultCode":0,
                            "resultDesc":"Success",
                            "data":pdict
                        }
            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)
    
class VacantUnits(Resource):
    def get(self):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:

                curr_user = UserOp.fetch_user_by_usercode("6753")

                props = fetch_all_apartments_by_user(curr_user)

                vacs = flatten([filter_out_occupied_houses(prop.name) for prop in props])
                try:
                    houses = []
                    for unit in vacs:
                        udict = {
                            "property_code":unit.apartment_id,
                            "property_name": unit.apartment.name,
                            "unit_code": unit.id,
                            "unit_name":unit.name,
                            "rent":unit.housecode.rentrate,
                            "status":"vacant",
                            "location":unit.apartment.location.name
                        }
                        houses.append(udict)

                    res = paginator(request,houses)
                    num_returned_items = len(res[1])
                    page_range = f"page {res[2]} of {len(res[0])}"
                    paged_items = res[1]

                    pdict = {
                        "total_items":len(vacs),
                        "page_size":num_returned_items,
                        "page":page_range,
                        "vacant_units":paged_items
                    }
                        
                except Exception as e:
                    print("Error processing all units",e)
                    pdict = {}

                response = {
                    "resultCode":0,
                    "resultDesc":"Success",
                    "data":pdict
                }
            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)
    
class VacantUnitsByProperty(Resource):
    def get(self,property_code):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:

                houses = []

                curr_user = UserOp.fetch_user_by_usercode("6753")

                propid = get_identifier(property_code)
                
                prop = ApartmentOp.fetch_apartment_by_id(propid)
                if not prop:
                    response = {
                        "resultCode":1,
                        "resultDesc":"Failed to fetch property",
                        "error":"property does not exist"
                    }
                else:
                    if not prop in curr_user.company.props:

                        response = {
                            "resultCode":1,
                            "resultDesc":"Failed to fetch property",
                            "error":"property does not exist"
                        }
                    
                    else:

                        vacs = filter_out_occupied_houses(prop.name)

                        try:
                            for unit in vacs:

                                udict = {
                                    "property_code":unit.apartment_id,
                                    "property_name": unit.apartment.name,
                                    "unit_code": unit.id,
                                    "unit_name":unit.name,
                                    "rent":unit.housecode.rentrate,
                                    "status":"vacant",
                                    "location":unit.apartment.location.name
                                }
                                houses.append(udict)

                            res = paginator(request,houses)
                            num_returned_items = len(res[1])
                            page_range = f"page {res[2]} of {len(res[0])}"
                            paged_items = res[1]

                            pdict = {
                                "total_items":len(vacs),
                                "page_size":num_returned_items,
                                "page":page_range,
                                "vacant_units":paged_items
                            }

                                
                        except Exception as e:
                            print("Error processing all units",e)
                            pdict = {}

                        response = {
                            "resultCode":0,
                            "resultDesc":"Success",
                            "data":pdict
                        }

            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)

class FetchInvoicesPerProperty(Resource):
    def get(self,property_code):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:
                houses = []

                curr_user = UserOp.fetch_user_by_usercode("6753")

                propid = get_identifier(property_code)
                
                prop = ApartmentOp.fetch_apartment_by_id(propid)
                if not prop:
                    response = {
                        "resultCode":1,
                        "resultDesc":"Failed to fetch property",
                        "error":"property does not exist"
                    }
                else:
                    if not prop in curr_user.company.props:

                        response = {
                            "resultCode":1,
                            "resultDesc":"Failed to fetch property",
                            "error":"property does not exist"
                        }
                    
                    else:

                        tenants = tenantauto(prop.id)

                        try:
                            for unit in tenants:

                                curr_inv = max(unit.monthly_charges, key=lambda x: x.id) if unit.monthly_charges else None
                                if curr_inv:
                                    idd = curr_inv.house.name + ""
                                    date = generate_exact_date(curr_inv.date.day, curr_inv.date.month, curr_inv.year)
                                    udict = {
                                        "property_code":unit.apartment_id,
                                        "property_name": unit.apartment.name,
                                        "unit_name": curr_inv.house.name,
                                        "tenant_name": unit.name,
                                        "tenant_phone": unit.phone,
                                        "invoice_code": curr_inv.id,
                                        "invoice_period": date,
                                        "amount_due":curr_inv.total_bill,
                                        "paid_amount":curr_inv.paid_amount,
                                        "balance":curr_inv.balance,
                                        "identifier":idd
                                    }
                                    houses.append(udict)

                            res = paginator(request,houses)
                            num_returned_items = len(res[1])
                            page_range = f"page {res[2]} of {len(res[0])}"
                            paged_items = res[1]

                            pdict = {
                                "total_items":len(houses),
                                "page_size":num_returned_items,
                                "page":page_range,
                                "invoices":paged_items
                            }
                                
                        except Exception as e:
                            print("Error processing all units",e)
                            pdict = {}

                        response = {
                            "resultCode":0,
                            "resultDesc":"Success",
                            "data":pdict
                        }
            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)


class FetchInvoicePerUnit(Resource):
    def get(self,unit_code):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:

                unitid = get_identifier(unit_code)
                
                unit = HouseOp.fetch_house_by_id(unitid)
                if not unit:
                    response = {
                        "resultCode":1,
                        "resultDesc":"Failed to fetch unit",
                        "error":"unit does not exist"
                    }

                else:
                    curr_user = UserOp.fetch_user_by_usercode("6753")

                    props = fetch_all_apartments_by_user(curr_user)

                    ca = [uu.houses for uu in props]

                    caa = flatten(ca)

                    if not unit in caa:

                        response = {
                            "resultCode":1,
                            "resultDesc":"Failed to fetch unit",
                            "error":"unit does not exist"
                        }

                    else:

                        try:

                            tenant = check_occupancy(unit)[1]
                            if tenant == "vacant":
                                tt = {
                                    "invoice_code":"N/A",
                                    "description":"invoice not available"
                                }
                            else:
                                curr_inv = max(tenant.monthly_charges, key=lambda x: x.id) if tenant.monthly_charges else None
                                if curr_inv:
                                    idd = curr_inv.house.name + ""
                                    date = generate_exact_date(curr_inv.date.day, curr_inv.date.month, curr_inv.year)

                                    tt = {
                                        "tenant_name":tenant.name,
                                        "tenant_phone":tenant.phone,
                                        "invoice_code": curr_inv.id,
                                        "invoice_period": date,
                                        "amount_due":curr_inv.total_bill,
                                        "paid_amount":curr_inv.paid_amount,
                                        "balance":curr_inv.balance,
                                        "identifier":idd
                                    }
                                    tenant = tenant.name

                                else:
                                    tt = {
                                        "invoice_code":"N/A",
                                        "description":"invoice not available"
                                    }

                            pdict = {
                                "property_code":unit.apartment_id,
                                "property_name": unit.apartment.name,
                                "unit_code":unit.id,
                                "unit_name":unit.name,
                                "tenant_name":tenant,
                                "tenant_invoice":tt
                            }
                                
                        except Exception as e:
                            print("Error processing",e)
                            pdict = {}

                        response = {
                            "resultCode":0,
                            "resultDesc":"Success",
                            "data":pdict
                        }
            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)
    
    

# class FetchLocations(Resource):
#     def get(self):
#         auth = request.headers.get("Authorization")

#         ckey="elloelesama"
#         skey="q150c2bf1c4ee7da42yt"

#         hash = generate_hash(ckey,skey)

#         if auth:
#             bearer = auth.split(" ")[1]
#             if bearer == hash:


#                 curr_user = UserOp.fetch_user_by_usercode("6753")
#                 locs = LocationOp.fetch_all_locations()

#                 props = fetch_all_apartments_by_user(curr_user)
#                 loca = []
#                 for loc in locs:
#                     houses = []
#                     pps_num = 0

#                     for prop in loc.apartments:
#                         if prop in props:
#                             pps_num += 1
#                             tenants = tenantauto(prop.id)
#                             vacs = filter_out_occupied_houses(prop.name)
#                             vacant_units = [str(u) for u in vacs]
#                             units = [str(u) for u in prop.houses]

#                             udict = {
#                                 "property_code":prop.id,
#                                 "name": prop.name,
#                                 "units_num":len(prop.houses),
#                                 "units":units,
#                                 "tenants":len(tenants),
#                                 "vacant_units":vacant_units,
#                                 "location":prop.location.name
#                             }

#                             houses.append(udict)

#                     # res = paginator(request,houses)
#                     # num_returned_items = len(res[1])
#                     # page_range = f"page {res[2]} of {len(res[0])}"
#                     # paged_items = res[1]

#                     # pdict = {
#                     #     "location":loc.name,
#                     #     "total_properties":len(houses),
#                     #     "num_items":num_returned_items,
#                     #     "pages_data":page_range,
#                     #     "properties":paged_items
#                     # }

#                     pdict = {
#                         "location":loc.name,
#                         "num_properties":pps_num,
#                         "properties":houses
#                     }

#                     loca.append(pdict)

#                 response = {
#                     "resultCode":0,
#                     "resultDesc":"Success",
#                     "data":loca
#                 }

#             else:

#                 response = {
#                     "resultCode":1,
#                     "resultDesc":"Failed Authorization"
#                 }
#         else:
#             response = {
#                 "resultCode":1,
#                 "resultDesc":"Invalid request"
#             }

#         resp = jsonify(response)
#         return make_response(resp)


class FetchLocations(Resource):
    def get(self):
        auth = request.headers.get("Authorization")

        ckey="elloelesama"
        skey="q150c2bf1c4ee7da42yt"

        hash = generate_hash(ckey,skey)

        if auth:
            bearer = auth.split(" ")[1]
            if bearer == hash:


                curr_user = UserOp.fetch_user_by_usercode("6753")
                locs = LocationOp.fetch_all_locations()

                props = fetch_all_apartments_by_user(curr_user)
                loca = []
                for loc in locs:
                    houses = []
                    pps_num = 0
                    
                    for prop in loc.apartments:
                        if prop in props:
                            pps_num += 1
                            vacs = filter_out_occupied_houses(prop.name)
                            udict = {
                                "property_code":prop.id,
                                "name": prop.name,
                                "units_num":len(prop.houses),
                                "vacants_num":len(vacs),
                            }

                            houses.append(udict)

                    if houses:

                        pdict = {
                            "location":loc.name,
                            "num_properties":pps_num,
                            "properties":houses
                        }

                        loca.append(pdict)

                res = paginator(request,loca)
                num_returned_items = len(res[1])
                page_range = f"page {res[2]} of {len(res[0])}"
                paged_items = res[1]

                fdict = {
                    "total_items":len(loca),
                    "page_size":num_returned_items,
                    "page":page_range,
                    "locations":paged_items
                }

                response = {
                    "resultCode":0,
                    "resultDesc":"Success",
                    "data":fdict
                }

            else:

                response = {
                    "resultCode":1,
                    "resultDesc":"Failed Authorization"
                }
        else:
            response = {
                "resultCode":1,
                "resultDesc":"Invalid request"
            }

        resp = jsonify(response)
        return make_response(resp)
    

