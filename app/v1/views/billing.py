
import os
from dateutil.parser import parse

import requests
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

# from rq import Queue
# from rq.job import Job
# from worker import conn
# q = Queue(connection=conn,default_timeout=10800)

# from datetime import timedelta
# import time

# from rq.registry import ScheduledJobRegistry

# # job = q.enqueue_at( datetime.datetime(2021, 1, 26, 22, 57), mbogi)
# job = q.enqueue_in(timedelta(seconds=30), mbogi)

# registry = ScheduledJobRegistry(queue=q)
# time.sleep(0.1)
# print('Number of jobs in registry %s' % registry.count)

# # for job_id in registry.get_job_ids():
# #     print('Number of jobs in registry %s' % registry.count)
# #     # if registry.count > 1:
# #     registry.remove(job_id, delete_job=True)


class SwitchPeriod(Resource):
    def get(self):
        pass
    def post(self):

        month = request.form.get('month')
        co = current_user.company

        switchmonth = date_formatter_alt(month)
        switchperiod = parse(switchmonth)

        # intnextmonth = co.billing_period.month + 1 if co.billing_period.month != 12 else 1
        # intyear = co.billing_period.year + 1 if co.billing_period.month == 12 else co.billing_period.year
        # billing_period = generate_date(intnextmonth,intyear)

        if current_user.username.startswith('qc') or current_user.usercode == "3551" or current_user.usercode == "9672" or current_user.username.startswith('quality'):
            CompanyOp.update_billing_period(co,switchperiod)
        else:
            CompanyOp.update_billing_period(co,switchperiod)
            print("DANGEROUS MOVE TO ADVANCE TO NEXT PERIOD")

        txt = f'{co.name} has switched to {get_str_month(switchperiod.month)}'
        send_internal_email_notifications(co.name,txt)

        # try:
        #     txt = f'{co.name} wants to advance to {get_str_month(switchperiod.month)}'
        #     response = sms.send(txt, ["+254716674695"],"KIOTAPAY")
        # except Exception as e:
        #     print("billing notification failed >>>>>>>>>>>>>>>>>>>>>>>> ",e)
        # timenow = datetime.datetime.now()
        # if timenow.day < 20:
        #     CompanyOp.set_rem_quota(company,200)
        # else:
        #     pass

class Replenish(Resource):
    def post(self):
        if current_user.username.startswith("qc") or current_user.national_id == "12345678" or current_user.username.startswith("quality"):
            co = current_user.company
            CompanyOp.set_rem_quota(co,500)
            CompanyOp.set_smsquota(co,500)

class ReplenishAll(Resource):
    def get(self):
        cos = CompanyOp.fetch_all_companies()
        for co in cos:
            CompanyOp.set_rem_quota(co,500)
            CompanyOp.set_smsquota(co,500)
        return "ok"

