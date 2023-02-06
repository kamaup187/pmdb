
from dateutil.parser import parse

from flask_login import login_required, current_user
from flask_restful import Resource
from flask_mail import Message
from flask import render_template,Response,request,flash,redirect,url_for,json
# from ..forms.forms import PaymentForm,AmendChargeForm

from app.v1.models.operations import *
from ..views.helperfuncs import *
# from ..views.secrets import *
from app import mail

class Reports(Resource):
    @login_required
    def get(self):

        start = request.args.get("from")
        stop = request.args.get("to")

        if start and stop:

            begin = date_formatter_alt(start)
            end = date_formatter_alt(stop)

            begin_date = parse(begin)
            end_date = parse(end)

            date_range = [begin_date.date() + datetime.timedelta(days=x) for x in range(0, (end_date-begin_date).days+1)]

            timeline = f'{begin_date.strftime("%b/%y")} to {end_date.strftime("%b/%y")}'
            period = begin_date
        
        else:
            date_range = []
            timeline = None
            period = current_user.company.billing_period

        print(">>>>",period)

        ##################################################################################################
        items = []

        grand_total_collections = 0.0
        grand_management_fee = 0.0

        ###################################################################################################
        props = fetch_all_apartments_by_user(current_user)

        for prop in props:
            total_collections = 0.0
            
            for item in prop.monthlybills:
                # period_of_billing = generate_date(item.month,item.year)
                # if period_of_billing.date() in date_range:

                if item.month == period.month and item.year == period.year:
                    print(item.month,item.year)

                    try:
                        total_collections += item.rent_paid if item.rent_paid > 0 else 0
                    except:
                        pass
                    try:
                        grand_total_collections += item.rent_paid if item.rent_paid > 0 else 0
                    except:
                        pass

            commission = prop.commission if prop.commission else 0.0
        
            management_fee = total_collections*commission*0.01

            if commission:
                commission_percentage = f"{commission} %"
            else:
                commission_percentage = ""
                

            if not commission:
                if total_collections:
                    commission = prop.int_commission if prop.int_commission else 0.0
                    management_fee = commission
                else:
                    commission = prop.int_commission if prop.int_commission else 0.0
                    management_fee = 0.0
                commission_percentage = f"{commission} flat rate"

            grand_management_fee += management_fee

            c_item = {
                "code":prop.id,
                "name":prop.name,
                "paid":total_collections,
                "commission":commission_percentage,
                "fees":f"{management_fee:,.1f}"
            }

            items.append(c_item)


        grandpaid = (f"{grand_total_collections:,}")
        grandcommission = (f"{grand_management_fee:,}")

        return Response(render_template(
            'report_commission_statement.html',
            tenantlist=[],
            timeline = timeline,
            grandpaid=grandpaid,
            grandcommission=grandcommission,
            bills=items,
            paging=page(items),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

# class Reports(Resource):
#     """report class"""
#     @login_required
#     def get(self):

#         delay = "no" if os.getenv("CURRENT_APP") == "app2" else "no"
#         time = datetime.datetime.now()
#         present_month = time.month
#         present_year = time.year
#         # apartment_list = fetch_all_apartments_by_user(current_user)
#         apartment_list = []

#         monthly_collection=[] #list of amounts from all payment objs
#         tenant_balances=[]
#         monthly_bill_members=[] #list of monthlybill amounts from monthly charge objs

#         update_login_history("reports",current_user)

#         for apartment in apartment_list:
#             db.session.expire(apartment)
#             ######################################
#             tenants = tenantauto(apartment.id)
#             for i in tenants:
#                 db.session.expire(i)
#                 bal_item = i.balance
#                 tenant_balances.append(bal_item)
#             #######################################
#             monthly_bills = apartment.monthlybills
#             for item in monthly_bills:
#                 if item.month == present_month and item.year == present_year:
#                     sum_member = item.total_bill
#                     monthly_bill_members.append(sum_member) #TODO vacated tenant whose bills have been discarded will have no record of water charges here, rectify this.

#             payment_collection = apartment.payment_data
#             for item in payment_collection:
#                 if item.pay_period.month == present_month and item.pay_period.year == present_year and not item.voided:
#                     sum_member = item.amount
#                     monthly_collection.append(sum_member)

#         monthly_bill_total = sum_positive_values(monthly_bill_members)
#         monthly_total = sum_positive_values(monthly_collection)
#         monthlybal_total = sum_positive_values(tenant_balances)
#         ############################################################    
#         formatted_monthly_bill_total = (f"{monthly_bill_total:,}")    
#         formatted_monthly_total = (f"{monthly_total:,}")
#         formatted_monthlybal_total = (f"{monthlybal_total:,}")
#         return Response(render_template(
#             "reports.html",
#             delay=delay,
#             tenantlist=[],
#             month_string=get_str_month(present_month),
#             monthly_bills = formatted_monthly_bill_total,
#             monthly_rent_collection=formatted_monthly_total,
#             monthly_bal=formatted_monthlybal_total,
#             suggestions=generate_suggestions(apartment_list),
#             logopath=logo(current_user.company)[0],
#             mobilelogopath=logo(current_user.company)[1],
#             parent=logo(current_user.company)[5],
#             name=current_user.name))


class ReportsTwo(Resource):
    """report class"""
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'report_empty_account_statement.html',
            props=apartment_list,
            name=current_user.name,
            tenant_obj = None,
            prop = "",
            prop_obj = None,
            co=current_user.company,
            tenantlist=[],
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1]
        ))

class SalesStatement(Resource):
    """report class"""
    @login_required
    def get(self):
        prop = request.args.get('selected_apartment')
        if not prop:
            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_sales.html',
                props=apartment_list,
                name=current_user.name,
                tenant_obj = None,
                prop = "",
                prop_obj = None,
                co=current_user.company,
                tenantlist=[],
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))

        else:
            bills = []
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            invoices = prop_obj.monthlybills
            for bill in invoices:
                bill_item = MonthlyChargeOp.view_crm(bill)
                bills.append(bill_item)

            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_sales.html',
                props=apartment_list,
                name=current_user.name,
                prop = prop,
                prop_obj = prop_obj,
                bills=bills,
                co=current_user.company,
                tenantlist=[],
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))

class ReportsThree(Resource):
    """report class"""
    @login_required
    def get(self):

        delay = "no" if os.getenv("CURRENT_APP") == "app2" else "no"
        time = datetime.datetime.now()
        present_month = time.month
        present_year = time.year
        # apartment_list = fetch_all_apartments_by_user(current_user)
        apartment_list = []

        monthly_collection=[] #list of amounts from all payment objs
        tenant_balances=[]
        monthly_bill_members=[] #list of monthlybill amounts from monthly charge objs

        update_login_history("reports",current_user)

        for apartment in apartment_list:
            db.session.expire(apartment)
            ######################################
            tenants = tenantauto(apartment.id)
            for i in tenants:
                db.session.expire(i)
                bal_item = i.balance
                tenant_balances.append(bal_item)
            #######################################
            monthly_bills = apartment.monthlybills
            for item in monthly_bills:
                if item.month == present_month and item.year == present_year:
                    sum_member = item.total_bill
                    monthly_bill_members.append(sum_member) #TODO vacated tenant whose bills have been discarded will have no record of water charges here, rectify this.

            payment_collection = apartment.payment_data
            for item in payment_collection:
                if item.pay_period.month == present_month and item.pay_period.year == present_year and not item.voided:
                    sum_member = item.amount
                    monthly_collection.append(sum_member)

        monthly_bill_total = sum_positive_values(monthly_bill_members)
        monthly_total = sum_positive_values(monthly_collection)
        monthlybal_total = sum_positive_values(tenant_balances)
        ############################################################    
        formatted_monthly_bill_total = (f"{monthly_bill_total:,}")    
        formatted_monthly_total = (f"{monthly_total:,}")
        formatted_monthlybal_total = (f"{monthlybal_total:,}")
        return Response(render_template(
            "reportsthree.html",
            delay=delay,
            tenantlist=[],
            month_string=get_str_month(present_month),
            monthly_bills = formatted_monthly_bill_total,
            monthly_rent_collection=formatted_monthly_total,
            monthly_bal=formatted_monthlybal_total,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            parent=logo(current_user.company)[5],
            name=current_user.name))


class Assetisha(Resource):
    def get(self, id_number):
        return {"report":"Report Unavailable"},404

class BalanceReport(Resource):
    """class"""
    def get(self):
        prop = request.args.get("prop")
        contact = request.args.get("contact")

        if "@" in contact:
            print("not a valid telephone number")
            tel = ""
        else:
            tel = sms_phone_number_formatter(contact)

        if tel:
            recipient = [tel]

            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            bills = prop_obj.monthlybills

            actualbills = fetch_current_billing_period_bills(prop_obj.billing_period,bills)

            time = datetime.datetime.now() + relativedelta(hours=3)

            sms_text = f"Balances for [{prop}] as of {time.strftime('%d/%m/%Y')}: "
            second_line = "\n\nHouse & Balance"
            sms_text += second_line

            start = 1
            for bill in actualbills:
                if bill.balance > 1:

                    new_line = f"\n{bill.house}:  {bill.balance:,.0f}"
                    start += 1
                    sms_text += new_line

            print("TEXT SENT:",sms_text)

            if prop_obj.company.sms_provider == "Advanta":
                sms_sender(prop_obj.company.name,sms_text,tel)
            else:
                try:
                    notify = sms.send(sms_text, recipient,sender)
                    print(notify)
                except Exception as e:
                    print("sending logs failed",e)
        else:
            print("Telephone not provided")

        

class RentReport(Resource):
    """report class"""
    @login_required
    def get(self):
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        apartments = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            "rent_report.html",
            props=apartments,
            tenantlist=[],
            month_list=month_list,
            year_list=year_list,
            suggestions=generate_suggestions(apartments),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    @login_required
    def post(self):
        prop = request.form.get("prop")
        year = request.form.get("year")
        month = request.form.get("month")

        present_year = datetime.datetime.now().year
        present_month = datetime.datetime.now().month

        if not year:
            int_year = present_year
        else:
            int_year = int(year)

        if not month:
            int_month = present_month
        else:
            int_month = get_numeric_month(month)

        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
        monthly_bills = prop_obj.monthlybills

        raw_target_bills = []
        rent_sum_members = []
        deposit_sum_members = []

        for bill in monthly_bills:
            if bill.year == int_year and bill.month == int_month:
                raw_target_bills.append(bill)

        target_bills = []
        for item in raw_target_bills:
            new_item = MonthlyChargeOp.minimal_view(item)
            target_bills.append(new_item)

            deposit = bill.deposit if bill.deposit else 0.0
            rent_sum_members.append(item.rent)
            deposit_sum_members.append(deposit)

        # for n in target_bills:
        #     start += 1
        #     n['rentdeposit'] = 0.0
        #     n['waterdeposit'] = 0.0
        #     n['pos'] = start

        #get new tenants to fetch their deposits
        
        # new_tenants = new_tenants_injector(prop_obj.id,int_month,int_year)
        # for i in new_tenants:

        #     for n in target_bills:
        #         if i.id == n['tenantid']:
        #             house_obj = check_house_occupied(i)[1]
        #             n['rentdeposit'] = house_obj.housecode.rentrate
        #             n['waterdeposit'] = house_obj.housecode.waterdep


        vacants = filter_out_occupied_houses(prop)
        for vac in vacants:
            new_item = {
                'house':vac.name,
                'tenant':"--VACANT--",
                'vacancy':"text-danger",
                'space':vac.description,
                'rent':0.0,
                'dep': 0.0
            }
            target_bills.append(new_item)
        
        rent_sum = sum_values(rent_sum_members)
        dep_sum = sum_values(deposit_sum_members)

        grand_total = rent_sum+dep_sum
        
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        str_month = get_str_month(int_month)
        timeline = f'{str_month} - {int_year}'

        props = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'rent_report.html',
            tenantlist=[],
            bills=target_bills,
            paging=page(target_bills),
            renttotal=(f"{rent_sum:,}"),
            deposittotal=(f"{dep_sum:,}"),
            grandtotal=(f"{grand_total:,}"),
            props = props,
            prop=prop,
            month_list=month_list,
            year_list=year_list,
            timeline=timeline,
            suggestions=generate_suggestions(props),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name
        )) 

class Settings(Resource):
    """report class"""
    @login_required
    def get(self):
        return Response(render_template(
            'settings.html',
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name
        ))
    @login_required
    def post(self):
        date = request.form.get("date")
        prop = request.form.get("prop")
        rate = request.form.get("rate")
        if prop:
            props = [prop]
        else:
            raw_props = fetch_all_apartments_by_user(current_user)
            props = stringify_list_items(raw_props)

        logopath = logo(current_user.company)[1]

        for prop in props:
            auto_generate_report(request,prop,logopath,rate,date)

        # msg = "settings saved"
        # flash(msg,"success")

        return redirect(url_for('api.settings'))


class CombinedReportSummary(Resource):
    """report class"""
    @login_required
    def get(self):

        prop = request.args.get('prop')
        selected_month = request.args.get('month')

        if not prop:

            apartments = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_landlord_summary.html',
                props=apartments,
                tenantlist=[],
                suggestions=generate_suggestions(apartments),
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name
            ))

        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()


        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
        db.session.expire(prop_obj)
        monthly_bills = prop_obj.monthlybills

        rent_collection = []
        water_collection = []
        e_collection = []
        deposit_collection = []

        for bill in monthly_bills:
            if bill.month == target_period.month and bill.year == target_period.year:
                deposit = bill.deposit if bill.deposit else 0.0
                rent_collection.append(bill.rent_paid)
                deposit_collection.append(deposit)

        raw_charges = prop_obj.charges
        charges = []
        echarges = []
        # for c in raw_charges:
        #     if c.charge_type_id == 2:
        #         charges.append(c)
        #     if c.charge_type_id == 5:
        #         echarges.append(c)

        # for waterbill in charges:
        #     if waterbill.date.year == target_period.year and waterbill.date.month == target_period.month:
        #         # if waterbill.house_id != 37: #TO DO
        #         water_collection_member = waterbill.amount
        #         water_collection.append(water_collection_member)

        # for ebill in echarges:
        #     if ebill.date.year == target_period.year and ebill.date.month == target_period.month:
        #         e_collection_member = ebill.amount
        #         e_collection.append(e_collection_member)

        renttotal = sum_values(rent_collection)
        watertotal = sum_values(water_collection)
        electricitytotal = sum_values(e_collection)
        depositcredit = sum_values(deposit_collection)

        credittotal = renttotal + watertotal + electricitytotal + depositcredit

        expenses = prop_obj.expenses
        current_month_expenses = []
        for exp in expenses:
            if exp.date.month == target_period.month and exp.status == "completed" and exp.expense_type != "remittance":
                current_month_expenses.append(exp)

        tokenamount = 0.0
        waterbillamount = 0.0
        salaries = 0.0
        miscellaneous = 0.0
        electricityservice = 0.0
        plumbingservice = 0.0
        depositrefund = 0.0
        paint = 0.0
        bills = []
        electricity_str_store = ""
        plumbing_str_store = ""
        paint_str_store = ""
        depositrefund_str_store = ""


        for item in current_month_expenses:
            if item.expense_type == "token":
                tokenamount += item.amount
                
            elif item.expense_type == "water_bill":
                waterbillamount += item.amount
            elif item.expense_type == "salaries":
                salaries += item.amount
            elif item.expense_type == "deposit_refund":
                depositrefund += item.amount
                depositrefund_str_store = depositrefund_str_store + " " + item.house if item.house and not item.house == "-" else ""
            elif item.expense_type == "electricity_service":
                electricityservice += item.amount
                electricity_str_store = electricity_str_store + " " + item.house if item.house and not item.house == "-" else ""
            elif item.expense_type == "plumbing_service":
                plumbingservice += item.amount
                plumbing_str_store = plumbing_str_store + " " + item.house if item.house and not item.house == "-" else ""
            elif item.expense_type == "paint":
                paint += item.amount
                paint_str_store = paint_str_store + " " + item.house if item.house and not item.house == "-" else ""
            else:
                bill = {
                    "name":item.name,
                    "amount":item.amount,
                    "targethouse":" - " + item.house if item.house and not item.house == "-" else ""
                }
                bills.append(bill)
                miscellaneous += item.amount

        commission = prop_obj.commission if prop_obj.commission else 0.0
        management_fee = renttotal*commission*0.01
        if commission:
            commission_percentage = f"({commission} %)"
        else:
            commission_percentage = ""

        if not commission:
            commission = prop_obj.int_commission if prop_obj.int_commission else 0.0
            management_fee = commission
       

        debittotal  = management_fee+tokenamount+waterbillamount+salaries+electricityservice+plumbingservice+miscellaneous+depositrefund+paint

        nettotal = credittotal-debittotal
        month=get_str_month(target_period.month)

        timeline = f"{month.upper()} - {target_period.year}"

        apartments = fetch_all_apartments_by_user(current_user)


        # stringwater = (f"{waterbillamount:,}") if waterbillamount > 0 else None
        # stringelec = (f"{electricityservice:,}") if electricityservice > 0 else None

        # elec = True if current_user.company == "Rikena Property Solutions" else False
        # watershow = False if prop_obj.name == "Joseph Muraya Apartments" else True

        return Response(render_template(
            'report_landlord_summary.html',
            tenantlist=[],
            bills=bills,
            renttotal=(f"{renttotal:,}"),
            watertotal=string_formatter(watertotal),
            electricitytotal=string_formatter(electricitytotal),
            depositcredit=string_formatter(depositcredit),
            credittotal=(f"{credittotal:,}"),
            managementfee=string_formatter(management_fee),
            commission_percentage=commission_percentage,
            tokenbill=string_formatter(tokenamount),
            waterbill=string_formatter(waterbillamount),
            salaries=string_formatter(salaries),
            electricityservice=string_formatter(electricityservice),
            plumbingservice=string_formatter(plumbingservice),
            plumbing_str_store=string_formatter_alt(plumbing_str_store),
            depositrefund_str_store=string_formatter_alt(depositrefund_str_store),
            electricity_str_store=string_formatter_alt(electricity_str_store),
            paint_str_store=string_formatter_alt(paint_str_store),
            paint=string_formatter(paint),
            depositrefund=string_formatter(depositrefund),
            otherexpenses=(f"{miscellaneous:,}"),
            debittotal=(f"{debittotal:,.2f}"),
            netamount=(f"{nettotal:,.2f}"),
            props = apartments,
            prop=prop,
            timeline=timeline,
            suggestions=generate_suggestions(apartments),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name
        )) 


class MonthlyStatement(Resource):
    """report class"""
    @login_required
    def get(self):

        prop = request.args.get('prop')
        selected_month = request.args.get('month')

        if not prop:

            apartments = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_monthly_statement.html',
                props=apartments,
                tenantlist=[],
                suggestions=generate_suggestions(apartments),
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name
            ))

        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()


        prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
        db.session.expire(prop_obj)
        monthly_bills = prop_obj.monthlybills

        rent_collection = []
        water_collection = []
        e_collection = []
        deposit_collection = []

        for bill in monthly_bills:
            if bill.month == target_period.month and bill.year == target_period.year:
                deposit = bill.deposit if bill.deposit else 0.0
                rent_collection.append(bill.rent)
                deposit_collection.append(deposit)

        raw_charges = prop_obj.charges
        charges = []
        echarges = []
        for c in raw_charges:
            if c.charge_type_id == 2:
                charges.append(c)
            if c.charge_type_id == 5:
                echarges.append(c)

        for waterbill in charges:
            if waterbill.date.year == target_period.year and waterbill.date.month == target_period.month:
                # if waterbill.house_id != 37: #TO DO
                water_collection_member = waterbill.amount
                water_collection.append(water_collection_member)

        for ebill in echarges:
            if ebill.date.year == target_period.year and ebill.date.month == target_period.month:
                e_collection_member = ebill.amount
                e_collection.append(e_collection_member)

        renttotal = sum_values(rent_collection)
        watertotal = sum_values(water_collection)
        electricitytotal = sum_values(e_collection)
        depositcredit = sum_values(deposit_collection)

        credittotal = renttotal + watertotal + electricitytotal + depositcredit

        expenses = prop_obj.expenses
        current_month_expenses = []
        for exp in expenses:
            if exp.date.month == target_period.month and exp.status == "completed":
                current_month_expenses.append(exp)

        tokenamount = 0.0
        waterbillamount = 0.0
        salaries = 0.0
        miscellaneous = 0.0
        electricityservice = 0.0
        plumbingservice = 0.0
        depositrefund = 0.0
        paint = 0.0
        bills = []
        electricity_str_store = ""
        plumbing_str_store = ""
        paint_str_store = ""
        depositrefund_str_store = ""


        for item in current_month_expenses:
            if item.expense_type == "token":
                tokenamount += item.amount
                
            elif item.expense_type == "water_bill":
                waterbillamount += item.amount
            elif item.expense_type == "salaries":
                salaries += item.amount
            elif item.expense_type == "deposit_refund":
                depositrefund += item.amount
                depositrefund_str_store = depositrefund_str_store + " " + item.house if item.house and not item.house == "-" else ""
            elif item.expense_type == "electricity_service":
                electricityservice += item.amount
                electricity_str_store = electricity_str_store + " " + item.house if item.house and not item.house == "-" else ""
            elif item.expense_type == "plumbing_service":
                plumbingservice += item.amount
                plumbing_str_store = plumbing_str_store + " " + item.house if item.house and not item.house == "-" else ""
            elif item.expense_type == "paint":
                paint += item.amount
                paint_str_store = paint_str_store + " " + item.house if item.house and not item.house == "-" else ""
            else:
                bill = {
                    "name":item.name,
                    "amount":item.amount,
                    "targethouse":" - " + item.house if item.house and not item.house == "-" else ""
                }
                bills.append(bill)
                miscellaneous += item.amount

        commission = prop_obj.commission if prop_obj.commission else 0.0
        management_fee = renttotal*commission*0.01
        if commission:
            commission_percentage = f"({commission} %)"
        else:
            commission_percentage = ""

        if not commission:
            commission = prop_obj.int_commission if prop_obj.int_commission else 0.0
            management_fee = commission
       

        debittotal  = management_fee+tokenamount+waterbillamount+salaries+electricityservice+plumbingservice+miscellaneous+depositrefund+paint

        nettotal = credittotal-debittotal
        month=get_str_month(target_period.month)

        timeline = f"{month.upper()} - {target_period.year}"

        apartments = fetch_all_apartments_by_user(current_user)


        # stringwater = (f"{waterbillamount:,}") if waterbillamount > 0 else None
        # stringelec = (f"{electricityservice:,}") if electricityservice > 0 else None

        # elec = True if current_user.company == "Rikena Property Solutions" else False
        # watershow = False if prop_obj.name == "Joseph Muraya Apartments" else True

        return Response(render_template(
            'report_monthly_statement.html',
            tenantlist=[],
            bills=bills,
            renttotal=(f"{renttotal:,}"),
            watertotal=string_formatter(watertotal),
            electricitytotal=string_formatter(electricitytotal),
            depositcredit=string_formatter(depositcredit),
            credittotal=(f"{credittotal:,}"),
            managementfee=string_formatter(management_fee),
            commission_percentage=commission_percentage,
            tokenbill=string_formatter(tokenamount),
            waterbill=string_formatter(waterbillamount),
            salaries=string_formatter(salaries),
            electricityservice=string_formatter(electricityservice),
            plumbingservice=string_formatter(plumbingservice),
            plumbing_str_store=string_formatter_alt(plumbing_str_store),
            depositrefund_str_store=string_formatter_alt(depositrefund_str_store),
            electricity_str_store=string_formatter_alt(electricity_str_store),
            paint_str_store=string_formatter_alt(paint_str_store),
            paint=string_formatter(paint),
            depositrefund=string_formatter(depositrefund),
            otherexpenses=(f"{miscellaneous:,}"),
            debittotal=(f"{debittotal:,.2f}"),
            netamount=(f"{nettotal:,.2f}"),
            props = apartments,
            prop=prop,
            timeline=timeline,
            suggestions=generate_suggestions(apartments),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name
        )) 

