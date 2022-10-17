# from app.v1.models import datamodel


# tnt9374


# from re import S
# import time
import os
import qrcode
# from unicodedata import category
from dateutil.parser import parse

import json
from openpyxl import load_workbook


import cloudinary as Cloud
# from sqlalchemy.sql.expression import except_
# from sqlalchemy import inspect
from werkzeug.utils import secure_filename

from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from flask_mail import Message
from flask_login import login_required, current_user
from flask_restful import Resource, abort
from flask import render_template,Response,request,flash,redirect,url_for
from dateutil.relativedelta import relativedelta
from sqlalchemy import exc
from app.v1.models.operations import *
from .helperfuncs import *
# from .secrets import *
from .advanta import *
from operator import add
from app import sms
from app import mail


# from rq import Queue
# from rq.job import Job
# from worker import conn
# q = Queue(connection=conn)

Cloud.config.update = ({
    'cloud_name':os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'api_key': os.environ.get('CLOUDINARY_API_KEY'),
    'api_secret': os.environ.get('CLOUDINARY_API_SECRET')
})


# urll = "https://api.whatso.net/api/v2/SendMessage"

# request = {
#     "Username": "60f30a6c321c412ba1b355a971f4056f",
#     "Password": "582fd28143eb44989a6f6f25091004f7",
#     "MessageText": "hvipi",
#     "MobileNumbers":"254716674695",
#     "ScheduleDate":"",
#     "FromNumber":"254716674695",
#     "Channel":"1"
# }

# try:
#     response = requests.post(urll, json=request)
# except:
#     response = requests.post(urll, json=request, verify=False)

# print(response.text)

# telll = sms_phone_number_formatter("0722801433")

# advanta_send_sms("Good morning Faith 🙂, \nWant some lunch today?",phonenuma,merit_api_key,merit_partner_id,"MERIT_LTD")

# advanta_send_sms("Greetings Michael 🙂, \nLymax sms sender Id is ready ~ KiotaPay Team",telll,kiotapay_api_key,kiotapay_partner_id,"LYMAXPROPER")

# report = advanta_send_sms("sms_text",phonenuma,kiotapay_api_key,kiotapay_partner_id,"Bizline")

# afrinet_send_sms("Good morning Peter \nWe have completed Kiotapay sms integration. \n\nSent from KiotaPay servers",telll,"045abd0ed75b563eb186b2a61d686a83",321,"GREATWALL")

class MonitorActivity(Resource):
    def get(self):
        target = request.args.get("target")
        datevar = request.args.get("date")

        if not datevar:
            obj_date = datetime.datetime.now()
            datevar = obj_date.strftime("%d %B, %Y")

        else:
            raw_date = date_formatter_weekday(datevar)
            from dateutil.parser import parse
            obj_date = parse(raw_date)



        if target == "smslogins":
            logsjob = q.enqueue_call(
                func=sendlogs, args=(obj_date,), result_ttl=5000
            )

        elif target == "daylogins":
            all_logins = UserLoginDataOp.fetch_logins_by_day(obj_date)
            logs = login_details(all_logins)
            # payids = get_obj_ids(detailed_payments_list)
            logins = f"{len(all_logins)} logins"
            return render_template("ajax_logs.html",items=logs,targetdate=datevar,logins=logins)

        elif target == "monthlogins":
            all_logins = UserLoginDataOp.fetch_logins_by_month(obj_date)
            logs = login_details(all_logins)
            # payids = get_obj_ids(detailed_payments_list)
            logins = f"{len(all_logins)} logins"
            return render_template("ajax_logs.html",items=logs,targetdate=datevar,logins=logins)


        else:
            time = datetime.datetime.now()
            return Response(render_template(
                'monitor_activity.html',
                logins = len(UserLoginDataOp.fetch_logins_by_day(time))
            ))

class Index(Resource):
    """class"""
    @login_required
    def get(self):

        coss = CompanyOp.fetch_all_companies()
        for t in coss:
            if t.name == "Litala" or t.name == "REVER MWIMUTO LIMITED" or t.name == "DEMO COMPANY 2":
                CompanyOp.update_ctype(t,"crm")
            else:
                CompanyOp.update_ctype(t,"noncrm")


        print(len(coss)," companies found")

        # job8 = q.enqueue_call(
        #     func=send_out_single_email_crm_invoice, args=(3504,), result_ttl=5000
        # )

        # if current_user.company.name == "Litala":
        #     CompanyOp.update_ctype(current_user.company,"crm")


        # CompanyOp.update_ctype(current_user.company,"crm")


        # ccm = ApartmentOp.fetch_apartment_by_id(584)
        # hq = ccm.houses
        # for h in hq:
        #     HouseOp.update_details(h,"","One Bedroom")

        # lfile("ready to start background job with lfile....")
        # print("ready to start background job with print....")

        # jobjob = q.enqueue_call(
        #         func=show_me, args=("changed it",current_user.id,), result_ttl=5000
        #     )

        # tnt_url = "https://kiotapay.com/query/tnt534"

        # imgg = qrcode.make(tnt_url)
        # imgg.save("greatwallqr.png")

        # todel = ApartmentOp.fetch_apartment_by_id(490)
        # if todel:
        #     ApartmentOp.delete(todel)
        
        # for cos in coss:
        #     print(cos.name)
        #     # for x in cos.groups:
        #     #     rights = AssignGroupRoleOp.fetch_assigned_roles_by_usergroup_id(x.id)
        #     #     for right in rights:
        #     #         AssignGroupRoleOp.delete(right)
        #     #     if x.users:
        #     #         pass
        #     #     else:
        #     #         CompanyUserGroupOp.delete(x)

        #     groups = ["Director","Manager","Accounts","Agent","Sales","Field","Owner"]
        #     for group in groups:
        #         if group in [str(x) for x in cos.groups]:
        #             continue
        #         group_obj = CompanyUserGroupOp(group,"",cos.id)
        #         group_obj.save()

        # unitts = ["A13","C11","E13"]

        # for unit in unitts:


        #     qws = ApartmentOp.fetch_apartment_by_id(23)
        #     hs = get_specific_house_obj(qws.id,unit)
        #     # if qws:
        #     #     ApartmentOp.update_loan_bank_details(qws,0.0)

        #     if qws and localenv:
        #         all_ptenants = hs.owner
        #         bookedon = "proposal"
        #         PermanentTenantOp.update_status(all_ptenants,bookedon)

                # MeterOp.update_decitype(i,decitype)

        # from rq import cancel_job
        # cancel_job('3771ae2a-e121-4834-af5a-1c61e04b5b08')

        # try:
        #     print("ndiooooo hiiiiii",CtoBop.fetch_record_by_id(171).trans_amnt)
        # except Exception as e:
        #     print("trans amnt is failing",e)

        # appss = ApartmentOp.fetch_all_apartments()
        # for qqq in appss:
        #     print("updating",qqq, "currently",qqq.reminder_status)
        #     ApartmentOp.update_reminder_status(qqq,"pending")
        #     print("Update complete",qqq, "now",qqq.reminder_status)

        # jendi = ApartmentOp.fetch_apartment_by_name("Vintage Phase I")

        # billing_period = jendi.billing_period

        # charges = jendi.charges

        # for charge in charges:
        #     if str(charge) == "Water" and charge.date.month == billing_period.month and charge.date.year == billing_period.year and charge.reading_id:
        #         ChargeOp.delete(charge)

        time = datetime.datetime.now() + relativedelta(hours=3)

        # gdsfg = CtoBop.fetch_record_by_mode("Bank")
        # if gdsfg:
        #     print(">>>>>>>>>>>>>>>>>>>",gdsfg)
        # else:
        #     print("<<<<<<<<<<<<<<<<<< NOT FOUND")

        # allhses = HouseOp.fetch_houses()
        # for i in allhses:
        #     if not i.housecode:
        #         print("HOUSE >>",i,"PROP >>",i.apartment,"Company >>",i.apartment.company)
        #         HouseOp.delete(i)

        # pts = PermanentTenantOp.fetch_all_tenants()
        # for pt in pts:
        #     if not pt.tenant_type:
        #         print("UPDATING OWNER",pt.name)
        #         PermanentTenantOp.update_tenant_type(pt,"owner")
        #     else:
        #         print(pt.name ,"OF",pt.apartment.name,"UPDATED ALREADY")

        # co = current_user.company
        # if co.name == "Vintage Residence Limited":
        #     if co.receipt_num:
        #         pass
        #     else:
        #         CompanyOp.increment_receipt_num(co,565)

        # cooo = CompanyOp.fetch_company_by_id(16)
        # if cooo:
        #     print("ccccccccccccccoooooo",cooo.name)
        #     CompanyOp.delete(cooo)

        # ctob_obj = CtoBop("MQCKMSCNS",time,50.0,"trans_type","400400","C5","invoice_num","0716674695",786.0,"Peter","Koech")
        # ctob_obj.save()

        #### WORST PRODUCTION DB INCIDENT ##############

        # propp = ApartmentOp.fetch_apartment_by_id(35)
        # if propp:
        #     ApartmentOp.delete(propp)

        ################################################

        # propp = ApartmentOp.fetch_apartment_by_id(37)
        # if propp:
        #     cs = propp.housecodes
        #     for c in cs:
        #         HouseCodeOp.update_sewerage_rate(c,112.5)

        # propp = ApartmentOp.fetch_apartment_by_id(132)
        # if propp:
        #     cs = propp.meter_readings
        #     pp = generate_date(6,2022)
        #     for c in cs:
        #         MeterReadingOp.update_reading_period(c,pp)

        # allhses = HouseOp.fetch_houses()
        # for cs in allhses:
        #     if not cs.housecode:
        #         prop = cs.apartment
        #         codded = get_specific_code_obj(prop.id,"DEFAULT")
        #         if not codded:
        #             codded = HouseCodeOp("DEFAULT",0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,prop.id,1)
        #             codded.save()
        #         HouseOp.update_housecode_id(cs,codded.id)

        # if current_user.company.name == "Latitude Properties":
        #     if current_user.username.startswith('qc'):
        #         pass
        #     else:
        #         send_internal_email_notifications(current_user.name," is trying to login")

        #         return Response(render_template("under_maintenance.html"))

        # if current_user.username.startswith('qc') or current_user.usercode =="3551" or current_user.username.startswith('quality'):
        if current_user.username == "kiotapay" or localenv:
            print("getting in")
            # cocc = CompanyOp.fetch_company_by_name("")
            # if cocc:
            #     CompanyOp.update_sms_provider(cocc,"Advanta")

            # commp = CompanyOp.fetch_company_by_name("Lesama Ltd")
            # commp = CompanyOp.fetch_company_by_name("Sentom Investment")

            # cms = CompanyOp.fetch_all_companies()

            # for ccs in cms:
            #     propsss = ccs.props
            #     for propp in propsss:

            #         apartment_id = propp.id

            #         print("APART",apartment_id)

            #         # billupdatejob = q.enqueue_call(
            #         #     func=run_update, args=("dict_array",apartment_id,current_user.id,), result_ttl=5000
            #         # )


            # if not cocc:
            #     cocc = current_user.company

            # props = cocc.props

            # for prop in props:

            #     hscodes = prop.housecodes
            #     for code in hscodes:
            #         HouseCodeOp.update_vatrates(code,3,0)

            # prop = ApartmentOp.fetch_apartment_by_id(280)
            # if prop:
            #     hs = prop.housecodes
            #     for h in hs:
            #         HouseCodeOp.update_waterrate_scale(h,330,65,90)

            # uss = UserOp.fetch_user_by_national_id("24142460")
            # UserOp.update_status(uss,False)

            # run_scripts(current_user)
            # run_company_data()

            print("TIME NOW IN US: ", (time + relativedelta(hours=0)).strftime("%X"))

        present_day = time.day
        weekday = time.weekday()

        update_login_history("general",current_user)

        if current_user.company and current_user.user_id != 1:
            present_month = current_user.company.billing_period.month
            present_year = current_user.company.billing_period.year
        else:
            present_month = time.month
            present_year = time.year

        apartment_list = fetch_all_apartments_by_user(current_user)

        try:
            reminder = current_user.company.template
        except:
            reminder = ""

        if reminder:
            setreminder = f'{reminder[0].txt}'
        else:
            setreminder = ""
            

        unread_messages = []
        prop_ids = []

        for prop in apartment_list:
            prop_ids.append(prop.id)

        apartment_list.append("All properties")

        usergroup = current_user.user_group
        user_group = str(usergroup)

        if user_group == "Tenant":
            #tenant user is connected to tenant obj by national id
            tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)

            resp = check_house_occupied(tenant_obj)
            if resp[0] == "Resident":
                myhouse = resp[1]
                apartment_obj = resp[1].apartment
                apartmentname = resp[1].apartment.name
            else:
                myhouse = ""
                apartmentname = "Non - resident"
                apartment_obj = None

            bills = fetch_current_month_bill(tenant_obj)
            payments = fetch_current_month_payments(tenant_obj)
            my_balance = tenant_obj.balance

            my_requests = []
            myrequests = fetch_active_requests(tenant_obj)
            for r in myrequests:
                obj = TenantRequestOp.view(r)
                my_requests.append(obj)

            req_id_list = []
            for req in my_requests:
                req_id = req["id"]
                req_id_list.append(req_id)

            mybills = (f"{bills:,}")
            mypayments = (f"{payments:,}")
            mybal = (f"{my_balance:,}")
            try:
                vacant_houses = filter_out_occupied_houses(apartment_obj.name)
            except:
                vacant_houses = []
            apartment_users = ApartmentOp.fetch_apartment_by_id(tenant_obj.apartment_id).users
            for user in apartment_users:
                if user.user_group == "Agent":
                    agenttel = user.phone
                else:
                    agenttel = ApartmentOp.fetch_apartment_by_id(tenant_obj.apartment_id).owner.phone

                if user.user_group == "Caretaker":
                    caretakertel = user.phone
                else:
                    caretakertel = ApartmentOp.fetch_apartment_by_id(tenant_obj.apartment_id).owner.phone

            return Response(render_template(
                'tenantindex.html',
                propertyname = apartmentname,
                tenantname = fname_extracter(current_user.name),
                house = myhouse,
                vacants = vacant_houses,
                monthly_bills = mybills,
                chartstring="",
                currentmonthpay=mypayments,
                my_balance=mybal,
                bills=my_requests,
                requestids=req_id_list,
                agenttel_url = phone_number_formatter_url(agenttel),
                caretakertel_url = phone_number_formatter_url(caretakertel),
                agenttel = agenttel,
                caretakertel = caretakertel,
                group=get_group_name(current_user.user_group_id),
                name=current_user.name
            ))


        elif user_group in ["Owner","Agent","User"]:
            """owners, agents and normal users"""
            if current_user.active == False:
                return Response(render_template("inactive_account.html"))

            unread_length = len(unread_messages)
            if unread_length == 0:
                unread_num = ""
            else:
                unread_num = unread_length

            company = current_user.company

            print("SMS PROVIDER:",company.sms_provider)
      
            if time.month == company.quotamonth:
                # CompanyOp.set_smsquota(company,300)
                # CompanyOp.set_rem_quota(company,company.smsquota)
                # CompanyOp.set_quota_month(company,time.month)

                # if company.name == "Thara Agency": #RESET SMS HERE FOR SPECIFIC COMPANY
                #     CompanyOp.set_rem_quota(company,100)
                pass
            else:
                # CompanyOp.set_rem_quota(company,company.smsquota)
                # CompanyOp.set_quota_month(company,time.month)
                pass

            if current_user.company.name == "Lesama Ltd":
                sms_units = advanta_sms_balance(lesama_api_key,lesama_partner_id)
                smsfrac = f"{sms_units} units"
                color = "text-success"

            elif current_user.company.name.title() == "Merit Properties Limited":
                sms_units = advanta_sms_balance(merit_api_key,merit_partner_id)
                smsfrac = f"{sms_units} units"
                color = "text-success"

            elif current_user.company.name.title() == "Denvic Property Managers":
                sms_units = afrinet_sms_balance(greatwall_api_key,greatwall_partner_id)
                smsfrac = f"{sms_units} units"
                color = "text-success"

                # elif current_user.company.name == "KEVMA REAL ESTATE":
                #     sms_units = advanta_sms_balance(kiotapay_api_key,kiotapay_partner_id)

                #     raw_smsunits = sms_units.replace(",","")
                #     int_units = int(raw_smsunits)
                #     CompanyOp.set_rem_quota(company,int_units)

                #     smsfrac = f"{sms_units} units"
                #     color = "text-success"

                # elif current_user.company.name.title() == "Latitude Properties":
                #     sms_units = advanta_sms_balance(kiotapay_api_key,kiotapay_partner_id)

                #     raw_smsunits = sms_units.replace(",","")
                #     int_units = int(raw_smsunits)
                #     CompanyOp.set_rem_quota(company,int_units)

                #     smsfrac = f"{sms_units} units"
                #     color = "text-success"

            else:
                remainingsms = company.remainingsms
                smsquota = company.smsquota
                if remainingsms < 0.2 * smsquota:
                    color = "text-danger"
                else:
                    color = "text-success"
                smsfrac = f"{remainingsms} units"

            # # display own sms balance:
            # if localenv:
            #     print("REMAINING SMS",advanta_sms_balance(kiotapay_api_key,kiotapay_partner_id))

                
            # if current_user.username.startswith('qc'):
            #     CompanyOp.set_rem_quota(company,916)

            propids = ','.join(map(str, prop_ids))

            if current_user.company.name == 'Rowam Properties Limited':
                logobg = "rowam-color"
            else:
                logobg = "bg-white"

            if current_user.company.name == 'Lesama Ltd':
                logobg = "lesama-color"
            else:
                logobg = "bg-white"
                # logobg = "bg-white"
            try:
                companyname = company.name.split(" ")[0].title() if len(company.name) > 15 else company.name
            except:
                txt = "COMPANY NAME IS FAILING"
                send_internal_email_notifications(current_user.company.name,txt)
                companyname = "Company"

            companyname2 = company.name.split(" ")[0]

            if company.name == "Lesama Ltd":
                shortcode2 = "Paybill: 969610 Acc: LesamaKe"
            else:
                if os.getenv("TARGET") == "lasshouse":
                    shortcode2 = f"Paybill: 000XXX Acc: {companyname2}#{company.id}"
                else:
                    shortcode2= f"Paybill: 4081687 Acc: {companyname2}#{company.id}"

            if crm(current_user):
                indexpage = "agentindex3.html"
            else:
                indexpage = os.getenv("INDEX") or INDEX


            ############################################################################################################
            coco = CompanyOp.fetch_company_by_name("Sentom Investment")
            if coco:
                userr = UserOp.fetch_user_by_usercode("00001")
                if not userr:
                    user_group_id = get_company_usergroup_id("Accounts",coco)
                    new_user = UserOp("name","00001","qcsentom1","00001109","","","qc00",4,user_group_id,coco.id,1)
                    new_user.save()

                    company_properties = coco.props
                    for prop in company_properties:
                        UserOp.relate(new_user,prop)
            #############################################################################################################

            ref = "QDR61YG8J8"
            # paymentt = PaymentOp.fetch_payment_by_ref(ref)
            # if paymentt:
            #     print("payment found for ref", ref)
            # else:
            #     print("payment not found for", ref)
            cbt = CtoBop.fetch_record_by_ref(ref)
            if cbt:
                print("cbt found for ref", ref)
                CtoBop.delete(cbt)
            else:
                print("cbt not found for", ref)

            # if company.name == "Latitude Propertiess":
            #     props = company.props
            #     for prop in props:
            #         payss = prop.payment_data
            #         for p in payss:

            #             trans = p.ref_number
            #             if trans == "N/A" or trans == "na" or trans == "NA":
            #                 print("passing transaction")
            #             else:
            #                 s = re.sub(r'[^a-zA-Z0-9]', '', trans)
            #                 PaymentOp.update_ref(p,s)

            #     shortcodes = company.shortcodes

            #     for shortcode in shortcodes:
            #         raw_unclaimed = CtoBop.fetch_all_records_by_shortcode(shortcode.shortcode)
            #         for i in raw_unclaimed:
            #             print(">>>cbid",i.trans_id,"STATUS",i.status)

            #             payyyy = PaymentOp.fetch_payment_by_ref(i.trans_id)
            #             if payyyy:
            #                 print("Resolving ", i.trans_id," and ",payyyy.amount,"payref ",payyyy.ref_number)
            #                 CtoBop.update_status(i,"claimed")
            #                 continue
            #             else:
            #                 print("cbid did not find its sibling payment")

            if company.name== "ASTROL":
                shorts = ["4091383"]
            else:
                shorts = []

            for short in shorts:
                cbid = ShortcodeOp.fetch_shortcode_by_id(short)
                if not cbid:
                    cbid = ShortcodeOp(short,"",company.id)
                    cbid.save()

            if company.name == "Latitude Properties":
                shortcodes = []
                banksdata = []
            else:
                shortcodes = company.shortcodes
                banksdata = company.cbids

            sifted = []
            for shortcode in shortcodes:
                if shortcode.shortcode == "4012401" or shortcode.shortcode == "4081687":
                    continue
                raw_unclaimed = CtoBop.fetch_all_records_by_shortcode(shortcode.shortcode)

                for r in raw_unclaimed:
                    # targets = ["532406","964399","4012401","4081687"]
                    if r.status == "unclaimed":
                        sifted.append(r)

            for r in banksdata:
                    if r.status == "unclaimed" and r.mode == "Bank":
                        sifted.append(r)

            cbids = ctb_payment_details(sifted)
            cbids_num = len(cbids)

            # apart1 = ApartmentOp.fetch_apartment_by_name("Aviv")
            # if not apart1.paymentdetails:
            #     print("noooooonnnoonooo",apart1.paymentdetails)
            #     p = PaymentDetailOp("mpesapay","tntnum","345345","","","","","",apart1.id)
            #     p.save()
            # else:
            #     print("herereeeeeeeeeeeeee",apart1.paymentdetails)

            # apart2 = ApartmentOp.fetch_apartment_by_name("La Casa Apartments")
            # if not apart2.paymentdetails:
            #     p = PaymentDetailOp("mpesa","203027","","","","","",apart1.id)
            #     p.save()

            # apart3 = ApartmentOp.fetch_apartment_by_name("Neema Homes")
            # if not apart3.paymentdetails:
            #     p = PaymentDetailOp("mpesa","602666","","","","","",apart1.id)
            #     p.save()

            # apart4 = ApartmentOp.fetch_apartment_by_name("The Container")
            # if not apart4.paymentdetails:
            #     p = PaymentDetailOp("mpesa","7555555","","","","","",apart1.id)
            #     p.save()

            secret_struct = os.getenv("SECRETNAME")
            if not secret_struct:
                secret_struct = SECRETNAME

            secret_num = os.getenv("SECRETNUM")
            if not secret_num:
                secret_num = SECRETNUM

            if current_user.company.name == secret_struct and current_user.username != secret_num:
                return Response(render_template("inactive_company.html"))


            return Response(render_template(
                indexpage,
                clientaccess = "access",
                sidebar_theme = "premier-sidebar-theme" if str(company) == "Premier Realty" else "sidebar-bg",
                topbar_theme = "bg-white" if str(company) == "Premier Realty" else "bg-white",
                card_theme = "premier-card-theme" if str(company) == "Premier Realty" else "card-bg",
                co=company,
                companyname = companyname,
                cbids=cbids,
                shortcodes=company.shortcodes,
                cbids_num=cbids_num,
                logobg=logobg,
                numsms=smsfrac,
                shortcode = shortcode2,
                smshighlight=color,
                username = fname_extracter(current_user.name),
                unread_num = unread_num,
                unread_msgs = unread_messages,
                setreminder=setreminder,
                chartstring="",
                current_year=present_year,
                month_string=get_str_month(present_month),
                month_string_alt=get_str_month(time.month),
                weekday = get_str_weekday(weekday),
                current_day=present_day,
                billingperiod = company.billing_period.strftime("%B/%Y"),
                billingmonth = get_str_month(company.billing_period.month),
                previousbillingmonth = get_str_month(get_next_month(company.billing_period.month)),
                props=apartment_list,
                propids=propids,
                group=current_user.company_user_group.name,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name,
                user_initials = get_initials(current_user.name),
                code=current_user.usercode
            ))

        else:
            unread_messages = TextMessagesOp.fetch_unread_messages()
            unread_length = len(unread_messages)
            if unread_length == 0:
                unread_num = ""
            else:
                unread_num = unread_length
                try:
                    with mail.connect() as conn:
                        print ("Mail connection successful, sending mails")
                        for item in unread_messages:
                            try:
                                txt = Message('KiotaPay, Client Messages', sender = 'info@kiotapay.com', recipients = ["koechpetersn@gmail.com"])
                                txt.body = f"{item.txt} \nSender details; Name: {item.name}, Email: {item.email}"
                                conn.send(txt)
                                TextMessagesOp.update_status(item,"read")
                            except Exception as e:
                                print(str(e))
                except:
                    print("no net")
                    for item in unread_messages:
                        TextMessagesOp.update_status(item,"read")

            return Response(render_template(
                'adminindex.html',
                username = "Admin",
                unread_num = unread_num,
                unread_msgs = unread_messages,
                chartstring="",
                group=current_user.company_user_group.name,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name
            ))

class PropData(Resource):
    @login_required
    def get(self):      

        prop_ids = []

        props = fetch_all_apartments_by_user(current_user)

        prop_ids = [prop.id for prop in props]
   
        propids = ','.join(map(str, prop_ids))

        return Response(render_template(
            'ajax_load_propdata.html',
            propids=propids
        ))

class FetchSentSms(Resource):
    @login_required
    def get(self):
        company = current_user.company
        sent_texts = company.sent_messages
        target_texts = []
        items = []
        for m in sent_texts:
            if m.date.month == company.billing_period.month and m.date.year == company.billing_period.year:
                target_texts.append(m)

        for t in target_texts:
            items.append(SentMessagesOp.view(t))

        return render_template("ajax_sent_messages.html",items=items)

class PropSearchData(Resource):
    @login_required
    def get(self):      

        raw_tenancy =[]
        raw_units=[]

        props = fetch_all_apartments_by_user(current_user)

        raw_tenancy = [tenantauto(prop.id) for prop in props]
        raw_units = [prop.houses for prop in props]
        raw_residents = [prop.ptenants for prop in props]
   
        ############################################################
        tenancy = flatten(raw_tenancy)
        residents = flatten(raw_residents)
        houses = flatten(raw_units)


        suggestions = generate_suggestions_alt(props,houses,tenancy,residents)  
        return Response(render_template(
            'ajax_load_searchdata.html',
            suggestions=suggestions
        ))

class ComStats(Resource):
    @login_required
    def get(self):
        
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


        usergroup = current_user.user_group
        user_group = str(usergroup)

        if user_group != "Admin":
            pass

        else:
            dashboard_coms.append("All clients")       
            
            return Response(render_template(
                'ajax_dashboard_refresh_alt.html',
                month_string=get_str_mnth(present_month),
                monthly_bills = formatted_monthly_bill_total,
                monthly_rent_collection=formatted_monthly_total,
                monthly_bal=formatted_monthlybal_total,
                comonfocus=comonfocus,
                clients = dashboard_coms,
            ))

class ComGraphStats(Resource):
    @login_required
    def get(self):

        com = request.args.get('com')

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
            
        return Response(render_template(
            'ajax_load_graph_data_alt.html',
            chartstring=chart_string,
            clients = len(clients),
            active_clients = len(active_clients),
            registered_users = users,
            props = len(flatten(props)),
            houses = len(flatten(houses)),
            tenants = len(flatten(tenants)),
            active_tenants = len(flatten(active_tenants)),
            smsestimate = len(flatten(active_tenants))*3,
            smssent = sms_spent,
            actualcosts = f"Kshs {actual_cost:,.1f}"
        ))