class Billing(Resource):
    """class"""
    @login_required
    def post(self):
        msg = None
        user_id = current_user.id


        apartment_name = request.form.get("apartment")
        houses = request.form.get("houses")
        tenantid = request.form.get("tenantid")
        date = request.form.get("date")

        target = request.form.get("target")

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
            propid = request.form.get("propid")
            print("APARTMENT ID TO BILL IS>>>>",propid)
            # apartment_id = propid[4:]
            apartment_id = get_identifier(propid)
            prop = ApartmentOp.fetch_apartment_by_id(get_identifier(propid))
            apartment_name = prop.name
        else:
            apartment_id = get_apartment_id(apartment_name)
            prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

        ApartmentOp.update_billing_progress(prop,"billing")
            
        chargetype = request.form.get("chargetype")

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
                return Response(render_template('noaccess.html',name=current_user.name))

        apartment_list = fetch_all_apartments_by_user(current_user)
        # charge_type_list = ChargeType.query.all()
        
        return Response(render_template(
            'bills.html',
            apartment_list=apartment_list,
            year_list = [2021,2022,2022,2024],
            month_list = generate_month_list(),
            chargetypelist=["All"],
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

class BillProgress(Resource):
    def get(self):
        propid = request.args.get("propid")
        apartment_id = propid[4:]
        prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
        return prop.billprogress


class ClientBilling(Resource):
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

        return render_template(
            "ajax_client_bills.html",
            bills=items,
            billids=billids
            )
            
class ClientInvoice(Resource):
    """class"""
    def get(self):
        # return render_template(
        #     "ajax_client_invoice.html"
        #     )
        clientbill_id = request.args.get("clientbillid")
        clientbillid = get_identifier(clientbill_id)
        bill = ClientBillOp.fetch_specific_bill(clientbillid)
        client = bill.company
        invnum = bill.id + 13285
        # invnum = 

        timenow = datetime.datetime.now()
        
        # diff = timenow.day - 2
        # invdate = bill.date - relativedelta(days = diff)
        invdate = generate_start_date(timenow.month,timenow.year)
        inv_date = invdate.strftime("%d/%b/%y")

        invdue = invdate + relativedelta(days=4)
        inv_due = invdue.strftime("%d/%b/%y")

        return render_template(
            "ajax_client_invoice.html",
            bill=bill,
            sub = f"{bill.subscription:,}",
            total=f"{bill.total:,}",
            invdate=inv_date,
            invdue=inv_due,
            client=client,
            kiotapay=current_user.company,
            invnum=invnum,
            logo=logo(current_user.company)[2]
            )
class CreateWaterCharge(Resource):
    """class"""
    def post(self):

        apartment_id = request.form.get('propid')
        file = request.files.get('file')

        billing_period = get_billing_period(ApartmentOp.fetch_apartment_by_id(apartment_id))

        month = billing_period.month
        year = billing_period.year

        if month != 12:
            month += 1
        else:
            month = 1
            year += 1

        if file:
            processed_data = upload_handler(file,current_user)
        else:
            return '<span class=text-danger>Select file first</span>'

        rows,sheet = processed_data[0],processed_data[1]

        data_format_error = False

        if sheet:
            if len(sheet.row_values(1)) != 2:
                data_format_error = True

        try:
            if data_format_error:
                
                nonexistent_item = sheet.row_values(1)[1000000] # INTRODUCE AN ERROR TO BE CAUGHT

            for row in rows:

                try:
                    billhouse = str(int(sheet.row_values(row)[0]) if sheet.row_values(row)[0] else "" )
                except:
                    billhouse = sheet.row_values(row)[0] if sheet.row_values(row)[0] else ""

                waterbill = sheet.row_values(row)[1]
                    


                try:
                    float_bill=float(waterbill)
                except:
                    float_bill=0.0
                    
                user_id = current_user.id

                bill_house = billhouse.upper()
                house_obj = get_specific_house_obj(apartment_id,bill_house)
                if not house_obj:
                    print("Specified house doesnt exist: ",bill_house)
                    continue
                else:
                    house_id = house_obj.id

                occupancy = check_occupancy(house_obj)
                if occupancy[0] != "occupied":
                    print("Specified house not occupied: ",bill_house)
                    continue

                else:
                    charge_type_id = get_charge_type_id("Water")

                    checker = None

                    result = check_occupancy(house_obj)
                    if result[0] == "occupied":
                        if not house_obj.billable:
                            float_bill = 0.0

                        all_charges = ChargeOp.fetch_charges_by_house_id(house_id)

                        for charge in all_charges:
                            if str(charge) == "Water" and charge.date.month == month and charge.date.year == year and not charge.reading_id:
                                checker = "exists"
                                break

                        if checker:
                            print("Skipping",house_obj,"fixed_water charging",float_bill,"exists")
                            continue
                        else:
                            print(">>>>>>>>> Charging",house_obj,"float_bill")
                            date = generate_date(month,year)
                            water_charge_obj = ChargeOp(charge_type_id,float_bill,apartment_id,house_id,user_id,date)
                            water_charge_obj.save()
                            
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

class BillInvoice(Resource):
    """class"""
    @login_required
    def get(self):
        billid = request.args.get('billid')

        target = request.args.get('target')

        if not billid:
            abort(403)

        for i in billid:
            if i.isdigit():
                target_index = billid.index(i)
                break

        identifier = billid[target_index:]

        bill = MonthlyChargeOp.fetch_specific_bill(identifier)

        second_bill = False

        house = bill.house


        if bill.ptenant:
            tenant=bill.ptenant
            current_target = "owner"
            print("OWNER INVOICE IS BEING ACCESSED FOR" ,bill.ptenant.name)
        else:
            current_target = "tenant"
            tenant=bill.tenant
            print("TENANT INVOICE IS BEING ACCESSED FOR" ,bill.tenant.name)


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

            if not bill.house.watertarget:
                watertarget = True
        except:
            watertarget = True


        sibling_water_bill = fetch_current_billing_period_readings(bill.apartment.billing_period,bill.house.meter_readings)
        print("WATER BILLS ARE HERE",sibling_water_bill)
        try:
            print(sibling_water_bill[0].reading_period)
        except:
            pass
        sibling_electricity_bill = fetch_current_billing_period_readings_alt(bill.apartment.billing_period,bill.house.meter_readings)
        print("ELECTRICITY BILLS ARE HERE",sibling_electricity_bill)
        try:
            print(sibling_electricity_bill[0].reading_period)
        except:
            pass


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

        invnum = bill.id + 13285

        timenow = datetime.datetime.now()
        # diff = timenow.day - 2
        diff = 0
        invdate = bill.date - relativedelta(days = diff)

        inv_date = invdate.strftime("%d/%b/%y")
        invdue = invdate + relativedelta(days=5)
        inv_due = invdue.strftime("%d/%b/%y")

        kiotapay = CompanyOp.fetch_company_by_name("KiotaPay")

        
        if target == "double email":

            identifier2 = bill.id + 1

            bill2 = MonthlyChargeOp.fetch_specific_bill(identifier2)

            if bill2 and bill2.apartment_id == bill.apartment_id:
                second_bill = True

                invnum2 = bill2.id + 13285

                house2 = bill2.house

                tenant2 = bill2.tenant

                sibling_water_bill2 = fetch_current_billing_period_readings(bill2.apartment.billing_period,bill2.house.meter_readings)
                sibling_electricity_bill2 = fetch_current_billing_period_readings_alt(bill2.apartment.billing_period,bill2.house.meter_readings)


                try:
                    wbill2 = sibling_water_bill2[0]
                    w_edited2 = "dispnone" if wbill2.units == float(wbill2.reading) - float(wbill2.last_reading) else ""
                except:
                    wbill2 = None
                    w_edited2 = "dispnone"

                try:
                    ebill2 = sibling_electricity_bill2[0]
                    e_edited2 = "dispnone" if ebill2.units == float(ebill2.reading) - float(ebill2.last_reading) else ""
                except:
                    ebill2 = None
                    e_edited2 = "dispnone"



                if wbill2 or ebill2:
                    visibility2 = ""
                else:
                    visibility2 = "hide"

                

                arrears2 = bill2.arrears
                
                if bill2.paid_amount:
                    billpaid2 = f"{bill2.paid_amount:,.2f}"
                    billbal2 = f"{bill2.balance:,.2f}"

                else:
                    billpaid2 = 0.0
                    billbal2 = 0.0

                if arrears2 < 0.0:
                    arrtitle2 = "Advance"
                    bbfhighlight2 = "text-success"

                    arrears2 = f"{arrears*-1}"
                elif arrears2 > 0.0:
                    arrtitle2 = "Arrears"
                    bbfhighlight2 = "text-danger"
                else:
                    arrtitle2 = ""
                    bbfhighlight2 = ""

            if second_bill:

                return render_template(
                    "ajax_tenant_invoice.html",
                    bill=bill,
                    readings = wbill,
                    w_edited = w_edited,
                    ereadings = ebill,
                    e_edited = e_edited,
                    visibility=visibility,
                    arrears=arrears,
                    bbfhighlight = bbfhighlight,
                    arrtitle=arrtitle,
                    billpaid=billpaid,
                    billbal=billbal,
                    house=house,
                    total=f"{bill.total_bill:,.2f}",
    
                    client=tenant,
                    invnum=invnum,
                    randid=bill.id,

                    bill2=bill2,
                    readings2 = wbill2,
                    w_edited2 = w_edited2,
                    ereadings2 = ebill2,
                    e_edited2 = e_edited2,
                    visibility2=visibility2,
                    arrears2=arrears2,
                    bbfhighlight2 = bbfhighlight2,
                    arrtitle2=arrtitle2,
                    billpaid2=billpaid2,
                    billbal2=billbal2,
                    house2=house2,
                    total2=f"{bill2.total_bill:,.2f}",
                    client2=tenant2,
                    invnum2=invnum2,
                    randid2=bill2.id,

                    invdate=inv_date,
                    invdue=inv_due,
                    company=current_user.company,
                    logo=logo(current_user.company)[2],
                    slogo=logo(kiotapay)[1],
                    sign=logo(kiotapay)[4]
                    )

            else:
                return render_template(
                    "ajax_tenant_invoice.html",
                    bill=bill,
                    readings = wbill,
                    w_edited = w_edited,
                    ereadings = ebill,
                    e_edited = e_edited,
                    visibility=visibility,
                    arrears=arrears,
                    bbfhighlight = bbfhighlight,
                    arrtitle=arrtitle,
                    billpaid=billpaid,
                    billbal=billbal,
                    house=house,
                    total=f"{bill.total_bill:,.2f}",
                    invdate=inv_date,
                    invdue=inv_due,
                    client=tenant,
                    company=current_user.company,
                    invnum=invnum,
                    randid=bill.id,
                    logo=logo(current_user.company)[2],
                    slogo=logo(kiotapay)[1],
                    sign=logo(kiotapay)[4]
                    )

        elif target == 'email':


            try:
                if bill.apartment.paymentdetails.nartype == 'hsenum':
                    narration = bill.house.name
                elif bill.apartment.paymentdetails.nartype == 'tntnum':
                    if bill.ptenant:
                        narration = "WN"+str(tenant.id)
                    else:
                        narration = "TNT"+str(tenant.id)
                else:
                    narration = ""
            except:
                narration = ""

            template = "ajax_tenant_invoice_mail2.html" if aviv(current_user) else "ajax_tenant_invoice_mail.html"

            if bill.house.housecode.billfrequency == 3:
                str_month = f"July, August, September"
            else:
                str_month = get_str_month(bill.month)

            return render_template(
                "ajax_tenant_invoice_mail.html",
                bill=bill,
                month = str_month,
                p = bill.apartment.paymentdetails,
                narration=narration,
                readings = wbill,
                watertarget = watertarget,
                w_edited = w_edited,
                ereadings = ebill,
                e_edited = e_edited,
                visibility=visibility,
                arrears=arrears,
                bbfhighlight = bbfhighlight,
                arrtitle=arrtitle,
                billpaid=billpaid,
                billbal=billbal,
                house=house,
                total=f"{bill.total_bill:,.2f}",
                invdate=inv_date,
                invdue=inv_due,
                client=tenant,
                company=current_user.company,
                invnum=invnum,
                randid=bill.id,
                logo=logo(current_user.company)[0],
                slogo=logo(kiotapay)[1],
                sign=logo(kiotapay)[4]
                )

        else:

            smsstatus = bill.sms_invoice

            action = "Resend"

            if smsstatus == "sent":
                delivery = "pending delivery"
    
            elif smsstatus == "success-alt":
                delivery = "Manually forwarded"
                
            elif smsstatus == "Success":
                delivery = "Delivered successfully"
            else:
                action = "Send"
                delivery = "Not yet sent"

            sms_highlight = "text-success" if smsstatus == "sent" or  smsstatus == "Success" or  smsstatus == "success-alt" else "text-danger"

            tenant = bill.tenant if bill.tenant else bill.ptenant
            prop_obj= bill.apartment

            if bill.house.housecode.billfrequency == 3:
                str_month = f"July, August, September"
            else:
                str_month = get_str_month(prop_obj.billing_period.month)

            salutation = f'Dear <span class="text-primary">{fname_extracter(tenant.name)}</span>,'
            intro = f'your {str_month} <span class="text-info">invoice </span>is as follows;'

            if bill.house.payment_bankacc:
                bankdetails = f'Bank: <span class="text-info">{bill.house.payment_bank} Acc: {bill.house.payment_bankacc}</span>'
            elif prop_obj.payment_bank:
                bankdetails = f'Bank: <span class="text-info">{prop_obj.payment_bank} Acc: {prop_obj.payment_bankacc}</span>'
            else:
                bankdetails = ""

            try:
                if bill.apartment.paymentdetails.nartype == 'hsenum':
                    narration = bill.house.name
                elif bill.apartment.paymentdetails.nartype == 'tntnum':
                    if bill.ptenant:
                        narration = "WN"+str(tenant.id)
                    else:
                        narration = "TNT"+str(tenant.id)
                else:
                    narration = ""
            except:
                narration = ""

            p = bill.apartment.paymentdetails
            if p:
                if p.paytype == "mpesapay":
                    bankdetails = f'\n\nPaybill: {p.mpesapaybill} \nAcc: {narration}'
                elif p.bankpaybill:
                    bankdetails = f'\n\nPaybill: {p.bankpaybill} \nAcc: {p.bankaccountnumber}#{narration}'
                    if p.paytype != "bankpay":
                        bankdetails = ""
                else:
                    bankdetails = f'\n\nBank: {p.bankname}, \nName: {p.bankaccountname} \nAcc: {p.bankaccountnumber}'
                    if p.paytype != "bankpay":
                        bankdetails = ""
                        
            co = current_user.company

            if co.name == 'LaCasa':
                str_co = f'<span class="text-primary">Tel: 0735267087</span>'
            else:
                str_co = f'<span class="text-primary">{str(co)}</span>'

            print("HEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEY")
            print("OWNER:",bill.ptenant)
            print("TENANT",bill.tenant)
            print("delivery REPORT",bill.sms_invoice)
            print("HEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEY")
            print("READINGS: ",wbill)
            print("WATERTARGET: ",watertarget)

            template = "ajax_sms_invoice2.html" if aviv(current_user) else "ajax_sms_invoice.html"

            return render_template(
                template,
                smsstatus=delivery,
                narration=narration,
                sms_highlight=sms_highlight,
                action=action,
                salutation=salutation,
                intro=intro,
                arrears=arrears,
                bbfhighlight = bbfhighlight,
                arrtitle=arrtitle,
                billpaid=billpaid,
                billbal=billbal,
                house=house,
                bill = bill,
                readings = wbill,
                w_edited = w_edited,
                ereadings = ebill,
                e_edited = e_edited,
                watertarget=watertarget,
                total=f"{bill.total_bill:,.1f}",
                bank=bankdetails,
                co=str_co
                )

class EditBill(Resource):
    """class"""
    @login_required
    def get(self):
        billid = request.args.get('billid')
        target = request.args.get('target')

        if not billid:
            abort(403)

        for i in billid:
            if i.isdigit():
                target_index = billid.index(i)
                break

        identifier = billid[target_index:]

        bill = MonthlyChargeOp.fetch_specific_bill(identifier)

        if bill.apartment.billing_period.month == bill.month and bill.apartment.billing_period.year:
            warning = ""
        else:
            warning = "CAUTION! This is not the current invoice"

        if bill.house.housecode.waterrate or bill.house.housecode.watercharge:
            # update = ['disabled','<i class="fa fa-lock ml-3 text-danger"></i>'] #TODO URGENT
            update = ['','Kshs']
        else:
            update = ['','Kshs']

        if target == "editarrears":
            if warning:
                warning = 'CAUTION! This is not the current invoice arrears'
            return render_template("ajax_dynamic_billarrears.html",bill=bill,warning=warning)
        elif target == "editpayments":
            if warning:
                warning = "CAUTION! This is not the current invoice payments"
            if current_user.username.startswith('qc') or current_user.usercode =="3551":
                return render_template("ajax_dynamic_billpayments.html",bill=bill,warning=warning)
            else:
                return render_template("ajax_dynamic_billpayments.html",bill=bill,warning=warning)
        else:
            return render_template("ajax_dynamic_bill_form_alt.html",waterlock=update[0],waterlock_icon=update[1],bill=bill,warning=warning)

    @login_required
    def post(self):
        bills = []
        billid = request.form.get('billid')

        target = request.form.get('target')

        rent = request.form.get('rent')
        water = request.form.get('water')
        garbage = request.form.get('garbage')
        security = request.form.get('security')
        fine = request.form.get('fine')
        agreement = request.form.get('agreement')
        electricity = request.form.get('electricity')
        if not electricity:
            electricity = ""
        deposit = request.form.get('deposit')
        maintenance = request.form.get('maintenance')
        arrears = request.form.get('arrears')

        identifier = get_identifier(billid)

        bill = MonthlyChargeOp.fetch_specific_bill(identifier)

        if bill:

            bills.append(bill)
        
        else:
            if target == "excelarrearsupload":
                apartment_id = request.form.get('propid')
                option = request.form.get('option')
                file = request.files.get('file')

                if file:
                    processed_data = upload_handler(file,current_user)
                else:
                    return '<span class=text-danger>Select file first!</span>'

                rows,sheet = processed_data[0],processed_data[1]

                data_format_error = False

                if sheet:
                    if len(sheet.row_values(1)) != 2:
                        data_format_error = True

                try:
                    if data_format_error:
                        #Throw error
                        nonexistent_item = sheet.row_values(1)[1000000]

                    dict_array = []

                    for row in rows:
                        print("Starting.........................................")
                        try:
                            housename = str(int(sheet.row_values(row)[0]) if sheet.row_values(row)[0] else "" )
                            print("Working as expected")
                        except:
                            housename = sheet.row_values(row)[0] if sheet.row_values(row)[0] else ""
                            print("house exception handled")

                        print("Extracted.......",housename)

                        try:
                            arr = float(sheet.row_values(row)[1])
                            print("Working")
                        except:
                            print("Failing")
                            arr = 0.0
                                                
                        dict_obj = {
                        "housename":housename,
                        "arr":arr
                        }

                        dict_array.append(dict_obj)

                    uploadsjob2 = q.enqueue_call(
                        func=read_arrears_excel, args=(dict_array,option,apartment_id,current_user.id,), result_ttl=5000
                    )

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
            else:
                print("Unknown error in bill update>>>>>>>>>>>>>>>>>>>>>!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                abort(403)

            

        for bill in bills:


            original_amount = bill.total_bill

            if target == "bill discard":

                all_charges = bill.house.charges

                for charge in all_charges:
                    if charge.date.month == bill.apartment.billing_period.month and charge.date.year == bill.apartment.billing_period.year:
                        ChargeOp.delete(charge)

                if bill.apartment.billing_period.month == bill.month:
                    if bill.tenant_id:
                        tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                        running_bal = tenant_obj.balance
                        running_bal = running_bal - original_amount
                        TenantOp.update_balance(tenant_obj,running_bal)

                    MonthlyChargeOp.delete(bill)
                else:
                    MonthlyChargeOp.delete(bill)

            elif target == "editarrears":
                # if bill.apartment.billing_period.month == bill.month: #DISABLED THIS CHECK TO EDIT PREVIOUS BILL ARREARS


                values = validate_float_inputs(rent,water,garbage,security,fine,deposit,"",agreement,electricity,maintenance)


                if bill.house.housecode.waterrate or bill.house.housecode.watercharge:
                    # update_water = bill.water
                    update_water = values[1] if values[1] != "null" else bill.water_balance
                else:
                    update_water = values[1] if values[1] != "null" else bill.water_balance

                update_rent = values[0] if values[0] != "null" else bill.rent_balance
                update_garbage = values[2] if values[2] != "null" else bill.garbage_balance
                update_security = values[3] if values[3] != "null" else bill.security_balance
                update_fine = values[4] if values[4] != "null" else bill.penalty_balance
                update_agreement = values[7] if values[7] != "null" else bill.agreement_balance
                update_deposit = values[5] if values[5] != "null" else bill.deposit_balance
                update_electricity = values[8] if values[8] != "null" else bill.electricity_balance
                update_maintenance = values[9] if values[9] != "null" else bill.maintenance_balance
                
                update_arrears = update_water+update_rent+update_garbage+update_security+update_fine+update_deposit+update_agreement+update_electricity+update_maintenance

                total_amount = original_amount - bill.arrears + update_arrears

                MonthlyChargeOp.update_monthly_charge(bill,"null","null","null","null","null","null","null","null","null",update_arrears,total_amount,current_user.id)

                MonthlyChargeOp.update_balances(bill,0.0,0.0,update_rent,update_water,update_electricity,update_garbage,update_security,update_maintenance,update_fine,update_deposit,update_agreement)


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

                MonthlyChargeOp.update_dues(bill,0.0,0.0,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)




                diff = total_amount - original_amount
                
                if bill.apartment.billing_period.month == bill.month:
                    if bill.tenant_id:

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


            elif target == "editpayments":
                # if bill.apartment.billing_period.month == bill.month: #DISABLED THIS CHECK TO EDIT PREVIOUS BILL PAYMENTS


                values = validate_float_inputs(rent,water,garbage,security,fine,deposit,"",agreement,electricity,maintenance)


                if bill.house.housecode.waterrate or bill.house.housecode.watercharge:
                    # update_water = bill.water
                    update_water = values[1] if values[1] != "null" else bill.water_paid
                else:
                    update_water = values[1] if values[1] != "null" else bill.water_paid

                update_rent = values[0] if values[0] != "null" else bill.rent_paid
                update_garbage = values[2] if values[2] != "null" else bill.garbage_paid
                update_security = values[3] if values[3] != "null" else bill.security_paid
                update_fine = values[4] if values[4] != "null" else bill.penalty_paid
                update_agreement = values[7] if values[7] != "null" else bill.agreement_paid
                update_deposit = values[5] if values[5] != "null" else bill.deposit_paid
                update_electricity = values[8] if values[8] != "null" else bill.electricity_paid
                update_maintenance = values[9] if values[9] != "null" else bill.maintenance_paid
                
                update_payments = update_water+update_rent+update_garbage+update_security+update_fine+update_deposit+update_agreement+update_electricity+update_maintenance

                if bill.paid_amount < 0.0:
                    MonthlyChargeOp.update_payment(bill,update_payments)

                if bill.paid_amount != update_payments and bill.paid_amount != 0.0:
                    print("MASTER PAYMENT IS NOT TALLYING WITH NEW PAYMENT>>>>","MASTER:",bill.paid_amount,"CHILD:",update_payments)
                    return None
                if bill.paid_amount != update_payments:
                    pass
                else:
                    MonthlyChargeOp.update_payment(bill,update_payments)

                MonthlyChargeOp.update_payments(bill,0.0,0.0,update_rent,update_water,update_electricity,update_garbage,update_security,update_maintenance,update_fine,update_deposit,update_agreement)


                # if bill.rent_balance:
                if bill.rent_balance:
                    rentbal = bill.rent + bill.rent_balance - bill.rent_paid
                else:
                    rentbal = bill.rent - bill.rent_paid

                if bill.water_balance:
                    waterbal = bill.water + bill.water_balance - bill.water_paid 
                else:
                    waterbal = bill.water - bill.water_paid

                if bill.electricity_balance:
                    electricitybal = bill.electricity + bill.electricity_balance - bill.electricity_paid
                else:
                    electricitybal = bill.electricity - bill.electricity_paid

                if bill.maintenance_balance:
                    servicebal = bill.maintenance + bill.maintenance_balance - bill.maintenance_paid
                else:
                    servicebal = bill.maintenance - bill.maintenance_paid

                if bill.penalty_balance:
                    penaltybal = bill.penalty + bill.penalty_balance - bill.penalty_paid
                else:
                    penaltybal = bill.penalty - bill.penalty_paid

                if bill.security_balance:
                    securitybal = bill.security + bill.security_balance - bill.security_paid
                else:
                    securitybal = bill.security - bill.security_paid

                if bill.garbage_balance:
                    garbagebal = bill.garbage + bill.garbage_balance - bill.garbage_paid
                else:
                    garbagebal = bill.garbage - bill.garbage_paid


                if bill.deposit_balance:
                    depositbal = bill.deposit + bill.deposit_balance - bill.deposit_paid
                else:
                    depositbal = bill.deposit - bill.deposit_paid

                if bill.agreement_balance:
                    agreementbal = bill.agreement + bill.agreement_balance - bill.agreement_paid
                else:
                    agreementbal = bill.agreement - bill.agreement_paid

                MonthlyChargeOp.update_dues(bill,0.0,0.0,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)




                # diff = total_amount - original_amount

                # tenant_obj = TenantOp.fetch_tenant_by_id(bill.tenant_id)
                # running_bal = tenant_obj.balance
                # running_bal = running_bal + diff
                # TenantOp.update_balance(tenant_obj,running_bal)

                # # bal = bill.balance
                # # bal = bal + diff
                # if bill.paid_amount:
                #     bal = total_amount - bill.paid_amount
                # else:
                #     bal = total_amount

                # MonthlyChargeOp.update_balance(bill,bal)




            else:
                # if bill.apartment.billing_period.month == bill.month:
                values = validate_float_inputs(rent,water,garbage,security,fine,deposit,arrears,agreement,electricity,maintenance)

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
                MonthlyChargeOp.update_monthly_charge(bill,values[1],values[0],values[2],"null",values[3],values[5],values[7],values[9],values[4],values[6],total_amount,current_user.id)

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
                    waterbal = bill.water_balance + update_water

                if bill.electricity_paid:
                    electricitybal = bill.electricity_balance + bill.electricity - bill.electricity_paid
                else:
                    electricitybal = bill.electricity_balance + bill.electricity

                if bill.maintenance_paid:
                    servicebal = bill.maintenance_balance + update_maintenance - bill.maintenance_paid
                else:
                    servicebal = bill.maintenance_balance + update_maintenance

                if bill.penalty_paid:
                    penaltybal = bill.penalty_balance + update_fine - bill.penalty_paid
                else:
                    penaltybal = bill.penalty_balance + update_fine

                if bill.security_paid:
                    securitybal = bill.security_balance + update_security - bill.security_paid
                else:
                    securitybal = bill.security_balance + update_security

                if bill.garbage_paid:
                    garbagebal = bill.garbage_balance + update_garbage - bill.garbage_paid
                else:
                    garbagebal = bill.garbage_balance + update_garbage


                if bill.deposit_paid:
                    depositbal = bill.deposit_balance + update_deposit - bill.deposit_paid
                else:
                    depositbal = bill.deposit_balance + update_deposit

                if bill.agreement_paid:
                    agreementbal = bill.agreement_balance + update_agreement - bill.agreement_paid
                else:
                    agreementbal = bill.agreement_balance + update_agreement

                MonthlyChargeOp.update_dues(bill,0.0,0.0,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)
                # MonthlyChargeOp.update_rent_balance(bill,rentarr)


                diff = total_amount - original_amount

                if bill.apartment.billing_period.month == bill.month:

                    if bill.tenant_id:

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


class EditSummary(Resource):
    """class"""
    @login_required
    def get(self):
        billid = request.args.get('billid')

        if not billid:
            abort(403)

        for i in billid:
            if i.isdigit():
                target_index = billid.index(i)
                break

        identifier = billid[target_index:]

        bill = LandlordSummaryOp.fetch_specific_bill(identifier)

        return render_template("ajax_dynamic_summary_form.html",bill=bill)

    @login_required
    def post(self):
        billid = request.form.get('billid')

        rent = request.form.get('rent')
        water = request.form.get('water')
        deposit = request.form.get('deposit')
        arrears = request.form.get('arrears')
        paid = request.form.get('paid')
        delinv = request.form.get('delinv')

        for i in billid:
            if i.isdigit():
                target_index = billid.index(i)
                break

        identifier = billid[target_index:]

        bill = LandlordSummaryOp.fetch_specific_bill(identifier)

        delinv_bool = get_bool(delinv)

        if delinv_bool:
            LandlordSummaryOp.delete(bill)
            return None

        # original_amount = bill.total_bill

        values = validate_float_inputs(rent,water,deposit,arrears,paid)

        #TODO -remove this block
        deposit = bill.deposit if bill.deposit else 0.0


        update_rent = values[0] if values[0] != "null" else bill.rent
        update_water = values[1] if values[1] != "null" else bill.water
        update_deposit = values[2] if values[2] != "null" else deposit
        update_arrears = values[3] if values[3] != "null" else bill.arrears
        update_paid = values[4] if values[4] != "null" else bill.paid_amount

        total_amount = update_water+update_rent+update_arrears+update_deposit + bill.garbage + bill.security

        bal = total_amount - update_paid

        # diff = total_amount - original_amount
        # bal = bill.balance
        # bal = bal + diff

        LandlordSummaryOp.update_summary(bill,values[0],values[1],values[2],values[3],total_amount,values[4],bal,current_user.id)

class SendInvoices(Resource):
    def get(self):
        prop = request.args.get('prop')
        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
        bills = prop_obj.monthlybills
        billing_period = get_billing_period(prop_obj)
        target_bills = []
        for i in bills:
            if i.month == billing_period.month and i.year == billing_period.year and i.sms_invoice != "sent":
                target_bills.append(i)

        if not target_bills:
            return f'<span class="text-danger">All invoices have already been sent !</span>'
        else:
            return f'<span class="text-success">Proceed to bill</span>'



    @login_required
    def post(self):

        prop = request.form.get('prop')
        propid = request.form.get('propid')
        # charge = request.form.get('charge')
        charge = "all"
        houses = request.form.get('houses')
        bill_id = request.form.get('billid')
        target = request.form.get('target')
        ctype = request.form.get('ctype')

        if not prop and propid:
            apartment_id = propid[3:]
            prop = str(ApartmentOp.fetch_apartment_by_id(apartment_id))

        print("Sending out invoices",prop,target)

        user_id = current_user.id

        message_invoice_type = houses if houses else "normal"

        override = True


        if target == "isolated mail":
            billid = get_identifier(bill_id)

            bill = MonthlyChargeOp.fetch_specific_bill(billid)

            if bill.tenant:
                print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC   sending tenant invoice of ",bill.tenant.name)
            else:
                print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB   sending owner invoice of ",bill.ptenant.name)

            job563 = q.enqueue_call(
                func=send_out_single_email_invoice, args=(billid,), result_ttl=5000
            )

            return None


        if target == "isolated":

            if ctype == "water":
                charge = "water"
                
                prop = str(ApartmentOp.fetch_apartment_by_id(prop))

                billid = request.form.get('billid')

                if not billid:
                    abort(403)

                for i in billid:
                    if i.isdigit():
                        target_index = billid.index(i)
                        break

                identifier = billid[target_index:]

                bill = MeterReadingOp.fetch_specific_reading(identifier)

                houses = str(bill.house)

            else:
                charge = "all"
                
                prop = str(ApartmentOp.fetch_apartment_by_id(prop))

                billid = request.form.get('billid')

                if not billid:
                    abort(403)

                for i in billid:
                    if i.isdigit():
                        target_index = billid.index(i)
                        break

                identifier = billid[target_index:]

                bill = MonthlyChargeOp.fetch_specific_bill(identifier)

                houses = str(bill.house)

        elif target == "mail":

            prop = str(ApartmentOp.fetch_apartment_by_id(prop))

            billid = request.form.get('billid')

            identifier = get_identifier(billid)

            bill = MonthlyChargeOp.fetch_specific_bill(identifier)

            houses = str(bill.house)
            
            override = False
            # txt = f'Email Invoicing of type: {charge} and target: {message_invoice_type} requested by {current_user.company} for {prop}'
            # send_internal_email_notifications(current_user.company.name,txt)

            job563 = q.enqueue_call(
                func=send_out_email_invoices, args=(prop,houses,override,charge,user_id,), result_ttl=5000
            )
            return None

        else:
            billid = ""
            txt = f'SMS Invoicing of type: {charge} and target: {message_invoice_type} requested by {current_user.company} for {prop}'
            send_internal_email_notifications(current_user.company.name,txt)

            # try:
            #     advanta_send_sms(txt,kiotanum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
            # except:
            #     pass

        # THIS IS INTENTIONAL, JOB IS NOT WITHIN THE IF BLOCK

        job982 = q.enqueue_call(
            func=send_out_sms_invoices, args=(prop,houses,billid,charge,user_id,), result_ttl=5000
        )
        return None

class SendMail(Resource):
    
    @login_required
    def get(self):
        if current_user.company_user_group.name == "User":
            return None
        target = request.args.get("target")
        if target:
            return None
        created_by = current_user.id
        payment_id = request.args.get("payid")

        txt = f'Receipting requested by {current_user.company} for {payment_id}'
        send_internal_email_notifications(current_user.company.name,txt)

        # response = sms.send(txt, ["+254716674695"],"KIOTAPAY")

        job99 = q.enqueue_call(
            func=auto_send_mail_receipt, args=(payment_id,created_by,), result_ttl=5000
        )


class DiscardBills(Resource):
    
    @login_required
    def post(self):

        propid = request.form.get("propid")

        propids = []
        propids.append(propid)

        prop_obj = ApartmentOp.fetch_apartment_by_id(propid)

        txt = f'All bills discard requested by {current_user.company} for {prop_obj.name}'

        send_internal_email_notifications(current_user.company.name,txt)


        # try:
        #     response = sms.send(txt, ["+254716674695"],"KIOTAPAY")
        # except:
        #     pass

        if current_user.username.startswith('qc') or current_user.username.startswith('quality') or current_user.usercode == "3551" or current_user.usercode == "9672":
            job34 = q.enqueue_call(
                func=discard_bills, args=(propids,), result_ttl=5000
            )
        else:
            pass

class SendSms(Resource):
    
    @login_required
    def get(self):

        if current_user.company_user_group.name == "User":
            return f'<span class="text-danger smallify ln-10">Not allowed</span>'

        payment_id = request.args.get("payid")
        
        if payment_id:

            payment_obj = PaymentOp.fetch_payment_by_id(payment_id)
            if payment_obj.voided:
                return f'<span class="text-danger smallify ln-10 small">Failed Payment voided!</span>'
            
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

            if os.getenv("TARGET") == "lasshouse":
                receipt = f"Receipt: https://kodimannapp.com/r/{payment_obj.rand_id}"
            else:
                receipt = f"Receipt: https://kiotapay.com/r/{payment_obj.rand_id}"


            tele = tenant_obj.phone

            phonenum = sms_phone_number_formatter(tele)


            co = payment_obj.apartment.company
            str_co = co.name
            raw_rem_sms =co.remainingsms
            message = f"Rental payment Ref {reference}, sum of {amount} confirmed. \n{running_bal} \n\n{receipt} \n\n~{str_co}."

            char_count = len(message)

            cost = 1 if char_count <= 160 else 2
            
            sms_obj = SentMessagesOp(message,char_count,cost,tenant_obj.id,payment_obj.apartment.id,co.id)
            sms_obj.save()

            if tenant_obj.sms:
                # if payment_obj.apartment.company.name == "Lesama Ltd":
                #     advanta_send_sms(message,phonenum,lesama_api_key,lesama_partner_id,"LESAMA")
                #     return f'<span class="text-success smallify ln-10">Sent successfully</span>'

                # elif payment_obj.apartment.company.name == "KEVMA REAL ESTATE":
                #     advanta_send_sms(message,phonenum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")
                #     return f'<span class="text-success smallify ln-10">Sent successfully</span>'

                if co.sms_provider == "Advanta":
                    sms_sender(co.name,message,phonenum)
                    return f'<span class="text-success smallify ln-10">Sent successfully</span>'

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
                                return f'<span class="text-success smallify ln-10">Sent successfully</span>'

                            elif code == 403:
                                print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                PaymentOp.update_sms_status(payment_obj,"fail")
                                return f'<span class="text-danger x-smallify ln-10">Failed! Check number</span>'
                            elif code == 405:
                                print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                txt = f"{co} has depleted sms"
                                response = sms.send(txt, ["+254716674695"],"KIOTAPAY")
                                return f'<span class="text-warning smallify ln-10">Try again later</span>'
                            elif code == 406:
                                PaymentOp.update_sms_status(payment_obj,"blocked")
                                print("SMS BLOCKED BY ",tenant_obj,payment_obj.house,payment_obj.apartment)
                                raw_cost = resp["cost"]
                                rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                                CompanyOp.set_rem_quota(co,rem_sms)
                                return f'<span class="text-danger smallify ln-10">Number error</span>'
                            
                        except Exception as e:
                            print(f"Houston, we have a problem {e}")
                            PaymentOp.update_sms_status(payment_obj,"fail")
                            return f'<span class="text-danger x-smallify ln-10">Incorrect number</span>'
                    else:
                        return f'<span class="text-danger x-smallify ln-10">Failed! Insufficient sms balance</span>'
            else:
                PaymentOp.update_sms_status(payment_obj,"off")
                return f'<span class="text-danger x-smallify ln-10">Failed! sms disabled for tenant</span>'

        if not payment_id:
            payids = []
            timenow = datetime.datetime.now()
            payments = PaymentOp.fetch_all_payments()
            for i in payments:
                if not i.voided and i.sms_status == "pending" and i.pay_period.month == timenow.month:
                    payids.append(i.id)

            job101 = q.enqueue_call(
                func=autosend_pending_smsreceipts, args=(payids,), result_ttl=5000
            )

            
class SetReminder(Resource):
    """class"""
    def post(self):

        return redirect(url_for('api.index'))
        

class AmendCharge(Resource):
    """class"""
    @login_required
    def get(self):
        pass

    @login_required
    def post(self):
        pass

class ReceivePayment(Resource):
    """class"""
    @login_required
    def get(self):


        # user_group = current_user.company_user_group
        # accessright = check_accessright(user_group,"receive_payment")
        # if accessright != True:
        #     return Response(render_template('noaccess.html',name=current_user.name))
        
        prop_id = request.args.get("propid")
        propname = request.args.get("propname")
        house_name = request.args.get("house")
        house_name2 = request.args.get("house2")
        cbid = request.args.get("cbid")
        payperiod = request.args.get("payperiod")
        target = request.args.get("target")


        propid = get_identifier(prop_id)

        if propname:
            prop = ApartmentOp.fetch_apartment_by_name(propname)
            propid = prop.id
        else:
            prop = ApartmentOp.fetch_apartment_by_id(propid)

        db.session.expire(prop)

        if payperiod:
            pay_period = date_formatter_alt(payperiod)
            pay_period_date = parse(pay_period)
        else:
            pay_period_date = get_billing_period(prop)

        print("PAYPERIOOOOOOOD",pay_period_date)

        if target == "proplist":
            props = fetch_all_apartments_by_user(current_user)
            return render_template('ajax_multivariable.html',items=sort_items(props),placeholder="select property",access="")

        if target == "houselist":
            if current_user.company.name == "Grashar Agencies" and current_user.username !="grasharp40":
                no_cash = "NOT ALLOWED"
            else:
                no_cash = ""

            if current_user.user_group_id == 2 and current_user.name != "WANGO SHEMA":
                return render_template('ajax_multivariable.html',items=[],placeholder="Not allowed",access=no_cash)
            else:
                tenant_list = tenantauto(propid)
                # house_tenant_list = generate_house_tenants(tenant_list)
                house_tenant_list = generate_house_ownertenants(tenant_list,propid)
                return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant/resident",access=no_cash)

        if target == "propname":
            return f'>> {prop.name}'

        if target == "fetch c2b item":
            cbid = request.args.get("cbid")
            cb = CtoBop.fetch_record_by_id(cbid)
            
            cb_obj = {
                "ref":cb.trans_id,
                "amount":cb.trans_amnt,
                "name":f"{cb.fname} {cb.lname}",
                "narration":cb.bill_ref_num
            }

            return render_template("c2bitem.html",c2bitem=cb_obj)

        if target == "fetch target tenant":
            cb = CtoBop.fetch_record_by_id(cbid)

            if cb.bill_ref_num:
                #######################################################################################
                if cb.bill_ref_num.startswith("TNT"):
                    tenant = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                    if not tenant:
                        tenant = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                elif cb.bill_ref_num.startswith("WN"):
                    tenant = PermanentTenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                    if not tenant:
                        tenant = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))

                ########################################################################################
                elif prop.name == "Greatwall Gardens Phase 2":
                    hh = get_specific_house_obj(propid,cb.bill_ref_num)
                    if hh:
                        tenant = hh.owner
                    else:
                        tenant = 'unidentified'
                elif prop.name == "Astrol Ridgeways":
                    tenant = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num.upper())
                    if not tenant:
                        tenant = "unidentified"
                ########################################################################################
                else:
                    tenant = "unidentified"
                #########################################################################################
            else:
                tenant = "unidentified"


            if isinstance(tenant, str):
                house = "unknown"
            else:
                if tenant.tenant_type == "resident" or tenant.tenant_type == "owner":
                    house = tenant.house
                else:
                    house = check_house_occupied(tenant)[1]

            if isinstance(tenant,str):
                tname = tenant
                thouse = house
            else:
                tname = tenant.name
                thouse = house.name


            return render_template("ajax_tenant_confirmation.html",tname=tname,thouse=thouse)

        if target == "period":
            period = get_billing_period(prop)
            nextperiod = get_next_month(period.month)

            propperiod=get_str_month(period.month)
            nextpropperiod = get_str_month(nextperiod)

            return render_template('ajax_prop_period.html',propperiod=propperiod,nextpropperiod=nextpropperiod)

        if target == "tenant name":
            house_obj = get_specific_house_obj_from_house_tenant_alt_alt(propid,house_name)
            if house_obj[1]:
                tenant_obj = house_obj[1]
            else:
                tenant_obj = check_occupancy(house_obj[0])[1]

            if tenant_obj.multiple_houses:
                houses = get_active_houses(tenant_obj)[1]
                return render_template('ajax_target_houses.html',house_list=houses,tenant_obj=tenant_obj)
            return f'<i class="fas fa-user mr-1"></i>: Tenant <span class="text-black mr-2">{tenant_obj.name}</span> balance: Kes <span class="text-danger">{tenant_obj.balance:,.1f}</span>'

        if target == "amount due":
            skip = False
            if cbid:
                cb = CtoBop.fetch_record_by_id(cbid)

                if cb.bill_ref_num:
                    # if cb.bill_ref_num.startswith("TNT"):
                    #     tenant_obj = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                    #     house_item = check_house_occupied(tenant_obj)[1]
                    #     bill = fetch_target_period_invoice(house_item,pay_period_date)

                    # elif cb.bill_ref_num.startswith("WN"):
                    #     tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                    #     house_item = tenant_obj.house
                    #     bill = fetch_target_period_owner_invoice(house_item,pay_period_date)

                    if cb.bill_ref_num.startswith("TNT"):
                        tenant = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                        if tenant:
                            hh = check_house_occupied(tenant)[1]
                            bill = fetch_target_period_invoice(hh,pay_period_date)

                        else:
                            tenant = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                            if tenant:
                                hh = check_house_occupied(tenant)[1]
                                bill = fetch_target_period_invoice(hh,pay_period_date)

                            else:
                                bill = None

                    elif cb.bill_ref_num.startswith("WN"):
                        tenant = PermanentTenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                        if tenant:
                            hh = tenant.house
                            bill = fetch_target_period_invoice(hh,pay_period_date)

                        else:
                            tenant = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                            if tenant:
                                hh = tenant.house
                                bill = fetch_target_period_invoice(hh,pay_period_date)
                            else:
                                bill = None

                    ########################################################################################
                    elif prop.name == "Greatwall Gardens Phase 2":
                        hh = get_specific_house_obj(propid,cb.bill_ref_num)
                        if hh:
                            bill = fetch_target_period_invoice(hh,pay_period_date)
                            tenant = hh.owner
                        else:
                            bill = None
                    elif prop.name == "Astrol Ridgeways":
                        tenant = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num.upper())
                        if tenant:
                            print("FOUND ASTROL GUY",tenant.name)
                            hh = check_house_occupied(tenant)[1]

                            bill = fetch_target_period_invoice(hh,pay_period_date)

                        else:
                            print("DID NOT FIND ASTROL GUY KATA SIM")
                            print("CBID NI HII",cb.bill_ref_num.upper())
                            print("NGOMBE NI HUYU",TenantOp.fetch_tenant_by_uid("RT92DZ7").uid)
                            bill = None

                    else:
                        skip = True
            else:
                skip = True

            if skip:
                print("running skip for amount due")
                house_obj = get_specific_house_obj_from_house_tenant_alt_alt(propid,house_name)
                if not house_obj[0]:
                    abort(403)

                if house_obj[1]:
                    tenant_obj = house_obj[1]
                else:
                    tenant_obj = check_occupancy(house_obj[0])[1]

                if tenant_obj.multiple_houses:
                    houses = get_active_houses(tenant_obj)[1]
                    return render_template('ajax_target_houses_alt.html',house_list=houses,tenant_obj=tenant_obj)

                if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
                    bill = fetch_target_period_owner_invoice(house_obj[0],pay_period_date)
                else:
                    bill = fetch_target_period_invoice(house_obj[0],pay_period_date)

            if bill:
                bill_balance = bill.balance
            else:
                bill_balance = 0.0

            return render_template('ajax_tenant_balance.html',totaldue=f'{bill_balance:,.1f}')

        if target == "tenant name2":
            house_obj = get_specific_house_obj(propid,house_name)
            bills = house_obj.monthlybills
            latest_bill = max(bills, key=lambda x: x.id) if bills else None
            
            if latest_bill:
                latest_bill_balance = latest_bill.balance
            else:
                latest_bill_balance = 0.0
            
            return f'<i class="fas fa-home mr-1"></i>: House  <span class="text-black mr-2">{house_obj.name}</span>  balance : Kes <span class="text-danger">{latest_bill_balance:,.1f}</span>'

        if target == "amount due alt":
            house_obj = get_specific_house_obj(propid,house_name)
            
            bills = house_obj.monthlybills

            latest_bill = max(bills, key=lambda x: x.id) if bills else None

            if latest_bill:
                latest_bill_balance = latest_bill.balance
            else:
                latest_bill_balance = 0.0
            
            return render_template('ajax_tenant_balance.html',totaldue=f'{latest_bill_balance:,.1f}')

        if target == "breakdown":

            skip = False
            if cbid:
                cb = CtoBop.fetch_record_by_id(cbid)

                if cb.bill_ref_num:
                    if cb.bill_ref_num.startswith("TNT"):
                        tenant = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                        if tenant:
                            hh = check_house_occupied(tenant)[1]
                            bill = fetch_target_period_invoice(hh,pay_period_date)

                        else:
                            tenant = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                            if tenant:
                                hh = check_house_occupied(tenant)[1]
                                bill = fetch_target_period_invoice(hh,pay_period_date)

                            else:
                                bill = None

                    elif cb.bill_ref_num.startswith("WN"):
                        tenant = PermanentTenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                        if tenant:
                            hh = tenant.house
                            bill = fetch_target_period_invoice(hh,pay_period_date)

                        else:
                            tenant = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                            if tenant:
                                hh = tenant.house
                                bill = fetch_target_period_invoice(hh,pay_period_date)
                            else:
                                bill = None

                    ########################################################################################
                    elif prop.name == "Greatwall Gardens Phase 2":
                        hh = get_specific_house_obj(propid,cb.bill_ref_num)
                        if hh:
                            bill = fetch_target_period_invoice(hh,pay_period_date)
                            tenant = hh.owner
                        else:
                            bill = None
                    elif prop.name == "Astrol Ridgeways":
                        tenant = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num.upper())
                        if tenant:
                            print("FOUND ASTROL GUY",tenant.name)
                            hh = check_house_occupied(tenant)[1]

                            bill = fetch_target_period_invoice(hh,pay_period_date)

                        else:
                            print("DID NOT FIND ASTROL GUY KATA SIM")
                            print("CBID NI HII",cb.bill_ref_num.upper())
                            print("NGOMBE NI HUYU",TenantOp.fetch_tenant_by_uid("RT92DZ7").uid)
                            bill = None
                    # if cb.bill_ref_num.startswith("TNT"):
                    #     tenant_obj = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                    #     house_item = check_house_occupied(tenant_obj)[1]
                    #     bill = fetch_target_period_invoice(house_item,pay_period_date)

                    # elif cb.bill_ref_num.startswith("WN"):
                    #     tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                    #     house_item = tenant_obj.house
                    #     bill = fetch_target_period_owner_invoice(house_item,pay_period_date)
                    else:
                        skip = True
            else:
                skip = True

            if skip:
                print("running skip for breakdown")
                if house_name2:
                    if house_name2 == "none selected":
                        return "<span class='text-danger text-xx'>Please specify house</span>"
                    house_obj = get_specific_house_obj(propid,house_name2)
                    tenant_obj = check_occupancy(house_obj)[1] # tenant
                else:
                    house_obj = get_specific_house_obj_from_house_tenant_alt_alt(propid,house_name)

                    if house_obj[1]:
                        tenant_obj = house_obj[1] # owner
                    else:
                        tenant_obj = check_occupancy(house_obj[0])[1] # tenant

                house_item = house_obj if house_name2 else house_obj[0]
            
                if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
                    bill = fetch_target_period_owner_invoice(house_item,pay_period_date)
                else:
                    bill = fetch_target_period_invoice(house_item,pay_period_date)


            if bill:
                # print("BILL DATE",bill.month,"/",bill.year)
                # print("PAID STATUS","RENT PAID",bill.rent_paid,"DEPOSIT PAID",bill.deposit_paid,"GARBAGE PAID",bill.garbage_paid,"TOTAL DUE",bill.total_bill)
                # print("BALANCE STATUS","RENT BALANCE",bill.rent_balance,"DEPOSIT BALANCE",bill.deposit_balance,"GARBAGE BALANCE",bill.garbage_balance,"OVERALL BALANCE",bill.balance)
                # print("DUE STATUS","RENT DUE",bill.rent_due,"DEPOSIT DUE",bill.deposit_due,"GARBAGE DUE",bill.garbage_due,"OVERALL DUE",bill.balance)
                return render_template('ajax_bill_breakdown.html',bill=bill)

            return "<span class='text-danger text-xx'>Invoice unavailable</span>"


    @login_required
    def post(self):
        current_period_payment = True
        prop_id = request.form.get('propid')
        propname = request.form.get('propname')

        propid = get_identifier(prop_id)

        if propname:
            prop = ApartmentOp.fetch_apartment_by_name(propname)
            propid = prop.id
        else:
            prop = ApartmentOp.fetch_apartment_by_id(propid)

        house_name = request.form.get('house')
        house_name2 = request.form.get('house2')

        bookingpaid = int(request.form.get('bookingpaid')) if request.form.get('bookingpaid') else 0
        instalmentpaid = int(request.form.get('instalmentpaid')) if request.form.get('instalmentpaid') else 0
        rentpaid = int(request.form.get('rentpaid')) if request.form.get('rentpaid') else 0
        waterpaid = int(request.form.get('waterpaid')) if request.form.get('waterpaid') else 0
        electricitypaid = int(request.form.get('electricitypaid')) if request.form.get('electricitypaid') else 0
        garbagepaid = int(request.form.get('garbagepaid')) if request.form.get('garbagepaid') else 0
        securitypaid = int(request.form.get('securitypaid')) if request.form.get('securitypaid') else 0
        servicepaid = int(request.form.get('servicepaid')) if request.form.get('servicepaid') else 0
        penaltypaid = int(request.form.get('penaltypaid')) if request.form.get('penaltypaid') else 0
        depositpaid = int(request.form.get('depositpaid')) if request.form.get('depositpaid') else 0
        agreementpaid = int(request.form.get('agreementpaid')) if request.form.get('agreementpaid') else 0

        cbid = request.form.get("cbid")

        book = "Booking balance" if bookingpaid else ""
        inst = "Instalment" if instalmentpaid else ""

        water = "Water" if waterpaid else ""
        rent = "Rent" if rentpaid else ""
        garbage = "Garbage" if garbagepaid else ""
        sec = "Security" if securitypaid else ""
        arr = ""
        dep = "Deposit" if depositpaid else ""
        serv = "Service" if servicepaid else ""

        narration = f"{rent} {water} {garbage} {sec} {serv} {dep} {book} {inst}"

        print(narration)

        bank = request.form.get("bank")

        payperiod = request.form.get("payperiod")
        paydate = request.form.get("date")
        paytime = request.form.get("time")

        textsms = request.form.get("sms")
        email = request.form.get("email")

        sms_bool = get_bool(textsms)
        email_bool = get_bool(email)

        if payperiod:
            pay_period = date_formatter_alt(payperiod)
            pay_period_date = parse(pay_period)
            current_period_payment = False
        else:
            current_period_payment = True
            pay_period_date = get_billing_period(prop)

        print("PAYPERIOOOOOOOD",pay_period_date)

        if paydate:

            formatted_paydate = date_formatter(paydate)

            if paytime:
                timestring = formatted_paydate + " " + paytime
                pay_date = parse(timestring)
            else:
                pay_date = parse(formatted_paydate)

        else:
            pay_date = datetime.datetime.now()
    
        paymode = request.form.get('paymode')#dropdown
        raw_bill_ref = request.form.get('bill_ref')#typed
        amount = request.form.get('paidamount')#typed
        overpayment = int(request.form.get('overpayment')) if request.form.get('overpayment') else 0


        valid_amount = validate_input(amount)

        if not valid_amount:
            return "<div class='center-btn text-danger text-xx'>Invalid amount !</div"

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
                    print("REFERENCE EXISTS >>","MONTH:",payob.pay_period.month,"PROP:",payob.apartment,"TENANT & HOUSE:",payob.tenant,payob.house,"ID:",payob.id,"VOID:",payob.voided)
                    return "<div class='center-btn text-danger text-xx'>Reference exists!</div"

        ########################################################################################

        skip = False

        tenant_id = None
        ptenant_id = None

        period = pay_period_date

        tenant_obj = None
        co = prop.company
        target_houses = []   

        if cbid:
            cb = CtoBop.fetch_record_by_id(cbid)

            if cb.bill_ref_num:
                # if cb.bill_ref_num.startswith("TNT"):
                #     tenant_obj = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                #     house_obj = check_house_occupied(tenant_obj)[1]
                #     target_houses.append(house_obj)
                #     tenant_id = tenant_obj.id

                #     print(">>>>> STARTING PAYMENT & TENANT TYPE")


                # elif cb.bill_ref_num.startswith("WN"):
                #     tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                #     house_obj = tenant_obj.house
                #     target_houses.append(house_obj)
                #     ptenant_id = tenant_obj.id

                #     print(">>>>> STARTING PAYMENT & OWNER TYPE")

                #######################################################################################
                if cb.bill_ref_num.startswith("TNT"):
                    tenant_obj = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                    if tenant_obj:
                        house_obj = check_house_occupied(tenant_obj)[1]
                        target_houses.append(house_obj)
                        tenant_id = tenant_obj.id
                    else:
                        tenant_obj = TenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                        if tenant_obj:
                            house_obj = check_house_occupied(tenant_obj)[1]
                            target_houses.append(house_obj)
                            tenant_id = tenant_obj.id
                        else:
                            print("TNT NOT FOUND")
                            abort(404) 

                elif cb.bill_ref_num.startswith("WN"):
                    tenant_obj = PermanentTenantOp.fetch_tenant_by_uid(cb.bill_ref_num)
                    if tenant_obj:
                        house_obj = tenant_obj.house
                        target_houses.append(house_obj)
                        tenant_id = tenant_obj.id
                    else:
                        tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(cb.bill_ref_num))
                        if tenant_obj:
                            house_obj = tenant_obj.house
                            target_houses.append(house_obj)
                            tenant_id = tenant_obj.id
                        else:
                            print("WN NOT FOUND")
                            abort(404) 

                ########################################################################################
                elif prop.name == "Greatwall Gardens Phase 2":
                    hh = get_specific_house_obj(propid,cb.bill_ref_num)
                    if hh:
                        house_obj = hh
                        target_houses.append(house_obj)
                        tenant_obj = hh.owner
                        tenant_id = tenant_obj.id
                    else:
                        print("HOUSE NOT FOUND")
                        abort(404) 
                elif prop.name == "Astrol Ridgeways":
                    tenant = TenantOp.fetch_tenant_by_uid(cb.bill_ref_num.upper())
                    if tenant:
                        house_obj = check_house_occupied(tenant_obj)[1]
                        target_houses.append(house_obj)
                        tenant_id = tenant_obj.id
                    else:
                        print("UID NOT FOUND")
                        abort(404) 
                ########################################################################################


                else:
                    skip = True
        else:
            skip = True



        if skip:
            print(">>>>> STARTING PAYMENT & SKIPPING")
            if house_name:
  
                if house_name2:

                    if house_name2 == "none selected":
                        return "<span class='text-danger text-xx'>Payment failed, please specify house!</span>"

                    str_houses = house_name2.replace(","," ")
                    houselist = list(str_houses.split(" "))

                    for hse in houselist:
                        hse_obj = get_specific_house_obj(propid,hse)
                        target_houses.append(hse_obj)

                else:
                    hse_obj = get_specific_house_obj_from_house_tenant_alt_alt(propid,house_name)
                    target_houses.append(hse_obj[0])

                house_obj = target_houses[0]

                try:
                    if not house_name2:
                        owner = get_specific_house_obj_from_house_tenant_alt_alt(propid,house_name)[1]
                        if owner:
                            tenant_obj = owner
                            ptenant_id = tenant_obj.id

                        else:
                            tenant_obj = check_occupancy(house_obj)[1]
                            tenant_id = tenant_obj.id
                    else:
                        tenant_obj = check_occupancy(house_obj)[1]
                        tenant_id = tenant_obj.id

                except:
                    print("FORGOT TO SELECT HOUSE WHILE MAKING PAYMENT")
                    abort(404) 


                if not tenant_obj:
                    print("FORGOT TO SELECT HOUSE WHILE MAKING PAYMENT")
                    abort(404)

            else:
                print("FORGOT TO SELECT HOUSE WHILE MAKING PAYMENT")
                abort(404)

        tenant_name = tenant_obj.name

        house_id = house_obj.id
        created_by = current_user.id
        chargetype_string = generate_string(water,rent,garbage,sec,arr,dep,serv)

        if not narration:
            narration = generate_string(water,rent,garbage,sec,arr,dep,serv)

        if aviv(current_user):
            narration = get_str_month(period.month)


        # monthly_charges = house_obj.monthlybills

        if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
            specific_charge_obj = fetch_target_period_owner_invoice(house_obj,pay_period_date)
        else:
            specific_charge_obj = fetch_target_period_invoice(house_obj,pay_period_date)

        # if tenant_obj.tenant_type == "owner":
        #     monthly_charges = tenant_obj.monthly_charges
        # else:
        #     monthly_charges = house_obj.monthlybills

        # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,period.month,period.year)

        # print("FOUND INV OF: ",specific_charge_obj.month,"/",specific_charge_obj.year,"amount due and bal:", specific_charge_obj.total_bill,"&",specific_charge_obj.balance)

        bal = specific_charge_obj.balance

        if tenant_obj.multiple_houses:
            pass
        else:
            # monthly_charges = house_obj.monthlybills
            # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,period.month)

            if specific_charge_obj and current_period_payment and current_user.company.name != "MULTIDIME AGENCIES":
                if specific_charge_obj.penalty:
                    standard_pen = house_obj.housecode.rentrate*0.1
                    accepted_balance = bal - 1000 - standard_pen
                    if valid_amount > accepted_balance:
                        if propid == 22:
                            dday = 5
                        else:
                            dday = 11
                        if pay_date.day < dday:
                            print("Fine status for", house_obj, "before payment >>>>> ",specific_charge_obj.fine_status)
                            bal -= specific_charge_obj.penalty
                            TenantOp.update_balance(tenant_obj,bal)
                            MonthlyChargeOp.update_balance(specific_charge_obj,bal)
                            update_total = specific_charge_obj.total_bill - specific_charge_obj.penalty
                            MonthlyChargeOp.update_monthly_charge(specific_charge_obj,"null","null","null","null","null","null","null","null",0.0,"null",update_total,None)
                            MonthlyChargeOp.update_fine_status(specific_charge_obj,"nil")
                            print("Fine status for", house_obj, "after payment >>>>> ",specific_charge_obj.fine_status)
                        else:
                            print("Paid late>>>>>>>>>>>")
                    else:
                        print("Paid little>>>>>>>>>>>")
                else:
                    print("No fines found>>>>>>>>>>>")
            elif specific_charge_obj and not current_period_payment:
                pass
            else:
                print("Not billed yet for ",get_str_month(period.month), ">>>>>>>>>>>")
                
        if paymode == "mpesa":
            description = "Manual Mpesa payment"
        elif paymode == "bank":
            description = bank if bank else None
        else:
            description = "Cash"
            bill_ref = "N/A"
        #######################################################################################
        # pay_period = paid to which bills
        # pay_date = alilipa lini?
        

        payment_obj = PaymentOp(paymode,bill_ref,description,narration,pay_date,period,bal,valid_amount,propid, house_id,tenant_id,ptenant_id,created_by)
        payment_obj.save()

        if cbid:
            cb = CtoBop.fetch_record_by_id(cbid)
            CtoBop.update_status(cb,"claimed")

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

        string_house = ""

        for h in target_houses:


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

                rent_paid = rentpaid + specific_charge_obj.rent_paid if specific_charge_obj.rent_paid is not None else 0
                rent_paid += overpayment
                water_paid = waterpaid + specific_charge_obj.water_paid if specific_charge_obj.water_paid is not None else 0
                penalty_paid = penaltypaid + specific_charge_obj.penalty_paid if specific_charge_obj.penalty_paid is not None else 0
                electricity_paid = electricitypaid + specific_charge_obj.electricity_paid if specific_charge_obj.electricity_paid  is not None else 0
                garbage_paid = garbagepaid + specific_charge_obj.garbage_paid if specific_charge_obj.garbage_paid is not None else 0
                security_paid = securitypaid+ specific_charge_obj.security_paid if specific_charge_obj.security_paid is not None else 0
                service_paid = servicepaid + specific_charge_obj.maintenance_paid if specific_charge_obj.maintenance_paid is not None else 0
                deposit_paid = depositpaid + specific_charge_obj.deposit_paid if specific_charge_obj.deposit_paid is not None else 0
                agreement_paid = agreementpaid + specific_charge_obj.agreement_paid if specific_charge_obj.agreement_paid is not None else 0

                MonthlyChargeOp.update_payments(specific_charge_obj,booking_paid,instalment_paid,rent_paid,water_paid,electricity_paid,garbage_paid,security_paid,service_paid,penalty_paid,deposit_paid,agreement_paid)
                PaymentOp.update_payments(payment_obj,booking_paid,instalment_paid,rentpaid,waterpaid,electricitypaid,garbagepaid,securitypaid,servicepaid,penaltypaid,depositpaid,agreementpaid)

                try:
                    bookbal = specific_charge_obj.booking_due - bookingpaid
                    instbal = specific_charge_obj.instalment_due - instalmentpaid

                    rentbal = specific_charge_obj.rent_due - rentpaid

                    rentbal -= overpayment
                    waterbal = specific_charge_obj.water_due - waterpaid
                    electricitybal = specific_charge_obj.electricity_due - electricitypaid
                    servicebal = specific_charge_obj.maintenance_due - servicepaid
                    penaltybal = specific_charge_obj.penalty_due - penaltypaid
                    securitybal = specific_charge_obj.security_due - securitypaid
                    garbagebal = specific_charge_obj.garbage_due - garbagepaid
                    depositbal = specific_charge_obj.deposit_due - depositpaid
                    agreementbal = specific_charge_obj.agreement_due - agreementpaid

                    MonthlyChargeOp.update_dues(specific_charge_obj,bookbal,instbal,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)
                except:
                    print("PAID TO LEGACY BILL")

            # elif not specific_charge_obj and not current_period_payment:
            #     subsequent_specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,billing_period.month,billing_period.year)

            #     db.session.expire(specific_charge_obj)
            #     bala = specific_charge_obj.balance
            #     bala-=valid_amount
            #     MonthlyChargeOp.update_balance(specific_charge_obj,bala)

            #     paid_amount = specific_charge_obj.paid_amount
            #     cumulative_pay = paid_amount + valid_amount
            #     MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
            #     MonthlyChargeOp.update_payment_date(specific_charge_obj,pay_date)

            #     if subsequent_specific_charge_obj:
            #         update_total = subsequent_specific_charge_obj.total_bill - valid_amount
            #         update_arrears = subsequent_specific_charge_obj.arrears - valid_amount
            #         update_balance = subsequent_specific_charge_obj.balance - valid_amount

            #         MonthlyChargeOp.update_arrears(subsequent_specific_charge_obj,update_arrears)
            #         MonthlyChargeOp.update_balance(subsequent_specific_charge_obj,update_balance)
            #         MonthlyChargeOp.update_monthly_charge(subsequent_specific_charge_obj,"null","null","null","null","null","null","null","null","null","null",update_total,None)


            stringname = h.name + " "

            string_house += stringname

        #################################################################################

        str_houses = string_house.rstrip(" ")
        house = list(str_houses.split(" "))

        # house = house_obj.name

        if payment_obj.receipt_num:
            receiptno = payment_obj.receipt_num
        else:
            receiptno = payment_obj.id
        
        paid = f'KES {payment_obj.amount:,.2f}'

        if bal < 1:
            bill = 0.0
        else:
            bill = (f"{bal:,.2f}")

        payment_id = payment_obj.id

        if email_bool and current_user.company_user_group.name != "User":
            if tenant_obj.email:
                try:
                    job9 = q.enqueue_call(
                        func=auto_send_mail_receipt, args=(payment_id,created_by,), result_ttl=5000
                    )
                except:
                    print("Redis server is off")
            else:
                print("Email address not found for tenant ",tenant_obj.name,"-",prop.name)
        else:
            print("Email has been disabled for this payment")

        # job11 = q.enqueue_call(
        #     func=auto_send_sms_receipt, args=(payment_id,created_by,), result_ttl=5000
        # )

        if payment_obj.balance > -1:
            baltitle = "Balance"
            outline = "text-danger"
            bal = f"KES {payment_obj.balance:,.0f}"
        else:
            baltitle = "Advance"
            outline = "text-success"
            bal = f"KES {payment_obj.balance*-1:,.0f}"

        if os.getenv("TARGET") == "lasshouse":
            receiptlink = f"https://cr.com/r/{rand_id}"
        else:
            receiptlink = f"https://kiotapay.com/r/{rand_id}"

        receipt = f"Receipt: {receiptlink}"

        if sms_bool and current_user.company_user_group.name != "Userrrrrr": #typo intentional

            job101 = q.enqueue_call(
                func=autosend_pending_smsreceipts, args=([payment_obj.id],), result_ttl=5000
            )


            # if payment_obj.ref_number != "N/A" and payment_obj.ref_number:
            #     reference = f'#{payment_obj.ref_number}'
            # else:
            #     reference = f'#{payment_obj.id}'

            # co = prop.company
            # str_co = co.name
            # raw_rem_sms =co.remainingsms
            # if tenant_obj.sms:
            #     if raw_rem_sms > 0:
            #         #Send the SMS
            #         tele = tenant_obj.phone
            #         name = tenant_obj.name
            #         fname = fname_extracter(name)
            #         if not fname:
            #             fname = name
            #         phonenum = sms_phone_number_formatter(tele)
            #         try:
            #             recipient = [phonenum]
            #             message = f"Rental payment Ref {reference}, sum of {paid} confirmed. \n{baltitle} {bal} \n\n{receipt} \n\n~{str_co}."
            #             sender = "KIOTAPAY"
            #             #Once this is done, that's it! We'll handle the rest
            #             response = sms.send(message, recipient, sender)
            #             print(response)
            #             resp = response["SMSMessageData"]["Recipients"][0]

            #             code = resp["statusCode"]
            #             smsid = resp["messageId"]
            #             PaymentOp.update_smsid(payment_obj,smsid)

            #             if code == 101: # SMS WAS SENT
            #                 PaymentOp.update_sms_status(payment_obj,"sent")
            #                 raw_cost = resp["cost"]
            #                 rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
            #                 CompanyOp.set_rem_quota(co,rem_sms)
            #                 print("EVERYTHING IS SMOOTH")
                            
            #             elif code == 403:
            #                 print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            #                 PaymentOp.update_sms_status(payment_obj,"fail")
                            
            #             elif code == 405:
            #                 response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
            #                 print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            
            #             elif code == 406:
            #                 PaymentOp.update_sms_status(payment_obj,"blocked")
            #                 raw_cost = resp["cost"]
            #                 rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
            #                 CompanyOp.set_rem_quota(co,rem_sms)
            #                 print("SMS BLOCKED BY ",tenant_obj,house_name,prop)
            #             else:
            #                 print("ALAAAAAAAA")

            #         except Exception as e:
            #             print(f"Houston, we have a problem {e}")
            #             PaymentOp.update_sms_status(payment_obj,"fail")
            #     else:
            #         txt = f"{co} has depleted sms"
            #         response = sms.send(txt, ["+254716674695"],"KIOTAPAY")
            #         print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN CLIENT HAS DEPLETED SMS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            # else:
            #     PaymentOp.update_sms_status(payment_obj,"off")
            #     print("XXXXXXXXXXXXXXXXXXXXXXXXXX Tenant sms disabled",tenant_obj,house_name,prop, "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


        else:
            PaymentOp.update_sms_status(payment_obj,"off")
            print("SMS has been disabled for this payment")
        ########################################################################################
        p = inflect.engine()
        int_amount = int(valid_amount)
        str_amount = p.number_to_words(int_amount)
        stramount = str_amount.capitalize()
        str_month = get_str_month(period.month)
        fname = fname_extracter(current_user.name)

        paydate = payment_obj.pay_date if payment_obj.pay_date else payment_obj.date

        address = None

        if current_user.company.name == "LaCasa":
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


        return render_template(
            'ajax_receiptpay.html',
            voided = "dispnone",
            tenant = tenant_name,
            house= house,
            amount=paid,
            str_amount=stramount,
            str_month=str_month,
            paydate=paydate.strftime("%d/%b/%y"),
            paytime=paydate.strftime("%X"),
            bill=bill,
            baltitle=baltitle,
            outline=outline,
            balance=bal,
            chargetype=narration,
            receiptno=receiptno,
            refnum=bill_ref,
            paymode=paymode,
            logopath=logo(current_user.company)[0],
            company=current_user.company,
            address=address,
            user=current_user.company if current_user.company == "MojaMbili Homes" else fname_extracter(current_user.name),
            prop=prop,
            randid=rand_id
        )