class SummarisedCombinedBill(Resource):
    """report class"""
    @login_required
    def get(self):
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        present_year = datetime.datetime.now().year

        apartments = fetch_all_apartments_by_user(current_user)
        raw_owners =  []
        for prop in apartments:
            owner_name = prop.owner
            raw_owners.append(owner_name)
        owners = remove_dups(raw_owners)

        return Response(render_template(
            'report_summarised_combined_bill.html',
            owners=owners,
            tenantlist=[],
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name
        ))

    @login_required
    def post(self):
        present_year = datetime.datetime.now().year
        present_month = datetime.datetime.now().month
        all_apartments_monthlybills = []
        apartment_combinedbill_objs = []
        plain_apartment_combinedbill_objs = []

        owner = request.form.get("owner")
        year = request.form.get("year")
        start_month = request.form.get("start_month")
        end_month = request.form.get("end_month")

        if start_month:
            start_month = get_numeric_month(start_month)
        else:
            start_month = present_month

        if not year:
            year = datetime.datetime.now().year
        else:
            year = int(year)

        if not end_month:
            end_month = present_month
        else:
            end_month = get_numeric_month(end_month)

        #######validate inputs##########

        if start_month>end_month:
            start_month = present_month

        # we are not in future yet, restriction applies
        if present_year==year:
            if end_month > present_month:
                end_month = present_month
            if start_month > present_month:
                start_month = present_month

        prop_list = fetch_all_apartments_by_user(current_user)
        owner_obj = OwnerOp.fetch_owner_by_uniquename(owner)
        target_apartments = owner_obj.apartments

        apartments_list = []
        for prop in prop_list:
            if prop in target_apartments:
                apartments_list.append(prop)
        # import pdb; pdb.set_trace()
        raw_all_apartments_monthlybills = []
        for apartment in apartments_list:
            item = apartment.monthlybills
            raw_all_apartments_monthlybills.append(item) #list of lists to one huge list

        unfiltered_bills = flatten(raw_all_apartments_monthlybills)
        year_filtered = []
        for bill in unfiltered_bills:
            if bill.year == year:
                year_filtered.append(bill)

        months = [*range(start_month, end_month +1, 1)]
        # print(start_month,end_month)
        # print(months)
        for bill in year_filtered:
            if bill.month in months:
                all_apartments_monthlybills.append(bill)

        for apart_item in apartments_list:
            apartment_bills = []
            total_bill_members = []
            total_paid_members = []
            total_balance_members = []
                
            for bill in all_apartments_monthlybills:
                if bill.apartment_id == apart_item.id:
                    apartment_bills.append(bill)

            for month in months:
                specific_month_bills = []
                for bill in apartment_bills:
                    if bill.month == month:
                        specific_month_bills.append(bill)

                for bill in specific_month_bills:
                    total_bill_member = bill.total_bill
                    total_bill_members.append(total_bill_member)

                    total_paid_member = bill.paid_amount
                    total_paid_members.append(total_paid_member)

                    total_balance_member = bill.balance
                    total_balance_members.append(total_balance_member)

                total_bills = 0.0
                for item in total_bill_members:
                    total_bills+=item

                totalbills = (f"{total_bills:,}")

                paid_totals = 0.0
                for item in total_paid_members:
                    paid_totals+=item

                paidtotals = (f"{paid_totals:,}")

                balances = 0.0
                for bal in total_balance_members:
                    if bal > 0.0:
                        balances+=bal

                bal = (f"{balances:,}")

                bill_obj = {
                    "year":year,
                    "month":get_str_month(month),
                    "apartment":apart_item.name,
                    "owner":apart_item.owner,
                    "total_bill":totalbills,
                    "total_paid":paidtotals,
                    "total_balance":bal
                }
                apartment_combinedbill_objs.append(bill_obj)

                plain_bill_obj = {
                    "year":year,
                    "month":get_str_month(month),
                    "apartment":apart_item.name,
                    "total_bill":total_bills,
                    "total_paid":paid_totals,
                    "total_balance":balances
                }#without comma formatting
                plain_apartment_combinedbill_objs.append(plain_bill_obj)

        total_balance_members = []
        total_paid_members = []
        total_bill_members = []

        for obj in plain_apartment_combinedbill_objs:
            total_bill_member = obj["total_bill"]
            total_bill_members.append(total_bill_member)

            total_paid_member = obj["total_paid"]
            total_paid_members.append(total_paid_member)

            total_balance_member = obj["total_balance"]
            total_balance_members.append(total_balance_member)

        total_bills = 0.0
        for item in total_bill_members:
            total_bills+=item

        totalbills = (f"{total_bills:,}")

        paid_totals = 0.0
        for item in total_paid_members:
            paid_totals+=item

        paidtotals = (f"{paid_totals:,}")

        balances = 0.0
        for bal in total_balance_members:
            if bal > 0.0:
                balances+=bal

        bal = (f"{balances:,}")


        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]

        apartments = fetch_all_apartments_by_user(current_user)
        raw_owners =  []
        for prop in apartments:
            owner_name = prop.owner
            raw_owners.append(owner_name)
        owners = remove_dups(raw_owners)

        return Response(render_template(
            'report_summarised_combined_bill.html',
            owners=owners,
            tenantlist=[],
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            year=year,
            startmonth=get_str_month(start_month) + " to",
            endmonth = get_str_month(end_month),
            bills=apartment_combinedbill_objs,
            billtotals=totalbills,
            paidbills=paidtotals,
            balances=bal,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name
        )) 

class InternalSummary(Resource):
    """class reports"""
    @login_required
    def get(self):
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        present_year = datetime.datetime.now().year

        apartment_list = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'report_internal_summary.html',
            tenantlist=[],
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            apartments = apartment_list,
            apartment="per property",
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name
        ))

    @login_required
    def post(self):
        present_year = datetime.datetime.now().year
        present_month = datetime.datetime.now().month
        all_apartments_monthlybills = []
        detailed_bills = []

        year = request.form.get("year")
        start_month = request.form.get("start_month")
        end_month = request.form.get("end_month")
        selected_apartment = request.form.get("selected_apartment")

        if start_month:
            start_month = get_numeric_month(start_month)
        else:
            start_month = 1

        if not year:
            year = datetime.datetime.now().year
        else:
            year = int(year)

        if not end_month:
            end_month = present_month
        else:
            end_month = get_numeric_month(end_month)

        #######validate inputs##########

        if start_month>end_month:
            start_month = 1 #restrict start_month to January

        # we are not in future yet, restriction applies
        if present_year==year:
            if end_month > present_month:
                end_month = present_month
            if start_month > present_month:
                start_month = present_month

        month_range = [*range(start_month, end_month +1, 1)]

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        items = apartment_obj.monthlybills

        year_filtered = [] #filter specific year bills
        for bill in items:
            if bill.year == year:
                year_filtered.append(bill)

        for bill in year_filtered:
            if bill.month in month_range:
                all_apartments_monthlybills.append(bill)
            
        for bill in all_apartments_monthlybills: # bills in specified months only
            bill_item = MonthlyChargeOp.view_detail(bill)
            detailed_bills.append(bill_item)

        total_bill_members = []
        total_paid_members = []
        total_balance_members = []

        for bill in all_apartments_monthlybills:
            total_bill_member = bill.total_bill
            total_bill_members.append(total_bill_member)

            total_paid_member = bill.paid_amount
            total_paid_members.append(total_paid_member)

            total_balance_member = bill.balance
            total_balance_members.append(total_balance_member)

        total_bills = 0.0
        for item in total_bill_members:
            total_bills+=item

        totalbills = (f"{total_bills:,}")

        paid_totals = 0.0
        for item in total_paid_members:
            paid_totals+=item

        paidtotals = (f"{paid_totals:,}")

        balances = 0.0
        for bal in total_balance_members:
            if bal > 0.0:
                balances+=bal

        bal = (f"{balances:,}")

        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        props = fetch_all_apartments_by_user(current_user)
        return Response(render_template(
            'report_internal_summary.html',
            prop=selected_apartment,
            apartments = props,
            tenantlist=[],
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            year=year,
            startmonth=get_str_month(start_month),
            endmonth = get_str_month(end_month),
            bills=detailed_bills,
            billtotals=totalbills,
            paidbills=paidtotals,
            balances=bal,
            suggestions=generate_suggestions(props),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name
        ))

class Balances(Resource):
    """class"""
    @login_required
    def get(self):
        print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
        txt = f"balances by {current_user.name}"
        send_internal_email_notifications(current_user.company.name,txt)

        # advanta_send_sms(txt,kiotanum,kiotapay_api_key,kiotapay_partner_id,"KEVMAREAL")

        target = request.args.get("target")

        apartment_list = fetch_all_apartments_by_user(current_user)
        main = []
        for prop in apartment_list:
            bills = prop.monthlybills
            if target == "old":
                targetbills = fetch_prev_billing_period_bills(prop.billing_period,bills)
            else:
                targetbills = fetch_current_billing_period_bills(prop.billing_period,bills)
            for i in targetbills:
                if not i.paid_amount and i.balance > 0:
                    main.append(i)

        bills = bill_details(main)

        return render_template("ajax_balances.html",bills=bills)


class ArrearsComparison(Resource):
    """class"""
    @login_required
    def get(self):
        print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        propid = request.args.get("propid")
        if not propid:
            props = fetch_all_apartments_by_user(current_user)
        else:
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            props = []
            props.append(prop)

        main = []

        for prop in props:
            monthlybills = prop.monthlybills
            period = prop.billing_period

            if period.month == 1:
                #TODO URGENT BY DECEMBER
                return "Reports failed"



            
            targetbills = []

            for bill in monthlybills:
                if bill.month == period.month and bill.year == period.year:
                    targetbills.append(bill)
                if bill.month == period.month-1 and bill.year == period.year:
                    targetbills.append(bill)

            houses = houseauto(prop.id)
            for hse in houses:
                pair = []

                for bill in targetbills:
                    if str(bill) == str(hse):
                        pair.append(bill)


                if len(pair) > 1:
                    elder = pair[0] if pair[0].month == period.month - 1 else pair[1]
                    child = pair[0] if pair[0].month == period.month else pair[1]

                    tname = child.tenant.name
                    fname = tname.split()[0]
                    house =  child.house.name
                    hst = f'{house} <span class="text-gray-600">({fname})</span>' 

                    arr_dict = {
                        "hst":hst,
                        "earr":elder.arrears,
                        "edue":elder.total_bill,
                        "epaid":elder.paid_amount,
                        "ebal":elder.balance,
                        "carr":child.arrears,
                        "cdue":child.total_bill,
                        "cpaid":child.paid_amount,
                        "cbal":child.balance,
                    }
                    main.append(arr_dict)
                
        return render_template("ajax_arrears.html",bills=main,elder=f"{get_str_month(period.month-1)}", child=f"{ get_str_month(period.month)}")

class PaymentsComparison(Resource):
    """class"""
    @login_required
    def get(self):

        target = request.args.get("target")

        main = []
        props = fetch_all_apartments_by_user(current_user)

        maintotal = 0.0
        maindue = 0.0
        maincp = 0.0
        mainbal = 0.0

        for prop in props:
            subtotal = 0.0
            subdue = 0.0
            subcp = 0.0
            subbal = 0.0
            if target == "old":
                targetbills = fetch_prev_billing_period_bills(prop.billing_period,prop.monthlybills)
            else:
                targetbills = fetch_current_billing_period_bills(prop.billing_period,prop.monthlybills)


            for i in targetbills:
                amount = 0.0
                individual_amounts = []

                tname = i.tenant.name
                fname = tname.split()[0]
                house =  i.house.name
                hst = f'{house} <span class="text-gray-600">({fname})</span>' 

                if target == "old":
                    all_payments = fetch_prev_billing_period_payments(prop.billing_period,i.house.payments)
                    all_payments += fetch_prev_billing_period_payments(prop.billing_period,i.house.split_payments)
                else:
                    all_payments = fetch_current_billing_period_payments(prop.billing_period,i.house.payments)
                    all_payments += fetch_current_billing_period_payments(prop.billing_period,i.house.split_payments)
                    

                for x in all_payments:
                    amount += x.amount

                    individual_amounts.append((f" <span class=\"text-black font--weight-bold small\">Kes </span>{x.amount:,.0f} "))

                values = ' '.join(map(str, individual_amounts))

                paydict = {
                    # "prop":f"<span>{prop.name}</span> <span class=\"hid\">totali</span",
                    "prop":f"<div class=\"divjust-end\"><span>{prop.name}</span></div>",
                    "hst":hst,
                    "values":values if values else "<span class = \"text-danger\">Not paid</span>",
                    "total":amount,
                    "due":i.total_bill,
                    "paid":i.paid_amount,
                    "balance":i.balance
                }

                main.append(paydict)
                subtotal += amount
                subdue += i.total_bill
                subcp += i.paid_amount
                subbal += i.balance

                maintotal += amount
                maindue += i.total_bill
                maincp += i.paid_amount
                mainbal += i.balance

            total_dict = {
                "outline":"bg-black",
                "prop":f"<div class=\"divjust-end\"><span>{prop.name}</span> <span class=\"text-info font-weight-bold text-4\">Subtotal</span></div>",
                # "prop":f"<span>{prop.name}</span> <span>hi</span> subtotal",
                "hst":"",
                "values":"-",
                "total": f"<span class=\"text-white font-weight-bold text-4\">{subtotal:,}</span>",
                "due":f"<span class=\"text-white-50 font-weight-bold text-4\">{subdue:,}</span>",
                "paid":f"<span class=\"text-white font-weight-bold text-4\">{subcp:,}</span>",
                "balance":f"<span class=\"text-warning font-weight-bold text-4\">{subbal:,}</span>"
                }

            main.append(total_dict)

        grand_total_dict = {
            "outline":"bg-black",
            "prop":f"<div class=\"divjust-end\"><span></span><span class=\"text-info font-weight-bold text-4\">Grand Total</span></div>",
            "hst":"",
            "values":"-",
            "total": f"<span class=\"text-white font-weight-bold text-4\">{maintotal:,}</span>",
            "due":f"<span class=\"text-white-50 font-weight-bold text-4\">{maindue:,}</span>",
            "paid":f"<span class=\"text-white font-weight-bold text-4\">{maincp:,}</span>",
            "balance":f"<span class=\"text-warning font-weight-bold text-4\">{mainbal:,}</span>"
        }
        main.append(grand_total_dict)
                
        return render_template("ajax_payments.html",bills=main,maintotal=f"{maintotal:,}",maindue=f"{maindue:,}",maincp=f"{maincp:,}",mainbal=f"{mainbal:,}")

