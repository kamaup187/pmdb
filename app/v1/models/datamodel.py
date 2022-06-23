from flask_login import UserMixin
from app import db
import datetime

#table names are in singular for many  to many relations
apartment_table = db.Table('apartment',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('apartment_id', db.Integer, db.ForeignKey('apartments.id'))
)

house_table = db.Table('house',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('house_id', db.Integer, db.ForeignKey('houses.id'))
)

class UserGroup(db.Model):
    """db model class"""

    __tablename__ = 'usergroups'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String,unique=True)
    description = db.Column(db.String)

    users = db.relationship('User', backref='user_group',order_by='User.name', cascade="all, delete-orphan")
    # roles_assigned = db.relationship('AssignGroupRole',backref='usergroup', cascade="all, delete-orphan")#grouprole_assignment object

    def __repr__(self):
        return self.name

class Company(db.Model):
    """db model class"""

    __tablename__ = 'companies'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String,unique=True)
    city = db.Column(db.VARCHAR)
    region = db.Column(db.VARCHAR)
    street_address = db.Column(db.VARCHAR)
    mail_box = db.Column(db.VARCHAR)
    email = db.Column(db.VARCHAR)
    phone = db.Column(db.VARCHAR)
    sphone = db.Column(db.VARCHAR)
    description = db.Column(db.String)

    receipt_num = db.Column(db.Integer)

    balance = db.Column(db.Float,default=0)
    subscription = db.Column(db.Float,default=0)
    active = db.Column(db.Boolean,default=True)

    billing_period = db.Column(db.DateTime,default=db.func.current_timestamp())

    smsquota = db.Column(db.Integer,default=500)
    remainingsms = db.Column(db.Integer,default=500)
    quotamonth = db.Column(db.Integer,default=7)
    sms_provider = db.Column(db.String,default="AFRICASTALKING")
    # comment = db.Column(db.String)

    users = db.relationship('User', backref='company',order_by='User.name', cascade="all, delete-orphan")
    reps = db.relationship('SalesRep', backref='company',order_by='SalesRep.username', cascade="all, delete-orphan")

    shortcodes = db.relationship('Shortcode', backref='company',order_by='Shortcode.shortcode', cascade="all, delete-orphan")
    props = db.relationship('Apartment', backref='company',order_by='Apartment.name', cascade="all, delete-orphan")
    groups = db.relationship('CompanyUserGroup', backref='company',order_by='CompanyUserGroup.name', cascade="all, delete-orphan")

    bills = db.relationship('ClientBill', backref='company',order_by='ClientBill.id', cascade="all, delete-orphan")
    payments = db.relationship('ClientPayment', backref='company',order_by='ClientPayment.id', cascade="all, delete-orphan")
    template = db.relationship('TextTemplate',backref='company', cascade="all, delete-orphan")
    sent_messages = db.relationship('SentMessages',backref='company',order_by='SentMessages.date', cascade="all, delete-orphan")
    remits = db.relationship('LandlordRemittance',backref='company',order_by='LandlordRemittance.date_remitted', cascade="all, delete-orphan")


    def __repr__(self):
        return self.name


class Shortcode(db.Model):
    """db model class"""

    __tablename__ = 'shortcodes'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    shortcode = db.Column(db.VARCHAR)
    description = db.Column(db.String)

    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

    def __repr__(self):
        return self.shortcode


class CompanyUserGroup(db.Model):
    """db model class"""

    __tablename__ = 'company_usergroups'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

    users = db.relationship('User', backref='company_user_group',order_by='User.name', cascade="all, delete-orphan")
    roles_assigned = db.relationship('AssignGroupRole',backref='company_usergroup', cascade="all, delete-orphan")#grouprole_assignment object

    def __repr__(self):
        return self.name

class GroupRole(db.Model):
    """db model class"""

    __tablename__ = 'grouproles'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String,unique=True,nullable=False)
    groups_assigned = db.relationship('AssignGroupRole',backref='grouprole', cascade="all, delete-orphan")#grouprole_assignment object

    def __repr__(self):
        return self.name


class User(db.Model,UserMixin):
    """db model class"""

    __tablename__ = 'users'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    name = db.Column(db.String,nullable=False)
    phone = db.Column(db.VARCHAR,nullable=False)
    national_id = db.Column(db.String)
    email = db.Column(db.VARCHAR)
    usercode = db.Column(db.String)
    username = db.Column(db.String)
    password = db.Column(db.VARCHAR,nullable=False)
    active = db.Column(db.Boolean,default=True)

    activation_link = db.Column(db.String,default="null")
    
    user_id = db.Column(db.Integer)

    user_group_id = db.Column(db.Integer, db.ForeignKey(UserGroup.id))
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))
    company_usergroup_id = db.Column(db.Integer, db.ForeignKey(CompanyUserGroup.id))

    apartments = db.relationship("Apartment",secondary=apartment_table,backref=db.backref('users'))
    houses = db.relationship("House",secondary=house_table,backref=db.backref('users'))

    expenses = db.relationship('InternalExpense', backref='user', cascade="all, delete-orphan")
    logins = db.relationship("UserLoginData",backref="user",cascade="all, delete-orphan")
    rep = db.relationship('SalesRep',backref='user',uselist=False, cascade="all, delete-orphan")


    def __repr__(self):
        return self.username

class UserLoginData(db.Model):

    __tablename__ = 'logins'

    id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    logged_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    logged_on_last = db.Column(db.DateTime, default=db.func.current_timestamp())
    frequency = db.Column(db.Integer,default=1)

    tenant_frequency = db.Column(db.Integer,default=0)
    search_frequency = db.Column(db.Integer,default=0)
    invoice_frequency = db.Column(db.Integer,default=0)
    payment_frequency = db.Column(db.Integer,default=0)
    report_frequency = db.Column(db.Integer,default=0)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    
class AssignGroupRole(db.Model):#has no children of her own
    """db model class"""

    __tablename__ = 'accessrights'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    accessright = db.Column(db.Boolean,default=True)

    company_usergroup_id = db.Column(db.Integer, db.ForeignKey(CompanyUserGroup.id))
    grouprole_id = db.Column(db.Integer, db.ForeignKey(GroupRole.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))


    def __repr__(self):
        rolename = GroupRole.query.filter_by(id=self.grouprole_id).first()
        role = str(rolename)
        return role