class UpdateBalance(Resource):
    def get(self):
        tenant_id = request.args.get("tenantid")
        ttype = request.args.get("ttype")

        if ttype == "owner" or ttype == "resident":
            tenant_obj = PermanentTenantOp.fetch_tenant_by_id(tenant_id)
            house_obj = tenant_obj.house
            current_invoice = fetch_current_owner_invoice(house_obj)
        else:
            tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
            house_obj = check_house_occupied(tenant_obj)[1]
            current_invoice = fetch_current_invoice(house_obj)

            
        print("Updating balance! currently",tenant_obj.balance)
        targetbills = []

        if tenant_obj.multiple_houses:
            bills = tenant_obj.monthly_charges
            targetbills = fetch_current_billing_period_bills(tenant_obj.apartment.billing_period,bills)
        else:
            targetbills.append(current_invoice)

        bill_balance = 0.0
        
        # print("totototal", len(targetbills))
        # print("totototal", targetbills[0].date.date())
        # print("totototal", targetbills[0].balance)

        try:
            for bill in targetbills:

                original_amount = bill.total_bill

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
                MonthlyChargeOp.update_monthly_charge(bill,values[1],values[0],values[2],"null",values[3],values[5],values[7],values[9],values[4],values[6],total_amount,current_user.id)

                print("NEW TOTAL :",total_amount,"OLD TOTAL :",original_amount)

                diff = total_amount - original_amount

                running_bal = tenant_obj.balance
                running_bal = running_bal + diff
                TenantOp.update_balance(tenant_obj,running_bal)

                if bill.paid_amount:
                    if bill.paid_amount < 0:
                        MonthlyChargeOp.update_payment(bill,0.0)
                        bal = total_amount
                    else:
                        bal = total_amount - bill.paid_amount
                else:
                    bal = total_amount

                MonthlyChargeOp.update_balance(bill,bal)

                db.session.expire(bill)
                
                bill_balance += bill.balance
                print(bill.month,bill.year,"KES",bill.balance)
        except:
            pass

        TenantOp.update_balance(tenant_obj,bill_balance)
        db.session.expire(tenant_obj)
        print("Balance updated! now",tenant_obj.balance)

        return (f"{bill_balance:,.1f} ")