class InternalDetail(Resource):
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        return Response(render_template(
            'report_internal_detailed.html',
            tenantlist=[],
            apartment_list=apartment_list,
            month_list=month_list,
            year_list=[2020,2021,2022,2024],
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        current_month_bill = []

        

        renttotal_sum_members = []
        watertotal_sum_members = []
        electricitytotal_sum_members = []
        garbagesectotal_sum_members = []
        depargtotal_sum_members = []
        finetotal_sum_members = []
        arrearstotal_sum_members = []
        billtotal_sum_members = []
        paidtotal_sum_members = []
        balancetotal_sum_members = []

        bill_list = []
        houses = []

        selected_apartment = request.form.get("selected_apartment")
        selected_month = request.form.get("selected_month")
        selected_year = request.form.get("selected_year")
        present_year = datetime.datetime.now().year

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        monthlybills = MonthlyChargeOp.fetch_all_monthlycharges_by_apartment_id(apartment_id)

        if selected_month:
            month =  get_numeric_month(selected_month)
        else:
            month = datetime.datetime.now().month

        if not selected_year:
            selected_year =  present_year
        else:
            selected_year = int(selected_year)
            
        str_month = get_str_month(month)
        
        for bill in monthlybills:
            if bill.month == month and bill.year == selected_year:
                current_month_bill.append(bill)

        for bill in current_month_bill:
            houses.append(bill.house)
            bill_item = MonthlyChargeOp.view_detail(bill)
            bill_list.append(bill_item)


            deposit = bill.deposit if bill.deposit else 0.0
            agreement = bill.agreement if bill.agreement else 0.0

            renttotal_sum_members.append(bill.rent)

            watertotal_sum_members.append(bill.water)

            electricitytotal_sum_members.append(bill.electricity)

            garbagesectotal_sum_members.append(bill.garbage)

            garbagesectotal_sum_members.append(bill.security)

            depargtotal_sum_members.append(agreement)

            depargtotal_sum_members.append(deposit)

            finetotal_sum_members.append(bill.penalty)

            arrearstotal_sum_members.append(bill.arrears)

            billtotal_sum_members.append(bill.total_bill)

            paidtotal_sum_members.append(bill.paid_amount)

            balancetotal_sum_members.append(bill.balance)

        vacants = filter_out_occupied_houses(apartment_obj.name)
        for vac in vacants:
            if vac in houses:
                continue
            all_charges = vac.charges
            water_charge = 0.0
            electricity_charge = 0.0
            for charge in all_charges:
                if charge.date.month == month and charge.date.year == selected_year and charge.charge_type_id == 2:
                    water_charge = charge.amount
                if charge.date.month == month and charge.date.year == selected_year and charge.charge_type_id == 5:
                    electricity_charge = charge.amount

            house_tenant = vac.name + "# " + "VACANT"

            new_item = {
                'hsetenant':house_tenant,
                'vacancy':"text-danger",
                'rent':0.0,
                'water':water_charge,
                'electricity':electricity_charge,
                'garbsec':0.0,
                'deparg':0.0,
                'fine': 0.0,
                'arrears': 0.0,
                'total': water_charge,
                'paid': water_charge,
                'payment_date': "N/A",
                'balance':0.0
            }
            bill_list.append(new_item)

            watertotal_sum_members.append(new_item['water'])
            electricitytotal_sum_members.append(new_item['electricity'])
            billtotal_sum_members.append(new_item['total'])
            paidtotal_sum_members.append(new_item['paid'])

        expenses = apartment_obj.expenses
        current_month_expenses = []

        expenses_amount = 0.0

        for exp in expenses:
            if exp.date.month == month and exp.date.year == selected_year and exp.status == "completed":
                current_month_expenses.append(exp)

        for item in current_month_expenses:
            expenses_amount += item.amount


        totalrent = sum_values(renttotal_sum_members)
        renttotal = (f"{totalrent:,}")

        totalwater = sum_values(watertotal_sum_members)
        watertotal = (f"{totalwater:,}")
        
        totalelectricity = sum_values(electricitytotal_sum_members)
        electricitytotal = (f"{totalelectricity:,}")

        totalgarbagesec = sum_values(garbagesectotal_sum_members)
        garbagesectotal = (f"{totalgarbagesec:,}")

        totaldeparg = sum_values(depargtotal_sum_members)
        depargtotal = (f"{totaldeparg:,}")

        totalfine = sum_values(finetotal_sum_members)
        finetotal = (f"{totalfine:,}")

        totalarrears = sum_positive_values(arrearstotal_sum_members)
        arrearstotal = (f"{totalarrears:,}")
        
        totalbill = sum_positive_values(billtotal_sum_members)
        billtotal = (f"{totalbill:,}")

        totalpaid = sum_values(paidtotal_sum_members)
        paidtotal = (f"{totalpaid:,}")

        totalbalance = sum_positive_values(balancetotal_sum_members)
        balancetotal = (f"{totalbalance:,}")

        # commission = totalrent * apartment_obj.commission * 0.01
        # str_commission = f'{apartment_obj.commission} %'
        # formatted_commission = (f"{commission:,.1f}")

        formatted_expenses = (f"{expenses_amount:,.1f}")

        if apartment_obj.commission:
            commission = totalrent * apartment_obj.commission * 0.01
            commission_percentage = f"({apartment_obj.commission} %)"

        else:
            commission = apartment_obj.int_commission
            commission_percentage = f"{commission} flat rate"

        netpay = totalpaid - commission - expenses_amount
        formatted_netpay = (f"{netpay:,.1f}")


        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        timeline = f"{str_month} / {selected_year}"

        return Response(render_template(
            'report_internal_detailed.html',
            prop=selected_apartment,
            tenantlist=[],
            year=selected_year,
            string_month = str_month,
            timeline = timeline,
            renttotal=renttotal,
            watertotal=watertotal,
            electricitytotal=electricitytotal,
            garbagesectotal=garbagesectotal,
            depargtotal=depargtotal,
            finetotal=finetotal,
            arrearstotal=arrearstotal,
            paidbills=paidtotal,
            billtotals=billtotal,
            balances=balancetotal,
            bills=bill_list,
            paging=page(bill_list),
            str_commission=commission_percentage,
            commission=commission,
            expenses=formatted_expenses,
            formatted_netpay=formatted_netpay,
            apartment_list=apartment_list,
            month_list=month_list,
            year_list=[2020,2021,2022,2024],
            apartment_name=selected_apartment,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name))

class InternalDetailAlt(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_general_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))

        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()



        current_month_bills = []

        renttotal_sum_members = []
        watertotal_sum_members = []
        electricitytotal_sum_members = []
        garbagesectotal_sum_members = []
        depargtotal_sum_members = []
        finetotal_sum_members = []
        arrearstotal_sum_members = []
        billtotal_sum_members = []
        paidtotal_sum_members = []
        balancetotal_sum_members = []

        bill_list = []
        houses = []



        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id
        monthlybills = MonthlyChargeOp.fetch_all_monthlycharges_by_apartment_id(apartment_id)

        
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                current_month_bills.append(bill)

        for bill in current_month_bills:
            houses.append(bill.house)
            bill_item = MonthlyChargeOp.view_detail(bill)
            bill_list.append(bill_item)


            deposit = bill.deposit if bill.deposit else 0.0
            agreement = bill.agreement if bill.agreement else 0.0

            renttotal_sum_members.append(bill.rent)

            watertotal_sum_members.append(bill.water)

            electricitytotal_sum_members.append(bill.electricity)

            garbagesectotal_sum_members.append(bill.garbage)

            garbagesectotal_sum_members.append(bill.security)

            depargtotal_sum_members.append(agreement)

            depargtotal_sum_members.append(deposit)

            finetotal_sum_members.append(bill.penalty)

            arrearstotal_sum_members.append(bill.arrears)

            billtotal_sum_members.append(bill.total_bill)

            paidtotal_sum_members.append(bill.paid_amount)

            balancetotal_sum_members.append(bill.balance)

        vacants = filter_out_occupied_houses(apartment_obj.name)
        for vac in vacants:
            if vac in houses:
                continue
            all_charges = vac.charges
            water_charge = 0.0
            electricity_charge = 0.0
            for charge in all_charges:
                if charge.date.month == target_period.month and charge.date.year == target_period.year and charge.charge_type_id == 2:
                    water_charge = charge.amount
                if charge.date.month == target_period.month and charge.date.year == target_period.year and charge.charge_type_id == 5:
                    electricity_charge = charge.amount

            house_tenant = vac.name + "# " + "VACANT"

            new_item = {
                'house':vac.name,
                'tenant':"vacant",
                'vacancy':"text-danger",
                'rent':0.0,
                'water':water_charge,
                'electricity':electricity_charge,
                'garbsec':0.0,
                'deposit':0.0,
                'fine': 0.0,
                'arrears': 0.0,
                'total': water_charge,
                'paid': water_charge,
                'payment_date': "N/A",
                'balance':0.0
            }
            bill_list.append(new_item)

            watertotal_sum_members.append(new_item['water'])
            electricitytotal_sum_members.append(new_item['electricity'])
            billtotal_sum_members.append(new_item['total'])
            paidtotal_sum_members.append(new_item['paid'])

        expenses = apartment_obj.expenses
        current_month_expenses = []

        expenses_amount = 0.0

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed":
                current_month_expenses.append(exp)

        for item in current_month_expenses:
            expenses_amount += item.amount


        totaldep = sum_values(depargtotal_sum_members)
        deptotal = (f"{totaldep:,}")

        totalrent = sum_values(renttotal_sum_members)
        renttotal = (f"{totalrent:,}")

        totalarrears = sum_positive_values(arrearstotal_sum_members)
        bbftotal = (f"{totalarrears:,}")
        
        totalbill = sum_positive_values(billtotal_sum_members)
        billtotal = (f"{totalbill:,}")

        totalpaid = sum_values(paidtotal_sum_members)
        paidtotal = (f"{totalpaid:,}")

        totalbalance = sum_positive_values(balancetotal_sum_members)
        bcftotal = (f"{totalbalance:,}")

        if apartment_obj.commission:
        
            commission = totalrent * apartment_obj.commission * 0.01

            commission_percentage = f"({apartment_obj.commission} %)"

        else:
            commission = apartment_obj.int_commission
            commission_percentage = f"{commission} flat rate"



        formatted_commission = (f"{commission:,.1f}")

        formatted_expenses = (f"{expenses_amount:,.1f}")

        # netpay = totalpaid - commission - expenses_amount
        # formatted_netpay = (f"{netpay:,.1f}")


        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        return Response(render_template(
            'report_general_statement.html',
            prop=selected_apartment,
            prop_obj=apartment_obj,
            tenantlist=[],
            timeline = timeline,
            deptotal=deptotal,
            renttotal=renttotal,
            bbftotal=bbftotal,
            paidtotal=paidtotal,
            billtotal=billtotal,
            bcftotal=bcftotal,
            bills=bill_list,
            paging=page(bill_list),
            commission_percentage=commission_percentage,
            commission=formatted_commission,
            expenses=formatted_expenses,
            apartment_list=props,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name))


class CombinedReport(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_combined_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                co=current_user.company,
                name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################
        current_month_bills = []
        house_ids = []
        detailed_bills = []

        bbftotal = 0.0

        renttotal = 0.0
        watertotal = 0.0
        garbagetotal = 0.0
        securitytotal = 0.0
        servicetotal = 0.0
        penaltytotal = 0.0
        deposittotal = 0.0

        amounttotal = 0.0
        billtotal = 0.0

        paidtotal = 0.0
        paid_rent = 0.0
        bcftotal = 0.0

        ###################################################################################################
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        db.session.expire(apartment_obj)

        # monthlybills = apartment_obj.monthlybills
        # for bill in monthlybills:
        #     if bill.month == target_period.month and bill.year == target_period.year:
        #         house_ids.append(bill.house_id)
        #         current_month_bills.append(bill)

        propid = apartment_obj.id
        month = target_period.month
        year = target_period.year
        current_month_bills = MonthlyChargeOp.fetch_all_monthlycharges_by_apartment_id_by_period(propid,month,year)

        ###################################################################################################
        availables = []
        for bill in current_month_bills:
            """compute subtotals"""
            # bill_item = LandlordSummaryOp.external_view(bill)
            bill_item = MonthlyChargeOp.view_detail(bill)
            detailed_bills.append(bill_item)

            total = bill.rent + bill.water + bill.garbage + bill.security + bill.maintenance + bill.deposit + bill.penalty
            total += bill.arrears if bill.arrears > 0 else 0.0

            amountdue = bill.arrears + bill.rent + bill.water + bill.garbage + bill.security + bill.maintenance + bill.deposit + bill.penalty

            bbftotal += bill.arrears if bill.arrears > 0 else 0.0

            renttotal += bill.rent
            watertotal += bill.water
            garbagetotal += bill.garbage
            securitytotal += bill.security
            servicetotal += bill.maintenance
            deposittotal += bill.deposit
            penaltytotal += bill.penalty

            billtotal += total if total > 0 else 0.0
            amounttotal += amountdue if amountdue > 0 else 0.0

            paidtotal += bill.paid_amount
            paid_rent += bill.rent_paid if bill.rent_paid else 0
            if bill.total_bill < 0:
                if bill.paid_amount:
                    bcftotal += bill.balance if bill.balance > 0 else 0.0 #refactor, negative total cannot lead to positive balance
                    bcftotal -= bill.paid_amount
                else:
                    bcftotal += bill.balance if bill.balance > 0 else 0.0
            else:
                bcftotal += bill.balance if bill.balance > 0 else 0.0
                
            availables.append(bill.house.name)

        vacants = filter_out_occupied_houses(apartment_obj.name)

        for vac in vacants:
            if vac.name in availables:
                continue
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)


        tbbf = (f"{bbftotal:,}")

        trent = (f"{renttotal:,}")
        twater = (f"{watertotal:,}")
        tgarbage= (f"{garbagetotal:,}")
        tsecurity = (f"{securitytotal:,}")
        tservice = (f"{servicetotal:,}")
        tdeposit = (f"{deposittotal:,}")
        tpenalty = (f"{penaltytotal:,}")


        tbill = (f"{billtotal:,}")
        tamount = f"{amounttotal:,}"
        tpaid = (f"{paidtotal:,}")
        tbcf= (f"{bcftotal:,}")

        expenses = apartment_obj.expenses
        expenses_amount = 0.0

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed" and exp.expense_type != "deposit_refund":
                expenses_amount += exp.amount

        loan = 0.0
  
        netrent = paid_rent

        formatted_netrent = (f"{netrent:,.1f}")

        if apartment_obj.commission:
            commission = netrent * apartment_obj.commission * 0.01
            commission_percentage = f"({apartment_obj.commission} %)"

        else:
            commission = apartment_obj.int_commission
            commission_percentage = f"{commission} flat rate"

        formatted_commision = (f"{commission:,.1f}")
        formatted_loan = (f"{loan:,.1f}")

        ll=0.0

        raw_netpay = netrent - commission - expenses_amount - loan - ll
        netpay = (f"{raw_netpay:,.1f}")

        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        fieldshow_loan =  "" if apartment_obj.id == 33 else "dispnone"

        return Response(render_template(
            'report_combined_statement.html',
            prop=selected_apartment,
            propid=propid,
            prop_obj=apartment_obj,
            
            fieldshow_loan=fieldshow_loan,
            tenantlist=[],
            timeline = timeline,

            bbftotal=tbbf,

            renttotal=trent,
            watertotal=twater,
            garbagetotal=tgarbage,
            securitytotal=tsecurity,
            servicetotal=tservice,
            deposittotal=tdeposit,
            penaltytotal=tpenalty,

            billtotal=tbill,
            amounttotal=tamount,
            paidtotal=tpaid,
            bcftotal=tbcf,

            expenses = f"{expenses_amount:,.1f}",
            loan = formatted_loan,
            formatted_netrent=formatted_netrent,
            commission=formatted_commision,
            commission_percentage=commission_percentage,
            netpay=netpay,
            bills=detailed_bills,
            paging=page(detailed_bills),
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            co=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

class CustomCombinedReport(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")
        target = request.args.get("target")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_custom_combined.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))


        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################
        house_ids = []
        detailed_bills = []

        totalrentarrears = 0.0
        totalrent = 0.0
        totalrentdue = 0.0
        totalrentpaid = 0.0
        totalrentbalance = 0.0

        utility = 0.0
        deposits = 0.0

        ###################################################################################################
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        db.session.expire(apartment_obj)

        llp = LandlordPaymentOp.fetch_current_llp(apartment_obj.id, target_period.month, target_period.year)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)

                """compute subtotals"""
                # bill_item = LandlordSummaryOp.external_view(bill)
                bill_item = MonthlyChargeOp.external_view(bill)
                detailed_bills.append(bill_item)

                totalrentarrears += bill.rent_balance
                totalrent += bill.rent
                totalrentdue += (bill.rent + bill.rent_balance)
                totalrentpaid += bill.rent_paid
                totalrentbalance += bill.rent_due

                utility += bill.water_paid + bill.garbage_paid + bill.security_paid + bill.maintenance_paid
                deposits += bill.deposit   

        vacants = filter_out_occupied_houses(apartment_obj.name)

        for vac in vacants:
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0.0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)



        renttotalarrears = (f"{totalrentarrears:,}")
        renttotal = (f"{totalrent:,}")
        renttotaldue = (f"{totalrentdue:,}")
        renttotalpaid = (f"{totalrentpaid:,}")
        renttotalbalance = (f"{totalrentbalance:,}")

        utilities = (f"{utility:,}")
        deposittotal = (f"{deposits:,}")

        try:
            ratio = (f"{(totalrentpaid/totalrentdue)*100:,.1f} %")
        except:
            ratio = f"0.0 %"


        expenses = apartment_obj.expenses
        expenses_amount = 0.0

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed" and exp.expense_type != "deposit_refund":
                expenses_amount += exp.amount

            
        netrent = totalrentpaid

        formatted_netrent = (f"{netrent:,.1f}")

        if apartment_obj.commission:
            commission = netrent * apartment_obj.commission * 0.01
            commission_percentage = f"{apartment_obj.commission:,.0f}%"

        else:
            commission = apartment_obj.int_commission
            commission_percentage = f"{commission} flat rate"


        formatted_commision = (f"{commission:,.1f}")
        grosspay = f"{(totalrentpaid - commission):,.1f}"

        llp_arr = llp.arrears if llp else 0.0

        raw_netpay = netrent - commission + deposits + utility - expenses_amount + llp_arr

        remitted = raw_netpay
        netpay = (f"{raw_netpay:,.1f}")

        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        if llp:
            llbal = f"{llp.arrears:.1f}"
        else:
            llbal = "0.0"

        template_vars = {
            "code":apartment_obj.id,
            "name":selected_apartment,
            "landlord":"",
            "ll_bbf":llbal,

            "tnt_bbf":totalrentarrears,
            "rent":totalrent,
            "expected":totalrentdue,
            "actual":totalrentpaid,
            "tnt_bcf":totalrentbalance,

            "utilities":utilities,
            "deposit":deposittotal,
            "expenses":expenses_amount,

            "commission":commission,
            "netpay":raw_netpay,

            "remitted":remitted,
            "ratio":ratio,

            "ll_bcf":0.0,
            "agent":current_user.name,
        }
        if target == "remit_data":
            return render_template('ajax_remit_template.html',vars=template_vars)

        remittances = None

        remits = remittances if remittances else llp_arr

        return Response(render_template(
            'report_custom_combined.html',
            selected_month=selected_month,
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            
            tenantlist=[],
            timeline = timeline,

            renttotalarrears=renttotalarrears,
            renttotal=renttotal,
            renttotaldue = renttotaldue,
            renttotalbalance = renttotalbalance,
            renttotalpaid = renttotalpaid,

            utilitiestotal=utilities,
            deposittotal=deposittotal,

            expenses = f"{expenses_amount:,.1f}",
            remits = f"{remits:,.1f}",

            formatted_netrent=formatted_netrent,
            commission=formatted_commision,
            commission_percentage=commission_percentage,
            gross=grosspay,
            netpay=netpay,
            bills=detailed_bills,
            llbal=llbal,
            paging="portrait",
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            reportmonth = datetime.datetime.now().strftime("%B"),
            name=current_user.name))

class ServiceStatement(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")
        target = request.args.get("target")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_servicecharge_statement.html',
                tenantlist=[],
                prop_obj=None,
                co=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)

        # CompanyOp.set_rem_quota(apartment_obj.company,960)

        ##################################################################################################
        house_ids = []
        detailed_bills = []

        totalbbf = 0.0
        totalrent = 0.0

        totalpaid = 0.0
        totalbcf = 0.0

        ###################################################################################################
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                """compute subtotals"""
                # bill_item = LandlordSummaryOp.external_view(bill)
                bill_item = MonthlyChargeOp.external_view(bill)
                detailed_bills.append(bill_item)

                totalbbf += bill.maintenance_balance if bill.maintenance_balance else 0.0
                totalrent += bill.maintenance if bill.maintenance else 0.0
                
                totalpaid += bill.maintenance_paid if bill.maintenance_paid else 0.0
                if bill.maintenance_due:
                    totalbcf += bill.maintenance_due if bill.maintenance_due > 0 else 0.0
        ###################################################################################################
   

        vacants = filter_out_owned_houses(apartment_obj.name)


        for vac in vacants:
            if vac.id in house_ids:
                continue
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)


        bbftotal = (f"{totalbbf:,}")

        renttotal = (f"{totalrent:,}")

        totalbill = totalbbf + totalrent
        billtotal = (f"{totalbill:,}")

        paidtotal = (f"{totalpaid:,}")

        bcftotal = (f"{totalbcf:,}")

        expense_list = []

        expenses = apartment_obj.expenses
        expenses_amount = 0.0
        remittances = 0.0

        exceptions = ["deposit refund", "remittance"]

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed" and exp.expense_type not in exceptions:
                expenses_amount += exp.amount

                if exp.expense_type == "deposit_refund":
                    ename = exp.name + "(Refund)"
                else:
                    ename = exp.name

                exp_dict = {
                    "house":exp.house,
                    "name":ename,
                    "amount":exp.amount,
                }
                expense_list.append(exp_dict)

            if exp.date.month == target_period.month and exp.status == "completed" and exp.expense_type == "remittance" and exp.expense_type != "deposit_refund":
                remittances += exp.amount



            
        netrent = totalpaid

        formatted_netrent = (f"{netrent:,.1f}")
        
        # commission = netrent * apartment_obj.commission * 0.01
        commission = 0

        # if apartment_obj.id == 33:
        #     loan = 0
        # else:
        #     loan = 0

        # if apartment_obj.commission:
        #     commission = netrent * apartment_obj.commission * 0.01
        #     commission_percentage = f"({apartment_obj.commission} %)"

        # else:
        #     commission = apartment_obj.int_commission
        #     commission_percentage = f"{commission} flat rate"

        # debits = commission + expenses_amount

        # formatted_debits = f"{debits:,.1f}"

        # formatted_commision = (f"{commission:,.1f}")
        # formatted_loan = (f"{loan:,.1f}")

        # llp_arr = llp.arrears if llp else 0.0 
            
        raw_netpay = netrent - commission - expenses_amount + remittances

        netpay = (f"{raw_netpay:,.1f}")

        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        fieldshow_loan =  "" if apartment_obj.id == 33 else "dispnone"

        try:
            ratio = (f"{(totalpaid/totalbill)*100:,.1f} %")
        except:
            ratio = f"0.0 %"

        llbal = "0.0"

        
        template_vars = {
            "code":apartment_obj.id,
            "name":selected_apartment,
            "landlord":"",
            "ll_bbf":llbal,

            "tnt_bbf":totalbbf,
            "rent":totalrent,
            "expected":totalbill,
            "actual":totalpaid,
            "tnt_bcf":totalbcf,

            "utilities":0.0,
            "deposit":0.0,

            "expenses":expenses_amount,

            "commission":commission,
            "netpay":raw_netpay,

            "remitted":raw_netpay,
            "ratio":ratio,

            "ll_bcf":0.0,
            "agent":current_user.name,
        }

        if target == "remit_data":
            return render_template('ajax_remit_template.html',vars=template_vars)

        remits = remittances if remittances else 0.0


        return Response(render_template(
            'report_servicecharge_statement.html',
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            selected_month=selected_month,
            fieldshow_loan=fieldshow_loan,
            tenantlist=[],
            timeline = timeline,
            bbftotal=bbftotal,
            renttotal=renttotal,
            billtotal=billtotal,
            paidtotal=paidtotal,
            bcftotal=bcftotal,
            expenses = f"{expenses_amount:,.1f}",
            remits = f"{remits:,.1f}",
            formatted_netrent=formatted_netrent,
            netpay=netpay,
            bills=detailed_bills,
            expenselist=expense_list,
            llbal=llbal,
            paging="portrait",
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            co=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

class RentStatement(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")
        target = request.args.get("target")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_rent_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                co=current_user.company,
                name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        llp = LandlordPaymentOp.fetch_current_llp(apartment_obj.id, target_period.month, target_period.year)

        ##################################################################################################
        house_ids = []
        detailed_bills = []

        totalbbf = 0.0
        totalrent = 0.0

        totalpaid = 0.0
        totalbcf = 0.0

        ###################################################################################################
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                """compute subtotals"""
                # bill_item = LandlordSummaryOp.external_view(bill)
                bill_item = MonthlyChargeOp.external_view(bill)
                detailed_bills.append(bill_item)

                if bill.rent_balance:
                    totalbbf += bill.rent_balance if bill.rent_balance > 0 else 0.0

                totalrent += bill.rent if bill.rent else 0.0
                totalpaid += bill.rent_paid if bill.rent_paid else 0.0

                if bill.rent_due:
                    totalbcf += bill.rent_due if bill.rent_due > 0 else 0.0
        ###################################################################################################
   

        vacants = filter_out_occupied_houses(apartment_obj.name)


        for vac in vacants:
            if vac.id in house_ids:
                continue
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)

        if apartment_obj.id == 137: #VERY URGENT
            paidll = 18500.0
        else:
            paidll = 0.0

        bbftotal = (f"{totalbbf:,}")

        renttotal = (f"{totalrent:,}")

        totalbill = totalbbf + totalrent
        billtotal = (f"{totalbill:,}")
        paidtotal = (f"{totalpaid:,}")
        bcftotal = (f"{totalbcf:,}")

        expense_list = []

        expenses = apartment_obj.expenses
        expenses_amount = 0.0
        remittances = 0.0
        

        exceptions = ["deposit refund", "remittance"]

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed" and exp.expense_type not in exceptions:
                expenses_amount += exp.amount

                if exp.expense_type == "deposit_refund":
                    ename = exp.name + "(Refund)"
                else:
                    ename = exp.name

                exp_dict = {
                    "house":exp.house,
                    "name":ename,
                    "amount":exp.amount,
                }
                expense_list.append(exp_dict)

            if exp.date.month == target_period.month and exp.status == "completed" and exp.expense_type == "remittance" and exp.expense_type != "deposit_refund":
                remittances += exp.amount



            
        netrent = totalpaid

        formatted_netrent = (f"{netrent:,.1f}")
        
        commission = netrent * apartment_obj.commission * 0.01

        if apartment_obj.id == 33:
            loan = 0
        else:
            loan = 0

        if apartment_obj.commission:
            commission = netrent * apartment_obj.commission * 0.01
            commission_percentage = f"({apartment_obj.commission} %)"

        else:
            commission = apartment_obj.int_commission
            commission_percentage = f"{commission} flat rate"

        debits = commission + expenses_amount + paidll

        formatted_debits = f"{debits:,.1f}"

        formatted_commision = (f"{commission:,.1f}")
        formatted_loan = (f"{loan:,.1f}")

        llp_arr = llp.arrears if llp else 0.0 
            
        raw_netpay = netrent - commission - expenses_amount - loan + remittances + llp_arr - paidll

        netpay = (f"{raw_netpay:,.1f}")

        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        fieldshow_loan =  "" if apartment_obj.id == 33 else "dispnone"

        try:
            ratio = (f"{(totalpaid/totalbill)*100:,.1f} %")
        except:
            ratio = f"0.0 %"

        if llp:
            llbal = f"{llp.arrears:.1f}"
        else:
            llbal = "0.0"

        totalpaid -= paidll
        paidtotal_alt = (f"{totalpaid:,}")
        
        template_vars = {
            "code":apartment_obj.id,
            "name":selected_apartment,
            "landlord":"",
            "ll_bbf":llbal,

            "tnt_bbf":totalbbf,
            "rent":totalrent,
            "expected":totalbill,
            "actual":totalpaid,
            "tnt_bcf":totalbcf,

            "utilities":0.0,
            "deposit":0.0,

            "expenses":expenses_amount,

            "commission":commission,
            "netpay":raw_netpay,

            "remitted":raw_netpay,
            "ratio":ratio,

            "ll_bcf":0.0,
            "agent":current_user.name,
        }

        if target == "remit_data":
            return render_template('ajax_remit_template.html',vars=template_vars)

        remits = remittances if remittances else llp_arr


        return Response(render_template(
            'report_rent_statement.html',
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            selected_month=selected_month,
            fieldshow_loan=fieldshow_loan,
            tenantlist=[],
            timeline = timeline,
            bbftotal=bbftotal,
            renttotal=renttotal,
            billtotal=billtotal,
            paidtotal=paidtotal,
            paidtotal_alt=paidtotal_alt,
            bcftotal=bcftotal,
            ratio=ratio,
            expenses = f"{expenses_amount:,.1f}",
            remits = f"{remits:,.1f}",
            paidll = f"{paidll:,.1f}",
            loan = formatted_loan,
            formatted_netrent=formatted_netrent,
            commission=formatted_commision,
            debits=formatted_debits,
            commission_percentage=commission_percentage,
            netpay=netpay,
            bills=detailed_bills,
            expenselist=expense_list,
            llbal=llbal,
            paging="portrait",
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            co=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

class TenantInvoice(Resource):
    """class"""
    def get(self,id_number,month,year,unit_number):
        curr_user = UserOp.fetch_user_by_national_id(id_number)
        if not curr_user:
            return {"message":"User not found"}, 404
        try:
            monthyear = month + "-" + year
        except:
            return {"message":"Bad url encoding"},404

        selected_month = monthyear

        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()


        props = curr_user.company.props
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

            if not tenant_obj:
                return {
                    "success":"false",
                    "message":f"unit number {unit_number} not occupied",
                    'unit_id':unit_number,
                    'occupied':"vacant",
                    "bill_details":{}
                    },404        

        except:
            return {
                "success":"false",
                "message":f"unit number {unit_number} format error",
                'unit_id':unit_number,
                'occupied':"",
                "bill_details":{}
                },404


        ###################################################################################################
        db.session.expire(tenant_obj)

        bill_item = None

        monthlybills = tenant_obj.monthly_charges
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                bill_item = bill
                break

        if bill_item:
            return {
                "success": "true",
                "message": "success",
                'unit_number': unit_number,
                'fname':fname,
                'lname':lname,
                "bill_details": {
                    "rent": bill.rent,
                    "water": bill.water,
                    "electricity":bill.electricity,
                    "garbage":bill.garbage,
                    "service":bill.maintenance,
                    "arrears": bill.arrears,
                    "total_due": bill.total_bill,
                    "paid": bill.paid_amount,
                    "balance": bill.balance,
                    "date": bill.date.strftime("%m-%d-%Y, %H:%M:%S"),
                }
            }, 200
        else:
            return {
                "success": "false",
                "message": "invoice not found",
                'unit_number': unit_number,
                "bill_details": {}
            }, 404

        # if bill_item:
        #     return {
        #         "success":"true",
        #         "message":"success",
        #         'unit_id':unit_number,
        #         'occupied':"true",
        #         "tenant_details":{
        #             "first_name":fname,
        #             "last_name":lname,
        #             "unit_number":unit_number,
        #             "phone_number":tenant_obj.phone,
        #             "check_in":tenant_obj.date.strftime("%m-%d-%Y, %H:%M:%S"),
        #             "deposit":deposit,
        #             "id":tenant_obj.national_id
        #             }
        #         },200
        # else:
        #     return {
        #         "success":"true",
        #         "message":"failed",
        #         'unit_id':unit_number,
        #         'occupied':"",
        #         "tenant_details":{
        #             "first_name":fname,
        #             "last_name":lname,
        #             "unit_number":unit_number,
        #             "phone_number":tenant_obj.phone,
        #             "check_in":tenant_obj.date.strftime("%m-%d-%Y, %H:%M:%S"),
        #             "deposit":deposit,
        #             "id":tenant_obj.national_id
        #             }
        #         },404


class RentNaiveraStatement(Resource):
    def get(self,id_number,month,year,prop):

        curr_user = UserOp.fetch_user_by_national_id(id_number)
        if not curr_user:
            return {"message":"User not found"}, 404
        else:
            current_user = curr_user

        selected_apartment = prop
        try:
            monthyear = month + "-" + year
        except:
            return {"message":"Bad url encoding"},404

        selected_month = monthyear
        target = request.args.get("target")

        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        if not apartment_obj:
            return "Apartment/Property not selected", 404
        llp = LandlordPaymentOp.fetch_current_llp(apartment_obj.id, target_period.month, target_period.year)

        ##################################################################################################
        house_ids = []
        detailed_bills = []

        totalbbf = 0.0
        totalrent = 0.0

        totalpaid = 0.0
        totalbcf = 0.0

        ###################################################################################################
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                """compute subtotals"""
                # bill_item = LandlordSummaryOp.external_view(bill)
                bill_item = MonthlyChargeOp.str_data(bill)
                detailed_bills.append(bill_item)

                if bill.rent_balance:
                    totalbbf += bill.rent_balance if bill.rent_balance > 0 else 0.0

                totalrent += bill.rent if bill.rent else 0.0
                totalpaid += bill.rent_paid if bill.rent_paid else 0.0

                if bill.rent_due:
                    totalbcf += bill.rent_due if bill.rent_due > 0 else 0.0
        ###################################################################################################
   

        vacants = filter_out_occupied_houses(apartment_obj.name)


        for vac in vacants:
            if vac.id in house_ids:
                continue
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)


        bbftotal = (f"{totalbbf:,}")

        renttotal = (f"{totalrent:,}")

        totalbill = totalbbf + totalrent
        billtotal = (f"{totalbill:,}")

        paidtotal = (f"{totalpaid:,}")

        bcftotal = (f"{totalbcf:,}")

        expense_list = []

        expenses = apartment_obj.expenses
        expenses_amount = 0.0
        remittances = 0.0

        exceptions = ["deposit refund", "remittance"]

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed" and exp.expense_type not in exceptions:
                expenses_amount += exp.amount

                if exp.expense_type == "deposit_refund":
                    ename = exp.name + "(Refund)"
                else:
                    ename = exp.name

                exp_dict = {
                    "house":exp.house,
                    "name":ename,
                    "amount":exp.amount,
                }
                expense_list.append(exp_dict)

            if exp.date.month == target_period.month and exp.status == "completed" and exp.expense_type == "remittance" and exp.expense_type != "deposit_refund":
                remittances += exp.amount



            
        netrent = totalpaid

        formatted_netrent = (f"{netrent:,.1f}")
        
        commission = netrent * apartment_obj.commission * 0.01

        if apartment_obj.id == 33:
            loan = 0
        else:
            loan = 0

        if apartment_obj.commission:
            commission = netrent * apartment_obj.commission * 0.01
            commission_percentage = f"({apartment_obj.commission} %)"

        else:
            commission = apartment_obj.int_commission
            commission_percentage = f"{commission} flat rate"

        debits = commission + expenses_amount

        formatted_debits = f"{debits:,.1f}"

        formatted_commision = (f"{commission:,.1f}")
        formatted_loan = (f"{loan:,.1f}")

        llp_arr = llp.arrears if llp else 0.0 
            
        raw_netpay = netrent - commission - expenses_amount - loan + remittances + llp_arr

        netpay = (f"{raw_netpay:,.1f}")

        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        fieldshow_loan =  "" if apartment_obj.id == 33 else "dispnone"

        try:
            ratio = (f"{(totalpaid/totalbill)*100:,.1f} %")
        except:
            ratio = f"0.0 %"

        if llp:
            llbal = f"{llp.arrears:.1f}"
        else:
            llbal = "0.0"

        
        template_vars = {
            "code":apartment_obj.id,
            "name":selected_apartment,
            "landlord":"",
            "ll_bbf":llbal,

            "tnt_bbf":totalbbf,
            "rent":totalrent,
            "expected":totalbill,
            "actual":totalpaid,
            "tnt_bcf":totalbcf,

            "utilities":0.0,
            "deposit":0.0,

            "expenses":expenses_amount,

            "commission":commission,
            "netpay":raw_netpay,

            "remitted":raw_netpay,
            "ratio":ratio,

            "ll_bcf":0.0,
            "agent":current_user.name,
        }

        if target == "remit_data":
            return render_template('ajax_remit_template.html',vars=template_vars)

        remits = remittances if remittances else llp_arr


        return {
            "records" : detailed_bills
        }

class DepositStatement(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        propid = request.args.get("propid")
        reporttype = request.args.get("reporttype")
        target = request.args.get("target")

        if target == "direct":
            prop_id = get_identifier(propid)
            select_options = "d-none"
            prop = ApartmentOp.fetch_apartment_by_id(prop_id)
            selected_apartment = prop.name

        elif selected_apartment:
            select_options = ""
            if selected_apartment:
                prop = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        else:
            prop = None
            select_options = ""

        company = current_user.company

        # CompanyOp.set_rem_quota(company,800)

        apartment_list = fetch_all_apartments_by_user(current_user)

        if not prop:
            return Response(render_template(
                'report_deposit_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                co=company,
                name=current_user.name))

        apartment_obj = prop

        ##################################################################################################
        detailed_bills = []
        ###################################################################################################
        db.session.expire(apartment_obj)

        deps = apartment_obj.deposits
        tenants = tenantauto(apartment_obj.id)
        totaldep = 0.0
        
        ###################################################################################################
        for bill in deps:
            """compute subtotals"""
            # bill_item = LandlordSummaryOp.external_view(bill)
            if bill.tenant not in tenants:
                continue

            if reporttype == "unrefunded":
                if bill.status == "refunded":
                    if bill.rentdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'DEP',
                            "deposit":f'{bill.rentdep:,.1f}',
                            "status":bill.status,
                            "amount":f'0.0'
                        }
                        detailed_bills.append(datadict)

                    if bill.waterdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'WDP',
                            "deposit":f'{bill.waterdep:,.1f}',
                            "status":bill.status,
                            "amount":f'0.0'
                        }
                        detailed_bills.append(datadict)

                    if bill.elecdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'EDP',
                            "deposit":f'{bill.elecdep:,.1f}',
                            "status":bill.status,
                            "amount":f'0.0'
                        }
                        detailed_bills.append(datadict)

                    if bill.otherdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'OTD',
                            "deposit":f'{bill.otherdep:,.1f}',
                            "status":bill.status,
                            "amount":f'0.0'
                        }
                        detailed_bills.append(datadict)

                else:
                    if bill.rentdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'DEP',
                            "status":bill.status,
                            "amount":f'{bill.rentdep:,.1f}'
                        }
                        totaldep += bill.rentdep

                        detailed_bills.append(datadict)

                    if bill.waterdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'WDP',
                            "status":bill.status,
                            "amount":f'{bill.waterdep:,.1f}'
                        }
                        totaldep += bill.waterdep

                        detailed_bills.append(datadict)

                    if bill.elecdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'EDP',
                            "status":bill.status,
                            "amount":f'{bill.elecdep:,.1f}'
                        }
                        totaldep += bill.elecdep

                        detailed_bills.append(datadict)

                    if bill.elecdep:
                        datadict = {
                            "house":bill.house,
                            "tenant":bill.tenant,
                            "datepaid":bill.date.strftime("%d/%b/%y"),
                            "paycode":'EDP',
                            "status":bill.status,
                            "amount":f'{bill.otherdep:,.1f}'
                        }
                        totaldep += bill.otherdep

                        detailed_bills.append(datadict)
            else:
                bill_item = TenantDepositOp.view(bill)
                detailed_bills.append(bill_item)
                totaldep += bill.total


        ###################################################################################################
        if reporttype == "unrefunded":
            template = "report_unrefunded_deposit_statement.html"
        else:
            template = "report_deposit_statement.html"
        return Response(render_template(
            template,
            select_options=select_options,
            prop=apartment_obj,
            propid=apartment_obj.id,
            bills=detailed_bills,
            deptotal=f'{totaldep:,.1f}',
            props=apartment_list,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            co=current_user.company,
            statementdate = datetime.datetime.today().strftime("%d/%B/%Y"),
            name=current_user.name))

