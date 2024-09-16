        # if current_user.usercode == "3245":
        #     propps = fetch_all_apartments_by_user(current_user)
        #     for prop in propps:
        #         if prop.name != "Benard" and prop.name != "Alice Properties Tolens" and prop.name != "paul & teresiah":
        #             # if not prop.payment_bankacc:
        #             ApartmentOp.update_bank(prop,"Equity","0240190724036")

        #         if prop.name == "paul & teresiah":
        #             houses = houseauto(prop.id)
        #             for h in houses:
        #                 if h.name in ["4","5","6","7","9","10","11","12","13","14"] :
        #                     HouseOp.update_bank(h,"Equity","0150191724552")
        #                 else:
        #                     HouseOp.update_bank(h,"Equity","0470166657097")

        #     # co = current_user.company
        #     # CompanyOp.set_rem_quota(co,"400")





        # cco = current_user.company
        # CompanyOp.set_rem_quota(cco,300)

        # propp =  ApartmentOp.fetch_apartment_by_name("Comelea rentals")
        # if propp:
        #     print(propp)
        #     ApartmentOp.update_name(propp,"Chomelea Rentals")
        # else:
        #     print("hehhehe")
        
        # user_objj = UserOp.fetch_user_by_username("abed.limo3")
        # if user_objj:
        #     username = "abedy.limo3"
        #     email = "abedy.limo3@gmail.com"
        #     UserOp.update_username_email(user_objj,username,email)
        # else:
        #     print("User not found")

        # response = sms.send("Dear Shem, your account has been activated. Have a goodnight.", ["+254719661892"],"KIOTAPAY")

        # co = CompanyOp.fetch_company_by_name("Nairuti & Associates")
        # props = co.props

        # userr = UserOp.fetch_user_by_id(35)

        # current_props = fetch_all_apartments_by_user(userr)

        # for prop in props:
        #     if prop in current_props:
        #         pass
        #     else:
        #         UserOp.relate(userr,prop)

        # # for prop in current_props:
        # #     if prop in props:
        # #         ApartmentOp.terminate(prop,userr)

        
        # prop = ApartmentOp.fetch_apartment_by_id(34)
        
        # rreadings = prop.meter_readings
        # for r in rreadings:
        #     if r.description != "initial reading":
        #         # print ("Desc# ",r.description,"Units# ",r.units,"Amount# ",r.charged,"#Period# ",r.reading_period)

        #         datee = generate_date(5,2021)
        #         MeterReadingOp.update_reading_period(r,datee)
                
        # ownerp = OwnerOp.fetch_owner_by_name("Jacob Nairuti")
        # OwnerOp.update_phone(ownerp,"0700000018")

        # tt = TenantOp.fetch_tenant_by_id(435)
        # TenantOp.delete(tt)

        # meters = MeterOp.fetch_all_meters()
        # for meter in meters:
        #     if not meter.metertype:
        #         print("Updating meter")
        #         MeterOp.update_metertype(meter,"water")

        # prop = ApartmentOp.fetch_apartment_by_id(40)
        # period = generate_date(4,2021)
        # ApartmentOp.update_billing_period(prop,period)
        
        # billss = prop.monthlybills
        # for i in billss:
        #     if i.month == 4 and i.year == 2021:
        #         MonthlyChargeOp.delete(i)

        # chargess = prop.charges
        # for i in chargess:
        #     if i.date.month == 5 and i.date.year == 2021 and i.charge_type_id == 2 and i.reading_id:
        #         ChargeOp.update_compiled_status(i,False)
        #         print("Kot",i.house,"type",i,"reading",i.reading_id,"amount",i.amount,"state",i.compiled,"date",i.date.date())
        #         # # ChargeOp.delete(i)

        # meterreadingss = prop.meter_readings
        # for i in meterreadingss:
        #     if i.reading_period.month == 4:
        #         MeterReadingOp.update_charge_status(i,False)

        # if current_user.username == "tharaenterpriseagencies":
        #     tenantss = tenantauto(40)
        #     for i in tenantss:
        #         raw_tel = i.phone
        #         rraw_tel = raw_tel[2:]
        #         tel=f'0{rraw_tel}'
        #         TenantOp.update_phone(i,tel)

        # reading_obj = MeterReadingOp.fetch_specific_reading(858)
        # if reading_obj:
        #     MeterReadingOp.delete(reading_obj)

        # company = current_user.company

        # if company.name == "Rikena Property Solutions":
        #     props = company.props
        #     for prop in props:
        #         ApartmentOp.update_billing_period(prop,generate_date(3,2021))
        #         CompanyOp.set_rem_quota(company,900)
        #         CompanyOp.set_smsquota(company,900)
        #         CompanyOp.set_quota_month(company,time.month)

        #     readings = prop.meter_readings
        #     for reading in readings:
        #         if reading.description != "initial reading":
        #             MeterReadingOp.delete(reading)



        # proppa = ApartmentOp.fetch_apartment_by_id(4)
        # ten_ants = tenantauto(proppa.id)
        # for ant in ten_ants:
        #     hse = check_house_occupied(ant)[1]
        #     billls = hse.monthlybills
        #     for i in billls:
        #         paid = (f"{i.paid_amount:,.1f}")
        #         balance = (f"{i.balance:,}")
        #         arrears = i.balance
        #         str_month = get_str_month(i.month)

        #         co = current_user.company
        #         rem_sms =co.remainingsms
        #         if ant.sms:
        #             if rem_sms > 0:
        #                 print("sending sms")
        #                 #Send the SMS
        #                 tele = ant.phone
        #                 name = ant.name
        #                 phonenum = sms_phone_number_formatter(tele)

        #                 try:
        #                     recipient = [phonenum]
        #                     if arrears > 0.0 :
        #                         message = f"Good morning {name}, your cummulative rent&water payment for {str_month} is Kes {paid}. Balance: Kes {balance}. Please clear your balance as soon as possible to help us serve you better. ~ MojaMbili Homes."
        #                     elif arrears < 0.0:
        #                         bbf = -1 * arrears
        #                         sms_bbf = (f"{bbf:,} ")
        #                         message = f"Good morning {name}, your cummulative rent&water payment for {str_month} is Kes {paid}. April advance payment: Kes {sms_bbf}. Have a good day. ~ MojaMbili Homes."
        #                     else:
        #                         message =  f"Good morning {name}, your cummulative rent&water payment for {str_month} is Kes {paid}. Balance: Kes 0.0. Have a good day. ~ MojaMbili Homes."
                            
        #                     response = sms.send(message, recipient)
        #                     print(response)
        #                     rem_sms -= 1
        #                     CompanyOp.set_rem_quota(co,rem_sms)
        #                 except Exception as e:
        #                     print(f"Houston, we have a problem {e}")

        #             else:
        #                 print("sms depleted")
        #         else:
        #             print("Tenant does not accept messages")

        

        # xtenants = tenantauto_reverse(4)
        # for i in xtenants:
        #     vacate_period = i.vacate_date - relativedelta(months=1)
        #     AllocateTenantOp.update_vacate_period(i,vacate_period)

        # xtenants = tenantauto_reverse(2)
        # for i in xtenants:
        #     vacate_period = i.vacate_date - relativedelta(months=1)
        #     AllocateTenantOp.update_vacate_period(i,vacate_period)

        # xtenants = tenantauto_reverse(6)
        # for i in xtenants:
        #     vacate_period = i.vacate_date - relativedelta(months=1)
        #     AllocateTenantOp.update_vacate_period(i,vacate_period)



        # props = ApartmentOp.fetch_all_apartments()
        # for prop in props:
        #     if not prop.billing_period:
        #         ApartmentOp.update_billing_period(prop,generate_date(3,2021))

        # pay_obj = PaymentOp.fetch_payment_by_id(287)
        # prop = pay_obj.apartment
        # period = get_billing_period(prop)
        # print("BEFORE UPDATE",pay_obj.pay_period)
        # PaymentOp.update_payperiod(pay_obj,period)

        # prop = ApartmentOp.fetch_apartment_by_id(4)
        # period = get_billing_period(prop)
        # tenant_obj = TenantOp.fetch_tenant_by_id(pay_obj.tenant_id)
        # monthly_charges = tenant_obj.monthly_charges
        # specific_charge_obj = get_specific_monthly_charge_obj(monthly_charges,period.month)
        # if specific_charge_obj:
        #     bala = specific_charge_obj.balance
        #     bala-=pay_obj.amount
        #     MonthlyChargeOp.update_balance(specific_charge_obj,bala)

        #     paid_amount = specific_charge_obj.paid_amount
        #     cumulative_pay = paid_amount + pay_obj.amount
        #     MonthlyChargeOp.update_payment(specific_charge_obj,cumulative_pay)
        #     MonthlyChargeOp.update_payment_date(specific_charge_obj,pay_obj.pay_date)


        
        # prop = ApartmentOp.fetch_apartment_by_id(6)
        # readings = prop.meter_readings
        # for i in readings:
        #     if i.reading_period.month == 4:
        #         reading_period = generate_date(3,2021)
        #         MeterReadingOp.update_reading_period(i,reading_period)

        # reading_obj = MeterReadingOp.fetch_specific_reading(379)
        # MeterReadingOp.update_prev(reading_obj,27)

        # tenantss = TenantOp.fetch_all_tenants()
        # for t in tenantss:
        #     if not t.sms and t.apartment_id != 6:
        #         TenantOp.update_can_receive_sms(t,True)


        # tenant_objj = TenantOp.fetch_tenant_by_id(171)
        # TenantOp.update_balance(tenant_objj,24100.0)
        # arr = tenant_objj.monthly_charges

        # monthlybill_obj = get_specific_monthly_charge_obj(arr,3)
        # MonthlyChargeOp.update_agreement(monthlybill_obj,0.0)
        # MonthlyChargeOp.update_total(monthlybill_obj,24100)
        # MonthlyChargeOp.update_balance(monthlybill_obj,24100)

        # punit = UserOp.fetch_user_by_id(17)
        # # UserOp.update_status(punit,True)
        # new_user = UserOp.fetch_user_by_id(19)
        # punit_co = punit.company
        # company_properties = punit_co.props
        # for prop in company_properties:
        #     UserOp.relate(new_user,prop)
        # period = generate_date(time.month,time.year)
        # CompanyOp.update_billing_period(punit_co,period)

        # if current_user.id  == 6:
        #     prop_obj = ApartmentOp.fetch_apartment_by_name("Jendi Heights")
        #     db.session.expire(prop_obj)


        # tenants = tenantauto(prop_obj.id)
        # for tenant in tenants:
        #     if tenant.id == 74:
        #         new_bal = 4400
        #         TenantOp.update_balance(tenant,new_bal)
        #     else:
        #         bal = tenant.balance
        #         new_bal = bal/2
        #         TenantOp.update_balance(tenant,new_bal)

        # del_items = prop_obj.monthlybills
        # for i in del_items:
        #     if i.date.month == 2:
        #         MonthlyChargeOp.delete(i)

        # co = current_user.company
        # date = generate_date(2,2021)
        # CompanyOp.update_billing_period(co,date)

        # payment_obj = PaymentOp.fetch_payment_by_id(248)
        # PaymentOp.update_payment(payment_obj,17700,17000,700)
        # tenant_obj = TenantOp.fetch_tenant_by_id(80)
        # TenantOp.update_balance(tenant_obj,700)
        # monthly_charge_obj = get_specific_monthly_charge_obj(tenant_obj.monthly_charges,2)
        # MonthlyChargeOp.update_payment(monthly_charge_obj,17000)
        # MonthlyChargeOp.update_balance(monthly_charge_obj,700)

