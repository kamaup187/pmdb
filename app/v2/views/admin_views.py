# from app.v1.models import datamodel
# import time
# from curses import raw
import os
from time import strptime

import cloudinary as Cloud
# from sqlalchemy import inspect
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from flask_mail import Message
from flask_login import login_required, current_user, login_user
from flask_restful import Resource, abort
from flask import render_template, Response, request, flash, redirect, url_for, send_file, after_this_request
from dateutil.relativedelta import relativedelta
from sqlalchemy import exc

from app.v1.models.operations import *
from app.v2.utils.user_validator import UserValidator
from app.v2.utils.property_validator import PropertyValidator
from app.v2.utils import validate
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
    'cloud_name': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
})


class Robots(Resource):
    def get(self):
        path = "robots.txt"
        print(send_file(path, as_attachment=True))
        return send_file(path, as_attachment=True)


class DownloadTemplate(Resource):
    def get(self, file):
        path = f"files/{file}.xls"
        return send_file(path, as_attachment=True)


class ViewReceipt(Resource):
    def get(self, ri):
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

        server = fname_extracter(
            UserOp.fetch_user_by_id(payment_obj.user_id).name)

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
                    "address": "Ongata Rongai",
                    "tel": "0735267087",
                    "email": "bizlineinvestment@gmail.com"
                }
            elif prop.id == 421:
                address = {
                    "address": "Mwiki, Kasarani",
                    "tel": "0735267087",
                    "email": "bizlineinvestment@gmail.com"
                }
            elif prop.name == "Baraka House":
                address = {
                    "address": "Mwiki, Kasarani",
                    "tel": "0735267087",
                    "email": "bizlineinvestment@gmail.com"
                }

            else:
                address = {
                    "address": "Mwiki, Kasarani",
                    "tel": "0735267087",
                    "email": "bizlineinvestment@gmail.com"
                }

        return Response(render_template(
            'user_receipt.html',
            voided="dispnone",
            tenant=tenant.name,
            house=payment_obj.house,
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

        # return Response(jsonify({
        # voided = "dispnone",
        # tenant = tenant.name,
        # house= payment_obj.house,
        # amount=paid,
        # str_amount=stramount,
        # str_month=get_str_month(payperiod.month),
        # paydate=paydate.strftime("%d/%b/%y"),
        # paytime=paydate.strftime("%X"),
        # bill=bill,
        # baltitle=baltitle,
        # outline=outline,
        # balance=bal,
        # chargetype=payment_obj.payment_name,
        # receiptno=receiptno,
        # refnum=payment_obj.ref_number,
        # paymode=payment_obj.paymode,
        # logopath=logo(co)[0],
        # company=co,
        # address=address,
        # user=server,
        # prop=prop,
        # randid=ri
        # }))


class UserActivation(Resource):
    def get(self, ri):

        user = UserOp.fetch_user_by_link(ri)
        if not user:
            print("chekererere")
        else:
            UserOp.update_status(user, True)
            login_user(user, remember=False)
            return redirect(url_for("api.index"))


class DemoAccess(Resource):
    def get(self, ri):

        user = UserOp.fetch_user_by_link(ri)
        if ri != "zjdqjpvnkgblhfweikkiloukrqcwijaofdf":
            print("zhekererere")
        else:
            return redirect(url_for("api.demo"))


class DownloadReceipt(Resource):
    """class"""

    def get(self, ri):

        rand_id = request.args.get('randid')

        print("AWESOME HERE", rand_id)

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

            server = fname_extracter(
                UserOp.fetch_user_by_id(payment_obj.user_id).name)

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
                        "address": "Ongata Rongai",
                        "tel": "0735267087",
                        "email": "bizlineinvestment@gmail.com"
                    }
                elif prop.id == 421:
                    address = {
                        "address": "Mwiki, Kasarani",
                        "tel": "0735267087",
                        "email": "bizlineinvestment@gmail.com"
                    }
                elif prop.name == "Baraka House":
                    address = {
                        "address": "Mwiki, Kasarani",
                        "tel": "0735267087",
                        "email": "bizlineinvestment@gmail.com"
                    }

                else:
                    address = {
                        "address": "Mwiki, Kasarani",
                        "tel": "0735267087",
                        "email": "bizlineinvestment@gmail.com"
                    }

            else:
                address = None

            template_vars = {
                "tenant": tenant.name,
                "voided": disp,
                "house": payment_obj.house.name,
                "amount": f'Kes: {payment_obj.amount:,.0f}',
                "str_amount": stramount,
                "str_month": get_str_month(payperiod.month),
                "paydate": paydate.strftime("%d/%b/%y"),
                "paytime": paydate.strftime("%X"),
                "bill": bill,
                "baltitle": baltitle,
                "outline": outline,
                "balance": bal,
                "chargetype": payment_obj.payment_name,
                "receiptno": receiptno,
                "refnum": payment_obj.ref_number,
                "paymode": payment_obj.paymode,
                "logopath": mail_logo,
                "address": address,
                "company": co,
                "user": server,
                "prop": prop
            }

            html_out = template.render(template_vars)
            filename = f"app/temp/receipt_{rand_id}.pdf"
            HTML(string=html_out, base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename, stylesheets=[
                "app/static/myfonts.css", "app/static/eapartment-min.css", "app/static/kiotapay.css", "app/static/receipt.css"])

            path = f"temp/receipt_{rand_id}.pdf"

            @after_this_request
            def remove_file(response):
                try:
                    filename = f"app/{path}"
                    os.remove(filename)
                except Exception as error:
                    print("Error removing or closing downloaded file handle", error)
                return response

            try:
                return send_file(path, as_attachment=True)
            except Exception as e:
                return "This receipt is longer available on our server " + str(e)


class DownloadInvoice(Resource):
    """class"""

    def get(self, ri):

        rand_id = request.args.get('randid')

        print("INVOICE IS BEING ACCESSSSSSSSSSSSSSSSEEEEEEEEEDDDDD", rand_id)

        if not rand_id:
            rand_id = ri

        bill = MonthlyChargeOp.fetch_specific_bill(rand_id)

        if bill:

            co = bill.apartment.company

            invnum = bill.id + 13285

            house = bill.house

            tenant = bill.tenant

            sibling_water_bill = fetch_current_billing_period_readings(
                bill.apartment.billing_period, bill.house.meter_readings)

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
            smstotal = (f"{bill.total_bill:,.1f}") if not calculated_total else (
                f"{calculated_total:,.1f}")

            timenow = datetime.datetime.now()
            # diff = timenow.day - 2
            diff = 0
            invdate = bill.date - relativedelta(days=diff)

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

            print(mail_logo, "<<<<<<<<<<<<<<<<<<<<<<<<<<<", mail_logo)

            template_vars = {
                "bill": bill,
                "readings": wbill,
                "waterbill": smsbill,
                "house": house,
                "total": f"{bill.total_bill:,.2f}",
                "invdate": inv_date,
                "invdue": inv_due,
                "client": tenant,
                "company": co,
                "invnum": invnum,
                "logo": mail_logo,
                "slogo": mail_slogo
            }

            html_out = template.render(template_vars)
            filename = f"app/temp/inv_{rand_id}.pdf"
            HTML(string=html_out, base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(
                filename, stylesheets=["app/static/myfonts.css", "app/static/eapartment-min.css", "app/static/kiotapay.css"])

            path = f"temp/inv_{rand_id}.pdf"

            @after_this_request
            def remove_file(response):
                try:
                    filename = f"app/{path}"
                    os.remove(filename)
                except Exception as error:
                    print("Error removing or closing downloaded file handle", error)
                return response

            try:
                return send_file(path, as_attachment=True)
            except Exception as e:
                return "This receipt is longer available on our server " + str(e)


class DeleteReceipt(Resource):
    def get(self, propid):
        deleted = False
        try:
            property_id = int(propid)
        except:
            return "Wrong prop id"

        prop = ApartmentOp.fetch_apartment_by_id(property_id)
        payments = prop.payment_data
        for i in payments:
            if i.rand_id:
                filename = f"app/temp/receipt_{i.rand_id}.pdf"
                try:
                    # os.remove(filename)
                    # deleted = True
                    pass
                except:
                    print("File does not exist for payment no.", i.id)

        if deleted:
            return "Deleted some"
        else:
            return "Non deleted"


class Properties(Resource):
    @login_required
    def get(self):
        target = request.args.get("target", default=None)

        if target == "prop update":
            propertyId = request.args.get("propid")
            property_id = get_identifier(propertyId)
            property = ApartmentOp.fetch_apartment_by_id(property_id)

            if property.commission:
                commission = property.commission
                commission_type = "percent"
            else:
                commission = property.int_commission
                commission_type = "static"

            if property.commission_type:
                if property.commission_type == "collected":
                    colltype = "collected"
                else:
                    colltype = "projected"
            else:
                colltype = "not set"

            try:
                if property.paymentdetails.nartype == 'hsenum':
                    nartype = "#HX"
                elif property.paymentdetails.nartype == "tntnum":
                    nartype = "#TNTXXX"
                else:
                    nartype = ""
            except:
                nartype = ""

            return {
                'property': property,
                'commission': commission,
                'commission_type': commission_type,
                'colltype': colltype,
                'nartype': nartype
            }, 200

        if current_user.username.startswith("qc") or localenv:
            raw_properties = ApartmentOp.fetch_all_unlinked_apartments()
        else:
            raw_properties = ApartmentOp.fetch_all_apartments_createdby_user_id(
                current_user.id)

        raw_properties2 = current_user.company.props

        if localenv:
            raw_properties3 = ApartmentOp.fetch_all_apartments()
            raw_properties4 = raw_properties + raw_properties2 + raw_properties3
        else:
            raw_properties4 = raw_properties + raw_properties2

        properties = remove_dups(raw_properties4)

        items = []
        property_ids = []

        for property in properties:
            tenants = len(tenantauto(property.id))
            ptnts = len(property.ptenants)

            if tenants:
                tnt_disp = ""
            houses = len(property.houses)
            try:
                occupancy = tenants/houses * 100
            except:
                occupancy = 0

            occ = f"{occupancy:,.0f}"

            if target == "tenants":
                template = "ajax_prop_tenants.html"
                dict_obj = {
                    'id': property.id,
                    'identity': "prp"+str(property.id),
                    'editid': "edit"+str(property.id),
                    'delid': "del"+str(property.id),
                    'name': property.name,
                    'houses': houses,
                    'tenants': tenants,
                    'ptenants': ptnts,
                    'vacant': houses - tenants,
                    'reminders': f'<span class="text-success font-weight-bold">{property.reminder_status}</span>' if property.reminder_status == "sent" else f'<span class="text-danger font-weight-bold">{property.reminder_status}</span>',
                    'occupancy': occ,
                    'createdby': property.user_id,
                }
            elif target == "tenant list":
                template = "ajax_prop_tenant_list.html"
                dict_obj = {
                    'id': property.id,
                    'identity': "prp"+str(property.id),
                    'editid': "edit"+str(property.id),
                    'delid': "del"+str(property.id),
                    'name': property.name,
                    'houses': houses,
                    'tenants': tenants,
                    'ptenants': ptnts,
                    'vacant': houses - tenants,
                    'reminders': f'<span class="text-success font-weight-bold">Sent</span>' if property.reminder_status else '<span class="text-danger font-weight-bold">Not yet</span>',
                    'occupancy': occ,
                    'createdby': property.user_id,
                }
            else:
                template = "ajax_allprops_detail.html"
                dict_obj = {
                    'id': property.id,
                    'identity': "prp"+str(property.id),
                    'editid': "edit"+str(property.id),
                    'delid': "del"+str(property.id),
                    'name': property.name,
                    'owner': property.owner.name,
                    'company': property.company.name if property.company else "N/A",
                    'houses': houses,
                    'tenants': tenants,
                    'ptenants': ptnts,
                    'reminders': f'<span class="text-success font-weight-bold">{property.reminder_status}</span>' if property.reminder_status else '<span class="text-danger font-weight-bold">not yet</span>',
                    'occupancy': occ,
                    'status': "active",
                    'link': '<i class="fas fa-share-alt mr-1 text-success"></i><span class="text-gray-900">link</span>' if not property.company_id else '<i class="fas fa-sign-out-alt mr-1 text-danger"></i><span class="text-gray-900">unlink</span>',
                    'link-target': "btn-outline-success" if not property.company_id else "btn-outline-danger",
                    'createdby': property.user_id,
                }

            items.append(dict_obj)
            property_ids.append(property.id)
            property_ids.append("prp"+str(property.id))
            property_ids.append("edit"+str(property.id))
            property_ids.append("del"+str(property.id))

        return {'properties': items}, 200

    @login_required
    def post(self):
        incoming_data = request.get_json()

        # Validate data
        invalid_data = validate(incoming_data, PropertyValidator)
        if invalid_data:
            return invalid_data

        property_name = incoming_data.get("property_name")
        agency = incoming_data.get("agency")
        telephone = incoming_data.get("telephone")
        owner = incoming_data.get("landlord")
        region = incoming_data.get("region")
        present = ApartmentOp.fetch_apartment_by_name(property_name.title())

        if present:
            return {
                "msg": "Property name already exists"
            }, 422

        if not owner:
            owner = current_user.company.name.title()

        # TO DO, UPDATE APARTMENT OWNER IN THE APARTMENT TABLE
        if not telephone:
            telephone = "N/A"
            landlord = OwnerOp(owner, telephone, None, "N/A", current_user.id)
            landlord.save()

        else:
            landlord = OwnerOp.fetch_owner_by_phone(telephone)
            if not landlord:
                landlord = OwnerOp(owner, telephone, None, "N/A", current_user.id)
                landlord.save()

        if not region:
            region = "Nairobi"

        location = LocationOp.fetch_location(region.title())
        if not location:
            location = LocationOp(region.title(), None)
            location.save()

        if not agency:
            agency = "False"

        bool_value = return_bool(agency)
        apartment_obj = ApartmentOp(
            property_name.title(), None, location.id, landlord.id, bool_value, current_user.id)
        apartment_obj.save()

        return {
            "msg": "Property added successfully"
        }, 200

class Property(Resource):
    @login_required
    def get(self, propertyId):
        apartment = ApartmentOp.fetch_apartment_by_id(propertyId)

        if not apartment:
            return {
                "msg": "Property was not found!"
            }, 404

        data = vars(apartment)
        
        property = {
            "name": data.get('name'),
            'company_id': data.get('company_id'), 
            'commission': data.get('commission'), 
            'image_url': data.get('image_url'),
            'agency_managed': data.get('agency_managed'),
            'billing_period': str(data.get('billing_period')),
            'consumer_key': data.get('consumer_key'),
            'payment_bankaccname': data.get('payment_bankaccname'),
            'billprogress': data.get('billprogress'),
            'payment_bank': data.get('payment_bank'),
            'shortcode': data.get('shortcode'),
            'landlord_bankacc_two': data.get('landlord_bankacc_two'),
            'garbage_collector_bankacc': data.get('garbage_collector_bankacc'),
            'landlord_bankaccname_two': data.get('landlord_bankaccname_two'),
            'int_commission': data.get('int_commission'),
            'garbage_collector_bank': data.get('garbage_collector_bank'),
            'owner_id': data.get('owner_id'),
            'garbage_collector_tel': data.get('garbage_collector_tel'),
            'commission_type': data.get('commission_type'),
            'landlord_bankacc': data.get('landlord_bankacc'),
            'garbage_collector': data.get('garbage_collector'),
            'agreement_fee': data.get('agreement_fee'),
            'landlord_bankaccname': data.get('landlord_bankaccname'),
            'reminder_status': data.get('reminder_status'),
            'landlord_bank': data.get('landlord_bank'),
            'consumer_secret': data.get('consumer_secret'),
            'agent_id': data.get('agent_id'),
            'uniqueid': data.get('uniqueid'),
            'payment_bankacc': data.get('payment_bankacc'),
            'user_id': data.get('user_id'),
            'caretaker_id': data.get('caretaker_id'),
            'id': data.get('id'),
        }
        
        return property, 200
        
    @login_required
    def put(self, propertyId):
        incoming_data = request.get_json()
        
        # Validate data
        validate(incoming_data, PropertyValidator)

        target = incoming_data.get("target")
        property = ApartmentOp.fetch_apartment_by_id(propertyId)
        
        if target == "update property":
            property_name = incoming_data.get("property_name")
            colltype = incoming_data.get("colltype")
            commission_type = incoming_data.get("commission_type")
            commission = incoming_data.get("commission")
            valid_commission = validate_input(commission)
            
            if property_name:
                property_name = property_name.title()
                existing_property = ApartmentOp.fetch_apartment_by_name(property_name)
                
                if existing_property and property.name != property_name:
                    return {
                        "msg": "name already taken"
                    }, 422

            if commission_type == "percent":
                ApartmentOp.update_commission(property,valid_commission)
            else:
                ApartmentOp.update_int_commission(property,valid_commission)

            ApartmentOp.update_details(property,property_name,colltype)

            return {
                "msg": "Property updated successfully"
            }, 200
        elif target == "update property billing info":
            properties = []
            if property == "Latitude Properties":
                properties = property.company.props

            if not properties:
                properties.append(property)

            for p in properties:
                bankbranch = incoming_data.get("bankbranch")
                bankname = incoming_data.get("bankname")
                bankaccountname = incoming_data.get("bankaccountname")
                bankaccountnumber = incoming_data.get("bankaccountnumber")
                bankpaybill = incoming_data.get("bankpaybill")
                mpesapaybill = incoming_data.get("mpesapaybill")
                nartype = incoming_data.get("nartype")
                paytype = incoming_data.get("paytype")
                payment_details_obj = p.paymentdetails

                if not payment_details_obj:
                    p = PaymentDetailOp(paytype, nartype, mpesapaybill, bankname,
                                        bankbranch, bankaccountname, bankaccountnumber, bankpaybill, p.id)
                    p.save()
                else:
                    PaymentDetailOp.update_details(
                        payment_details_obj, paytype, nartype, mpesapaybill, bankname, bankbranch, bankaccountname, bankaccountnumber, bankpaybill)
            return {
                "msg": "Biling info updated successfully"
            }, 200

    @login_required
    def delete(self, propertyId):
        apartment = ApartmentOp.fetch_apartment_by_id(propertyId)

        if not apartment:
            return {
                "msg": "Property was not found!"
            }, 404
        
        qc_user = current_user.username.startswith("qc")
        test_agent = current_user.name == "Test Agent"
        quality_user = current_user.username.startswith("quality")

        if qc_user or test_agent or quality_user or localenv:
            apartment_dict = vars(apartment)

            if apartment_dict.get('company_id'):
                return {
                    "msg": "You are not allowed to perform this operation"
                }, 403
            else:
                ApartmentOp.delete(apartment)
                
                return {
                    "msg": "Property was deleted successfully"
                }, 200
        else:
            return {
                "msg": "You are not allowed to perform this operation"
            }, 403


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

        # TODO URGENT > USE proper naming of owners not props
        props = OwnerOp.fetch_all_owners()

        items = []
        properties = []
        property_ids = []

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
                'id': prop.id,
                'editid': "edit"+str(prop.id),
                'delid': "del"+str(prop.id),
                'name': prop.name,
                'natid': prop.national_id,
                'phone': prop.phone,
                'properties': prop_number,
                'acc': "Yes" if user_obj else "No",
                'createdby': prop.user_id,
            }

            items.append(dict_obj)
            property_ids.append(prop.id)
            property_ids.append("prp"+str(prop.id))
            property_ids.append("edit"+str(prop.id))
            property_ids.append("del"+str(prop.id))

        propids = ','.join(map(str, property_ids))

        return render_template("ajax_owners.html", propids=propids, items=items, company=current_user.company)


class AddProp(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")

        if target == "regions":
            regions = LocationOp.fetch_all_locations()
            return render_template('ajax_datalist.html', items=regions, placeholder="select region")

    @login_required
    def post(self):
        incoming_data = request.get_json()

        target = request.form.get('target')

        if target == "excelupload":
            file = request.files.get('file')

            if file:
                processed_data = upload_handler(file, current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows, sheet = processed_data[0], processed_data[1]

            data_format_error = False

            if sheet:
                if len(sheet.row_values(1)) != 4:
                    data_format_error = True

            try:
                if data_format_error:

                    nonexistent_item = sheet.row_values(1)[1000000]

                for row in rows:
                    property = sheet.row_values(row)[0]
                    region = sheet.row_values(row)[1]
                    owner = sheet.row_values(
                        row)[2] if sheet.row_values(row)[2] else ""
                    if sheet.row_values(row)[3]:
                        tel = "0" + str(int(sheet.row_values(row)[3])) if not str(int(sheet.row_values(
                            row)[3])).startswith("0") else str(int(sheet.row_values(row)[3]))
                    else:
                        tel = "N/A"

                    agency = "True"

                    print("VALUES", property, region, owner, tel, agency)

                    housecode = property.title()
                    code_obj = ApartmentOp.fetch_apartment_by_name(housecode)

                    if code_obj:
                        print("Skipping ", housecode)
                        continue

                    else:
                        if not owner:
                            owner = current_user.company.name.title()

                        # tel = request.form.get("tel")
                        if not tel or tel == "N/A":
                            tel = "N/A"
                            landlord = OwnerOp(
                                owner.title(), tel, None, "N/A", current_user.id)
                            landlord.save()

                        else:
                            landlord = OwnerOp.fetch_owner_by_phone(tel)
                            if not landlord:
                                landlord = OwnerOp(
                                    owner.title(), tel, None, "N/A", current_user.id)
                                landlord.save()

                        if not region:
                            region = "Nairobi"

                        location = LocationOp.fetch_location(region.title())
                        if not location:
                            location = LocationOp(region.title(), None)
                            location.save()

                        if not agency:
                            agency = "False"

                        bool_value = return_bool(agency)

                        if not property:
                            print("Property name blank")
                            continue

                        apartment_obj = ApartmentOp(
                            property.title(), None, location.id, landlord.id, bool_value, current_user.id)
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
                    print("RARE FATAL CASE: Error occured while saving item: ", e)
                    abort(403)


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

        uniquename = uniquename_generator(name, phone)
        is_present = OwnerOp.fetch_owner_by_uniquename(uniquename)
        is_present2 = OwnerOp.fetch_owner_by_phone(phone)

        if is_present:
            return f'<span class="text-danger">Record exists in the database already</span>'

        if is_present2:
            return f'<span class="text-danger">Record exists in the database already</span>'

        owner = OwnerOp(name, phone, None, uniquename, created_by)
        owner.save()

        owner_user = UserOp.fetch_user_by_phone(phone)

        if owner_user:
            natid = owner_user.national_id
            OwnerOp.update_natid(owner, natid)
            UserOp.update_status(owner_user, True)

        return f'<span class="text-success">Success</span>'


class AddRegion(Resource):
    @login_required
    def get(self):
        pass

    def post(self):
        name = request.form.get("name")
        loc_obj = LocationOp.fetch_location(name)
        if not loc_obj:
            region_obj = LocationOp(name, None)
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
                for company in companies:
                    if not company.name:
                        CompanyOp.delete(company)
            else:
                companies = [current_user.company]
            return render_template('ajax_multivariable.html', items=companies, placeholder="select company")
        else:
            companies = []
            return render_template('ajax_multivariable.html', items=companies, placeholder="ready to unlink")

    def post(self):
        propid = request.form.get("propid")
        co = request.form.get("company")
        target = request.form.get("target")

        prop = ApartmentOp.fetch_apartment_by_id(propid)

        if target == "link":
            company = CompanyOp.fetch_company_by_name(co)
            ApartmentOp.update_company(prop, company.id)
            company_users = company.users
            for i in company_users:
                ApartmentOp.relate(prop, i)
                print(i, "user added to ", str(prop))

        else:
            access = True
            # if current_user.id == 1:
            if access:
                prop_co = CompanyOp.fetch_company_by_id(prop.company_id)
                ApartmentOp.update_company(prop, None)
                company_users = prop_co.users
                for i in company_users:
                    print("These are users", company_users)
                    current_user_apartments = fetch_all_apartments_by_user(i)
                    if prop in current_user_apartments:
                        ApartmentOp.terminate(prop, i)
                        print("user removed from ", prop)
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