class RentRemit(Resource):

    @login_required
    def post(self):

        propid = request.form.get("propid")
        tntbbf = request.form.get("tntbbf")
        mrent = request.form.get("mrent")
        expected = request.form.get("expected")
        actual = request.form.get("actual")
        tntbcf = request.form.get("tntbcf")
        ratio = request.form.get("ratio")

        expenses = request.form.get("expenses")
        deposit = request.form.get("deposit")
        utilities = request.form.get("utilities")
        commission = request.form.get("commission")

        llbbf = request.form.get("llbbf")
        payable = request.form.get("payable")
        paid = request.form.get("paid")

        llbcf = request.form.get("llbcf")
        agent = request.form.get("agent")

        try:

            prop = ApartmentOp.fetch_apartment_by_id(propid)

            remit_obj = LandlordRemittanceOp(propid,prop.name,prop.owner.name,tntbbf,mrent,expected,actual,tntbcf,ratio,expenses,deposit,utilities,commission,llbbf,payable,paid,llbcf,agent,prop.billing_period,propid,prop.company.id)
            remit_obj.save()

            return proceed
        except Exception as e:
            print(e)
            return err



class RemitStatement(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        # if not selected_apartment:

        #     apartment_list = fetch_all_apartments_by_user(current_user)

        #     return Response(render_template(
        #         'report_rent_remit.html',
        #         tenantlist=[],
        #         prop_obj=None,
        #         props=apartment_list,
        #         logopath=logo(current_user.company)[0],
        #         mobilelogopath=logo(current_user.company)[1],
        #         name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################

        detailed_bills = []

        ###################################################################################################
        if selected_apartment:
            apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
            db.session.expire(apartment_obj)

            monthlybills = apartment_obj.remits
        else:
            monthlybills = current_user.company.remits
            apartment_obj = None

        ###################################################################################################
        for bill in monthlybills:
            if bill.period.month == target_period.month and bill.period.year == target_period.year:

                bill_item = LandlordRemittanceOp.view(bill)
                detailed_bills.append(bill_item)



        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"
       

        return Response(render_template(
            'report_rent_remit.html',
            prop=selected_apartment,
            propid=apartment_obj.id if apartment_obj else "N/A",
            prop_obj=apartment_obj if apartment_obj else "N/A",
            
            tenantlist=[],
            timeline = timeline,

            bills=detailed_bills,
            paging=page(detailed_bills),
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            reportmonth = datetime.datetime.now().strftime("%B"),
            name=current_user.name))


class CustomReport(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_custom_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################
        current_month_bills = []
        house_ids = []
        detailed_bills = []

        bbftotal_sum_members = []

        renttotal_sum_members = []
        watertotal_sum_members = []
        garbagetotal_sum_members = []
        securitytotal_sum_members = []
        servicetotal_sum_members = []
        penaltytotal_sum_members = []
        deposittotal_sum_members = []

        billtotal_sum_members = []

        paidtotal_sum_members = []
        paid_rent = 0
        bcftotal_sum_members = []

        ###################################################################################################
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                current_month_bills.append(bill)

        ###################################################################################################
        
        for bill in current_month_bills:
            """compute subtotals"""
            # bill_item = LandlordSummaryOp.external_view(bill)
            bill_item = MonthlyChargeOp.view_detail(bill)
            detailed_bills.append(bill_item)

            bff = bill.arrears
            rent = bill.rent
            water = bill.water
            garbage = bill.garbage
            security = bill.security
            service = bill.maintenance
            deposit = bill.deposit
            penalty = bill.penalty

            total = bff + rent + water + garbage + security + service + deposit + penalty

            paid = bill.paid_amount
            paid_rent += bill.rent_paid if bill.rent_paid else 0
            paid_rent += bill.maintenance_paid if bill.maintenance_paid else 0
            bcf = bill.balance
            # bbf = 18900 if bill.tenant_id == 86 and bill.month == 4 else 0.0

            bbftotal_sum_members.append(bff)

            renttotal_sum_members.append(rent)
            watertotal_sum_members.append(water)
            garbagetotal_sum_members.append(garbage)
            securitytotal_sum_members.append(security)
            servicetotal_sum_members.append(service)
            deposittotal_sum_members.append(deposit)
            penaltytotal_sum_members.append(penalty)

            billtotal_sum_members.append(total)

            paidtotal_sum_members.append(paid)
            bcftotal_sum_members.append(bcf)

   

        vacants = filter_out_occupied_houses(apartment_obj.name)
        print("rents",billtotal_sum_members)

        for vac in vacants:
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)


        totalbbf = sum_values(bbftotal_sum_members)
        bbftotal = (f"{totalbbf:,}")

        totalrent = sum_values(renttotal_sum_members)
        renttotal = (f"{totalrent:,}")

        totalwater = sum_values(watertotal_sum_members)
        watertotal = (f"{totalwater:,}")

        totalgarbage = sum_values(garbagetotal_sum_members)
        garbagetotal = (f"{totalgarbage:,}")

        totalsecurity = sum_values(securitytotal_sum_members)
        securitytotal = (f"{totalsecurity:,}")

        totalservice = sum_values(servicetotal_sum_members)
        servicetotal = (f"{totalservice:,}")

        totaldeposit = sum_values(deposittotal_sum_members)
        deposittotal = (f"{totaldeposit:,}")

        totalpenalty = sum_values(penaltytotal_sum_members)
        penaltytotal = (f"{totalpenalty:,}")


        totalbill = sum_values(billtotal_sum_members)
        billtotal = (f"{totalbill:,}")

        totalpaid = sum_values(paidtotal_sum_members)
        paidtotal = (f"{totalpaid:,}")

        totalbcf = sum_positive_values(bcftotal_sum_members)
        bcftotal = (f"{totalbcf:,}")

        expenses = apartment_obj.expenses
        expenses_amount = 0.0

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed" and exp.expense_type != "deposit_refund":
                expenses_amount += exp.amount

 
        loan = 0

            
        netrent = paid_rent

        formatted_netrent = (f"{netrent:,.1f}")

        if apartment_obj.commission:
        
            commission = netrent * apartment_obj.commission * 0.01

            commission_percentage = f"({apartment_obj.commission} %)"

        else:
            commission = apartment_obj.int_commission
            commission_percentage = f"{commission} flat rate"




        formatted_commision = (f"{commission:,.1f}")

        ll=0.0

        # raw_netpay = netrent - commission - expenses_amount - ll
        raw_netpay = netrent - commission - expenses_amount - ll

        netpay = (f"{raw_netpay:,.1f}")

        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        

        return Response(render_template(
            'report_custom_statement.html',
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            
            tenantlist=[],
            timeline = timeline,
            bbftotal=bbftotal,

            renttotal=renttotal,
            watertotal=watertotal,
            garbagetotal=garbagetotal,
            securitytotal=securitytotal,
            servicetotal=servicetotal,
            deposittotal=deposittotal,
            penaltytotal=penaltytotal,

            billtotal=billtotal,
            paidtotal=paidtotal,
            bcftotal=bcftotal,
            expenses = f"{expenses_amount:,.1f}",
            formatted_netrent=formatted_netrent,
            commission=formatted_commision,
            commission_percentage=commission_percentage,
            netpay=netpay,
            bills=detailed_bills,
            paging=page(detailed_bills),
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

class WaterStatement(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")
        targettype = request.args.get("targettype")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_water_statement.html',
                tenantlist=[],
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################
        current_month_bills = []
        house_ids = []
        detailed_bills = []

        bbftotal_sum_members = []
        renttotal_sum_members = []
        billtotal_sum_members = []

        paidtotal_sum_members = []
        bcftotal_sum_members = []

        ###################################################################################################
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                current_month_bills.append(bill)

        ###################################################################################################

        if targettype == 'water':
            template = "report_water_statement.html"
            for bill in current_month_bills:
                """compute subtotals"""
                # bill_item = LandlordSummaryOp.external_view(bill)
                bill_item = MonthlyChargeOp.external_view(bill)
                detailed_bills.append(bill_item)

                bbf = bill.water_balance if bill.water_balance else 0.0
                water = bill.water if bill.water else 0.0
                total = water + bbf
                paid = bill.water_paid if bill.water_paid else 0.0
                bcf = bill.water_due if bill.water_due else 0.0
                # bbf = 18900 if bill.tenant_id == 86 and bill.month == 4 else 0.0

                bbftotal_sum_members.append(bbf)
                renttotal_sum_members.append(water)
                billtotal_sum_members.append(total)

                paidtotal_sum_members.append(paid)
                bcftotal_sum_members.append(bcf)
        else:
            template = "report_electricity_statement.html"
            for bill in current_month_bills:
                """compute subtotals"""
                # bill_item = LandlordSummaryOp.external_view(bill)
                bill_item = MonthlyChargeOp.external_view(bill)
                detailed_bills.append(bill_item)

                bbf = bill.electricity_balance if bill.electricity_balance else 0.0
                elec = bill.electricity if bill.electricity else 0.0
                total = elec + bbf
                paid = bill.electricity_paid if bill.electricity_paid else 0.0
                bcf = bill.electricity_due if bill.electricity_due else 0.0
                # bbf = 18900 if bill.tenant_id == 86 and bill.month == 4 else 0.0

                bbftotal_sum_members.append(bbf)
                renttotal_sum_members.append(elec)
                billtotal_sum_members.append(total)

                paidtotal_sum_members.append(paid)
                bcftotal_sum_members.append(bcf)
   

        vacants = filter_out_occupied_houses(apartment_obj.name)
        print("rents",billtotal_sum_members)

        for vac in vacants:
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)


        totalbbf = sum_positive_values(bbftotal_sum_members)
        bbftotal = (f"{totalbbf:,}")

        totalrent = sum_values(renttotal_sum_members)
        renttotal = (f"{totalrent:,}")

        totalbill = sum_values(billtotal_sum_members)
        billtotal = (f"{totalbill:,}")

        totalpaid = sum_values(paidtotal_sum_members)
        paidtotal = (f"{totalpaid:,}")

        totalbcf = sum_positive_values(bcftotal_sum_members)
        bcftotal = (f"{totalbcf:,}")

            
        netrent = totalpaid

        formatted_netrent = (f"{netrent:,.1f}")
        
        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        

        return Response(render_template(
            template,
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            
            tenantlist=[],
            timeline = timeline,
            bbftotal=bbftotal,
            renttotal=renttotal,
            billtotal=billtotal,
            paidtotal=paidtotal,
            bcftotal=bcftotal,
            formatted_netrent=formatted_netrent,
            bills=detailed_bills,
            paging=page(detailed_bills),
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))


class LPFStatement(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_lpf_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################
        current_month_bills = []
        house_ids = []
        detailed_bills = []

        bbftotal_sum_members = []
        renttotal_sum_members = []
        billtotal_sum_members = []

        paidtotal_sum_members = []
        bcftotal_sum_members = []

        ###################################################################################################
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                current_month_bills.append(bill)

        ###################################################################################################
        
        for bill in current_month_bills:
            """compute subtotals"""
            # bill_item = LandlordSummaryOp.external_view(bill)
            bill_item = MonthlyChargeOp.external_view(bill)
            detailed_bills.append(bill_item)

            bbf = bill.penalty_balance if bill.penalty_balance else 0.0
            garbage = bill.penalty if bill.penalty else 0.0
            total = garbage + bbf
            paid = bill.penalty_paid if bill.penalty_paid else 0.0
            bcf = bill.penalty_due if bill.penalty_due else 0.0
            # bbf = 18900 if bill.tenant_id == 86 and bill.month == 4 else 0.0

            bbftotal_sum_members.append(bbf)
            renttotal_sum_members.append(garbage)
            billtotal_sum_members.append(total)

            paidtotal_sum_members.append(paid)
            bcftotal_sum_members.append(bcf)

   

        vacants = filter_out_occupied_houses(apartment_obj.name)
        print("rents",billtotal_sum_members)

        for vac in vacants:
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)


        totalbbf = sum_values(bbftotal_sum_members)
        bbftotal = (f"{totalbbf:,}")

        totalrent = sum_values(renttotal_sum_members)
        renttotal = (f"{totalrent:,}")

        totalbill = sum_values(billtotal_sum_members)
        billtotal = (f"{totalbill:,}")

        totalpaid = sum_values(paidtotal_sum_members)
        paidtotal = (f"{totalpaid:,}")

        totalbcf = sum_positive_values(bcftotal_sum_members)
        bcftotal = (f"{totalbcf:,}")

            
        netrent = totalpaid

        formatted_netrent = (f"{netrent:,.1f}")
        
        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        

        return Response(render_template(
            'report_lpf_statement.html',
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            
            tenantlist=[],
            timeline = timeline,
            bbftotal=bbftotal,
            renttotal=renttotal,
            billtotal=billtotal,
            paidtotal=paidtotal,
            bcftotal=bcftotal,
            formatted_netrent=formatted_netrent,
            bills=detailed_bills,
            paging=page(detailed_bills),
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

class GarbageStatement(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_garbage_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))



        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################
        current_month_bills = []
        house_ids = []
        detailed_bills = []

        bbftotal_sum_members = []
        renttotal_sum_members = []
        billtotal_sum_members = []

        paidtotal_sum_members = []
        bcftotal_sum_members = []

        ###################################################################################################
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                current_month_bills.append(bill)

        ###################################################################################################
        
        for bill in current_month_bills:
            """compute subtotals"""
            # bill_item = LandlordSummaryOp.external_view(bill)
            bill_item = MonthlyChargeOp.external_view(bill)
            detailed_bills.append(bill_item)

            bbf = bill.garbage_balance if bill.garbage_balance else 0.0
            garbage = bill.garbage if bill.garbage else 0.0
            total = garbage + bbf
            paid = bill.garbage_paid if bill.garbage_paid else 0.0
            bcf = bill.garbage_due if bill.garbage_due else 0.0
            # bbf = 18900 if bill.tenant_id == 86 and bill.month == 4 else 0.0

            bbftotal_sum_members.append(bbf)
            renttotal_sum_members.append(garbage)
            billtotal_sum_members.append(total)

            paidtotal_sum_members.append(paid)
            bcftotal_sum_members.append(bcf)

   

        vacants = filter_out_occupied_houses(apartment_obj.name)
        print("rents",billtotal_sum_members)

        for vac in vacants:
            new_item = {
                'id':"0",
                'delid':"0",
                'editid':"0",
                'house':vac.name,
                'tenant-alt':"--VACANT--",
                'vacancy':"text-danger",
                'arrears':0,
                'rent':0.0,
                'calc_total':0.0,
                'paid':0.0,
                'balance': 0.0
            }
            detailed_bills.append(new_item)


        totalbbf = sum_positive_values(bbftotal_sum_members)
        bbftotal = (f"{totalbbf:,}")

        totalrent = sum_values(renttotal_sum_members)
        renttotal = (f"{totalrent:,}")

        totalbill = sum_values(billtotal_sum_members)
        billtotal = (f"{totalbill:,}")

        totalpaid = sum_values(paidtotal_sum_members)
        paidtotal = (f"{totalpaid:,}")

        totalbcf = sum_positive_values(bcftotal_sum_members)
        bcftotal = (f"{totalbcf:,}")

            
        netrent = totalpaid

        formatted_netrent = (f"{netrent:,.1f}")
        
        props = fetch_all_apartments_by_user(current_user)
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        

        return Response(render_template(
            'report_garbage_statement.html',
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            
            tenantlist=[],
            timeline = timeline,
            bbftotal=bbftotal,
            renttotal=renttotal,
            billtotal=billtotal,
            paidtotal=paidtotal,
            bcftotal=bcftotal,
            formatted_netrent=formatted_netrent,
            bills=detailed_bills,
            paging=page(detailed_bills),
            props=props,
            apartment_name=selected_apartment,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            billids = get_obj_ids(detailed_bills),
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

class ListedProperties(Resource):
    @login_required
    def get(self):
        target_period = datetime.datetime.now()
        
        if current_user.username == "kiotapay":
            raw_props = ApartmentOp.fetch_all_apartments()
        else:
            raw_props = fetch_all_apartments_by_user(current_user)
        # new_props = ApartmentOp.fetch_all_apartments_createdby_user_id(current_user.id)
        # for i in new_props:
        #     raw_props.append(i)

        props = remove_dups(raw_props)

        items = []

        sum_tenants = 0
        sum_houses = 0
        
        for prop in props:
            tenants = len(tenantauto(prop.id))
            houses = len(prop.houses)
            try:
                occupancy = tenants/houses * 100
            except:
                occupancy = 0
                
            occ = f"{occupancy:,.0f}%"
            agent_user = UserOp.fetch_user_by_username(prop.agent_id)
            agent = agent_user.company if agent_user else "N/A"

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
                'occupancy':occ,
                'status':"active",
                'client-disp':"" if current_user.username.startswith("qc") else "dispnone",
                'createdby':prop.user_id,
            }

            sum_tenants += tenants
            sum_houses += houses

            items.append(dict_obj)

        overall_occupancy = sum_tenants/sum_houses * 100


        access = {
            'client-disp':"" if current_user.id == 1 else "dispnone"
        }
        
        str_month = get_str_month(target_period.month)
        timeline = f"{str_month.upper()} / {target_period.year}"

        return Response(render_template(
            'report_listed_properties.html',
            tenantlist=[],
            timeline = timeline,
            houses=sum_houses,
            tenants=sum_tenants,
            occupancy=f"{overall_occupancy:,.0f}%",
            access=access,
            items=items,
            paging=page(items),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))

class ExternalDetail(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)
            # suggestions = generate_suggestions(apartment_list)
            suggestions = []
            month_list = generate_month_list()
            return Response(render_template(
                'report_external_detailed.html',
                co=current_user.company,
                prop_obj=None,
                props=apartment_list,
                month_list=month_list,
                year_list=[2020,2021,2022,2024],
                suggestions=suggestions,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))


        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()
            
        ##################################################################################################
        current_month_bills = []
        current_month_summaries = []
        house_ids = []
        summary_house_ids = []
        detailed_bills = []

        billtotal_sum_members = []
        paidtotal_sum_members = []
        bcftotal_sum_members = []
        bbftotal_sum_members = []
        renttotal_sum_members = []
        watertotal_sum_members = []
        garbagetotal_sum_members = []
        securitytotal_sum_members = []
        deposittotal_sum_members = []

        ###################################################################################################
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        db.session.expire(apartment_obj)

        monthlybills = apartment_obj.monthlybills
        landlordsummaries = apartment_obj.landlordsummaries
        ###################################################################################################
        for bill in monthlybills:
            if bill.month == target_period.month and bill.year == target_period.year:
                house_ids.append(bill.house_id)
                current_month_bills.append(bill)
        for bill in landlordsummaries:
            if bill.month == target_period.month and bill.year == target_period.year:
                current_month_summaries.append(bill)
                summary_house_ids.append(bill.house_id)
        ###################################################################################################
        if not current_month_summaries:
            #create summary
            for bill in current_month_bills:

                bill_value = bill.rent + bill.water + bill.garbage + bill.security + bill.deposit
                
                if bill.balance > bill.rent *2 and  bill.deposit == 0 and bill.apartment_id in [3,4]:
                    paid = 0.0
                    bcf = bill_value

                else:
                    paid = bill_value
                    bcf = 0
                    
                summary = LandlordSummaryOp(target_period.year,target_period.month,bill.rent,bill.water,bill.garbage,bill.security,bill.electricity,bill.deposit,0,bill_value,paid,bcf,bill.apartment_id,bill.house_id,bill.tenant_id,bill.user_id)
                summary.save()
                current_month_summaries.append(summary)
        else:
            for house_id in house_ids:    
                                   
                if house_id not in summary_house_ids:
                    # target_bill = None
                    target_bill = MonthlyChargeOp.fetch_monthlycharge_by_house_id(house_id)
                    # for i in tenant_bills:
                    #     if i.month == month and i.year == selected_year:
                    #         target_bill = i

                    if target_bill:
                        bill_value = target_bill.rent + target_bill.water + target_bill.garbage + target_bill.security + target_bill.deposit
                        
                        if target_bill.balance > target_bill.rent *2 and  target_bill.deposit == 0 and target_bill.apartment_id in [3,4,33,34]:
                            paid = 0.0
                            bcf = bill_value

                        else:
                            paid = bill_value
                            bcf = 0
                            
                        summary = LandlordSummaryOp(target_period.year,target_period.month,target_bill.rent,target_bill.water,target_bill.garbage,target_bill.security,target_bill.electricity,target_bill.deposit,0,bill_value,paid,bcf,target_bill.apartment_id,target_bill.house_id,target_bill.tenant_id,target_bill.user_id)
                        summary.save()
                        current_month_summaries.append(summary)



        ###################################################################################################
        check_vacancies = []
        for bill in current_month_summaries:
            """compute subtotals"""
            bill_item = LandlordSummaryOp.external_view(bill)
            check_vacancies.append(bill.house_id)
            detailed_bills.append(bill_item)

            rent = bill.rent if bill.rent else 0.0
            water = bill.water if bill.water else 0.0
            garbage = bill.garbage if bill.garbage else 0.0
            security = bill.security if bill.security else 0.0
            deposit = bill.deposit if bill.deposit else 0.0
            bbf = bill.arrears if bill.arrears else 0.0
            total = bill.total_bill if bill.total_bill else 0.0
            paid = bill.paid_amount if bill.paid_amount else 0.0
            bcf = bill.balance if bill.balance else 0.0
            # bbf = 18900 if bill.tenant_id == 86 and bill.month == 4 else 0.0

            renttotal_sum_members.append(rent)
            watertotal_sum_members.append(water)
            garbagetotal_sum_members.append(garbage)
            securitytotal_sum_members.append(security)
            deposittotal_sum_members.append(deposit)

            billtotal_sum_members.append(total)
            paidtotal_sum_members.append(paid)
            bcftotal_sum_members.append(bcf)
            bbftotal_sum_members.append(bbf)

   

        vacants = filter_out_occupied_houses(apartment_obj.name)

        for vac in vacants:
            if vac.id in check_vacancies:
                continue

            all_charges = vac.charges
            water_charge = 0.0
            for charge in all_charges:
                if charge.date.month == target_period.month and charge.date.year == target_period.year and charge.charge_type_id == 2:
                    water_charge = charge.amount

            # if apartment_obj.id in [3,4,33,34]:
            if apartment_obj.id not in [4000000]:
                found = True if apartment_obj.id in [33,34] else False # URGENT TODO reconsider this condition
                recently_vacated_tenants = last_month_vacation_injector(apartment_obj.id)
                for item in recently_vacated_tenants:
                    if item.house_id == vac.id:
                        found = True
                        break


                if found:
                    # garbage_charge = vac.housecode.garbagerate
                    garbage_charge = 0.0
                else:
                    garbage_charge = 0.0
                

                # c_total = garbage_charge + water_charge
                c_total = 0

                new_item = {
                    'id':"0",
                    'delid':"0",
                    'editid':"0",
                    'house':vac.name,
                    'tenant':"--VACANT--",
                    'vacancy':"text-danger",
                    'rent':0.0,
                    'water':0.0,
                    'garbage':0.0,
                    'security':0.0,
                    'dep': 0.0,
                    'arrears':0,
                    'calc_total':c_total,
                    'paid':0.0,
                    'balance': 0.0
                }
                detailed_bills.append(new_item)

            else:
                new_item = {
                    'id':"0",
                    'delid':"0",
                    'editid':"0",
                    'house':vac.name,
                    'tenant':"--VACANT--",
                    'vacancy':"text-danger",
                    'rent':0.0,
                    'water':water_charge,
                    'garbage':0.0,
                    'security':0.0,
                    'dep': 0.0,
                    'arrears':0,
                    'calc_total':0.0,
                    'paid':0.0,
                    'balance': 0.0
                }
                detailed_bills.append(new_item)

            watertotal_sum_members.append(new_item['water'])
            garbagetotal_sum_members.append(new_item['garbage'])
            billtotal_sum_members.append(new_item['calc_total'])
            paidtotal_sum_members.append(new_item['paid'])


        totalbill = sum_values(billtotal_sum_members)
        billtotal = (f"{totalbill:,}")

        totalpaid = sum_values(paidtotal_sum_members)
        paidtotal = (f"{totalpaid:,}")

        totalbcf = sum_values(bcftotal_sum_members)
        bcftotal = (f"{totalbcf:,}")

        totalbbf = sum_values(bbftotal_sum_members)
        bbftotal = (f"{totalbbf:,}")

        totalrent = sum_values(renttotal_sum_members)
        renttotal = (f"{totalrent:,}")

        totalwater = sum_values(watertotal_sum_members)
        watertotal = (f"{totalwater:,}")

        totalgarbage = sum_values(garbagetotal_sum_members)
        garbagetotal = (f"{totalgarbage:,}")

        totalsecurity = sum_values(securitytotal_sum_members)
        securitytotal = (f"{totalsecurity:,}")

        totaldeposit = sum_values(deposittotal_sum_members)
        deposittotal = (f"{totaldeposit:,}")

        expenses = apartment_obj.expenses
        current_month_expenses = []
        expense_list = []
        expenses_amount = 0.0

        for exp in expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed":
                current_month_expenses.append(exp)

        for item in current_month_expenses:
            expenses_amount += item.amount

            if item.expense_type == "deposit_refund":
                ename = item.name + "(Refund)"
            else:
                ename = item.name

            exp = {
                "house":item.house,
                "name":ename,
                "amount":item.amount,
            }
            expense_list.append(exp)

        # mathrent = sum_values(mathrent_sum_members)
        # mathwater = sum_values(mathwater_sum_members)
        # mathgarb = sum_values(mathgarb_sum_members)
        # mathsec = sum_values(mathsec_sum_members)
        # mathdep = sum_values(mathdep_sum_members)

        mathrentt = totalpaid - totalwater - totalgarbage - totaldeposit

        # if apartment_obj.id in [3]:#TEMP
        #     journal_balance = -18900
        # else:
        #     journal_balance = 0
        journal_balance = 0
            
        netrent = mathrentt - journal_balance

        formatted_netrent = (f"{netrent:,.1f}")

        
        commission = netrent * apartment_obj.commission * 0.01

        if apartment_obj.id == 33:
            loan = 0
        else:
            loan = 0

        if commission:
            commission_percentage = f"({apartment_obj.commission} %)"
        else:
            commission_percentage = ""

        formatted_commision = (f"{commission:,.1f}")
        formatted_loan = (f"{loan:,.1f}")
            
        raw_netpay = netrent - commission - expenses_amount - loan + totaldeposit + totalwater
        netpay = (f"{raw_netpay:,.1f}")

        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        str_month = get_str_month(target_period.month)

        timeline = f"{str_month} / {target_period.year}"

        
        fieldshow_sec = "dispnone" if not totalsecurity else ""
        fieldshow_garb = "dispnone" if not totalgarbage else ""
        fieldshow_water = "dispnone" if not totalwater else ""
        fieldshow_dep = "dispnone" if not totaldeposit else ""

        fieldshow_loan =  "dispnone" if apartment_obj.id == 33 else "dispnone"

        

        # suggestions = generate_suggestions(apartment_list)
        suggestions = []

        return Response(render_template(
            'report_external_detailed.html',
            prop=selected_apartment,
            propid=apartment_obj.id,
            prop_obj=apartment_obj,
            
            fieldshow_sec=fieldshow_sec,
            fieldshow_garb=fieldshow_garb,
            fieldshow_water=fieldshow_water,
            fieldshow_dep=fieldshow_dep,
            fieldshow_loan=fieldshow_loan,
            tenantlist=[],
            timeline = timeline,
            billtotal=billtotal,
            paidtotal=paidtotal,
            bcftotal=bcftotal,
            bbftotal=bbftotal,
            renttotal=renttotal,
            watertotal=watertotal,
            garbagetotal=garbagetotal,
            securitytotal=securitytotal,
            deposittotal=deposittotal,
            expenses = expenses_amount,
            loan = formatted_loan,
            formatted_netrent=formatted_netrent,
            commission=formatted_commision,
            commission_percentage=commission_percentage,
            netpay=netpay,
            expenselist=expense_list,
            bills=detailed_bills,
            paging="landscape",
            props=apartment_list,
            suggestions=suggestions,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            co=current_user.company,
            billids = get_obj_ids(detailed_bills),
            name=current_user.name))

class ViewPayment(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")
        prop = request.args.get("prop")
        print("PROPPPPPP>>>>",prop)
        if target:
            print("I'M UNSTOPPABLE TODAY")
            prop = request.args.get("apartment")
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            tenants = tenantauto(prop_obj.id)
            vacated_tenants = tenantauto_reverse(prop_obj.id)
            house_tenant_list = generate_house_tenants_alt(tenants,vacated_tenants)
            return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant")

        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        
        apartment_list = fetch_all_apartments_by_user(current_user)
        # return Response(render_template('report_payments.html',props=apartment_list, name=current_user.name,tenantlist=[]))

        if not prop:
            return Response(render_template(
                'report_payments2.html',
                props=apartment_list,
                prop_obj=None,
                name=current_user.name,
                tenantlist=[],
                month_list=month_list,
                year_list=year_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))


        # present_year = datetime.datetime.now().year
        # present_month = datetime.datetime.now().month
        raw_payments_list = []
        payments_list = []
        
        year = request.args.get("year")
        mode = request.args.get("selected_mode")
        raw_tenant = request.args.get("selected_tenant")

        start_month = request.args.get("month")


        if start_month:
            datestring = date_formatter_alt(start_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        # end_month = request.args.get("end_month")

        # if start_month:
        #     start_month = get_numeric_month(start_month)
        # else:
        #     start_month = present_month

        # if not year:
        #     year = datetime.datetime.now().year
        # else:
        #     year = int(year)

        # if not end_month:
        #     end_month = present_month
        # else:
        #     end_month = get_numeric_month(end_month)

        # #######validate inputs##########

        # if start_month>end_month:
        #     start_month = present_month #restrict start_month to current month

        # # we are not in future yet, restriction applies
        # # if present_year==year:
    
        # #     if end_month-present_month == 1:
        # #         print("it got into this section")
        # #         pass
        # #     elif end_month > present_month:
        # #         print("never got here")
        # #         end_month = present_month
        # #     else:
        # #         pass

        # #     # if start_month > present_month:
        # #     #     start_month = present_month

        month_range = [*range(target_period.month, target_period.month +1, 1)]

        apartment_obj = ApartmentOp.fetch_apartment_by_name(prop)
        payments = apartment_obj.payment_data
        bills = apartment_obj.monthlybills

        if raw_tenant:
            if raw_tenant.startswith("Vac"):
                tenant_obj = extract_tenant(raw_tenant)
                tenant_id = tenant_obj.id
            else:
                house_obj = get_specific_house_obj_from_house_tenant_alt(apartment_obj.id,raw_tenant)
                tenant_obj = check_occupancy(house_obj)[1]
                tenant_id = tenant_obj.id

        else:
            tenant_id = None

        if mode and not tenant_id:
            target_bills = fetch_current_billing_period_bills(target_period,bills)
            for bill in payments:
                if bill.pay_period.month in month_range and bill.pay_period.year == target_period.year and not bill.voided and bill.paymode == mode:
                    raw_payments_list.append(bill)
        elif mode and tenant_id:
            bills = tenant_obj.monthly_charges
            target_bills = fetch_current_billing_period_bills(target_period,bills)
            for bill in payments:
                if bill.pay_period.month in month_range and bill.pay_period.year == target_period.year and not bill.voided and bill.paymode == mode and bill.tenant_id == tenant_id:
                    raw_payments_list.append(bill)
        elif tenant_id and not mode:
            bills = tenant_obj.monthly_charges
            target_bills = fetch_current_billing_period_bills(target_period,bills)
            for bill in payments:
                if bill.pay_period.month in month_range and bill.pay_period.year == target_period.year and not bill.voided and bill.tenant_id == tenant_id:
                    raw_payments_list.append(bill)
        else:
            target_bills = fetch_current_billing_period_bills(target_period,bills)
            for bill in payments:
                if not bill.pay_period:
                    
                    # PaymentOp.update_payment(bill,bill.date,0,0) #TODO quickfix for legacy payments
                    # print("Updating >>>>>>>>>>>>>>>>>>", bill.amount, bill.apartment, "Date>>>>>", bill.date.month)
                    pass
                else: 
                    if bill.pay_period.month in month_range and bill.pay_period.year == target_period.year and not bill.voided:
                        raw_payments_list.append(bill)

        # actual_payments = fetch_actual_payments(raw_payments_list)
        actual_payments = raw_payments_list

        for payment in actual_payments:
            pay_item = PaymentOp.view(payment)
            payments_list.append(pay_item)

        #####################################################################################################
        total_bill_members = []
        total_paid_members = []
        total_balance_members = []

        # items = apartment_obj.monthlybills

        # year_filtered = [] #filter specific year bills
        # for bill in items:
        #     if bill.year == year:
        #         year_filtered.append(bill)

        # for bill in year_filtered:
        #     if bill.month == end_month:
        #         monthlybills.append(bill)

        house_cluster = []

        for bill in actual_payments:
            total_bill_member = bill.charged_amount
            total_bill_members.append(total_bill_member)


            total_paid_member = bill.amount
            total_paid_members.append(total_paid_member)

            house_cluster.append(bill.house)

        # trimmed_cluster = remove_dups(house_cluster)
        # for i in trimmed_cluster:
        for i in target_bills:
            # actual_bill = max(i.monthlybills, key=lambda x: x.id)
            try:
                total_balance_member = i.balance if i.balance > 0 else 0.0
            except:
                total_balance_member = 0.0
            total_balance_members.append(total_balance_member)

        total_bills = sum_positive_values(total_bill_members)
        totalbills = (f"{total_bills:,}")

        paid_totals = sum_values(total_paid_members)
        paidtotals = (f"{paid_totals:,}")

        balances = sum_positive_values(total_balance_members)
        bal = (f"{balances:,}")
        ########################################################
        startmonth=get_str_month(target_period.month)
        endmonth = get_str_month(target_period.month)
        if startmonth == endmonth:
            timeline = f"{startmonth} / {target_period.year}"
        else:
            timeline = f"{startmonth} to {endmonth} / {target_period.year}"
        ########################################################

        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        return Response(render_template(
            'report_payments2.html',
            bills=payments_list,
            billtotals=totalbills,
            paidtotals=paidtotals,
            balances=bal,
            props=apartment_list,
            prop=prop,
            prop_obj=apartment_obj,
            apartment_name=prop,
            name=current_user.name,
            tenantlist=[],
            endmonth=endmonth,
            timeline=timeline,
            month_list=month_list,
            year_list=year_list,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company
        ))

class TenantStatement(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")
        if target:
            prop = request.args.get("apartment")
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            tenants = tenantauto(prop_obj.id)
            vacated_tenants = tenantauto_reverse(prop_obj.id)
            house_tenant_list = generate_house_tenants_alt(tenants,vacated_tenants)
            return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant")

        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        present_year = datetime.datetime.now().year
        
        apartment_list = fetch_all_apartments_by_user(current_user)
        # return Response(render_template('report_payments.html',props=apartment_list, name=current_user.name,tenantlist=[]))
        return Response(render_template(
            'report_tenant_statement.html',
            props=apartment_list,
            name=current_user.name,
            tenantlist=[],
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1]
        ))

    def post(self):
        present_year = datetime.datetime.now().year
        present_month = datetime.datetime.now().month
        
        year = request.form.get("year")
        mode = request.form.get("selected_mode")
        raw_tenant = request.form.get("selected_tenant")
        start_month = request.form.get("start_month")
        end_month = request.form.get("end_month")

        if start_month:
            start_month = get_numeric_month(start_month)
        else:
            start_month = 1

        if not year:
            year = datetime.datetime.now().year
        else:
            year = int(year)

        if not end_month:
            end_month = present_month
        else:
            end_month = get_numeric_month(end_month)

        #######validate inputs##########

        if start_month>end_month:
            start_month = 1 #restrict start_month to current month

        # we are not in future yet, restriction applies
        # if present_year==year:
    
        #     if end_month-present_month == 1:
        #         print("it got into this section")
        #         pass
        #     elif end_month > present_month:
        #         print("never got here")
        #         end_month = present_month
        #     else:
        #         pass

        #     # if start_month > present_month:
        #     #     start_month = present_month

        month_range = [*range(start_month, end_month +1, 1)]

        selected_apartment = request.form.get("selected_apartment")
        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)

        if raw_tenant:
            if raw_tenant.startswith("Vac"):
                tenant_obj = extract_tenant(raw_tenant)
                print("VACATED TENANT >>>>STATEMENT",tenant_obj.monthly_charges)
                tenant_id = tenant_obj.id
            else:
                house_obj = get_specific_house_obj_from_house_tenant_alt(apartment_obj.id,raw_tenant)
                tenant_obj = check_occupancy(house_obj)[1]
                tenant_id = tenant_obj.id

        else:
            tenant_id = None

        if tenant_id:
            
            range_period_data = []
            for i in tenant_obj.monthly_charges:
                if i.month in month_range and i.year == year:
                    range_period_data.append(i)

            renttotal = 0.0
            watertotal = 0.0
            electotal = 0.0
            garbagetotal = 0.0
            securitytotal = 0.0
            servicetotal = 0.0
            finetotal = 0.0
            duetotal = 0.0
            paidtotal = 0.0

            main = []
            try:
                initial_set = min(range_period_data, key=lambda x: x.month)
                latest_set = max(range_period_data, key=lambda x: x.month)
                # current_bal = latest_set.balance
                current_bal = tenant_obj.balance
                print("lamba",initial_set.month)
            except:
                initial_set = None
                latest_set = None
                # current_bal = 0.0
                current_bal = tenant_obj.balance



            for item in range_period_data:
                
                individual_amounts = []

                # if tenant_obj.multiple_houses:
                #     that_month_payments = fetch_specific_period_payments(item.month,item.year,tenant_obj.split_payments)
                # else:
                #     that_month_payments = fetch_specific_period_payments(item.month,item.year,tenant_obj.payments)

                that_month_payments = fetch_specific_period_payments(item.month,item.year,tenant_obj.payments)

                for x in that_month_payments:
                    if item.house == x.house:
                        individual_amounts.append((f" <span class=\"text-black font--weight-bold small\">Kes </span>{x.amount:,.0f} "))
                values = ' '.join(map(str, individual_amounts))

                period = get_str_mnth(item.month)

                renttotal += item.rent
                watertotal += item.water
                electotal += item.electricity
                garbagetotal += item.garbage
                securitytotal += item.security
                servicetotal += item.maintenance
                finetotal += item.penalty
                duetotal += item.total_bill
                duetotal -= item.arrears if item != initial_set else 0.0
                paidtotal += item.paid_amount

                datadict = {
                    "period":period,
                    "house":item.house.name,
                    "rent":f"{item.rent:,.0f}",
                    "water":f"{item.water:,.0f}",
                    "elec":f"{item.electricity:,.0f}",
                    "garbage":f"{item.garbage:,.0f}",
                    "security":f"{item.security:,.0f}",
                    "service":f"{item.maintenance:,.0f}",
                    "fine":f"{item.penalty:,.0f}",
                    "arrears":f"{item.arrears:,.0f}",
                    "values":values if values else "<span class = \"text-danger\">Not paid</span>", #TODO
                    "due":f"{item.total_bill:,.0f}",
                    "paid":f"{item.paid_amount:,.0f}",
                    "balance":f"{item.balance:,.0f}"
                }
                main.append(datadict)
                  

        ########################################################
        startmonth=get_str_month(start_month)
        endmonth = get_str_month(end_month)
        if start_month == end_month:
            timeline = f"{startmonth} - ({year})"
        else:
            timeline = f"{startmonth} to {endmonth} - ({year})"
        ########################################################

        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        year_list = [2020,2021,2022,2023,2024]
        return Response(render_template(
            'report_tenant_statement.html',
            bills=main,
            renttotal= f"{renttotal:,.0f}",
            watertotal= f"{watertotal:,.0f}",
            electotal= f"{electotal:,.0f}",
            garbagetotal= f"{garbagetotal:,.0f}",
            securitytotal= f"{securitytotal:,.0f}",
            finetotal= f"{finetotal:,.0f}",
            duetotal= f"{duetotal:,.0f}",
            paidtotal= f"{paidtotal:,.0f}",
            balance= f"{current_bal:,.0f}",
            rentshow="" if renttotal else "dispnone",
            watershow="" if watertotal else "dispnone",
            elecshow="" if electotal else "dispnone",
            garbageshow="" if garbagetotal else "dispnone",
            securityshow="" if securitytotal else "dispnone",
            serviceshow ="" if servicetotal else "dispnone",
            fineshow="" if finetotal else "dispnone",
            props=apartment_list,
            prop=apartment_obj,
            tenant_name=tenant_obj.name,
            name=current_user.name,
            tenantlist=[],
            endmonth=endmonth,
            timeline=timeline,
            year=year,
            month_list=month_list,
            year_list=year_list,
            yearnow=present_year,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company
        ))

class TenantStatementTwo(Resource):
    @login_required
    def get(self):
        tenant_id = None
        target = request.args.get("target")
        prop = request.args.get("selected_apartment")

        if target == "tenants":
            prop = request.args.get("apartment")
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            tenants = tenantauto(prop_obj.id)
            vacated_tenants = tenantauto_reverse(prop_obj.id)
            house_tenant_list = generate_house_tenants_alt(tenants,vacated_tenants)
            return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant")

        if not prop and target != "direct":
            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_tenant_statement2.html',
                props=apartment_list,
                name=current_user.name,
                tenant_obj = None,
                prop = "",
                tenantlist=[],
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))

        if target == "direct":
            tenant_id = request.args.get("tenantid")
            if tenant_id.startswith("ptnt"):
                tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(tenant_id))
            else:
                tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)

            begin_date = tenant_obj.date
            end_date = datetime.datetime.now()

        else:
            start = request.args.get("from")
            stop = request.args.get("to")

            begin = date_formatter_alt(start)
            end = date_formatter_alt(stop)

            begin_date = parse(begin)
            end_date = parse(end)

        month_range = [(begin_date.date() + datetime.timedelta(days=x)).month for x in range(0, (end_date-begin_date).days+1)]
        year_range = [(begin_date.date() + datetime.timedelta(days=x)).year for x in range(0, (end_date-begin_date).days+1)]

        # print("RANGES",month_range)
        # print("RANGES",year_range)

        raw_tenant = request.args.get("selected_tenant")

        apartment_obj = ApartmentOp.fetch_apartment_by_name(prop)

        if raw_tenant:
            if raw_tenant.startswith("Vac"):
                tenant_obj = extract_tenant(raw_tenant)
                print("VACATED TENANT >>>>STATEMENT",tenant_obj.monthly_charges)
                tenant_id = tenant_obj.id
            else:
                house_obj = get_specific_house_obj_from_house_tenant_alt(apartment_obj.id,raw_tenant)
                tenant_obj = check_occupancy(house_obj)[1]
                tenant_id = tenant_obj.id
            

        if tenant_id:
            
            range_period_data = []
            for i in tenant_obj.monthly_charges:
                period_of_billing = generate_start_date(i.month,i.year)
                # print("PERIOD",period_of_billing)
                if period_of_billing.month in month_range and period_of_billing.year in year_range:
                    # print("PERIOD",period_of_billing)
                    range_period_data.append(i)


        # target = request.args.get("target")
        # prop = request.args.get("selected_apartment")

        # if target == "tenants":
        #     prop = request.args.get("apartment")
        #     prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
        #     tenants = tenantauto(prop_obj.id)
        #     vacated_tenants = tenantauto_reverse(prop_obj.id)
        #     house_tenant_list = generate_house_tenants_alt(tenants,vacated_tenants)
        #     return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant")

        # if not prop:
        #     apartment_list = fetch_all_apartments_by_user(current_user)
        #     return Response(render_template(
        #         'report_tenant_statement2.html',
        #         props=apartment_list,
        #         name=current_user.name,
        #         tenant_obj = None,
        #         prop = "",
        #         tenantlist=[],
        #         logopath=logo(current_user.company)[0],
        #         mobilelogopath=logo(current_user.company)[1]
        #     ))

        # start = request.args.get("from")
        # stop = request.args.get("to")

        # begin = date_formatter_alt(start)
        # end = date_formatter_alt(stop)

        # begin_date = parse(begin)
        # end_date = parse(end)

        # date_range = [begin_date.date() + datetime.timedelta(days=x) for x in range(0, (end_date-begin_date).days+1)]

        # # print("RANGES",date_range)

        # raw_tenant = request.args.get("selected_tenant")

        # apartment_obj = ApartmentOp.fetch_apartment_by_name(prop)

        # if raw_tenant:
        #     if raw_tenant.startswith("Vac"):
        #         tenant_obj = extract_tenant(raw_tenant)
        #         print("VACATED TENANT >>>>STATEMENT",tenant_obj.monthly_charges)
        #         tenant_id = tenant_obj.id
        #     else:
        #         house_obj = get_specific_house_obj_from_house_tenant_alt(apartment_obj.id,raw_tenant)
        #         tenant_obj = check_occupancy(house_obj)[1]
        #         tenant_id = tenant_obj.id

        # else:
        #     tenant_id = None

        # if tenant_id:
            
        #     range_period_data = []
        #     for i in tenant_obj.monthly_charges:
        #         period_of_billing = generate_date(i.month,i.year)
        #         # print("PERIOD",period_of_billing)
        #         if period_of_billing.date() in date_range:
        #             print("PERIOD",period_of_billing)
        #             range_period_data.append(i)


            main = []

            for item in range_period_data:
                cb = 0.0

                prev_num = item.month -1 if item != 1 else 12
                month = get_str_month(item.month)
                prev_month = get_str_month(prev_num)

                date = item.date.strftime("%d/%b/%y")

                if item.arrears > 0:
                    cb += item.arrears
                    datadict = {
                        "month":month,
                        "date":date,
                        "desc":f"{prev_month} arrears",
                        "ref":f'{item.id}',
                        "debit":item.arrears,
                        "credit":"-",
                        "balance":cb
                    }
                    main.append(datadict)
                                
                if item.rent:
                    cb += item.rent
                    datadict = {
                        "month":month,
                        "date":date,
                        "desc":f"{month} rent",
                        "ref":f'{item.id}',
                        "debit":item.rent,
                        "credit":"-",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.balance < 0:
                    cb += item.balance
                    datadict = {
                        "month":month,
                        "date":date,
                        "desc":"Advance payment",
                        "ref":f'{item.id}',
                        "debit":"-",
                        "credit":item.balance,
                        "balance":cb
                    }
                    main.append(datadict)

                if item.water:
                    cb += item.water
                    datadict = {
                        "month":month,
                        "date":date,
                        "desc":f"{month} water bill",
                        "ref":f'{item.id}',
                        "debit":item.water,
                        "credit":"-",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.garbage:
                    cb += item.garbage
                    datadict = {
                        "month":month,
                        "date":date,
                        "desc":"Garbage fee",
                        "ref":f'{item.id}',
                        "debit":item.garbage,
                        "credit":"-",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.security:
                    cb += item.security
                    datadict = {
                        "month":month,
                        "date":date,
                        "desc":"Security fee",
                        "ref":f'{item.id}',
                        "debit":item.security,
                        "credit":"-",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.maintenance:
                    cb += item.maintenance
                    datadict = {
                        "month":month,
                        "date":date,
                        "desc":"Service charge",
                        "ref":f'{item.id}',
                        "debit":item.maintenance,
                        "credit":"-",
                        "balance":cb
                    }
                    main.append(datadict)

                that_month_payments = fetch_specific_period_payments(item.month,item.year,tenant_obj.payments)
                for x in that_month_payments:
                    paydate = x.pay_date.strftime("%d/%b/%y")

                    ref = f'#{x.id} [{x.ref_number}]',

                    cb -= x.amount
                    datadict = {
                        "month":month,
                        "date":paydate,
                        "desc":f"{x.payment_name} payments",
                        "ref":ref,
                        "debit":"-",
                        "credit":x.amount,
                        "balance":cb
                    }
                    main.append(datadict)

                period = generate_date(item.month,item.year)

                datadict = {
                    # "month":f'<span class="font-weight-bold">End of {period.strftime("%B/%y")}</span>',
                    "month":f'<span class="font-weight-bold">Subtotal</span>',
                    "date":"",
                    "desc":"",
                    "ref":"",
                    "debit":"",
                    "credit":"",
                    "balance":f'<span class="font-weight-bold">{cb}</span>'
                }
                main.append(datadict)


                
                  

        ########################################################
        timeline = f'{begin_date.strftime("%b/%y")} to {end_date.strftime("%b/%y")}'
        ########################################################

        apartment_list = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'report_tenant_statement2.html',
            bills=main,
            props=apartment_list,
            prop=apartment_obj,
            tenant_obj=tenant_obj,
            tenant_name=tenant_obj.name,
            name=current_user.name,
            tenantlist=[],
            timeline=timeline,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company
        ))

class TenantStatementThree(Resource):
    @login_required
    def get(self):
        tenant_id = None
        target = request.args.get("target")
        prop = request.args.get("selected_apartment")

        if target == "tenants":
            prop = request.args.get("apartment")
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            tenants = tenantauto(prop_obj.id)
            vacated_tenants = tenantauto_reverse(prop_obj.id)
            house_tenant_list = generate_house_tenants_alt(tenants,vacated_tenants)
            return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant")

        if not prop and target != "direct":
            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_tenant_statement3.html',
                props=apartment_list,
                name=current_user.name,
                tenant_obj = None,
                prop = "",
                tenantlist=[],
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))

        if target == "direct":
            tenant_id = request.args.get("tenantid")
            if tenant_id.startswith("ptnt"):
                tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(tenant_id))
            else:
                tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)

            begin_date = tenant_obj.date
            end_date = datetime.datetime.now()

        else:
            start = request.args.get("from")
            stop = request.args.get("to")

            begin = date_formatter_alt(start)
            end = date_formatter_alt(stop)

            begin_date = parse(begin)
            end_date = parse(end)

        month_range = [(begin_date.date() + datetime.timedelta(days=x)).month for x in range(0, (end_date-begin_date).days+1)]
        year_range = [(begin_date.date() + datetime.timedelta(days=x)).year for x in range(0, (end_date-begin_date).days+1)]

        # print("RANGES",month_range)
        # print("RANGES",year_range)

        raw_tenant = request.args.get("selected_tenant")

        apartment_obj = ApartmentOp.fetch_apartment_by_name(prop)

        if raw_tenant:
            if raw_tenant.startswith("Vac"):
                tenant_obj = extract_tenant(raw_tenant)
                print("VACATED TENANT >>>>STATEMENT",tenant_obj.monthly_charges)
                tenant_id = tenant_obj.id
            else:
                house_obj = get_specific_house_obj_from_house_tenant_alt(apartment_obj.id,raw_tenant)
                tenant_obj = check_occupancy(house_obj)[1]
                tenant_id = tenant_obj.id
            

        if tenant_id:
            
            range_period_data = []
            for i in tenant_obj.monthly_charges:
                period_of_billing = generate_start_date(i.month,i.year)
                # print("PERIOD",period_of_billing)
                if period_of_billing.month in month_range and period_of_billing.year in year_range:
                    # print("PERIOD",period_of_billing)
                    range_period_data.append(i)


            main = []

            # if range_period_data:
            #     sorted_ids = sort_items_by_id(range_period_data)

            # sorted_data = []
            # if sorted_ids:
            #     # rr = [r for r in range_period_data if r.id in sortedd]
            #     for i in sorted_ids:
            #         for r in range_period_data:
            #             if i == r.id:
            #                 sorted_data.append(r)

            # print("unsorted",[i.id for i in range_period_data])
            # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            # print("sorted",[x.id for x in sorted_data])

            # for item in sorted_data:
            for item in range_period_data:

                cb = 0.0

                journal_rent_correction = 0.0

                prev_num = item.month -1 if item != 1 else 12
                month = get_str_month(item.month)
                prev_month = get_str_month(prev_num)

                date = item.date.strftime("%d/%b/%y")

                if item.rent:
                    cb += item.rent
                    
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {month} rent",
                        "ref":f'{item.id}',
                        "debit":item.rent,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.rent_balance:
                    if item.rent_balance > 0:
                        cb += item.rent_balance
                        datadict = {
                            "month":f"{item.year} {month}",
                            "date":date,
                            "desc":f"{item.house} {prev_month} rent arrears",
                            "ref":f'{item.id}',
                            "debit":item.rent_balance,
                            "credit":"",
                            "balance":cb
                        }
                        main.append(datadict)

                if item.rent_balance:
                    if item.rent_due:
                        if item.rent_due < 0:
                            cb += item.rent_balance
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} rent advance payment",
                                "ref":f'{item.id}',
                                "debit":"",
                                "credit":item.rent_balance,
                                "balance":cb
                            }
                            main.append(datadict)

                if item.water:
                    cb += item.water
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {month} water bill",
                        "ref":f'{item.id}',
                        "debit":item.water,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.water_balance:
                    cb += item.water_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} water arrears",
                        "ref":f'{item.id}',
                        "debit":item.water_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.water_balance:
                    if item.water_due:
                        if item.water_due < 0:
                            cb += item.water_balance
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} water advance payment",
                                "ref":f'{item.id}',
                                "debit":item.water_balance,
                                "credit":"",
                                "balance":cb
                            }
                            main.append(datadict)

                if item.garbage:
                    cb += item.garbage
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} Garbage fee",
                        "ref":f'{item.id}',
                        "debit":item.garbage,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.garbage_balance:
                    cb += item.garbage_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} garbage arrears",
                        "ref":f'{item.id}',
                        "debit":item.garbage_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.security:
                    cb += item.security
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} security fee",
                        "ref":f'{item.id}',
                        "debit":item.security,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.security_balance:
                    cb += item.security_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} security arrears",
                        "ref":f'{item.id}',
                        "debit":item.security_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.maintenance:
                    cb += item.maintenance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} Service charge",
                        "ref":f'{item.id}',
                        "debit":item.maintenance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.maintenance_balance:
                    cb += item.maintenance_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} service charge arrears",
                        "ref":f'{item.id}',
                        "debit":item.maintenance_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.maintenance_balance:

                    if item.maintenance_due < 0:
                        cb += item.maintenance_balance
                        datadict = {
                            "month":f"{item.year} {month}",
                            "date":date,
                            "desc":f"{item.house} service charge advance payment",
                            "ref":f'{item.id}',
                            "debit":item.maintenance_balance,
                            "credit":"",
                            "balance":cb
                        }
                        main.append(datadict)



                that_month_payments = fetch_specific_period_payments(item.month,item.year,tenant_obj.payments)
                for x in that_month_payments:
                    paydate = x.pay_date.strftime("%d/%b/%y")

                    ref = f'#{x.id} [{x.ref_number}]',

                    # if item.month == 8:
                    #     import pdb;
                    #     pdb.set_trace()

                    # if item.month == 7 and item.year == 2022:
                    #     import pdb; pdb.set_trace()
                                

                    if x.rent_paid:
                        credit = 0.0
                        if item.rent_due:
                            if item.rent_due < 0:
                                cb += item.rent_due
                                credit += abs(item.rent_due)
                        credit += x.rent_paid
                        cb -= x.rent_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Rent payment",
                            "ref":ref,
                            "debit":"",
                            "credit":f'{credit:,.1f}',
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.water_paid:
                        cb -= x.water_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Water bill payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.water_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.garbage_paid:
                        cb -= x.garbage_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Garbage fee payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.garbage_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.security_paid:
                        cb -= x.security_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Security fee payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.security_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.maintenance_paid:
                        cb -= x.maintenance_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Service fee payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.maintenance_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                period = generate_date(item.month,item.year)

                datadict = {
                    # "month":f'<span class="font-weight-bold">End of {period.strftime("%B/%y")}</span>',
                    "month":f'<span class="text-muted">Closing balance</span>',
                    "date":"",
                    "desc":"",
                    "ref":"",
                    "debit":"",
                    "credit":"",
                    "balance":f'<span class="font-weight-bold">{cb}</span>'
                }
                main.append(datadict)
                datadict2 = {
                    # "month":f'<span class="font-weight-bold">End of {period.strftime("%B/%y")}</span>',
                    "month":"",
                    "date":"",
                    "desc":"",
                    "ref":"",
                    "debit":"",
                    "credit":"",
                    "balance":"`"
                }
                # main.append(datadict2)

                
        ########################################################
        timeline = f'{begin_date.strftime("%b/%y")} to {end_date.strftime("%b/%y")}'
        ########################################################

        apartment_list = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'report_tenant_statement3.html',
            bills=main,
            props=apartment_list,
            prop=apartment_obj,
            tenant_obj=tenant_obj,
            tenant_name=tenant_obj.name,
            name=current_user.name,
            tenantlist=[],
            timeline=timeline,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company
        ))