class Receipt(Resource):
    @login_required
    def get(self):

        pay_id = request.args.get("payid")

        payment_obj = PaymentOp.fetch_payment_by_id(pay_id)
        db.session.expire(payment_obj)
        if payment_obj.voided:
            disp = ""
        else:
            disp = "dispnone"

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
            bal = f"Kes {payment_obj.balance:,.0f}"
        else:
            baltitle = "Advance"
            outline = "text-success"
            bal = f"Kes {payment_obj.balance*-1:,.0f}"

        server = fname_extracter(UserOp.fetch_user_by_id(payment_obj.user_id).name)

        co = current_user.company

        if payment_obj.receipt_num:
            receiptno = payment_obj.receipt_num
        else:
            receiptno = payment_obj.id

        prop = payment_obj.apartment

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

        if payment_obj.ptenant:
            tenant = payment_obj.ptenant
        else:
            tenant = payment_obj.tenant

        return render_template(
            'ajax_receiptpay.html',
            voided = disp,
            tenant = tenant.name,
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
            logopath=logo(current_user.company)[0],
            company=current_user.company,
            address=address,
            user=current_user.company if current_user.company == "MojaMbili Homes" else server,
            prop=prop,
            randid=payment_obj.rand_id if payment_obj.rand_id else "a"
        )