class PropStats(Resource):
    @login_required
    def get(self):

        prop = request.args.get('prop')

        time = datetime.datetime.now()
       
        if current_user.company and current_user.id != 1:
            period = current_user.company.billing_period
            present_month = current_user.company.billing_period.month
            present_year = current_user.company.billing_period.year
        else:
            present_month = time.month
            present_year = time.year
            period = time
            
        if not present_month: # remove this check on april 2021
            present_month = time.month
        if not present_year:
            present_year = time.year
            
        total_collections = 0
        real_collections = 0
        total_balances = 0
        total_bills = 0
        defaulters = 0
        invs = 0

        apartment_list = fetch_all_apartments_by_user(current_user)

        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)

        props = []

        if prop == "All properties":
            proponfocus = "All properties"
            props = apartment_list
        elif prop_obj:
            if prop_obj in apartment_list:
                proponfocus = fname_extracter(str(prop_obj))
                props.append(prop_obj)
            else:
                try:
                    proponfocus = fname_extracter(str(apartment_list[0]))
                    props.append(apartment_list[0])
                except:
                    proponfocus = None
        else:
            try:
                proponfocus = fname_extracter(str(apartment_list[0]))
                props.append(apartment_list[0])
            except:
                proponfocus = "None"

        dashboard_props = []

        for i in apartment_list:
            dashboard_props.append(i.name)

        occupancy = [filter_in_occupied_houses(prop.name) for prop in props]

        unpacked_occupancy = flatten(occupancy)

        num_of_occ = len(unpacked_occupancy)

        for apartment in props:

            monthly_bills = apartment.monthlybills
            for item in monthly_bills:
                if item.month == present_month and item.year == present_year:
                    invs += 1
                    # boolie = False
                    # if not boolie:
                    # if not item.updated:
                    #     MonthlyChargeOp.update_balances(item,item.rent,item.water,item.electricity,item.garbage,item.security,item.maintenance,item.penalty,item.deposit,item.agreement)

                    # total_bills += item.total_bill if item.total_bill > 0 else 0
                    total_bills += item.total_bill
                    total_balances += item.balance if item.balance > 0 else 0

                    if not item.paid_amount:
                        defaulters += 1 if item.balance > 1 else 0

                    total_collections += item.paid_amount if item.paid_amount > 0 else 0

                    if item.balance > -0.99999:
                        real_collections += item.paid_amount if item.paid_amount > 0 else 0
                    else:
                        real_collections += item.total_bill if item.total_bill > 0 else 0

                    

            # payment_collection = apartment.payment_data
            # for item in payment_collection:
            #     if item.pay_period.month == present_month and item.pay_period.year == present_year and not item.voided:
            #         total_collections += item.amount if item.amount > 0 else 0
            #         if item.balance > -1:
            #             real_collections += item.amount if item.amount > 0 else 0
                            

        dashboard_props.append("All properties")

        try:

            collection_percentage = real_collections / total_bills * 100
        except:
            collection_percentage = 0

        if period.day > 5:
            # defaulters will not be overwritten
            pass
        else:
            defaulters = "--"

        invss = f"{invs}/{num_of_occ}"
            
        return Response(render_template(
            'ajax_dashboard_refresh.html',
            card_theme = "premier-card-theme" if str(current_user.company) == "Premier Realty" else "card-bg",
            month_string=get_str_month(present_month),
            month_str=get_str_mnth(present_month),
            collection_percentage = f"{collection_percentage:,.0f}",
            total_collections=(f"{total_collections:,.1f}"),
            total_balances=(f"{total_balances:,.1f}"),
            total_bills = (f"{total_bills:,.1f}"),
            numdefaulters = defaulters,
            numinvs = invss,
            proponfocus=proponfocus,
            props = dashboard_props,
        ))

class HouseStats(Resource):
    @login_required
    def get(self):
        prop = request.args.get('prop')
    
        occupancy=[]
        houses_list=[]

        apartment_list = fetch_all_apartments_by_user(current_user)

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
        ###############################################################################


        occupancy = [filter_in_occupied_houses(prop.name) for prop in props]
        houses_list = [prop.houses for prop in props]


        ############################################################

        unpacked_house_list = flatten(houses_list)
        houses_num = len(unpacked_house_list)

        unpacked_occupancy = flatten(occupancy)
        occupancy_num = len(unpacked_occupancy)
        
        try:
            occfrac = occupancy_num/houses_num 
        except:
            occfrac = 0.0

        if houses_num:
            vacfrac = 1 - occfrac
        else:
            vacfrac = 0.0

        occupancy_rate = f'{(occfrac * 100):,.0f} %'
        vacancy_rate = f'{(vacfrac * 100):,.0f} %'     
            
        return Response(render_template(
            'ajax_load_house_data.html',
            targetprop = prop,
            occupancy_rate = occupancy_rate,
            vacancy_rate = vacancy_rate,
            numhouse = houses_num,
            numalloc = occupancy_num,
            numvac = houses_num - occupancy_num
        ))

class GraphStats(Resource):
    @login_required
    def get(self):
        prop = request.args.get('prop')
        time = datetime.datetime.now()
       
        if current_user.company and current_user.id != 1:
            present_month = current_user.company.billing_period.month
            present_year = current_user.company.billing_period.year
        else:
            present_month = time.month
            present_year = time.year
            
        if not present_month: # remove this check on april 2021
            present_month = time.month
        if not present_year:
            present_year = time.year
        

        apartment_list = fetch_all_apartments_by_user(current_user)


        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)

        props = []

        if prop == "All properties":
            props = apartment_list
        elif prop_obj:
            if prop_obj in apartment_list:
                props.append(prop_obj)
            else:
                try:
                    props.append(apartment_list[0])
                except:
                    pass
        else:
            try:
                props.append(apartment_list[0])
            except:
                pass
        ###############################################################################

        collections_per_apartment = []
        bills_per_apartment = []
        units_per_apartment = []

        commission_per_apartment = []

        present_month_income = 0.0

        for apartment in props:
            db.session.expire(apartment)

            # prop_messages = []
            # for msg in prop_messages:
            #     if msg.status == "pending":
            #         unread_messages.append(msg)


            ##########################################
            annual_month_collections=[] #list of monthlycollections combined totals
            annual_month_bills=[] #list of monthlycollections combined totals
            annual_month_units=[] #list of monthlycollections combined totals

            annual_month_commissions = []


            range_arg = present_month +1 
            months = [*range(1, range_arg, 1)]
            

            for month in months:
                that_month_total = 0
                that_month_totalbill = 0
                that_month_totalunits = 0

                that_month_commissionable = 0

                monthly_collection_data = [] #list of amounts of a particular month
                monthly_bill_data = [] #list of amounts of a particular month
                monthly_reading_data = [] #list of amounts of a particular month


                for item in apartment.payment_data:
                    if item.pay_period.month == month and item.pay_period.year == present_year and not item.voided:
                        sum_member = item.amount
                        monthly_collection_data.append(sum_member)

                for item in apartment.monthlybills:
                    if item.month == month and item.year == present_year:
                        sum_member = item.total_bill
                        rentpaid = item.rent_paid if item.rent_paid else 0.0
                        monthly_bill_data.append(sum_member)
                        that_month_commissionable += rentpaid

                for item in apartment.meter_readings:
                    if item.reading_period:
                        if item.reading_period.month == month and item.reading_period.year == present_year:
                            sum_member = item.units
                            monthly_reading_data.append(sum_member)
                    
                for member in monthly_collection_data:
                    that_month_total += member

                for member in monthly_bill_data:
                    that_month_totalbill += member

                for member in monthly_reading_data:
                    that_month_totalunits += member

                if apartment.commission:
                    commission = that_month_commissionable * apartment.commission * 0.01
                    commission_percentage = f"({apartment.commission} %)"

                else:
                    commission = apartment.int_commission if apartment.int_commission else 0.0
                    commission_percentage = f"{commission} flat rate"

                if month == present_month:
                    present_month_income += commission

                annual_month_commissions.append(commission)

                annual_month_collections.append(that_month_total)
                annual_month_bills.append(that_month_totalbill)
                annual_month_units.append(that_month_totalunits)
            
            collections_per_apartment.append(annual_month_collections) #list of lists
            bills_per_apartment.append(annual_month_bills) #list of lists
            units_per_apartment.append(annual_month_units) #list of lists

            commission_per_apartment.append(annual_month_commissions)

                
        collectiondatalist = [sum(elts) for elts in zip(*collections_per_apartment)]
        billdatalist = [sum(elts) for elts in zip(*bills_per_apartment)]
        unitdatalist = [sum(elts) for elts in zip(*units_per_apartment)]

        commissiondatalist = [sum(elts) for elts in zip(*commission_per_apartment)]


        ############################################################
       
    
        collection_string = ','.join(map(str, collectiondatalist))
        bill_string = ','.join(map(str, billdatalist))
        water_string = ','.join(map(str, unitdatalist))
        commission_string = ','.join(map(str,commissiondatalist))

        if crm(current_user):
            template = 'ajax_load_graph_data3.html'
        else:
            template = 'ajax_load_graph_data.html'
      
            
        return Response(render_template(
            template,
            targetprop = prop,
            collectionstring=collection_string,
            billstring=bill_string,
            waterstring=water_string,
            incomestring=commission_string,
            outcomestring = 0,
            netcomestring=commission_string,
            income = f'{present_month_income} ({get_str_month(present_month)}',
            outcome = f'0.0 ({get_str_month(present_month)}',
            netcome = f'{present_month_income} ({get_str_month(present_month)}'
        ))


class Dashboard(Resource):
    @login_required
    def get(self):

        prop = request.args.get('prop')
        target = request.args.get('target')

        if target == "proponfocus":
            return prop

        props = run_props(prop,current_user)
        period = current_user.company.billing_period

        if target == "expectedstats":


            total_bills = 0
            invs = 0

            for apartment in props:

                monthly_bills = apartment.monthlybills
                for item in monthly_bills:
                    if item.month == period.month and item.year == period.year:
                        invs += 1
                        # total_bills += item.total_bill if item.total_bill > 0 else 0
                        total_bills += item.total_bill


            month_str=f'{get_str_mnth(period.month)} invoices'

            if current_user.username.startswith("qc") and current_user.company.name == "KEVMA REAL ESTATE":
                total_bills = 3629379.0
                invs = "170"

            return [f'Kes {total_bills:,.1f}',invs,month_str]

        if target == "collectionstats":

            period = current_user.company.billing_period

            total_bills = 0
            total_collections = 0


            props = run_props(prop,current_user)

            for apartment in props:

                monthly_bills = apartment.monthlybills
                for item in monthly_bills:
                    if item.month == period.month and item.year == period.year:
                        total_bills += item.total_bill if item.total_bill > 0 else 0
                        total_collections += item.paid_amount if item.paid_amount > 0 else 0

            try:
                ratio = total_collections / total_bills * 100
            except:
                ratio = 0

            if current_user.username.startswith("qc") and current_user.company.name == "KEVMA REAL ESTATE":
                total_collections = 17500.0
                ratio = 0.0


            return [f'Kes {total_collections:,.1f}',f'{ratio:,.0f} %']

        if target == "balancestats":

            period = current_user.company.billing_period

            total_balances = 0
            defaulters = 0

            props = run_props(prop,current_user)

            for apartment in props:

                monthly_bills = apartment.monthlybills
                for item in monthly_bills:
                    if item.month == period.month and item.year == period.year:
                        total_balances += item.balance if item.balance > 0 else 0

                        if not item.paid_amount:
                            defaulters += 1 if item.balance > 1 else 0

            if period.day < 6:
                defaulters = "--"
            else:
                pass

            if current_user.username.startswith("qc") and current_user.company.name == "KEVMA REAL ESTATE":
                total_balances = 3629379.0
                defaulters = "168"

            return [f'Kes {total_balances:,.1f}',f'{defaulters}']


        if target == "propstats":
            return len(props)

        if target == "housestats":
            return len(flatten([prop.houses for prop in props]))

        if target == "ptenantstats":
            return len(flatten([prop.ptenants for prop in props]))

        if target == "tenantstats":
            return len(flatten([filter_in_occupied_houses(prop.name) for prop in props]))

        if target == "vacantstats":
            return len(flatten([prop.houses for prop in props])) - len(flatten([filter_in_occupied_houses(prop.name) for prop in props]))
            # occupancy = [filter_out_occupied_houses(prop.name) for prop in props]
            
            # houses_list = [prop.houses for prop in props]

            # houses_num = len(flatten(houses_list))
            # occupancy_num = len(flatten(occupancy))
            
            # try:
            #     occfrac = occupancy_num/houses_num 
            # except:
            #     occfrac = 0.0

            # occupancy_rate = f'{(occfrac * 100):,.0f} %'

            # return  len(occupancy)

class PropOverview(Resource):
    @login_required
    def get(self):
        prop = request.args.get('prop')
        return len(run_props(prop,current_user))

class HouseOverview(Resource):
    @login_required
    def get(self):
        prop = request.args.get('prop')
        props = run_props(prop,current_user)
        return len(flatten([prop.houses for prop in props]))

class TenantOverview(Resource):
    @login_required
    def get(self):
        prop = request.args.get('prop')
        props = run_props(prop,current_user)

        numtnts = len(flatten([filter_in_occupied_houses(prop.name) for prop in props]))
        numptnts =len(flatten([prop.ptenants for prop in props]))

        return f'<span class="me-5">{numtnts}</span> <span class="ms-4">{numptnts}</span>'

            
class OccupancyOverview(Resource):
    @login_required
    def get(self):
        prop = request.args.get('prop')
        props = run_props(prop,current_user)
        occupancy = [filter_in_occupied_houses(prop.name) for prop in props]
        numptnts =len(flatten([prop.ptenants for prop in props]))
        houses_list = [prop.houses for prop in props]

        houses_num = len(flatten(houses_list))
        occupancy_num = len(flatten(occupancy))
        
        try:
            occfrac = occupancy_num/houses_num 
        except:
            occfrac = 0.0

        try:
            pfrac = numptnts/houses_num 
        except:
            pfrac = 0.0

        occupancy_rate = f'{(occfrac * 100):,.0f} %'
        print(numptnts,houses_num)
        p_rate = f'{(pfrac * 100):,.0f} %'

        # return  occupancy_rate
        return f'<span class="me-5">{occupancy_rate}</span> <span class="ms-4">{p_rate}</span>'


class InvoiceOverview(Resource):
    @login_required
    def get(self):

        prop = request.args.get('prop')

        period = current_user.company.billing_period

        total_bills = 0
        invs = 0

        props = run_props(prop,current_user)

        for apartment in props:

            monthly_bills = apartment.monthlybills
            for item in monthly_bills:
                if item.month == period.month and item.year == period.year:
                    invs += 1
                    total_bills += item.total_bill if item.total_bill > 0 else 0

        return f'Kes {total_bills:,.1f}'

class PaidOverview(Resource):
    @login_required
    def get(self):

        prop = request.args.get('prop')

        period = current_user.company.billing_period

        total_bills = 0

        props = run_props(prop,current_user)

        for apartment in props:

            monthly_bills = apartment.monthlybills
            for item in monthly_bills:
                if item.month == period.month and item.year == period.year:
                    total_bills += item.paid_amount if item.paid_amount > 0 else 0

        return f'Kes {total_bills:,.1f}'

class BalanceOverview(Resource):
    @login_required
    def get(self):

        prop = request.args.get('prop')

        period = current_user.company.billing_period

        total_bills = 0

        props = run_props(prop,current_user)

        for apartment in props:

            monthly_bills = apartment.monthlybills
            for item in monthly_bills:
                if item.month == period.month and item.year == period.year:
                    total_bills += item.balance if item.balance > 0 else 0

        return f'Kes {total_bills:,.1f}'

class CollectionOverview(Resource):
    @login_required
    def get(self):

        prop = request.args.get('prop')

        period = current_user.company.billing_period

        total_bills = 0
        real_collections = 0

        props = run_props(prop,current_user)

        for apartment in props:

            monthly_bills = apartment.monthlybills
            for item in monthly_bills:
                if item.month == period.month and item.year == period.year:

                    total_bills += item.total_bill if item.total_bill > 0 else 0

                    if item.balance > -0.99999:
                        real_collections += item.paid_amount if item.paid_amount > 0 else 0
                    else:
                        real_collections += item.total_bill if item.total_bill > 0 else 0
        try:
            occupancy_rate = f'{(real_collections / total_bills * 100):,.1f} %'
        except:
            occupancy_rate = "0 %"

        return occupancy_rate

class CreateLocation(Resource):
    @login_required
    def get(self):
        pass
        # return Response(render_template('regions.html',name=current_user.name))
    def post(self):
        location_name = request.form.get('region')
        description = request.form.get('description')

        print("yeeeeeeeuuuuuu","name",location_name,"desc",description)

        region_obj = LocationOp(location_name,description)
        region_obj.save()

        