class TenantStatementFour(Resource):
    @login_required
    def get(self):
        tenant_id = None
        target = request.args.get("target")
        prop = request.args.get("selected_apartment")
        house_obj = None

        main = []

        if target == "tenants":
            prop = request.args.get("apartment")
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            # tenants = tenantauto(prop_obj.id)
            houses = prop_obj.houses
            vacated_tenants = tenantauto_reverse(prop_obj.id)
            house_tenant_list = generate_house_tenants_alt2(houses,vacated_tenants)
            return render_template('ajax_multivariable.html',items=sort_items(house_tenant_list),placeholder="select tenant")

        if not prop and target != "direct":
            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_tenant_statement4.html',
                props=apartment_list,
                name=current_user.name,
                tenant_obj = None,
                prop =None,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                co=current_user.company
            ))

        if target == "direct":
            tenant_id = request.args.get("tenantid")
            if tenant_id.startswith("ptnt"):
                tenant_obj = PermanentTenantOp.fetch_tenant_by_id(get_identifier(tenant_id))
                house_obj = tenant_obj.house
                prop = house_obj.apartment.name
            else:
                tenant_obj = TenantOp.fetch_tenant_by_id(tenant_id)
                house_obj = check_house_occupied(tenant_obj)[1]
                prop = house_obj.apartment.name



            begin_date = tenant_obj.date
            end_date = datetime.datetime.now()

        else:
            start = request.args.get("from")
            stop = request.args.get("to")

            begin = date_formatter_alt(start)
            end = date_formatter_alt(stop)

            begin_date = parse(begin)
            end_date = parse(end)

        month_range = [(begin_date.date() + datetime.timedelta(days=x)).month for x in range(0, (end_date-begin_date).days+1)]
        year_range = [(begin_date.date() + datetime.timedelta(days=x)).year for x in range(0, (end_date-begin_date).days+1)]

        # print("RANGES",month_range)
        # print("RANGES",year_range)

        raw_tenant = request.args.get("selected_tenant")

        apartment_obj = ApartmentOp.fetch_apartment_by_name(prop)


        if raw_tenant:
            if raw_tenant.startswith("Vac"):
                tenant_obj = extract_tenant(raw_tenant)
                print("VACATED TENANT >>>>STATEMENT",tenant_obj.monthly_charges)
                tenant_id = tenant_obj.id
                house_obj = check_house_occupied(tenant_obj)[2].house
            else:
                house_obj = get_specific_house_obj_from_house_tenant_alt(apartment_obj.id,raw_tenant)
                tenant_obj = check_occupancy(house_obj)[1]
                tenant_id = tenant_obj.id
            

        # if tenant_id:
        if house_obj:

            
            range_period_data = []
            for i in house_obj.monthlybills:
                period_of_billing = generate_start_date(i.month,i.year)
                # print("PERIOD",period_of_billing)
                if period_of_billing.month in month_range and period_of_billing.year in year_range:
                    # print("PERIOD",period_of_billing)
                    range_period_data.append(i)


            # if range_period_data:
            #     sorted_ids = sort_items_by_id(range_period_data)

            # sorted_data = []
            # if sorted_ids:
            #     # rr = [r for r in range_period_data if r.id in sortedd]
            #     for i in sorted_ids:
            #         for r in range_period_data:
            #             if i == r.id:
            #                 sorted_data.append(r)

            # print("unsorted",[i.id for i in range_period_data])
            # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            # print("sorted",[x.id for x in sorted_data])

            # for item in sorted_data:
            for item in range_period_data:

                cb = 0.0

                prev_num = item.month -1 if item != 1 else 12
                month = get_str_month(item.month)
                prev_month = get_str_month(prev_num)

                # date = item.date.strftime("%d/%b/%y")
                rdate = generate_exact_date(item.date.day,item.month,item.year)
                date = rdate.strftime("%d/%b/%y")

                # print(tenant_obj.date.month, tenant_obj.date.year, "vs", item.month, item.year)
                if item.month == tenant_obj.date.month and item.year == tenant_obj.date.year:
                    if house_obj.deposits:
                        if house_obj.deposits.rentdep:
                            cb += house_obj.deposits.rentdep
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} RENT DEPOSIT BILL",
                                "ref":f'{item.id}',
                                "debit":house_obj.deposits.rentdep,
                                "credit":"",
                                "balance":cb
                            }
                            main.append(datadict)
                        if house_obj.deposits.waterdep:
                            cb += house_obj.deposits.waterdep
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} WATER DEPOSIT BILL",
                                "ref":f'{item.id}',
                                "debit":house_obj.deposits.waterdep,
                                "credit":"",
                                "balance":cb
                            }
                            main.append(datadict)

                        if house_obj.deposits.elecdep:
                            cb += house_obj.deposits.elecdep
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} ELECTRICITY DEPOSIT BILL",
                                "ref":f'{item.id}',
                                "debit":house_obj.deposits.elecdep,
                                "credit":"",
                                "balance":cb
                            }
                            main.append(datadict)


                        if house_obj.deposits.rentdep:
                            cb -= house_obj.deposits.rentdep
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} RENT DEPOSIT PAYMENT",
                                "ref":f'{item.id}',
                                "debit":"",
                                "credit":house_obj.deposits.rentdep,
                                "balance":cb
                            }
                            main.append(datadict)
                        if house_obj.deposits.waterdep:
                            cb -= house_obj.deposits.waterdep
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} WATER DEPOSIT PAYMENT",
                                "ref":f'{item.id}',
                                "debit":"",
                                "credit":house_obj.deposits.waterdep,
                                "balance":cb
                            }
                            main.append(datadict)

                        if house_obj.deposits.elecdep:
                            cb -= house_obj.deposits.elecdep
                            datadict = {
                                "month":f"{item.year} {month}",
                                "date":date,
                                "desc":f"{item.house} ELECTRICITY DEPOSIT PAYMENT",
                                "ref":f'{item.id}',
                                "debit":"",
                                "credit":house_obj.deposits.elecdep,
                                "balance":cb
                            }
                            main.append(datadict)
                                
                if item.rent:
                    cb += item.rent
                    
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} PREMISES RENT BILL",
                        "ref":f'{item.id}',
                        "debit":item.rent,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.rent_balance:
                    if item.rent_balance > 0:
                        cb += item.rent_balance
                        datadict = {
                            "month":f"{item.year} {month}",
                            "date":date,
                            "desc":f"{item.house} {prev_month} rent arrears",
                            "ref":f'{item.id}',
                            "debit":item.rent_balance,
                            "credit":"",
                            "balance":cb
                        }
                        main.append(datadict)

                if item.rent_balance:
                    if item.rent_balance < 0:
                        cb += item.rent_balance
                        datadict = {
                            "month":f"{item.year} {month}",
                            "date":date,
                            "desc":f"{item.house} rent advance payment",
                            "ref":f'{item.id}',
                            "debit":"",
                            "credit":f'{abs(item.rent_balance):,.1f}',
                            "balance":cb
                        }
                        main.append(datadict)

                if item.water:
                    cb += item.water
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} water bill",
                        "ref":f'{item.id}',
                        "debit":item.water,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.water_balance:
                    cb += item.water_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} water arrears",
                        "ref":f'{item.id}',
                        "debit":item.water_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.water_due:
                    if item.water_due < 0:
                        cb += item.water_due
                        datadict = {
                            "month":f"{item.year} {month}",
                            "date":date,
                            "desc":f"{item.house} water advance payment",
                            "ref":f'{item.id}',
                            "debit":"",
                            "credit":item.water_due,
                            "balance":cb
                        }
                        main.append(datadict)

                if item.garbage:
                    cb += item.garbage
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} Garbage fee",
                        "ref":f'{item.id}',
                        "debit":item.garbage,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.garbage_balance:
                    cb += item.garbage_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} garbage arrears",
                        "ref":f'{item.id}',
                        "debit":item.garbage_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.security:
                    cb += item.security
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} security fee",
                        "ref":f'{item.id}',
                        "debit":item.security,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.security_balance:
                    cb += item.security_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} security arrears",
                        "ref":f'{item.id}',
                        "debit":item.security_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.maintenance:
                    cb += item.maintenance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} Service charge",
                        "ref":f'{item.id}',
                        "debit":item.maintenance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.maintenance_balance:
                    cb += item.maintenance_balance
                    datadict = {
                        "month":f"{item.year} {month}",
                        "date":date,
                        "desc":f"{item.house} {prev_month} service charge arrears",
                        "ref":f'{item.id}',
                        "debit":item.maintenance_balance,
                        "credit":"",
                        "balance":cb
                    }
                    main.append(datadict)

                if item.maintenance_due:

                    if item.maintenance_due < 0:
                        cb += item.maintenance_due
                        datadict = {
                            "month":f"{item.year} {month}",
                            "date":date,
                            "desc":f"{item.house} service charge advance payment",
                            "ref":f'{item.id}',
                            "debit":"",
                            "credit":item.maintenance_due,
                            "balance":cb
                        }
                        main.append(datadict)



                that_month_payments = fetch_specific_period_payments(item.month,item.year,house_obj.payments)
                for x in that_month_payments:
                    paydate = x.pay_date.strftime("%d/%b/%y")

                    ref = x.ref_number if x.ref_number else x.id

                    # if item.month == 8:
                    # import pdb;
                    # pdb.set_trace()

                    # if x.rent_paid:
                    #     cb -= x.rent_paid
                    #     datadict = {
                    #         "month":month,
                    #         "date":paydate,
                    #         "desc":f" Rent payment",
                    #         "ref":x.ref_number,
                    #         "debit":"",
                    #         "credit":x.rent_paid,
                    #         "balance":cb
                    #     }
                    #     main.append(datadict)

                    if x.rent_paid:
                        credit = 0.0
                        if item.rent_due:
                            if item.rent_due < 0:
                                cb += item.rent_due
                                credit += abs(item.rent_due)
                        credit += x.rent_paid
                        cb -= x.rent_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Rent payment",
                            "ref":ref,
                            "debit":"",
                            "credit":f'{credit:,.1f}',
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.water_paid:
                        cb -= x.water_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Water bill payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.water_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.garbage_paid:
                        cb -= x.garbage_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Garbage fee payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.garbage_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.security_paid:
                        cb -= x.security_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Security fee payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.security_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                    if x.maintenance_paid:
                        cb -= x.maintenance_paid
                        datadict = {
                            "month":month,
                            "date":paydate,
                            "desc":f"{x.house} Service fee payment",
                            "ref":ref,
                            "debit":"",
                            "credit":x.maintenance_paid,
                            "balance":cb
                        }
                        main.append(datadict)

                period = generate_date(item.month,item.year)

                datadict = {
                    "month":f'<span class="font-weight-bold">End of {period.strftime("%B/%y")}</span>',
                    "month":f'<span class="text-muted">Closing balance</span>',
                    "date":"",
                    "desc":"",
                    "ref":"",
                    "debit":"",
                    "credit":"",
                    "balance":f'<span class="font-weight-bold">{cb}</span>'
                }
                main.append(datadict)
                datadict2 = {
                    "month":f'<span class="font-weight-bold">End of {period.strftime("%B/%y")}</span>',
                    "month":"",
                    "date":"",
                    "desc":"",
                    "ref":"",
                    "debit":"",
                    "credit":"",
                    "balance":"`"
                }
                main.append(datadict2)

                
        ########################################################
        timeline = f'{begin_date.strftime("%b/%y")} to {end_date.strftime("%b/%y")}'
        ########################################################

        apartment_list = fetch_all_apartments_by_user(current_user)

        return Response(render_template(
            'report_tenant_statement4.html',
            bills=main,
            props=apartment_list,
            prop=apartment_obj,
            tenant_obj=tenant_obj,
            tenant_name=tenant_obj.name,
            thouse=house_obj,
            name=current_user.name,
            timeline=timeline,
            statementdate = datetime.datetime.today().strftime("%d/%B/%Y"),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            co=current_user.company
        ))