#     for bill in all_bills:
#         if bill.month == 2 and bill.year == 2022 and bill.rent_balance and not bill.rent_paid and bill.arrears == 0.0:
#             print("PROPLEMATIC BILL>>>>>",bill.apartment,bill.house,bill.total_bill,bill.paid_amount,"rent",bill.rent,"rent arrears",bill.rent_balance,"rentpaid",bill.rent_paid,"bal",bill.rent_due)
#             MonthlyChargeOp.update_balances(bill,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0)
#             MonthlyChargeOp.update_dues(bill,bill.rent,bill.water,bill.electricity,bill.garbage,bill.security,bill.maintenance,bill.penalty,bill.deposit,bill.agreement)

        # for bill in all_bills:
        # if bill.month == 2 and bill.year == 2022 and bill.rent_balance and not bill.rent_paid and bill.arrears > 0 and not bill.paid_amount:
        #     print("PROPLEMATIC BILL>>>>>",bill.apartment,bill.house,bill.total_bill,bill.paid_amount,"rent",bill.rent,"rent arrears",bill.rent_balance,"rentpaid",bill.rent_paid,"bal",bill.rent_due)
        #     MonthlyChargeOp.update_balances(bill,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0)
        #     MonthlyChargeOp.update_dues(bill,bill.rent,bill.water,bill.electricity,bill.garbage,bill.security,bill.maintenance,bill.penalty,bill.deposit,bill.agreement)


import psycopg2

try:
    conn = psycopg2.connect(
        dbname="maindb",
        user="doadmin",
        password="AVNS_mkXV0cjvPdXAeho00m7",
        host="db-postgresql-nyc1-45362-may-28-backup-do-user-14457444-0.c.db.ondigitalocean.com",
        port="25060"
    )
    print("Connection successful")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