class RegisterOwner(Resource):
    """This class registers an owner."""
    @login_required
    def get(self):
        user_group = current_user.company_user_group
        accessright = check_accessright(user_group,"create_owner")
        if accessright != True:
            return Response(render_template('noaccess.html',name=current_user.name))

        return Response(render_template(
            'owner.html',
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        """ Handle POST request for this view. Url ---> /add/owner """

        email=request.form.get('email')

        fname = request.form.get('fname')
        lname = request.form.get('lname')
        ftel = request.form.get('ftel')
        ltel = request.form.get('ltel')


        created_by = current_user.id
        name = fname+" "+lname
        tel_validation = ValidatePass.validate_password(ftel,ltel)
        if not tel_validation:
            flash("Please provide owners' mobile number","fail")
            return redirect(url_for('api.registerowner'))
        if tel_validation == "no match":
            flash("Please check the mobile number and try again","fail")
            return redirect(url_for('api.registerowner'))
        else:
            phone = ftel


        uniquename = uniquename_generator(name,phone)
        is_present  = OwnerOp.fetch_owner_by_uniquename(uniquename)
        is_present2  = OwnerOp.fetch_owner_by_phone(phone)
        
        
        if is_present:
            flash("Record exists in the database already","fail")
            return redirect(url_for('api.registerowner'))

        if is_present2:
            flash("Owner with similar mobile number already registered","fail")
            return redirect(url_for('api.registerowner'))

        owner = OwnerOp(name,phone,email,uniquename,created_by)
        owner.save()

        owner_user = UserOp.fetch_user_by_phone(phone)
        
        if owner_user:
            natid = owner_user.national_id
            OwnerOp.update_natid(owner,natid)
            UserOp.update_status(owner_user,True)

        msg='Success, add apartments below.'
        flash(msg,"success")
        return redirect(url_for('api.createapartment'))

class CreateApartment(Resource):
    @login_required
    def get(self):
        user_group = current_user.company_user_group
        accessright = check_accessright(user_group,"add_apartment")
        if accessright != True:
            return Response(render_template('noaccess.html',name=current_user.name))

        owners = OwnerOp.fetch_all_owners()

        location_list = fetch_all_locations()
        regions = stringify_list_items(location_list)
        regions.sort()
        return Response(render_template(
            'apartments.html',
            name=current_user.name,
            option_list=regions,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            owners=owners))

    def post(self):
        formatted_url = None
        name = request.form.get("name")
        owner = request.form.get("owner")
        location = request.form.get("location")
        file_to_upload = request.files.get("image") # get uploaded image
        if file_to_upload:
            upload_result = upload(file_to_upload) # send image to cloud
            # style the image and get its url after styling
            formatted_url, options = cloudinary_url(upload_result['public_id'],format="png",crop="fill",width=64,height=64)
            print(formatted_url)
        secure_image  = url_security(formatted_url)

        # pipeshelf = Cloud.CloudinaryImage("'upload_result[public_id]'+'.png'")
        agency_managed = request.form.get('agency_management')

        if not agency_managed:
            agency_managed = "False"

        bool_value = return_bool(agency_managed)


        owner_id = get_owner_id(owner)
        location_id = get_location_id(location)
        
        present = ApartmentOp.fetch_apartment_by_name(name)
        if present:
            flash("Similar apartment exists","fail")
            
            return redirect(url_for('api.createapartment'))

        
        apartment_obj = ApartmentOp(name,secure_image,location_id,owner_id,bool_value,current_user.id)
        apartment_obj.save()
        owner_obj = OwnerOp.fetch_owner_by_uniquename(owner)
        owner_natid = owner_obj.national_id
        if owner_natid:
            owner_user = UserOp.fetch_user_by_national_id(owner_natid)
            ApartmentOp.relate(apartment_obj,owner_user)

            if not bool_value:
                owner_co_id = owner_user.company_id
                ApartmentOp.update_company(apartment_obj,owner_co_id)

        msg = "Property registration success, time to add some houses"
        flash(msg,"success")

        return redirect(url_for('api.createapartment'))

class PropertyManagement(Resource):
    """class"""
    @login_required
    def get(self):
        prop_id = request.args.get("propid")
        prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
        db.session.expire(prop_obj)
        period=get_billing_period(prop_obj)
        str_period=get_str_month(period.month)
        house_list = prop_obj.houses
        houses = len(house_list)
        tenancy = tenantauto(prop_obj.id)
        tenants = len(tenancy)
        owner = prop_obj.owner
        if prop_obj.caretaker_id:
            caretaker = UserOp.fetch_user_by_username(prop_obj.caretaker_id)
        else:
            caretaker = "Unavailable"
        if prop_obj.agency_managed:
            agent = UserOp.fetch_user_by_username(prop_obj.agent_id)
            try:
                agent_name = agent.name
                contact = agent.phone
            except:
                agent_name = "Not available"
                contact = "N/A"
        else:
            agent_name = "Not managed by an Agency"
            contact = "N/A"


        houselist = house_details(house_list)
        houseids = get_obj_ids(houselist)

        template = "ajax_prop_detail2.html" if crm(current_user) else "ajax_prop_detail.html"

        return render_template(
            template,
            prop=prop_obj,
            owner=owner,
            caretaker=caretaker,
            agent=agent_name,
            num_units=houses,
            num_tenants=tenants,
            contact=contact,
            items=houselist,
            period=str_period,
            houseids=houseids
            )

class SalesRepsManagement(Resource):
    """class"""
    @login_required
    def get(self):
        com_obj = current_user.company
        props = com_obj.props
        reps = com_obj.reps
        attlist = att_details(reps)
        subids = get_obj_ids(attlist)
        
        return render_template("ajax_reps_detail.html",stations=props,subids=subids,bills=attlist)

class AddSalesAgent(Resource):
    @login_required
    def get(self):
        pass
        # return Response(render_template('regions.html',name=current_user.name))
    def post(self):
        company_obj = current_user.company

        prop = request.form.get('prop')
        name = request.form.get('name')
        email = request.form.get('mail')
        phone = request.form.get('tel')
        natid = request.form.get('natid')

        target = request.form.get('target')



        if target:
            att_id = request.form.get("attid")
            att_obj = SalesRepOp.fetch_attendant_by_id(get_identifier(att_id))

            if att_obj:
                SalesRepOp.delete(att_obj)
                return proceed
            else:
                return err

        if email and name:
            pass
        else:
            return err + "name or email missing"

        user_obj = None

        user_obj = UserOp.fetch_user_by_email(email) if email else None
        if not user_obj:
            user_obj = UserOp.fetch_user_by_phone(phone) if phone else None
            if not user_obj:
                user_obj = UserOp.fetch_user_by_national_id(natid) if natid else None
                       
        if not user_obj:

            usercode = usercode_generator()
            is_present  = UserOp.fetch_user_by_usercode(usercode)
            if is_present:
                usercode = usercode_generator()#generate code again

            if not email:
                username = username_extracter(name)
                is_present2  = UserOp.fetch_user_by_username(username)
                if is_present2:
                    username = username_extracternum(name)#append random numbers to name
                    is_present3 = UserOp.fetch_user_by_username(username)
                    if is_present3:
                        username = username_extracternum(name) #generate username again
            else:
                username = username_exctractermail(email)

            found = False

            for obj in company_obj.groups:
                    if str(obj) == "Sales":
                        found = True
                        company_usergroup_obj = obj

            if not found: #REFACTOR TO REMOVE THIS BLOCK
                group2 = CompanyUserGroupOp("Sales","Sales rep",company_obj.id)
                group2.save()
                company_usergroup_obj = group2

            user_obj = UserOp(name,usercode,username,natid,phone,email,"1234",4,company_usergroup_obj.id,company_obj.id)
            user_obj.save()

            repp = SalesRepOp.fetch_rep_by_name(name.lower())
            if not repp:
            
                rep_obj = SalesRepOp(name,name,phone,company_obj.id)
                rep_obj.save()

                if prop:
                    prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
                    UserOp.relate(user_obj,prop_obj)

                # att_obj = SalesRepOp(name,phone,prop_obj.id)
                # att_obj.save()

                msg = "Sales agent added"
                return proceed + msg

class TenantManagement(Resource):
    """class"""
    @login_required
    def get(self):
        prop_id = request.args.get("propid")
        propid = get_identifier(prop_id)
        prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
        db.session.expire(prop_obj)
        house_list = prop_obj.houses
        houses = len(house_list)
        tenancy = tenantauto(prop_obj.id)
        tenants = len(tenancy)

        tenantlist = []

        all_tenants = tenantauto(propid)
        for i in all_tenants:
            new_i = TenantOp.view(i)
            tenantlist.append(new_i)

        all_ptenants = prop_obj.ptenants
        for i in all_ptenants:
            new_i = PermanentTenantOp.view(i)
            tenantlist.append(new_i)

        tenantids = get_obj_ids(tenantlist)
        moreids = inject_tenants_ids(tenantlist) 
        full_ids = tenantids + "," + moreids

        template = "ajax_tenants_detail2.html" if crm(current_user) else "ajax_tenants_detail.html"

        return render_template(template,prop=prop_obj,num_units=houses,num_tenants=tenants,tenantids=full_ids,bills=tenantlist)

class SubmissionsManagement(Resource):
    """class"""
    @login_required
    def get(self):

        target = request.args.get('target')
        prop = request.args.get("prop")
        house = request.args.get("house")

        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
        if prop_obj:
            propid = prop_obj.id

        if target == "submissions":

            db.session.expire(prop_obj)
            submissions = prop_obj.submissions

            gtotal = 0.0

            target_submissions = fetch_current_billing_period_data_alt(prop_obj.billing_period,submissions)

            submissionlist = []

            for i in target_submissions:
                gtotal += i.amount_paid
                sub = SubmissionOp.view(i)
                submissionlist.append(sub)

            subids = get_obj_ids(submissionlist)
            
            return render_template("ajax_prop_submissions.html",prop=prop_obj,subids=subids,bills=submissionlist,gtotal=f"{gtotal:,.1f}")

        if target == "houses":
            tenant_list = tenantauto(propid)
            house_tenant_list = generate_house_tenants(tenant_list)
            return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant",access="",propid=propid)

        if target == "tname":
            house_obj = get_specific_house_obj_from_house_tenant_alt(propid,house)
            tenant_obj = check_occupancy(house_obj)[1]
            if tenant_obj.multiple_houses:
                houses = get_active_houses(tenant_obj)[1]
                return render_template('ajax_target_houses.html',house_list=houses,tenant_obj=tenant_obj,propid=propid)
            return f'<i class="fas fa-user mr-1"></i>: Tenant <span class="text-black mr-2">{tenant_obj.name}</span> balance: Kes <span class="text-danger">{tenant_obj.balance:,.2f}</span>'

        if target == "tenant name2":
            house_obj = get_specific_house_obj(propid,house)
            bills = house_obj.monthlybills
            latest_bill = max(bills, key=lambda x: x.id) if bills else None
            if latest_bill:
                latest_bill_balance = latest_bill.balance
            else:
                latest_bill_balance = 0.0
            
            return f'<i class="fas fa-home mr-1"></i>: House  <span class="text-black mr-2">{house_obj.name}</span>  balance : Kes <span class="text-danger">{latest_bill_balance:,.2f}</span>'

        else:
            period = current_user.company.billing_period
            props = fetch_all_apartments_by_user(current_user)
            return render_template("ajax_submissions_detail.html",dataperiod=get_str_month(period.month),co=current_user.company,subprops=props)


            


    @login_required
    def post(self):
        prop = request.form.get('prop')
        house_name = request.form.get('house')
        house_name2 = request.form.get('house2')

        paydate = request.form.get("date")
        paymonth = request.form.get("select_month")

        from dateutil.parser import parse

        if paydate:
            formatted_paydate = date_formatter(paydate)
            pay_date = parse(formatted_paydate)
        else:
            pay_date = datetime.datetime.now()
    
        raw_bill_ref = request.form.get('bill_ref')#typed
        amount = request.form.get('paidamount')#typed

        valid_amount = validate_input(amount)

        if not valid_amount:
            return "<div class='center-btn text-danger text-xx'>Invalid amount !</div"

        if raw_bill_ref.upper() == "N/A":
            bill_ref = raw_bill_ref
        elif raw_bill_ref.upper() == "NA":
            bill_ref = "N/A"
        elif len(raw_bill_ref) < 1:
            bill_ref = "N/A"
        else:
            bill_ref = raw_bill_ref

        ########################################################################################

        if house_name:
            prop = ApartmentOp.fetch_apartment_by_name(prop)

            if not paymonth:
                period = prop.billing_period
            else:
                num_month = get_numeric_month(paymonth)
                period = generate_date(num_month,prop.billing_period.year)

            target_houses = []       

            if house_name2:

                if house_name2 == "none selected":
                    return "<span class='text-danger text-xx'>Submission failed, please specify house!</span>"

                str_houses = house_name2.replace(","," ")
                houselist = list(str_houses.split(" "))

                for hse in houselist:
                    hse_obj = get_specific_house_obj(prop.id,hse)
                    target_houses.append(hse_obj)

            else:
                hse_obj = get_specific_house_obj_from_house_tenant_alt(prop.id,house_name)
                target_houses.append(hse_obj)

            house_obj = target_houses[0]
            

            tenant_obj = check_occupancy(house_obj)[1]

            house_id = house_obj.id
            tenant_id = tenant_obj.id
            created_by = current_user.id

            #######################################################################################
            # pay_period = paid to which bills
            # pay_date = alilipa lini?
            sub_obj = SubmissionOp(valid_amount,bill_ref,period,pay_date,prop.id, house_id,tenant_id,created_by)
            sub_obj.save()
            #################################################################################################

            return "Submitted successfully"
        else:
            print("FORGOT TO SELECT HOUSE WHILE MAKING SUBMISSION")
            abort(404)

class PaymentsManagement(Resource):
    """class"""
    @login_required
    def get(self):
        prop_id = request.args.get("propid")
        prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
        db.session.expire(prop_obj)

        period = get_billing_period(prop_obj)

        tenant_payments = prop_obj.payment_data

        filtered_payments = fetch_current_billing_period_payments(period,tenant_payments)
        dict_item = ""

        if filtered_payments:

            latest_set = max(filtered_payments, key=lambda x: x.id)
            for i in filtered_payments:
                if i == latest_set:
                    latest_set_index = filtered_payments.index(i)
                    break
            popped_latest_set = filtered_payments.pop(latest_set_index)

            item = popped_latest_set

            dict_item={
                'id':item.id,
                'editid':PaymentOp.generate_editid(item),
                'delid':PaymentOp.generate_delid(item),
                'tenant':item.tenant.name,
                'house':item.house.name,
                'hst':PaymentOp.combine_house_tenant_alt(item),
                'mode':PaymentOp.fname_extracter(item.paymode),
                'payid':item.id,
                'ref':item.ref_number,
                'chargedamnt':PaymentOp.fig_format(item.charged_amount),
                'highlight':PaymentOp.highlight(item),
                'amount':PaymentOp.fig_format(item.amount),
                'charge':item.payment_name,
                'month':PaymentOp.get_month(item),
                'date':PaymentOp.get_date_time(item)[0],
                'time':PaymentOp.get_date_time(item)[1],
                'balance':PaymentOp.fig_format(item.balance),
                'ref':item.ref_number,
                'smsstatus':PaymentOp.get_sms_status(item),
                'emailstatus':item.email_status if item.email_status else "-",
                'by':PaymentOp.get_name(item),
                'new':"new",
                'on':PaymentOp.get_date(item)
            }

        detailed_payments_list = payment_details(filtered_payments)
        if dict_item:
            detailed_payments_list.append(dict_item)

        payids = get_obj_ids(detailed_payments_list)

        return render_template("ajax_payments_detail.html",prop=prop_obj,payids=payids,items=detailed_payments_list,dataperiod=get_str_month(period.month))

class Bills(Resource):
    """class"""
    @login_required
    def get(self):

        target = request.args.get('target')
        period_target = request.args.get('target_period')

        if not period_target:
            period_target = "current"

        if target == "houses":
            propid = request.args.get('propid')
            prop_id = get_identifier(propid)
            prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
            # return prop_obj.houses

            tenant_list = tenantauto(prop_id)
            house_tenant_list = generate_house_ownertenants(tenant_list,prop_id)
            houses = []
            for item in house_tenant_list:
                hs = get_specific_house_obj_from_house_tenant_alt_alt(prop_id,item)[0]
                dict_obj = {
                    "name": item,
                    "id":hs.id
                }
                houses.append(dict_obj)
            return render_template("ajax_bill_houses.html",houses=houses)

        update_login_history("invoice",current_user)


        props = fetch_all_apartments_by_user(current_user)

        co = current_user.company

        period = get_billing_period(current_user.company)

        items = []
        prop_ids = []

        frenttotal = 0
        fwatertotal = 0
        felectotal = 0
        fgarbtotal = 0
        fsectotal = 0
        fsevtotal = 0
        fdeptotal = 0
        fargtotal = 0
        fpenalties = 0
        farrearstotal = 0
        fothers = 0
        ftotalbills = 0
        ftotalpaid = 0
        ftotalbalance = 0
        
        for prop in props:
            # sms = "0/0"
            monthlybills = prop.monthlybills

            if period_target == "current":
                filtered_bills = fetch_current_billing_period_bills(period,monthlybills)
            elif period_target == "previous":
                filtered_bills = fetch_prev_billing_period_bills(period,monthlybills)
            else:
                filtered_bills = fetch_next_billing_period_bills(period,monthlybills)

            renttotal = 0
            watertotal = 0
            electotal = 0
            garbtotal = 0
            sectotal = 0
            sevtotal = 0
            deptotal = 0
            argtotal = 0
            penalties = 0
            arrearstotal = 0
            others = 0
            totalbills = 0
            totalpaid = 0
            totalbalance = 0

            smsstatus = []

            for bill in filtered_bills:
                renttotal += bill.rent
                watertotal += bill.water
                electotal += bill.electricity
                garbtotal += bill.garbage 
                sectotal += bill.security
                sevtotal += bill.maintenance
                deptotal += bill.deposit
                argtotal += bill.agreement
                penalties += bill.penalty
                arrearstotal += bill.arrears if bill.arrears > 0 else 0
                others += bill.electricity + bill.garbage + bill.maintenance + bill.security + bill.agreement
                totalbills += bill.total_bill if bill.total_bill > 0 else 0 
                totalpaid += bill.paid_amount
                totalbalance += bill.balance if bill.balance > 0 else 0

                # print("INV STATUS for ",bill.house, prop, "SMS >>>>>",bill.sms_invoice,"Email >>>",bill.email_invoice)

                if bill.sms_invoice == "pending" or bill.sms_invoice == "waiting" or bill.sms_invoice == "fail":
                    smsstatus.append("0")
                else:
                    smsstatus.append("1")

            numerator = smsstatus.count("1")

            if numerator == 0 and len(smsstatus) != 0:
                sms_outline = "text-primary"
            # elif numerator < len(smsstatus) and len(smsstatus) != 0:
            #     sms_outline = "btn-warning"
            else:
                sms_outline = "text-success"

            sms = f'{numerator}/{len(smsstatus)}'

            num_units = len(tenantauto(prop.id))
            ptnts = len(prop.ptenants)
            # num_vacs = len(houseauto(prop.id)) - num_units


            frenttotal += renttotal
            fwatertotal += watertotal
            felectotal += electotal
            fgarbtotal += garbtotal
            fsectotal += sectotal
            fsevtotal += sevtotal
            fdeptotal += deptotal
            fargtotal += argtotal
            fpenalties += penalties
            farrearstotal += arrearstotal
            fothers += others
            ftotalbills += totalbills
            ftotalpaid += totalpaid
            ftotalbalance += totalbalance

            if prop.billing_period.month != co.billing_period.month:
                bill_outline = "text-primary"
            else:
                bill_outline = "text-dark"

            if prop.billprogress == "billing":
                progress = '<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Billing'
            elif prop.billprogress == "failed":
                progress = '<i class="fas fa-exclamation mr-2" role="status" aria-hidden="true"></i>Retry'
            else:
                progress = 'Generate'

            if len(smsstatus) < 1:
                invs = '<span class="text-danger font-weight-bold">not billed</span'
            else:
                invs = len(smsstatus)

            dict_obj = {
                'propid':prop.id,
                'identity':"prp"+str(prop.id),
                'billid':"bill"+str(prop.id),
                'smsid':"sms"+str(prop.id),
                'name':fname_extracter(prop.name),
                'tenants':num_units,
                'ptenants':ptnts,
                'invs':invs,
                'progress':progress,
                'water':(f"{watertotal:,.1f} "),
                'deposit':(f"{deptotal:,.1f} "),
                'rent':(f"{renttotal:,.1f} "),
                'fine':(f"{penalties:,.1f} "),
                'arrears':(f"{arrearstotal:,.1f} "),
                'others':(f"{others:,.1f} "),
                'total':(f"{totalbills:,.1f} "),
                'paid':(f"{totalpaid:,.1f} "),
                'bal':(f"{totalbalance:,.1f} "),
                'bill_outline':bill_outline,
                'sms_outline':sms_outline,
                'sms':sms
            }

            items.append(dict_obj)
            prop_ids.append(prop.id)
            prop_ids.append("prp"+str(prop.id))
            prop_ids.append("bill"+str(prop.id))
            prop_ids.append("sms"+str(prop.id))

        propids = ','.join(map(str, prop_ids))

        prevmonth = f'{get_str_month(get_prev_month(co.billing_period.month))}'
        nextmonth = f'{get_str_month(get_next_month(co.billing_period.month))}'

        template = 'crm_ajax_bills.html' if crm(current_user) else 'ajax_bills.html'

        return render_template(
            template,
            renttotal = frenttotal,
            watertotal = f"{fwatertotal:,.2f}",
            electotal = felectotal,
            garbtotal = fgarbtotal,
            sectotal = fsectotal,
            sevtotal = fsevtotal,
            deptotal = fdeptotal,
            argtotal = fargtotal,
            penalties = f"{fpenalties:,.1f}",
            arrearstotal = f"{farrearstotal:,.1f}",
            others = f"{fothers:,.1f}",
            totalbills = f"{ftotalbills:,.1f}",
            totalpaid = f"{ftotalpaid:,.1f}",
            totalbalance = f"{ftotalbalance:,.1f}",
            fieldshow_dep = "dispnone" if not fdeptotal else "",
            fieldshow_fine = "dispnone" if not fpenalties else "",
            fieldshow_arr = "dispnone" if not farrearstotal else "",
            propids=propids,
            items=items,
            company=current_user.company,
            previous_month = prevmonth,
            next_month = nextmonth,
            current_month=get_str_month(period.month),
            period_target=period_target
            )

class Payments(Resource):
    """class"""
    @login_required
    def get(self):

        update_login_history("payment",current_user)

        props = fetch_all_apartments_by_user(current_user)

        co = current_user.company

        period = get_billing_period(current_user.company)

        items = []
        prop_ids = []

        frenttotal = 0
        fwatertotal = 0
        felectotal = 0
        fgarbtotal = 0
        fsectotal = 0
        fsevtotal = 0
        fdeptotal = 0
        fargtotal = 0
        fpenalties = 0
        farrearstotal = 0
        fothers = 0
        ftotalbills = 0
        ftotalpaid = 0
        ftotalbalance = 0
        
        for prop in props:
            # sms = "0/0"
            monthlybills = prop.monthlybills
            filtered_bills = fetch_current_billing_period_bills(period,monthlybills)

            renttotal = 0
            p_renttotal = 0

            watertotal = 0
            p_watertotal = 0

            deptotal = 0
            p_deptotal = 0

            penalties = 0
            p_penalties = 0

            electotal = 0

            garbtotal = 0

            sectotal = 0

            sevtotal = 0

            argtotal = 0

            others = 0
            p_others = 0

            arrearstotal = 0
            totalbills = 0
            totalpaid = 0
            totalbalance = 0

            smsstatus = []
            payments = []

            for bill in filtered_bills:
                renttotal += bill.rent
                p_renttotal += bill.rent_paid if bill.rent_paid else 0

                watertotal += bill.water
                p_watertotal += bill.water_paid if bill.water_paid else 0

                deptotal += bill.deposit
                p_deptotal += bill.deposit_paid if bill.deposit_paid else 0
                
                penalties += bill.penalty
                p_penalties += bill.penalty_paid if bill.penalty_paid else 0

                electotal += bill.electricity
                garbtotal += bill.garbage 
                sectotal += bill.security
                sevtotal += bill.maintenance
                argtotal += bill.agreement


                arrearstotal += bill.arrears if bill.arrears > 0 else 0
                others += bill.electricity + bill.garbage + bill.maintenance + bill.security + bill.agreement

                p_others += bill.electricity_paid if bill.electricity_paid else 0
                p_others += bill.garbage_paid if bill.garbage_paid else 0
                p_others += bill.maintenance_paid if bill.maintenance_paid else 0
                p_others += bill.security_paid if bill.security_paid else 0
                p_others += bill.agreement_paid if bill.agreement_paid else 0

                totalbills += bill.total_bill if bill.total_bill > 0 else 0 
                totalpaid += bill.paid_amount
                totalbalance += bill.balance if bill.balance > 0 else 0

                # print("INV STATUS for ",bill.house, prop, "SMS >>>>>",bill.sms_invoice,"Email >>>",bill.email_invoice)

                if bill.sms_invoice == "pending" or bill.sms_invoice == "waiting" or bill.sms_invoice == "fail":
                    smsstatus.append("0")
                else:
                    smsstatus.append("1")

                if bill.paid_amount:
                    payments.append("1")
                else:
                    payments.append("0")

            numerator = smsstatus.count("1")

            if numerator == 0 and len(smsstatus) != 0:
                sms_outline = "btn-danger"
            # elif numerator < len(smsstatus) and len(smsstatus) != 0:
            #     sms_outline = "btn-warning"
            else:
                sms_outline = "btn-success"

            sms = f'{numerator}/{len(smsstatus)}'
            payment_ratio = f'{payments.count("1")}/{len(payments)}'

            # num_units = len(tenantauto(prop.id))
            # num_vacs = len(houseauto(prop.id)) - num_units


            frenttotal += renttotal
            fwatertotal += watertotal
            felectotal += electotal
            fgarbtotal += garbtotal
            fsectotal += sectotal
            fsevtotal += sevtotal
            fdeptotal += deptotal
            fargtotal += argtotal
            fpenalties += penalties
            farrearstotal += arrearstotal
            fothers += others
            ftotalbills += totalbills
            ftotalpaid += totalpaid
            ftotalbalance += totalbalance

            if prop.billing_period.month != co.billing_period.month:
                bill_outline = "btn-primary"
            else:
                bill_outline = "btn-secondary"

            if prop.billprogress == "billing":
                progress = '<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Billing...'
            else:
                progress = 'Generate'

            dict_obj = {
                'propid':prop.id,
                'identity':"prp"+str(prop.id),
                'billid':"bill"+str(prop.id),
                'smsid':"sms"+str(prop.id),
                'name':fname_extracter(prop.name),
                'payments':payment_ratio,
                'invs':len(smsstatus),
                'progress':progress,
                'deposit':(f"{p_deptotal:,.1f} / {deptotal:,.1f}"),
                'water':(f"{p_watertotal:,.1f} / {watertotal:,.1f} "),
                'rent':(f"{p_renttotal:,.1f} / {renttotal:,.1f} "),
                'fine':(f"{p_penalties:,.1f} / {penalties:,.1f} "),
                'others':(f"{p_others:,.1f} / {others:,.1f} "),
                'total':(f"{totalbills:,.1f} "),
                'paid':(f"{totalpaid:,.1f} "),
                'bal':(f"{totalbalance:,.1f} "),
                'bill_outline':bill_outline,
                'sms_outline':sms_outline,
                'sms':sms
            }

            items.append(dict_obj)
            prop_ids.append(prop.id)
            prop_ids.append("prp"+str(prop.id))
            prop_ids.append("bill"+str(prop.id))
            prop_ids.append("sms"+str(prop.id))

        propids = ','.join(map(str, prop_ids))

        prevmonth = f'{get_str_month(get_prev_month(co.billing_period.month))}'

        template = 'crm_ajax_allpayments.html' if crm(current_user) else 'ajax_allpayments.html'

        return render_template(
            template,
            props=props,
            renttotal = frenttotal,
            watertotal = f"{fwatertotal:,.2f}",
            electotal = felectotal,
            garbtotal = fgarbtotal,
            sectotal = fsectotal,
            sevtotal = fsevtotal,
            deptotal = fdeptotal,
            argtotal = fargtotal,
            penalties = f"{fpenalties:,.1f}",
            arrearstotal = f"{farrearstotal:,.1f}",
            others = f"{fothers:,.1f}",
            totalbills = f"{ftotalbills:,.1f}",
            totalpaid = f"{ftotalpaid:,.1f}",
            totalbalance = f"{ftotalbalance:,.1f}",
            fieldshow_fine = "dispnone" if not fpenalties else "",
            fieldshow_dep = "dispnone" if not fdeptotal else "",
            propids=propids,
            items=items,
            company=current_user.company,
            previous_month = prevmonth,
            current_month=get_str_month(period.month)
            )

# class BillsManagement(Resource):
#     """class"""
#     @login_required
#     def get(self):
#         prop_id = request.args.get("propid")
#         prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
#         db.session.expire(prop_obj)

#         period = get_billing_period(prop_obj)

#         monthlybills = prop_obj.monthlybills

#         filtered_bills = fetch_current_billing_period_bills(period,monthlybills)

#         detailed_bills_list = bill_details(filtered_bills)

#         billids = get_obj_ids(detailed_bills_list)

#         return render_template("ajax_bills_detail.html",prop=prop_obj,billids=billids,items=detailed_bills_list)


class MeterManagement(Resource):
    """class"""
    @login_required
    def get(self):
        prop_id = request.args.get("propid")
        prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
        db.session.expire(prop_obj)


        unread_units = len(filtered_house_list(prop_id))
        metered_units = len(filter_in_metered_houses(prop_obj.name))
        read_units = metered_units - unread_units

        # readings = prop_obj.meter_readings
        billing_period = get_billing_period(prop_obj)
        next_billing_month = billing_period.month + 1 if billing_period.month != 12 else 1
        billing_month = billing_period.month
        str_month = get_str_month(next_billing_month)
        str_current_month = get_str_month(billing_month)
        recent_readings = readingsauto_new(billing_period,prop_obj)
        meter_readings = reading_details(recent_readings)

        reading_ids = get_obj_ids(meter_readings)

        return render_template("ajax_meter_detail.html",prop=prop_obj,current_month=str_current_month,period=str_month,metered_units=metered_units,unread_units=unread_units,read_units=read_units,bills=meter_readings,readingids=reading_ids)

class PropertyImageChange(Resource):
    def get(self):
        pass
    def post(self):
        formatted_url = None
        prop_id = request.form.get("propid")
        file_to_upload = request.files.get("image") # get uploaded image

        if file_to_upload:
            upload_result = upload(file_to_upload) # send image to cloud
            # style the image and get its url after styling
            formatted_url, options = cloudinary_url(upload_result['public_id'],format="png",crop="fill",width=64,height=64)
            print(formatted_url)
        prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
        secure_image  = url_security(formatted_url)

        ApartmentOp.update_image(prop_obj,secure_image)

        return redirect(url_for("api.index"))

class UpdateCompanyDetails(Resource):
    def get(self):
        pass

    @login_required
    def post(self):
        co = current_user.company
        co_name = request.form.get("co_name")
        co_street = request.form.get("co_address")
        co_mailbox = request.form.get("co_mailbox")
        co_city = request.form.get("co_city")
        co_region = request.form.get("co_region")
        co_mail = request.form.get("co_mail")
        co_phone = request.form.get("co_tel")
        co_sphone = request.form.get("co_stel")

        if current_user.username.startswith("qc") or os.getenv('APP_SETTINGS') or APP_SETTINGS == "development":
            pass
        else:
            co_name = ""

        CompanyOp.update_details(co,co_name,co_street,co_city,co_region,co_mailbox,co_mail,co_phone)
        CompanyOp.update_sphone(co,co_sphone)

        return redirect(url_for("api.index"))

class UpdatePropertyDetails(Resource):
    def get(self):
        pass
    def post(self):

        target = request.form.get("target")

        prop_id = request.form.get("propid")
        month = request.form.get("period")
        category = request.form.get("category")
        amount = request.form.get("arrears")
        desc = request.form.get("desc")


        agreement = request.form.get("agreement")
        commission = request.form.get("commission")
        int_commission = request.form.get("int_commission")

        shortcode = request.form.get("shortcode")
        consumer_key = request.form.get("consumer_key")
        consumer_secret = request.form.get("consumer_secret")

        prop_garb = request.form.get("prop_garb")
        prop_garb_tel = request.form.get("prop_garb_tel")
        prop_garbbank = request.form.get("prop_garbbank")
        prop_garbacc = request.form.get("prop_garbacc")

        prop_bank = request.form.get("prop_bank")
        prop_acc = request.form.get("prop_accno")
        prop_accname = request.form.get("prop_accname")

        lb = request.form.get("lb")
        lbaccname = request.form.get("lbaccname")
        lbaccno = request.form.get("lbaccno")

        lbtwo = request.form.get("lbtwo")
        lbaccnametwo = request.form.get("lbaccnametwo")
        lbaccnotwo = request.form.get("lbaccnotwo")


        prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)

        if target == "set llbal":
            month = request.form.get("month")

            if month:
                datestring = date_formatter_alt(month)
                target_period = parse(datestring)
            else:
                target_period = prop_obj.billing_period

            print("llp period",target_period, "propid",prop_id)

            llp = LandlordPaymentOp.fetch_current_llp(prop_id, target_period.month, target_period.year)

            # llp = LandlordPaymentOp.fetch_llp_by_id()

            # import pdb;
            # pdb.set_trace()

            try:
                arr = float(amount)
            except Exception as e:
                print("errror",e)
                arr = 0.0

            if category == "advance":
                if arr:
                    arr = arr*-1

            if llp:
                print("found llp")
                LandlordPaymentOp.update_arrears(llp,arr)
            else:
                print("llp not not found")
                llp = LandlordPaymentOp(arr,0.0,0.0,0.0,target_period,prop_id)
                llp.save()

            return proceed


        # ApartmentOp.update_prop_details(prop_obj,shortcode,consumer_key,consumer_secret,prop_garb,prop_garb_tel,prop_garbbank,prop_garbacc,prop_bank,prop_accname,prop_acc,lb,lbaccname,lbaccno,lbtwo,lbaccnametwo,lbaccnotwo,agreement,commission,int_commission)

        return redirect(url_for("api.index"))

class PropertyAccess(Resource):
    """class"""
    @login_required
    def get(self):
        accessright = current_user.username
        if accessright != "admin":
            return Response(render_template('noaccess.html',name=current_user.name))

        owners = OwnerOp.fetch_all_owners()
        agents = fetch_all_agents()

        return Response(render_template(
            'propertyaccess.html',
            name=current_user.name,
            owners=owners,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            agents=agents))

    @login_required
    def post(self):
        owner = request.form.get('owner')
        apartment = request.form.get('property')
        username = request.form.get('agent')
        propertyauto = request.form.get('propertyauto')

        owner_id = OwnerOp.fetch_owner_by_uniquename(owner).id
        apartments = ApartmentOp.fetch_all_apartments_by_owner(owner_id)

        if propertyauto:
            apartments.append("All")
            return render_template('allocapartmentoptions.html', apartmentlist=apartments)

        agent_obj = UserOp.fetch_user_by_username(username)

        if apartment == "All":
            for prop in apartments:
                current_apartments = fetch_all_apartments_by_user(agent_obj)
                if prop in current_apartments:
                    print("skipping...")
                else:
                    ApartmentOp.relate(prop,agent_obj)
                    print("Agent given access to ",str(prop))
                    UserOp.update_status(agent_obj,True)
                    ApartmentOp.update_agent(prop,agent_obj.username)
                    if prop.agency_managed:
                        agent_co = agent_obj.company
                        ApartmentOp.update_company(prop,agent_co.id)

                        company_users = agent_co.users
                        for i in company_users:
                            if i.user_group_id == 4:
                                ApartmentOp.relate(prop,i)
                                print("user added to ",str(prop))

        else:
            apartment_obj = ApartmentOp.fetch_apartment_by_name(apartment)
            current_apartments = fetch_all_apartments_by_user(agent_obj)
            if apartment_obj in current_apartments:
                print("Agent already has access to ",str(apartment_obj))
            else:
                ApartmentOp.relate(apartment_obj,agent_obj)
                print("Agent given access to ",str(apartment_obj))
                UserOp.update_status(agent_obj,True)
                if not apartment_obj.agent_id:
                    ApartmentOp.update_agent(apartment_obj,agent_obj.username)
                    if apartment_obj.agency_managed:
                        agent_co = agent_obj.company
                        ApartmentOp.update_company(apartment_obj,agent_co.id)
    
                        company_users = agent_co.users
                        for i in company_users:
                            if i.user_group_id == 4:
                                ApartmentOp.relate(apartment_obj,i)
                                print("user added to apartment")

        msg = "Operation completed"
        flash(msg,"success")
        return redirect(url_for('api.propertyaccess'))

class PropertyAccessTermination(Resource):
    """class"""
    @login_required
    def get(self):
        accessright = current_user.username
        if accessright != "admin":
            return Response(render_template('noaccess.html',name=current_user.name))

        owners = OwnerOp.fetch_all_owners()
        agents = fetch_all_agents()

        return Response(render_template(
            'propertyaccesstermination.html',
            name=current_user.name,
            owners=owners,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            agents=agents))

    @login_required
    def post(self):
        owner = request.form.get('owner')
        apartment = request.form.get('property')
        username = request.form.get('agent')
        propertyauto = request.form.get('propertyauto')

        owner_id = OwnerOp.fetch_owner_by_uniquename(owner).id
        apartments = ApartmentOp.fetch_all_apartments_by_owner(owner_id)

        if propertyauto:
            apartments.append("All")
            return render_template('allocapartmentoptions.html', apartmentlist=apartments)

        agent_obj = UserOp.fetch_user_by_username(username)

        if apartment == "All":
            # for prop in apartments:
            #     current_apartments = fetch_all_apartments_by_user(agent_obj)
            #     if prop in current_apartments:
            #         print("skipping...")
            #     else:
            #         ApartmentOp.relate(prop,agent_obj)
            #         ApartmentOp.update_agent(prop,agent_obj.username)
            #         if prop.agency_managed:
            #             agent_obj_co = agent_obj.company_id
            #             ApartmentOp.update_company(prop,agent_obj_co)
            pass
        else:
            apartment_obj = ApartmentOp.fetch_apartment_by_name(apartment)
            current_apartments = fetch_all_apartments_by_user(agent_obj)
            if apartment_obj not in current_apartments:
                print("Agent did not have access to ",str(apartment_obj))
            else:
                ApartmentOp.terminate(apartment_obj,agent_obj)
                print("Agent terminated from ",str(apartment_obj))
                # ApartmentOp.update_agent(apartment_obj,None)
                if apartment_obj.agent_id == agent_obj.username:
                    ApartmentOp.update_agent(apartment_obj,None)

                    agent_co = agent_obj.company
                    ApartmentOp.update_company(apartment_obj,None)

                    company_users = agent_co.users
                    for i in company_users:
                        print("These are users",company_users)
                        if i.user_group_id == 4:
                            current_user_apartments = fetch_all_apartments_by_user(i)
                            if apartment_obj in current_user_apartments:
                                ApartmentOp.terminate(apartment_obj,i)
                                print("user removed from ",str(apartment_obj))
                            else:
                                print("User did not have access to", str(apartment_obj))


                # # UserOp.update_status(agent_obj,True)
                # if apartment_obj.agency_managed:
                #     agent_obj_co = agent_obj.company_id
                #     ApartmentOp.update_company(apartment_obj,agent_obj_co)

        msg = "Operation completed"
        flash(msg,"success")
        return redirect(url_for('api.propertyaccesstermination'))

class ExpenseManagement(Resource):
    """class"""
    def get(self):
        target = request.args.get('target')
        period = request.args.get('period')
        prop_id = request.args.get("propid")
        prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
        db.session.expire(prop_obj)

        # all_expenses = filter_in_recent_data(prop_obj.expenses)
        if period == "old":
            all_expenses = fetch_prev_billing_period_data(prop_obj.billing_period,prop_obj.expenses)
        else:
            all_expenses = fetch_current_billing_period_data(prop_obj.billing_period,prop_obj.expenses)

        raw_approved_expenses = []

        pending_expenses = []
        approved_expenses = []
        completed_expenses = []
        rejected_expenses = []

        for i in all_expenses:
            if i.status == "approved":
                raw_approved_expenses.append(i)

        if target == "approved":
            for i in raw_approved_expenses:
                item = InternalExpenseOp.view(i)
                approved_expenses.append(item)

            reqids = get_obj_ids(approved_expenses)

            return render_template('ajax_search_expense.html',bills=approved_expenses,expids=reqids,approved_exps=raw_approved_expenses,datahighlight="text-success",data_group="Approved requests")

        if target == "completed":
            for i in all_expenses:
                if i.status == "completed":
                    item = InternalExpenseOp.view(i)
                    completed_expenses.append(item)

            reqids = get_obj_ids(completed_expenses)

            return render_template('ajax_search_expense.html',bills=completed_expenses,expids=reqids,approved_exps=raw_approved_expenses,datahighlight="text-info",data_group="Completed requests")

        if target == "rejected":
            for i in all_expenses:
                if i.status == "rejected":
                    item = InternalExpenseOp.view(i)
                    rejected_expenses.append(item)

            reqids = get_obj_ids(rejected_expenses)

            return render_template('ajax_search_expense.html',bills=rejected_expenses,expids=reqids,approved_exps=raw_approved_expenses,data_group="Rejected requests")
        
        elif target == "pending":
            for i in all_expenses:
                if i.status == "pending":
                    item = InternalExpenseOp.view(i)
                    pending_expenses.append(item)

            reqids = get_obj_ids(pending_expenses)

            return render_template('ajax_search_expense.html',bills=pending_expenses,expids=reqids,approved_exps=raw_approved_expenses,datahighlight="text-danger",data_group="Pending expenses")

        else:
            for item in all_expenses:
                if item.status == "completed":     
                    obj = InternalExpenseOp.view(item)
                    completed_expenses.append(obj)
            
            reqids = get_obj_ids(completed_expenses)

            return render_template("ajax_expenses.html",items=completed_expenses,approved_exps=raw_approved_expenses,expids=reqids,prop=prop_obj,propname=fname_extracter(str(prop_obj)))

    def post(self):
        # prop_id = request.form.get("propid")
        # prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)

        # db.session.expire(prop_obj)
        # all_expenses = filter_in_recent_data(prop_obj.expenses)

        # pending_expenses = []
        # approved_expenses = []

        # for item in all_expenses:
        #     if item.status == "approved":
        #         approved_expenses.append(item)
        
        # for item in all_expenses:
        #     if item.status == "pending":     
        #         obj = InternalExpenseOp.view(item)
        #         pending_expenses.append(obj)
        
        # reqids = get_obj_ids(pending_expenses)

        # return render_template("ajax_expenses.html",items=pending_expenses,approved_exps=approved_expenses,expids=reqids,prop=prop_obj)
        pass


class Expenses(Resource):
    """class"""
    @login_required
    def get(self):
        # apartment_list = fetch_all_apartments_by_user(current_user)

        # raw_expenses = []
        # pending_expenses = []
        # approved_expenses = []
        
        # for prop in apartment_list:
        #     exps = prop.expenses
        #     raw_expenses.append(exps)
        
        # all_expenses = flatten(raw_expenses)
        # for item in all_expenses:
        #     if item.status == "pending":
        #         pending_expenses.append(item)

        # for item in all_expenses:
        #     if item.status == "approved":
        #         approved_expenses.append(item)
        

        # my_expenses = []
        # for r in pending_expenses:
        #     obj = InternalExpenseOp.view(r)
        #     my_expenses.append(obj)

        # req_id_list = []
        # for req in my_expenses:
        #     req_id = req["id"]
        #     req_id_list.append(req_id)

        # return Response(render_template(
        #     'expenses.html',
        #     props=apartment_list,
        #     bills=my_expenses,
        #     expenseids=req_id_list,
        #     approved_exps=approved_expenses,
        #     name=current_user.name,
        #     logopath=logo(current_user.company)[0],
        #     mobilelogopath=logo(current_user.company)[1],
        #     group=get_group_name(current_user.user_group_id)
        # ))
        pass
    @login_required
    def post(self):
        expense_id = request.form.get('expenseid')
        action = request.form.get('action')

        expid = request.form.get('expid')

        propid = request.form.get('propid')
        expense_type = request.form.get('exp_type')
        name = request.form.get('name')
        month = request.form.get('month')
        qty = request.form.get('qty')
        house = request.form.get('house')
        deposit = request.form.get('deposit')
        cost = request.form.get('cost')
        labour = request.form.get('labour')
        desc = request.form.get('desc')

        # date = request.form.get('date')
        # status = request.form.get('status')
        
        run = request.form.get('run')

        try:
            deposit = float(deposit)
        except:
            deposit = 0.0

        try:
            cost = float(cost)
        except:
            cost = 0.0

        try:
            labour = float(labour)
        except:
            labour = 0.0

        amount = cost + labour

        prop_obj = ApartmentOp.fetch_apartment_by_id(propid)

        if not month:
            expense_period = prop_obj.billing_period
        else:
            int_month = get_numeric_month(month)
            # expense_period = generate_date(int_month,datetime.datetime.now().year) #TODO GET  APPROPRIATE YEAR
            expense_period = generate_date(int_month,2022)

        pending_expenses = []
        completed_expenses = []
        rejected_expenses = []

        
        db.session.expire(prop_obj)

        if run == "expenseapproval":
            if not action:
                action = "pending"
            expense_obj = InternalExpenseOp.fetch_expense_by_id(expense_id)
            status_before_edit = expense_obj.status

            InternalExpenseOp.update_status(expense_obj,action)
            InternalExpenseOp.update_comment(expense_obj,desc)

            # all_expenses = filter_in_recent_data(prop_obj.expenses)
            all_expenses = fetch_current_billing_period_data(prop_obj.billing_period,prop_obj.expenses)

            if status_before_edit == "pending":
                for i in all_expenses:
                    if i.status == "pending":
                        item = InternalExpenseOp.view(i)
                        pending_expenses.append(item)

                reqids = get_obj_ids(pending_expenses)
                return render_template('ajax_search_expense.html',bills=pending_expenses,expids=reqids,data_group="Pending expenses")


            elif status_before_edit == "completed":
                for i in all_expenses:
                    if i.status == "completed":
                        item = InternalExpenseOp.view(i)
                        completed_expenses.append(item)

                reqids = get_obj_ids(completed_expenses)
                return render_template('ajax_search_expense.html',bills=completed_expenses,expids=reqids,data_group="Completed requests")

            else:
                for i in all_expenses:
                    if i.status == "rejected":
                        item = InternalExpenseOp.view(i)
                        rejected_expenses.append(item)

                reqids = get_obj_ids(rejected_expenses)
                return render_template('ajax_search_expense.html',bills=rejected_expenses,expids=reqids,data_group="Rejected requests")

        elif run == "expenserequest":
            if not expense_type:
                expense_type = "other"

            expense_obj = InternalExpenseOp(name,expense_period,qty,house,deposit,cost,labour,amount,desc,expense_type,prop_obj.id,current_user.id)
            expense_obj.save()

            InternalExpenseOp.update_status(expense_obj,"completed")

            # all_expenses = filter_in_recent_data(prop_obj.expenses)
            all_expenses = fetch_current_billing_period_data(prop_obj.billing_period,prop_obj.expenses)

            for i in all_expenses:
                if i.status == "completed":
                    item = InternalExpenseOp.view(i)
                    completed_expenses.append(item)

            reqids = get_obj_ids(completed_expenses)

            return render_template('ajax_search_expense.html',bills=completed_expenses,expids=reqids,datahighlight="text-success",data_group="Completed requests")

        elif run == "expenseedit":
            editid = request.form.get('editid')
            for i in editid:
                if i.isdigit():
                    target_index = editid.index(i)
                    break

            number = editid[target_index:]

            expense_obj = InternalExpenseOp.fetch_expense_by_id(number)
            if expense_obj.expense_type == "Deposit refund":
                InternalExpenseOp.update_name(expense_obj,None,None,house,None)
                InternalExpenseOp.update_cost(expense_obj,deposit,cost,None,amount)
            else:
                if not cost:
                    target_cost = expense_obj.cost if expense_obj.cost else 0.0
                else:
                    target_cost = cost
                if not labour:
                    target_labour = expense_obj.labour if expense_obj.labour else 0.0
                else:
                    target_labour = labour
                
                target_amount = target_cost + target_labour

                InternalExpenseOp.update_name(expense_obj,name,qty,house,desc)
                InternalExpenseOp.update_cost(expense_obj,None,target_cost,target_labour,target_amount)
                InternalExpenseOp.update_expense_type(expense_obj,expense_type)

            # all_expenses = filter_in_recent_data(prop_obj.expenses)
            all_expenses = fetch_current_billing_period_data(prop_obj.billing_period,prop_obj.expenses)


            if expense_obj.status == "pending":
                for i in all_expenses:
                    if i.status == "pending":
                        item = InternalExpenseOp.view(i)
                        pending_expenses.append(item)

                reqids = get_obj_ids(pending_expenses)
                return render_template('ajax_search_expense.html',bills=pending_expenses,expids=reqids,data_group="Pending expenses")

            elif expense_obj.status == "completed":
                for i in all_expenses:
                    if i.status == "completed":
                        item = InternalExpenseOp.view(i)
                        completed_expenses.append(item)

                reqids = get_obj_ids(completed_expenses)
                return render_template('ajax_search_expense.html',bills=completed_expenses,expids=reqids,data_group="Completed requests")

            else:
                for i in all_expenses:
                    if i.status == "rejected":
                        item = InternalExpenseOp.view(i)
                        rejected_expenses.append(item)

                reqids = get_obj_ids(rejected_expenses)
                return render_template('ajax_search_expense.html',bills=rejected_expenses,expids=reqids,data_group="Rejected requests")

        elif run == "expensedelete":
            delid = request.form.get('delid')
            for i in delid:
                if i.isdigit():
                    target_index = delid.index(i)
                    break

            number = delid[target_index:]

            expense_obj = InternalExpenseOp.fetch_expense_by_id(number)
            status_before_delete = expense_obj.status

            InternalExpenseOp.delete(expense_obj)

            # all_expenses = filter_in_recent_data(prop_obj.expenses)
            all_expenses = fetch_current_billing_period_data(prop_obj.billing_period,prop_obj.expenses)

            if status_before_delete == "pending":
                for i in all_expenses:
                    if i.status == "pending":
                        item = InternalExpenseOp.view(i)
                        pending_expenses.append(item)

                reqids = get_obj_ids(pending_expenses)
                return render_template('ajax_search_expense.html',bills=pending_expenses,expids=reqids,data_group="Pending expenses")

            elif status_before_delete == "completed":
                for i in all_expenses:
                    if i.status == "completed":
                        item = InternalExpenseOp.view(i)
                        completed_expenses.append(item)

                reqids = get_obj_ids(completed_expenses)
                return render_template('ajax_search_expense.html',bills=completed_expenses,expids=reqids,data_group="Completed requests")

            else:
                for i in all_expenses:
                    if i.status == "rejected":
                        item = InternalExpenseOp.view(i)
                        rejected_expenses.append(item)

                reqids = get_obj_ids(rejected_expenses)
                return render_template('ajax_search_expense.html',bills=rejected_expenses,expids=reqids,data_group="Rejected requests")


        # elif run == "expensedisplay":
        #     """deprecated"""
            
        #     expenses = fetch_expenses(current_user)

        #     my_expenses = []

        #     req_id_list = []

        #     if prop:
        #         new_list = []
        #         for item in expenses:
        #             if str(item.apartment) == prop:
        #                 new_list.append(item)

        #     if date:
        #         filter_list = [] #to hold filtered data
        #         if prop:
                    
        #             for item in new_list:
        #                 str_item_date = str(item.date.date())
        #                 if str_item_date == date:
        #                     filter_list.append(item)

        #         else:
        #             for item in expenses:
        #                 str_item_date = str(item.date.date())
        #                 if str_item_date == date:
        #                     filter_list.append(item)

        #     if status:
        #         filter_list2 = [] # to hold further filtered data
        #         if prop:
        #             if date:
        #                 for item in filter_list:
        #                     if item.status == status:
        #                         filter_list2.append(item)
        #             else:
        #                 for item in new_list:
        #                     if item.status == status:
        #                         filter_list2.append(item)

        #         else:
        #             if date:
        #                 for item in filter_list:
        #                     if item.status == status:
        #                         filter_list2.append(item)
        #             else:
        #                 for item in expenses:
        #                     if item.status == status:
        #                         filter_list2.append(item)

        #     else:
        #         filter_list2 = []
            

        #     # my_expenses = []
        #     if prop and date and status:
        #         print("ayeya")
        #         expense_data = filter_list2
        #     elif prop and date:
        #         expense_data = filter_list
        #     elif prop and status:
        #         expense_data = filter_list2
        #     elif date and status:
        #         expense_data = filter_list2
        #     elif prop:
        #         expense_data = new_list
        #     elif date:
        #         expense_data = filter_list
        #     else:
        #         expense_data = filter_list2

        #     # expense_data = remove_dups(new_list)
        #     for r in expense_data:
        #         obj = InternalExpenseOp.view(r)
        #         my_expenses.append(obj)

        #     req_id_list = []
        #     for req in my_expenses:
        #         req_id = req["id"]
        #         req_id_list.append(req_id)

        #     return render_template('ajax_search_expense.html',bills=my_expenses,expids=req_id_list)

            # my_expenses = []
            # for r in expenses:
            #     obj = InternalExpenseOp.view(r)
            #     my_expenses.append(obj)

            # req_id_list = []
            # for req in my_expenses:
            #     req_id = req["id"]
            #     req_id_list.append(req_id)

            # return render_template('ajax_search_expense.html',bills=my_expenses,expenseids=req_id_list)




class BulkSms(Resource):
    @login_required
    def get(self):

        target = request.args.get("target")

        if target == "set":
            pass
        elif target == "set reminder":
            reminders = ReminderOp.fetch_all_reminders()
            for reminder in reminders:
                txt = reminder.txt
                print(txt)
                # text = f'Bulk sms requested by {reminder.apartment.company} for {reminder.apartment.name}'
                # response = sms.send(text, ["+254716674695"],"KIOTAPAY")

                # job8 = q.enqueue_call(
                #     func=send_bulk_sms, args=(propid,txt,), result_ttl=5000
                # )
        else:
            pass
                

    def post(self):

        rem_date = request.form.get("date")
        rem_prop = request.form.get("prop")
        channel = request.form.get("channel")
        rem_txt = request.form.get("text")
        target = request.form.get("target")

        print("Date: ",rem_date,"Prop ",rem_prop,"Channel ",channel, "Target ",target,"Text",rem_txt)

        try:
            prop_obj = ApartmentOp.fetch_apartment_by_name(rem_prop)
            propid = prop_obj.id
        except:
            print("running statement")
            propid = None
            pass

        if target == "general":
            if not propid:
                return failure
            job8 = q.enqueue_call(
                func=send_bulk_sms, args=(propid,rem_txt,), result_ttl=5000
            )
            text = f'General sms requested by {prop_obj.company} for {prop_obj.name}'
            response = sms.send(text, ["+254716674695"],sender)

            return success

        if target == "statement":
            tenantid = request.form.get("uuid")
            job9 = q.enqueue_call(
                func=send_statement, args=(tenantid,), result_ttl=5000
            )

            return success


        if target == "set template":
            if rem_txt:
                current_template = current_user.company.template
                if current_template:
                    TextTemplateOp.delete(current_template[0])

                texttemplate = TextTemplateOp(rem_txt,current_user.company.id)
                texttemplate.save()
                return success
            else:
                return failure

        else:
            if not propid:
                return failure
            try:
                raw_date = date_formatter(rem_date)

                from dateutil.parser import parse

                obj_date = parse(raw_date)
            except:
                obj_date = datetime.datetime.now() + relativedelta(hours=3)

            rem_obj = ReminderOp(obj_date,rem_txt,"0",propid)
            rem_obj.save()

            if channel == "email":
                text = f'Bulk email requested by {prop_obj.company} for {prop_obj.name}'
                send_internal_email_notifications(prop_obj.company.name,text)

                if current_user.username.startswith("qc") or current_user.national_id == "12345678" or localenv:
                    # ApartmentOp.update_reminder_status(prop_obj,"sent")
                    for ptenant in prop_obj.ptenants:
                        if ptenant.classtype.lower() != "shareholder":
                            continue
                        ptenantid = ptenant.id
                        job8 = q.enqueue_call(
                            func=send_out_single_email_crm_invoice, args=(ptenantid,), result_ttl=5000
                        )
                    return success
                else:
                    # if prop_obj.reminder_status == "sent":
                    #     text = f'Bulk email requested again by {prop_obj.company} for {prop_obj.name}'
                    #     send_internal_email_notifications(prop_obj.company.name,text)
                    #     response = sms.send(text, ["+254716674695"],sender)
                    #     return failure
                    # else:
                        # ApartmentOp.update_reminder_status(prop_obj,"sent")
                    for ptenant in prop_obj.ptenants:
                        ptenantid = ptenant.id
                        job8 = q.enqueue_call(
                            func=send_out_single_email_crm_invoice, args=(ptenantid,), result_ttl=5000
                        )
                    return success

            else:
                text = f'Bulk sms requested by {prop_obj.company} for {prop_obj.name}'
                send_internal_email_notifications(prop_obj.company.name,text)
                # response = sms.send(text, ["+254716674695"],sender)

                if current_user.username.startswith("qc") or current_user.national_id == "12345678" or current_user.usercode == "3551":
                    ApartmentOp.update_reminder_status(prop_obj,"sent")
                    job8 = q.enqueue_call(
                        func=send_reminder_sms, args=(propid,rem_txt,channel,), result_ttl=5000
                    )
                    return success
                else:
                    if prop_obj.reminder_status == "sent":
                        text = f'Bulk sms requested again by {prop_obj.company} for {prop_obj.name}'
                        send_internal_email_notifications(prop_obj.company.name,text)
                        response = sms.send(text, ["+254716674695"],sender)
                        return failure
                    else:
                        ApartmentOp.update_reminder_status(prop_obj,"sent")
                        job8 = q.enqueue_call(
                            func=send_reminder_sms, args=(propid,rem_txt,channel,), result_ttl=5000
                        )
                        return success
        

class TenantSms(Resource):
    def get(self):
        pass
    def post(self):
        tenant_id = request.form.get('tenant_id')
        sms_text = request.form.get('text')

        tenant = TenantOp.fetch_tenant_by_id(tenant_id)
        if tenant.sms:
            tele = tenant.phone
            phonenum = sms_phone_number_formatter(tele)

            co = current_user.company


                
            rem_sms =co.remainingsms
            if rem_sms > 0:
                #Send the SMS
                try:
                    recipient = [phonenum]
                    # message = f"Rental payment #{ref_number} Confirmed. We have received sum of Kshs {paid}. Outstanding balance is Kshs. {running_bal}"
                    new_text = current_user.company.name
                    message_body = f"{sms_text} \n~ {new_text}"
                    message = message_body

                    char_count = len(message)
                    if char_count <= 160:
                        cost = 1
                    elif char_count <= 320:
                        cost = 2
                    else:
                        cost = 3

                    ptenant_id = None
                    
                    sms_obj = SentMessagesOp(message,char_count,cost,tenant.id,ptenant_id,tenant.apartment.id,co.id)
                    sms_obj.save()

                    if co.sms_provider == "Advanta":
                        sms_sender(co.name,sms_text,phonenum)

                        msg = "Message sent successfully"
                        return render_template('ajaxproceed.html',alert=msg)            

                    else:
                        if sender == "AFRICASTKNG":
                            response = sms.send(message, recipient)
                        else:
                            response = sms.send(message, recipient,sender)
                        
                    print(response)
                    rem_sms -= 1
                    CompanyOp.set_rem_quota(co,rem_sms)
                    msg = "Message sent successfully"
                    return render_template('ajaxproceed.html',alert=msg)

                except Exception as e:
                    print(f"Houston, we have a problem {e}")
                    msg = "Sending failed!"
                    return render_template('ajaxghosthouse.html',alert=msg)
            else:
                msg = "Sending failed!"
                return render_template('ajaxghosthouse.html',alert=msg)
        else:
            msg = "Sms turned off for tenant!"
            return render_template('ajaxghosthouse.html',alert=msg)


class DataUpload(Resource):
    """class"""

    @login_required
    def get(self):
        pass

    def post(self):

        prop_name = request.form.get('prop')
        ttype = request.form.get('ttype')

        lfile("staring point")


        if prop_name and prop_name != "null":

            apartment_id = ApartmentOp.fetch_apartment_by_name(prop_name).id

            file = request.files.get('file')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            if sheet:
                if len(sheet.row_values(1)) != 7:
                    data_format_error = True
            try:
                if data_format_error:
                    nonexistent_item = sheet.row_values(1)[1000000]

                dict_array = []

                for row in rows:
                    dict_obj = {
                    "unit":sheet.row_values(row)[0],
                    "desc":sheet.row_values(row)[1],
                    "group":sheet.row_values(row)[2],
                    "tenant":sheet.row_values(row)[3],
                    "mobile":sheet.row_values(row)[4],
                    "email":sheet.row_values(row)[5],
                    "water":sheet.row_values(row)[6],
                    }

                    dict_array.append(dict_obj)

                uploadsjob = q.enqueue_call(
                    func=read_excel, args=(dict_array,apartment_id,ttype,current_user.id,), result_ttl=5000
                )

                lfile("finish point: rows",len(dict_array))

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

        else:
            return '<span class=text-danger>Select property first</span>'
            

class CreateHouseCode(Resource):
    """class"""

    @login_required
    def get(self):

        groupid = request.args.get('groupid')
        group_id = get_identifier(groupid)

        housegroup = HouseCodeOp.fetch_group_by_id(group_id)

        if not housegroup:
            savecontext = "Submit"
        else:
            savecontext = "Update"

        template = "ajax_groupform2.html" if crm(current_user) else "ajax_groupform.html"

        return render_template(
            template,
            savecontext=savecontext,
            group=housegroup)


    def post(self):

        target = request.form.get('target')
        apartment_id = request.form.get('propid')

        if target == "excelupload":
            file = request.files.get('file')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            if sheet:
                if len(sheet.row_values(1)) != 7:
                    data_format_error = True

            try:
                if data_format_error:
                    
                    nonexistent_item = sheet.row_values(1)[1000000]

                for row in rows:
                    house_code = sheet.row_values(row)[0]
                    rentrate = sheet.row_values(row)[1]
                    waterrate = sheet.row_values(row)[2]
                    garbagerate = sheet.row_values(row)[3]
                    securityrate = sheet.row_values(row)[4]
                    waterdep = sheet.row_values(row)[5]
                    elecdep = sheet.row_values(row)[6]

                    # print(type(rentrate))
                    if isinstance(house_code,float):
                        housecode = str(int(house_code))
                    else:
                        housecode = house_code

                    housecode = housecode.upper()

                    code_obj = get_specific_code_obj(apartment_id,housecode)

                    # run_validations = validate_float_inputs_to_exclude_zeros_alt(rentrate,waterrate,garbagerate,securityrate,waterdep,elecdep)

                    if code_obj:
                        print("Skipping ",housecode)
                        continue
                        
                    else:
                        valid_inputs = validate_float_inputs_to_exclude_zeros_alt(rentrate,waterrate,garbagerate,securityrate,waterdep,elecdep)
                        user_id = current_user.id     

                        new_code_obj = HouseCodeOp(housecode,valid_inputs[0],valid_inputs[1],valid_inputs[2],valid_inputs[3],0.0,valid_inputs[4],valid_inputs[5],0.0,0.0,0.0,apartment_id,user_id)
                        new_code_obj.save()

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
            

        else:
            house_code = request.form.get('housecode')
            rentrate = request.form.get('rentrate')
            watercharge = request.form.get('waterrate')
            waterrate = request.form.get('unitrate')
            electricityrate = request.form.get('elecunitrate')
            garbagerate = request.form.get('garbagerate')
            securityrate= request.form.get('securityrate')
            servicerate= request.form.get('servicerate')
            seweragerate= request.form.get('seweragerate')
            agreementrate= request.form.get('agreementrate')
            finerate = request.form.get('finerate')
            discount = request.form.get('discount')
            depnum = request.form.get('depnum')

            waterdep = request.form.get('waterdep')
            elecdep = request.form.get('elecdep')

            runalert = request.form.get('runalert')

            housecode = house_code.upper()
            code_obj = get_specific_code_obj(apartment_id,housecode)
            
            if runalert:
                if code_obj:
                    msg = "unavailable"
                    return msg + err
                if housecode:
                    msg = "Name accepted"
                    return msg + proceed
                return None

            if code_obj:
                msg = "exist already"
                return err + msg
            else:
                valid_inputs = validate_float_inputs_to_exclude_zeros(rentrate,waterrate,garbagerate,securityrate,finerate,waterdep,elecdep,watercharge,electricityrate,servicerate,seweragerate,discount,depnum)
                user_id = current_user.id     

                new_code_obj = HouseCodeOp(housecode,valid_inputs[0],valid_inputs[1],valid_inputs[2],valid_inputs[3],valid_inputs[4],valid_inputs[5],valid_inputs[6],valid_inputs[7],valid_inputs[8],valid_inputs[9],valid_inputs[10],valid_inputs[11],valid_inputs[12],apartment_id,user_id)
                new_code_obj.save()

                valid_inputs2 = validate_float_inputs_to_exclude_zeros(agreementrate)
                HouseCodeOp.update_agreement_rate(new_code_obj,valid_inputs2[0])

                if crm(current_user):
                    HouseCodeOp.update_listprice(new_code_obj,valid_inputs[0])
                    HouseCodeOp.update_rentrate(new_code_obj,0.0)

                msg = "House code added"
                return render_template('ajaxproceed.html',alert=msg)

class EditHouseCode(Resource):
    """update codes class"""
    # @login_required
    # def get(self):
    #     groupid = request.args.get('groupid')
    #     target = request.args.get('target')

    #     group_obj = HouseCodeOp.fetch_group_by_id(groupid)

    #     if target == "groupname":
    #         return f"<span class='text-success'>Enter new rates for group {group_obj.codename}</span>"
    #         # return render_template('ajaxproceed.html',alert=msg)
    #     else:
    #         return render_template('ajax_hscode_form.html',obj=group_obj)

    @login_required
    def post(self):

        target = request.form.get("target")

        if target == "delete":
            group_id = request.form.get("groupid")
            groupid = get_identifier(group_id)
            group_obj = HouseCodeOp.fetch_group_by_id(groupid)
            HouseCodeOp.delete(group_obj)

        else:
            groupid = request.form.get("groupid")
            codename = request.form.get('housecode')
            rentrate = request.form.get('rentrate')
            watercharge = request.form.get('waterrate')
            waterrate = request.form.get('unitrate')
            electricityrate = request.form.get('elecunitrate')
            garbagerate = request.form.get('garbagerate')
            securityrate= request.form.get('securityrate')
            servicerate= request.form.get('servicerate')
            finerate = request.form.get('finerate')
            seweragerate = request.form.get('seweragerate')
            agreementrate= request.form.get('agreementrate')
            waterdep = request.form.get('waterdep')
            elecdep = request.form.get('elecdep')
            carddep = request.form.get('carddep')
            discount = request.form.get('discount')
            depnum = request.form.get('depnum')
            vatrate = request.form.get('vatrate')
            bill_freq = request.form.get('billfreq')
            commission = request.form.get('commission')
            deposit = request.form.get('deposit')
            listprice = request.form.get('listprice')
            instalments = request.form.get("instalments")


            print("commission is here", commission)

            group_obj = HouseCodeOp.fetch_group_by_id(groupid)
            apartment_id = group_obj.apartment_id

            if bill_freq == "yearly" or bill_freq == "annually":
                billfreq = 12
            elif bill_freq == "semi-annually":
                billfreq = 6
            elif bill_freq == "quarterly":
                billfreq = 3
            else:
                billfreq = 1

            try:
                int_codename = int(codename)
                is_int = True
            except:
                is_int = False

            if codename:
                if not is_int:
                    housecode = codename.upper()
                    if housecode == group_obj.codename:
                        pass
                    else:
                        code_obj = get_specific_code_obj(apartment_id,housecode)
                        if code_obj:
                            msg = "Update failed, House code name unavailable"
                            return render_template('ajaxghosthouse.html',alert=msg)
                else:
                    housecode = codename
                    if housecode == group_obj.codename:
                        pass
                    else:
                        code_obj = get_specific_code_obj(apartment_id,housecode)
                        if code_obj:
                            msg = "Update failed, House code name unavailable"
                            return render_template('ajaxghosthouse.html',alert=msg)
                
            else:
                print("Group name missing")
                housecode = "null"

            if "%" in discount:
                disc = ""
            else:
                disc = discount

            result = validate_float_inputs(rentrate,waterrate,garbagerate,securityrate,finerate,waterdep,elecdep,watercharge,electricityrate,servicerate,seweragerate,vatrate,carddep,disc,depnum)

            HouseCodeOp.update_rates(group_obj,housecode,result[0],result[1],result[2],result[3],result[4],result[5],result[6],result[7],result[8],result[9],result[10],billfreq,result[11],result[12],result[13],result[14],current_user.id)

            valid_inputs2 = validate_float_inputs_to_exclude_zeros(agreementrate)
            HouseCodeOp.update_agreement_rate(group_obj,valid_inputs2[0])


            valid_inputs3 = validate_float_inputs_to_include_percent(listprice,deposit,commission,discount,instalments)
            # import pdb; pdb.set_trace()

            if "%" in commission:
                HouseCodeOp.update_commission(group_obj,valid_inputs3[2])
            else:
                HouseCodeOp.update_int_commission(group_obj,valid_inputs3[2])

            if "%" in deposit:
                HouseCodeOp.update_percentage_deposit(group_obj,valid_inputs3[1])
            else:
                HouseCodeOp.update_deposit(group_obj,valid_inputs3[1])

            if "%" in discount:
                HouseCodeOp.update_percentage_discount(group_obj,valid_inputs3[3])

            HouseCodeOp.update_listprice(group_obj,valid_inputs3[0])
            HouseCodeOp.update_instalments(group_obj,valid_inputs3[4])

            msg = "Rates updated successfully"
            return render_template('ajaxproceed.html',alert=msg)

class CreateHouse(Resource):
    """class"""
    @login_required
    def get(self):
        pass

    @login_required
    def post(self):

        target = request.form.get('target')
        apartment_id = request.form.get('propid')

        if target == "excelupload":
            file = request.files.get('file')
            codetype = request.form.get('type')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            if sheet:
                if len(sheet.row_values(1)) != 3:
                    data_format_error = True

            try:
                if data_format_error:
                    
                    nonexistent_item = sheet.row_values(1)[1000000]

                for row in rows:
                    try:
                        housename = str(int(sheet.row_values(row)[0]) if sheet.row_values(row)[0] else "" )
                    except:
                        housename = sheet.row_values(row)[0] if sheet.row_values(row)[0] else ""

                    housecode = str(sheet.row_values(row)[1])
                    desc = str(sheet.row_values(row)[2])

                    if housename == "":
                        print("EMPTY CELL")
                        continue

                    try:
                        house_name = housename.upper()
                    except:
                        house_name = housename

                    house_obj = get_specific_house_obj(apartment_id,house_name)
                    
                    if house_obj:
                        print("Skipping ",house_name)
                        continue

                    try:
                        rent_value = float(housecode)
                        print("RENT VALUE",rent_value)
                        found = False
                        prop_codes = ApartmentOp.fetch_apartment_by_id(apartment_id).housecodes
                        for code in prop_codes:
                            if codetype == "crm":
                                if code.listprice == rent_value:
                                    house_code = code.codename
                                    found = True
                                    print("RENT CODE FOUND",house_code)
                                    break
                            else:
                                if code.rentrate == rent_value:
                                    house_code = code.codename
                                    found = True
                                    print("RENT CODE FOUND",house_code)
                                    break
                        if not found:
                            print("RENT CODE NOOOOOOOOOOOT FOUND",housecode)
                            house_code = ""

                    except:
                        try:
                            house_code = housecode.upper()
                            print("string ACCEPTED FOR formatting",house_code)
                        except:
                            house_code = ""
                            print("string NOT accepted",housecode)


                    code_obj = get_specific_code_obj(apartment_id,house_code)
                    if not code_obj:
                        print("Specified code doesnt exist")
                        continue
                    else:
                        code_id = code_obj.id
                        
                    created_by = current_user.id
                    house_obj = HouseOp(house_name,apartment_id,code_id,created_by,desc)
                    house_obj.save()

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

        else:

            house_code = request.form.get('housecode')
            housename = request.form.get('house')
            desc = request.form.get('desc')


            runcode = request.form.get("runcode")
            runalert = request.form.get("runalert")
            runcodechange = request.form.get("runcodechange")

            prop_obj = ApartmentOp.fetch_apartment_by_id(apartment_id)

            if house_code:
                if house_code.startswith("\n>> "):
                    print("length is",len(house_code))
                    print(house_code)
                    housecode = house_code[4:]
                    print("after",housecode)
                else:
                    housecode = house_code
            else:
                housecode = None

            if runcode:
                prop_housecodes = prop_obj.housecodes
                return render_template('ajax_multivariable.html',items=prop_housecodes,placeholder="Select group")

            if not housecode:
                msg = "You must select the group first"
                return msg + err

            code_obj = get_specific_code_obj(apartment_id,housecode)
            code_id = code_obj.id

            if runcodechange:
                # return render_template('ajax_variable.html',item=housecode,rent)
                code_string = f'<span class="text-primary small"> >>{code_obj.codename} ( Rent:{code_obj.rentrate} & Unit:{code_obj.waterrate})</span>'
                return code_string


            house_name = housename.upper()
            house_obj = get_specific_house_obj(apartment_id,house_name)
            
            if runalert:
                if house_obj:
                    msg = "Similar name exists"
                    return err + msg
                if house_name:
                    return proceed
                return None

            if house_obj:
                return err

            created_by = current_user.id
            house_obj = HouseOp(house_name,apartment_id,code_id,created_by,desc)
            house_obj.save()

            msg = f"House {house_obj.name} added successfully"
            return proceed + msg
class EditHouse(Resource):
    """class"""
    def get(self):
        propid = request.args.get('propid')
        houseid = request.args.get('houseid')
        housename = request.args.get('house')

        target = request.args.get("target")

        if target == "checkdups":
            house_name = housename.upper()
            house_obj = get_specific_house_obj(propid,house_name)

            if house_obj:
                msg = "Similar name exists"
                return render_template('ajaxghosthouse.html',alert=msg)
            if housename:
                msg = "Name accepted"
                return render_template('ajaxproceed.html',alert=msg)
            return None


        if target == "listhouses":
            prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
            prop_housecodes = prop_obj.housecodes
            return render_template('ajax_multivariable.html',items=prop_housecodes,placeholder="select new group")

        if target == "houseinfo":
            house_obj = HouseOp.fetch_house_by_id(houseid)
            housecode = house_obj.housecode
            msg = f'{house_obj.name} is currently placed at Group {housecode}'
            return render_template('ajaxproceed.html',alert=msg)

        if target == "houseinfo-alt":
            house_id = get_identifier(houseid)
            house_obj = HouseOp.fetch_house_by_id(house_id)
            housecode = house_obj.housecode
            msg = f'Editing {house_obj.name}'
            return render_template('ajaxproceed.html',alert=msg)

    def post(self):
        propid = request.form.get('propid')
        houseid = request.form.get('houseid')
        name = request.form.get('name')
        watertarget = request.form.get('watertarget')
        servicetarget = request.form.get('servicetarget')

        desc = request.form.get('desc')
        group = request.form.get('group')

        target = request.form.get("target")

        if target == "delete":
            if houseid:
                house_id = get_identifier(houseid)
                print(house_id)
                house_obj = HouseOp.fetch_house_by_id(house_id)
                HouseOp.delete(house_obj)
                return None
            return None

        if target == "edit house group":
            # house_obj = get_specific_house_obj(apartment_id,housename)
            group_obj = get_specific_code_obj(propid,group)
            house_obj = HouseOp.fetch_house_by_id(houseid)

            HouseOp.update_housecode_id(house_obj,group_obj.id)

            msg = f"House {house_obj.name} updated successfully"
        else:
            house_name = name.upper()
            house_obj = get_specific_house_obj(propid,house_name)

            if house_obj:
                msg = "Similar name exists"
            else:
                house_id = get_identifier(houseid)
                house_obj = HouseOp.fetch_house_by_id(house_id)

                HouseOp.update_details(house_obj,name,desc)
                HouseOp.update_billing_details(house_obj,watertarget,servicetarget)

                msg = f"House {house_obj.name} updated successfully"

        return render_template('ajaxproceed.html',alert=msg)

class HouseBillStatus(Resource):
    def get(self):
        pass
    def post(self):
        houseid = request.form.get("houseid")
        status = request.form.get("bill_status")

        house_obj = HouseOp.fetch_house_by_id(houseid)
        bool_val = get_bool(status)

        HouseOp.update_billable(house_obj,bool_val)

        return redirect(url_for("api.index"))

class TenantSmsStatus(Resource):
    def get(self):
        pass
    def post(self):
        tenantid = request.form.get("tenantid")
        status = request.form.get("sms_status")

        tenant_obj = TenantOp.fetch_tenant_by_id(tenantid)
        bool_val = get_bool(status)

        TenantOp.update_can_receive_sms(tenant_obj,bool_val)

        return redirect(url_for("api.index"))

class SmsDelivery(Resource):
    def post(self):
        my_data=request.form.to_dict(flat=True)
        print("Delivery status >>>>>>",my_data)
        smsid = my_data["id"]
        status = my_data["status"]

        if status == "Failed":
            try:
                status = my_data["failureReason"]
            except:
                status = "unknown"

        payment_obj = PaymentOp.fetch_payment_by_smsid(smsid)
        invoice_obj = MonthlyChargeOp.fetch_monthlycharge_by_smsid(smsid)
        reading_obj = MeterReadingOp.fetch_meterreading_by_smsid(smsid)

        if payment_obj:
            try:
                print("Found payment of ",payment_obj.tenant.name,"Message status>>",status)
            except:
                print("Found payment of ",payment_obj.ptenant.name,"Message status>>",status)

            PaymentOp.update_sms_status(payment_obj,status)
            db.session.expire(payment_obj)
            if payment_obj.sms_status == "UserInBlackList" or payment_obj.sms_status == "AbsentSubscriber":
                PaymentOp.update_sms_status(payment_obj,"Success-mb")

                if payment_obj.ref_number != "N/A" and payment_obj.ref_number:
                    reference = f'#{payment_obj.ref_number}'
                else:
                    reference = f'#{payment_obj.id}'

                if payment_obj.ptenant:
                    tenant_obj = payment_obj.ptenant
                else:
                    tenant_obj = payment_obj.tenant
                prop_obj = payment_obj.apartment

                paid = f'KES {payment_obj.amount:,.0f}'

                if tenant_obj.balance < 0:
                    bal = tenant_obj.balance * -1
                    running_bal = (f"Advance: KES {bal:,.0f}")
                else:
                    running_bal = (f"Balance: KES {tenant_obj.balance:,.0f}")

                receipt = f"Receipt: https://kiotapay.com/r/{payment_obj.rand_id}"

                co = payment_obj.apartment.company
                raw_rem_sms =co.remainingsms
                str_co = co.name

                tele = tenant_obj.phone
                name = tenant_obj.name
                fname = fname_extracter(name)
                if not fname:
                    fname = name

                recipient = [sms_phone_number_formatter(co.sphone)] if co.sphone else ["+254716674695"]

                # txt = f"Failed delivery to {tenant_obj.name} of {tele} ({prop_obj.name}). \n\nRental payment Ref-{reference} Confirmed. \nDear {fname}, we have received sum of Kshs. {payment_obj.amount}. \n{running_bal} \n\n~{str_co}."
                txt = f"Failed delivery to {tenant_obj.name} of {tele} ({prop_obj.name}). \n\nRental payment Ref {reference}, sum of {paid} confirmed. \n{running_bal} \n\n{receipt} \n\n~{str_co}."

                response = sms.send(txt, recipient ,sender)

                resp = response["SMSMessageData"]["Recipients"][0]
                raw_cost = resp["cost"]
                rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                CompanyOp.set_rem_quota(co,rem_sms)


        elif invoice_obj:
            try:
                print("Found invoice of ",invoice_obj.tenant.name,"Message status>>",status)
            except:
                print("Found invoice of ",invoice_obj.ptenant.name,"Message status>>",status)

            MonthlyChargeOp.update_sms_status(invoice_obj,status)

            db.session.expire(invoice_obj)
            if invoice_obj.sms_invoice == "UserInBlackList" or invoice_obj.sms_invoice == "AbsentSubscriber":
                MonthlyChargeOp.update_sms_status(invoice_obj,"success-alt")

                if invoice_obj.ptenant:
                    tenant = invoice_obj.ptenant
                else:
                    tenant = invoice_obj.tenant

                prop_obj = invoice_obj.apartment
                billing_period = get_billing_period(prop_obj)

                co = invoice_obj.apartment.company
                str_co = co.name

                tele = tenant.phone
                name = tenant.name
                fname = fname_extracter(name)
                if not fname:
                    fname = name

                sibling_water_bill = fetch_current_billing_period_readings(prop_obj.billing_period,invoice_obj.house.meter_readings)

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

                        standing_charge = invoice_obj.house.housecode.watercharge
                        if standing_charge:
                            amount += standing_charge

                    smslastreading = (f"{wbill.last_reading} ")
                    smscurrentreading = (f"{wbill.reading} ")
                    smsunits = (f"{wbill.units} ")
                    smsstd = f"Standing charge: Kes {standing_charge}" if invoice_obj.house.housecode.watercharge else ""
                    smsbill = (f"Kes {amount:,} ")

                    wmessage = f"\n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \n{smsstd} \nWater: {smsbill}"
                else:
                    wmessage = ""

                arrears = invoice_obj.arrears

                calculated_total = 0.0
                if invoice_obj.paid_amount and arrears > 0:
                    if arrears <= invoice_obj.paid_amount:
                        calculated_total = invoice_obj.total_bill - arrears
                        arrears = 0.0
                    else:
                        arrears = invoice_obj.arrears - invoice_obj.paid_amount
                        calculated_total = invoice_obj.total_bill - invoice_obj.paid_amount

                smsrent = f"\n\nRent:{invoice_obj.rent:,}," if invoice_obj.rent else ""

                if wmessage:
                    smswater = wmessage
                else:
                    smswater = f"\nWater:{invoice_obj.water}," if invoice_obj.water else ""

                if invoice_obj.house.payment_bankacc:
                    bankdetails = f'\n\nBank: {invoice_obj.house.payment_bank} \nAcc: {invoice_obj.house.payment_bankacc}'
                elif prop_obj.payment_bank == "PayBill":
                    prop_name = prop_obj.name.split(" ")[0]
                    bankdetails = f'\n\n {prop_obj.payment_bank}: {prop_obj.payment_bankacc} \nAcc: {prop_name.lower()}/{invoice_obj.house.name}'
                elif prop_obj.payment_bank:
                    bankdetails = f'\n\nBank: {prop_obj.payment_bank} \nAcc: {prop_obj.payment_bankacc}'
                else:
                    bankdetails = ""

                smsgarb = f"\nGarbage:{invoice_obj.garbage}," if invoice_obj.garbage else ""
                smssec = f"\nSecurity:{invoice_obj.security}," if invoice_obj.security else ""
                smselec = f"\nElectricity:{invoice_obj.electricity}," if invoice_obj.electricity else ""
                smsdep = f"\nDeposit:{invoice_obj.deposit}" if invoice_obj.deposit else ""
                smsarrears = f"\nArrears:{invoice_obj.arrears}" if invoice_obj.arrears else ""
                smsfine = f"\nFine:{invoice_obj.penalty}" if invoice_obj.penalty else ""
                # smstotal = (f"{invoice_obj.total_bill:,.1f}")
                smstotal = (f"{invoice_obj.total_bill:,.1f}") if not calculated_total else (f"{calculated_total:,.1f}")
                bankdetails = bankdetails


                raw_rem_sms =co.remainingsms


                tele = tenant.phone
                str_month = get_str_month(billing_period.month)

                try:
                    recipient = [sms_phone_number_formatter(co.sphone)] if co.sphone else ["+254716674695"]

                    if arrears < 0.0:
                        bbf = -1 * arrears
                        sms_bbf = (f"{bbf:,}")
                        message = f"Failed delivery to {tenant.name} of {tele} ({prop_obj.name}). \n\nDear {fname}, your {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smselec} {smsdep} {smsfine} \nPaid: {sms_bbf} \nTotal due: {smstotal} {bankdetails} \n\n ~ {str_co}."
                    else:
                        message = f"Failed delivery to {tenant.name} of {tele} ({prop_obj.name}). \n\nDear {fname}, your {str_month} bill is as follows; {smsrent} {smswater} \n {smsgarb} {smssec} {smselec} {smsdep} {smsfine} {smsarrears} \nTotal due: {smstotal} {bankdetails} \n\n ~ {str_co}."

                    response = sms.send(message, recipient, sender)

                    resp = response["SMSMessageData"]["Recipients"][0]
                    raw_cost = resp["cost"]
                    rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                    CompanyOp.set_rem_quota(co,rem_sms)

                except Exception as e:
                    print(f"Houston, we have a problem {e}")

        elif reading_obj:
            print("Found reading of ",reading_obj.house.name,"Message status>>",status)
            MeterReadingOp.update_sms_status(reading_obj,status)

            db.session.expire(reading_obj)
            if reading_obj.sms_invoice == "UserInBlackList" or reading_obj.sms_invoice == "AbsentSubscriber":
                MeterReadingOp.update_sms_status(reading_obj,"success-alt")

                house = reading_obj.house
                tenant = check_occupancy(house)[1]
                amount = 0.0

                co = reading_obj.apartment.company
                str_co = co.name

                billing_period = get_billing_period(reading_obj.apartment.id)

                if reading_obj.charged:
                    charge_obj = ChargeOp.fetch_charge_by_reading_id(reading_obj.id)
                    amount = charge_obj.amount

                    standing_charge = house.housecode.watercharge
                    if standing_charge:
                        amount += standing_charge

                smslastreading = (f"{reading_obj.last_reading} ")
                smscurrentreading = (f"{reading_obj.reading} ")
                smsunits = (f"{reading_obj.units} ")
                smsstd = f"Standing charge: Kes {standing_charge}" if house.housecode.watercharge else ""
                smsbill = (f"Kes {amount:,} ")

                raw_rem_sms =co.remainingsms

                tele = tenant.phone if not isinstance(tenant, str) else ""
                tenantname = tenant.name if not isinstance(tenant, str) else reading_obj.house.name
                prop_obj = reading_obj.apartment

                str_month = get_str_month(billing_period.month)
                try:
                    recipient = [sms_phone_number_formatter(co.sphone)] if co.sphone else ["+254716674695"]

                    message = f"Failed delivery to {tenantname} of {tele} ({prop_obj.name}). \n\nDear {tenantname}, \nYour updated {str_month} water bill reading is as follows: \n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \n{smsstd} \nBill: {smsbill} \n\n~{str_co}"

                    # message = f"Dear {tenant.name}, \nYour {str_month} water bill reading is as follows: \n\nLast reading: {smslastreading} \nCurrent reading: {smscurrentreading} \nUnits: {smsunits} \n{smsstd} \nBill: {smsbill} \n\n~{str_co}"
                    response = sms.send(message, recipient, sender)

                    resp = response["SMSMessageData"]["Recipients"][0]
                    raw_cost = resp["cost"]
                    rem_sms = calculate_sms_cost(raw_rem_sms,raw_cost)
                    CompanyOp.set_rem_quota(co,rem_sms)

                except Exception as e:
                    print(f"Houston, we have a problem {e}")
        else:
            print("Nothing found for this particular message")


class AddTenant(Resource):
    """class"""
    @login_required
    def get(self):
        target = request.args.get("target")
        raw_checkin = request.args.get("date")

        propid = request.args.get("propid")
        prop_id = get_identifier(propid)

        prop = ApartmentOp.fetch_apartment_by_id(prop_id)
        
        if target == "reps":
            co_users = prop.company.reps
            return render_template('ajax_multivariable.html',items=sort_items(co_users),placeholder="select agent")


        if target == "plots":
            house_list = filter_out_owned_houses(prop.name)
            return render_template('ajax_multivariable.html',items=sort_items(house_list),placeholder="select unit")

        ptenant_id = request.args.get('tenant_id')
        ptenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(ptenant_id))
        house_obj = ptenant_obj.house

        if target == "client details":

            print(ptenant_obj.classtype,"<<<<<<<<<<<<<<<<<<<<<<")

            if ptenant_obj.classtype.lower() == "shareholder":
                ng = house_obj.housecode.listprice * 0.95
            else:
                ng = house_obj.housecode.listprice

            return render_template('ajax_client_details.html',client=ptenant_obj.name,plot=house_obj,mp=f'{ng:,.1f}')

        if target == "client discount":
            discount = request.args.get("discount")
            if discount == "true":
                ng = house_obj.housecode.listprice * 0.95
            else:
                ng = house_obj.housecode.listprice

            return render_template('ajax_discount.html',mp=f'{ng:,.1f}')

        elif target == "negotiated details":
            if not raw_checkin:
                # return "date not specified"
                abort(403)
            else:
                str_checkin = date_formatter_alt(raw_checkin)
                instalment_date = parse(str_checkin)

                # instalment_date = datenow + relativedelta(months=1)

                # project_end_date = generate_start_date(7,2023)
                project_end_date = instalment_date + relativedelta(months=15)

                print("START:", instalment_date.date())
                print("ENDING:", project_end_date.date())

                # diff = relativedelta(project_date, datenow)
                # delta = relativedelta(project_end_date, instalment_date)
                # months = delta.months + (delta.years * 12)
                months = 15

                # print("MONTHS",months)

                negprice = ptenant_obj.negotiated_price
                deposit = negprice * 0.3
                # deposit = negprice * 0.1

                # deposit2 = negprice * 0.2

                bal = negprice - deposit

                try:
                    instalment = f"{(bal/months):,.0f}"
                except:
                    instalment = 0.0

            return render_template(
                'ajax_client_details_two.html',
                client=ptenant_obj.name,
                plot=house_obj,
                mp=f"{ptenant_obj.negotiated_price:,.1f}",
                deposit=deposit,
                num_mi=months,
                mi=instalment)  

    def post(self):
        target = request.form.get('target')
        prop_id = request.form.get('propid')


        apartment_id = get_identifier(prop_id)

        prop = ApartmentOp.fetch_apartment_by_id(apartment_id)

        if target == "excelupload":
            file = request.files.get('file')
            ttype = request.form.get('ttype')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            if sheet:
                if ttype == 'clients':
                    if len(sheet.row_values(1)) != 8:
                        data_format_error = True
                else:
                    if len(sheet.row_values(1)) != 5:
                        data_format_error = True

            try:
                if data_format_error:
                    
                    nonexistent_item = sheet.row_values(1)[1000000]

                for row in rows:
                    tenantname = sheet.row_values(row)[1]

                    try:
                        tenanthouse = str(int(sheet.row_values(row)[0]) if sheet.row_values(row)[0] else "" )
                    except:
                        tenanthouse = sheet.row_values(row)[0] if sheet.row_values(row)[0] else ""

                    raw_mobile = sheet.row_values(row)[2]

                    print("STARTING...TELL:",raw_mobile,"Type:",type(raw_mobile))

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

                    # try:
                    #     telle = str(int(sheet.row_values(row)[2]))
                    # except:
                    #     telle = sheet.row_values(row)[2]

                    # if telle:
                    #     telle2 = telle.replace(" ", "")
                    #     strtelle = str(int(telle2))
                    # else:
                    #     strtelle = ""

                    # tenantphone = "0" + strtelle
                    
                    tenantemail = sheet.row_values(row)[3]
                    try:
                        tenantnatid = str(int(sheet.row_values(row)[4]) if sheet.row_values(row)[4] else "" )
                    except:
                        tenantnatid = ""

                    classtype = sheet.row_values(row)[5]
                    rep = sheet.row_values(row)[6]

                        
                    migrate = "True"

                    if not migrate:
                        migrate = "False"
                    bool_migrate = return_bool(migrate)

                    similar = False

                    tenant_house = tenanthouse.upper()
                    house_obj = get_specific_house_obj(apartment_id,tenant_house)
                    if not house_obj:
                        print("Specified house doesnt exist: ",tenant_house)
                        continue
                    else:
                        house_id = house_obj.id

                    if ttype:
                        if not tenantname:
                            continue

                    if not ttype:

                        occupancy = check_occupancy(house_obj)
                    
                        if occupancy[0] == "occupied":
                            print("Specified house occupied: ",tenant_house)
                            continue

                        if not tenantnatid:
                            tenantnatid = nationalid_generator()
                            check_dup = TenantOp.fetch_tenant_by_nat_id(tenantnatid)
                            nat_id = nationalid_generator() if check_dup else tenantnatid
                        else:
                            nat_id = tenantnatid

                        if tenantname:
                            if tenantname.lower() == "vacant":
                                print(tenantname,"name is not allowed")
                                similar = True
                        else:
                            continue

                        tenants = prop.tenants
                        for tenant in tenants:
                            if tenant.name.lower() == tenantname.lower() and tenantphone == "0":
                                print("SIMILAR TENANT EXISTS: ",tenant.name,tenantname)
                                similar = True

                        if similar:
                            continue

                        present = TenantOp.fetch_tenant_by_nat_id(nat_id)
                        if present:
                            print("SIMILAR NATIONAL ID EXISTS: ",nat_id)
                            continue

                        if tenantemail:
                            present2 = TenantOp.fetch_tenant_by_email(tenantemail)
                            present3 = UserOp.fetch_user_by_email(tenantemail)
                            if present2 or present3:
                                print("SIMILAR EMAIL EXISTS: ",tenantemail)
                                continue

                        if tenantphone and tenantphone != "0":
                            present4 = TenantOp.fetch_tenant_by_tel(tenantphone)
                            if present4:
                                print("SIMILAR MOBILE NUMBER EXISTS: ",tenantphone,present4,"House",present4.house_allocated,"Apartment",present4.apartment)
                                continue

                    else:
                        nat_id = nationalid_generator() if not tenantnatid else tenantnatid
                        
                    created_by = current_user.id

                    if ttype:

                        if house_obj.owner:
                            continue
                        

                        ptenant_obj = PermanentTenantOp(tenantname,tenantphone,nat_id,tenantemail,0.0,house_obj.id,apartment_id,created_by)
                        ptenant_obj.save()

                        print("BEFORE UPDATING",ptenant_obj.resident_type)
                        print("BEFORE UPDATING T",ptenant_obj.tenant_type)

                        rep_id = None

                        if ttype == "clients":
                            PermanentTenantOp.update_resident_type(ptenant_obj,"normal")
                            print("AFTER UPDATING",ptenant_obj.resident_type)
                            print("AFTER UPDATING T",ptenant_obj.tenant_type)


                            if rep:
                                # username = username_extracter(rep)
                                try:
                                    rep_id = SalesRepOp.fetch_rep_by_name(rep).id
                                except:
                                    print("REP NOT FOUND FOR", rep)
                                    rep_id = None
                            else:
                                rep_id = None


                            if classtype:

                                PermanentTenantOp.update_classtype(ptenant_obj,classtype)
                                if classtype.lower() == "shareholder":
                                    pass
                                else:
                                    PermanentTenantOp.update_rep_id(ptenant_obj,rep_id)


                            PermanentTenantOp.update_status(ptenant_obj,"proposal")

                            HouseOp.update_status(house_obj,"booked")

                    else:

                        tenant_obj = TenantOp(tenantname,tenantphone,nat_id,tenantemail,0.0,apartment_id,created_by)
                        tenant_obj.save()

                    # tenant_house = tenanthouse.upper()
                    # house_obj = get_specific_house_obj(apartment_id,tenant_house)
                    # if not house_obj:
                    #     print("Specified house doesnt exist: ",tenant_house)
                    #     continue
                    # else:
                    #     house_id = house_obj.id

                    # occupancy = check_occupancy(house_obj)
                    if not ttype:

                        if occupancy[0] == "occupied":
                            print("Specified house occupied: ",tenant_house)
                            continue

                        else:
                            house_id = house_obj.id
                            tenant_id = tenant_obj.id
                            user_id = current_user.id

                            allocate_tenant_obj = AllocateTenantOp(apartment_id,house_id,tenant_id,user_id,description=None)
                            allocate_tenant_obj.save()
                            TenantOp.update_status(tenant_obj,"Resident")
                            if bool_migrate:
                                TenantOp.update_residency(tenant_obj,"Old")
                            else:
                                TenantOp.update_residency(tenant_obj,"New")


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

        elif target == "excelmobileupload":
            file = request.files.get('file')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            if sheet:
                if len(sheet.row_values(1)) != 3:
                    data_format_error = True

            try:
                if data_format_error:
                    """introduce an error"""
                    nonexistent_item = sheet.row_values(1)[1000000]

                for row in rows:
                    
                    try:
                        tenanthouse = str(int(sheet.row_values(row)[0]) if sheet.row_values(row)[0] else "" )
                    except:
                        tenanthouse = sheet.row_values(row)[0] if sheet.row_values(row)[0] else ""

                    raw_mobile = sheet.row_values(row)[1]

                    print("STARTING...TELL:",raw_mobile,"Type:",type(raw_mobile))

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
                
                    tenant_house = tenanthouse.upper()
                    house_obj = get_specific_house_obj(apartment_id,tenant_house)
                    if not house_obj:
                        print("Specified house doesnt exist: ",tenant_house)
                        continue
                    else:
                        house_id = house_obj.id

                    occupancy = check_occupancy(house_obj)

                    if occupancy[0] == "occupied":
                        tenant = occupancy[1]
                    else:
                        tenant = None
                        continue

                    
                    if tenantphone and tenantphone != "0":
                        present4 = TenantOp.fetch_tenant_by_tel(tenantphone)
                        if present4:
                            print("SIMILAR MOBILE NUMBER EXISTS: ",present4,"of",tenantphone)
                            # TenantOp.delete(present4)
                            continue
                        
                        created_by = current_user.id

                        if tenant:
                            print("FNDHBVSDJBVHFVJFBVHDBVHBVJB::::",tenant)
                            if len(tenant.phone)<2:
                                print("Updating...",tenant)
                                TenantOp.update_phone(tenant,tenantphone)
 
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


        elif target == "exceldepositupload":
            file = request.files.get('file')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            if sheet:
                if len(sheet.row_values(1)) != 7:
                    data_format_error = True
            try:
                if data_format_error:
                    nonexistent_item = sheet.row_values(1)[1000000]

                dict_array = []

                for row in rows:
                    dict_obj = {
                    "unit":sheet.row_values(row)[0],
                    "rentdep":sheet.row_values(row)[1],
                    "waterdep":sheet.row_values(row)[2],
                    "elecdep":sheet.row_values(row)[3],
                    "otherdep":sheet.row_values(row)[4],
                    "datepaid":sheet.row_values(row)[5],
                    "status":sheet.row_values(row)[6],
                    }

                    dict_array.append(dict_obj)

                lfile2("finish point: rows",len(dict_array))

                uploadsjob = q.enqueue_call(
                    func=read_deposits_excel, args=(dict_array,apartment_id,current_user.id,), result_ttl=5000
                )

                lfile("finish point: rows",len(dict_array))

                return '<span class="text-success">Upload successful</span>'

            # if sheet:
            #     if len(sheet.row_values(1)) != 6:
            #         data_format_error = True

            # try:
            #     if data_format_error:
            #         """introduce an error"""
            #         nonexistent_item = sheet.row_values(1)[1000000]

            #     for row in rows:
                    
            #         try:
            #             tenanthouse = str(int(sheet.row_values(row)[0]) if sheet.row_values(row)[0] else "" )
            #         except:
            #             tenanthouse = sheet.row_values(row)[0] if sheet.row_values(row)[0] else ""

            #         try:
            #             deposit = float(int(sheet.row_values(row)[1]) if sheet.row_values(row)[1] else 0.0 )
            #         except:
            #             print(tenanthouse,"deposit failing")
            #             deposit = 0.0

            #         print("STARTING...",deposit,"Type:",type(deposit))

            #         tenant_house = tenanthouse.upper()

            #         house_obj = get_specific_house_obj(apartment_id,tenant_house)
            #         if not house_obj:
            #             print("Specified house doesnt exist: ",tenant_house)
            #             continue
            #         else:
            #             house_id = house_obj.id

            #         occupancy = check_occupancy(house_obj)

            #         if occupancy[0] == "occupied":
            #             tenant = occupancy[1]
            #         else:
            #             tenant = None
            #             continue
                    
            #         if tenant:
            #             print("Updating...",tenant)
            #             TenantOp.update_deposit(tenant,deposit)
 
            #     return '<span class="text-success">Upload successful</span>'

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

            name = request.form.get('name')
            if not name:
                fname = request.form.get('fname')
                oname = request.form.get('oname')
                sname = request.form.get('sname')

                try:
                    name = fname + oname + sname
                except:
                    name = fname

            phone = request.form.get('tel')
            national_id = request.form.get('national_id')
            email = request.form.get('email')
            existing_arrears = request.form.get('arr')
            house_num = request.form.get('house')#auto populated dropdown

            migrate = request.form.get('migrate')#checkbox
            ttype = request.form.get('ttype')
            target = request.form.get('target')
            classtype=request.form.get('classtype')
            rep = request.form.get("rep")

            if rep:
                rep_id = SalesRepOp.fetch_rep_by_username(rep).id
            else:
                rep_id = None


            try:
                created_by = current_user.id
            except:
                created_by = request.form.get('current_user')

            try:
                float_arrears=float(existing_arrears)
            except:
                float_arrears=0.0

            if not migrate:
                migrate = "False"
            bool_migrate = return_bool_alt(migrate)

            if not national_id:
                natid = nationalid_generator()
                check_dup = TenantOp.fetch_tenant_by_nat_id(natid)
                nat_id = nationalid_generator() if check_dup else natid
            else:
                nat_id = national_id


            if email:
                present2 = TenantOp.fetch_tenant_by_email(email)
                # present3 = UserOp.fetch_user_by_email(email)
                present3 = None

                # if present2 or present3:
                #     msg="Email taken, use another email or leave blank"
                #     return render_template('ajaxghosthouse.html',alert=msg)

            present = TenantOp.fetch_tenant_by_nat_id(national_id)
            if present:
                msg = "Tenant of similar national id exists"
                return render_template('ajaxghosthouse.html',alert=msg)

            if ttype != "tenant":
                if not house_num:
                    return render_template('ajaxghosthouse.html',alert="select house first")

                house_obj = get_specific_house_obj(apartment_id,house_num)

                ptenant_obj = PermanentTenantOp(name,phone,nat_id,email,float_arrears,house_obj.id,apartment_id,created_by)
                ptenant_obj.save()

                if target == "purchasing":


                    PermanentTenantOp.update_classtype(ptenant_obj,classtype)

                    if classtype == "shareholder":
                        pass
                    else:
                        PermanentTenantOp.update_rep_id(ptenant_obj,rep_id)

                    PermanentTenantOp.update_status(ptenant_obj,"proposal")

                    HouseOp.update_status(house_obj,"booked")
                
                msg = "Resident registered successfully"

            else:

                tenant_obj = TenantOp(name,phone,nat_id,email,float_arrears,apartment_id,created_by)
                tenant_obj.save()

                if house_num:
                    house_list = filter_out_occupied_houses(tenant_obj.apartment.name)

                    house_obj = get_specific_house_obj_alt(house_list,house_num)
                    
                    allocs = tenant_obj.house_allocated
                    if allocs:
                        if tenant_obj.multiple_houses:
                            pass
                        else:
                            for i in allocs:
                                AllocateTenantOp.delete(i)

                    house_id = house_obj.id
                    tenant_id = tenant_obj.id

                    allocate_tenant_obj = AllocateTenantOp(apartment_id,house_id,tenant_id,created_by,description=None)
                    allocate_tenant_obj.save()
                    TenantOp.update_status(tenant_obj,"Resident")
                    if bool_migrate:
                        TenantOp.update_residency(tenant_obj,"Old")
                    else:
                        TenantOp.update_residency(tenant_obj,"New")
            
                msg = "Tenant added successfully"
            return msg + proceed