class MpesaStatement(Resource):
    @login_required
    def get(self):

        shortcode_id = request.args.get("shortcode")

        start = request.args.get("from")

        if not start:
            begin_date_month = datetime.datetime.now().month
            begin_date_year = datetime.datetime.now().year
            begin_date = generate_start_date(begin_date_month, begin_date_year)
        else:
            begin = date_formatter_alt(start)
            begin_date = parse(begin)

        end_date = begin_date.date() + datetime.timedelta(days=29)

        month_range = [(begin_date.date() + datetime.timedelta(days=x)).month for x in range(0, (end_date-begin_date.date()).days+1)]
        year_range = [(begin_date.date() + datetime.timedelta(days=x)).year for x in range(0, (end_date-begin_date.date()).days+1)]


        shortcode = ShortcodeOp.fetch_shortcode_by_id(shortcode_id)

        cbids = CtoBop.fetch_all_records_by_shortcode(shortcode_id)

            
        main = []
        total = 0.0
        for i in cbids:

            if i.post_date.month in month_range and i.post_date.year in year_range:
                total += i.trans_amnt
                main.append(i)

        cbids_dicts = ctb_payment_details(main)
                
        ########################################################
        timeline = f'{begin_date.strftime("%b/%y")} to {end_date.strftime("%b/%y")}'
        ########################################################

        return Response(render_template(
            'report_mpesa_statement.html',
            bills=cbids_dicts,
            total=f"{total:,.1f}",
            prop="someprop",
            shortcode=shortcode,
            name=current_user.name,
            tenantlist=[],
            timeline=timeline,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company
        ))