class EditPayment(Resource):
    @login_required
    def get(self):
        
        target = request.args.get("target")

        if target == "void payment":
            raw_payid = request.args.get("delid")
            payid = get_identifier(raw_payid)
        elif target == "edit payment":
            raw_payid = request.args.get("editid")
            payid = get_identifier(raw_payid)
        else:
            payid = request.args.get("payid")

        payment_obj = PaymentOp.fetch_payment_by_id(payid)
        print("PAYMENT PAID STATUS >>","RENT PAID",payment_obj.rent_paid,"DEPOSIT PAID",payment_obj.deposit_paid)
        return f"Tenant: <span class='text-black font-weight-bold'>{payment_obj.tenant.name}</span><br> Paid: <span class='text-black font-weight-bold'>Kshs {payment_obj.amount:,.0f}</span>"

    @login_required
    def post(self):
        amountpaid = request.form.get("paidamount")
        paydate = request.form.get("paydate")
        paytime = request.form.get("paytime")
        ref = request.form.get("editref")
        target = request.form.get("target")

        if target == "void payment":
            raw_payid = request.form.get("delid")
            payid = get_identifier(raw_payid)
        elif target == "edit payment":
            raw_payid = request.form.get("editid")
            payid = get_identifier(raw_payid)
        else:
            payid = request.form.get("payid")

        payment_obj = PaymentOp.fetch_payment_by_id(payid)
        period = payment_obj.pay_period

        if paydate:
            formatted_paydate = date_formatter(paydate)
        else:           
            formatted_paydate = db_date_formatter(str(payment_obj.pay_date.date()))

        if paytime:
            timestring = formatted_paydate + " " + paytime
            pay_date = parse(timestring)
        else:
            pay_date = parse(formatted_paydate)

        tenant_obj = TenantOp.fetch_tenant_by_id(payment_obj.tenant_id)
        tenant_bills = tenant_obj.monthly_charges

        target_bills = fetch_current_billing_period_bills(tenant_obj.apartment.billing_period,tenant_bills)

        target_bill = None

        for tbill in target_bills:
            if tbill.house_id == payment_obj.house_id:
                target_bill = tbill
                break
        # target_bill = get_specific_monthly_charge_obj(tenant_bills,period.month)



        if target == "void payment":
            # if str(current_user.company_user_group) == "User":
            #     abort(403)
            
            # if tenant_obj.multiple_houses:
            #     abort(403)
            #     # return "Voiding rejected"

            if target_bill:
                print("Payment voided")
                PaymentOp.void(payment_obj,True,current_user.id)

                balance = target_bill.balance
                balance += payment_obj.amount
                MonthlyChargeOp.update_balance(target_bill,balance)

                print("VOIDING PAYMENT NOW:::::::::::::PAYMENT PAID STATUS >>","RENT PAID",payment_obj.rent_paid,"DEPOSIT PAID",payment_obj.deposit_paid)

                try:
                    rent_paid = target_bill.rent_paid - payment_obj.rent_paid
                    water_paid = target_bill.water_paid - payment_obj.water_paid
                    penalty_paid = target_bill.penalty_paid - payment_obj.penalty_paid
                    electricity_paid = target_bill.electricity_paid - payment_obj.electricity_paid
                    garbage_paid = target_bill.garbage_paid - payment_obj.garbage_paid
                    security_paid = target_bill.security_paid - payment_obj.security_paid
                    service_paid = target_bill.maintenance_paid - payment_obj.maintenance_paid
                    deposit_paid = target_bill.deposit_paid - payment_obj.deposit_paid
                    agreement_paid = target_bill.agreement_paid - payment_obj.agreement_paid

                    MonthlyChargeOp.update_payments(target_bill,rent_paid,water_paid,electricity_paid,garbage_paid,security_paid,service_paid,penalty_paid,deposit_paid,agreement_paid)
                    print("VOID WORKING TO REMOVE PAYMENTS")
                except:
                    print("Voiding DID NOT AFFECT segregated payments")


                try:
                    rent_balance = target_bill.rent_due + payment_obj.rent_paid
                    water_balance = target_bill.water_due + payment_obj.water_paid
                    penalty_balance = target_bill.penalty_due + payment_obj.penalty_paid
                    electricity_balance = target_bill.electricity_due + payment_obj.electricity_paid
                    garbage_balance = target_bill.garbage_due + payment_obj.garbage_paid
                    security_balance = target_bill.security_due + payment_obj.security_paid
                    service_balance = target_bill.maintenance_due + payment_obj.maintenance_paid
                    deposit_balance = target_bill.deposit_due + payment_obj.deposit_paid
                    agreement_balance = target_bill.agreement_due + payment_obj.agreement_paid

                    MonthlyChargeOp.update_dues(target_bill,0.0,0.0,rent_balance,water_balance,electricity_balance,garbage_balance,security_balance,service_balance,penalty_balance,deposit_balance,agreement_balance)
                    print("VOID WORKING TO UPDATE BALANCES")

                except:
                    print("Voiding DID NOT AFFECT segregated payments")

                paid_amount = target_bill.paid_amount
                cumulative_pay = paid_amount - payment_obj.amount

                if cumulative_pay < 0.0:
                    cumulative_pay = 0.0
                    
                MonthlyChargeOp.update_payment(target_bill,cumulative_pay)
                MonthlyChargeOp.update_payment_date(target_bill,None)

                if period.month != payment_obj.apartment.billing_period.month:
                    update_total = target_bill.total_bill + payment_obj.amount
                    MonthlyChargeOp.update_monthly_charge(target_bill,"null","null","null","null","null","null","null","null","null","null",update_total,None)

                running_balance = tenant_obj.balance
                running_balance += payment_obj.amount
                TenantOp.update_balance(tenant_obj,running_balance)
            else:
                print("Payment voided, no target bill")
                PaymentOp.void(payment_obj,True,current_user.id)

                running_balance = tenant_obj.balance
                running_balance += payment_obj.amount
                TenantOp.update_balance(tenant_obj,running_balance)

            prop = payment_obj.apartment
            co = prop.company
            str_co = co.name

            raw_rem_sms =co.remainingsms
            if tenant_obj.sms:
                if raw_rem_sms > 0:
                    #Send the SMS
                    tele = tenant_obj.phone
                    name = tenant_obj.name
                    fname = fname_extracter(name)

                    if not fname:
                        fname = name
                    phonenum = sms_phone_number_formatter(tele)
                    if payment_obj.ref_number != "N/A":
                        reference = f'#{payment_obj.ref_number}'
                    else:
                        reference = f'No. {payment_obj.id}'

                    if tenant_obj.balance < 0:
                        bal = tenant_obj.balance * -1
                        running_bal = (f"Advance: Kes {bal:,.0f}")
                    else:
                        running_bal = (f"Balance: Kes {tenant_obj.balance:,.0f}")

                    amount = f'Kes {payment_obj.amount:,.0f}'

                    try:
                        pass
                        # temp_txt = f"Payment REVERSAL notification. \n\nDear {fname},kindly note that Rental payment ref-{reference} of {amount} has been VOIDED. \nYour balance has been updated as {running_bal}. \n\n ~{str_co}."
    
                        # recipient = [phonenum]
                        # sender = "KIOTAPAY"
                        # #Once this is done, that's it! We'll handle the rest
                        # response = sms.send(temp_txt, recipient, sender)
                        # print(response)
                        # resp = response["SMSMessageData"]["Recipients"][0]

                        # code = resp["statusCode"]

                        # if code == 101: # SMS WAS SENT
                        #     raw_cost = resp["cost"]
                        #     rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                        #     CompanyOp.set_rem_quota(co,rem_sms)
                        #     print("PAYMENT REVERSAL")
                            
                        # elif code == 403:
                        #     print("XXXXXXXXXXXXXXXXXXXXXXXXXX Invalid number", phonenum, " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            
                        # elif code == 405:
                        #     response = sms.send("Messages have been depleted!", ["+254716674695"],"KIOTAPAY")
                        #     print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN SMS DEPLETED XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                            
                        # elif code == 406:
                        #     raw_cost = resp["cost"]
                        #     rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                        #     CompanyOp.set_rem_quota(co,rem_sms)
                        #     print("SMS BLOCKED BY ",tenant_obj,prop)
                        # else:
                        #     print("ALAAAAAAAA")

                    except Exception as e:
                        print(f"Houston, we have a problem {e}")
                else:
                    txt = f"{co} has depleted sms"
                    response = sms.send(txt, ["+254716674695"],sender)
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXX HEY ADMIN CLIENT HAS DEPLETED SMS XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            else:
                print("XXXXXXXXXXXXXXXXXXXXXXXXXX Tenant sms disabled",tenant_obj,prop, "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")


        else:
            if target_bill:
                print("EDITING TIME",pay_date)
                edit_amount = validate_float_inputs_to_exclude_zeros(amountpaid)[0]
                
                old_amount = payment_obj.amount
                diff = old_amount - edit_amount

                pay_balance = payment_obj.balance - diff
                
                PaymentOp.update_payment(payment_obj,pay_date,edit_amount,pay_balance)

                PaymentOp.update_ref(payment_obj,ref)

                # balance = target_bill.balance
                # balance -= diff
                # MonthlyChargeOp.update_balance(target_bill,balance)

                # paid_amount = target_bill.paid_amount
                # cumulative_pay = paid_amount - diff
                # MonthlyChargeOp.update_payment(target_bill,cumulative_pay)
                MonthlyChargeOp.update_payment_date(target_bill,pay_date)

                # running_balance = tenant_obj.balance
                # running_balance -= diff
                # TenantOp.update_balance(tenant_obj,running_balance)

                print("Payment edited")
                PaymentOp.update_state(payment_obj,"Modified")



        # db.session.expire(prop)
        # payments = prop.payment_data

        # filtered_payments = fetch_current_billing_period_payments(period,payments)

        # detailed_payments_list = payment_details(filtered_payments)

        # payids = get_obj_ids(detailed_payments_list)

        # return render_template("ajax_payments_refresh.html",payids=payids,items=detailed_payments_list)




class ReceiveDepositPayment(Resource):
    """class"""
    @login_required
    def get(self):
        pass
    
    @login_required
    def post(self):

        apartmentssvar = request.form.get('apartmentsessionvariable')

        if apartmentssvar == '--Select Apartment--':
            pass
        else:
            stored_apartment = apartmentssvar

        house_name = request.form.get('house')#auto populated dropdown        
        tenant_name = request.form.get('tenant')
        p_amount = request.form.get('amount')#typed
        bill_ref = request.form.get('bill_ref')#typed
        billable = request.form.get('billable')#checkbox

        if not billable:
            billable = "False"

        bool_billable = return_bool(billable)

        try:
            amount = float(p_amount)
        except Exception as e:
            print(">>>>>>>>>>>>>>>>> EXCEPTION ...",e)
            amount = 0.0

        apartment_id = get_apartment_id(stored_apartment)
        tenant_list = filtertenants(apartment_id)
        house_list = filter_out_occupied_houses(stored_apartment)

        house_obj = None
        for house in house_list:
            if str(house) == house_name:
                house_obj = house
        tenant_obj = None
        for tenant in tenant_list:
            if str(tenant) == tenant_name:
                tenant_obj = tenant

        tenant_id = tenant_obj.id

        total_hse_dep = fetch_total_deposit(house_obj,billable)

        tenant_dep = tenant_obj.deposit

        bill = total_hse_dep-tenant_dep
        running_bal = bill-amount

        if amount <= 0.0:
            return render_template('ajaxghosthouse.html',alert="Payment not successful")
            
        #######################################################################################
        # payment_obj = PaymentOp(paymode,bill_ref,description,chargetype_string,bal,amount,apartment_id, house_id,tenant_id,created_by)
        # payment_obj.save()
        #################################################################################################
        tenant_dep += amount
        TenantOp.update_deposit(tenant_obj,tenant_dep)
        ###################################################################################
        templateLoader = FileSystemLoader(searchpath="app/templates")
        templateEnv = Environment(loader=templateLoader)
        TEMPLATE_FILE = "ajax_payment_mailreceipt.html"
        template = templateEnv.get_template(TEMPLATE_FILE)

        pay_time = datetime.datetime.now()
        paydate = pay_time.strftime("%B %d, %Y")
        paytime = pay_time.strftime("%H:%M:%S")
        pdftime = paydate + " " + paytime

        mail_logo = "../" + logo(current_user.company)[0]
        
        template_vars = {
            "tenant":tenant_name,
            "house":house_name,
            "amount":amount,
            "bill":bill,
            "balance":running_bal,
            "chargetype":"Deposit",
            "receiptno":tenant_obj.id,
            "refnum":bill_ref,
            "paymode":"Cash",
            "logopath":mail_logo,
            "pdftime":pdftime,
            "paytime":paydate,
            "prop":stored_apartment
        }
        html_out = template.render(template_vars)
        filename = f"app/temp/report_{tenant_id}.pdf"
        HTML(string=html_out,base_url=os.path.abspath(os.path.dirname(__file__))).write_pdf(filename,stylesheets=["app/static/eapartment-min.css","app/static/kiotapay.css"])
        ###################################################################################
        # LETS SEND EMAIL
        paid = (f"{amount:,}")
        mail_filename = f"report_{tenant_id}"
        with open("app/temp/"+mail_filename+".pdf",'rb') as fh:
            # print (fh)
            try:
                email_addr = tenant_obj.email
                txt = Message('Payment Acknowledgement', sender = 'info@kiotapay.com', recipients = [email_addr])
                txt.body = "Dear Tenant;" "\nThis is acknowledging that we have received payment of Kshs " + paid + "\nIn case of any query, feel free to contact us. \nThank you. \nKIndly find the attached receipt."
                # txt.html = render_template('ajax_payment_receipt.html',tenant=tenant_name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno,prop=stored_apartment)
                txt.attach(filename="payment_receipt.pdf",disposition="attachment",content_type="application/pdf",data=fh.read())
                # mail.send(txt)
            except Exception as e:
                print(str(e))
        #########################################################################################

        os.remove(filename)

        ########################################################################################

        #Send the SMS
        tele = tenant_obj.phone
        phonenum = sms_phone_number_formatter(tele)
        try:
            recipient = [phonenum]
            message = f"Rental Payment deposit acknowledged. We have received sum of Kshs. {amount}. Thank you."
            sender = "4211"
            #Once this is done, that's it! We'll handle the rest
            # response = sms.send(message, recipient)
            # print(response)
        except Exception as e:
            print(f"Houston, we have a problem {e}")
        ########################################################################################

        return render_template(
            'ajax_payment_receipt.html',
            tenant=tenant_name,
            house=house_name,
            amount=amount,
            bill=bill,
            balance=running_bal,
            chargetype="Deposit",
            receiptno=tenant_obj.id,
            refnum=bill_ref,
            paymode="Cash",
            logopath=logo(current_user.company)[0],
            prop=stored_apartment
        )

class Invoice(Resource):
    """invoice class"""
    def get(self):
        pass

    @login_required
    def post(self):
        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
        monthly_charges = tenant_obj.monthly_charges
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,month,year)
        house = check_house_occupied(tenant_obj)[1]
        apartment = ApartmentOp.fetch_apartment_by_id(tenant_obj.apartment_id).name
        return render_template(
            "ajaxinvoice.html",
            tenant_name=current_user.name,
            house=house,
            apartment=apartment,
            bill=specific_charge_obj
        )

class MyPayments(Resource):
    """invoice class"""
    def get(self):
        pass

    @login_required
    def post(self):
        run_check = request.form.get("runcheck")
        if run_check != "run_report":
            return render_template("ajaxpayments.html")
        detailed_payments_list = []
        str_month = request.form.get("selected_month")

        month = get_numeric_month(str_month)

        # if month == datetime.datetime.now().month:
        #     disp_month = "this month"
        # else:
        disp_month = f'in {get_str_month(month)}'
        
        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
        payments = tenant_obj.payments

        mypayments = get_specific_month_payments(payments,month)
        # house = check_house_occupied(tenant_obj)[1]
        # apartment = ApartmentOp.fetch_apartment_by_id(tenant_obj.apartment_id).name
        for pay in mypayments:
            pay_item = PaymentOp.view(pay)
            detailed_payments_list.append(pay_item)
    
        return render_template(
            "ajaxpayments.html",
            month=disp_month,
            tenant_name=current_user.name,
            bills=detailed_payments_list
        )