class Deal(Resource):
    def get(self):
        pass
    def post(self):
        ptenant_id = request.form.get('tenant_id')

        target = request.form.get('target')

        alloc = PermanentTenantOp.fetch_tenant_by_id(get_identifier(ptenant_id))

        print("getting here")


        if target=="negotiations":
            negprice = validate_input(request.form.get('negprice'))
            deposit = validate_input(request.form.get('deposit'))

            # deposit2 = validate_input(request.form.get('deposit2'))
            # mi = validate_input(request.form.get('mi'))
            # num_mi = validate_input(request.form.get('num_mi'))

            PermanentTenantOp.update_status(alloc,"contracts")

            PermanentTenantOp.update_payment_plan(alloc,negprice,"partial",deposit,0.0,0,0,"","")

            msg = "Client details updated"
            return msg + proceed
        else:
            # path = f"app/temp/litala.pdf"
            mi = validate_input(request.form.get('mi'))
            num_mi = validate_input(request.form.get('num_mi'))

            raw_checkin = request.form.get('date')

            if not raw_checkin:
                # return "date not specified"
                abort(403)
            else:
                str_checkin = date_formatter_alt(raw_checkin)
                bookedon = parse(str_checkin)


            path = request.files.get('file')

            if path:
                filename = f"app/temp/contracts.pdf"

                path.save(filename,buffer_size=16384)
            
                res = Cloud.uploader.upload(filename)
                print(res['secure_url'])

                pdf2img = res['secure_url'][:-4]
                img = pdf2img + ".png"

                os.remove(filename)
            else:
                img = ""

            PermanentTenantOp.update_payment_plan(alloc,0.0,"partial",0.0,0.0,mi,num_mi,bookedon,bookedon)

            plot = alloc.house
            PermanentTenantOp.upload_contracts(alloc,img,"")
            HouseOp.update_status(plot,"sold")
            PermanentTenantOp.update_status(alloc,"closed")

            # if alloc.plan == "partial":
            #     PermanentTenantOp.update_balance(alloc,alloc.negotiated_price)
            #     # balance = alloc[2].deposit + alloc[2].instalment
            #     # TenantOp.update_balance(tenant_obj,balance)
            # else:
            #     PermanentTenantOp.update_balance(alloc,alloc.negotiated_price)

            # bill = alloc.instalment + alloc.deposit

            # billplan = MonthlyChargeTwoOp(alloc.negotiated_price,alloc.deposit,30,30,alloc.num_instalment,alloc.num_instalment,1,alloc.instalment,0,bill,0,0,alloc.apartment.id,plot.id,alloc.id,current_user.id)
            # billplan.save()

            # MonthlyChargeTwoOp.update_cumulative_balance(billplan,alloc.negotiated_price)
            # MonthlyChargeTwoOp.update_balance(billplan,bill)

            return render_template('ajaxproceed.html',alert="success")