class BookingSchedule(Resource):
    @login_required
    def get(self):
        prop = request.args.get('selected_apartment')
        if not prop:
            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_booking.html',
                props=apartment_list,
                name=current_user.name,
                tenant_obj = None,
                prop = "",
                prop_obj = None,
                co=current_user.company,
                tenantlist=[],
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))

        else:
            bills = []
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            units = prop_obj.houses
            for unit in units:
                unit_item = HouseOp.view(unit)
                bills.append(unit_item)

            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_booking.html',
                props=apartment_list,
                name=current_user.name,
                prop = prop,
                prop_obj = prop_obj,
                bills=bills,
                co=current_user.company,
                tenantlist=[],
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))


class TenantListing(Resource):
    def get(self):
        selected_apartment = request.args.get("prop")
        propid = request.args.get("propid")
        target = request.args.get("target")

        if target == "direct":
            prop_id = get_identifier(propid)
            select_options = "d-none"
            prop = ApartmentOp.fetch_apartment_by_id(prop_id)
            selected_apartment = prop.name

        elif selected_apartment:
            select_options = ""
            if selected_apartment:
                prop = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        else:
            prop = None
            select_options = ""

        company = current_user.company

        if not prop:
            return Response(render_template(
                'report_tenant_listing.html',
                select_options=select_options,
                name=current_user.name,
                prop=None,
                props = company.props,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                fulllogopath=logo(current_user.company)[2],
                letterhead=logo(current_user.company)[3],
                co=current_user.company
                ))

        units = []
        allrent = 0.0
        allunits = 0
        alltenants = 0
        all_units = prop.houses

        for unit in all_units:
            allunits += 1
            allrent += unit.housecode.rentrate
            check = check_occupancy(unit)
            if check[0] == "occupied":
                tenant = check[1].name
                contact = check[1].phone
                alltenants += 1
            else:
                tenant = "Vacant"
                contact = ""

            dict_obj = {
                "house":unit.name,
                "tenant":tenant,
                "contact":contact,
                "schedule": get_schedule(unit.housecode.billfrequency),
                "rent":f"{unit.housecode.rentrate:,.1f}",
                "serv":unit.housecode.servicerate,
                "park":0.0
            }
            units.append(dict_obj)

        return Response(render_template(
            "report_tenant_listing.html",
            select_options=select_options,
            bills=units,
            tothouses=allunits,
            tottenants=alltenants,
            totrent=f"{allrent:,.1f}",
            totserv = 0.0,
            totpark = 0.0,
            prop=prop,
            propname=prop.name,
            props = company.props,
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            statementdate = datetime.datetime.today().strftime("%d/%B/%Y"),
            co=current_user.company
        ))

class MeritStatementOne(Resource):
    def get(self):
        selected_apartment = request.args.get("prop")
        owner = request.args.get("owner")
        month = request.args.get("month")

        company = current_user.company
        users = company.users
        owner_users = []
        for user in users:
            if str(user.company_user_group) == "Owner":
                owner_users.append(user)

        if not selected_apartment:
            return Response(render_template(
                'report_merit_one_statement.html',
                tenant_obj=None,
                name=current_user.name,
                tenantlist=[],
                owners=owner_users,
                props = company.props,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                fulllogopath=logo(current_user.company)[2],
                letterhead=logo(current_user.company)[3],
                co=current_user.company
                ))

        prop = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        owner_user = UserOp.fetch_user_by_username(owner)

        print(owner_user,"<<<<< user")
        units = fetch_all_houses_by_user(owner_user)

        print("unitts>>>",units)

        if month:
            datestring = date_formatter_alt(month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        target_units = []

        for unit in units:
            if unit in prop.houses:
                target_units.append(unit)

        main = []

        formatted_bills = []
        for unitt in target_units:
            main.append(fetch_current_billing_period_bills(target_period,unitt.monthlybills))

        bills = flatten(main)
        formatted_bills = []

        print(bills,"<<<<<<")

        totrent = 0.0
        totserv = 0.0
        totmgt = 0.0
        totdue = 0.0

        for bill in bills:
            totrent += bill.rent_paid + bill.maintenance_paid
            if bill.house.name == "B3":
                totserv += 2500
            else:
                totserv += bill.maintenance
            if bill.rent_paid > 2000:
                raw_mgt = (bill.rent_paid / bill.rent) * 2000
                mgt = round(raw_mgt,-3) if raw_mgt > 1999 else 0
            else:
                mgt =  0

            totmgt += mgt

            totdue += (bill.rent_paid + bill.maintenance_paid)  - MonthlyChargeOp.get_management_fees(bill) - float(MonthlyChargeOp.get_maintenance(bill).replace(",",""))

            formatted_bills.append(MonthlyChargeOp.view_merit(bill))

        # for item in formatted_bills:
        #     totmgt += item["mgt"]
        #     totdue += item["ownerdue"]

        expense_list = []

        expenses_amount = 0.0

        exceptions = ["deposit refund", "remittance"]

        for exp in prop.expenses:
            if exp.date.month == target_period.month and exp.date.year == target_period.year and exp.status == "completed" and exp.expense_type not in exceptions:
                expenses_amount += exp.amount

                if exp.expense_type == "deposit_refund":
                    ename = exp.name + "(Refund)"
                else:
                    ename = exp.name

                exp_dict = {
                    "house":exp.house,
                    "name":ename,
                    "amount":exp.amount,
                }
                expense_list.append(exp_dict)

        debits = totmgt + totserv + expenses_amount
        netpay = totrent - debits

        return Response(render_template(
                'report_merit_one_statement.html',
                name=current_user.name,
                tenantlist=[],
                bills = formatted_bills,
                expenselist = expense_list,
                units = ','.join(map(str, units)),
                propname = prop.name,
                owner = owner_user.name,
                statementdate = f"{get_str_month(target_period.month)}, {target_period.year}",
                bank = owner_user.bank,
                bankacc=owner_user.bankacc,
                totrent=totrent,
                totserv=totserv,
                totmgt=totmgt,
                totdue=totdue,
                expenses=expenses_amount,
                debits=debits,
                netpay=netpay,
                owners=owner_users,
                props = company.props,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                fulllogopath=logo(current_user.company)[2],
                letterhead=logo(current_user.company)[3],
                co=current_user.company
        ))


class StatementOfAccounts(Resource):
    def get(self):
        tenant_id = None
        target = request.args.get("target")
        prop = request.args.get("selected_apartment")

        if target == "tenants":
            prop = request.args.get("apartment")
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            owners = generate_house_owners(prop_obj.id)
            return render_template('ajax_multivariable.html',items=sort_items(owners),placeholder="select client")

        if not prop and target != "direct":
            apartment_list = fetch_all_apartments_by_user(current_user)
            return Response(render_template(
                'report_empty_account_statement.html',
                props=apartment_list,
                name=current_user.name,
                tenant_obj = None,
                prop = "",
                prop_obj = None,
                co=current_user.company,
                tenantlist=[],
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1]
            ))


        # target = request.args.get("target")

        if target == "direct":
            tenantid = request.args.get("tenantid")
            if not tenantid:
                tenantid = request.args.get("uuid")

            tenant_obj = PermanentTenantOp.fetch_tenant_by_id(tenantid)

        else:
            prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
            housename = request.args.get("selected_tenant")
            hse_obj = get_specific_house_obj_from_house_tenant_alt_alt(prop_obj.id, housename)
            tenant_obj = hse_obj[0].owner


        schtotal = 0.0
        schpaid = 0.0

        bills = tenant_obj.schedules

        formatted_bills = []

        for bill in bills:
            schtotal += bill.schedule_amount
            schpaid += bill.paid
            formatted_bills.append(PaymentScheduleOp.view_detail(bill))

        rbal = f"{tenant_obj.balance:,.1f}"

        prop = tenant_obj.apartment

        return Response(render_template(
            'report_account_statement.html',
            statementdate=datetime.datetime.now().strftime("%d %B %Y"),
            bills=formatted_bills,
            paging=page(formatted_bills),
            schtotal=f"{schtotal:,.1f}",
            schpaid=f"{schpaid:,.1f}",
            rbal=rbal,
            prop_obj=prop,
            prop = tenant_obj.apartment.name,
            tenant_obj=tenant_obj,
            tenant_name=tenant_obj.name,
            name=prop.name,
            tenantlist=[],
            logopath=logo(prop.company)[0],
            mobilelogopath=logo(prop.company)[1],
            fulllogopath=logo(prop.company)[2],
            letterhead=logo(prop.company)[3],
            co=prop.company
        ))