class TenantPayment(Resource):
    @login_required
    def get(self):
        pass
    @login_required
    def post(self):
        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
        tenant_id = tenant_obj.id
        
        #################################################################################################
        mpesarequests = tenant_obj.mpesarequests
        for obj in mpesarequests:
            if obj.active:
                print(">>>>>>>>>>>>>stale mpesa requests found, they are being auto resolved<<<<<<<<<<<")
                result = "Auto resolved"
                MpesaRequestOp.update_status(obj,False,result)

        mpesa_objs = tenant_obj.mpesarecords
        for obj in mpesa_objs:
            if not obj.claimed:
                print(">>>>>>>>>>>>>stale mpesa data found, they are being auto resolved<<<<<<<<<<<")
                MpesaPaymentOp.update_status(obj,True)
        ################################################################################################
        paymode = request.form.get("paymode")
        amount = request.form.get("paidamount")
        chargetype_string = request.form.get("payingfor")

        phonenum = tenant_obj.phone
        tenant_id = tenant_obj.id
        tel = phone_number_formatter(phonenum)

        if not chargetype_string:
            return render_template('ajaxreceiptfailedmpesa.html',tenant=tenant_obj.name,tel=tenant_obj.phone,response="Please indicate payment purpose")

        if paymode == "mpesa":
            try:
                stk_request = lipa_na_mpesa_online(amount,tel)
                # stk_request = lipa_na_mpesa_online2(amount,tel)
                print(stk_request.text)
                # resp = stk_request.status_code
                # response = stk_request.text

                json_response = (stk_request.json())
                if "errorMessage" in json_response:
                    result = json_response["errorMessage"]
                    if result == "No ICCID found on NMS":
                        failure = f"{phonenum} is not Mpesa-registered"
                    elif result == "Unable to lock subscriber, a transaction is already in process for the current subscriber":
                        failure = "We are unable to complete the request, try again in a few minutes."
                    elif result == "Invalid PhoneNumber":
                        failure = f"{phonenum} is not a valid phone number"
                    else:
                        failure = "Sorry, STK push payment is experiencing delays. Try again later."
                        # failure = result
                        
                    return render_template('ajaxreceiptfailedmpesa.html',tenant=tenant_obj.name,tel=tenant_obj.phone,response=failure)
                
                cri = json_response["CheckoutRequestID"]
                ###########################################
                print("#########STK PUSH INITIATED#########")
                print(cri)
                print("####################################")
                ###########################################
                stk_request_obj = MpesaRequestOp(cri,amount,phonenum,chargetype_string,tenant_id)
                stk_request_obj.save()

                return render_template('ajaxmpesa.html')
            except Exception as e:
                # this block is entered when there is no internet
                print(e)
                
                return render_template('ajaxreceiptfailedmpesa.html',tenant=tenant_obj.name,tel=tenant_obj.phone,response="Seems you have no internet")

        return render_template('ajaxreceiptfailedmpesa.html',tenant=tenant_obj.name,tel=tenant_obj.phone,response="Visa payment not supported currently")