class UpdateTenant(Resource):
    """class"""
    @login_required
    def get(self):

        target = request.args.get("target")
        if target == "nonselfupdate":
            tenantid = request.args.get("tenantid")
            identity = get_identifier(tenantid)
            if tenantid.startswith("pedit"):
                tenant = PermanentTenantOp.fetch_tenant_by_id(identity)
            else:
                tenant = TenantOp.fetch_tenant_by_id(identity)
                db.session.expire(tenant)
                if tenant.multiple_houses == None:
                    TenantOp.update_tenant(tenant,"","","","","","","",False,"")
            return render_template('ajax_dynamic_tenant_form.html',tenant=tenant)

        if target == "tenant sms":

            tenantid = request.args.get("tenantid")
            identity = get_identifier(tenantid)
            if tenantid.startswith("pedit"):
                tenant = PermanentTenantOp.fetch_tenant_by_id(identity)
            else:
                tenant = TenantOp.fetch_tenant_by_id(identity)

            return "yes" if tenant.sms else "no"
        
        #scan_for_tenant_user
        if str(current_user.user_group) == "Tenant":
            tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
            tenant_id = "edit" + str(tenant_obj.id)
            return Response(render_template('self_update_tenant.html',tenant_id=tenant_id,tenant=tenant_obj,name=current_user.name))

    def post(self):
        tenant_id = request.form.get('tenant_id')

        uid = request.form.get("uid")
        name = request.form.get("name")
        phone = request.form.get('tel')
        national_id = request.form.get('national_id')
        email = request.form.get('email')
        arr = request.form.get('arr')
        fine = request.form.get('fine')
        multi = request.form.get('multi')
        smsaccess = request.form.get('sms')


        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')

        target = request.form.get('target')


        modified_by = current_user.id

        if not multi:
            multi = "null"
        bool_multi = return_bool(multi)

        if not smsaccess:
            smsaccess = "null"
        bool_sms = return_bool_alt_alt(smsaccess)

        identity = get_identifier(tenant_id)
        if tenant_id.startswith("pedit"):
            update_tenant = PermanentTenantOp.fetch_tenant_by_id(identity)
        else:
            update_tenant = TenantOp.fetch_tenant_by_id(identity)

        print(update_tenant,"hererer it issssssssssss",">>>",tenant_id,"<<<")
            
        if target == "tenant name":
            return update_tenant.name

        if target == "delete" and not tenant_id.startswith("pedit"):
            if check_house_occupied(update_tenant)[0] == "Resident":
                pass
            else:
                TenantOp.delete(update_tenant)

        ###########################################################
        
        if email:
            present1 = TenantOp.fetch_tenant_by_email(email)
            present2 = UserOp.fetch_user_by_email(email)
            # if present1 or present2:
            #     msg="Email taken, use another email or leave blank"
            #     # return render_template('ajaxghosthouse.html',alert=msg)

        if national_id:
            present3 = TenantOp.fetch_tenant_by_nat_id(national_id)
            present4 = TenantOp.fetch_tenant_by_nat_id(national_id)
            if present3 or present4:
                msg = "Tenant of similar national id exists"
                return render_template('ajaxghosthouse.html',alert=msg)

        if tenant_id.startswith("pedit"):
            PermanentTenantOp.update_tenant(update_tenant,uid,name,phone,email,national_id,arr,fine,bool_multi,modified_by)
        else:
            TenantOp.update_tenant(update_tenant,uid,name,phone,email,national_id,arr,fine,bool_multi,modified_by)
            TenantOp.update_can_receive_sms(update_tenant,bool_sms)

            tenant_user = UserOp.fetch_user_by_national_id(update_tenant.national_id)

            if tenant_user:
                if pass1 and pass2:
                    validate_pass = ValidatePass.validate_password(pass1,pass2)
                    if validate_pass=="no match":
                        password = None
                        # flash("Password update failed,not match","fail")
                    else:
                        password = pass1
                else:
                    password = None

                user_group_id = None
                company_id = None

                UserOp.update_user(tenant_user,name,phone,national_id,email,password,user_group_id,company_id,modified_by)
        
        msg='Tenant info updated.'
        
        return render_template('ajaxproceed.html',alert=msg)