class ExpenseDetail(Resource):
    """class"""
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        return Response(render_template(
            'report_expenses_detailed.html',
            tenantlist=[],
            apartment_list=apartment_list,
            month_list=month_list,
            year_list=[2020,2021,2022,2024],
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        current_month_bill = []
        amount_sum_members = []
        bill_list = []

        selected_apartment = request.form.get("selected_apartment")
        selected_month = request.form.get("selected_month")
        selected_year = request.form.get("selected_year")
        present_year = datetime.datetime.now().year

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        monthlybills = apartment_obj.expenses

        if selected_month:
            month =  get_numeric_month(selected_month)
        else:
            month = datetime.datetime.now().month

        if not selected_year:
            selected_year =  present_year
        else:
            selected_year = int(selected_year)
            
        str_month = get_str_month(month)
        
        for bill in monthlybills:
            if bill.date.month == month and bill.date.year == selected_year and bill.status == "completed":
                current_month_bill.append(bill)

        for bill in current_month_bill:
            bill_item = InternalExpenseOp.view(bill)
            bill_list.append(bill_item)


            amount_sum_members.append(bill.amount)


        totalamount = sum_values(amount_sum_members)
        amounttotal = (f"{totalamount:,}")

        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        timeline = f"{str_month} - {selected_year}"

        return Response(render_template(
            'report_expenses_detailed.html',
            prop=selected_apartment,
            tenantlist=[],
            year=selected_year,
            string_month = str_month,
            timeline = timeline,
            amounttotal=amounttotal,
            bills=bill_list,
            paging=page(bill_list),
            apartment_list=apartment_list,
            month_list=month_list,
            year_list=[2020,2021,2022,2024],
            apartment_name=selected_apartment,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name))


class SubmissionsReport(Resource):
    """class"""
    @login_required
    def get(self):
        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        return Response(render_template(
            'report_submissions_detailed.html',
            tenantlist=[],
            apartment_list=apartment_list,
            month_list=month_list,
            year_list=[2020,2021,2022,2024],
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            name=current_user.name))

    def post(self):
        current_month_bill = []
        amount_sum_members = []
        bill_list = []

        selected_apartment = request.form.get("selected_apartment")
        selected_month = request.form.get("selected_month")
        selected_year = request.form.get("selected_year")
        present_year = datetime.datetime.now().year

        apartment_obj = ApartmentOp.fetch_apartment_by_name(selected_apartment)
        apartment_id = apartment_obj.id

        monthlybills = apartment_obj.submissions

        if selected_month:
            month =  get_numeric_month(selected_month)
        else:
            month = datetime.datetime.now().month

        if not selected_year:
            selected_year =  present_year
        else:
            selected_year = int(selected_year)
            
        str_month = get_str_month(month)
        
        for bill in monthlybills:
            if bill.pay_period.month == month and bill.pay_period.year == selected_year:
                current_month_bill.append(bill)
        print("hhjkkvcxfcgvh",month,selected_year,current_month_bill)
        for bill in current_month_bill:
            bill_item = SubmissionOp.view(bill)
            bill_list.append(bill_item)

            amount_sum_members.append(bill.amount_paid)

        totalamount = sum_values(amount_sum_members)
        amounttotal = (f"{totalamount:,}")

        apartment_list = fetch_all_apartments_by_user(current_user)
        month_list = generate_month_list()
        timeline = f"{str_month} - {selected_year}"

        return Response(render_template(
            'report_submissions_detailed.html',
            prop=selected_apartment,
            tenantlist=[],
            year=selected_year,
            string_month = str_month,
            timeline = timeline,
            amounttotal=amounttotal,
            bills=bill_list,
            paging=page(bill_list),
            apartment_list=apartment_list,
            month_list=month_list,
            year_list=[2020,2021,2022,2024],
            apartment_name=selected_apartment,
            suggestions=generate_suggestions(apartment_list),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            name=current_user.name))


class FetchLeads(Resource):
    def get(self):
        if request.args.get("target") == "lead name":
            lead_obj = LeadOp.fetch_lead_by_id(get_identifier(request.args.get("lead_id")))
            return f' ({lead_obj.name})'

        # co = current_user.company
        # leads = co.leads


        # Set the pagination configuration
        page = request.args.get('page', 1, type=int)
        pg = Lead.query.filter_by(company_id=current_user.company.id).filter(or_(Lead.status=="hot",Lead.status=="cold")).paginate(page=page, per_page=ROWS_PER_PAGE)
        # q1 = Lead.query.filter_by(company_id=current_user.company.id).filter_by(status="hot")
        # q2 = Lead.query.filter_by(company_id=current_user.company.id).filter_by(status="cold")
        # pg = q1.or_(q2).paginate(page=page, per_page=ROWS_PER_PAGE)


        # import pdb; pdb.set_trace()
        tenant_data = lead_details(pg.items)
        tenantids = get_obj_ids(tenant_data)

        return render_template("ajax_leads.html",tenantids=tenantids,items=tenant_data,pg=pg)

class FetchTenants(Resource):
    def get(self):
        prop_id = request.args.get('propid')
        target = request.args.get('target')

        propid = get_identifier(prop_id)

        if target == "tenant details":
            tenantid = request.args.get('tenantid')
            tenant_obj = TenantOp.fetch_tenant_by_id(tenantid)
            tenant_info = [tenant_obj]
            tenant_data = tenant_details(tenant_info)
            tenantids = get_obj_ids(tenant_data)
            return render_template("ajax_tenant_info.html",tenantids=tenantids,items=tenant_data)
        
        elif target == "closed":
            tenancy = tenantauto_alt(propid,"closed")
            tenantlist = ptenant_details(tenancy)
            tenantids = get_obj_ids(tenantlist)

            moreids = inject_tenants_ids(tenantlist) 
            full_ids = tenantids + "," + moreids
            return render_template("ajax_oldtenantlist2.html",items=tenantlist,tenantids=full_ids)

        elif target == "proposals":
            tenancy = tenantauto_alt(propid,"proposal") + tenantauto_alt(propid,"prospective")
            tenantlist = ptenant_details(tenancy)
            tenantids = get_obj_ids(tenantlist)
            moreids = inject_tenants_ids(tenantlist) 
            full_ids = tenantids + "," + moreids
            if current_user.company_user_group.name == "Sales":
                access = "dispnone"
            else:
                access = ""
            return render_template("ajax_newtenantlist2.html",access=access,items=tenantlist,tenantids=full_ids)

        elif target == "contracts":
            # tenancy = tenantauto_alt(propid,"invoiced and missing contracts") + tenantauto_alt(propid,"invoiced and contracts")

            page = request.args.get('page', 1, type=int)
            pg = PermanentTenant.query.filter_by(apartment_id=propid).filter(or_(PermanentTenant.status == 'invoiced and missing contracts', PermanentTenant.status == 'invoiced and contracts')).paginate(page=page, per_page=ROWS_PER_PAGE)

            tenantlist = ptenant_details(pg.items)
            tenantids = get_obj_ids(tenantlist)
            moreids = inject_tenants_ids(tenantlist) 
            full_ids = tenantids + "," + moreids
            return render_template("ajax_clientcontractslist.html",items=tenantlist,tenantids=full_ids,pg=pg)

        elif target == "old":
            tenancy = xtenantauto(propid)
            tenantlist = tenant_details(tenancy)
            tenantids = get_obj_ids(tenantlist)
            return render_template("ajax_oldtenantlist.html",items=tenantlist,tenantids=tenantids)
        elif target == "new":
            tenancy = newtenantsauto(propid)
            tenantlist = tenant_details(tenancy)
            tenantids = get_obj_ids(tenantlist)
            return render_template("ajax_newtenantlist.html",items=tenantlist,tenantids=tenantids)
        else:
            tenancy = tenantauto(propid)
            tenantlist = tenant_details(tenancy)

            prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
            all_ptenants = prop_obj.ptenants
            for i in all_ptenants:
                new_i = PermanentTenantOp.view(i)
                tenantlist.append(new_i)

            tenantids = get_obj_ids(tenantlist)

            moreids = inject_tenants_ids(tenantlist) 
            full_ids = tenantids + "," + moreids

            return render_template("ajax_tenantlist.html",items=tenantlist,tenantids=full_ids)

class FetchReadings(Resource):
    def get(self):
        propid = request.args.get('propid')
        target = request.args.get('target')

        prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
        
        billing_period = get_billing_period(prop_obj)
        
        if target == "old":
            next_billing_month = billing_period.month
            str_month = get_str_month(next_billing_month)
            readings = readingsauto(billing_period,prop_obj)
            readinglist = reading_details(readings)
            readingids = get_obj_ids(readinglist)
            return render_template("ajax_oldreadings.html",period=str_month,items=readinglist,readingids=readingids)
        else:
            next_billing_month = billing_period.month + 1 if billing_period.month != 12 else 1
            str_month = get_str_month(next_billing_month)
            readings = readingsauto_new(billing_period,prop_obj)
            readinglist = reading_details(readings)
            readingids = get_obj_ids(readinglist)
            return render_template("ajax_currentreadings.html",period=str_month,items=readinglist,readingids=readingids)


class FetchHouses(Resource):
    @timer
    @login_required
    def get(self):
        prop_id = request.args.get('propid')
        propid = get_identifier(prop_id)

        pg = None

        if crm(current_user):
            page = request.args.get('page', 1, type=int)
            pg = House.query.filter_by(apartment_id=propid).order_by(House.id.asc()).paginate(page=page, per_page=ROWS_PER_PAGE)
            houselist = house_details(pg.items)
        else:
            prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
            houses = prop_obj.houses
            houselist = house_details(houses)


        houseids = get_obj_ids(houselist)

        template = "ajax_houselist2.html" if crm(current_user) else "ajax_houselist.html"

        return render_template(template,items=houselist,houseids=houseids,pg=pg)

class FetchRates(Resource):
    def get(self):
        propid = request.args.get('propid')
        prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
        housecodes = prop_obj.housecodes

        housecodelist = group_details(housecodes)
        groupids = get_obj_ids(housecodelist)

        template = "ajax_housecodelist2.html" if crm(current_user) else "ajax_housecodelist.html"


        return render_template(template,items=housecodelist,groupids=groupids)

class FetchMeters(Resource):
    def get(self):
        propid = request.args.get('propid')
        prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
        meters = prop_obj.meters

        meterlist = meter_details(meters)
        meterids = get_obj_ids(meterlist)

        return render_template("ajax_meterlist.html",items=meterlist,meterids=meterids)

class FetchAgents(Resource):
    def get(self):
        com_obj = current_user.company
        reps = com_obj.reps
        attlist = att_details(reps)
        subids = get_obj_ids(attlist)

        return render_template("ajax_agentlist.html",items=attlist,subids=subids)

class FetchUsers(Resource):
    def get(self):
        # com_obj = current_user.company
        # users = com_obj.users

        # if current_user.username.startswith("qc"):
        #     kw_user = UserOp.fetch_user_by_username("kelvinwanjiku")
        #     if kw_user:
        #         users.remove(kw_user)

        # userlist = user_details(users)


        # userlist_alt = []
        # if current_user.username.startswith("qc"):
        #     kw_user = UserOp.fetch_user_by_username("wanjikukelvin")
        #     if kw_user:
        #         for i in userlist:
        #             if i["username"] == kw_user.username:
        #                 pass
        #             else:
        #                 userlist_alt.append(i)
        #     else:
        #         userlist_alt = userlist
        # else:
        #     userlist_alt = userlist

        # subids = get_obj_ids(userlist_alt)

        # users = current_user.company.users

        all_users = current_user.company.users
        # users = [user for user in all_users if not user.delete]
        users = [user for user in all_users]


        allowed_categories = ["Manager","Director"]

        if current_user.username == "admin":
            users = fetch_all_users()
        elif current_user.company_user_group.name not in allowed_categories:
            users = [current_user]
        if current_user.username.startswith("qc"):
            users = current_user.company.users

        user_data = user_details(users)

        user_data_alt = []
        if current_user.username.startswith("qc"):
            kw_user = UserOp.fetch_user_by_username(KW_USER)
            if kw_user:
                print("got it",kw_user.username)
                for i in user_data:
                    print("here are ises",i["username"],"and kv_user:",kw_user.username)
                    if i["username"] == kw_user.username:
                        pass
                    else:
                        user_data_alt.append(i)
            else:
                user_data_alt = user_data
        else:
            user_data_alt = user_data
        

        userids = get_obj_ids(user_data_alt)

        # return render_template("ajax_userlist.html",items=userlist_alt,userids=subids)

        return render_template(
            "ajax_userlist.html",
            userids=userids,
            items=user_data_alt
            )


class FetchPayments(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")

        if target == "unclaimed":
            prop_id = request.args.get("propid")
            propid = get_identifier(prop_id)
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            sifted = []
            try:
                if prop.payment_bank == "PayBill" or prop.paymentdetails.mpesapaybill:
                    shortcode = prop.payment_bankacc
                    if not shortcode:
                        shortcode = prop.paymentdetails.mpesapaybill
                    if shortcode == "000000":
                        raw_unclaimed = prop.company.cbids
                    else:
                        raw_unclaimed = CtoBop.fetch_all_records_by_shortcode(shortcode)

                    for r in raw_unclaimed:
                        # targets = ["532406","964399","4012401","4081687"]
                        # if r.post_date.day == 6 and r.post_date.year == 2022 and r.post_date.month == 4:
                        #     pass
                        # else:
                        #     if r.business_shortcode in targets:
                        #         CtoBop.update_status(r,"claimed")
                        if r.status == "unclaimed":
                            sifted.append(r)
            except:
                pass

            unclaimed = ctb_payment_details(sifted)
            cbids = get_obj_ids(unclaimed)

            return render_template("ajax_unresolved_payments.html",cbids=cbids,items=unclaimed,dataperiod="")

        if target == "archived":
            prop_id = request.args.get("propid")
            propid = get_identifier(prop_id)
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            sifted = []
            if prop.payment_bank == "PayBill" or prop.paymentdetails.mpesapaybill:
                shortcode = prop.payment_bankacc
                if not shortcode:
                    shortcode = prop.paymentdetails.mpesapaybill
                raw_unclaimed = CtoBop.fetch_all_records_by_shortcode(shortcode)

                for r in raw_unclaimed:
                    # targets = ["532406","964399","4012401","4081687"]
                    # if r.post_date.day == 6 and r.post_date.year == 2022 and r.post_date.month == 4:
                    #     pass
                    # else:
                    #     if r.business_shortcode in targets:
                    #         CtoBop.update_status(r,"claimed")
                    if r.status == "archived":
                        sifted.append(r)

            unclaimed = ctb_payment_details(sifted)
            cbids = get_obj_ids(unclaimed)

            return render_template("ajax_archived_payments.html",cbids=cbids,items=unclaimed,dataperiod="")

        if target == "claimed":
            prop_id = request.args.get("propid")
            propid = get_identifier(prop_id)
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            sifted = []
            if prop.payment_bank == "PayBill" or prop.paymentdetails.mpesapaybill:
                shortcode = prop.payment_bankacc
                if not shortcode:
                    shortcode = prop.paymentdetails.mpesapaybill
                raw_unclaimed = CtoBop.fetch_all_records_by_shortcode(shortcode)

                for r in raw_unclaimed:
                    # targets = ["532406","964399","4012401","4081687"]
                    # if r.post_date.day == 6 and r.post_date.year == 2022 and r.post_date.month == 4:
                    #     pass
                    # else:
                    #     if r.business_shortcode in targets:
                    #         CtoBop.update_status(r,"claimed")
                    if r.status == "claimed" and r.post_date.month == prop.billing_period.month and r.post_date.year == prop.billing_period.year:
                        sifted.append(r)

            unclaimed = ctb_payment_details(sifted)
            cbids = get_obj_ids(unclaimed)

            return render_template("ajax_claimed_payments.html",cbids=cbids,items=unclaimed,dataperiod="")

        if target == "new":
            prop_id = request.args.get("propid")
            propid = get_identifier(prop_id)
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            db.session.expire(prop)
            payments = prop.payment_data

            period = get_billing_period(prop)

            if crm(current_user):
                filtered_payments = payments
            else:
                filtered_payments = fetch_current_billing_period_payments(period,payments)

            dict_item = ""
            if filtered_payments:
                latest_set = max(filtered_payments, key=lambda x: x.id)
                for i in filtered_payments:
                    if i == latest_set:
                        latest_set_index = filtered_payments.index(i)
                        break
                popped_latest_set = filtered_payments.pop(latest_set_index)

                item = popped_latest_set

                if item.ptenant:
                    tenant = item.ptenant.name
                else:
                    tenant = item.tenant.name

                dict_item={
                    'id':item.id,
                    'editid':PaymentOp.generate_editid(item),
                    'delid':PaymentOp.generate_delid(item),
                    'tenant':tenant,
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

            return render_template("ajax_payments_refresh.html",payids=payids,items=detailed_payments_list,dataperiod=get_str_month(period.month))

        if target == "new alt":
            prop_id = request.args.get("propid")
            propid = get_identifier(prop_id)

            prop = ApartmentOp.fetch_apartment_by_id(propid)
            db.session.expire(prop)
            payments = prop.payment_data

            period = get_billing_period(prop)

            if crm(current_user):
                filtered_payments = payments
            else:
                filtered_payments = fetch_current_billing_period_payments(period,payments)

            dict_item = ""
            if filtered_payments:
                latest_set = max(filtered_payments, key=lambda x: x.id)
                for i in filtered_payments:
                    if i == latest_set:
                        latest_set_index = filtered_payments.index(i)
                        break
                popped_latest_set = filtered_payments.pop(latest_set_index)

                item = popped_latest_set

                if item.ptenant:
                    tenant = item.ptenant.name
                else:
                    tenant = item.tenant.name

                dict_item={
                    'id':item.id,
                    'editid':PaymentOp.generate_editid(item),
                    'delid':PaymentOp.generate_delid(item),
                    'tenant':tenant,
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

            return render_template("ajax_tenant_payments.html",payids=payids,items=detailed_payments_list,prop=prop,dataperiod=get_str_month(period.month))

        if target == "voided":
            prop_id = request.args.get("propid")
            propid = get_identifier(prop_id)
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            db.session.expire(prop)

            if str(current_user.user_group) != "Owner":
                payments = prop.payment_data
            else:
                payments = []

            period = get_billing_period(prop)

            filtered_payments = fetch_current_billing_period_voided_payments(period,payments)

            detailed_payments_list = payment_details(filtered_payments)

            payids = get_obj_ids(detailed_payments_list)

            return render_template("ajax_payments_refresh.html",payids=payids,items=detailed_payments_list,dataperiod=get_str_month(period.month) + " voided",greyout="text-gray-500 b-none",active="disabled")

        elif target == "old":
            prop_id = request.args.get("propid")
            propid = get_identifier(prop_id)
            prop = ApartmentOp.fetch_apartment_by_id(propid)
            db.session.expire(prop)
            payments = prop.payment_data

            period = get_billing_period(prop)

            month = period.month -1 if period.month != 1 else 12
            year = period.year if period.month != 1 else period.year - 1

            filtered_payments = fetch_last_months_payments(month,year,payments)
            print(">>>>>",payments)

            detailed_payments_list = payment_details(filtered_payments)

            payids = get_obj_ids(detailed_payments_list)

            return render_template("ajax_payments_refresh.html",payids=payids,items=detailed_payments_list,dataperiod=get_str_month(month),greyout="text-gray-50 b-none",active="")

        else:
            tenantid = request.args.get('tenantid')
            ttype = request.args.get('ttype')

            if ttype == "owner" or ttype == "resident":
                tenant_obj = PermanentTenantOp.fetch_tenant_by_id(tenantid)
            else:
                tenant_obj = TenantOp.fetch_tenant_by_id(tenantid)

            tenant_payments = tenant_obj.payments

            # filtered_payments = filter_in_recent_data(tenant_payments)

            actual_payments = fetch_actual_payments(tenant_payments)

            detailed_payments_list = payment_details(actual_payments)

            payids = get_obj_ids(detailed_payments_list)

            return render_template("ajax_tenant_payments_refresh.html",items=detailed_payments_list,payids=payids)

class FetchSubmissions(Resource):
    @login_required
    def get(self):
        target = request.args.get("target")

        propname = request.args.get("prop")
        prop = ApartmentOp.fetch_apartment_by_name(propname)
        db.session.expire(prop)
        submissions = prop.submissions

        if not target:
            period = get_billing_period(prop)
        else:
            num_month = get_numeric_month(target)
            period = generate_date(num_month, prop.billing_period.year)

        gtotal = 0.0

        print(period,"MMMMMMMMMMMMMMMMMMMMMMMMMMMM")

        filtered_submissions = fetch_current_billing_period_data_alt(period,submissions)

        for i in filtered_submissions:
            gtotal += i.amount_paid

        detailed_submissions_list = submission_details(filtered_submissions)

        payids = get_obj_ids(detailed_submissions_list)
        
        print(detailed_submissions_list,">>>>>>>>>>>>>>>>>>>>>>>>>")

        return render_template("ajax_submissions_refresh.html",payids=payids,items=detailed_submissions_list,gtotal=f"{gtotal:,.1f}",dataperiod=get_str_month(period.month))


class FetchBills(Resource):
    @login_required
    def get(self):
        propid = request.args.get('propid')
        target = request.args.get('target')
        ttarget = request.args.get('ttarget')
        ttype = request.args.get('ttype')

        if target == "tenant bill":
            tenant_id = request.args.get('tenantid')

            tenantid = get_identifier(tenant_id)

            print("What is ttype?",ttype)

            #####################################################################################################
            #################### ORIGINAL VERSION #################################
            # if tenant_id.startswith("tnt") or ttarget == "ttarget" or ttype == "tenant":
            #     print("expecting tenant here")
            #     tenant_obj = TenantOp.fetch_tenant_by_id(tenantid)
            # else:
            #     print("expecting owner here")
            #     tenant_obj = PermanentTenantOp.fetch_tenant_by_id(tenantid)
            ######################################################################################################

            #####################################################################################################
            if ttype != "resident" and ttype != "owner":
                print("expecting tenant here")
                tenant_obj = TenantOp.fetch_tenant_by_id(tenantid)
            else:
                print("expecting owner here")
                tenant_obj = PermanentTenantOp.fetch_tenant_by_id(tenantid)

            if not tenant_obj:
                return '<span class="hide ms-5 ml-5">hide</span>' + err + "Invoices could not be retrieved"
            #######################################################################################################
                
            db.session.expire(tenant_obj)

            # tenant_bills = tenant_obj.monthly_charges
            # recent_bills = fetch_recent_bills(period,tenant_bills)
            recent_bills = tenant_obj.monthly_charges

            if recent_bills:
                detailed_bills = bill_details(recent_bills)

                billids = get_obj_ids_alt(detailed_bills)

                # billids = get_obj_ids(detailed_bills)

                template = "ajax_tenantbill2.html" if crm(current_user) else "ajax_tenantbill.html"

                return render_template(
                    template,
                    fieldshow_sec = "dispnone" if not get_sum(detailed_bills,"security") else "",
                    fieldshow_sev = "dispnone" if not get_sum(detailed_bills,"maintenance") else "",
                    fieldshow_elec = "dispnone" if not get_sum(detailed_bills,"electricity") else "",
                    fieldshow_garb = "dispnone" if not get_sum(detailed_bills,"garbage") else "",
                    fieldshow_water = "dispnone" if not get_sum(detailed_bills,"water") else "",
                    fieldshow_rent = "dispnone" if not get_sum(detailed_bills,"rent") else "",
                    fieldshow_dep = "dispnone" if not get_sum(detailed_bills,"deposit") else "",
                    fieldshow_arg = "dispnone" if not get_sum(detailed_bills,"agreement") else "",
                    fieldshow_fine = "dispnone" if not get_sum(detailed_bills,"penalty") else "",
                    fieldshow_arr = "dispnone" if not get_sum(detailed_bills,"arrears") else "",
                    items=detailed_bills,
                    billids=billids
                    )
 
            else:
                return "Unavailable"
        
        else:
            prop_obj = ApartmentOp.fetch_apartment_by_id(propid)
            db.session.expire(prop_obj)
            
            bills = prop_obj.monthlybills

            current_bills = fetch_current_billing_period_bills(prop_obj.billing_period,bills)

            detailed_bills = []

            renttotal_sum_members = []
            watertotal_sum_members = []
            electricitytotal_sum_members = []
            garbagetotal_sum_members = []
            securitytotal_sum_members = []
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
                    'water':f"{water_charge:,.1f}",
                    'electricity':electricity_charge,
                    'garbage':0.0,
                    'security':0.0,
                    'agreement':0.0,
                    'deposit':0.0,
                    'fine': 0.0,
                    'arrears': 0.0,
                    'total': water_charge + electricity_charge,
                    'paid': water_charge + electricity_charge,
                    'smsstatus': '<i class="fas fa-ban text-danger ml-3"></i>',
                    'smsactive':"disabled",
                    'mailstatus': '<i class="fas fa-ban text-danger ml-3"></i>',
                    'mailactive':"disabled",
                    'active':"disabled",
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
            electricitytotal = (f"{totalelectricity:,}")

            totalgarbage = sum_values(garbagetotal_sum_members)
            garbagesectotal = (f"{totalgarbage:,}")

            totalsecurity = sum_values(securitytotal_sum_members)
            garbagesectotal = (f"{totalsecurity:,}")

            totalagreement = sum_values(agreementtotal_sum_members)
            agreementtotal = (f"{totalagreement:,}")

            totaldeposit = sum_values(deposittotal_sum_members)
            deposittotal = (f"{totaldeposit:,}")

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
            fieldshow_elec = "dispnone" if not totalelectricity else ""
            fieldshow_garb = "dispnone" if not totalgarbage else ""
            fieldshow_water = "dispnone" if not totalwater else ""
            fieldshow_rent = "dispnone" if not totalrent else ""
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
                "ajax_prop_bills.html",
                prop=prop_obj,
                fieldshow_dep=fieldshow_dep,
                fieldshow_water=fieldshow_water,
                fieldshow_rent=fieldshow_rent,
                fieldshow_garb=fieldshow_garb,
                fieldshow_elec=fieldshow_elec,
                fieldshow_arg=fieldshow_arg,
                fieldshow_fine=fieldshow_fine,
                fieldshow_sec=fieldshow_sec,
                fieldshow_arr=fieldshow_arr,
                current_month=str_month,
                bills=detailed_bills,
                billids=billids
                )


class CollectionRatioReport(Resource):
    @login_required
    def get(self):

        selected_month = request.args.get("month")

        if selected_month:
            datestring = date_formatter_alt(selected_month)
            target_period = parse(datestring)
        else:
            target_period = datetime.datetime.now()

        ##################################################################################################
        collection_ratios = []

        grand_total_bills = 0.0
        grand_total_balances = 0.0
        grand_total_collections = 0.0
        grand_collection_ratio = 0.0

        ###################################################################################################
        props = fetch_all_apartments_by_user(current_user)

        for apartment in props:
            total_bills = 0.0
            total_balances = 0.0
            total_collections = 0.0
            real_collections = 0.0

            monthly_bills = apartment.monthlybills
            for item in monthly_bills:
                if item.month == target_period.month and item.year == target_period.year:

                    total_bills += item.total_bill if item.total_bill > 0 else 0
                    grand_total_bills += item.total_bill if item.total_bill > 0 else 0

                    total_balances += item.balance if item.balance > 0 else 0
                    grand_total_balances += item.balance if item.balance > 0 else 0

                    total_collections += item.paid_amount if item.paid_amount > 0 else 0
                    grand_total_collections += item.paid_amount if item.paid_amount > 0 else 0

                    if item.balance > -0.99999:
                        real_collections += item.paid_amount if item.paid_amount > 0 else 0
                    else:
                        real_collections += item.total_bill if item.total_bill > 0 else 0

                                           
            try:
                collection_percentage = real_collections / total_bills * 100
                grand_collection_ratio += collection_percentage
            except:
                collection_percentage = 0

            cr_item = {
                "code":apartment.id,
                "name":apartment.name,
                "bills":total_bills,
                "paid":real_collections,
                "unpaid":total_balances,
                "ratio":f"{collection_percentage:,.1f} %"
            }


            collection_ratios.append(cr_item)


        grandtotal = (f"{grand_total_bills:,}")

        grandunpaid = (f"{grand_total_balances:,}")

        grandpaid = (f"{grand_total_collections:,}")

        try:
            cp = grand_collection_ratio/len(props)
        except:
            cp = 0.0

        grandratio = f"{cp:,.1f} %"

        strmonth=get_str_month(target_period.month)
        timeline = f"{strmonth.upper()} - {target_period.year}"

        return Response(render_template(
            'report_cr_statement.html',
            tenantlist=[],
            timeline = timeline,
            grandtotal=grandtotal,
            grandpaid=grandpaid,
            grandunpaid=grandunpaid,
            grandratio=grandratio,
            bills=collection_ratios,
            paging=page(collection_ratios),
            logopath=logo(current_user.company)[0],
            mobilelogopath=logo(current_user.company)[1],
            fulllogopath=logo(current_user.company)[2],
            letterhead=logo(current_user.company)[3],
            company=current_user.company,
            reportdate = datetime.datetime.now().strftime("%d/%m/%Y"),
            name=current_user.name))



class OfficePnL(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_office_pnl_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))

class OfficeExpenses(Resource):
    @login_required
    def get(self):
        selected_apartment = request.args.get("prop")
        selected_month = request.args.get("month")


        if not selected_apartment:

            apartment_list = fetch_all_apartments_by_user(current_user)

            return Response(render_template(
                'report_office_expenses_statement.html',
                tenantlist=[],
                prop_obj=None,
                props=apartment_list,
                logopath=logo(current_user.company)[0],
                mobilelogopath=logo(current_user.company)[1],
                name=current_user.name))