class Owner(db.Model):
    """db model class"""

    __tablename__ = 'owners'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String,nullable=False)
    phone = db.Column(db.VARCHAR)
    email = db.Column(db.VARCHAR)
    uniquename = db.Column(db.VARCHAR)
    national_id = db.Column(db.String)
    # company_name = db.Column(db.VARCHAR)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    
    apartments = db.relationship("Apartment",backref=db.backref('owner'),cascade="all, delete-orphan")

    def __repr__(self):
        return self.uniquename

class BugsReport(db.Model):
    """bugs db model class"""

    __tablename__ = "bugs"
    id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    description = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

class Location(db.Model):
    """db model class"""

    __tablename__ = 'regions'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String,unique=True)
    description = db.Column(db.String)
    apartments = db.relationship('Apartment', backref='location', cascade="all, delete-orphan")

    def __repr__(self):
        return self.name

class Apartment(db.Model):
    """db model class"""

    __tablename__ = 'apartments'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String)
    uniqueid = db.Column(db.String)
    image_url = db.Column(db.VARCHAR)
    agreement_fee = db.Column(db.Float,default=0)

    commission_type = db.Column(db.String, default="collected")
    commission = db.Column(db.Float,default=0)
    int_commission = db.Column(db.Float,default=0)
    shortcode = db.Column(db.String)
    billprogress = db.Column(db.String)
    consumer_key = db.Column(db.VARCHAR)
    consumer_secret = db.Column(db.VARCHAR)
    reminder_status = db.Column(db.String,default="no")

    garbage_collector = db.Column(db.VARCHAR)
    garbage_collector_tel = db.Column(db.VARCHAR)
    garbage_collector_bank = db.Column(db.VARCHAR)
    garbage_collector_bankacc = db.Column(db.VARCHAR)

    payment_bank = db.Column(db.VARCHAR)
    payment_bankaccname = db.Column(db.VARCHAR)
    payment_bankacc = db.Column(db.VARCHAR)

    landlord_bank = db.Column(db.VARCHAR)
    landlord_bankaccname = db.Column(db.VARCHAR)
    landlord_bankacc = db.Column(db.VARCHAR)

    landlord_bank_two = db.Column(db.VARCHAR)
    landlord_bankaccname_two = db.Column(db.VARCHAR)
    landlord_bankacc_two = db.Column(db.VARCHAR)

    agency_managed = db.Column(db.Boolean,default=True)

    caretaker_id = db.Column(db.String)#national id for unique identification
    
    agent_id = db.Column(db.String)#national id for unique identification
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

    location_id = db.Column(db.Integer, db.ForeignKey(Location.id))
    owner_id = db.Column(db.Integer, db.ForeignKey(Owner.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    billing_period = db.Column(db.DateTime,default=db.func.current_timestamp())

    housecodes = db.relationship('HouseCode', backref='prop',order_by='HouseCode.codename', cascade="all, delete-orphan")
    houses = db.relationship('House', backref='apartment', cascade="all, delete-orphan")
    tenants = db.relationship('Tenant', backref='apartment', cascade="all, delete-orphan")
    ptenants = db.relationship('PermanentTenant', backref='apartment', cascade="all, delete-orphan")

    tenants_allocated = db.relationship('Occupancy',backref='apartment',order_by='Occupancy.date' , cascade="all, delete-orphan")
    meters = db.relationship('Meter',backref='apartment',order_by='Meter.meter_number' , cascade="all, delete-orphan")
    # meters_allocation = db.relationship('AllocateMeter',backref='apartment',order_by='AllocateMeter.date' , cascade="all, delete-orphan")
    elec_readings = db.relationship('ElectricityReading',backref='apartment', order_by='ElectricityReading.date',cascade="all, delete-orphan")
    meter_readings = db.relationship('MeterReading',backref='apartment_reading', order_by='MeterReading.date',cascade="all, delete-orphan")
    charges = db.relationship('Charge',backref='apartment',order_by='Charge.date', cascade="all, delete-orphan")
    monthlybills = db.relationship('MonthlyCharge',backref='apartment',order_by='MonthlyCharge.date', cascade="all, delete-orphan")
    landlordsummaries = db.relationship('LandlordSummary',backref='apartment',order_by='LandlordSummary.date', cascade="all, delete-orphan")
    payment_data = db.relationship('Payment',backref='apartment',order_by='Payment.date', cascade="all, delete-orphan")
    submissions = db.relationship('Submission',backref='apartment',order_by='Submission.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    tenantrequests = db.relationship('TenantRequest',backref='apartment',order_by='TenantRequest.date', cascade="all, delete-orphan")
    transferrequests = db.relationship('TransferRequest',backref='apartment',order_by='TransferRequest.date', cascade="all, delete-orphan")
    clearrequests = db.relationship('ClearanceRequest',backref='apartment',order_by='ClearanceRequest.date', cascade="all, delete-orphan")
    expenses = db.relationship('InternalExpense', backref='apartment', cascade="all, delete-orphan")
    messages = db.relationship('InternalMessages',backref='apartment',order_by='InternalMessages.date', cascade="all, delete-orphan")
    reminders = db.relationship('Reminder',backref='apartment',order_by='Reminder.date', cascade="all, delete-orphan")
    sent_messages = db.relationship('SentMessages',backref='apartment',order_by='SentMessages.date', cascade="all, delete-orphan")
    paymentdetails = db.relationship('PaymentDetail',backref='apartment',uselist=False,cascade="all, delete-orphan")
    remits = db.relationship('LandlordRemittance',backref='apartment',order_by='LandlordRemittance.date_remitted', cascade="all, delete-orphan")



    def __repr__(self):
        return self.name


class PaymentDetail(db.Model):
    """db model class"""

    __tablename__ = 'paymentdetails'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    paytype = db.Column(db.VARCHAR)
    nartype = db.Column(db.VARCHAR)
    mpesapaybill = db.Column(db.VARCHAR)
    
    bankname = db.Column(db.VARCHAR)
    bankbranch = db.Column(db.VARCHAR)
    bankaccountname = db.Column(db.VARCHAR)
    bankaccountnumber = db.Column(db.VARCHAR)
    bankpaybill = db.Column(db.VARCHAR)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))

    def __repr__(self):
        return self.paytype


class SalesRep(db.Model):
    """db model class"""

    __tablename__ = 'salesreps'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.VARCHAR,default="Sales Agent")
    phone = db.Column(db.VARCHAR)

    username = db.Column(db.String)
    active = db.Column(db.Boolean,default=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    monthly_commission = db.Column(db.Float,default=0)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

    sales = db.relationship('MonthlyChargeTwo',backref='rep', cascade="all, delete-orphan")
    clients = db.relationship('PermanentTenant',backref='rep',order_by='PermanentTenant.date', cascade="all, delete-orphan")
    
    def __repr__(self):
        return str(self.username)

# class Member(db.Model):
#     """db model class"""

#     __tablename__ = 'members'

#     id = db.Column(db.Integer,autoincrement=True,primary_key=True)
#     membership_level = db.Column(db.String,nullable=False)
#     created_by = db.Column(db.String)

#     user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    
#     apartments = db.relationship("Apartment",secondary=apartment_table,backref=db.backref('members'))

class ChargeType(db.Model):
    """db model class"""

    __tablename__ = 'chargetypes'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    charge_type = db.Column(db.String)
    charges = db.relationship('Charge',backref='charge_type',order_by='Charge.date', cascade="all, delete-orphan")#use backref chargetype to access the parent directly from child
    
    def __repr__(self):
        return self.charge_type

class HouseCode(db.Model):
    """db model class"""

    __tablename__ = 'housecodes'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    codename = db.Column(db.String)

    listprice = db.Column(db.Float,default=0)

    rentrate = db.Column(db.Float,default=0)
    watercharge = db.Column(db.Float,default=0)
    waterrate = db.Column(db.Float,default=0)
    waterrate1 = db.Column(db.Float,default=0)
    waterrate2 = db.Column(db.Float,default=0)
    waterrate3 = db.Column(db.Float,default=0)

    seweragerate = db.Column(db.Float,default=0)
    agreementrate = db.Column(db.Float,default=0)

    electricityrate = db.Column(db.Float,default=0)
    securityrate = db.Column(db.Float,default=0)
    servicerate = db.Column(db.Float,default=0)
    garbagerate = db.Column(db.Float,default=0)
    finerate = db.Column(db.Float,default=0)

    waterdep = db.Column(db.Float,default=0)
    elecdep = db.Column(db.Float,default=0)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    createdby = db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedby= db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedon = db.Column(db.DateTime, default=db.func.current_timestamp())

    # houses = db.relationship('House', backref='housecode', cascade="all, delete-orphan")
    houses = db.relationship('House', backref='housecode')

    def __repr__(self):
        return self.codename

class House(db.Model):
    """db house model class"""

    __tablename__ = 'houses'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.VARCHAR)
    status = db.Column(db.String, default="available")

    description = db.Column(db.String)
    billable = db.Column(db.Boolean,default=True)
    payment_bank = db.Column(db.VARCHAR)
    payment_bankacc = db.Column(db.VARCHAR)

    watertarget = db.Column(db.String,default="tenant")
    servicetarget = db.Column(db.String,default="owner")

    housecode_id = db.Column(db.Integer, db.ForeignKey(HouseCode.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    meter_allocated = db.relationship('AllocateMeter',backref='house', cascade="all, delete-orphan")
    tenant_allocated = db.relationship('Occupancy',backref='house', cascade="all, delete-orphan")
    meter_readings = db.relationship('MeterReading',backref='house', order_by='MeterReading.date',cascade="all, delete-orphan")
    elec_readings = db.relationship('ElectricityReading',backref='house', order_by='ElectricityReading.date',cascade="all, delete-orphan")
    charges = db.relationship('Charge',backref='house',order_by='Charge.date', cascade="all, delete-orphan")
    monthlybills = db.relationship('MonthlyCharge',backref='house',order_by='MonthlyCharge.date', cascade="all, delete-orphan")
    invoices = db.relationship('MonthlyChargeTwo',backref='house', cascade="all, delete-orphan")
    landlordsummaries = db.relationship('LandlordSummary',backref='house',order_by='LandlordSummary.month', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    payments = db.relationship('Payment',backref='house',order_by='Payment.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    submissions = db.relationship('Submission',backref='house',order_by='Submission.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    split_payments = db.relationship('SplitPayment',backref='house',order_by='SplitPayment.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    tenantrequests = db.relationship('TenantRequest',backref='house',order_by='TenantRequest.date', cascade="all, delete-orphan")
    transferrequests = db.relationship('TransferRequest',backref='house',order_by='TransferRequest.date', cascade="all, delete-orphan")
    clearrequests = db.relationship('ClearanceRequest',backref='house',order_by='ClearanceRequest.date', cascade="all, delete-orphan")

    owner = db.relationship('PermanentTenant',backref='house', uselist=False, cascade="all, delete-orphan")

    
    def __repr__(self):
        return self.name

class Meter(db.Model):
    """db model class"""

    __tablename__ = 'meters'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    serial_number = db.Column(db.VARCHAR)
    meter_number = db.Column(db.VARCHAR)
    initial_reading = db.Column(db.Integer,default=0)
    decitype = db.Column(db.String)
    metertype = db.Column(db.String)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    meter_readings = db.relationship('MeterReading',backref='meter', order_by='MeterReading.date',cascade="all, delete-orphan")
    elec_readings = db.relationship('ElectricityReading',backref='meter', order_by='ElectricityReading.date',cascade="all, delete-orphan")
    house_allocated = db.relationship('AllocateMeter',backref='meter', cascade="all, delete-orphan")#needs refactoring, house_allocated is not list of houses but single one to one allocation
    billings = db.relationship('Charge',backref='meter', order_by='Charge.date',cascade="all, delete-orphan")


    def __repr__(self):
        return self.meter_number

class AllocateMeter(db.Model):#has no children of her own
    """db model class"""

    __tablename__ = 'allocations'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    description = db.Column(db.String)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    active = db.Column(db.Boolean,default=True)
    cleared_by = db.Column(db.String)
    
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    meter_id = db.Column(db.Integer, db.ForeignKey(Meter.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    # def __repr__(self):
    #     rep = self.meter_id
    #     data=str(rep)
    #     return data

class MeterReading(db.Model):
    """db model class"""

    __tablename__ = 'meterreadings'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    description = db.Column(db.String)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    # month = db.Column(db.Integer)
    reading_period = db.Column(db.DateTime,default=db.func.current_timestamp())
    reading = db.Column(db.Integer)
    last_reading = db.Column(db.Integer)
    units = db.Column(db.Float,nullable=False)
    charged = db.Column(db.Boolean,default=False)
    sms_invoice = db.Column(db.String,default="pending")
    smsid = db.Column(db.VARCHAR)

    #foreign keys
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    meter_id = db.Column(db.Integer, db.ForeignKey(Meter.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    createdby = db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedby= db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedon = db.Column(db.DateTime, default=db.func.current_timestamp())

    charge = db.relationship('Charge',backref='reading', uselist=False, cascade="all, delete-orphan")

    # def __repr__(self):
    #     rep = self.id
    #     data = str(rep)
    #     return data

class ElectricityReading(db.Model):
    """db model class"""

    __tablename__ = 'electricityreadings'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    description = db.Column(db.String)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    # month = db.Column(db.Integer)
    reading_period = db.Column(db.DateTime,default=db.func.current_timestamp())
    reading = db.Column(db.Integer)
    last_reading = db.Column(db.Integer)
    units = db.Column(db.Float,nullable=False)
    charged = db.Column(db.Boolean,default=False)
    #foreign keys
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    meter_id = db.Column(db.Integer, db.ForeignKey(Meter.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    charge = db.relationship('Charge',backref='elecreading', uselist=False, cascade="all, delete-orphan")

    # def __repr__(self):
    #     rep = self.id
    #     data = str(rep)
    #     return data



# class ChargeDesc(db.Model):
#     """db model class"""

#     __tablename__ = 'chargedescriptions'

#     id = db.Column(db.Integer,autoincrement=True,primary_key=True)
#     amount = db.Column(db.Float,default=0)
#     date = db.Column(db.DateTime,default=db.func.current_timestamp())

#     charge_type_id = db.Column(db.Integer,db.ForeignKey(ChargeType.id))
#     apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
#     housecode_id = db.Column(db.Integer, db.ForeignKey(HouseCode.id))
    
#     user_id = db.Column(db.Integer, db.ForeignKey(User.id))

#     def __repr__(self):
#         charge_type_name = ChargeType.query.filter_by(id=self.charge_type_id).first()
#         charge_type = str(charge_type_name)
#         return charge_type

class Charge(db.Model):
    """db model class"""

    __tablename__ = 'charges'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    amount = db.Column(db.Float, nullable=False,default=0)
    date = db.Column(db.DateTime,default=db.func.current_timestamp())
    state = db.Column(db.String,default="initial")
    compiled = db.Column(db.Boolean,default=False)
    #foreign keys
    reading_id = db.Column(db.Integer, db.ForeignKey(MeterReading.id))
    elec_reading_id = db.Column(db.Integer, db.ForeignKey(ElectricityReading.id))

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    meter_id = db.Column(db.Integer, db.ForeignKey(Meter.id))
    charge_type_id = db.Column(db.Integer,db.ForeignKey(ChargeType.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        charge_type_name = ChargeType.query.filter_by(id=self.charge_type_id).first()
        charge_type = str(charge_type_name)
        return charge_type

class PermanentTenant(db.Model):
    """db model class"""

    __tablename__ = 'permanenttenants'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    uniquenameid = db.Column(db.String)
    name = db.Column(db.String,nullable=False)
    phone = db.Column(db.VARCHAR)
    email = db.Column(db.VARCHAR)
    national_id = db.Column(db.String)
    sms = db.Column(db.Boolean,default=True)
    balance = db.Column(db.Float,default=0)
    accumulated_fine = db.Column(db.Float,default=0)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    initial_arrears = db.Column(db.Float,default=0)

    negotiated_price = db.Column(db.Float,default=0)
    plan = db.Column(db.String)
    deposit = db.Column(db.Float,default=0)
    instalment = db.Column(db.Float,default=0)
    num_instalment = db.Column(db.Float,default=0)
    contracts_url = db.Column(db.VARCHAR)

    multiple_houses =  db.Column(db.Boolean,default=False)
    tenant_type = db.Column(db.String,default="resident")
    status = db.Column(db.String,default="Booked")
    classtype = db.Column(db.String,default="investor")

    # cleared = db.Column(db.Boolean,default=False)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    rep_id = db.Column(db.Integer, db.ForeignKey(SalesRep.id))


    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    payments = db.relationship('Payment',backref='ptenant',order_by='Payment.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    monthly_charges = db.relationship('MonthlyCharge',backref='ptenant',order_by='MonthlyCharge.id', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    mpesarecords = db.relationship('MpesaPayment',backref='ptenant',order_by='MpesaPayment.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    mpesarequests = db.relationship('MpesaRequest',backref='ptenant',order_by='MpesaRequest.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    tenantrequests = db.relationship('TenantRequest',backref='ptenant',order_by='TenantRequest.date', cascade="all, delete-orphan")
    messages = db.relationship('InternalMessages',backref='ptenant',order_by='InternalMessages.date', cascade="all, delete-orphan")
    sent_messages = db.relationship('SentMessages',backref='ptenant',order_by='SentMessages.date', cascade="all, delete-orphan")
    invoices = db.relationship('MonthlyChargeTwo',backref='tenant',cascade="all, delete-orphan")#use backref tenant to access the parent directly from child




    def __repr__(self):
        return self.name

class Tenant(db.Model):
    """db model class"""

    __tablename__ = 'tenants'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    uniquenameid = db.Column(db.String)
    name = db.Column(db.String,nullable=False)
    phone = db.Column(db.VARCHAR)
    email = db.Column(db.VARCHAR)
    national_id = db.Column(db.String)
    sms = db.Column(db.Boolean,default=True)
    balance = db.Column(db.Float,default=0)
    deposit = db.Column(db.Float,default=0)
    accumulated_fine = db.Column(db.Float,default=0)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String,default="Booked")
    residency = db.Column(db.String,default="N/A")
    initial_arrears = db.Column(db.Float,default=0)

    tenant_type = db.Column(db.String,default="tenant")

    multiple_houses =  db.Column(db.Boolean,default=False)
    # cleared = db.Column(db.Boolean,default=False)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    house_allocated = db.relationship('Occupancy',backref='tenant', cascade="all, delete-orphan")#will create allocation obj
    monthly_charges = db.relationship('MonthlyCharge',backref='tenant',order_by='MonthlyCharge.id', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    landlordsummaries = db.relationship('LandlordSummary',backref='tenant',order_by='LandlordSummary.month', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    payments = db.relationship('Payment',backref='tenant',order_by='Payment.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    submissions = db.relationship('Submission',backref='tenant',order_by='Submission.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    split_payments = db.relationship('SplitPayment',backref='tenant',order_by='SplitPayment.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    mpesarecords = db.relationship('MpesaPayment',backref='tenant',order_by='MpesaPayment.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    mpesarequests = db.relationship('MpesaRequest',backref='tenant',order_by='MpesaRequest.date', cascade="all, delete-orphan")#use backref tenant to access the parent directly from child
    tenantrequests = db.relationship('TenantRequest',backref='tenant',order_by='TenantRequest.date', cascade="all, delete-orphan")
    clearrequests = db.relationship('ClearanceRequest',backref='tenant',order_by='ClearanceRequest.date', cascade="all, delete-orphan")
    messages = db.relationship('InternalMessages',backref='tenant',order_by='InternalMessages.date', cascade="all, delete-orphan")
    sent_messages = db.relationship('SentMessages',backref='tenant',order_by='SentMessages.date', cascade="all, delete-orphan")



    def __repr__(self):
        return self.name


class TenantDeposit(db.Model):
    """db model class"""

    __tablename__ = 'tenantdeposits'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)

    rentdep = db.Column(db.Float,default=0)
    waterdep = db.Column(db.Float,default=0)
    elecdep = db.Column(db.Float,default=0)
    description = db.Column(db.String,default="unrefunded")

    total = db.Column(db.Float,default=0)

    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

    def __repr__(self):
        strhouse = str(self.id)

        return strhouse

class Occupancy(db.Model):
    """
    Relate house and tenant
    """
    __tablename__ = 'occupancy'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    description = db.Column(db.String)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    vacate_date = db.Column(db.DateTime)
    vacate_period = db.Column(db.DateTime)
    active = db.Column(db.Boolean,default=True)
    checkout_balance = db.Column(db.Float)
    cleared_by = db.Column(db.String)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        rep = Tenant.query.filter_by(id=self.tenant_id).first()
        data = rep.name
        return data

class MonthlyCharge(db.Model):
    """db model class"""

    __tablename__ = 'monthlycharges'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)

    rent = db.Column(db.Float,default=0)
    water = db.Column(db.Float,default=0)
    garbage = db.Column(db.Float,default=0)
    security = db.Column(db.Float,default=0)
    electricity = db.Column(db.Float,default=0)
    maintenance = db.Column(db.Float,default=0)
    agreement = db.Column(db.Float,default=0)
    deposit = db.Column(db.Float,default=0)
    penalty = db.Column(db.Float,default=0)

    rent_balance = db.Column(db.Float,default=0)
    water_balance  = db.Column(db.Float,default=0)
    garbage_balance  = db.Column(db.Float,default=0)
    security_balance  = db.Column(db.Float,default=0)
    electricity_balance  = db.Column(db.Float,default=0)
    maintenance_balance  = db.Column(db.Float,default=0)
    agreement_balance  = db.Column(db.Float,default=0)
    deposit_balance  = db.Column(db.Float,default=0)
    penalty_balance  = db.Column(db.Float,default=0)

    rent_paid = db.Column(db.Float,default=0)
    water_paid = db.Column(db.Float,default=0)
    garbage_paid = db.Column(db.Float,default=0)
    security_paid = db.Column(db.Float,default=0)
    electricity_paid = db.Column(db.Float,default=0)
    maintenance_paid = db.Column(db.Float,default=0)
    agreement_paid = db.Column(db.Float,default=0)
    deposit_paid = db.Column(db.Float,default=0)
    penalty_paid = db.Column(db.Float,default=0)

    rent_due = db.Column(db.Float,default=0)
    water_due  = db.Column(db.Float,default=0)
    garbage_due  = db.Column(db.Float,default=0)
    security_due  = db.Column(db.Float,default=0)
    electricity_due  = db.Column(db.Float,default=0)
    maintenance_due  = db.Column(db.Float,default=0)
    agreement_due  = db.Column(db.Float,default=0)
    deposit_due  = db.Column(db.Float,default=0)
    penalty_due  = db.Column(db.Float,default=0)
    
    arrears = db.Column(db.Float,default=0)
    total_bill = db.Column(db.Float,default=0)
    paid_amount = db.Column(db.Float,default=0)
    balance = db.Column(db.Float,default=0)

    pay_date = db.Column(db.DateTime)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    fine_status = db.Column(db.String,default="nil")
    fine_date = db.Column(db.Integer)

    sms_invoice = db.Column(db.String,default="pending")
    email_invoice = db.Column(db.String,default="pending")
    smsid = db.Column(db.VARCHAR)

    arrears_updated = db.Column(db.Boolean,default=False)
    updated = db.Column(db.Boolean,default=False)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    ptenant_id = db.Column(db.Integer, db.ForeignKey(PermanentTenant.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    createdby = db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedby= db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedon = db.Column(db.DateTime, default=db.func.current_timestamp())

    # histories = db.relationship('MonthlyChargeHistory',backref='invoice',order_by='MonthlyChargeHistory.date', cascade="all, delete-orphan")


    def __repr__(self):
        house = House.query.filter_by(id=self.house_id).first()
        strhouse = str(house)
        # return str(self.total_bill)
        return strhouse

class MonthlyChargeTwo(db.Model):
    """db model class"""

    __tablename__ = 'monthlychargestwo'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    total_amount = db.Column(db.Float, nullable=False,default=0) #expected full amount
    deposit = db.Column(db.Float,default=0)
    method = db.Column(db.String, default="partial")
    plans = db.Column(db.Integer, default=1) #number of days (7,14,30)
    plan_counter = db.Column(db.Integer, default=1) #decrement plan to zero then reset to original plan
    number_instalments = db.Column(db.Integer, default=1) #number of instalments
    remaining_number_instalments = db.Column(db.Integer, default=1) #number of remaining instalments
    payment_stage = db.Column(db.Integer, default=1) #paystage/number of instalments

    instalment = db.Column(db.Float,default=0)
    bbf = db.Column(db.Float,default=0)
    bill = db.Column(db.Float,default=0)
    paid = db.Column(db.Float,default=0)
    bcf = db.Column(db.Float,default=0)
    cpaid = db.Column(db.Float,default=0)
    cbal = db.Column(db.Float,default=0)
    sms_invoice = db.Column(db.String,default="pending")

    date = db.Column(db.DateTime,default=db.func.current_timestamp())
    pay_date = db.Column(db.DateTime,default=db.func.current_timestamp())
    state = db.Column(db.String,default="initial")

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    ptenant_id = db.Column(db.Integer,db.ForeignKey(PermanentTenant.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    rep_id = db.Column(db.Integer, db.ForeignKey(SalesRep.id))


    def __repr__(self):
        name = Tenant.query.filter_by(id=self.tenant_id).first()
        tenant = str(name)
        return tenant

# class Test(db.Model):
#     """db model class"""

#     __tablename__ = 'tests'
#     id = db.Column(db.Integer,autoincrement=True,primary_key=True)
#     rent = db.Column(db.Float,default=0)


# class MonthlyChargeHistory(db.Model):
#     """db model class"""

#     __tablename__ = 'monthlychargehistories'

#     id = db.Column(db.Integer,autoincrement=True,primary_key=True)
#     month = db.Column(db.Integer)
#     year = db.Column(db.Integer)

#     rent = db.Column(db.Float,default=0)
#     water = db.Column(db.Float,default=0)
#     garbage = db.Column(db.Float,default=0)
#     security = db.Column(db.Float,default=0)
#     electricity = db.Column(db.Float,default=0)
#     maintenance = db.Column(db.Float,default=0)
#     agreement = db.Column(db.Float,default=0)
#     deposit = db.Column(db.Float,default=0)
#     penalty = db.Column(db.Float,default=0)

#     rent_balance = db.Column(db.Float,default=0)
#     water_balance  = db.Column(db.Float,default=0)
#     garbage_balance  = db.Column(db.Float,default=0)
#     security_balance  = db.Column(db.Float,default=0)
#     electricity_balance  = db.Column(db.Float,default=0)
#     maintenance_balance  = db.Column(db.Float,default=0)
#     agreement_balance  = db.Column(db.Float,default=0)
#     deposit_balance  = db.Column(db.Float,default=0)
#     penalty_balance  = db.Column(db.Float,default=0)

#     rent_paid = db.Column(db.Float,default=0)
#     water_paid = db.Column(db.Float,default=0)
#     garbage_paid = db.Column(db.Float,default=0)
#     security_paid = db.Column(db.Float,default=0)
#     electricity_paid = db.Column(db.Float,default=0)
#     maintenance_paid = db.Column(db.Float,default=0)
#     agreement_paid = db.Column(db.Float,default=0)
#     deposit_paid = db.Column(db.Float,default=0)
#     penalty_paid = db.Column(db.Float,default=0)

#     rent_due = db.Column(db.Float,default=0)
#     water_due  = db.Column(db.Float,default=0)
#     garbage_due  = db.Column(db.Float,default=0)
#     security_due  = db.Column(db.Float,default=0)
#     electricity_due  = db.Column(db.Float,default=0)
#     maintenance_due  = db.Column(db.Float,default=0)
#     agreement_due  = db.Column(db.Float,default=0)
#     deposit_due  = db.Column(db.Float,default=0)
#     penalty_due  = db.Column(db.Float,default=0)
    
#     arrears = db.Column(db.Float,default=0)
#     total_bill = db.Column(db.Float,default=0)
#     paid_amount = db.Column(db.Float,default=0)
#     balance = db.Column(db.Float,default=0)

#     pay_date = db.Column(db.DateTime)
#     date = db.Column(db.DateTime, default=db.func.current_timestamp())
#     fine_status = db.Column(db.String,default="nil")
#     fine_date = db.Column(db.Integer)

#     sms_invoice = db.Column(db.String,default="pending")
#     email_invoice = db.Column(db.String,default="pending")
#     smsid = db.Column(db.VARCHAR)

#     arrears_updated = db.Column(db.Boolean,default=False)
#     updated = db.Column(db.Boolean,default=False)

#     apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
#     house_id = db.Column(db.Integer, db.ForeignKey(House.id))
#     tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
#     invoice_id = db.Column(db.Integer, db.ForeignKey(MonthlyCharge.id))
#     user_id = db.Column(db.Integer, db.ForeignKey(User.id))

#     createdby = db.Column(db.Integer, db.ForeignKey(User.id))
#     modifiedby= db.Column(db.Integer, db.ForeignKey(User.id))
#     modifiedon = db.Column(db.DateTime, default=db.func.current_timestamp())

#     def __repr__(self):
#         house = House.query.filter_by(id=self.house_id).first()
#         strhouse = str(house)
#         # return str(self.total_bill)
#         return strhouse

class ClientBill(db.Model):
    """db model class"""

    __tablename__ = 'clientbills'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    installation = db.Column(db.Float,default=0)
    subscription = db.Column(db.Float,default=0)
    description = db.Column(db.String,default="Secure cloud data storage,sms & monthly maintenance/updates")
    maintenance = db.Column(db.Float,default=0)
    customization = db.Column(db.Float,default=0)

    arrears = db.Column(db.Float,default=0)
    total = db.Column(db.Float,default=0)
    paid = db.Column(db.Float,default=0)
    balance = db.Column(db.Float,default=0)
    pay_date = db.Column(db.DateTime)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    sms_invoice = db.Column(db.String,default="pending")
    email_invoice = db.Column(db.String,default="pending")

    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

    def __repr__(self):
        strhouse = str(self.id)

        return strhouse

class LandlordSummary(db.Model):
    """db model class"""

    __tablename__ = 'landlordsummaries'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    water = db.Column(db.Float,default=0)
    rent = db.Column(db.Float,default=0)
    garbage = db.Column(db.Float,default=0)
    security = db.Column(db.Float,default=0)
    electricity = db.Column(db.Float,default=0)
    # maintenance = db.Column(db.Float,default=0)
    # agreement = db.Column(db.Float,default=0)
    deposit = db.Column(db.Float,default=0)
    # miscellaneous = db.Column(db.Float,default=0)
    # penalty = db.Column(db.Float,default=0)
    # fine_status = db.Column(db.String,default="nil")
    arrears = db.Column(db.Float,default=0)
    total_bill = db.Column(db.Float,default=0)
    paid_amount = db.Column(db.Float,default=0)
    balance = db.Column(db.Float,default=0)
    # pay_date = db.Column(db.DateTime)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # sms_invoice = db.Column(db.String,default="pending")
    # email_invoice = db.Column(db.String,default="pending")
    # smsid = db.Column(db.VARCHAR)

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        # house = House.query.filter_by(id=self.house_id).first()
        # house = str(house)
        return str(self.total_bill)


class Payment(db.Model):
    """db model class"""

    __tablename__ = 'payments'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    paymode = db.Column(db.String)
    # ref_number = db.Column(db.VARCHAR,unique=True)
    ref_number = db.Column(db.VARCHAR)
    receipt_num = db.Column(db.Integer)
    rand_id = db.Column(db.VARCHAR)
    description = db.Column(db.String)
    payment_name = db.Column(db.String)

    rent_paid = db.Column(db.Float,default=0)
    water_paid = db.Column(db.Float,default=0)
    garbage_paid = db.Column(db.Float,default=0)
    security_paid = db.Column(db.Float,default=0)
    electricity_paid = db.Column(db.Float,default=0)
    maintenance_paid = db.Column(db.Float,default=0)
    agreement_paid = db.Column(db.Float,default=0)
    deposit_paid = db.Column(db.Float,default=0)
    penalty_paid = db.Column(db.Float,default=0)

    charged_amount = db.Column(db.Float)
    amount = db.Column(db.Float,nullable=False)
    balance = db.Column(db.Float)

    voided = db.Column(db.Boolean,default=False)
    state = db.Column(db.String, default="Initial")
    original_amount = db.Column(db.Float)
    
    pay_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    pay_period = db.Column(db.DateTime, default=db.func.current_timestamp())
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    sms_status = db.Column(db.String,default="pending")
    email_status = db.Column(db.String,default="pending")
    smsid = db.Column(db.VARCHAR)


    chargetype_id = db.Column(db.Integer,db.ForeignKey(ChargeType.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    ptenant_id = db.Column(db.Integer, db.ForeignKey(PermanentTenant.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    createdby = db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedby= db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedon = db.Column(db.DateTime, default=db.func.current_timestamp())
    # payment_data = db.relationship('ChargePayment',backref='payment',uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        rep = self.id
        data = str(rep)
        return data

class SplitPayment(db.Model):
    """db model class"""

    __tablename__ = 'splitpayments'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    paymode = db.Column(db.String)
    # ref_number = db.Column(db.VARCHAR,unique=True)
    ref_number = db.Column(db.VARCHAR)
    rand_id = db.Column(db.VARCHAR)
    description = db.Column(db.String)
    payment_name = db.Column(db.String)
    charged_amount = db.Column(db.Float)
    amount = db.Column(db.Float,nullable=False)
    balance = db.Column(db.Float)
    voided = db.Column(db.Boolean,default=False)
    state = db.Column(db.String, default="Initial")
    original_amount = db.Column(db.Float)
    
    pay_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    pay_period = db.Column(db.DateTime, default=db.func.current_timestamp())
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    sms_status = db.Column(db.String,default="pending")
    email_status = db.Column(db.String,default="pending")
    smsid = db.Column(db.VARCHAR)


    # chargetype_id = db.Column(db.Integer,db.ForeignKey(ChargeType.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

    createdby = db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedby= db.Column(db.Integer, db.ForeignKey(User.id))
    modifiedon = db.Column(db.DateTime, default=db.func.current_timestamp())
    # payment_data = db.relationship('ChargePayment',backref='payment',uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        rep = self.id
        data = str(rep)
        return data


class LandlordRemittance(db.Model):
    """db model class"""

    __tablename__ = 'landlordremittances'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    code = db.Column(db.VARCHAR)
    landlord = db.Column(db.VARCHAR)
    ll_balbf = db.Column(db.Float,default=0.0)

    t_balbf = db.Column(db.Float,default=0.0)
    rent = db.Column(db.Float,default=0.0)
    expected = db.Column(db.Float,default=0.0)
    actual = db.Column(db.Float,default=0.0)
    t_balcf = db.Column(db.Float,default=0.0)

    commission = db.Column(db.Float,default=0.0)

    utilities = db.Column(db.Float,default=0.0)
    deposit = db.Column(db.Float,default=0.0)

    remitted = db.Column(db.Float,default=0.0)
    ratio = db.Column(db.Float,default=0.0)
    
    ll_balcf = db.Column(db.Float,default=0.0)
    agent = db.Column(db.Float,default=0.0)

    status = db.Column(db.String, default="unremitted")

    date_remitted = db.Column(db.DateTime, default=db.func.current_timestamp())
    period = db.Column(db.DateTime, default=db.func.current_timestamp())

    apartment_id = db.Column(db.Integer,db.ForeignKey(Apartment.id))
    company_id = db.Column(db.Integer,db.ForeignKey(Company.id))

    def __repr__(self):
        return str(self.id)


class ClientPayment(db.Model):
    """db model class"""

    __tablename__ = 'clientpayments'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    paymode = db.Column(db.String)
    ref_number = db.Column(db.VARCHAR)
    payment_name = db.Column(db.String)
    charged_amount = db.Column(db.Float)
    amount = db.Column(db.Float,nullable=False)
    balance = db.Column(db.Float)

    pay_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    pay_period = db.Column(db.DateTime, default=db.func.current_timestamp())
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    sms_status = db.Column(db.String,default="pending")
    email_status = db.Column(db.String,default="pending")


    company_id = db.Column(db.Integer,db.ForeignKey(Company.id))


    def __repr__(self):
        rep = self.id
        data = str(rep)
        return data

class Submission(db.Model):
    """db model for submissions"""

    __tablename__ = 'submissions'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    amount_paid = db.Column(db.Float)
    month_paid = db.Column(db.Integer)
    receipt_number = db.Column(db.VARCHAR)
    pay_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    pay_period = db.Column(db.DateTime, default=db.func.current_timestamp())

    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

# class ChargePayment(db.Model):
#     """db model class"""

#     __tablename__ = 'chargepayments'

#     id = db.Column(db.Integer,autoincrement=True,primary_key=True)
#     month = db.Column(db.Integer)
#     date = db.Column(db.DateTime, default=db.func.current_timestamp())
#     paid_amount = db.Column(db.Float)
#     water_charge = db.Column(db.Float)
#     rent_charge = db.Column(db.Float)
#     garbage_charge = db.Column(db.Float)

#     apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
#     house_id = db.Column(db.Integer, db.ForeignKey(House.id))
#     tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
#     payment_id = db.Column(db.Integer, db.ForeignKey(Payment.id))
#     user_id = db.Column(db.Integer, db.ForeignKey(User.id))

class MpesaPayment(db.Model):
    """db model class"""

    __tablename__ = 'mpesadata'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    ref_number = db.Column(db.VARCHAR)
    amount = db.Column(db.Float)
    phone = db.Column(db.VARCHAR)
    date = db.Column(db.VARCHAR)
    claimed = db.Column(db.Boolean,default=False)

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    ptenant_id = db.Column(db.Integer, db.ForeignKey(PermanentTenant.id))


class CtoB(db.Model):
    """class"""

    __tablename__ = 'ctobdata'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    trans_type = db.Column(db.VARCHAR)
    trans_id = db.Column(db.VARCHAR)
    trans_amnt = db.Column(db.Float)
    trans_time = db.Column(db.VARCHAR)
    post_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    business_shortcode = db.Column(db.VARCHAR)
    bill_ref_num = db.Column(db.VARCHAR)
    invoice_num = db.Column(db.VARCHAR)
    msisdn = db.Column(db.VARCHAR)
    fname = db.Column(db.VARCHAR)
    mname = db.Column(db.VARCHAR)
    lname = db.Column(db.VARCHAR)
    org_acc_bal = db.Column(db.Float)

    status = db.Column(db.String,default="unclaimed")
    # tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))


class BankData(db.Model):
    """class"""

    __tablename__ = 'banksdata'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    username = db.Column(db.VARCHAR)
    password = db.Column(db.VARCHAR)
    billNumber = db.Column(db.VARCHAR)
    billAmount = db.Column(db.Float)
    customerRefNumber = db.Column(db.VARCHAR)
    bankReference = db.Column(db.VARCHAR)
    transParticular = db.Column(db.VARCHAR)
    paymentMode = db.Column(db.VARCHAR)
    post_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    transDate = db.Column(db.VARCHAR)
    phoneNumber = db.Column(db.VARCHAR)
    debitAccount = db.Column(db.VARCHAR)
    debitCustName = db.Column(db.VARCHAR)
    dataType = db.Column(db.VARCHAR)


    status = db.Column(db.String,default="unclaimed")

class MpesaRequest(db.Model):
    """db model class"""

    __tablename__ = 'mpesarequestdata'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    checkoutrequestid = db.Column(db.VARCHAR)
    amount = db.Column(db.Float)
    phone = db.Column(db.VARCHAR)
    chargetype = db.Column(db.String)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    active = db.Column(db.Boolean,default=True)
    result = db.Column(db.VARCHAR)

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    ptenant_id = db.Column(db.Integer, db.ForeignKey(PermanentTenant.id))


class TenantRequest(db.Model):
    """db model class"""

    __tablename__ = 'tenantrequests'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    requesttype = db.Column(db.String)
    title = db.Column(db.String)
    cost = db.Column(db.Float,default=0.0)
    cost_estimate = db.Column(db.Float,default=0.0)
    description = db.Column(db.VARCHAR)
    status = db.Column(db.String,default="pending")
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    state = db.Column(db.Boolean,default=True)
    handled_description = db.Column(db.String,default="")

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    ptenant_id = db.Column(db.Integer, db.ForeignKey(PermanentTenant.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))

class ClearanceRequest(db.Model):
    """db model class"""

    __tablename__ = 'clearrequests'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    clear_month = db.Column(db.VARCHAR)
    description = db.Column(db.VARCHAR)
    status = db.Column(db.String,default="pending")
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    state = db.Column(db.Boolean,default=True)
    handled_description = db.Column(db.String,default="")

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))

class TransferRequest(db.Model):
    """db model class"""

    __tablename__ = 'transferrequests'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    target_house = db.Column(db.String)
    paint_costs = db.Column(db.Float,default=0.0)
    description = db.Column(db.VARCHAR)
    status = db.Column(db.String,default="pending")
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    state = db.Column(db.Boolean,default=True)
    handled_description = db.Column(db.String,default="")

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))

class InternalExpense(db.Model):
    """db model class"""

    __tablename__ = 'internalexpenses'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    expense_type = db.Column(db.String)
    name = db.Column(db.String)
    qty = db.Column(db.VARCHAR)
    house = db.Column(db.VARCHAR)
    deposit = db.Column(db.Float)
    cost = db.Column(db.Float)
    labour = db.Column(db.Float)
    amount = db.Column(db.Float)
    description = db.Column(db.VARCHAR)
    status = db.Column(db.String,default="pending")
    
    handled_description = db.Column(db.String,default="")

    # tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    # house_id = db.Column(db.Integer, db.ForeignKey(House.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __repr__(self):
        Uid = self.id
        name = self.name
        separator = " #"
        data = name + separator + str(Uid)
        return data

# class Toggle(db.Model):
#     """db"""

#     __tablename__ = 'toggledata'

#     id = db.Column(db.Integer,autoincrement=True,primary_key=True)
#     name = db.Column(db.String)

class TextMessages(db.Model):
    """class"""

    __tablename__ = 'txtmessages'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    email = db.Column(db.VARCHAR)
    txt = db.Column(db.VARCHAR)
    name = db.Column(db.VARCHAR)
    status = db.Column(db.String,default="pending")

class TextTemplate(db.Model):
    """class"""

    __tablename__ = 'texttemplates'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    txt = db.Column(db.VARCHAR)
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))

class Reminder(db.Model):
    """class"""

    __tablename__ = 'reminders'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    txt = db.Column(db.VARCHAR)
    category = db.Column(db.VARCHAR)
    status = db.Column(db.String,default="pending")

    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))

class InternalMessages(db.Model):
    """class"""

    __tablename__ = 'internalmessages'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    txt = db.Column(db.VARCHAR)
    title = db.Column(db.VARCHAR)
    status = db.Column(db.String,default="pending")

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    ptenant_id = db.Column(db.Integer, db.ForeignKey(PermanentTenant.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))

class SentMessages(db.Model):
    """class"""

    __tablename__ = 'sentmessages'

    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    text = db.Column(db.VARCHAR)
    characters = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float,default=0.0)
    status = db.Column(db.String,default="sent")

    tenant_id = db.Column(db.Integer, db.ForeignKey(Tenant.id))
    ptenant_id = db.Column(db.Integer, db.ForeignKey(PermanentTenant.id))
    apartment_id = db.Column(db.Integer, db.ForeignKey(Apartment.id))
    company_id = db.Column(db.Integer, db.ForeignKey(Company.id))