class AllocateTenants(Resource):
    """class"""
    @login_required
    def get(self):
        pass
    
    @login_required
    def post(self):

        prop_id = request.form.get('propid')
        tenantid = request.form.get('tenant_id')
        house_num = request.form.get('house')#auto populated dropdown
        ttype = request.form.get('ttype')

        migrate = request.form.get('migrate')#checkbox

        target = request.form.get('target')

        if not migrate:
            migrate = "False"
        bool_migrate = return_bool(migrate)

        apartment_id = get_identifier(prop_id)
        tenant_id = get_identifier(tenantid)
        
        stored_apartment = ApartmentOp.fetch_apartment_by_id(apartment_id) if prop_id else None
        house_list = filter_out_occupied_houses(stored_apartment.name) if stored_apartment else None
        tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id) if tenant_id else None

        if target == "house options":
            return render_template('ajax_multivariable.html',items=sort_items(house_list),placeholder="select house")
        if target == "house options2":
            if ttype == "tenant":
                return render_template('ajax_multivariable.html',items=sort_items(house_list),placeholder="select house")
            else:
                house_list = [h for h in stored_apartment.houses if not h.owner]
                return render_template('ajax_multivariable.html',items=sort_items(house_list),placeholder="select house")

        if target == "tenant name":
            return tenant_obj.name

        #################################################################################

        house_obj = get_specific_house_obj_alt(house_list,house_num)

        ######################### PERFORM VALIDATIONS ###################################
        # import pdb; pdb.set_trace()
        occupancy = check_occupancy(house_obj)
        metered = fetch_active_meter(house_obj)
        ##################################################################################
        if target=="alerts" and ttype == "tenant":
            if occupancy[0] == "occupied":
                tenant = occupancy[1]
                msg = f"House occupied by : {tenant}, checkout current tenant to allocate"
                return render_template('ajaxghosthouse.html',alert=msg)
            elif not metered:
                msg = "House has no allocated meter"
                return render_template('ajaxwarning.html',alert=msg) 
            else:
                msg = "Ready to allocate"
                return render_template('ajaxproceed.html',alert=msg)
        ###################################################################################           

        else:
            if ttype == "tenant":
                allocs = tenant_obj.house_allocated
                if allocs:
                    if tenant_obj.multiple_houses:
                        pass
                    else:
                        for i in allocs:
                            AllocateTenantOp.delete(i)

                house_id = house_obj.id
                tenant_id = tenant_obj.id
                user_id = current_user.id

                allocate_tenant_obj = AllocateTenantOp(apartment_id,house_id,tenant_id,user_id,description=None)
                allocate_tenant_obj.save()
                TenantOp.update_status(tenant_obj,"Resident")
                if bool_migrate:
                    TenantOp.update_residency(tenant_obj,"Old")
                else:
                    TenantOp.update_residency(tenant_obj,"New")

                msg = f"Tenant {tenant_obj.name} has been allocated house {house_num} successfully"
            else:
                msg = f"{tenant_obj.name} has been allocated house {house_num} successfully"

        return render_template('ajaxproceed.html',alert=msg)