class StkCallBackUrlProminance(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        body = data["Body"]

        stkcallback = body["stkCallback"]
        if stkcallback["ResultCode"] == 0:
            callbackmeta = stkcallback["CallbackMetadata"]
            item = callbackmeta["Item"] #list of json objs
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<MPESAMPESAMPESA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(item)
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<MPESAMPESAMPESA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            if len(item) == 4:
                amount_obj = item[0]
                amount_val = amount_obj["Value"]
                receipt_obj = item[1]
                receipt_val = receipt_obj["Value"]
                date_obj = item[2]
                date_val = date_obj["Value"]
                tel_obj = item[3]
                tel_val = tel_obj["Value"]

            else:

                amount_obj = item[0]
                amount_val = amount_obj["Value"]
                receipt_obj = item[1]
                receipt_val = receipt_obj["Value"]
                date_obj = item[3]
                date_val = date_obj["Value"]
                tel_obj = item[4]
                tel_val = tel_obj["Value"]

            tel = phone_number_formatter_r(tel_val)

            tenant_obj = TenantOp.fetch_tenant_by_tel(tel)
            tenant_id = tenant_obj.id

            print(amount_val,receipt_val,date_val,tel)

            mpesa_obj = MpesaPaymentOp(receipt_val,amount_val,tel,date_val,tenant_id)
            mpesa_obj.save()
        else:
            print(">>>>>>>>>>>>>>>>There was an error, printing datareceive callback error body>>>>>",body)

        return None

class StkCallBackUrlKiotapay(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        body = data["Body"]

        stkcallback = body["stkCallback"]
        if stkcallback["ResultCode"] == 0:
            callbackmeta = stkcallback["CallbackMetadata"]
            item = callbackmeta["Item"] #list of json objs
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<MPESAMPESAMPESA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(item)
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<MPESAMPESAMPESA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            if len(item) == 4:
                amount_obj = item[0]
                amount_val = amount_obj["Value"]
                receipt_obj = item[1]
                receipt_val = receipt_obj["Value"]
                date_obj = item[2]
                date_val = date_obj["Value"]
                tel_obj = item[3]
                tel_val = tel_obj["Value"]

            else:

                amount_obj = item[0]
                amount_val = amount_obj["Value"]
                receipt_obj = item[1]
                receipt_val = receipt_obj["Value"]
                date_obj = item[3]
                date_val = date_obj["Value"]
                tel_obj = item[4]
                tel_val = tel_obj["Value"]

            tel = phone_number_formatter_r(tel_val)

            tenant_obj = TenantOp.fetch_tenant_by_tel(tel)
            tenant_id = tenant_obj.id

            print(amount_val,receipt_val,date_val,tel)

            mpesa_obj = MpesaPaymentOp(receipt_val,amount_val,tel,date_val,tenant_id)
            mpesa_obj.save()
        else:
            print(">>>>>>>>>>>>>>>>There was an error, printing datareceive callback error body>>>>>",body)

        return None


class StkCallBackUrlAstrol(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        body = data["Body"]

        stkcallback = body["stkCallback"]
        if stkcallback["ResultCode"] == 0:
            callbackmeta = stkcallback["CallbackMetadata"]
            item = callbackmeta["Item"] #list of json objs
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ASTROL MPESAMPESAMPESA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(item)
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ASTROL MPESAMPESAMPESA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            if len(item) == 4:
                amount_obj = item[0]
                amount_val = amount_obj["Value"]
                receipt_obj = item[1]
                receipt_val = receipt_obj["Value"]
                date_obj = item[2]
                date_val = date_obj["Value"]
                tel_obj = item[3]
                tel_val = tel_obj["Value"]

            else:

                amount_obj = item[0]
                amount_val = amount_obj["Value"]
                receipt_obj = item[1]
                receipt_val = receipt_obj["Value"]
                date_obj = item[3]
                date_val = date_obj["Value"]
                tel_obj = item[4]
                tel_val = tel_obj["Value"]

            tel = phone_number_formatter_r(tel_val)

            tenant_obj = TenantOp.fetch_tenant_by_tel(tel)
            tenant_id = tenant_obj.id

            print(amount_val,receipt_val,date_val,tel)

            mpesa_obj = MpesaPaymentOp(receipt_val,amount_val,tel,date_val,tenant_id)
            mpesa_obj.save()
        else:
            print(">>>>>>>>>>>>>>>>There was an error, printing ASTROL datareceive callback error body>>>>>",body)

        return None

class CallBackUrlProminance(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        auto_consume_ctob(ctob_obj)

class CallBackUrlKiotapay(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        txtx = f'SMS MPESA PAYMENT DATA JUST IN from {bill_ref_num} of {trans_amnt}'

        response = sms.send(txtx, ["+254716674695"],"KIOTAPAY")

        auto_consume_ctob2(ctob_obj)

class CallBackUrlLatitude(Resource):
    def get(self):
        pass
    def post(self):
        try:
            #parse for json
            my_data=request.data
            my_json = my_data.decode('utf8').replace("'", '"')
            data = json.loads(my_json)

            trans_id = data['TransID']
            trans_time = data['TransTime']
            trans_amnt = data['TransAmount']
            trans_type = data['TransactionType']
            business_shortcode = data['BusinessShortCode']
            bill_ref_num = data['BillRefNumber']
            invoice_num = data['InvoiceNumber']
            msisdn = data['MSISDN']
            org_acc_bal = data['OrgAccountBalance']
            fname = data['FirstName']
            lname = data['LastName']

            print("MPESA DATA RECEIEVED: ",data)

            # message1 = f"Email: {email} has just signed up as an agent({company_name}). \nPlease follow up immediately. \n\nThis message was auto sent by the system."
            # response = sms.send(message1, ["+254716674695"],sender)

            ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
            ctob_obj.save()
        except:

            response = sms.send("PROD LATITUDE Equity has sent data", ["+254716674695"],"KIOTAPAY")

            #parse for json
            my_data=request.data
            my_json = my_data.decode('utf8').replace("'", '"')
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EQUITY EQUITY>>>>>>>>>",my_json)
            try:
                data = json.loads(my_json)
                print("#####################################EQUITY EQUITY EQUITY############################################")
                print(data)
                print("#####################################EQUITY EQUITY EQUITY############################################")
        
                print("Data will be proccessed here")
                
                username = data['username']
                password = data['password']
                billNumber = data['billNumber']
                billAmount = data['billAmount']
                customerRefNumber = data['CustomerRefNumber']
                bankReference = data['bankreference']
                transParticular = data['tranParticular']
                paymentMode = data['paymentMode']
                transDate = data['transactionDate']
                phoneNumber = data['phonenumber']
                debitAccount = data['debitaccount']
                debitCustName = data['debitcustname']

                data_type = "prod"

                data_obj = BankDataOp.fetch_record_by_ref(bankReference)
                if data_obj:
                    response =  {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":"Record with similar bank reference exists"}
                else:
                    data_obj = BankDataOp(username,password,billNumber,billAmount,customerRefNumber,bankReference,transParticular,paymentMode,transDate,phoneNumber,debitAccount,debitCustName,data_type)
                    data_obj.save()
                    response =  {"responseCode": "OK","responseMessage": "SUCCESSFUL","Message":f'Record #Ref{bankReference} saved successfully'}


            except Exception as e:
                sms.send("TEST LATITUDE Equity has error data", ["+254716674695"],"KIOTAPAY")
                response = {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":f'{e}'}
                print ("It failed, Bank integration has an error")

            resp = jsonify(response)
            return make_response(resp)


        # ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        # ctob_obj.save()

        # auto_consume_ctob2(ctob_obj)

class CallBackUrlMLatitude(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        print("MPESA DATA RECEIEVED: ",data)

        # message1 = f"Email: {email} has just signed up as an agent({company_name}). \nPlease follow up immediately. \n\nThis message was auto sent by the system."
        # response = sms.send(message1, ["+254716674695"],sender)

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        # ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        # ctob_obj.save()

        # auto_consume_ctob2(ctob_obj)
        response = sms.send("NEW LATITUDE MPESA DATA JUST IN", ["+254716674695"],"KIOTAPAY")


class CallBackUrlPremier(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        print("MPESA DATA RECEIEVED: ",data)

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        # auto_consume_ctob2(ctob_obj)

class CallBackUrlPremierRealty(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        print("MPESA DATA RECEIEVED: ",data)

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        # auto_consume_ctob2(ctob_obj)

class CallBackUrlAstrol(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        print("MPESA DATA RECEIEVED: ",data)

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        response = sms.send("ASTROL MPESA DATA JUST IN", ["+254716674695"],"KIOTAPAY")


        # auto_consume_ctob2(ctob_obj)

class CallBackUrlDenvic(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        print("MPESA DATA RECEIEVED: ",data)

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        # response = sms.send("Denvic MPESA DATA JUST IN", ["+254716674695"],"KIOTAPAY")


        # auto_consume_ctob2(ctob_obj)

class CallBackUrlDenvicTwo(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data['TransID']
        trans_time = data['TransTime']
        trans_amnt = data['TransAmount']
        trans_type = data['TransactionType']
        business_shortcode = data['BusinessShortCode']
        bill_ref_num = data['BillRefNumber']
        invoice_num = data['InvoiceNumber']
        msisdn = data['MSISDN']
        org_acc_bal = data['OrgAccountBalance']
        fname = data['FirstName']
        lname = data['LastName']

        print("MPESA DATA RECEIEVED: ",data)

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        # response = sms.send("Denvic MPESA DATA JUST IN", ["+254716674695"],"KIOTAPAY")


        # auto_consume_ctob2(ctob_obj)

class CallBackUrlVintage(Resource):
    def get(self):
        pass
    def post(self):
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        trans_id = data.get('TransID')
        trans_id = data.get('TransID')
        trans_time = data.get('TransTime')
        trans_amnt = data.get('TransAmount')
        trans_type = data.get('TransactionType')
        business_shortcode = data.get('BusinessShortCode')
        bill_ref_num = data.get('BillRefNumber')
        invoice_num = data.get('InvoiceNumber')
        msisdn = data.get('MSISDN')
        org_acc_bal = data.get('OrgAccountBalance')
        fname = data.get('FirstName')
        lname = data.get('LastName')

        print("MPESA DATA RECEIEVED: ",data)

        ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
        ctob_obj.save()

        response = sms.send("VINTAGE MPESA DATA JUST IN", ["+254716674695"],"KIOTAPAY")


        # auto_consume_ctob2(ctob_obj)


class CallBackUrlEquity(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("Equity test has sent data", ["+254716674695"],"KIOTAPAY")

        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EQUITY EQUITY>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################EQUITY EQUITY EQUITY############################################")
            print(data)
            print("#####################################EQUITY EQUITY EQUITY############################################")
       
            print("Data will be proccessed here")
            # trans_id = data['TransID']
            # trans_time = data['TransTime']
            # trans_amnt = data['TransAmount']
            # trans_type = data['TransactionType']
            # business_shortcode = data['BusinessShortCode']
            # bill_ref_num = data['BillRefNumber']
            # invoice_num = data['InvoiceNumber']
            # msisdn = data['MSISDN']
            # org_acc_bal = data['OrgAccountBalance']
            # fname = data['FirstName']
            # lname = data['LastName']

            # ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
            # ctob_obj.save()

            # auto_consume_ctob(ctob_obj)
        except:
            print ("It failed, Bank integration has an error")

        response = {"responseCode": "OK","responseMessage": "SUCCESSFUL"}
        resp = jsonify(response)
        return make_response(resp)


class CallBackUrlLatitudeEquity(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("PROD LATITUDE Equity has sent data", ["+254716674695"],"KIOTAPAY")

        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EQUITY EQUITY>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################EQUITY EQUITY EQUITY############################################")
            print(data)
            print("#####################################EQUITY EQUITY EQUITY############################################")
       
            print("Data will be proccessed here")
            
            username = data['username']
            password = data['password']
            billNumber = data['billNumber']
            billAmount = data['billAmount']
            customerRefNumber = data['CustomerRefNumber']
            bankReference = data['bankreference']
            transParticular = data['tranParticular']
            paymentMode = data['paymentMode']
            transDate = data['transactionDate']
            phoneNumber = data['phonenumber']
            debitAccount = data['debitaccount']
            debitCustName = data['debitcustname']

            data_type = "prod"

            data_obj = BankDataOp.fetch_record_by_ref(bankReference)
            if data_obj:
                response =  {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":"Record with similar bank reference exists"}
            else:
                data_obj = BankDataOp(username,password,billNumber,billAmount,customerRefNumber,bankReference,transParticular,paymentMode,transDate,phoneNumber,debitAccount,debitCustName,data_type)
                data_obj.save()
                response =  {"responseCode": "OK","responseMessage": "SUCCESSFUL","Message":f'Record #Ref{bankReference} saved successfully'}


        except Exception as e:
            sms.send("PROD LATITUDE Equity has error data", ["+254716674695"],"KIOTAPAY")
            response = {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":f'{e}'}
            print ("It failed, Bank integration has an error")

        resp = jsonify(response)
        return make_response(resp)


class CallBackUrlTestLatitudeEquity(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("TEST LATITUDE Equity has sent data", ["+254716674695"],"KIOTAPAY")

        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EQUITY EQUITY>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################EQUITY EQUITY EQUITY############################################")
            print(data)
            print("#####################################EQUITY EQUITY EQUITY############################################")
       
            print("Data will be proccessed here")

            username = data['username']
            password = data['password']
            billNumber = data['billNumber']
            billAmount = data['billAmount']
            customerRefNumber = data['CustomerRefNumber']
            bankReference = data['bankreference']
            transParticular = data['tranParticular']
            paymentMode = data['paymentMode']
            transDate = data['transactionDate']
            phoneNumber = data['phonenumber']
            debitAccount = data['debitaccount']
            debitCustName = data['debitcustname']

            data_type = "test"

            data_obj = BankDataOp.fetch_record_by_ref(bankReference)
            if data_obj:
                response =  {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":"Record with similar bank reference exists"}
            else:
                data_obj = BankDataOp(username,password,billNumber,billAmount,customerRefNumber,bankReference,transParticular,paymentMode,transDate,phoneNumber,debitAccount,debitCustName,data_type)
                data_obj.save()
                response =  {"responseCode": "OK","responseMessage": "SUCCESSFUL","Message":f'Record #Ref{bankReference} saved successfully'}


        except Exception as e:
            sms.send("TEST LATITUDE Equity has error data", ["+254716674695"],"KIOTAPAY")
            response = {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":f'{e}'}
            print ("It failed, Bank integration has an error")

        resp = jsonify(response)
        return make_response(resp)

class CallBackUrlSentomEquity(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("PROD SENTOM Equity has sent data", ["+254716674695"],"KIOTAPAY")

        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EQUITY EQUITY>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################EQUITY EQUITY EQUITY############################################")
            print(data)
            print("#####################################EQUITY EQUITY EQUITY############################################")
       
            print("Data will be proccessed here")
            
            username = data['username']
            password = data['password']
            billNumber = data['billNumber']
            billAmount = data['billAmount']
            customerRefNumber = data['CustomerRefNumber']
            bankReference = data['bankreference']
            transParticular = data['tranParticular']
            paymentMode = data['paymentMode']
            transDate = data['transactionDate']
            phoneNumber = data['phonenumber']
            debitAccount = data['debitaccount']
            debitCustName = data['debitcustname']

            data_type = "prod"

            data_obj = BankDataOp.fetch_record_by_ref(bankReference)
            if data_obj:
                response =  {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":"Record with similar bank reference exists"}
            else:
                data_obj = BankDataOp(username,password,billNumber,billAmount,customerRefNumber,bankReference,transParticular,paymentMode,transDate,phoneNumber,debitAccount,debitCustName,data_type)
                data_obj.save()
                response =  {"responseCode": "OK","responseMessage": "SUCCESSFUL","Message":f'Record #Ref{bankReference} saved successfully'}


        except Exception as e:
            sms.send("PROD sentom Equity has error data", ["+254716674695"],"KIOTAPAY")
            response = {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":f'{e}'}
            print ("It failed, Bank integration has an error")

        resp = jsonify(response)
        return make_response(resp)


class CallBackUrlTestSentomEquity(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("TEST SENTOM Equity has sent data", ["+254716674695"],"KIOTAPAY")

        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EQUITY EQUITY>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################EQUITY EQUITY EQUITY############################################")
            print(data)
            print("#####################################EQUITY EQUITY EQUITY############################################")
       
            print("Data will be proccessed here")

            username = data['username']
            password = data['password']
            billNumber = data['billNumber']
            billAmount = data['billAmount']
            customerRefNumber = data['CustomerRefNumber']
            bankReference = data['bankreference']
            transParticular = data['tranParticular']
            paymentMode = data['paymentMode']
            transDate = data['transactionDate']
            phoneNumber = data['phonenumber']
            debitAccount = data['debitaccount']
            debitCustName = data['debitcustname']

            data_type = "test"

            data_obj = BankDataOp.fetch_record_by_ref(bankReference)
            if data_obj:
                response =  {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":"Record with similar bank reference exists"}
            else:
                data_obj = BankDataOp(username,password,billNumber,billAmount,customerRefNumber,bankReference,transParticular,paymentMode,transDate,phoneNumber,debitAccount,debitCustName,data_type)
                data_obj.save()
                response =  {"responseCode": "OK","responseMessage": "SUCCESSFUL","Message":f'Record #Ref{bankReference} saved successfully'}


        except Exception as e:
            sms.send("TEST SENTOM Equity has error data", ["+254716674695"],"KIOTAPAY")
            response = {"responseCode": "OK","responseMessage": "UNSUCCESSFUL","errorMessage":f'{e}'}
            print ("It failed, Bank integration has an error")

        resp = jsonify(response)
        return make_response(resp)

class CallBackUrlLes(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("Lesama prod has sent data", ["+254716674695"],"KIOTAPAY")

        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>COOP TEST DATA>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################COOP COOP COOP############################################")
            print(data)
            print("#####################################COOP COOP COOP############################################")
       
            print("Data will be proccessed here")
            # trans_id = data['TransID']
            # trans_time = data['TransTime']
            # trans_amnt = data['TransAmount']
            # trans_type = data['TransactionType']
            # business_shortcode = data['BusinessShortCode']
            # bill_ref_num = data['BillRefNumber']
            # invoice_num = data['InvoiceNumber']
            # msisdn = data['MSISDN']
            # org_acc_bal = data['OrgAccountBalance']
            # fname = data['FirstName']
            # lname = data['LastName']

            # ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
            # ctob_obj.save()

            # auto_consume_ctob(ctob_obj)
        except:
            print ("It failed, Bank integration has an error")

        response = {"responseCode": "OK","responseMessage": "SUCCESSFUL"}
        resp = jsonify(response)
        return make_response(resp)

class CallBackUrlTestLes(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("Coop test has sent data", ["+254716674695"],"KIOTAPAY")

        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>COOP TEST DATA>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################COOP COOP COOP############################################")
            print(data)
            house_data = data["Narration"]
            amount = data["Amount"]

            valid_amount = validate_input(amount)
            current_period_payment = True
            
            print("#####################################COOP COOP COOP############################################")

            # propid = 135

            # proppp = ApartmentOp.fetch_apartment_by_id(propid)
            # period = proppp.billing_period

            # house_name = house_data[2:]

            # target_houses = []
       
            # hse_obj = get_specific_house_obj_from_house_tenant_alt(propid,house_name)

            # target_houses.append(hse_obj)

            # house_obj = target_houses[0]
            

            # tenant_obj = check_occupancy(house_obj)[1]

            # tenant_name = tenant_obj.name


            # house_id = house_obj.id
            # tenant_id = tenant_obj.id
            # created_by = current_user.id

            # chargetype_string = generate_string(water,rent,garbage,sec,arr,dep,serv)

            # if not narration:
            #     narration = generate_string(water,rent,garbage,sec,arr,dep,serv)


            # monthly_charges = house_obj.monthlybills
            # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,period.month,period.year)

            # # print("FOUND INV OF: ",specific_charge_obj.month,"/",specific_charge_obj.year,"amount due and bal:", specific_charge_obj.total_bill,"&",specific_charge_obj.balance)

            # bal = specific_charge_obj.balance

            # if tenant_obj.multiple_houses:
            #     pass
            # else:
            #     # monthly_charges = house_obj.monthlybills
            #     # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,period.month)

            #     if specific_charge_obj and current_period_payment and current_user.company.name != "MULTIDIME AGENCIES":
            #         if specific_charge_obj.penalty:
            #             standard_pen = house_obj.housecode.rentrate*0.1
            #             accepted_balance = bal - 1000 - standard_pen
            #             if valid_amount > accepted_balance:
            #                 if propid == 22:
            #                     dday = 5
            #                 else:
            #                     dday = 11
            #                 if pay_date.day < dday:
            #                     print("Fine status for", house_obj, "before payment >>>>> ",specific_charge_obj.fine_status)
            #                     bal -= specific_charge_obj.penalty
            #                     TenantOp.update_balance(tenant_obj,bal)
            #                     MonthlyChargeOp.update_balance(specific_charge_obj,bal)
            #                     update_total = specific_charge_obj.total_bill - specific_charge_obj.penalty
            #                     MonthlyChargeOp.update_monthly_charge(specific_charge_obj,"null","null","null","null","null","null","null","null",0.0,"null",update_total,None)
            #                     MonthlyChargeOp.update_fine_status(specific_charge_obj,"nil")
            #                     print("Fine status for", house_obj, "after payment >>>>> ",specific_charge_obj.fine_status)
            #                 else:
            #                     print("Paid late>>>>>>>>>>>")
            #             else:
            #                 print("Paid little>>>>>>>>>>>")
            #         else:
            #             print("No fines found>>>>>>>>>>>")
            #     elif specific_charge_obj and not current_period_payment:
            #         pass
            #     else:
            #         print("Not billed yet for ",get_str_month(period.month), ">>>>>>>>>>>")
                    
            # if paymode == "mpesa":
            #     description = "Manual Mpesa payment"
            # elif paymode == "bank":
            #     description = bank if bank else None
            # else:
            #     description = "Cash"
            #     bill_ref = "N/A"
            # #######################################################################################
            # # pay_period = paid to which bills
            # # pay_date = alilipa lini?
            

            # payment_obj = PaymentOp(paymode,bill_ref,description,narration,pay_date,period,bal,valid_amount,propid, house_id,tenant_id,created_by)
            # payment_obj.save()
            # #################################################################################################

            # rand_id = random_generator()
            # if PaymentOp.fetch_payment_by_rand_id(rand_id):
            #     rand_id = random_generator(size=11)
            #     awe = sms.send("Ran random the second time !", ["+254716674695"],sender)
            #     if PaymentOp.fetch_payment_by_rand_id(rand_id):
            #         rand_id = random_generator(size=12)
            #         awe = sms.send("Ran random the third time !", ["+254716674695"],sender)
            #         if PaymentOp.fetch_payment_by_rand_id(rand_id):
            #             rand_id = random_generator(size=13)
            #             awe = sms.send("Ran random the fouth time !", ["+254716674695"],sender)
            #             if PaymentOp.fetch_payment_by_rand_id(rand_id):
            #                 awe = sms.send("There is a problem with random, payment aborted !", ["+254716674695"],sender)
            #                 return "Payment could not be processed at this time! Try again later"

            # tenant_bal = tenant_obj.balance
            # tenant_bal -= valid_amount
            # TenantOp.update_balance(tenant_obj,tenant_bal)

            # running_balance = bal
            # running_balance-= valid_amount

            # PaymentOp.update_balance(payment_obj,running_balance)
            # PaymentOp.update_rand_id(payment_obj,rand_id)

            # string_house = ""

            # for h in target_houses:



            #     if specific_charge_obj and current_period_payment:

            #         db.session.expire(specific_charge_obj)
            #         bala = specific_charge_obj.balance
            #         bala-=valid_amount
            #         MonthlyChargeOp.update_balance(specific_charge_obj,bala)

            #         paid_amount = specific_charge_obj.paid_amount
            #         cumulative_pay = paid_amount + valid_amount
            #         MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
            #         MonthlyChargeOp.update_payment_date(specific_charge_obj,pay_date)

            #         rent_paid = rentpaid + specific_charge_obj.rent_paid if specific_charge_obj.rent_paid is not None else 0
            #         rent_paid += overpayment
            #         water_paid = waterpaid + specific_charge_obj.water_paid if specific_charge_obj.water_paid is not None else 0
            #         penalty_paid = penaltypaid + specific_charge_obj.penalty_paid if specific_charge_obj.penalty_paid is not None else 0
            #         electricity_paid = electricitypaid + specific_charge_obj.electricity_paid if specific_charge_obj.electricity_paid  is not None else 0
            #         garbage_paid = garbagepaid + specific_charge_obj.garbage_paid if specific_charge_obj.garbage_paid is not None else 0
            #         security_paid = securitypaid+ specific_charge_obj.security_paid if specific_charge_obj.security_paid is not None else 0
            #         service_paid = servicepaid + specific_charge_obj.maintenance_paid if specific_charge_obj.maintenance_paid is not None else 0
            #         deposit_paid = depositpaid + specific_charge_obj.deposit_paid if specific_charge_obj.deposit_paid is not None else 0
            #         agreement_paid = agreementpaid + specific_charge_obj.agreement_paid if specific_charge_obj.agreement_paid is not None else 0

            #         MonthlyChargeOp.update_payments(specific_charge_obj,rent_paid,water_paid,electricity_paid,garbage_paid,security_paid,service_paid,penalty_paid,deposit_paid,agreement_paid)
            #         PaymentOp.update_payments(payment_obj,rentpaid,waterpaid,electricitypaid,garbagepaid,securitypaid,servicepaid,penaltypaid,depositpaid,agreementpaid)

            #         try:
            #             rentbal = specific_charge_obj.rent_due - rentpaid
            #             rentbal -= overpayment
            #             waterbal = specific_charge_obj.water_due - waterpaid
            #             electricitybal = specific_charge_obj.electricity_due - electricitypaid
            #             servicebal = specific_charge_obj.maintenance_due - servicepaid
            #             penaltybal = specific_charge_obj.penalty_due - penaltypaid
            #             securitybal = specific_charge_obj.security_due - securitypaid
            #             garbagebal = specific_charge_obj.garbage_due - garbagepaid
            #             depositbal = specific_charge_obj.deposit_due - depositpaid
            #             agreementbal = specific_charge_obj.agreement_due - agreementpaid

            #             MonthlyChargeOp.update_dues(specific_charge_obj,rentbal,waterbal,electricitybal,garbagebal,securitybal,servicebal,penaltybal,depositbal,agreementbal)
            #         except:
            #             print("PAID TO LEGACY BILL")

            #     elif not specific_charge_obj and not current_period_payment:
            #         subsequent_specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,billing_period.month,billing_period.year)

            #         db.session.expire(specific_charge_obj)
            #         bala = specific_charge_obj.balance
            #         bala-=valid_amount
            #         MonthlyChargeOp.update_balance(specific_charge_obj,bala)

            #         paid_amount = specific_charge_obj.paid_amount
            #         cumulative_pay = paid_amount + valid_amount
            #         MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
            #         MonthlyChargeOp.update_payment_date(specific_charge_obj,pay_date)

            #         if subsequent_specific_charge_obj:
            #             update_total = subsequent_specific_charge_obj.total_bill - valid_amount
            #             update_arrears = subsequent_specific_charge_obj.arrears - valid_amount
            #             update_balance = subsequent_specific_charge_obj.balance - valid_amount

            #             MonthlyChargeOp.update_arrears(subsequent_specific_charge_obj,update_arrears)
            #             MonthlyChargeOp.update_balance(subsequent_specific_charge_obj,update_balance)
            #             MonthlyChargeOp.update_monthly_charge(subsequent_specific_charge_obj,"null","null","null","null","null","null","null","null","null","null",update_total,None)


            #     stringname = h.name + " "

            #     string_house += stringname

            # #################################################################################

            # str_houses = string_house.rstrip(" ")
            # house = list(str_houses.split(" "))

            # # house = house_obj.name

            # receiptno = payment_obj.id
            
            # paid = f'KES {payment_obj.amount:,.2f}'

            # if bal < 1:
            #     bill = 0.0
            # else:
            #     bill = (f"{bal:,.2f}")

            # payment_id = payment_obj.id

            # if email_bool and current_user.company_user_group.name != "User":
            #     if tenant_obj.email:
            #         try:
            #             job9 = q.enqueue_call(
            #                 func=auto_send_mail_receipt, args=(payment_id,created_by,), result_ttl=5000
            #             )
            #         except:
            #             print("Redis server is off")
            #     else:
            #         print("Email address not found for tenant ",tenant_obj.name,"-",prop.name)
            # else:
            #     print("Email has been disabled for this payment")

            # # job11 = q.enqueue_call(
            # #     func=auto_send_sms_receipt, args=(payment_id,created_by,), result_ttl=5000
            # # )

            # if payment_obj.balance > -1:
            #     baltitle = "Balance"
            #     outline = "text-danger"
            #     bal = f"KES {payment_obj.balance:,.0f}"
            # else:
            #     baltitle = "Advance"
            #     outline = "text-success"
            #     bal = f"KES {payment_obj.balance*-1:,.0f}"

            # receiptlink = f"https://kiotapay.com/r/{rand_id}"

            # receipt = f"Receipt: {receiptlink}"

            # if sms_bool and current_user.company_user_group.name != "User":

            #     job101 = q.enqueue_call(
            #         func=autosend_pending_smsreceipts, args=([payment_obj.id],), result_ttl=5000
            #     )


            print("Data will be proccessed here")
            # trans_id = data['TransID']
            # trans_time = data['TransTime']
            # trans_amnt = data['TransAmount']
            # trans_type = data['TransactionType']
            # business_shortcode = data['BusinessShortCode']
            # bill_ref_num = data['BillRefNumber']
            # invoice_num = data['InvoiceNumber']
            # msisdn = data['MSISDN']
            # org_acc_bal = data['OrgAccountBalance']
            # fname = data['FirstName']
            # lname = data['LastName']

            # ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
            # ctob_obj.save()

            # auto_consume_ctob(ctob_obj)
        except:
            print ("It failed, Bank integration has an error")

        response = {"responseCode": "OK","responseMessage": "SUCCESSFUL"}
        resp = jsonify(response)
        return make_response(resp)

class CallBackUrlEquityProd(Resource):
    def get(self):
        pass
    def post(self):
        response = sms.send("Equity prod has sent data", ["+254716674695"],"KIOTAPAY")
        #parse for json
        my_data=request.data
        my_json = my_data.decode('utf8').replace("'", '"')
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>EQUITY EQUITY>>>>>>>>>",my_json)
        try:
            data = json.loads(my_json)
            print("#####################################EQUITY EQUITY EQUITY PRODUCTION############################################")
            print(data)
            print("#####################################EQUITY EQUITY EQUITY PRODUCTION############################################")
       
            print("Data will be proccessed here")
            # trans_id = data['TransID']
            # trans_time = data['TransTime']
            # trans_amnt = data['TransAmount']
            # trans_type = data['TransactionType']
            # business_shortcode = data['BusinessShortCode']
            # bill_ref_num = data['BillRefNumber']
            # invoice_num = data['InvoiceNumber']
            # msisdn = data['MSISDN']
            # org_acc_bal = data['OrgAccountBalance']
            # fname = data['FirstName']
            # lname = data['LastName']

            # ctob_obj = CtoBop(trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname)
            # ctob_obj.save()

            # auto_consume_ctob(ctob_obj)
        except:
            print ("It failed, Bank integration has an error")

        response = {"responseCode": "OK","responseMessage": "SUCCESSFUL"}
        resp = jsonify(response)
        return make_response(resp)

class ResultUrl(Resource):
    """transaction status api, not in use"""
    def get(self,shortcode=None):
        if shortcode:
            sc = str(shortcode)
            records = CtoBop.fetch_all_records_by_shortcode(sc)
           
            senddata = []
            for record in records:
                mydict = CtoBop.view(record)
                senddata.append(mydict)
            # print(senddata)
            return make_response( jsonify(senddata))
        errormsg = [{"error":"Please provide valid arguments"}]
        return jsonify(errormsg)

class TestApi(Resource):
    def get(self):
        # import pdb; pdb.set_trace()
        mydata = requests.get("https://kiotapay.com/getdata/4012401")
        # print(mydata)
        # print(mydata.status_code)

        dat = mydata.json()
        return mydata

    def post(self):
        pass

class ConsumeMpesaData(Resource):
    def get(self):
        pass
    @login_required
    def post(self):
        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)

        tenant_id = tenant_obj.id
        mpesarequests = tenant_obj.mpesarequests
        chargetype_string = None
        target_obj = None #target request obj to be updated

        for obj in mpesarequests:
            if obj.active:
                print(">>>>>>>>> active request found, acting upon it!")
                chargetype_string = obj.chargetype
                target_obj = obj
                break

        mpesa_objs = tenant_obj.mpesarecords
        for obj in mpesa_objs:
            if not obj.claimed:
                print(">>>>>>>>Unclaimed datareceive record found, acting upon it!")
                description = "Stk push auto-payment"
                # charged_amount = tenant_obj.balance
                ref_number = obj.ref_number              
                apartment_id = tenant_obj.apartment_id
                house_id = check_house_occupied(tenant_obj)[1].id
                prop = check_house_occupied(tenant_obj)[2].apartment
                try:
                    agent = UserOp.fetch_user_by_username(prop.agent_id)
                except:
                    agent = prop.owner

                co = agent.company

                logopath = logo(co)[0]
                #############################################################################
                #lets fetch c2b payment obj
                payment_obj = PaymentOp.fetch_payment_by_ref(ref_number)
                if payment_obj:
                    #lets update its chargetype string
                    PaymentOp.update_payment_info(payment_obj,description,chargetype_string)
                    # lets get the charged amount
                    charged_amount = payment_obj.charged_amount
                    amount_paid = payment_obj.amount
                    ############################################################################
                    p = inflect.engine()
                    int_amount = int(payment_obj.amount)
                    str_amount = p.number_to_words(int_amount)
                    stramount = str_amount.capitalize()
                    ############################################################################
                    # amount = obj.amount
                    # paymode = "mpesa"
                    # created_by = current_user.id
                    # payment_obj = PaymentOp(paymode,ref_number,description,chargetype_string,charged_amount,amount,apartment_id,house_id,tenant_id,created_by)
                    # payment_obj.save() # ctb will handle all payments

                    # running_balance = tenant_obj.balance
                    # running_balance-=float(amount)
                    # TenantOp.update_balance(tenant_obj,running_balance)
                    # PaymentOp.update_balance(payment_obj,running_balance)

                    # month = datetime.datetime.now().month
                    # monthly_charges = tenant_obj.monthly_charges
                    # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,month)
                    # bala = specific_charge_obj.balance
                    # bala-=float(amount)
                    # MonthlyChargeOp.update_balance(specific_charge_obj,bala)

                    # paid_amount = specific_charge_obj.paid_amount
                    # cumulative_pay = paid_amount + float(amount)
                    # MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)

                    MpesaPaymentOp.update_status(obj,True)
                    MpesaRequestOp.update_status(target_obj,False,"Transaction was successful")

                    house = HouseOp.fetch_house_by_id(house_id).name
                    # paid = (f"{float(amount):,}")
                    paid = (f"{float(amount_paid):,}")

                    if charged_amount < 1:
                        bill = 0.0
                    else:
                        bill = (f"{charged_amount:,}")

                    running_bal = (f"{tenant_obj.balance:,}")
                    receiptno = payment_obj.id

                    # #Send the SMS
                    # tele = tenant_obj.phone
                    # phonenum = sms_phone_number_formatter(tele)
                    # try:
                    #     recipient = [phonenum]
                    #     message = f"Rental payment Confirmed. We have received sum of Kshs. {paid}. Outstanding balance is Kshs. {running_bal}"
                    #     sender = "4211"
                    #     #Once this is done, that's it! We'll handle the rest
                    #     response = sms.send(message, recipient)
                    #     print(response)
                    # except Exception as e:
                    #     print(f"Houston, we have a problem {e}")


                    
                    # return render_template('ajaxreceiptmpesa.html',tenant=tenant_obj.name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,ref=ref_number,receiptno=receiptno)
                    
                    return render_template(
                    'ajax_payment_receipt.html',
                    tenant=tenant_obj.name,
                    house=house,
                    amount=paid,
                    str_amount=stramount,
                    str_month=get_str_month(payment_obj.pay_date.month),
                    paydate=payment_obj.pay_date.date(),
                    bill=bill,
                    balance=running_bal,
                    chargetype=chargetype_string,
                    receiptno=receiptno,
                    refnum=ref_number,
                    paymode="Mpesa",
                    logopath=logopath,
                    company=co,
                    user="N/A",
                    prop=prop
                )

                return "Something went wrong, we have commenced investigation into the issue."

        return render_template('ajaxcallbackfail.html')

class ResetAllMpesaData(Resource):
    def get(self):
        mpesa_requests = MpesaRequestOp.fetch_all_records()

        for obj in mpesa_requests:
            if obj.active:
                MpesaRequestOp.update_status(obj,False,"Transaction was successful")

        mpesa_data = MpesaPaymentOp.fetch_all_records()
        for obj in mpesa_data:
            if not obj.claimed:
                MpesaPaymentOp.update_status(obj,True)
        return "data reset"

class QueryMpesaTrans(Resource):
    """stk status api, in use"""
    def get(self):
        pass
    @login_required
    def post(self):

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)

        tenant_id = tenant_obj.id
        mpesarequests = tenant_obj.mpesarequests
        chargetype_string = None
        target_obj = None #target request obj to be updated

        for obj in mpesarequests:
            if obj.active:
                chargetype_string = obj.chargetype
                target_obj = obj
                break

        if target_obj:
            cri = target_obj.checkoutrequestid
            str_cri = str(cri)
            query = stkquery(str_cri)
            try:
                json_response = (query.json())
                result = json_response["ResultDesc"]
                print(result)
            except:
                result = "Timed out"

            if result == "The service request is processed successfully.": # transaction was smooth
                result = "Transaction was successful"
                description = "Non-callback Stk push payment"
                apartment_id = tenant_obj.apartment_id
                house_id = check_house_occupied(tenant_obj)[1].id
                prop = check_house_occupied(tenant_obj)[2].apartment
                try:
                    agent = UserOp.fetch_user_by_username(prop.agent_id)
                except:
                    agent = prop.owner

                co = agent.company

                logopath = logo(co)[0]
                ###########################################################################################
                #lets fetch c2b payment obj
                payment_obj = PaymentOp.fetch_latest_payment_by_tenant_id(tenant_id)
                if payment_obj.amount == target_obj.amount:
                    #lets update its chargetype string
                    PaymentOp.update_payment_info(payment_obj,description,chargetype_string)
                    # lets get the charged amount
                    charged_amount = payment_obj.charged_amount
                    amount_paid = payment_obj.amount
                    ref_number = payment_obj.ref_number

                    ############################################################################
                    p = inflect.engine()
                    int_amount = int(payment_obj.amount)
                    str_amount = p.number_to_words(int_amount)
                    stramount = str_amount.capitalize()
                    ############################################################################
                    # charged_amount = tenant_obj.balance
                    # amount = target_obj.amount
                    # tel = target_obj.phone
                    # paymode = "mpesa"
                    # created_by = current_user.id
                    # payment_obj = PaymentOp(paymode,cri,description,chargetype_string,charged_amount,amount,apartment_id,house_id,tenant_id,created_by)
                    # payment_obj.save()

                    # running_balance = tenant_obj.balance
                    # running_balance-=float(amount)
                    # TenantOp.update_balance(tenant_obj,running_balance)
                    # PaymentOp.update_balance(payment_obj,running_balance)

                    # month = datetime.datetime.now().month
                    # monthly_charges = tenant_obj.monthly_charges
                    # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,month)
                    # bala = specific_charge_obj.balance
                    # bala-=float(amount)
                    # MonthlyChargeOp.update_balance(specific_charge_obj,bala)

                    # paid_amount = specific_charge_obj.paid_amount
                    # cumulative_pay = paid_amount + float(amount)
                    # MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)

                    MpesaRequestOp.update_status(target_obj,False,result)

                    house = HouseOp.fetch_house_by_id(house_id).name
                    # paid = (f"{float(amount):,}")
                    paid = (f"{float(amount_paid):,}")

                    if charged_amount < 1:
                        bill = 0.0
                    else:
                        bill = (f"{charged_amount:,}")

                    running_bal = (f"{tenant_obj.balance:,}")
                    receiptno = payment_obj.id

                    # #Send the SMS
                    # tele = tenant_obj.phone
                    # phonenum = sms_phone_number_formatter(tele)
                    # try:
                    #     recipient = [phonenum]
                    #     message = f"Rental payment Confirmed. We have received sum of Kshs {paid} Outstanding balance Kshs {running_bal}"
                    #     sender = "4211"
                    #     #Once this is done, that's it! We'll handle the rest
                    #     response = sms.send(message, recipient)
                    #     print(response)
                    # except Exception as e:
                    #     print(f"Houston, we have a problem {e}")

                    # # LETS SEND EMAIL
                    # try:
                    #     email_addr = tenant_obj.email
                    #     txt = Message('Payment Acknowledgement', sender = 'info@kiotapay.com', recipients = [email_addr])
                    #     # txt.body = "Dear Tenant;" "\nThis is acknowledge that we have received payment of Kshs " + paid + "\nIn case of any query, feel free to contact us. \nThank you."
                    #     txt.html = render_template('ajaxreceipt2.html',tenant=tenant_obj.name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,receiptno=receiptno)
                    #     mail.send(txt)
                    # except Exception as e:
                    #     print(str(e))
                    
                    # return render_template('ajaxreceiptmpesa.html',tenant=tenant_obj.name,house=house,amount=paid,bill=bill,balance=running_bal,chargetype=chargetype_string,ref=ref_number,receiptno=receiptno)
                    return render_template(
                    'ajax_payment_receipt.html',
                    tenant=tenant_obj.name,
                    house=house,
                    amount=paid,
                    str_amount=stramount,
                    str_month=get_str_month(payment_obj.pay_date.month),
                    paydate=payment_obj.pay_date.date(),
                    bill=bill,
                    balance=running_bal,
                    chargetype=chargetype_string,
                    receiptno=receiptno,
                    refnum=ref_number,
                    paymode="Mpesa",
                    logopath=logopath,
                    company=co,
                    user="N/A",
                    prop=prop
                )
                failure = "Something went wrong, We are investigating the issue"
                return render_template('ajaxreceiptfailedmpesa.html',tenant=tenant_obj.name,tel=tenant_obj.phone,response=failure)

            elif result == "The initiator information is invalid.":
                result = "You entered wrong pin!"
            elif result == "The balance is insufficient for the transaction":
                result = "You have insufficient funds"
            elif result == "Request cancelled by user":
                result = "You cancelled the request"
            else:
                result = "Request Timed out, try again"

            MpesaRequestOp.update_status(target_obj,False,result)
            return render_template('ajaxreceiptfailedmpesa.html',tenant=tenant_obj.name,tel=tenant_obj.phone,response=result)
                
        return "Kindly make mpesa request first"

class ViewMonthlyReading(Resource):
    @login_required
    def get(self):
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        present_year = datetime.datetime.now().year

        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'report_monthlyreadings.html',
            tenantlist=[],
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            apartment_list=apartment_list,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        present_year = datetime.datetime.now().year
        present_month = datetime.datetime.now().month

        year = request.form.get("year")
        month = request.form.get("month")

        if not year:
            int_year = present_year
        else:
            int_year = int(year)

        if not month:
            int_month = present_month
        else:
            int_month = get_numeric_month(month)

        current_month_readings = []
        raw_read_list = []
        charge_members = []
        read_list = []

        selected_apartment = request.form.get("prop")
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        monthlyreading_list = MeterReadingOp.fetch_all_readings_by_apartment(apartment_id)
        for bill in monthlyreading_list:
            if bill.reading_period:
                if bill.reading_period.year == int_year and bill.reading_period.month == int_month:
                    current_month_readings.append(bill)

        for reading in current_month_readings:
            reading_item = MeterReadingOp.view(reading)
            raw_read_list.append(reading_item)


        for item in raw_read_list:
            charge_member = item["amount"]
            charge_members.append(charge_member)

            if item["description"] != "initial reading":
                read_list.append(item)
            # if item["charged"] == "not charged":
            #     try:
            #         read_list.remove(item)
            #         print("removing")
            #     except Exception as e:
            #         print("ererrerer",e)
        
        start = 0
        classids = []
        for i in read_list:
            start += 1
            house = i['house'].name
            if house.startswith("0") or house.startswith("G") or house.startswith("A"):
                i['floor'] = "Gnd Floor"
                i['floorclass'] = "groundfloor"
                classids.append("groundfloor")
            elif house.startswith("1") or house.startswith("B"):
                i['floor'] = "1st Floor"
                i['floorclass'] = "firstfloor"
                classids.append("firstfloor")
            elif house.startswith("2") or house.startswith("C"):
                i['floor'] = "2nd Floor"
                i['floorclass'] = "secondfloor"
                classids.append("secondfloor")
            elif house.startswith("3") or house.startswith("D"):
                i['floor'] = "3rd Floor"
                i['floorclass'] = "thirdfloor"
                classids.append("thirdfloor")
            elif house.startswith("4") or house.startswith("E"):
                i['floor'] = "4th Floor"
                i['floorclass'] = "fourthfloor"
                classids.append("fourthfloor")
            elif house.startswith("5") or house.startswith("F"):
                i['floor'] = "5th Floor"
                i['floorclass'] = "fifthfloor"
                classids.append("fifthfloor")
            elif house.startswith("6") or house.startswith("H"):
                i['floor'] = "6th Floor"
                i['floorclass'] = "sixthfloor"
                classids.append("sixthfloor")
            else:
                i['floor'] = "Other"
                i['floorclass'] = "rooftop"
                classids.append("rooftop")

        class_ids = ','.join(map(str, classids))

        total_charge = 0.0
        for i in charge_members:
            try:
                total_charge += i
            except:
                pass

        # print(read_list)

        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        month=get_str_month(int_month)
        timeline = f"{month} - ({int_year})"
        return Response(render_template(
            'report_monthlyreadings.html',
            bills=read_list,
            totalbills=(f"{total_charge:,}"),
            tenantlist=[],
            classids=class_ids,
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            timeline=timeline,
            apartment_list=apartment_list,
            prop=selected_apartment,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name))

class ViewWaterCharge(Resource):
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'view_waterbills.html',
            tenantlist=[],
            apartment_list=apartment_list,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        bill_list = []
        water_charges = []
        selected_apartment = request.form.get("selected_apartment")
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        charges = ChargeOp.fetch_charges_by_apartment_id(apartment_id)
        for charge in charges:
            if charge.charge_type_id == 2:
                bill_list.append(charge)

        for bill in bill_list:
            bill_item = ChargeOp.view(bill)
            water_charges.append(bill_item)

        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'view_waterbills.html',
            bills=water_charges,
            apartment_list=apartment_list,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

class ViewHouses(Resource):
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'report_houses.html',
            props=apartment_list,
            name=current_user.name,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            tenantlist=[]))

    def post(self):
        house_list = []
        
        selected_apartment = request.form.get("selected_apartment")
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        occupied_houses = filter_in_occupied_houses(selected_apartment)
        all_units = apartment_obj.houses
        unoccupied_houses = len(all_units)-len(occupied_houses)

        houses = apartment_obj.houses
        for house in houses:
            house_item = HouseOp.view(house)
            house_list.append(house_item)

        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'report_houses.html',
            bills=house_list,
            props=apartment_list,
            occupancy=len(occupied_houses),
            vacancy=unoccupied_houses,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name,
            tenantlist=[]))

class ViewMeters(Resource):
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'view_meters.html',
            apartment_list=apartment_list,
            name=current_user.name,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            tenantlist=[]))

    def post(self):
        meter_list = []
        
        # selected_apartment = request.form.get("selected_apartment")
        # apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        # apartment_id = apartment_obj.id

        meters = MeterOp.fetch_all_meters()
        for meter in meters:
            meter_item = MeterOp.view(meter)
            meter_list.append(meter_item)

        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'view_meters.html',
            bills=meter_list,
            apartment_list=apartment_list,
            name=current_user.name,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            tenantlist=[]))

class ViewBookings(Resource):
    @login_required
    def get(self):

        return Response(render_template('view_bookings.html', name=current_user.name))

    def post(self):
        book_list = []
        bookings = []

        tenants = TenantOp.fetch_all_tenants()
        for tenant in tenants:
            if not tenant.house_allocated:
                bookings.append(tenant)

        for booking in bookings:
            book_item = TenantOp.view(booking)
            book_list.append(book_item)

        return Response(render_template('view_bookings.html',bills=book_list,name=current_user.name))

class ViewTenantDetail(Resource):
    @login_required
    def get(self):
        pass

    def post(self):
        tenant_bills = []
        detailed_bills = []
        
        selected_apartment = request.form.get("apartment")
        print(">>>>>>>>>>>>>>>",selected_apartment)
        tenant_id = request.form.get("tenant")

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        # tenant_list_compare = []
        # alloc_objs = apartment_obj.tenants_allocated
        # for alloc in alloc_objs:
        #     tenant_item = alloc.tenant
        #     tenant_list_compare.append(tenant_item)

        # tenant_obj = None
        # for tenant in tenant_list_compare:
        #     if str(tenant) == tenant_name:
        #         tenant_obj = tenant
        tenant_obj = TenantOp.fetch_tenant_by_nat_id(tenant_id)
        tenant_name = tenant_obj.name

        bal = tenant_obj.balance
        balance = (f"{bal:,}")

        monthlybill_list = apartment_obj.monthlybills
        for bill in monthlybill_list:
            if bill.tenant == tenant_obj:
                tenant_bills.append(bill)

        for bill in tenant_bills:
            bill_item = MonthlyChargeOp.view_detail(bill)
            detailed_bills.append(bill_item)


        # tenants = TenantOp.fetch_all_tenants()
        # for tenant in tenants:
        #     tenant_item = TenantOp.view(tenant)
        #     tenant_list.append(tenant_item)

        # apartment_list = fetch_all_apartments_by_user(current_user)
        # return Response(render_template('view_tenant.html',bills=tenant_list,apartment_list=apartment_list,tenant=tenant,apartment_name=selected_apartment,name=current_user.name))
        return render_template('ajaxtenantreport.html',tenant=tenant_name,apartment_name=selected_apartment,bills=detailed_bills,balance=balance)

class ViewTenantDetailTwo(Resource):
    @login_required
    def get(self):
        pass
    @login_required
    def post(self):
        detailed_bills = []
        
        tenant_id = current_user.national_id

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(tenant_id)
        tenant_name = tenant_obj.name

        bal = tenant_obj.balance
        balance = (f"{bal:,}")

        tenant_bills = tenant_obj.monthly_charges

        for bill in tenant_bills:
            bill_item = MonthlyChargeOp.view_detail(bill)
            detailed_bills.append(bill_item)

        return render_template('ajaxtenantreporttwo.html',tenant=tenant_name,bills=detailed_bills,balance=balance)

class ViewTenantInfo(Resource):
    @login_required
    def get(self):
        pass

    def post(self):

        tenant_info = []
        
        selected_apartment = request.form.get("apartment")
        tenant_id = request.form.get("tenant")

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(tenant_id)
        tenant_name = tenant_obj.name

        bal = tenant_obj.balance
        balance = (f"{bal:,}")
        
        tenant_data = TenantOp.view(tenant_obj)
        tenant_info.append(tenant_data)
            
        return render_template('ajaxtenantinfo.html',tenant=tenant_name,bills=tenant_info,balance=balance)

class ViewTenancy(Resource):
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'view_tenancy.html',
            tenantlist=[],
            apartment_list=apartment_list,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        tenancy_list = []
        tenant_nat_ids = []
        tenant_balances = []
   
        selected_apartment = request.form.get("selected_apartment")
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        tenants = tenantauto(apartment_id)
        for tenant in tenants:
            tenant_id = tenant.national_id
            tenant_nat_ids.append(tenant_id)

            tenant_item = TenantOp.view(tenant)
            tenancy_list.append(tenant_item)

            tenant_balance = tenant.balance
            tenant_balances.append(tenant_balance)

        injection = recent_vacation_injector(apartment_id)
        inject_list = []
        for inject in injection:
            tenant_obj = inject.tenant
            inject_list.append(tenant_obj)

        for tenant in inject_list:
            tenant_id = tenant.national_id
            tenant_nat_ids.append(tenant_id)

        tenantids = remove_dups(tenant_nat_ids)

        balances = 0.0
        for bal in tenant_balances:
            if bal > 0.0:
                balances+=bal

        bal = (f"{balances:,}")
        

        # tenant_alloc_objs = apartment_obj.tenants_allocated
        # for tenant_alloc in tenant_alloc_objs:
        #     tenant_item = AllocateTenantOp.view(tenant_alloc)
        #     tenancy_list.append(tenant_item)
        #     tenant_name = tenant_alloc.tenant.name
        #     tenant_names.append(tenant_name)

        apartment_list = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'view_tenancy.html',
            tenantlist=tenantids,
            bills=tenancy_list,
            apartment_list=apartment_list,
            apartment_name=selected_apartment,
            name=current_user.name,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            balances=bal))

class ViewVacatedTenants(Resource):
    """tenant history"""
    @login_required
    def get(self):

        apartment_list = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'view_vacatedtenants.html',
            apartment_list=apartment_list,
            name=current_user.name,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            tenantlist=[]))

    def post(self):
        x_tenants = []

        tenant_balances = []
   
        selected_apartment = request.form.get("selected_apartment")
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        x_alloc_objs = tenantauto_reverse(apartment_id)

        for x_tenant in x_alloc_objs:
            obj = AllocateTenantOp.view(x_tenant)
            x_tenants.append(obj)

            tenant_balance = x_tenant.tenant.balance
            tenant_balances.append(tenant_balance)


        balances = 0.0
        for bal in tenant_balances:
            if bal > 0.0:
                balances+=bal

        bal = (f"{balances:,}")

        apartment_list = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'view_vacatedtenants.html',
            bills=x_tenants,
            apartment_list=apartment_list,
            apartment_name=selected_apartment,
            name=current_user.name,
            balances=bal,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            tenantlist=[]))


class ViewMonthlyPayments(Resource):
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'view_payments.html',
            apartment_list=apartment_list,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        detailed_payments_list = []
        tenant_monthly_payments = []
        
        selected_apartment = request.form.get("apartment")
        tenant_id = request.form.get("tenant")

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(tenant_id)
        tenant_name = tenant_obj.name

        bal = tenant_obj.balance
        balance = (f"{bal:,}")

        monthlypayments_list = apartment_obj.payment_data
        for pay in monthlypayments_list:
            if pay.tenant == tenant_obj:
                tenant_monthly_payments.append(pay)

        for pay in tenant_monthly_payments:
            pay_item = PaymentOp.view(pay)
            detailed_payments_list.append(pay_item)

        # apartment_list = fetch_all_apartments_by_user(current_user)

        return render_template('ajaxtenantpayreport.html',tenant=tenant_name,bills=detailed_payments_list,balance=balance)

        # return Response(render_template('view_payments.html',bills=payments_list,apartment_list=apartment_list,apartment_name=selected_apartment,name=current_user.name))
        