class TenantClearance(Resource):
    @login_required
    def get(self):
        pass

    @login_required
    def post(self):
        # stored_apartment = request.form.get('prop')#dropdown
        tenantid = request.form.get('tenant_id')
        discard_bill = request.form.get('discard_bill')
        pay_off_balance = request.form.get('pay_off_balance')
        ttype = request.form.get("ttype")
        runalert = request.form.get('runalert')
        target = request.form.get('target')

        tenant_id = get_identifier(tenantid)

        print("TTTTTTYYYYYYYYPPPPPPPEEEEEEEEEEEEEEEEEEEEEEEEE",ttype)

        if ttype == "owner" or ttype == "resident":
            tenant_obj = PermanentTenantOp.fetch_tenant_by_id(tenant_id)

            if target == "tenant name":
                return tenant_obj.name

            if not runalert:
                PermanentTenantOp.delete(tenant_obj)
                return proceed + "removed successfully"
                
            return proceed + "ready to remove"


        else:
            tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)

        if tenant_obj.multiple_houses:
            return "Cannot clear, tenant occupies multiple units"

        house_obj = check_house_occupied(tenant_obj)[1]

        checkbox = False
        checkboxtwo = False
        month = None
        msg_one = ""
        msg_two = ""
        msg_three = "Proceed to clear"
        target_bill = None

        if target == "tenant name":
            return tenant_obj.name

        if not house_obj:
            msg_two = "Tenant has been cleared already"
            return render_template('ajax_clearance.html',checkbox=checkbox,alert_one=msg_one,alert_two=msg_two,current_bill_month=month)

        prop_obj = house_obj.apartment
        billing_period = get_billing_period(prop_obj)
        present_day_period = datetime.datetime.now().day
        present_month_period = datetime.datetime.now().month
        bills = tenant_obj.monthly_charges

        balance = tenant_obj.balance
        if balance > 0.0:
            checkboxtwo = True
            msg_three = ""
            month = get_str_month(billing_period.month)
            msg_two = f"arrears of Kshs {balance}"

        for bill in bills:
            if bill.month == billing_period.month and bill.year == billing_period.year:
                target_bill = bill
                if present_day_period < 30 and present_month_period == billing_period.month:
                    month = get_str_month(billing_period.month)
                    checkbox = True
                    msg_three = ""
                    msg_one = f"{tenant_obj}'s {month} rent bill?,"

        
        if runalert:
            if msg_three:
                return render_template("ajaxproceed.html",alert=msg_three)
            return render_template('ajax_clearance.html',checkbox=checkbox,checkboxtwo=checkboxtwo,alert_one=msg_one,alert_two=msg_two,current_bill_month=month)
       
        bill_discard = get_bool(discard_bill)
        pay_off_balance_with_deposit = get_bool(pay_off_balance)
        vacate_period = billing_period
        
        if bill_discard:
            vacate_period = billing_period - relativedelta(months=1)
            
            deductions = house_obj.housecode.rentrate + house_obj.housecode.garbagerate + house_obj.housecode.securityrate

            # update_water = target_bill.water

            # update_rent = 0.0

            # update_garbage = 0.0

            # update_electricity = target_bill.electricity

            # update_security = 0.0

            # update_maintenance = target_bill.maintenance

            # update_penalty = target_bill.penalty

            # const_arrears = target_bill.arrears
            # const_deposit = target_bill.deposit if target_bill.deposit else 0.0
            # const_agreement = target_bill.agreement if target_bill.agreement else 0.0

            # total_amount = update_water+update_rent+update_garbage+update_electricity+update_security+update_maintenance+update_penalty+const_arrears+const_deposit+const_agreement #total amount is incremented only by updates
            # MonthlyChargeOp.update_monthly_charge(target_bill,update_water,update_rent,update_garbage,update_electricity,update_security,"null","null",update_maintenance,update_penalty,"null",total_amount,current_user.id)

            # bal = target_bill.balance
            # bal = bal - deductions #these are updates, if one has update, the rest are zeros
            # MonthlyChargeOp.update_balance(target_bill,bal)
            MonthlyChargeOp.delete(target_bill)

            all_charges = house_obj.charges

            for charge in all_charges:
                if charge.date.month == billing_period.month and charge.date.year == billing_period.year and not charge.reading_id:
                    ChargeOp.delete(charge)

            tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
            running_bal = tenant_obj.balance
            running_bal -= deductions
            TenantOp.update_balance(tenant_obj,running_bal)


        # pay off the balances using deposit
        deposit = house_obj.housecode.rentrate + house_obj.housecode.waterdep
        db.session.expire(tenant_obj)
        new_balance = tenant_obj.balance

        if pay_off_balance_with_deposit:

            if new_balance > 0.0:
                if new_balance < deposit:
                    amount_paid = new_balance
                    print("GREAAAAAAAAAAAAAAT<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                else:
                    print("NOMAAAAAAAAAAAAAAA>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    amount_paid = deposit
                    rem_dep_balance = new_balance - deposit # TO DO save the remaining balance for reference

                # payment_obj = PaymentOp("deposit deduction","N/A","N/A","Arrears",None,billing_period,new_balance,amount_paid,tenant_obj.apartment_id,house_obj.id,tenant_id,current_user.id)
                # payment_obj.save()
                #################################################################################################

                running_balance = tenant_obj.balance
                running_balance-=float(amount_paid)
                TenantOp.update_balance(tenant_obj,running_balance)
                # PaymentOp.update_balance(payment_obj,running_balance)

                monthly_charges = tenant_obj.monthly_charges
                specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,billing_period.month,billing_period.year)
                if specific_charge_obj:
                    bala = specific_charge_obj.balance
                    bala-=float(amount_paid)
                    MonthlyChargeOp.update_balance(specific_charge_obj,bala)

                    paid_amount = specific_charge_obj.paid_amount
                    cumulative_pay = paid_amount + float(amount_paid)
                    MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
                    MonthlyChargeOp.update_payment_date(specific_charge_obj,datetime.datetime.now())

        active_alloc = check_house_occupied(tenant_obj)[2]

        AllocateTenantOp.update_status(active_alloc,False,tenant_obj.balance,vacate_period,current_user.name)
        TenantOp.update_status(tenant_obj,"Vacated")

        msg = f"{tenant_obj} cleared successfully"

        return render_template('ajaxproceed.html',alert=msg)

class MeterRemoval(Resource):
    @login_required
    def get(self):
        # user_group = current_user.company_user_group
        # accessright = check_accessright(user_group,"allocate_tenant")
        # if accessright != True:
        #     return Response(render_template('noaccess.html',name=current_user.name))
        meter_id = request.args.get("meter_id")
        meterid = get_identifier(meter_id)
        meter_obj = MeterOp.fetch_meter_by_id(meterid)
        # last_reading = getlast_reading(meterid)
        house_obj = fetch_specific_metered_house(meter_obj)[0]

        if house_obj:
            return f'<span class="text-danger">Remove <span class="text-info">{meter_obj}</span> from <span class="text-info">{house_obj}</span>?</span>'
        else:
            return f'<span class="text-danger">Error!</span>'

    @login_required
    def post(self):

        meter_id = request.form.get("meter_id")
        meterid = get_identifier(meter_id)
        meter_obj = MeterOp.fetch_meter_by_id(meterid)
        last_reading = getlast_reading(meterid)
        house_obj = fetch_specific_metered_house(meter_obj)[0]
        if house_obj:
            active_alloc = fetch_specific_metered_house(meter_obj)[1]

            cleared_by = current_user.id

            AllocateMeterOp.update_status(active_alloc,False,cleared_by)
            MeterOp.update_initial_reading(meter_obj,last_reading)

            return f'<span class="text-success"><span class="text-info">{meter_obj}</span> removed from <span class="text-info">{house_obj}</span> successfully</span>'


class CreateMeter(Resource):
    """class"""
    @login_required
    def get(self):
        pass

    def post(self):
        target = request.form.get('target')

        apartment_id = request.form.get('propid')
        metertype = request.form.get('metertype')
        meter_num = request.form.get('meternum')
        serial_num = request.form.get('serialnum')
        if not serial_num:
            serial_num = "N/A"
        initial_reading = request.form.get('initreading')
        if not initial_reading:
            initial_reading = 0
        decitype = request.form.get('decitype')
        if not decitype:
            decitype = 0

        created_by =current_user.id


        if target == "excelupload":
            
            file = request.files.get('file')

            if file:
                processed_data = upload_handler(file,current_user)
            else:
                return '<span class=text-danger>Select file first</span>'

            rows,sheet = processed_data[0],processed_data[1]

            data_format_error = False

            print("fields>>>>>>>>>>>>>>",len(sheet.row_values(1)))

            if sheet:
                if len(sheet.row_values(1)) != 2:
                    data_format_error = True

            try:
                if data_format_error:
                    
                    nonexistent_item = sheet.row_values(1)[1000000]

                for row in rows:

                    try:
                        meter_num = str(int(sheet.row_values(row)[0]) if sheet.row_values(row)[0] else "NA" )
                    except:
                        meter_num = sheet.row_values(row)[0] if sheet.row_values(row)[0] else "NA"

                    initial_reading = int(sheet.row_values(row)[1]) if sheet.row_values(row)[1] else 0

                    metertype = "water"
                    raw_meter_no = meter_num.upper()
                    meter_no = "W-" + raw_meter_no

                    target_meter_obj = get_specific_meter_obj(apartment_id,meter_no)
                    house_obj = get_specific_house_obj(apartment_id,raw_meter_no)


                    if target_meter_obj:
                        print("Similar name exists")
                        continue

                    if not meter_num:
                        print("Meter Name NOT accepted")
                        continue

                    meter_obj = MeterOp(serial_num,meter_no,initial_reading,decitype,metertype,apartment_id,created_by)
                    meter_obj.save()


                    prop_obj = meter_obj.apartment
                    w_allocate = False
                    e_allocate = False

                    if house_obj:
                        if metertype == "water":
                            target_houses = filter_out_metered_houses(prop_obj.name)
                            if house_obj in target_houses:
                                w_allocate = True
                        else:
                            target_houses = filter_out_metered_houses_alt(prop_obj.name)
                            if house_obj in target_houses:
                                e_allocate = True

                    if w_allocate or e_allocate:

                        house_id = house_obj.id
                        user_id = current_user.id

                        allocate_meter_obj = AllocateMeterOp(apartment_id,house_id,meter_obj.id,user_id)
                        allocate_meter_obj.save()

                        meter_init_reading = meter_obj.initial_reading
                        reading_period = None

                        reading_obj = MeterReadingOp("initial reading",meter_init_reading,meter_init_reading,0,reading_period,apartment_id,house_id,meter_obj.id,user_id)
                        reading_obj.save()

                        # charge_type_id = get_charge_type_id("Water")
                        # charge_obj =  ChargeOp(charge_type_id,0.0,apartment_id,house_id,user_id,meter_id,reading_obj.id)#REFACTOR meter can be left out for rent,garbage and security
                        # charge_obj.save()

                        MeterReadingOp.update_charge_status(reading_obj,True)
                        
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


        runalert = request.form.get('runalert')

        if not metertype:
            msg = "Select metertype first"
            return render_template('ajaxghosthouse.html',alert=msg)

        raw_meter_no = meter_num.upper()
        if metertype == "water":
            meter_no = "W-" + raw_meter_no
        else:
            meter_no = "E-" + raw_meter_no 


        target_meter_obj = get_specific_meter_obj(apartment_id,meter_no)
        house_obj = get_specific_house_obj(apartment_id,raw_meter_no)


        if target_meter_obj:
            msg = "Similar name exists"
            return render_template('ajaxghosthouse.html',alert=msg)

        if runalert:
            if meter_num:
                msg = "Name accepted"
                return render_template('ajaxproceed.html',alert=msg)
            return render_template('ajaxghosthouse.html',alert="Meter number cannot be blank")

        meter_obj = MeterOp(serial_num,meter_no,initial_reading,decitype,metertype,apartment_id,created_by)
        meter_obj.save()
        msg = "Meter added successfully"

        prop_obj = meter_obj.apartment
        w_allocate = False
        e_allocate = False

        if house_obj:
            if metertype == "water":
                target_houses = filter_out_metered_houses(prop_obj.name)
                if house_obj in target_houses:
                    w_allocate = True
            else:
                target_houses = filter_out_metered_houses_alt(prop_obj.name)
                if house_obj in target_houses:
                    e_allocate = True

        if w_allocate or e_allocate:

            house_id = house_obj.id
            user_id = current_user.id

            allocate_meter_obj = AllocateMeterOp(apartment_id,house_id,meter_obj.id,user_id)
            allocate_meter_obj.save()

            meter_init_reading = meter_obj.initial_reading
            reading_period = None

            reading_obj = MeterReadingOp("initial reading",meter_init_reading,meter_init_reading,0,reading_period,apartment_id,house_id,meter_obj.id,user_id)
            reading_obj.save()

            # charge_type_id = get_charge_type_id("Water")
            # charge_obj =  ChargeOp(charge_type_id,0.0,apartment_id,house_id,user_id,meter_id,reading_obj.id)#REFACTOR meter can be left out for rent,garbage and security
            # charge_obj.save()

            MeterReadingOp.update_charge_status(reading_obj,True)

            msg = f"Meter added to {house_obj.name}"

        return render_template('ajaxproceed.html',alert=msg)

class UpdateMeter(Resource):
    def get(self):
        pass

    @login_required
    def post(self):
        meter_id = request.form.get('meter_id')
        reading = request.form.get('reading')
        decitype = request.form.get('decitype')
        # meter_no = request
        print(">>>>>>>>>>>>>>>>>>> deci",decitype)
        print(">>>>>>>>>>>>>>>>>>>",reading)
        if meter_id:
            meterid = get_identifier(meter_id)
            meter_obj = MeterOp.fetch_meter_by_id(meterid)
            MeterOp.update_initial_reading(meter_obj,reading)
            MeterOp.update_decitype(meter_obj,decitype)

            reading_objs = meter_obj.meter_readings
            for reading_obj in reading_objs:
                if reading_obj.description == "initial reading":
                    MeterReadingOp.update_curr(reading_obj,reading)


class AllocateMeters(Resource):
    """class"""

    @login_required
    def get(self):

        # user_group = current_user.company_user_group
        # accessright = check_accessright(user_group,"allocate_meter")
        # if accessright != True:
        #     return Response(render_template('noaccess.html',name=current_user.name))

        # form = MeterAllocForm()
        # apartment_list = fetch_all_apartments_by_user(current_user)
        # place_holder_item = '--Select Apartment--'
        # apartment_list.insert(0,place_holder_item)
        # form.apartment.choices = apartment_list

        # store = None

        # cur_apartment = f"{store}"
        # return Response(render_template(
        #     'wtmeteralloc.html',
        #     form=form,
        #     apartment_name=cur_apartment,
        #     logopath=logo(current_user.company)[0],
        #     mobilelogopath=logo(current_user.company)[1],
        #     name=current_user.name))
        pass
    
    @login_required
    def post(self):

        propid = request.form.get('propid')
        house = request.form.get('house')
        meterid = request.form.get('meterid')
        run = request.form.get('run')

        prop_obj = ApartmentOp.fetch_apartment_by_id(propid)

        meter_id = get_identifier(meterid)
        meter_obj = MeterOp.fetch_meter_by_id(meter_id)

        if meter_obj.metertype == "water":
            target_houses = filter_out_metered_houses(prop_obj.name)
        else:
            target_houses = filter_out_metered_houses_alt(prop_obj.name)

        if run == "houselist":
            return render_template('ajax_multivariable.html',items=target_houses,placeholder="select house")

        house_obj = None
        for i in target_houses:
            if str(i) == house:
                house_obj = i


        house_id = house_obj.id
        user_id = current_user.id

        allocate_meter_obj = AllocateMeterOp(propid,house_id,meter_id,user_id)
        allocate_meter_obj.save()

        meter_init_reading = meter_obj.initial_reading
        reading_period = None #TODO

        reading_obj = MeterReadingOp("initial reading",meter_init_reading,meter_init_reading,0,reading_period,propid,house_id,meter_id,user_id)
        reading_obj.save()

        # charge_type_id = get_charge_type_id("Water")
        # charge_obj =  ChargeOp(charge_type_id,0.0,apartment_id,house_id,user_id,meter_id,reading_obj.id)#REFACTOR meter can be left out for rent,garbage and security
        # charge_obj.save()

        MeterReadingOp.update_charge_status(reading_obj,True)

        return f"<span class='text-success'> {meter_obj.meter_number} allocated to {house} successfully </span>"




# class StandardRates(Resource):
#     """class"""
#     def get(self):
#         pass
#     def post(self):
#         apartment = request.form.get('apartmentsessionvariable2')
#         chargetype = request.form.get('chargetype2')
#         amount = request.form.get('standardamount')

#         apartment_id = get_apartment_id(apartment)
#         charge_type_id = get_charge_type_id(chargetype)
#         user_id = current_user.id
#         houses = houseauto(apartment_id)
        
#         for house in houses:
#             house_id = house.id
#             charged_house_list = ChargeDescOp.fetch_all_charge_descs_by_house_id(house_id)
#             if charged_house_list:
#                 str_charge_list = stringify_list_items(charged_house_list)

#                 if chargetype == "Electricity":
#                     if chargetype in str_charge_list:
#                         for item_obj in charged_house_list:
#                             if item_obj.charge_type_id == 5:
#                                 update_obj = item_obj

#                         ChargeDescOp.update_amount(update_obj,amount,user_id)

#                     else:
#                         charge_desc_obj = ChargeDescOp(charge_type_id,amount,apartment_id,house_id,user_id)
#                         charge_desc_obj.save()


#                 elif chargetype == "Security":
#                     if chargetype in str_charge_list:
#                         for item_obj in charged_house_list:
#                             if item_obj.charge_type_id == 6:
#                                 update_obj = item_obj

#                         ChargeDescOp.update_amount(update_obj,amount,user_id)

#                     else:
#                         charge_desc_obj = ChargeDescOp(charge_type_id,amount,apartment_id,house_id,user_id)
#                         charge_desc_obj.save()


#                 else:
#                     # this block captures garbage standard charges
#                     if chargetype in str_charge_list:
#                         for item_obj in charged_house_list:
#                             if item_obj.charge_type_id == 4:
#                                 update_obj = item_obj

#                         ChargeDescOp.update_amount(update_obj,amount,user_id)

#                     else:
#                         charge_desc_obj = ChargeDescOp(charge_type_id,amount,apartment_id,house_id,user_id)
#                         charge_desc_obj.save()

#             else:
#                 charge_desc_obj = ChargeDescOp(charge_type_id,amount,apartment_id,house_id,user_id)
#                 charge_desc_obj.save()

#         msg = "Standard rates set successfully"
#         flash(msg,"success")

#         form = ChargeDescForm()
#         apartment_list = fetch_all_apartments_by_user(current_user)
#         place_holder_item = '--Select Apartment--'
#         apartment_list.insert(0,place_holder_item)
#         form.apartment.choices = apartment_list

#         house_list = houseauto(apartment_id)
#         place_holder_item = '--Select House--'
#         house_list.insert(0,place_holder_item)
#         form.house.choices = house_list

#         charge_type_list = ChargeType.query.all()
#         rm_all = ChargeTypeOp.fetch_charge_type("All")
#         rm_water = ChargeTypeOp.fetch_charge_type("Water")
#         charge_type_list.remove(rm_all)
#         charge_type_list.remove(rm_water)

#         charge_type_list2 = charge_type_list.copy()
#         place_holder_item = '--Select Charge--'
#         charge_type_list2.insert(0,place_holder_item)
#         form.chargetype.choices = charge_type_list2

#         charge_type_list3 = charge_type_list.copy()
#         rm_rent = ChargeTypeOp.fetch_charge_type("Rent")
#         charge_type_list3.remove(rm_rent)

#         store = apartment
#         stored_h = None

#         cur_apartment = f"{store}"
#         cur_house = f"{stored_h}"

#         return Response(render_template(
#             'wtchargedesc.html',
#             form=form,
#             apartment_name=cur_apartment,
#             house_name=cur_house,
#             apartment_list=fetch_all_apartments_by_user(current_user),
#             chargetype_list = charge_type_list3,
#             logopath=logo(current_user.company)[0],
#             mobilelogopath=logo(current_user.company)[1],
#             name=current_user.name
#         ))

#############################################################################################  
class CaptureReading(Resource):
    """class"""

    @login_required
    def get(self):

        prop_id = request.args.get("propid")
        prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
        db.session.expire(prop_obj)
        billing_period = get_billing_period(ApartmentOp.fetch_apartment_by_id(prop_id))


        readperiod = request.args.get('readperiod')
        if readperiod == "current":
            readdate = billing_period
        else:
            readdate = generate_date(billing_period.month + 1,billing_period.year) #URGENT TODO , CHECK DATE AND TAKE CARE OF DECEMBER

        unread_units = len(filtered_house_list(prop_id,readdate))
        metered_units = len(filter_in_metered_houses(prop_obj.name))
        read_units = metered_units - unread_units

        return render_template("refresh_meter_overview.html",metered_units=metered_units,unread_units=unread_units,read_units=read_units)


    def post(self):

        apartment_id = request.form.get('propid')
        target = request.form.get('target')

        billing_period = get_billing_period(ApartmentOp.fetch_apartment_by_id(apartment_id))
        
        if target == "excelupload":

            file = request.files.get('file')


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

                dict_array = []

                for row in rows:
                                     
                    dict_obj = {
                    "house":sheet.row_values(row)[0],
                    "reading":sheet.row_values(row)[1]
                    }

                    dict_array.append(dict_obj)

                uploadsjob = q.enqueue_call(
                    func=read_water_excel, args=(dict_array,apartment_id,current_user.id,), result_ttl=5000
                )
                                
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




        house = request.form.get('house')
        reading = request.form.get('reading')

        readtype = request.form.get('readtype')
        run = request.form.get('run')

        prop = ApartmentOp.fetch_apartment_by_id(apartment_id)
        readperiod = request.form.get('readperiod')
        if readperiod == "current":
            readdate = billing_period
        else:
            readdate = generate_date(billing_period.month + 1,billing_period.year) #URGENT TODO , CHECK DATE AND TAKE CARE OF DECEMBER

        #################################################################################################
        if run == "houselist":
            house_list = filtered_house_list(apartment_id,readdate)
            return render_template('ajax_multivariable.html',items=sort_items(house_list),placeholder="select house")
        elif run == "houselist-alt":
            house_list = filtered_house_list_alt(apartment_id,readdate)
            return render_template('ajax_multivariable.html',items=sort_items(house_list),placeholder="select house")
        ##################################################################################################
        if not house:
            return '<div class="text-success center-btn"><i class="fas fa-info-circle mr-1 text-warning"></i>"Reading complete</div>'

        house_obj = get_specific_house_obj(apartment_id,house)
        house_id = house_obj.id
        ##################################### VALIDATIONS ###############################################      

        if readtype == "water":
            meter = fetch_active_meter(house_obj)
        
            meter_id = meter.id
            last_reading = getlast_reading(meter_id)

            meter_num = meter.meter_number
            str_decitype = get_str_decitype(meter_id)
            prev_reading = f"Last reading: {last_reading}"
            meter = f"{meter_num}"
            mtype = f"Type: {str_decitype}"
        else:
            meter = fetch_active_meter_alt(house_obj)
        
            meter_id = meter.id
            last_reading = getlast_reading(meter_id)

            meter_num = meter.meter_number
            str_decitype = get_str_decitype(meter_id)
            prev_reading = f"Last reading: {last_reading}"
            meter = f"{meter_num}"
            mtype = f"Type: {str_decitype}"

        if run == "run-reading":
            return render_template('ajaxreadingdata.html',prev_reading=prev_reading,meter=meter,mtype=mtype)
        
        decitype = get_decitype(meter_id)
        try:
            float_current_reading = float(reading)*decitype
            float_last_reading = float(last_reading)*decitype
        except:
            float_current_reading = 0.0 * decitype
            float_last_reading = 0.0 * decitype
  
        calc_units = float_current_reading - float_last_reading
        units_consumed = round(calc_units,3)

        if run == "run-units":
            if units_consumed > 0:
                disp_units = f"{units_consumed}"
            else:
                disp_units = "0.0"
            return render_template('ajaxunitsdata.html',units=disp_units)

        ###################################################################################################
        if last_reading > int(reading):
            return render_template("ajaxghosthouse.html",alert="Failed, check your readings and try again")
        else:
            user_id = current_user.id

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

            reading_period = generate_date(month,year)

            if readtype == "water":
                reading_obj = MeterReadingOp("actual water reading",reading,last_reading,units_consumed,reading_period,apartment_id,house_id,meter_id,user_id)
                reading_obj.save()
            else:
                reading_obj = MeterReadingOp("actual electricity reading",reading,last_reading,units_consumed,reading_period,apartment_id,house_id,meter_id,user_id)
                reading_obj.save()

            msg = f"Readings captured successfully"

            return render_template("ajaxproceed.html",alert=msg)       

class EditReading(Resource):
    """class"""
    
    @login_required
    def get(self):
        reading_id = request.args.get('reading_id')

        identifier = get_identifier(reading_id)
        reading_obj = MeterReadingOp.fetch_specific_reading(identifier)

        meter = reading_obj.meter
        str_decitype =  get_decitype(meter.id)
        curr_reading = reading_obj.reading
        last_reading = reading_obj.last_reading
        units_consumed = reading_obj.units
        return render_template('ajax_editreading.html',last=last_reading,current=curr_reading,units=units_consumed,meter=meter,mtype=str_decitype)

    @login_required
    def post(self):
        reading_id = request.form.get('reading_id')
        l_reading = request.form.get('lreading')
        reading = request.form.get('reading')
        units = request.form.get('units')
        target = request.form.get('target')


        identifier = get_identifier(reading_id)
        reading_obj = MeterReadingOp.fetch_specific_reading(identifier)

        if target == "delete":

            if reading_obj.charged:
                # return render_template("ajaxghosthouse.html",alert="Reading billed, edit instead")
                try:
                    charge_obj = reading_obj.charge
                    ChargeOp.delete(charge_obj)
                except Exception as e:
                    print(f"Houston, we have a problem {e}")
                    
            MeterReadingOp.delete(reading_obj)
            return render_template("ajaxproceed.html",alert="Deleted successfully")

        meter = reading_obj.meter
        house = reading_obj.house
        decitype = get_decitype(meter.id)


        if l_reading:
            try:
                last_reading = float(l_reading) * decitype
            except:
                last_reading = reading_obj.last_reading * decitype
        else:
            last_reading = reading_obj.last_reading * decitype



        if reading:
            try:
                current_reading = float(reading) * decitype
            except:
                current_reading = reading_obj.reading * decitype
        else:
            current_reading = reading_obj.reading * decitype

        
  
        calc_units = current_reading - last_reading
        units_consumed = round(calc_units,2)

        print("LAST ",last_reading,"CURR ",current_reading,"UNITS ",units_consumed)
        
        if target == "dispunits":
            if units_consumed > -0.00000000001:
                disp_units = f"{units_consumed}"
            else:
                disp_units = "Check input"
            return disp_units

        #check if the reading has been charged

        charge_obj = reading_obj.charge
        if charge_obj:
            if house.housecode.waterrate1:
                print("working right well")
                if units_consumed < 7:
                    amount = house.housecode.waterrate1
                elif units_consumed < 20:
                    amount = house.housecode.waterrate2 * units_consumed
                else:
                    amount = house.housecode.waterrate3 * units_consumed
            else:
                unitcost1 = house.housecode.waterrate
                unitcost2 = house.housecode.electricityrate
                if charge_obj.charge_type_id == 2:

                    if house.housecode.seweragerate:
                        amount = (unitcost1 * units_consumed) + (house.housecode.seweragerate * units_consumed)
                    else:
                        amount = unitcost1 * units_consumed

                    # amount = units_consumed*unitcost1
                else:
                    amount = units_consumed*unitcost2

                # amount = units_consumed * house.housecode.waterrate if charge_obj.charge_type_id == 2 else units_consumed * house.housecode.electricityrate
        constant_standing_charge = house.housecode.watercharge if house.housecode.watercharge else 0.0

        #######################################################################################################################################################

        if target == "edit readings":

            found = False
            for c in reading:
                if not c.isdigit():
                    found = True
            
            if found:
                msg = "Failed to update readings, Are you updating units?"
                return render_template("ajaxghosthouse.html",alert=msg)
            else: 
                MeterReadingOp.update_reading_units(reading_obj,l_reading,reading,units_consumed,current_user.id)
                msg = "Reading updated"

                if reading_obj.charged:
                    
                    amount_before = charge_obj.amount
                    # diff = amount - amount_before

                    ChargeOp.update_amount(charge_obj,amount,current_user.id)
                    msg = "Reading and corresponding charge updated"

                    monthlycharge_obj = MonthlyChargeOp.fetch_monthlycharge_by_house_id(house.id)

                    if monthlycharge_obj:
                        if monthlycharge_obj.month == charge_obj.date.month and monthlycharge_obj.year == charge_obj.date.year:
                            totalbill = monthlycharge_obj.total_bill
                            totalbill -= amount_before
                            totalbill += amount

                            if charge_obj.charge_type_id != 2:
                                MonthlyChargeOp.update_monthly_charge(monthlycharge_obj,"null","null","null",amount,"null","null","null","null","null","null",totalbill,current_user.id)
                            else:
                                amount += constant_standing_charge
                                MonthlyChargeOp.update_monthly_charge(monthlycharge_obj,amount,"null","null","null","null","null","null","null","null","null",totalbill,current_user.id)

                            if monthlycharge_obj.paid_amount:
                                bal = totalbill - monthlycharge_obj.paid_amount
                            else:
                                bal = totalbill
                            MonthlyChargeOp.update_balance(monthlycharge_obj,bal)

                            msg = "Reading and corresponding bill updated"

                        tenant_obj = monthlycharge_obj.tenant
                        if tenant_obj:
                            tenant_balance = tenant_obj.balance
                            tenant_balance -= amount_before
                            amount -= constant_standing_charge
                            tenant_balance += amount
                            TenantOp.update_balance(tenant_obj,tenant_balance)

        ####################################################################################################################################################

        else:
            if not reading_obj.charged:
                msg = "Failed to update units, edit readings readings instead"
                return render_template("ajaxghosthouse.html",alert=msg)
            else:
                try:
                    float_units = float(units)
                except:
                    return render_template("ajaxghosthouse.html",alert="Units entered are not valid")


                MeterReadingOp.update_reading_units(reading_obj,0,0,units,current_user.id)

                if house.housecode.waterrate1:
                    print("working right well")
                    if float_units < 7:
                        calculated_amount = house.housecode.waterrate1
                    elif float_units < 20:
                        calculated_amount = house.housecode.waterrate2 * float_units
                    else:
                        calculated_amount = house.housecode.waterrate3 * float_units
                else:
                    unitcost1 = house.housecode.waterrate
                    unitcost2 = house.housecode.electricityrate
                    if charge_obj.charge_type_id == 2:

                        if house.housecode.seweragerate:
                            calculated_amount = (unitcost1 * float_units) + (house.housecode.seweragerate * float_units)
                        else:
                            calculated_amount = unitcost1 * float_units

                        # calculated_amount = float_units*unitcost1
                    else:
                        calculated_amount = float_units*unitcost2

                # calculated_amount = float_units * reading_obj.house.housecode.waterrate if charge_obj.charge_type_id == 2 else float_units * house.housecode.electricityrate

                amount_before = charge_obj.amount

                ChargeOp.update_amount(charge_obj,calculated_amount,current_user.id)
                msg = "Units updated"

                monthlycharge_obj = MonthlyChargeOp.fetch_monthlycharge_by_house_id(house.id)

                if monthlycharge_obj:
                    if monthlycharge_obj.month == charge_obj.date.month and monthlycharge_obj.year == charge_obj.date.year:
                        totalbill = monthlycharge_obj.total_bill
                        totalbill -= amount_before
                        totalbill += calculated_amount


                        if charge_obj.charge_type_id != 2:
                            MonthlyChargeOp.update_monthly_charge(monthlycharge_obj,"null","null","null",calculated_amount,"null","null","null","null","null","null",totalbill,current_user.id)
                        else:
                            calculated_amount += constant_standing_charge
                            MonthlyChargeOp.update_monthly_charge(monthlycharge_obj,calculated_amount,"null","null","null","null","null","null","null","null","null",totalbill,current_user.id)

                        if monthlycharge_obj.paid_amount:
                            bal = totalbill - monthlycharge_obj.paid_amount
                        else:
                            bal = totalbill
                        MonthlyChargeOp.update_balance(monthlycharge_obj,bal)
                        msg = "Reading and corresponding bill updated"

                    tenant_obj = monthlycharge_obj.tenant
                    if tenant_obj:
                        tenant_balance = tenant_obj.balance
                        tenant_balance -= amount_before
                        calculated_amount -= constant_standing_charge
                        tenant_balance += calculated_amount
                        TenantOp.update_balance(tenant_obj,tenant_balance)
        
        return render_template("ajaxproceed.html",alert=msg)

class HandleTenantRequest(Resource):
    """class"""
    @login_required
    def get(self):
        
        # if current_user.username.startswith("qc"):

        #     props = [18,17,11,15,10]
        #     # props = [22]

        #     penjob = q.enqueue_call(
        #         func=penalty_calculator, args=(props,), result_ttl=5000
        #     )


        # obj = MonthlyChargeOp.fetch_specific_bill(2078)
        # MonthlyChargeOp.update_payment(obj,2000)
        # MonthlyChargeOp.update_balance(obj,3200)

        apartments = fetch_all_apartments_by_user(current_user)
        reqtypes = ["House Maintenance","House Transfer","House Clearance"]
        categories = ["Pending","Queued","In progress","Completed","Rejected"]

        reqdata_list = fetch_reqdata(apartments)
        

        return Response(render_template(
            "handlerequests.html",
            bills=reqdata_list,
            props=apartments,
            reqtypes=reqtypes,
            categories=categories,
            group=get_group_name(current_user.user_group_id),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name
        ))

    @login_required
    def post(self):
        
        apartment =  request.form.get("property")
        requesttype = request.form.get("reqtype")
        category = request.form.get("category")

        run = request.form.get("run")

        apartment_obj = ApartmentOp.fetch_apartment_by_name(apartment)

        if run == "display":

            if requesttype == "House Maintenance":
                request_objs = apartment_obj.tenantrequests
                resps = display_reqs(request_objs,category)

                my_requests = []
                for r in resps:
                    obj = TenantRequestOp.view(r)
                    my_requests.append(obj)

                req_id_list = []
                for req in my_requests:
                    req_id = req["id"]
                    req_id_list.append(req_id)

                if len(my_requests) == 0:
                    title  = f"No {category} {requesttype} requests at the moment"
                else:
                    title = f"{category} {requesttype} requests"


                return render_template("ajax_dispreqs.html",bills=my_requests,title=title,requestids=req_id_list)

            elif requesttype ==  "House Transfer":
                transfer_objs = apartment_obj.transferrequests
                resps = display_reqs(transfer_objs,category)

                my_requests = []
                for r in resps:
                    obj = TransferRequestOp.view(r)
                    my_requests.append(obj)

                req_id_list = []
                for req in my_requests:
                    req_id = req["id"]
                    req_id_list.append(req_id)

                if len(my_requests) == 0:
                    title  = f"No {category} {requesttype} requests at the moment"
                else:
                    title = f"{category} {requesttype} requests"

                return render_template("ajax_disp_transreqs.html",bills=my_requests,title=title,requestids=req_id_list)

            elif requesttype ==  "House Clearance":
                clear_objs = apartment_obj.clearrequests
                resps = display_reqs(clear_objs,category)

                my_requests = []
                for r in resps:
                    obj = ClearanceRequestOp.view(r)
                    my_requests.append(obj)

                req_id_list = []
                for req in my_requests:
                    req_id = req["id"]
                    req_id_list.append(req_id)

                if len(my_requests) == 0:
                    title  = f"No {category} {requesttype} requests at the moment"
                else:
                    title = f"{category} {requesttype} requests"

                return render_template("ajax_disp_clearreqs.html",bills=my_requests,title=title,requestids=req_id_list)

        elif run == "reqdata":
            apartments = fetch_all_apartments_by_user(current_user)
            reqdata_list = fetch_reqdata(apartments)
            return render_template("ajax_refresh_reqdata.html",bills=reqdata_list)

class ReactToRequest(Resource):
    """class"""
    def get(self):
        pass
    def post(self):
        # action
        req_id = request.form.get("requestid")
        action = request.form.get("action")
        cost = request.form.get("cost")
        estimate = request.form.get("costestimate")
        desc = request.form.get("desc")
        debit_target = request.form.get("debit_target")

        run = request.form.get("run")

        if run == "maintenance":

            if action == "completed":
                try:
                    charge = float(cost)
                except:
                    charge = None #escaping type error

                print(">>>> handled request action >>>>", action, "<<<<<")

                request_obj = TenantRequestOp.fetch_a_request_by_id(req_id)

                TenantRequestOp.update_comment(request_obj,desc)
                TenantRequestOp.update_status(request_obj,action)
                TenantRequestOp.update_cost(request_obj,charge)

            elif action == "queued":
                try:
                    c_estimate = float(estimate)
                except:
                    c_estimate = None #escaping type error

                print(">>>> handled request action >>>>", action, "<<<<<")

                request_obj = TenantRequestOp.fetch_a_request_by_id(req_id)
                tenant_obj = request_obj.tenant

                TenantRequestOp.update_comment(request_obj,desc)
                TenantRequestOp.update_status(request_obj,action)
                TenantRequestOp.update_estimate(request_obj,c_estimate)

                #Send the SMS
                if tenant_obj.sms:
                    tele = tenant_obj.phone
                    phonenum = sms_phone_number_formatter(tele)
                    try:
                        recipient = [phonenum]
                        message = f"Dear Tenant, We have received request No.{req_id}. The estimated costs are Kshs.{c_estimate}. To cancel this request, log into your account https://kiotapay.com/signin"
                        
                        #Once this is done, that's it! We'll handle the rest
                        response = sms.send(message, recipient, sender)
                        print(response)
                    except Exception as e:
                        print(f"Houston, we have a problem {e}")

            else:
                if action:

                    print(">>>> handled request action >>>>", action, "<<<<<")

                    request_obj = TenantRequestOp.fetch_a_request_by_id(req_id)

                    TenantRequestOp.update_comment(request_obj,desc)
                    TenantRequestOp.update_status(request_obj,action)


        elif run == "transfer":
            if cost:
                try:
                    floatcost = float(cost)
                except:
                    floatcost = None # a text was passed instead
            else:
                floatcost = None

            if action == "completed":
                charge = floatcost
            else:
                charge = None

            if action:
                print(">>>> handled request action >>>>", action, "<<<<<")

                transfer_obj = TransferRequestOp.fetch_a_request_by_id(req_id)

                TransferRequestOp.update_comment(transfer_obj,desc)

                TransferRequestOp.update_status(transfer_obj,action)
                TransferRequestOp.update_cost(transfer_obj,charge)

        elif run == "clearance":
            # clear_obj = ClearanceRequestOp.fetch_a_request_by_id(req_id)
            # if cost:
            #     try:
            #         floatcost = float(cost)
            #     except:
            #         floatcost = None # a text was passed instead
            # else:
            #     floatcost = None

            # if action == "completed":
            #     tenant_obj = TenantOp.fetch_tenant_by_id(clear_obj.tenant_id)
            #     tenant_alloc = check_house_occupied(tenant_obj)[2]
            #     balance = floatcost
            #     cleared_by = current_user.id
            #     AllocateTenantOp.update_status(tenant_alloc,False,balance,period,cleared_by)
            #     TenantOp.update_status(tenant_obj,"Vacated")
            # else:
            #     charge = None

            # if action:
            #     print(">>>> handled request action >>>>", action, "<<<<<")

                

            #     ClearanceRequestOp.update_comment(clear_obj,desc)

            #     ClearanceRequestOp.update_status(clear_obj,action)
            #     # ClearanceRequestOp.update_cost(clear_obj,charge)
            pass

        # refresh
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Reuse above code to refresh!!!!!
        apartment =  request.form.get("property")
        requesttype = request.form.get("reqtype")
        category = request.form.get("category")

        print(">>>>>>",apartment,requesttype,category)

        apartment_obj = ApartmentOp.fetch_apartment_by_name(apartment)
        if requesttype == "House Maintenance":
            request_objs = apartment_obj.tenantrequests
            resps = display_reqs(request_objs,category)

            my_requests = []
            for r in resps:
                obj = TenantRequestOp.view(r)
                my_requests.append(obj)

            req_id_list = []
            for req in my_requests:
                req_id = req["id"]
                req_id_list.append(req_id)

            if len(my_requests) == 0:
                title  = f"No {category} {requesttype} requests at the moment"
            else:
                title = f"{category} {requesttype} requests"

            return render_template("ajax_dispreqs.html",bills=my_requests,title=title,requestids=req_id_list)

        elif requesttype ==  "House Transfer":
            transfer_objs = apartment_obj.transferrequests
            resps = display_reqs(transfer_objs,category)

            my_requests = []
            for r in resps:
                obj = TransferRequestOp.view(r)
                my_requests.append(obj)

            req_id_list = []
            for req in my_requests:
                req_id = req["id"]
                req_id_list.append(req_id)

            if len(my_requests) == 0:
                title  = f"No {category} {requesttype} requests at the moment"
            else:
                title = f"{category} {requesttype} requests"

            return render_template("ajax_disp_transreqs.html",bills=my_requests,title=title,requestids=req_id_list)

        elif requesttype ==  "House Clearance":
            clear_objs = apartment_obj.clearrequests
            resps = display_reqs(clear_objs,category)

            my_requests = []
            for r in resps:
                obj = ClearanceRequestOp.view(r)
                my_requests.append(obj)

            req_id_list = []
            for req in my_requests:
                req_id = req["id"]
                req_id_list.append(req_id)

            if len(my_requests) == 0:
                title  = f"No {category} {requesttype} requests at the moment"
            else:
                title = f"{category} {requesttype} requests"

            return render_template("ajax_disp_clearreqs.html",bills=my_requests,title=title,requestids=req_id_list)

class TenantHouseRequest(Resource):
    def get(self):
        pass

    @login_required
    def post(self):
        requesttype = request.form.get("requesttype")
        title = request.form.get("title")
        desc = request.form.get("description")
        
        if not requesttype:
            return render_template("ajax_request_fail.html",status="Failed, Request type required")
        if not title:
            return render_template("ajax_request_fail.html",status="Failed, title required")
        
        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
        check = check_house_occupied(tenant_obj)
        if check[0] != "Resident":
            return render_template("ajax_request_fail.html",status="Seems you've moved out")
        house_id = check[2].house_id
        apartment_id = check[2].apartment_id
        tenant_id = tenant_obj.id

        request_obj = TenantRequestOp(requesttype,title,desc,tenant_id,house_id,apartment_id)
        request_obj.save()

        return render_template("ajax_request_success.html",status="Request submitted successfully")


class HouseTransferRequest(Resource):
    def get(self):
        pass
    @login_required
    def post(self):
        trans_house = request.form.get("trans_house")
        desc = request.form.get("description")

        if not trans_house:
            return render_template("ajax_transferrequest_fail.html",status="Failed, Please specify house")

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
        check = check_house_occupied(tenant_obj)
        if check[0] != "Resident":
            return render_template("ajax_transferrequest_fail.html",status="Non resident. Please use check vacancy option")
        house_id = check[2].house_id
        apartment_id = check[2].apartment_id
        tenant_id = tenant_obj.id
        apartment_id = tenant_obj.apartment_id
        # tenant_bal = tenant_obj.balance

        run = request.form.get("run")
        if run == "runmessage":
            # if tenant_bal > 0.0:
            status = f"You have requested to be transferred from {check[1].name} to house {trans_house}"
            message = f"On a first come first served basis, this request will be considered if {trans_house} is available"
            return render_template("ajax_transrequest.html",status=status,message=message)

        paint_cost = 0.0

        hse_trans_obj = TransferRequestOp(trans_house,desc,paint_cost,tenant_id,house_id,apartment_id)
        hse_trans_obj.save()
        return render_template("ajax_request_success.html", status="House transfer request submitted succesfully")

class HouseClearanceRequest(Resource):
    def get(self):
        pass
    @login_required
    def post(self):
        clr_month = request.form.get("clr_month")
        desc = request.form.get("description")

        if not clr_month:
            return render_template("ajax_clearancerequest_fail.html",status="Failed, Please specify month")

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
        check = check_house_occupied(tenant_obj)
        if check[0] != "Resident":
            return render_template("ajax_clearancerequest_fail.html",status="Seems you've moved out")
        house_id = check[2].house_id
        apartment_id = check[2].apartment_id
        tenant_id = tenant_obj.id
        apartment_id = tenant_obj.apartment_id
        tenant_bal = tenant_obj.balance

        run = request.form.get("run")
        if run == "runbalance":
            if tenant_bal > 0.0:
                status = f"You have a balance of Kshs {tenant_bal:,}"
                message = f"Ensure to clear the balance by 30th of {clr_month}"
            return render_template("ajax_house_clearance_balance.html",status=status,message=message)
        clear_month = get_numeric_month(clr_month)
        hse_clr_obj = ClearanceRequestOp(clear_month,desc,tenant_id,house_id,apartment_id)
        hse_clr_obj.save()
        return render_template("ajax_request_success.html", status="House clearance request submitted succesfully")

class TrackRequest(Resource):
    def get(self):
        pass
    def post(self):
        req_id = request.form.get("requestid")

        request_obj = TenantRequestOp.fetch_a_request_by_id(req_id)
        print(">>>>>>>>>>>>>>>>##############",request_obj.status,request_obj.id,request_obj.title)
        comment = request_obj.handled_description
        if request_obj.status == "pending":
            level = "Pending"
            status = "Queued"
            p1 = "progtrckr-done"
            p2 = "progtrckr-todo"
            p3 = "progtrckr-todo"
            p4 = "progtrckr-todo"
        elif request_obj.status == "rejected":
            level = "Received"
            status = "Rejected"
            p1 = "progtrckr-done"
            p2 = "progtrckr-todo text-warning"
            p3 = ""
            p4 = ""
        elif request_obj.status == "queued":
            level = "Received"
            status = "Queued"
            p1 = "progtrckr-done"
            p2 = "progtrckr-done"
            p3 = "progtrckr-todo"
            p4 = "progtrckr-todo"
        elif request_obj.status == "running":
            level = "Received"
            status = "Queued"
            p1 = "progtrckr-done"
            p2 = "progtrckr-done"
            p3 = "progtrckr-done"
            p4 = "progtrckr-todo"
        else:
            level = "Received"
            status = "Queued"
            p1 = "progtrckr-done"
            p2 = "progtrckr-done"
            p3 = "progtrckr-done"
            p4 = "progtrckr-done"

        return render_template(
            "ajaxtenantrequest.html",
            str_reqid = "RequestId: "+str(req_id),
            comment = comment,
            reqobj=request_obj,
            status=status,
            level=level,
            progress1=p1,
            progress2=p2,
            progress3=p3,
            progress4=p4,
            reqid=req_id
        )

class DeleteRequest(Resource):
    def get(self):
        pass
    @login_required
    def post(self):
        req_id = request.form.get("requestid")
        request_obj = TenantRequestOp.fetch_a_request_by_id(req_id)
        TenantRequestOp.delete(request_obj)

        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)

        my_requests = []
        myrequests = fetch_active_requests(tenant_obj)
        for r in myrequests:
            obj = TenantRequestOp.view(r)
            my_requests.append(obj)

        req_id_list = []
        for req in my_requests:
            req_id = req["id"]
            req_id_list.append(req_id)

        return render_template("ajax_reqs_del_refresh.html",bills=my_requests,requestids=req_id_list)

class CheckVacancy(Resource):
    """class"""
    @login_required
    def get(self):
        apartments = ApartmentOp.fetch_all_apartments()
        return Response(render_template("housevacancy.html",props=apartments,name=current_user.name))

class Search(Resource):
    """class"""
    @login_required
    def get(self):
        letters = request.args.get('letters')
        user_id = current_user.id
        suggestions_list = []
        if letters:
            char  = '%'
            phrase = char + letters + char
            print(phrase)
            first_search_props = ApartmentOp.search_user_props_by_matching_pattern(phrase,user_id)
            print(first_search_props)
            for item in first_search_props:
                suggestions_list.append(item)

            str_suggestions = ','.join(map(str, suggestions_list))

            return render_template("ajax_search_results.html",items=str_suggestions)

class Results(Resource):
    """class"""
    def get(self):
        item = request.args.get('id')
        period_target = request.args.get('target_period')

        user_id = current_user.id
        if not item:
            return "Error fetching results, try refreshing the page!"
        if item.startswith("prop"):
            prop_id = item[4:]
            prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)

            house_list = prop_obj.houses
            houses = len(house_list)
            period=get_billing_period(prop_obj)
            str_period=get_str_month(period.month)
            tenancy = tenantauto(prop_obj.id)
            tenants = len(tenancy)
            owner = prop_obj.owner
            if prop_obj.caretaker_id:
                caretaker = UserOp.fetch_user_by_username(prop_obj.caretaker_id)
            else:
                caretaker = "Unavailable"
            if prop_obj.agency_managed:
                agent = UserOp.fetch_user_by_username(prop_obj.agent_id)
                try:
                    agent_name = agent.name
                    contact = agent.phone
                except:
                    agent_name = "Not available"
                    contact = "N/A"
            else:
                agent_name = "N/A"
                contact = "N/A"

            houselist = []

            for i in house_list:
                new_i = HouseOp.view(i)
                houselist.append(new_i)

            return render_template("ajax_prop_detail.html",prop=prop_obj,owner=owner,caretaker=caretaker,agent=agent_name,num_units=houses,num_tenants=tenants,contact=contact,period=str_period,items=houselist)

        elif item.startswith("hse"):
            hse_id = item[3:]
            house_obj = HouseOp.fetch_house_by_id(hse_id)

            update_login_history("search",current_user)

            current_invoice = fetch_current_invoice(house_obj)

            prop_obj = house_obj.apartment
            month = get_str_month(prop_obj.billing_period.month)


            if check_occupancy(house_obj)[0]=="occupied":
                tenant_obj = check_occupancy(house_obj)[1]
            else:
                tenant_obj = None

            if tenant_obj:
                db.session.expire(tenant_obj)

                if current_invoice:

                    if current_invoice.tenant_id == tenant_obj.id:
                        if current_invoice.paid_amount:
                            paid_status = "paid"
                            badge_status = "badge badge-success badge-counter"

                            if current_invoice.balance > 0.0:
                                paid_status = "partialy paid"
                                badge_status = "badge badge-warning badge-counter"
                        else:
                            paid_status = "unpaid"
                            badge_status = "badge badge-danger badge-counter"
                    else:
                        paid_status = 'not invoiced'
                        badge_status = "badge badge-danger badge-counter"
                else:
                    paid_status = "-"
                    badge_status = ""


                if tenant_obj.sms:
                    smsable = "Yes"
                else:
                    smsable = "No"

                # tenant_payments = tenant_obj.payments
                tenant_payments = []

                filtered_payments = filter_in_recent_data(tenant_payments)

                actual_payments = fetch_actual_payments(filtered_payments)

                detailed_payments_list = payment_details(actual_payments)

                payids = get_obj_ids(detailed_payments_list)

                

                return render_template("ajax_tenant_detail.html",prop=prop_obj,houses=house_obj,tenant=tenant_obj,paid_status=paid_status,badge_status=badge_status,smsable=smsable,month=month)

            else:
                tenant_obj = f'<span class="text-danger">Vacant</span>'
                if house_obj.billable:
                    billable = "Yes"
                else:
                    billable = "No"
                readings = MeterReadingOp.fetch_all_readings_by_house(hse_id)
                filtered_readings = filter_in_recent_data(readings)
                meter_readings = []
                for i in filtered_readings:
                    new_i = MeterReadingOp.view(i)
                    meter_readings.append(new_i)
                return render_template("ajax_house_detail.html",prop=prop_obj,house=house_obj,tenant=tenant_obj,billing_status=billable,bills=meter_readings)

        elif item.startswith("prp"):
            prop_id = item[3:]
            prop_obj = ApartmentOp.fetch_apartment_by_id(prop_id)
            db.session.expire(prop_obj)

            bills = prop_obj.monthlybills

            if period_target == "current":
                current_bills = fetch_current_billing_period_bills(prop_obj.billing_period,bills)
            elif period_target == "previous":
                current_bills = fetch_prev_billing_period_bills(prop_obj.billing_period,bills)
            else:
                current_bills = fetch_next_billing_period_bills(prop_obj.billing_period,bills)

            detailed_bills = []

            renttotal_sum_members = []
            watertotal_sum_members = []
            electricitytotal_sum_members = []
            garbagetotal_sum_members = []
            securitytotal_sum_members = []
            servicetotal_sum_members = []
            deposittotal_sum_members = []
            agreementtotal_sum_members = []
            finetotal_sum_members = []
            arrearstotal_sum_members = []
            billtotal_sum_members = []
            paidtotal_sum_members = []
            balancetotal_sum_members = []

            for bill in current_bills:

                deposit = bill.deposit if bill.deposit else 0.0
                agreement = bill.agreement if bill.agreement else 0.0

                renttotal_sum_members.append(bill.rent)

                watertotal_sum_members.append(bill.water)

                electricitytotal_sum_members.append(bill.electricity)

                garbagetotal_sum_members.append(bill.garbage)

                securitytotal_sum_members.append(bill.security)

                servicetotal_sum_members.append(bill.maintenance)

                deposittotal_sum_members.append(deposit)

                agreementtotal_sum_members.append(agreement)

                finetotal_sum_members.append(bill.penalty)

                arrearstotal_sum_members.append(bill.arrears)

                billtotal_sum_members.append(bill.total_bill)

                paidtotal_sum_members.append(bill.paid_amount)

                balancetotal_sum_members.append(bill.balance)

            vacants = filter_out_occupied_houses(prop_obj.name)
            for vac in vacants:
                if vac.owner:
                    continue
                all_charges = vac.charges
                water_charge = 0.0
                electricity_charge = 0.0
                for charge in all_charges:
                    if charge.date.month == prop_obj.billing_period.month and charge.date.year == prop_obj.billing_period.year and charge.charge_type_id == 2:
                        water_charge = charge.amount
                    if charge.date.month == prop_obj.billing_period.month and charge.date.year == prop_obj.billing_period.year and charge.charge_type_id == 5:
                        electricity_charge = charge.amount

                house_tenant = vac.name  + "(Vacant)"

                new_item = {
                    'id':"0",
                    'viewid':"0",
                    'smsid':"0",
                    'mailid':"0",
                    'delid':"0",
                    'editid':"0",
                    'payid':"0",
                    'hst':house_tenant,
                    'vacancy':"text-danger",
                    'rent':0.0,
                    'water':water_charge,
                    'electricity':electricity_charge,
                    'garbage':0.0,
                    'security':0.0,
                    'service': 0.0,
                    'agreement':0.0,
                    'deposit':0.0,
                    'fine': 0.0,
                    'arrears': 0.0,
                    'total': water_charge + electricity_charge,
                    'paid': 0.0,
                    'active':"disabled",
                    'smsstatus': '<i class="fas fa-ban text-danger ml-3"></i>',
                    'smsactive':"disabled",
                    'mailstatus': '<i class="fas fa-ban text-danger ml-3"></i>',
                    'mailactive':"disabled",
                    'balance':0.0
                }
                detailed_bills.append(new_item)

                watertotal_sum_members.append(new_item['water'])
                electricitytotal_sum_members.append(new_item['electricity'])
                billtotal_sum_members.append(new_item['total'])
                paidtotal_sum_members.append(new_item['paid'])

            totalrent = sum_values(renttotal_sum_members)
            renttotal = (f"{totalrent:,}")

            totalwater = sum_values(watertotal_sum_members)
            watertotal = (f"{totalwater:,}")
            
            totalelectricity = sum_values(electricitytotal_sum_members)
            electotal = (f"{totalelectricity:,}")

            totalgarbage = sum_values(garbagetotal_sum_members)
            garbtotal = (f"{totalgarbage:,}")

            totalsecurity = sum_values(securitytotal_sum_members)
            sectotal = (f"{totalsecurity:,}")

            totalservice = sum_values(servicetotal_sum_members)
            servtotal = (f"{totalservice:,}")

            totalagreement = sum_values(agreementtotal_sum_members)
            agrtotal = (f"{totalagreement:,}")

            totaldeposit = sum_values(deposittotal_sum_members)
            deptotal = (f"{totaldeposit:,}")

            totalfine = sum_values(finetotal_sum_members)
            finetotal = (f"{totalfine:,}")

            totalarrears = sum_positive_values(arrearstotal_sum_members)
            arrearstotal = (f"{totalarrears:,}")
            
            totalbill = sum_values(billtotal_sum_members)
            billtotal = (f"{totalbill:,}")

            totalpaid = sum_values(paidtotal_sum_members)
            paidtotal = (f"{totalpaid:,}")

            totalbalance = sum_positive_values(balancetotal_sum_members)
            balancetotal = (f"{totalbalance:,}")

            fieldshow_sec = "dispnone" if not totalsecurity else ""
            fieldshow_sev = "dispnone" if not totalservice else ""
            fieldshow_rent = "dispnone" if not totalrent else ""
            fieldshow_elec = "dispnone" if not totalelectricity else ""
            fieldshow_garb = "dispnone" if not totalgarbage else ""
            fieldshow_water = "dispnone" if not totalwater else ""
            fieldshow_dep = "dispnone" if not totaldeposit else ""
            fieldshow_arg = "dispnone" if not totalagreement else ""
            fieldshow_fine = "dispnone" if not totalfine else ""

            # fieldshow_arr = "dispnone" if not totalarrears else ""

            fieldshow_arr = ""

            print(totalagreement,fieldshow_arg)

            detailed_bills_alt = bill_details(current_bills)

            detailed_bills += detailed_bills_alt

            billids = get_obj_ids_alt(detailed_bills)

            str_month = get_str_month(prop_obj.billing_period.month)

            return render_template(
                "ajax_bills_detail.html",
                prop=prop_obj,
                rent=renttotal,
                water=watertotal,
                elec=electotal,
                garb=garbtotal,
                sec=sectotal,
                serv=servtotal,
                arg=agrtotal,
                dep=deptotal,
                fine=finetotal,
                arrears=arrearstotal,
                total=billtotal,
                paid=paidtotal,
                bal=balancetotal,
                fieldshow_dep=fieldshow_dep,
                fieldshow_water=fieldshow_water,
                fieldshow_rent=fieldshow_rent,
                fieldshow_garb=fieldshow_garb,
                fieldshow_elec=fieldshow_elec,
                fieldshow_arg=fieldshow_arg,
                fieldshow_fine=fieldshow_fine,
                fieldshow_sec=fieldshow_sec,
                fieldshow_sev=fieldshow_sev,
                fieldshow_arr=fieldshow_arr,
                current_month=str_month,
                bills=detailed_bills,
                billids=billids
                )


        else:

            tenant_id = get_identifier(item)

            if item.startswith("tnt"):
                print("fetching tenant",item)
                tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
            else:
                print("fetching resident",item)
                tenant_obj = PermanentTenantOp.fetch_tenant_by_id(tenant_id)

            update_login_history("search",current_user)

            db.session.expire(tenant_obj)
            prop_obj = tenant_obj.apartment

            month = get_str_month(prop_obj.billing_period.month)

            if tenant_obj.multiple_houses:
                paid_status = "-"
                badge_status = ""
            else:
                # print(tenant_obj.resident_type,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<restype")
                # print(tenant_obj.tenant_type,"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<ttype")

                # PermanentTenantOp.update_resident_type(tenant_obj,"investor")

                if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
                    house_obj = tenant_obj.house
                    current_invoice = fetch_current_owner_invoice(house_obj)
                else:
                    house_obj = check_house_occupied(tenant_obj)[1]
                    current_invoice = fetch_current_invoice(house_obj)

                if current_invoice:
                    if current_invoice.paid_amount:
                        paid_status = "paid"
                        badge_status = "badge badge-success badge-counter"

                        if current_invoice.balance > 0.0:
                            paid_status = "partialy paid"
                            badge_status = "badge badge-warning badge-counter"
                    else:
                        paid_status = "unpaid"
                        badge_status = "badge badge-danger badge-counter"
                else:
                    paid_status = 'not invoiced'
                    badge_status = "badge badge-danger badge-counter"


            if tenant_obj.tenant_type == "owner" or tenant_obj.tenant_type == "resident":
                houses = tenant_obj.house
            else:
                if get_active_houses(tenant_obj)[0] == "Resident":
                    print(get_active_houses(tenant_obj)[0])
                    houses = get_active_houses(tenant_obj)[1]
                elif get_active_houses(tenant_obj)[0] == "Vacated":
                    print(get_active_houses(tenant_obj)[0])
                    houses = get_active_houses(tenant_obj)[1].house
                else:
                    houses = None

            if tenant_obj.sms:
                smsable = "Yes"
            else:
                smsable = "No"

            tenant_payments = []

            filtered_payments = filter_in_recent_data(tenant_payments)

            actual_payments = fetch_actual_payments(filtered_payments)

            detailed_payments_list = payment_details(actual_payments)

            payids = get_obj_ids(detailed_payments_list)

            template = "ajax_tenant_detail2.html" if crm(current_user) else "ajax_tenant_detail.html"

            return render_template(template,prop=prop_obj,houses=houses,tenant=tenant_obj,paid_status=paid_status,badge_status=badge_status,smsable=smsable,month=month)


class ContactManagement(Resource):
    def get(self):
        pass

    @login_required
    def post(self):
        tenant_obj = TenantOp.fetch_tenant_by_nat_id(current_user.national_id)
        check = check_house_occupied(tenant_obj)
        if check[0] != "Resident":
            return render_template("ajax_request_fail.html",status="Seems you've moved out")
        # house_id = check[2].house_id
        apartment_id = check[2].apartment_id
        tenant_id = tenant_obj.id

        txt = request.form.get('message')
        title = "Tenant Message"

        if txt:
            txt_obj = InternalMessagesOp(title,txt,tenant_id,apartment_id)
            txt_obj.save()

class HouseData(Resource):
    def get(self,user_id,unit_number):
        user_obj = UserOp.fetch_user_by_national_id(user_id)
        if not user_obj:
            payload = {
                "success":"false",
                "message":f"user of {user_id} not found",
                'unit_id':unit_number,
                'occupied':"",
                "tenant_details":{}
                }
        else:
            props = user_obj.company.props
            raw_units = []
            for prop in props:
                raw_units.append(prop.houses)
            units = flatten(raw_units)

            try:
                house_obj = get_specific_house_obj_alt(units,unit_number)
                tenant_obj = None
                if house_obj:
                    check = check_occupancy(house_obj)
                    if check[0] == "occupied":
                        tenant_obj = check[1]

                    if tenant_obj:
                        try:
                            fname = tenant_obj.name.split(' ')[0]
                        except:
                            fname = "Unnamed"

                        try:
                            lname = tenant_obj.name.split(' ')[1]
                        except:
                            lname = "Unnamed"

                        try:
                            deposit = tenant_obj.deposits.total
                        except:
                            deposit = 0.0


                        payload = {
                            "success":"true",
                            "message":"success",
                            'unit_id':unit_number,
                            'occupied':"true",
                            "tenant_details":{
                                "first_name":fname,
                                "last_name":lname,
                                "unit_number":unit_number,
                                "phone_number":tenant_obj.phone,
                                "check_in":tenant_obj.date.strftime("%m-%d-%Y, %H:%M:%S"),
                                "deposit":deposit,
                                "id":tenant_obj.national_id
                                }
                            }
                    else:
                        payload = {
                            "success":"true",
                            "message":"success",
                            'unit_id':unit_number,
                            'occupied':"false",
                            "tenant_details":{}
                            }

                else:
                    payload = {
                        "success":"true",
                        "message":"unit not found",
                        'unit_id':unit_number,
                        'occupied':"",
                        "tenant_details":{}
                        }

            except:
                payload = {
                    "success":"false",
                    "message":f"unit number {unit_number} format error",
                    'unit_id':unit_number,
                    'occupied':"",
                    "tenant_details":{}
                    }

        return payload






        
 
        

    
  