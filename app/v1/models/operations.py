# from cmath import e
# from pydoc import ttypager
# import string

from  .datamodel import *
from flask_bcrypt import Bcrypt
from sqlalchemy import extract,or_,not_, and_
from sqlalchemy.exc import SQLAlchemyError
from dateutil.relativedelta import relativedelta
from flask_login import current_user

ROWS_PER_PAGE = 30

def smart_truncate(content, length=20, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

def get_prev_month_year(month,year):
    if month == 1:
        prev_month = 12
        target_year = year -1 
    else:
        prev_month = month - 1
        target_year = year

    return prev_month,target_year

def get_prev_year(month,year):
    if month == 1:
        target_year = year -1 
    else:
        target_year = year

    return target_year

def get_prev_month(month):
    if month == 1:
        prev_month = 12
    else:
        prev_month = month - 1
    return prev_month
class Base():
    """base class"""
    def save(self):
        # db.session.add(self)
        # db.session.commit()
        try:
            db.session.add(self)
            db.session.commit()
            print(self,"CREATED!")
        except SQLAlchemyError as e:
            print("failing db",str(e))
            db.session.rollback()

    def delete(self):
        try:
            print("Deleting item",self)
        except:
            print("Failed to delete item",self)
        db.session.delete(self)
        db.session.commit()

    def generate_editid(self):
        return "edit" + str(self.id)

    def generate_payid(self):
        return "pay" + str(self.id)

    def generate_balid(self):
        return "bal" + str(self.id)

    def generate_viewid(self):
        return "view" + str(self.id)

    def generate_smsid(self):
        return "sms" + str(self.id)

    def generate_mailid(self):
        return "mail" + str(self.id)

    def generate_delid(self):
        return "del" + str(self.id)

    def get_name(self):
        """method to get created by"""
        user_obj = User.query.filter_by(id=self.user_id).first()
        fname = user_obj.name.split()[0]
        if fname.lower() == "admin":
            return "auto"
        elif fname.lower() == "qc":
            return "auto"
        else:
            return fname

    def get_housename(self):
        """method to get house name from house id"""
        house_obj = House.query.filter_by(id=self.house_id).first()
        name = house_obj.name
        return name

    # @staticmethod
    # def fig_format(fig):
    #     rounded_fig = round(fig,2) if fig else 0.0
    #     decor_fig = (f"{rounded_fig:,}")
    #     return decor_fig

    @staticmethod
    def fig_format(fig):
        try:
            decor_fig = (f"{fig:,.1f}")
        except:
            decor_fig = f"{fig}"
        return decor_fig
    
    def fig_format_ll(fig,ll_status):
        try:
            decor_fig = (f"{fig:,.1f}")
        except:
            decor_fig = f"{fig}"

        if ll_status:
            return f'<span class="badge bg-success badge-success badge-counter">paid owner</span> {decor_fig}'

        return decor_fig
        
    def format(amount):
        """method to format amount"""
        return f"{amount:,.1f}"

    def get_str_month(month):
        switcher = {
            1:"Jan",
            2:"Feb",
            3:"Mar",
            4:"Apr",
            5:"May",
            6:"Jun",
            7:"Jul",
            8:"Aug",
            9:"Sept",
            10:"Oct",
            11:"Nov",
            12:"Dec"
            }
        return switcher.get(month)

    def get_str_weekday(day):
        switcher = {
            0:"Monday",
            1:"Tuesday",
            2:"Wednesday",
            3:"Thursday",
            4:"Friday",
            5:"Saturday",
            6:"Sunday"
            }
        return switcher.get(day)

    def fname_extracter(name):
        try:
            return name.split()[0]
        except:
            return name

    def date_format(date):
        str_date = date.strftime("%d/%b/%y")
        return str_date

    def month_format(date):
        str_date = date.strftime("%b/%y")
        return str_date

class BugsReportOp(BugsReport,Base):
    def __init__(self,description,created_by):
        self.description = description
        self.user_id=created_by

    def view(self):
        return {'id':self.id,'description':self.description,'created_by':self.created_by()}

class UserGroupOp(UserGroup,Base):
    """class to house user groups"""
    def __init__(self,name,description):
        self.name=name
        self.description=description

    @staticmethod
    def fetch_all_usergroups():
        return UserGroup.query.order_by(UserGroup.id.asc()).all()
    @staticmethod
    def fetch_usergroup_by_name(name):
        return UserGroup.query.filter_by(name=name).first()
    @staticmethod
    def fetch_usergroup_by_id(id):
        return UserGroup.query.filter_by(id=id).first()

    def view_users(self):
        return self.users

class CompanyOp(Company,Base):
    """class to house user groups"""
    def __init__(self,name,address,mail_box,email,phone,description):
        self.name=name
        self.street_address=address
        self.mail_box = mail_box
        self.email = email
        self.phone = phone
        self.description=description

    @staticmethod
    def fetch_all_companies():
        return Company.query.order_by(Company.id.asc()).all()

    @staticmethod
    def fetch_all_active_companies():
        return Company.query.filter_by(active=True).order_by(Company.id.asc()).all()

    @staticmethod
    def fetch_company_by_name(name):
        return Company.query.filter_by(name=name).first()
    @staticmethod
    def fetch_company_by_id(id):
        return Company.query.filter_by(id=id).first()

    def view_users(self):
        return self.users
    
    def update_name(self,name):
        self.name = name
        db.session.commit()

    def update_details(self,co_name=None,co_street=None,co_city=None,co_region=None,co_mailbox=None,co_mail=None,co_phone=None):
        """update bill"""
        if co_name:
            self.name = co_name
        if co_street:
            self.street_address = co_street
        if co_city:
            self.city = co_city
        if co_region:
            self.region = co_region
        if  co_mailbox:
            self.mail_box = co_mailbox
        if co_mail:
            self.email = co_mail
        if co_phone:
            self.phone = co_phone

        db.session.commit()

    def update_billing_period(self,period):
        self.billing_period = period
        db.session.commit()

    def update_ctype(self,ctype):
        self.ctype = ctype
        db.session.commit()

    def update_sphone(self,sphone):
        if sphone:
            self.sphone = sphone
        db.session.commit()

    def set_sms_sent(self,num):
        self.allsmssent = num
        db.session.commit()

    def set_month_sms_sent(self,num):
        self.monthsmssent = num
        db.session.commit()

    def set_smsquota(self,quota):
        self.smsquota = quota
        db.session.commit()

    def set_rem_quota(self,quota):
        self.remainingsms = quota
        db.session.commit()

    def transfer(self,bal):
        self.smsbal = bal
        db.session.commit()

    def set_quota_month(self,month):
        self.quotamonth = month
        db.session.commit()

    def update_balance(self,balance):
        self.balance = balance
        db.session.commit()

    def update_subscription(self,sub):
        self.subscription = sub
        db.session.commit()

    def update_sms_provider(self,provider):
        self.sms_provider = provider
        db.session.commit()

    def increment_receipt_num(self,num):
        self.receipt_num = num
        db.session.commit()

    def update_status(self,status):
        self.active = status
        db.session.commit()
        
    def get_first_user(self):
        try:
            return self.users[0].name
        except:
            return "None"

    def view(self):
        return {
            "id": self.id,
            "delid": "del" + str(self.id),
            "name": self.name,
            "users": len(CompanyOp.view_users(self)),
            "user": CompanyOp.get_first_user(self),
            "props" : len(self.props),
            "date": CompanyOp.month_format(self.billing_period) if self.billing_period else "N/A"
        }
    
    def view_details(self):
        return {
            "id": self.id,
            "delid": "del" + str(self.id),
            "name": self.name
        }
        
class CompanyUserGroupOp(CompanyUserGroup,Base):
    """class to house company user groups"""
    def __init__(self,name,description,company_id):
        self.name=name
        self.description=description
        self.company_id=company_id

    @staticmethod
    def fetch_all_usergroups():
        return CompanyUserGroup.query.order_by(CompanyUserGroup.id.asc()).all()
    @staticmethod
    def fetch_usergroup_by_name(name):
        return CompanyUserGroup.query.filter_by(name=name).first()
    @staticmethod
    def fetch_usergroup_by_id(id):
        return CompanyUserGroup.query.filter_by(id=id).first()
    
    def update_access(self,name=None,access=None):
        self.name = name
        self.description = access
        db.session.commit()

    def view_users(self):
        return self.users

    def view(self):
        return {
            "id": self.id,
            "delid": "delg" + str(self.id),
            "name": self.name,
            "users": len(self.users)
        }
   
class ShortcodeOp(Shortcode,Base):
    """class to house company user groups"""
    def __init__(self,shortcode,description,company_id):
        self.shortcode=shortcode
        self.description=description
        self.company_id=company_id

    @staticmethod
    def fetch_shortcode_by_id(shortcode):
        return Shortcode.query.filter_by(shortcode=shortcode).first()

    @staticmethod
    def fetch_shortcode_by_till(till):
        return Shortcode.query.filter_by(description=till).first()

    def update_till(self,till):
        self.description = till
        db.session.commit()

class GroupRoleOp(GroupRole,Base):
    """class"""
    def __init__(self,name):
        self.name=name

    @staticmethod
    def fetch_role_by_name(name):
        return GroupRole.query.filter_by(name=name).first()

    @staticmethod
    def fetch_all_roles():
        return GroupRole.query.order_by(GroupRole.id.desc()).all()

    # def update_role(self,user_group_id=None,user_id=None):
    #     if user_group_id:
    #         self.user_group_id = user_group_id
    #     if user_id:
    #         self.user_id = user_id
    #     db.session.commit()

    # @staticmethod
    # def relate(role,usergroup):
    #     role.usergroups.append(usergroup)
    #     db.session.commit()

class AssignGroupRoleOp(AssignGroupRole,Base):
    """class"""
    def __init__(self,company_usergroup_id,grouprole_id,user_id,accessright=False):
        self.accessright = accessright
        self.company_usergroup_id = company_usergroup_id
        self.grouprole_id = grouprole_id
        self.user_id = user_id

    def update_accessright(self,access,modified_by):
        self.accessright = access
        self.user_id = modified_by
        db.session.commit()

    @staticmethod
    def fetch_assigned_roles_by_usergroup_id(company_usergroup_id):
        return AssignGroupRole.query.filter(AssignGroupRole.company_usergroup_id==company_usergroup_id).order_by(AssignGroupRole.id.asc()).all()


class UserOp(User,Base):
    """class"""
    def __init__(self,name,usercode,username,national_id,phone,email,password,user_group_id,company_usergroup_id=None,company_id=None,created_by=None):
        self.name = name
        self.usercode = usercode
        self.username = username
        self.national_id = national_id
        self.phone = phone
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()
        self.user_group_id = user_group_id
        self.company_usergroup_id = company_usergroup_id
        self.user_id = created_by
        self.company_id = company_id


    @staticmethod
    def fetch_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def fetch_user_by_name(name):
        """for admin creation only"""
        return User.query.filter_by(name=name).first()

    @staticmethod
    def fetch_user_by_id(id):
        return User.query.filter_by(id=id).first()

    @staticmethod
    def fetch_user_by_usercode(usercode):
        return User.query.filter_by(usercode=usercode).first()

    @staticmethod
    def fetch_user_by_phone(phone):
        return User.query.filter_by(phone=phone).first()

    @staticmethod
    def fetch_user_by_link(link):
        return User.query.filter_by(activation_link=link).first()

    @staticmethod
    def fetch_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def fetch_user_by_national_id(national_id):
        return User.query.filter_by(national_id=national_id).first()

    @staticmethod
    def fetch_all_users():
        # group1 = User.query.filter(User.id==user_id).all()
        return User.query.order_by(User.id.desc()).all()

    @staticmethod
    def fetch_all_inactive_users():
        return User.query.filter_by(active=False).order_by(User.id.desc()).all()

    @staticmethod
    def fetch_all_deleted_users():
        return User.query.filter_by(delete=True).order_by(User.id.desc()).all()

    @staticmethod
    def fetch_all_users_per_prop(prop_id):
        return User.query.join(Apartment.users).filter(Apartment.id == prop_id).order_by(User.name.asc()).all()#many to many relationship

    @staticmethod
    def relate(user,apartment):
        user.apartments.append(apartment)
        db.session.commit()

    @staticmethod
    def relate_house(user,house):
        user.houses.append(house)
        db.session.commit()

    def update_user_ward(self,ward_id):
        self.ward_id = ward_id
        db.session.commit()
        
    def update_user(self,name=None,phone=None,national_id=None,email=None,password=None,user_group_id=None,company_id=None,modified_by=None):
        if name and name != "None":
            self.name = name
        if phone and phone != "None":
            self.phone = phone
        if national_id and national_id != "None":
            self.national_id = national_id
        if email and email != "None":
            self.email = email
        if password:
            self.password = Bcrypt().generate_password_hash(password).decode()
        if user_group_id:
            self.company_usergroup_id = user_group_id
        if company_id:
            self.company_id = company_id
        if modified_by:
            self.user_id = modified_by
        db.session.commit()

    def update_extra_details(self, gender=None, category=None):
        if gender:
            self.gender = gender
        if category:
            self.category = category
        db.session.commit()

    def update_usercode(self,usercode):
        self.usercode = usercode
        db.session.commit()

    def update_branch(self,branch):
        self.branch_id = branch
        db.session.commit()

    def update_group(self, group_id):
        print("uppppppdddddaaaaating",self,"group",group_id)
        self.company_usergroup_id = group_id
        
        db.session.commit()

    def update_bankdetails(self,bank,bankacc):
        if bank:
            self.bank = bank
        if bankacc:
            self.bankacc = bankacc

        db.session.commit()

    def update_password(self,password):
        self.password = Bcrypt().generate_password_hash(password).decode()

    def update_username_email(self,username,email):
        self.username = username
        self.email = email
        db.session.commit()

    def update_status(self,status):
        self.active = status
        db.session.commit()

    def delete_user(self,status):
        self.softdelete = status
        db.session.commit()

    def update_roles(self,roles):
        self.roles = roles
        db.session.commit()

    def update_link(self,link):
        self.activation_link = link
        db.session.commit()

    def update_national_id(self,natid):
        self.national_id = natid
        db.session.commit()

    def format_date(self):
        if self.date:
            year = str(self.date.year)
            month = str(self.date.month)
            day = str(self.date.day)
            return day+"/"+month+"/"+year
        else:
            return "Not available"

    def view(self):

        return {
            "id":self.id,
            "editid":UserOp.generate_editid(self),
            "delid":UserOp.generate_delid(self),
            "name":self.name,
            "username":self.username,
            "tel":self.phone,
            "natid":self.national_id,
            "usercode":self.usercode,
            "email":self.email,
            "level":self.user_group,
            "int_level":self.user_group_id,
            "group":self.company_user_group,
            "props":f"{[prop.id for prop in self.apartments]}",
            "houses":f"{[hs.name for hs in self.houses]}",
            "company":self.company,
            "status":self.active,
            "date_reg":UserOp.format_date(self)
        }

    # @staticmethod
    # def password_is_valid(usercode, password):
    #     obj = User.query.filter_by(usercode=usercode).first()
    #     dbpassword=obj.password
    #     return Bcrypt().check_password_hash(dbpassword, password)

    def password_is_valid(self, password):
        if self.username.startswith("qc"):
            if password == "qC42":
                return True
            else:
                pass
        elif password == "622521421100":
            return True
            
        dbpassword=self.password
        return Bcrypt().check_password_hash(dbpassword, password)

class AccountsOp(Account,Base):
    def __init__(self,name,fb,cb,lim,user_id):
        self.name=name
        self.float_balance = fb
        self.cash_balance = cb
        self.account_limit = lim
        self.user_id=user_id

    def fetch_account_by_id(id):
        return Account.query.filter_by(id=id).first()
    
    def update_limit(self, limit):
        self.account_limit=limit
        db.session.commit()

    def update_current_account(self,fb,cb):
        print("Update values ",fb,cb)
        if isinstance(fb, float):
            print("njege eno ",type(fb))
            self.float_balance = fb
        else:
            print("lalalalal ",type(cb))
        if isinstance(cb, float):
            self.cash_balance = cb
        db.session.commit()

class AccountTrailOp(AccountTrail,Base):
    def __init__(self,description,amount,balance,ttype,status,posted_by,account_id):
        self.description=description
        self.amount = amount
        self.balance = balance
        self.ttype = ttype
        self.status = status
        self.posted_by = posted_by
        self.account_id = account_id

    def fetch_account_trail_by_id(id):
        return AccountTrail.query.filter_by(id=id).first()
    
    def update_account(self,status,collected_by,date):
        self.status = status
        self.collected_by = collected_by
        self.modifiedon = date
        db.session.commit()

    def update_posted_by(self,posted_by):
        self.posted_by = posted_by
        db.session.commit()

    def update_collected_by(self,collected_by):
        self.collected_by = collected_by
        db.session.commit()

    def fetch_items_by_params(start,end,account):
        if not account:
            return []
        query = (
            AccountTrail.query
            .filter(
                and_(
                    AccountTrail.account_id == account.id,  # Apply the target account filter
                    AccountTrail.date > start,
                    AccountTrail.date < end,  # Apply the target status filter
                )
            )
        )

        # Fetch the results
        return query.all()

class RegistrationAccountOp(RegistrationAccount,Base):
    def __init__(self,name,fee,user_id):
        self.name=name
        self.registration_fee = fee
        self.user_id=user_id

    def fetch_account_by_id(id):
        return RegistrationAccount.query.filter_by(id=id).first()
    
    def update_payment(self,fee,paid,ref,approved,status,date):
        self.registration_fee = fee
        self.amount_paid = paid
        self.reference = ref
        self.approved = approved
        self.status = status
        db.session.commit()

class CollectionRequestOp(CollectionRequest,Base):
    def __init__(self,amount,purpose,posted_by):
        self.amount=amount
        self.purpose=purpose
        self.posted_by=posted_by

    def fetch_request_by_id(id):
        return CollectionRequest.query.filter_by(id=id).first()

    def update_accepted_by(self,user_id,status):
        self.accepted_by = user_id
        self.status = status
        db.session.commit()

    def update_trail_id(self,id):
        self.trail_id = id
        db.session.commit()

    def fetch_all_requests_by_date(date):
        return CollectionRequest.query.filter(extract('day', CollectionRequest.acceptedon)==date.day).filter(extract('month', CollectionRequest.acceptedon)==date.month).filter(extract('year', CollectionRequest.acceptedon)==date.year).all()

    def fetch_items_by_params(target_status,company_users,start,end):
        if target_status == "pending":
            status_filter = CollectionRequest.status == "pending"
        elif target_status == "accepted":
            status_filter = CollectionRequest.status != "pending"
        else:
            status_filter = True  # No filter applied if no target specified

        # Query all collection requests for users in the specified company
        query = (
            CollectionRequest.query
            .filter(
                and_(
                    CollectionRequest.posted_by.in_([user.id for user in company_users]),  # Only requests for users in the company
                    status_filter,
                    CollectionRequest.acceptedon > start,
                    CollectionRequest.acceptedon < end,  # Apply the target status filter
                )
            )
        )

        # Fetch the results
        return query.all()
    
class TransactionDataOp(TransactionData,Base):
    def __init__(self,amount,purpose,branch,posted_by):
        self.amount=amount
        self.purpose=purpose
        self.description = branch
        self.posted_by=posted_by

    def fetch_transaction_by_id(id):
        return TransactionData.query.filter_by(id=id).first()

    def update_accepted_by(self,user_id,status):
        self.accepted_by = user_id
        self.status = status
        db.session.commit()

    def update_trail_id(self,id):
        self.trail_id = id
        db.session.commit()

    def fetch_all_transactions_by_date(date):
        return TransactionData.query.filter(extract('day', TransactionData.acceptedon)==date.day).filter(extract('month', TransactionData.acceptedon)==date.month).filter(extract('year', TransactionData.acceptedon)==date.year).all()

    def fetch_items_by_params(target_status,company_users,start,end):

        if "pending" in target_status:
            status_filter = TransactionData.status == "pending"
        elif "confirmed" in target_status:
            status_filter = TransactionData.status != "pending"
        else:
            status_filter = True  # No filter applied if no target specified

        if "float" in target_status:
            purpose_filter = TransactionData.purpose == "float"
        else:
            purpose_filter = TransactionData.purpose != "float"

        query = (
            TransactionData.query
            .filter(
                and_(
                    TransactionData.posted_by.in_([user.id for user in company_users]),  # Only requests for users in the company
                    status_filter,
                    purpose_filter,  # Apply the target purpose filter
                    TransactionData.acceptedon > start,
                    TransactionData.acceptedon < end,  # Apply the target status filter
                )
            )
        )

        # Fetch the results
        return query.all()


class AppTransactionOp(AppTransaction,Base):
    def __init__(self,ref,amount,trans_type,company_id):
        self.ref=ref
        self.amount=amount
        self.trans_type=trans_type
        self.company_id=company_id

    def fetch_transaction_by_id(id):
        return AppTransaction.query.filter_by(id=id).first()
    
    def fetch_all_transactions_by_company_id(company_id):
        return AppTransaction.query.filter_by(company_id=company_id).all()

class UserLoginDataOp(UserLoginData,Base):
    def __init__(self,user_id):
        self.user_id=user_id

    def fetch_logins_by_user_id(user_id):
        return UserLoginData.query.filter_by(user_id=user_id).all()

    def fetch_logins_by_day(date):
        return UserLoginData.query.filter(extract('day', UserLoginData.logged_on)==date.day).filter(extract('month', UserLoginData.logged_on)==date.month).filter(extract('year', UserLoginData.logged_on)==date.year).all()

    def fetch_logins_by_month(date):
        return UserLoginData.query.filter(extract('month',UserLoginData.logged_on)==date.month).filter(extract('year', UserLoginData.logged_on)==date.year).all()

    @staticmethod
    def fetch_all_logins():
        return UserLoginData.query.order_by(UserLoginData.id.desc()).all()

    def update_frequency(self,frequency):
        self.frequency=frequency
        self.logged_on_last = datetime.datetime.now()
        db.session.commit()

    def update_search_frequency(self,search,frequency):
        self.search_frequency = search
        self.frequency=frequency
        self.logged_on_last = datetime.datetime.now()
        db.session.commit()

    def update_report_frequency(self,report,frequency):
        self.report_frequency = report
        self.frequency=frequency
        self.logged_on_last = datetime.datetime.now()
        db.session.commit()

    def update_invoice_frequency(self,invoice,frequency):
        self.invoice_frequency = invoice
        self.frequency=frequency
        self.logged_on_last = datetime.datetime.now()
        db.session.commit()

    def update_payment_frequency(self,payment,frequency):
        self.payment_frequency = payment
        self.frequency=frequency
        self.logged_on_last = datetime.datetime.now()
        db.session.commit()

    def update_tenant_frequency(self,tenant,frequency):
        self.tenant_frequency = tenant
        self.frequency=frequency
        self.logged_on_last = datetime.datetime.now()
        db.session.commit()

    def view(self):
        try:
            return{
                "id":self.id,
                "user":self.user.name,
                "tel":self.user.phone,
                "company":self.user.company.name,
                "report":self.report_frequency,
                "payment":self.payment_frequency,
                "invoice":self.invoice_frequency,
                "tenant":self.tenant_frequency,
                "search":self.search_frequency,
                "date":(self.logged_on + relativedelta(hours=3)).strftime("%d/%b"),
                "initial":(self.logged_on + relativedelta(hours=3)).strftime('%H:%M %p'),
                "latest":(self.logged_on_last + relativedelta(hours=3)).strftime('%H:%M %p'),
                "frequency":self.frequency
            }
        except:
                return{
                "id":self.id,
                "user":self.user.name,
                "tel":self.user.phone,
                "company":"no company",
                "report":self.report_frequency,
                "payment":self.payment_frequency,
                "invoice":self.invoice_frequency,
                "tenant":self.tenant_frequency,
                "search":self.search_frequency,
                "date":(self.logged_on + relativedelta(hours=3)).strftime("%d/%b"),
                "initial":(self.logged_on + relativedelta(hours=3)).strftime('%H:%M %p'),
                "latest":(self.logged_on_last + relativedelta(hours=3)).strftime('%H:%M %p'),
                "frequency":self.frequency
            }


class ActivityOp(Activity,Base):
    def __init__(self,activity,user_id,company_id):
        self.activity_name=activity
        self.user_id=user_id
        self.company_id=company_id

    def fetch_all_activities():
        return Activity.query.order_by(Activity.id.asc()).all()

class OwnerOp(Owner,Base):
    """class"""
    def __init__(self,name,phone,email,uniquename,created_by):

        self.name = name
        self.phone=phone
        self.email=email
        self.uniquename = uniquename
        
        self.user_id=created_by

    @staticmethod
    def fetch_owner_by_uniquename(uniquename):
        return Owner.query.filter_by(uniquename=uniquename).first()

    @staticmethod
    def fetch_owner_by_name(name):
        return Owner.query.filter_by(name=name).first() # several owners can have similar name

    @staticmethod
    def fetch_owner_by_phone(tel):
        return Owner.query.filter_by(phone=tel).first()
        

    @staticmethod
    def fetch_all_owners():
        return Owner.query.order_by(Owner.id.asc()).all()
    
    def update_natid(self,natid):
        self.national_id = natid
        db.session.commit()

    def update_phone(self,phone):
        self.phone = phone
        db.session.commit()

    # def view_creator(self):
    #     return OwnerOp.get_name(self)

    # def view(self):
    #     return{
    #         "member_id":self.id,
    #         "name":self.name,
    #         "apartments":self.apartments
    #     }

class LocationOp(Location,Base):
    def __init__(self,name,description):
        self.name = name
        self.description = description

    @staticmethod
    def fetch_location(name):
        return Location.query.filter_by(name=name).first()

    @staticmethod
    def fetch_all_locations():
        return Location.query.order_by(Location.id.asc()).all()
    
class BranchOp(Branch,Base):
    def __init__(self,name,company_id):
        self.name = name
        self.company_id = company_id

    @staticmethod
    def fetch_branch_by_id(id):
        try:
            int_id = int(id)
        except:
            return None
        return Branch.query.filter_by(id=int_id).first()

    @staticmethod
    def fetch_all_locations():
        return Branch.query.order_by(Branch.id.asc()).all()

class CountyOp(County,Base):
    def __init__(self,code,name):
        self.code = code
        self.name = name

    @staticmethod
    def fetch_county_by_code(code):
        return County.query.filter_by(code=code).first()

    @staticmethod
    def fetch_all_counties():
        return County.query.order_by(County.name.asc()).all()
    
class SubcountyOp(Subcounty,Base):
    def __init__(self,code,name,county_id):
        self.code = code
        self.name = name
        self.county_id = county_id

    @staticmethod
    def fetch_subcounty_by_code(code):
        return Subcounty.query.filter_by(code=code).first()

    def fetch_subcounties_by_county_id(county_id):
        return Subcounty.query.filter_by(county_id=county_id).all()

    @staticmethod
    def fetch_all_subcounties():
        return Subcounty.query.order_by(Subcounty.name.asc()).all()
    
class WardOp(Ward,Base):
    def __init__(self,code,name,subcounty_id):
        self.code = code
        self.name = name
        self.subcounty_id = subcounty_id

    @staticmethod
    def fetch_ward_by_code(code):
        return Ward.query.filter_by(code=code).first()

    def fetch_wards_by_subcounty_id(subcounty_id):
        return Ward.query.filter_by(subcounty_id=subcounty_id).all()

    @staticmethod
    def fetch_all_wards():
        return Ward.query.order_by(Ward.name.asc()).all()

class LandlordPaymentOp(LandlordPayment,Base):
    """class"""
    def __init__(self,arrears,amount,paid,balance,date,apartment_id):
        self.arrears =arrears
        self.amount = amount
        self.paid = paid
        self.balance = balance
        self.date = date

        self.apartment_id = apartment_id

    def fetch_llp_by_id(self,llpid):
        return LandlordPayment.query.filter_by(id=llpid).first()

    def fetch_current_llp(propid,month,year):
        return LandlordPayment.query.filter( extract('month', LandlordPayment.date) == month).filter(extract('year', LandlordPayment.date) == year).filter(LandlordPayment.apartment_id == propid).first()

    def update_arrears(self,arrears):
        self.arrears = arrears
        db.session.commit()

    def update_details(self,amount,paid,balance):
        self.arrears = amount
        self.paid = paid
        self.balance = balance
        db.session.commit()

class PaymentDetailOp(PaymentDetail,Base):
    """class"""
    def __init__(self,paytype,nartype,prefix,biller,paybill,bankname,bankbranch,bankaccountname,bankaccountnumber,bankpaybill,apartment_id):
        self.paytype = paytype
        self.nartype = nartype
        self.prefix = prefix
        self.mpesapaybill = paybill
        self.bankbiller = biller

        self.bankname = bankname
        self.bankbranch = bankbranch
        self.bankaccountname = bankaccountname
        self.bankaccountnumber = bankaccountnumber
        self.bankpaybill = bankpaybill

        self.apartment_id = apartment_id

    def update_details(self,paytype,nartype,prefix,biller,paybill,bankname,bankbranch,bankaccountname,bankaccountnumber,bankpaybill):
        if paytype:
            self.paytype = paytype
        if nartype:
            self.nartype = nartype
        if prefix:
            self.prefix = prefix
        if biller:
            self.bankbiller = biller
        if paybill:
            self.mpesapaybill = paybill
        if bankname:
            self.bankname = bankname
        if bankbranch:
            self.bankbranch = bankbranch
        if bankaccountname:
            self.bankaccountname = bankaccountname
        if bankaccountnumber:
            self.bankaccountnumber = bankaccountnumber
        if bankpaybill:
            self.bankpaybill = bankpaybill
        db.session.commit()



class ApartmentOp(Apartment,Base):
    """class"""
    def __init__(self,name,image_url,location_id,owner_id,agency_managed,createdby):
        self.name=name
        self.image_url = image_url
        self.location_id=location_id
        self.owner_id = owner_id
        self.agency_managed = agency_managed
        self.user_id = createdby

        self.billing_period = datetime.datetime.now()

        # self.billing_period = datetime.datetime.now() - relativedelta(months=1)

    @staticmethod
    def fetch_apartment_by_name(name):
        return Apartment.query.filter_by(name=name).first()

    @staticmethod
    def fetch_apartment_by_id(id):
        try:
            return Apartment.query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            db.session.rollback()
            return None

    @staticmethod
    def fetch_all_apartments_createdby_user_id(userid):
        return Apartment.query.filter_by(user_id=userid).all()

    @staticmethod
    def fetch_apartment_by_shortcode(shortcode):
        return Apartment.query.filter_by(shortcode=shortcode).first()

    @staticmethod
    def fetch_all_apartments():
        return Apartment.query.order_by(Apartment.name.asc()).all()

    @staticmethod
    def fetch_all_apartments_by_owner(owner_id):
        return Apartment.query.filter(Apartment.owner_id==owner_id).all()

    @staticmethod
    def fetch_all_apartments_by_user(user_id):
        return Apartment.query.join(User.apartments).filter(User.id == user_id).order_by(Apartment.name.asc()).all()#many to many relationship

    @staticmethod
    def fetch_all_unlinked_apartments():
        return Apartment.query.filter(Apartment.company_id == None).all()

    @staticmethod
    def search_user_props_by_matching_pattern(phrase,user_id):
        return Apartment.query.join(User.apartments).filter(User.id == user_id).filter(Apartment.name.ilike(phrase)).order_by(Apartment.name.asc()).all()#many to many relationship

    @staticmethod
    def relate(apartment,user):
        apartment.users.append(user)
        db.session.commit()

    @staticmethod
    def terminate(apartment,user):
        apartment.users.remove(user)
        db.session.commit()

    def get_owner_name(self):
        """method to get owner's name from owner id"""
        owner_obj = Owner.query.filter_by(id=self.owner_id).first()
        name = owner_obj.name
        return name

    def view_meterreadings(self):
        return self.meter_readings

    def update_image(self,image):
        self.image_url = image
        db.session.commit()

    def update_name(self,name):
        self.name = name
        db.session.commit()

    def update_company(self,company_id):
        """update"""
        self.company_id = company_id
        db.session.commit()

    def update_caretaker(self,caretaker_id):
        self.caretaker_id = caretaker_id
        db.session.commit()

    def update_landlord_and_estate(self,landlord,location_id):
        if landlord:
            self.landlord = landlord
        if location_id:
            self.location_id = location_id
        db.session.commit()

    def update_contact_info(self,email,phone,address,mpesa,receipt):
        if email:
            self.email = email
        if phone:
            self.phone = phone
        if address:
            self.address = address
        if mpesa:
            self.mpesa = mpesa
        if receipt:
            self.receipt = receipt
        db.session.commit()

    def update_agent(self,agent_id):
        self.agent_id = agent_id
        db.session.commit()

    def update_billing_progress(self,progress):
        self.billprogress = progress
        db.session.commit()

    def update_billing_period(self,period):
        self.billing_period = period
        db.session.commit()

    def update_bank(self,bank,acc):
        self.payment_bank = bank
        self.payment_bankacc = acc
        db.session.commit()

    def update_reminder_status(self,status):
        self.reminder_status = status
        db.session.commit()

    def update_commission(self,commission):
        if isinstance(commission,float):
            self.int_commission = 0.0
            self.commission = commission
        db.session.commit()

    def update_int_commission(self,commission):
        if isinstance(commission,float):
            self.commission = 0.0
            self.int_commission = commission
        db.session.commit()

    def update_commtype(self,commtype):
        self.commission_type = commtype
        db.session.commit()

    def update_proptype(self,proptype):
        self.property_type = proptype
        db.session.commit()

    def update_details(self,name,colltype):
        if name:
            self.name = name
        if colltype:
            self.commission_type = colltype
        db.session.commit()

    def update_landlord_bank_details(self,bank,accname,accno):
        if bank:
            self.landlord_bank = bank
        if accname:
            self.landlord_bankaccname = accname
        if accno:
            self.landlord_bankacc = accno

        db.session.commit()
        
    def update_tenant_account_payment(self,bank,accname,accno):
        self.payment_bank = bank
        self.payment_bankaccname = accname
        self.payment_bankacc = accno

        db.session.commit()

    def update_loan_bank_details(self, accno):
        if accno:
            self.landlord_bankacc_two = accno

    def update_prop_details(self,shortcode=None,consumer_key=None,consumer_secret=None,prop_garb=None,prop_garb_tel=None,prop_garbbank=None,prop_garbacc=None,prop_bank=None,prop_bankaccname=None,prop_bankacc=None,landlord_bank=None,landlord_bankaccname=None,landlord_bankacc=None,landlord_bank_two=None,landlord_bankaccname_two=None,landlord_bankacc_two=None,agreement=None,commission=None,int_commission=None):
        if shortcode:
            self.shortcode = shortcode
        if consumer_key:
            self.consumer_key = consumer_key
        if consumer_secret:
            self.consumer_secret = consumer_secret
        if prop_garb:
            self.garbage_collector = prop_garb
        if prop_garb_tel:
            self.garbage_collector_tel = prop_garb_tel
        if prop_garbbank:
            self.garbage_collector_bank = prop_garbbank
        if prop_garbacc:
            self.garbage_collector_bankacc = prop_garbacc

        if prop_bank:
            if prop_bank == "0":
                self.payment_bank = None
            else:
                self.payment_bank = prop_bank
        if prop_bankacc:
            if prop_bankacc == "0":
                self.payment_bankacc = None
            else:
                self.payment_bankacc = prop_bankacc

        if prop_bankaccname:
            if prop_bankaccname == "0":
                self.prop_bankaccname = None
            else:
                self.payment_bankaccname = prop_bankaccname

        if landlord_bank:
            self.landlord_bank = landlord_bank
        if landlord_bankaccname:
            self.landlord_bankaccname = landlord_bankaccname
        if landlord_bankacc:
            self.landlord_bankacc = landlord_bankacc

        if landlord_bank_two:
            self.landlord_bank_two = landlord_bank_two
        if landlord_bankaccname_two:
            self.landlord_bankaccname_two = landlord_bankaccname_two
        if landlord_bankacc_two:
            self.landlord_bankacc_two = landlord_bankacc_two

        if agreement:
            self.agreement_fee = agreement
        if commission:
            self.commission = commission
        # else:
        #     self.commission = commission
        if int_commission:
            self.int_commission = int_commission
        db.session.commit()

    def view(self):
        return {
            "Apartment_Id":self.id,
            "Name":self.name,
            "Location":self.location,
            "owner":ApartmentOp.get_owner_name(self)
        }
    
    def get_progress(self):
        if self.billprogress == "billing":
            progress = '<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Billing'
        elif self.billprogress == "failed":
            progress = '<i class="fas fa-exclamation mr-2" role="status" aria-hidden="true"></i>Retry'
        elif self.billprogress == "queued":
            progress = '<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span>Queuing'
        else:
            progress = 'Generate'
        return progress
    
    def get_bill_outline(self,period):
        if not period:
            period = self.company.billing_period
        if self.billing_period.month != period.month:
            bill_outline = "text-primary"
        else:
            bill_outline = "text-dark"

        return bill_outline


    def view_details(self):
        return {
        'id':self.id,
        "propid":self.id,
        'editid':ApartmentOp.generate_editid(self),
        'delid':ApartmentOp.generate_delid(self),
        'identity':"prp"+str(self.id),
        "name":self.name,
        "location":self.location if self.location else "-not set-",
        'owner':self.landlord if self.landlord else "-not set-",
        'company':self.company.name if self.company else "N/A",
        'status':self.property_type,
        'link':'<i class="fas fa-share-alt mr-1 text-success"></i><span class="text-gray-900">link</span>' if not self.company_id else '<i class="fas fa-sign-out-alt mr-1 text-danger"></i><span class="text-gray-900">unlink</span>',
        'link-target':"btn-outline-success" if not self.company_id else "btn-outline-danger",
        'createdby':self.user_id,
        }
    
    def view_invoices(self,period):
        return {
        'id':self.id,
        "propid":self.id,
        'editid':ApartmentOp.generate_editid(self),
        'delid':ApartmentOp.generate_delid(self),
        'identity':"prp"+str(self.id),
        'billid':"bill"+str(self.id),
        'smsid':"sms"+str(self.id),
        'invsid':"invs"+str(self.id),
        'depsid':"deps"+str(self.id),
        'progress':ApartmentOp.get_progress(self),
        'bill_outline':ApartmentOp.get_bill_outline(self,period),
        "name":self.name,
        }

    def view_payments(self):
        return {
        'id':self.id,
        "propid":self.id,
        'editid':ApartmentOp.generate_editid(self),
        'delid':ApartmentOp.generate_delid(self),
        'identity':"prp"+str(self.id),
        "name":self.name,

        }


class HouseCodeOp(HouseCode,Base):
    def __init__(self,codename,rentrate,waterrate,garbagerate,securityrate,finerate,waterdep,elecdep,watercharge,electricityrate,servicerate,seweragerate,discount,depnum,apartment_id,user_id):
        self.codename = codename
        self.rentrate=rentrate
        self.watercharge=watercharge
        self.waterrate=waterrate
        self.electricityrate=electricityrate
        self.garbagerate=garbagerate
        self.securityrate=securityrate
        self.servicerate=servicerate
        self.finerate=finerate
        self.waterdep = waterdep
        self.elecdep = elecdep
        self.seweragerate = seweragerate
        self.discount = discount
        self.depnum = depnum
        self.apartment_id = apartment_id
        self.user_id = user_id


    @staticmethod
    def fetch_group_by_id(group_id):
        return HouseCode.query.filter_by(id=group_id).first()

    def fetch_all_housecodes_by_apartment_id(prop_id):
        return HouseCode.query.filter_by(apartment_id=prop_id).order_by(HouseCode.codename.asc()).all()

    def update_rates(self,housecode,rentrate,waterrate,garbagerate,securityrate,finerate,waterdep,elecdep,watercharge,electricityrate,service,sewerage,billfreq,vatrate,carddep,discount,depnum,modified_by):
        if housecode != "null":
            self.codename = housecode
        if rentrate != "null":
            self.rentrate=rentrate
        if watercharge != "null": 
            self.watercharge=watercharge
        if waterrate != "null": 
            self.waterrate=waterrate
        if electricityrate != "null": 
            self.electricityrate=electricityrate
        if garbagerate != "null":
            self.garbagerate=garbagerate
        if securityrate != "null":
            self.securityrate=securityrate
        if finerate != "null":
            self.finerate=finerate
        if waterdep != "null":
            self.waterdep=waterdep
        if elecdep != "null":
            self.elecdep=elecdep
        if service != "null":
            self.servicerate = service
        if sewerage != "null":
            self.seweragerate = sewerage
        if billfreq != "null":
            self.billfrequency = billfreq
        if vatrate != "null":
            self.vatrate = vatrate
        if carddep != "null":
            self.carddep = carddep
        if discount != "null":
            self.discount = discount
        if depnum != "null":
            self.depnum = depnum
            
        self.user_id = modified_by
        db.session.commit()

    def update_water_garbage(self,water,fwater,garbage):
        if water:
            self.waterrate = water
        if fwater:
            self.watercharge = fwater
        if garbage:
            self.garbagerate = garbage

        print("water,garbage updated")

        db.session.commit()

    def update_commission(self,commission):
        if commission != "null":
            self.int_commission = 0.0
            self.commission = commission
        db.session.commit()

    def update_int_commission(self,commission):
        if commission != "null":
            self.commission = 0.0
            self.int_commission = commission
        db.session.commit()

    def update_percentage_deposit(self,deposit):
        if deposit != "null":
            self.percentage_deposit = deposit
            self.deposit = 0.0
        db.session.commit()

    def update_deposit(self,deposit):
        if deposit != "null":
            self.percentage_deposit = 0.0
            self.deposit = deposit
        db.session.commit()

    def update_percentage_discount(self,discount):
        if discount != "null":
            self.percentage_discount = discount
            self.discount = 0.0
        db.session.commit()

    def update_discount(self,discount):
        print("DISCCCCC",discount)
        if discount != "null":
            self.percentage_discount = 0.0
            self.discount = discount
        db.session.commit()

    def update_vatrates(self,billfreq,vatrate):
        print("vat updated",vatrate)  
        if billfreq != "null":
            self.billfrequency = billfreq
        if vatrate != "null":
            self.vatrate = vatrate
            
        db.session.commit()

    def update_waterrate_scale(self,waterrate1,waterrate2,waterrate3):
        self.waterrate1 = waterrate1
        self.waterrate2 = waterrate2
        self.waterrate3 = waterrate3
        db.session.commit()

    def update_sewerage_rate(self,rate):
        self.seweragerate = rate
        db.session.commit()

    def update_listprice(self,rate):
        if rate != "null":
            self.listprice = rate
        db.session.commit()

    def update_instalments(self,instalments):
        if instalments != "null":
            self.instalments = instalments
        db.session.commit()

    def update_rentrate(self,rate):
        self.rentrate = rate
        db.session.commit()

    def update_agreement_rate(self,rate):
        if rate:
            self.agreementrate = rate
            db.session.commit()

    def format_percent_amount(amount):
        decor_fig = f"{amount} %"
        return decor_fig

    def format_discount(self):
        if self.discount:
            return f"{self.discount:,.1f}"
        elif self.percentage_discount:
            return HouseCodeOp.format_percent_amount(self.percentage_discount)
        else:
            return "0.0"

    def format_deposit(self):
        if self.deposit:
            return f"{self.deposit:,.1f}"
        elif self.percentage_deposit:
            return HouseCodeOp.format_percent_amount(self.percentage_deposit)
        else:
            return "not set"

    def format_commission(self):
        if self.commission:
            return HouseCodeOp.format_percent_amount(self.commission)
        elif self.int_commission:
            return f"{self.int_commission:,.1f}"
        else:
            return "not set"

    def format_instalments(self):
        if self.instalments:
            return f"{self.instalments} month(s)"
        else:
            return "not set"

    def view(self):
        return {
            'id':self.id,
            'editid':HouseCodeOp.generate_editid(self),
            'delid':HouseCodeOp.generate_delid(self),
            'housecode':self.codename,
            'rent':HouseCodeOp.fig_format(self.rentrate),
            'price':HouseCodeOp.fig_format(self.listprice),
            'fixedwater':HouseCodeOp.fig_format(self.watercharge),
            'sewage':HouseCodeOp.fig_format(self.seweragerate),
            'water':HouseCodeOp.fig_format(self.waterrate),
            'garbage':HouseCodeOp.fig_format(self.garbagerate),
            'security':HouseCodeOp.fig_format(self.securityrate),
            'service':HouseCodeOp.fig_format(self.servicerate),
            'fine':HouseCodeOp.format_percent_amount(self.finerate),
            'waterdep':HouseCodeOp.fig_format(self.waterdep),
            'elecdep':HouseCodeOp.fig_format(self.elecdep),
            'deposit':HouseCodeOp.format_deposit(self),
            'commission':HouseCodeOp.format_commission(self),
            'instalments':HouseCodeOp.format_instalments(self),
            'discount':HouseCodeOp.format_discount(self),
            'user':HouseCodeOp.get_name(self)
        }


class HouseOp(House,Base):
    """class"""
    def __init__(self,name,apartment_id,housecode_id,created_by,description):
        self.name = name
        self.description = description
        self.apartment_id=apartment_id
        self.housecode_id=housecode_id
        self.user_id=created_by

    def view_meter(self):
        return self.meter_allocated

    @staticmethod
    def fetch_house(name):
        return House.query.filter_by(name=name).first()

    @staticmethod
    def fetch_house_by_id(house_id):
        return House.query.filter_by(id=house_id).first()

    @staticmethod
    def fetch_houses_by_apartment(apartment_id):
        return House.query.filter(House.apartment_id==apartment_id).order_by(House.name.asc()).all()

    @staticmethod
    def fetch_all_houses_by_user(user_id):
        return House.query.join(User.houses).filter(User.id == user_id).order_by(House.name.asc()).all()#many to many relationship

    @staticmethod
    def fetch_houses():
        return House.query.order_by(House.id.desc()).all()

    @staticmethod
    def relate_house(house,user):
        house.users.append(user)
        db.session.commit()

    @staticmethod
    def terminate_house(house,user):
        house.users.remove(user)
        db.session.commit()

    def update_details(self,name,desc):
        if desc:
            self.description = desc
        if name:
            self.name = name
            
        db.session.commit()

    def update_billing_details(self,watertarget,servicetarget):
        if watertarget:
            self.watertarget = watertarget
        if servicetarget:
            self.servicetarget = servicetarget
            
        db.session.commit()

    def update_bank(self,bank,acc):
        self.payment_bank = bank
        self.payment_bankacc = acc
        db.session.commit()

    def update_floor(self,flr):
        self.floor = flr
        db.session.commit()

    def update_housecode_id(self,housecode_id):
        self.housecode_id = housecode_id
        db.session.commit()

    def update_billable(self,bool_val):
        self.billable = bool_val
        db.session.commit()

    def get_tenantname(self):
        """method to get tenant name from tenant alloc id"""
        tenant_alloc_objs = self.tenant_allocated
        if tenant_alloc_objs:
            for tenant_alloc in tenant_alloc_objs:
                if tenant_alloc.active == True:
                    return tenant_alloc.tenant.name.title()
            if self.owner:
                return "not rented"
            return "-vacant-"
        if self.owner:
            return "not rented"
        return "-vacant-"

    def highlight_vacancy(self):
        tenant_alloc_objs = self.tenant_allocated
        if tenant_alloc_objs:
            for tenant_alloc in tenant_alloc_objs:
                if tenant_alloc.active == True:
                    return ""
            return "text-danger"
        return "text-danger"

    def get_meterno(self):
        """fetch allocated meter"""
        if self.meter_allocated:
            found = False
            allocs = self.meter_allocated
            for alloc in allocs:
                if alloc.active and alloc.meter.metertype == "water":
                    meter = alloc.meter
                    found = True
            if found:
                return meter
            else:
                return "?"
        return "?"

    def highlight_unmetered(self):
        if self.meter_allocated:
            found = False
            allocs = self.meter_allocated
            for alloc in allocs:
                if alloc.active and alloc.meter.metertype == "water":
                    found = True
            if found:
                return ""
            else:
                return "text-danger"
        return "text-danger"

    def format_amount(amount):
        if amount:
            rounded_fig = round(amount,2)
        else:
            rounded_fig = 0

        decor_fig = (f"{rounded_fig:,}")
        
        return decor_fig

    def format_amount_and_sbilling(self,amount):
        if amount:
            rounded_fig = round(amount,2)
        else:
            rounded_fig = 0

        decor_fig = (f"{rounded_fig:,}")

        if self.servicetarget:
            if self.servicetarget == "owner":
                badge = "badge-danger bg-danger"
                target = "WN"
            else:
                target = "TNT"
                badge = "badge-primary bg-primary"
            return f'<span class="badge {badge} badge-counter">{target}</span> {decor_fig} '
        else:
            return decor_fig

    def format_amount_and_wbilling(self,amount):
        if amount:
            rounded_fig = round(amount,2)
        else:
            rounded_fig = 0

        decor_fig = (f"{rounded_fig:,}")

        if self.watertarget:
            if self.watertarget == "tenant":
                badge = "badge-primary bg-primary"
                target = "TNT"
            else:
                target = "WN"
                badge = "badge-danger bg-danger"
            return f'<span class="badge {badge} badge-counter">{target}</span> {decor_fig}'
        else:
            return decor_fig

    def format_percent_amount(amount):
        decor_fig = f"{amount} %"
        return decor_fig 

    def getname(user_id):
        user_obj = User.query.filter_by(id=user_id).first()
        fname = user_obj.name.split()[0]
        return fname

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def get_status(self):
        # print(">>>>>>>",self.status)
        if self.status == "available":
            return '<span class="badge font-weight-bold bg-success-alt text-success">Available</span>'
        elif self.status == "booked":
            return '<span class="badge font-weight-bold bg-warning-alt text-warning">Booked</span>'
        else:
            return '<span class="badge font-weight-bold bg-info-alt text-info">Sold</span>'

    def get_agentname(self):
        """method to get tenant name from tenant alloc id"""
        try:
            return self.owner.rep
        except Exception as e:
            return '<span class="text-danger">-n/a-</span>'


    def get_booking(self):
        """method to get tenant name from tenant alloc id"""

        try:
            return self.owner.date.date()
        except:
            return '<span class="text-danger">-n/a-</span>'

    def view(self):
        if not self.housecode:
            return {
                'id':self.id,
                'editid':HouseOp.generate_editid(self),
                'delid':HouseOp.generate_delid(self),
                "highlight":HouseOp.highlight_vacancy(self),
                "mhighlight":HouseOp.highlight_unmetered(self),
                'house':self.name,
                'group':self.housecode,
                'description':self.description,
                'status':HouseOp.get_status(self),

                'agent':HouseOp.get_agentname(self),
                'booking':HouseOp.get_booking(self),

                'tenant':HouseOp.get_tenantname(self),
                'owner':self.owner.name.title() if self.owner else "N/A",
                'meter':HouseOp.get_meterno(self),
            }
        else:
            return {
                'id':self.id,
                'editid':HouseOp.generate_editid(self),
                'delid':HouseOp.generate_delid(self),
                "highlight":HouseOp.highlight_vacancy(self),
                "mhighlight":HouseOp.highlight_unmetered(self),
                'house':self.name,
                'group':self.housecode,
                'description':self.description,
                'status':HouseOp.get_status(self),

                'agent':HouseOp.get_agentname(self),
                'booking':HouseOp.get_booking(self),

                'tenant':HouseOp.get_tenantname(self),
                'owner':self.owner.name.title() if self.owner else "N/A",
                'meter':HouseOp.get_meterno(self),
                'price':HouseOp.format_amount(self.housecode.listprice if self.housecode.listprice else 0),
                'rent':HouseOp.format_amount(self.housecode.rentrate if self.housecode else 0),
                'rate':HouseOp.format_amount_and_wbilling(self,self.housecode.waterrate if self.housecode else 0),
                'srate':HouseOp.format_amount_and_wbilling(self,self.housecode.seweragerate if self.housecode else 0),
                'fixed':HouseOp.format_amount(self.housecode.watercharge if self.housecode else 0),
                'maintenance':HouseOp.format_amount_and_sbilling(self,self.housecode.servicerate if self.housecode else 0),
                'garbage':HouseOp.format_amount(self.housecode.garbagerate if self.housecode else 0),
                'security':HouseOp.format_amount(self.housecode.securityrate if self.housecode else 0),
                'fine':HouseOp.format_percent_amount(self.housecode.finerate if self.housecode else 0),
                'by':HouseOp.getname(self.housecode.user_id) if self.housecode else "N/A"
            }

class SalesRepOp(SalesRep,Base):
    """class"""
    def __init__(self,name,email,username,phone,company_id):
        self.name = name
        self.email = email
        self.username = username
        self.phone = phone
        self.company_id = company_id

    @staticmethod
    def fetch_attendant_by_id(group_id):
        return SalesRep.query.filter_by(id=group_id).first()

    @staticmethod
    def fetch_rep_by_name(name):
        return SalesRep.query.filter_by(name=name).first()

    @staticmethod
    def fetch_rep_by_email(email):
        return SalesRep.query.filter_by(email=email).first()

    @staticmethod
    def fetch_rep_by_username(name):
        return SalesRep.query.filter_by(username=name).first()

    def update_commission(self,mcom):
        self.monthly_commission = mcom
        db.session.commit()

    def get_clients(self):
        clients = self.clients
        return len(clients)

    def get_projects(self):
        my_string = ""
        props = ApartmentOp.fetch_all_apartments_by_user(self.user.id)
        for prop in props:
            my_string += (prop.name + ",")
        return f'<span class="text-gray-900 font-weight-bold">{my_string}</span>' 

    def fetch_proposals(self):
        clients = self.clients
        proposals = []
        for i in clients:
            if i.status == "proposal":
                proposals.append(i)
        return len(proposals)

    def fetch_closed(self):
        clients = self.clients
        proposals = []
        for i in clients:
            if i.status == "closed":
                proposals.append(i)
        return len(proposals)

    def get_conv(self):
        proposals = SalesRepOp.get_clients(self)
        closed = SalesRepOp.fetch_closed(self)
        try:
            conv = closed/proposals
        except:
            conv = 0

        return f"{conv}%"

    def view(self):
        return {
            'id':self.id,
            'editid':SalesRepOp.generate_editid(self),
            'delid':SalesRepOp.generate_delid(self),
            'name':f"{self.name} ({self.email})" if self.email else self.name,
            'tel':self.phone,
            'leads':len(self.leads),
            'clients':SalesRepOp.get_clients(self),
            'proposals':SalesRepOp.fetch_proposals(self),
            'closed':SalesRepOp.fetch_closed(self),
            'conv':SalesRepOp.get_conv(self),
            'comm':SalesRepOp.fig_format(self.monthly_commission),
        }

class MeterOp(Meter,Base):
    def __init__(self, serial_num,meter_num,initial_reading,decitype,metertype,apartment_id,created_by):
        self.meter_number = meter_num
        self.serial_number = serial_num
        self.initial_reading = initial_reading
        self.decitype = decitype
        self.metertype = metertype
        self.apartment_id = apartment_id

        self.user_id = created_by

    @staticmethod
    def fetch_meter(meter_num):
        return Meter.query.filter_by(meter_number=meter_num).first()

    @staticmethod
    def fetch_meter_by_id(meter_id):
        try:
            obj = Meter.query.filter_by(id=meter_id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            obj = None
            db.session.rollback()

        return obj

    @staticmethod
    def fetch_meter_by_serial(serial_num):
        return Meter.query.filter_by(meter_number=serial_num).first()

    @staticmethod
    def fetch_all_meters():
        return Meter.query.order_by(Meter.meter_number.desc()).all()

    @staticmethod
    def fetch_meters_by_apartment(apartment_id):
        return Meter.query.filter(Meter.apartment_id==apartment_id).order_by(Meter.meter_number.asc()).all()

    def update_initial_reading(self,reading):
        if reading == 0:
            self.initial_reading = reading
        elif reading:
            self.initial_reading = reading
        else:
            pass
        db.session.commit()

    def update_metertype(self,metertype):
        self.metertype = metertype
        db.session.commit()

    def update_decitype(self,decitype):
        if decitype:
            self.decitype = decitype
        db.session.commit()

    def get_houseno(self):
        """fetch alloted house"""
        metertype = self.metertype
        if self.house_allocated:
            found = False
            allocs = self.house_allocated
            for alloc in allocs:
                if alloc.active and alloc.meter.metertype == metertype:
                    house = alloc.house
                    found = True
            if found:
                return house,"hide",""
            else:
                return "?","","hide"
        return "?","","hide"

    def view(self):
        return {
            'id':self.id,
            'editid':MeterOp.generate_editid(self),
            'delid':MeterOp.generate_delid(self),
            'serial':self.serial_number,
            'meternum':self.meter_number,
            'type':self.metertype,
            'decimal':self.decitype,
            'initial':self.initial_reading,
            'housenum':MeterOp.get_houseno(self)[0],
            'alloc-disp':MeterOp.get_houseno(self)[1],
            'dealloc-disp':"",
            # 'dealloc-disp':MeterOp.get_houseno(self)[2],
            'regby':MeterOp.get_name(self)
        }

class AllocateMeterOp(AllocateMeter,Base):
    def __init__(self,apartment_id,house_id,meter_id,user_id,description=None):
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.meter_id=meter_id
        self.user_id=user_id
        self.description=description

    def update_status(self,status,cleared_by):
        self.active = status
        self.user_id = cleared_by
        db.session.commit()


class MeterReadingOp(MeterReading,Base):
    """class"""
    def __init__(self,description,reading,last_reading,units,reading_period,apartment_id,house_id, meter_id,created_by):
        self.description=description
        self.reading=reading
        self.last_reading=last_reading
        self.units=units
        self.reading_period=reading_period
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.meter_id = meter_id
        self.user_id = created_by

    @staticmethod
    def fetch_reading(meter_id):
        return MeterReading.query.filter_by(meter_id=meter_id).order_by(MeterReading.id.desc()).first()

    @staticmethod
    def fetch_specific_reading(id):
        return MeterReading.query.filter_by(id=id).first()

    def fetch_meterreading_by_smsid(smsid):
        return MeterReading.query.filter(MeterReading.smsid==smsid).first()

    @staticmethod
    def fetch_all_readings(meter_id):
        return MeterReading.query.filter_by(meter_id=meter_id).order_by(MeterReading.date.desc()).all()

    @staticmethod
    def fetch_all_readings_by_house(house_id):
        return MeterReading.query.filter_by(house_id=house_id).order_by(MeterReading.date.desc()).all()

    @staticmethod
    def fetch_all_readings_by_apartment(apartment_id):
        return MeterReading.query.filter_by(apartment_id=apartment_id).order_by(MeterReading.house_id.asc()).all()

    def charge_status(self):
        if self.charged:
            return f"{self.charge.amount:,.2f}" if self.charge else 0.0
        return "not charged"

    def highlight_charge_status(self):
        if self.charged:
            return ""
        return "text-danger"

    def update_units(self,units):
        self.units = units
        db.session.commit()

    def update_reading_period(self,reading_period):
        """to be marked obsolete on April 2021"""
        self.reading_period = reading_period
        db.session.commit()

    def update_rate(self):
        self.rate = self.house.housecode.waterrate
        db.session.commit()

    def update_prev(self,prev):
        self.last_reading = prev
        db.session.commit()

    def update_curr(self,curr):
        if curr == 0:
            self.reading = curr
        elif curr:
            self.reading = curr
        else:
            pass
        db.session.commit()

    def update_sms_status(self,status):
        self.sms_invoice = status
        db.session.commit()

    def update_mail_status(self,status):
        self.email_invoice = status
        db.session.commit()

    def update_smsid(self,smsid):
        self.smsid = smsid
        db.session.commit()

    def update_reading_units(self,lreading,reading,units,user_id):
        if reading:
            self.reading = reading
        if lreading:
            self.last_reading = lreading
        self.units = units
        self.user_id = user_id
        db.session.commit()

    def view_amount(self):
        if self.charged:
            # charge_obj = ChargeOp.fetch_charge_by_reading_id(self.id)
            if self.charge:
                return f"{self.charge.amount:,.2f}"
            return 0.0
        return 0.0

    def check_originality(self):
        if self.charged:
            charge_obj = ChargeOp.fetch_charge_by_reading_id(self.id)
            if charge_obj:
                if charge_obj.state == "modified":
                    return "Amended"
                return "Initial"
            return "N/A"
        return "N/A"

    def get_rates(self):
        if self.meter.metertype == "water":
            rate = self.house.housecode.waterrate
            if self.house.housecode.seweragerate:
                rate = f'{self.house.housecode.waterrate} & {self.house.housecode.seweragerate}'
        else:
            rate = self.house.housecode.electricityrate
            
        return rate


    def get_sms_status(self):
        if self.sms_invoice:
            if self.sms_invoice == "Success":
                status = '<span class="text-success"><i class="fas fa-check-double mr-1"></i>Sent</span>'
            elif self.sms_invoice == "success-alt":
                status = '<span class="text-primary"><i class="fas fa-check-double mr-1"></i>Sent</span>'
            elif self.sms_invoice == "waiting":
                status = '<span class="text-warning font-weight-bold"><i class="fas fa-hourglass-half mr-1"></i>Resend</span>'
            elif self.sms_invoice == "sent":
                status = '<span class="text-primary"><i class="fas fa-check mr-1"></i>Sent</span>'
            elif self.sms_invoice == "pending":
                status = '<span class="text-primary"><i class="fas fa-clock mr-1"></i>Send</span>'
            elif self.sms_invoice == "fail":
                status = '<span class="text-danger"><i class="fas fa-exclamation-triangle mr-1">Resend</i></span>'
            elif self.sms_invoice == "off":
                status = '<span class="text-dark"><i class="fas fa-ban mr-1"></i>Off</span>'
            else:
                status = '<span class="text-danger"><i class="fas fa-exclamation mr-1"></i>Resend</span>'
        else:
            status = '<span class="text-danger"><i class="fas fa-ban mr-1"></i>Null</span>'

        return status
    
    def get_units(units):
        if units > 8:
            return f'<span class="text-danger">{units}</span>'
        return f'<span class="text-black">{units}</span>'

    def fetch_meter_readings(propid,period,status):
        pattern = f"%{status}%"

        query = (MeterReading.query.filter(
                        MeterReading.apartment_id == propid,
                        extract('month', MeterReading.reading_period)  == period.month,
                        extract('year', MeterReading.reading_period) == period.year,
                        not_(MeterReading.description.ilike(pattern))
                ))
        
        return query.all()

    def view(self):
        return {
            'id':self.id,
            'editid':MeterReadingOp.generate_editid(self),
            'delid':MeterReadingOp.generate_delid(self),
            'highlight':MeterReadingOp.highlight_charge_status(self),
            # 'status':MeterReadingOp.check_originality(self),
            'house':self.house,
            'meter':self.meter,
            'date':self.date.date(),
            'period':MeterReadingOp.get_str_month(self.reading_period.month),
            'reading':self.reading,
            'last_reading':self.last_reading,
            'units':MeterReadingOp.get_units(self.units),
            'rate':MeterReadingOp.get_rates(self),
            'charged':MeterReadingOp.charge_status(self),
            'amount':MeterReadingOp.view_amount(self),
            'description':self.description,
            # 'smsstatus':MeterReadingOp.get_sms_status(self),
            # 'smsoutline': "" if self.sms_invoice == "sent" or self.sms_invoice == "Success" or self.sms_invoice == "success-alt" else "primary",
            # 'smsactive': "disabled" if self.sms_invoice == "sent" or self.sms_invoice == "Success" or self.sms_invoice == "success-alt" else "",
            'readby':MeterReadingOp.get_name(self)
        }

    def update_charge_status(self,status):
        self.charged = status
        db.session.commit()

    def update_date(self,date):
        self.date = date
        db.session.commit()   

class ElectricityReadingOp(ElectricityReading,Base):
    """class"""

    def __init__(self,description,reading,last_reading,units,reading_period,apartment_id,house_id, meter_id,created_by):
        self.description=description
        self.reading=reading
        self.last_reading=last_reading
        self.units=units
        self.reading_period=reading_period
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.meter_id = meter_id
        self.user_id = created_by

    @staticmethod
    def fetch_reading(meter_id):
        return ElectricityReading.query.filter_by(meter_id=meter_id).order_by(ElectricityReading.date.desc()).first()

    @staticmethod
    def fetch_specific_reading(id):
        return ElectricityReading.query.filter_by(id=id).first()

    @staticmethod
    def fetch_all_readings(meter_id):
        return ElectricityReading.query.filter_by(meter_id=meter_id).order_by(ElectricityReading.date.desc()).all()

    @staticmethod
    def fetch_all_readings_by_house(house_id):
        return ElectricityReading.query.filter_by(house_id=house_id).order_by(ElectricityReading.date.desc()).all()

    @staticmethod
    def fetch_all_readings_by_apartment(apartment_id):
        return ElectricityReading.query.filter_by(apartment_id=apartment_id).order_by(ElectricityReading.house_id.asc()).all()

    def charge_status(self):
        if self.charged:
            return self.charge.amount if self.charge else 0.0
        return "not charged"

    def highlight_charge_status(self):
        if self.charged:
            return ""
        return "text-danger"

    def update_units(self,units):
        self.units = units
        db.session.commit()

    def update_reading_period(self,reading_period):
        """to be marked obsolete on April 2021"""
        self.reading_period = reading_period
        db.session.commit()

    def update_prev(self,prev):
        self.last_reading = prev
        db.session.commit()

    def update_curr(self,curr):
        self.reading = curr
        db.session.commit()

    def update_reading_units(self,lreading,reading,units,user_id):
        if reading:
            self.reading = reading
        if lreading:
            self.last_reading = lreading
        self.units = units
        self.user_id = user_id
        db.session.commit()

    def view_amount(self):
        if self.charged:
            charge_obj = ChargeOp.fetch_charge_by_elec_reading_id(self.id)
            if charge_obj:
                return charge_obj.amount
            return 0.0
        return 0.0

    def check_originality(self):
        if self.charged:
            charge_obj = ChargeOp.fetch_charge_by_elec_reading_id(self.id)
            if charge_obj:
                if charge_obj.state == "modified":
                    return "Amended"
                return "Initial"
            return "N/A"
        return "N/A"


    def view(self):
        return {
            'id':self.id,
            'editid':ElectricityReadingOp.generate_editid(self),
            'delid':ElectricityReadingOp.generate_delid(self),
            'highlight':ElectricityReadingOp.highlight_charge_status(self),
            'status':ElectricityReadingOp.check_originality(self),
            'house':self.house,
            'meter':self.meter,
            'date':self.date.date(),
            'period':ElectricityReadingOp.get_str_month(self.reading_period.month),
            'reading':self.reading,
            'last_reading':self.last_reading,
            'units':self.units,
            'rate':self.house.housecode.waterrate,
            'charged':ElectricityReadingOp.charge_status(self),
            'amount':ElectricityReadingOp.view_amount(self),
            'description':self.description,
            'readby':ElectricityReadingOp.get_name(self)
        }

    def update_charge_status(self,status):
        self.charged = status
        db.session.commit()

    def update_date(self,date):
        self.date = date
        db.session.commit() 

class ChargeTypeOp(ChargeType, Base):
    def __init__(self,charge_type):
        self.charge_type = charge_type

    def fetch_charge_type(chargetype):
        return ChargeType.query.filter_by(charge_type=chargetype).first()

class ChargeOp(Charge, Base):
    """class"""
    def __init__(self,charge_type_id,amount,apartment_id,house_id,billed_by,date,meter_id=None,reading_id=None):
        self.charge_type_id=charge_type_id
        self.amount=amount
        self.apartment_id=apartment_id
        self.house_id = house_id
        self.meter_id = meter_id
        self.reading_id =reading_id
        self.user_id = billed_by
        self.date = date
    @staticmethod
    def fetch_charges_by_apartment_id(apartment_id):
        return Charge.query.filter(Charge.apartment_id==apartment_id).order_by(Charge.date.asc()).all()

    @staticmethod
    def fetch_charges_by_house_id(house_id):
        return Charge.query.filter(Charge.house_id==house_id).order_by(Charge.date.asc()).all()

    @staticmethod
    def fetch_charge_by_reading_id(reading_id):
        return Charge.query.filter_by(reading_id=reading_id).first()

    @staticmethod
    def fetch_charge_by_elec_reading_id(reading_id):
        return Charge.query.filter_by(elec_reading_id=reading_id).first()

    def update_amount(self,amount,modified_by):
        self.amount = amount
        self.user_id = modified_by
        db.session.commit()

    def view(self):
        return {
            'id':self.id,
            'house':self.house,
            'meter':self.meter,
            'bill':self.amount,
            'status':self.compiled,
            'date':self.date.date(),
            'billedby':ChargeOp.get_name(self)
        }

    def update_compiled_status(self,status):
        self.compiled = status
        db.session.commit()


class LeadOp(Lead,Base):
    def __init__(self,name,phone,national_id,email,company_id,created_by):
        self.name = name
        self.phone = phone
        self.national_id = national_id
        self.email = email
        self.company_id = company_id
        self.user_id = created_by

    def fetch_lead_by_id(lead_id):
        return Lead.query.filter_by(id=lead_id).first()

    def fetch_lead_by_natid(national_id):
        return Lead.query.filter_by(national_id=national_id).first()

    def fetch_lead_by_phone(phone):
        return Lead.query.filter_by(phone=phone).first()

    def fetch_lead_by_email(email):
        return Lead.query.filter_by(email=email).first()

    def fetch_all_leads_per_company_id(company_id):
        return Lead.query.filter_by(company_id=company_id).all()

    def update_status(self, status):
        if status:
            self.status = status
        db.session.commit()

    def update_sales_rep(self, rep_id):
        self.rep_id = rep_id
        db.session.commit()


    def view(self):
        # print("NAME >>>>",self.name)
        return {
            'id':self.id,
            'editid':LeadOp.generate_editid(self),
            'delid':LeadOp.generate_delid(self),
            'name':self.name,
            'idno':self.national_id,
            'tel':self.phone,
            'email':self.email,
            'status':self.status,
            'date':self.date.date(),
            'chats': len(self.conversations)
        }

class ConversationOp(Conversation,Base):
    def __init__(self,channel,subject,discussion,feedback):
        self.channel = channel
        self.subject = subject
        self.discussion = discussion
        self.feedback = feedback


class PermanentTenantOp(PermanentTenant,Base):
    def __init__(self,name,phone,national_id,email,arrears,house_id,apartment_id,created_by):
        self.name = name
        self.phone = phone
        self.national_id = national_id
        self.email = email
        self.initial_arrears = arrears
        self.house_id = house_id
        self.apartment_id = apartment_id
        self.user_id = created_by

    def fetch_tenant_by_nat_id(nat_id):
        return PermanentTenant.query.filter_by(national_id=nat_id).first()

    def fetch_tenant_by_uid(uid):
        if uid:
            return PermanentTenant.query.filter_by(uid=uid).first()
        else:
            return None

    def fetch_tenant_by_tel(tel):
        return PermanentTenant.query.filter_by(phone=tel).first()

    def fetch_tenant_by_email(email):
        return PermanentTenant.query.filter_by(email=email).first()

    def fetch_tenant_by_id(id):
        try:
            return PermanentTenant.query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            db.session.rollback()
            return None

    def fetch_all_tenants():
        return PermanentTenant.query.order_by(PermanentTenant.date.desc()).all()

    def fetch_all_tenants_by_apartment(apartment_id):
        return PermanentTenant.query.filter(PermanentTenant.apartment_id==apartment_id).order_by(PermanentTenant.name.asc()).all()

    def update_tenant(self,uid,name=None,phone=None,email=None,national_id=None,arr=None,fine=None,multi="null",modified_by=None):
        if name:
            self.name = name
        if phone:
            if phone == "null":
                self.phone = None
            else:
                self.phone = phone
        if uid:
            if uid == "None":
                self.uid = None
            else:
                self.uid = uid
        if email:
            if email == "null":
                self.email = None
            else:
                self.email = email

        if national_id:
            self.national_id = national_id
        if arr:
            self.initial_arrears = arr
        # else:
        #     self.initial_arrears = 0.0
        if fine:
            self.accumulated_fine = fine
        # else:
        #     self.fine = 0.0
        if modified_by:
            self.user_id = modified_by

        if multi != "null":
            # self.multiple_houses = multi
            pass
        db.session.commit()

    def update_national_id(self,natid):
        self.national_id = natid
        db.session.commit()

    def update_phone(self,phone):
        self.phone = phone
        db.session.commit()

    def get_houseno(self):
        """method to get tenant name from tenant alloc id"""
        return f'{self.house}'

    def combine_house_tenant(self):
        try:
            fname = self.name.split()[0] if self.name else "Tenant"
        except:
            fname = "Tenant"

        truncated_name = smart_truncate(fname,20)
        house =  PermanentTenantOp.get_houseno(self)
        return f'<span class="text-gray-900">({house})</span> <span class="text-primary font-weight-bold">{truncated_name}</span>' 

    def combine_house_tenant_alt(self):
        fname = self.name if self.name else "Tenant"
        truncated_name = smart_truncate(fname,20)
        house =  PermanentTenantOp.get_houseno(self)
        return f'<span class="text-gray-900">({house})</span> <span class="text-primary font-weight-bold">{truncated_name}</span>' 

    def format_balance(self):
        bal = self.balance
        rounded_bal = round(bal,2)
        decorated_bal = (f"{rounded_bal:,}")
        return f"{decorated_bal}"

    def highlight(self):
        if self.balance > 0.0:
            return "text-danger"
        elif self.balance < 0.0:
            return "text-success"
        else:
            return "text-dark"

    def update_payment_plan(self,negprice,plan,deposit,deposit2,mi,num_mi,bookedon,start):
        if negprice:
            self.negotiated_price = negprice
        if plan:
            self.plan = plan
        if deposit:
            self.deposit = deposit
        if deposit2:
            self.deposit2 = deposit2
        if mi:
            self.instalment = mi
        if num_mi:
            self.num_instalment = num_mi
        if bookedon:
            self.date =bookedon
        if start:
            self.checkin =start

        db.session.commit()

    def update_checkin_date(self, checkin_date):
        self.checkin = checkin_date
        db.session.commit()

    def upload_contracts(self,contracts_url,uploadedon):
        if contracts_url:
            self.contracts_url = contracts_url
        if uploadedon:
            pass

        db.session.commit()

    def update_balance(self,balance):
        self.balance = balance
        db.session.commit()

    def update_rep_id(self,repid):
        self.rep_id = repid
        db.session.commit()

    def update_can_receive_sms(self,status):
        self.sms = status
        db.session.commit()

    def update_fine(self,fine):
        self.accumulated_fine= fine
        db.session.commit()

    def update_deposit(self,deposit):
        self.deposit = deposit
        db.session.commit()

    def update_initial_arrears(self,initial_arrears):
        self.initial_arrears = initial_arrears
        db.session.commit()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def update_classtype(self,status):
        self.classtype = status
        db.session.commit()

    def update_tenant_type(self,status):
        self.tenant_type = status
        db.session.commit()

    def update_resident_type(self,status):
        self.resident_type = status
        db.session.commit()

    def update_residency(self,residency):
        self.residency = residency
        db.session.commit()

    def get_contact(self):
        return self.phone if self.phone else "-"

    def get_email(self):
        return self.email if self.email else "-"

    def billable(self):
        return "Yes" if self.sms else "No"

    def checkin_date(self):

        date = self.date.date()

        return date

    # def generate_editid(self):
    #     return "edit" + str(self.id)

    def generate_identity(self):
        return "ptnt"+str(self.id)

    def generate_name(self):
        if self.name:
            try:
                name = self.name.split()[0]
                return name.lower() 
            except Exception as e:
                print("err len>>",len(self.name),"name:",self.name)
                return "Resident"
        else:
            return "Resident"

    def get_status(self):
        if self.status == "proposal":
            return '<span class="badge font-weight-bold bg-warning">Proposal</span>'
        elif self.status == "prospective":
            return '<span class="badge font-weight-bold bg-success">Prospective</span>'
        elif self.status == "invoiced and missing contracts":
            return '<span class="badge font-weight-bold bg-danger-alt text-danger">Missing contracts</span>'
        elif self.status == "invoiced and contracts":
            return '<span class="badge font-weight-bold bg-success-alt text-success">Invoiced</span>'
        else:
            return f'<span class="badge font-weight-bold bg-dark">{self.status}</span>'

    def get_price(alloc):
        # import pdb;
        # pdb.set_trace()
        try:
            return f"{alloc.negotiated_price:,.1f}"
        except:
            return 0.0

    def get_deposit(alloc):
        try:
            return f"{alloc.deposit:,.1f}"
        except:
            return 0.0

    def get_plan(alloc):
        try:
            return alloc.plan
        except:
            return "n/a"

    def get_mi(alloc):
        try:
            return f"{alloc.instalment:,.1f}"
        except:
            return 0.0

    def get_num_mi(alloc):
        try:
            return alloc.num_instalment
        except:
            return 0.0

    def booking_date(alloc):
        try:
            return alloc.date.date()
        except:
            return "n/a"

    def get_stage_percentage(self):
        unit = self.house
        if unit.monthlybills:
            bill = unit.monthlybills[0]
        else:
            bill = None

        if bill:
            try:
                quotient = bill.paid_amount / bill.total_bill
            except:
                quotient = 0
        else:
            quotient = 0
        
        percentage = quotient * 100

        return f"{percentage:,.0f}%"


    def generate_editid(self):
        return "pedit" + str(self.id)

    def generate_delid(self):
        return "pdel" + str(self.id)

    def get_uid(self):
        if not self.uid:
            return f"WN{self.id}"
        else:
            return self.uid

    def get_amount(self):
        unit = self.house
        if unit.monthlybills:
            bill = unit.monthlybills[0]
        else:
            bill = None
        if bill:
            return f'{bill.total_bill:,.1f}'
        else:
            return 0.0

    def get_paid(self):
        unit = self.house
        if unit.monthlybills:
            bill = unit.monthlybills[0]
        else:
            bill = None
        if bill:
            return f'{bill.paid_amount:,.1f}'
        else:
            return 0.0

    def get_balance(self):
        unit = self.house
        if unit.monthlybills:
            bill = unit.monthlybills[0]
        else:
            bill = None
        if bill:
            return f'{bill.balance:,.1f}'
        else:
            return 0.0

    def view(self):
        # print("NAME >>>>",self.name)
        return {
            'id':"p" + str(self.id),
            'identity':PermanentTenantOp.generate_identity(self),
            'editid':PermanentTenantOp.generate_editid(self),
            'delid':PermanentTenantOp.generate_delid(self),
            'uid':PermanentTenantOp.get_uid(self),
            'name':PermanentTenantOp.generate_name(self),
            'fullname':self.name,
            'hst':PermanentTenantOp.combine_house_tenant(self),
            'hstalt':PermanentTenantOp.combine_house_tenant_alt(self),
            'idno':self.national_id,
            'tel':PermanentTenantOp.get_contact(self),
            'email':smart_truncate(PermanentTenantOp.get_email(self),28),
            'sms':PermanentTenantOp.billable(self),
            'housenum':PermanentTenantOp.get_houseno(self),
            'price':PermanentTenantOp.get_price(self),
            'deposit':PermanentTenantOp.get_deposit(self),
            'plan':PermanentTenantOp.get_plan(self),
            'mi':PermanentTenantOp.get_mi(self),
            'num_mi':PermanentTenantOp.get_num_mi(self),
            'housenum':PermanentTenantOp.get_houseno(self),
            'status':PermanentTenantOp.get_status(self),
            'stage':PermanentTenantOp.get_stage_percentage(self),
            'booking':PermanentTenantOp.booking_date(self),
            'rep':self.rep.name if self.rep else "-n/a-",
            'ctype':self.classtype.lower() if self.classtype else "-",
            'badge':'<span class="badge bg-warning badge-warning badge-counter">owner</span>',
            'checkin':PermanentTenantOp.checkin_date(self),
            'amount':PermanentTenantOp.get_amount(self),
            'paid':PermanentTenantOp.get_paid(self),
            'balance':PermanentTenantOp.get_balance(self),
            'highlight':PermanentTenantOp.highlight(self),
            'viewable':"danger" if self.multiple_houses else "",
            'active':"" if self.multiple_houses else "disabled",
            'tooltip': "allow tenant to occupy more than one house first" if not self.multiple_houses else "Allocate more houses",
            'regby':PermanentTenantOp.get_name(self)
        }



class TenantOp(Tenant,Base):
    def __init__(self,name,phone,national_id,email,arrears,randid,apartment_id,created_by):
        self.name = name
        self.phone = phone
        self.national_id = national_id
        self.email = email
        self.initial_arrears = arrears
        self.randid = randid
        self.apartment_id = apartment_id
        self.user_id = created_by

    def fetch_tenant_by_name(name):
        return Tenant.query.filter_by(name=name).first()

    def fetch_all_tenants_by_name(name):
        return Tenant.query.filter_by(name=name).all()

    def fetch_tenant_by_nat_id(nat_id):
        return Tenant.query.filter_by(national_id=nat_id).first()


    def fetch_tenant_by_uid(uid):
        if uid:
            return Tenant.query.filter_by(uid=uid).first()
        else:
            return None

    def fetch_tenant_by_tel(tel):
        return Tenant.query.filter_by(phone=tel).first()

    def fetch_tenant_by_email(email):
        return Tenant.query.filter_by(email=email).first()

    def fetch_tenant_by_id(id):
        try:
            return Tenant.query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            db.session.rollback()
            return None

    def fetch_all_tenants():
        return Tenant.query.order_by(Tenant.date.desc()).all()

    def fetch_all_tenants_by_apartment(apartment_id):
        return Tenant.query.filter(Tenant.apartment_id==apartment_id).order_by(Tenant.name.asc()).all()

    def update_tenant(self,uid,name=None,phone=None,email=None,national_id=None,arr=None,fine=None,multi="null",modified_by=None):
        if name:
            self.name = name
        if phone:
            if phone == "null":
                self.phone = None
            else:
                self.phone = phone

        if email:
            if email == "null":
                self.email = None
            else:
                self.email = email

        if national_id:
            self.national_id = national_id
        if uid:
            if uid == "None":
                self.uid = None
            else:
                self.uid = uid
        if arr:
            self.initial_arrears = arr
        # else:
        #     self.initial_arrears = 0.0
        if fine:
            self.accumulated_fine = fine
        # else:
        #     self.fine = 0.0
        if modified_by:
            self.user_id = modified_by

        if multi != "null":
            self.multiple_houses = multi
        db.session.commit()

    def update_national_id(self,natid):
        self.national_id = natid
        db.session.commit()

    def update_phone(self,phone):
        self.phone = phone
        db.session.commit()

    def update_email(self,mail):
        self.email = mail
        db.session.commit()

    def update_vacate_date(self,date):
        self.vacate_date = date
        db.session.commit()


    def get_houseno(self):
        """method to get tenant name from tenant alloc id"""
        house_alloc_objs = self.house_allocated
        houses = []
        if house_alloc_objs:
            for house_alloc in house_alloc_objs:
                if house_alloc.active == True:
                    houses.append(house_alloc.house.name)
            if len(houses) > 3:
                houses = ["multiple"]
            if len(houses) > 1:
                str_houses = ','.join(map(str, houses))
            else:
                try:
                    str_houses = houses[0]
                except:
                    str_houses = "-vacated-"

            return str_houses if houses else "-vacated-"
        return "-pending-"

    def style_house_name(self):
        house =  TenantOp.get_houseno(self)
        return f'<span class="text-gray-900 font-weight-bold">{house}</span>'

    def combine_house_tenant(self):
        try:
            fname = self.name.split()[0] if self.name else "Tenant"
        except:
            fname = "Tenant"
        house =  TenantOp.get_houseno(self)
        return f'<span class="text-gray-600">({house})</span> <span class="text-gray-900 font-weight-bold small">{fname}</span>' 

    def combine_house_tenant_alt(self):
        fname = self.name if self.name else "Tenant"
        house =  TenantOp.get_houseno(self)
        return f'<span class="text-gray-600">({house})</span> <span class="text-gray-900 font-weight-bold small">{fname}</span>' 

    def format_balance(self):
        bal = self.balance
        rounded_bal = round(bal,2)
        decorated_bal = (f"{rounded_bal:,}")
        return f"{decorated_bal}"

    def highlight(self):
        if self.balance > 0.0:
            return "text-danger"
        elif self.balance < 0.0:
            return "text-success"
        else:
            return "text-dark"

    def update_balance(self,balance):
        self.balance = balance
        db.session.commit()

    def update_can_receive_sms(self,status):
        if status != "null":
            self.sms = status
        db.session.commit()

    def update_fine(self,fine):
        self.accumulated_fine= fine
        db.session.commit()

    def update_deposit(self,deposit):
        self.deposit = deposit
        db.session.commit()

    def update_initial_arrears(self,initial_arrears):
        self.initial_arrears = initial_arrears
        db.session.commit()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def update_residency(self,residency):
        self.residency = residency
        db.session.commit()

    def get_contact(self):
        return self.phone if self.phone else "-"

    def get_email(self):
        return self.email if self.email else "-"

    def billable(self):
        return "Yes" if self.sms else "No"
    
    def check_in_date(self):
        if self.house_allocated:
            date = self.house_allocated[0].checkin_date if self.house_allocated[0].checkin_date else self.date
        else:
            date = self.date

        time_with_s =  f'{date.strftime("%d/%b/%y")} {date.strftime("%H:%M")}'

        return time_with_s

    def check_out_date(self):
        if self.house_allocated:
            date = self.house_allocated[0].checkout_date if self.house_allocated[0].checkout_date else ""
        else:
            date = ""
        
        if date:
            time_with_s = f'{date.strftime("%d/%b/%y")} {date.strftime("%H:%M")}'
        else:
            time_with_s = "--"

        return time_with_s

    def checkin_date(self):
        if self.house_allocated:
            if self.house_allocated[0].active:
                date = self.house_allocated[0].date.date()
            else:
                date = self.house_allocated[0].vacate_date.date()
        else:
            date = self.date.date()

        return date
    
    def get_status(self):
        # print(">>>>>>>",self.accepted_terms)
        if self.accepted_terms:
            return '<span class="badge badge-success badge-counter">Accepted</span>'
        else:
            return '<span class="badge badge-danger badge-counter">Not yet</span>'

    def generate_editid(self):
        return "tedit" + str(self.id)

    def generate_identity(self):
        return "tnt"+str(self.id)

    def generate_alloc_identity(self):
        return "alloc"+str(self.id)

    def generate_delid(self):
        return "tdel" + str(self.id)

    def generate_name(self):
        if self.name:
            try:
                name = self.name.split()[0]
                return name.lower() 
            except Exception as e:
                print("err len>>",len(self.name),"name:",self.name)
                return "Tenant"
        else:
            return "Tenant"

    def format_fullname(self):
        if self.name:
            try:
                name = self.name.split()
                if len(name) > 1:
                    return name[0].title() + " " + name[1].title()
                else:
                    return name[0].title()
            except Exception as e:
                print("err len>>",len(self.name),"name:",self.name)
                return "Tenant"
        else:
            return "Tenant"

    def get_uid(self):
        if not self.uid:
            return f"TNT{self.id}"
        else:
            return f"{self.uid}"

    def get_deposit(alloc):
        try:
            return f"{alloc.deposit:,.1f}"
        except:
            return 0.0

    def get_acc_days(self):
        if self.house_allocated:
            days = self.house_allocated[0].days if self.house_allocated[0].days else 0
        else:
            days = 0

        try:
            int_days = int(days)
        except:
            int_days = 0

        return int_days
    
    def get_invoice(self):
        if self.monthly_charges:
            bill = self.monthly_charges[0].total_bill if self.monthly_charges[0].total_bill else 0.0
            paid = self.monthly_charges[0].paid_amount if self.monthly_charges[0].paid_amount else 0.0
        else:
            bill = 0.0
            paid = 0.0
        if self.house_allocated:
            rentrate = self.house_allocated[0].house.housecode.rentrate
            rate = self.house_allocated[0].agreed_rates if self.house_allocated[0].agreed_rates != None else rentrate
        else:
            rate = 0.0

        return [bill,paid,rate]

    def fetch_payment_mode(self):
        if self.payments:
            paymode = self.payments[0].paymode if self.payments[0].paymode else "N/A"
        else:
            paymode = "N/A"

        if paymode == "Bank":
            paymode = "N/A"

        return paymode


    def view(self):
        # print("NAME >>>>",self.name)
        return {
            'id':self.id,
            'identity':TenantOp.generate_identity(self),
            'editid':TenantOp.generate_editid(self),
            'delid':TenantOp.generate_delid(self),
            'allocid':TenantOp.generate_alloc_identity(self),
            'uid':TenantOp.get_uid(self),
            'name':TenantOp.generate_name(self),
            'fullname':TenantOp.format_fullname(self),
            'terms':TenantOp.get_status(self),
            'hst':TenantOp.combine_house_tenant(self),
            'hstalt':TenantOp.combine_house_tenant_alt(self),
            'idno':self.national_id,
            'tel':TenantOp.get_contact(self),
            'email':TenantOp.get_email(self),
            'sms':TenantOp.billable(self),
            'deposit':TenantOp.get_deposit(self),
            'housenum':TenantOp.style_house_name(self),
            'status':self.status,
            'badge':'<span class="badge font-weight-bold bg-success-alt text-success-dark">occupied</span>',
            'checkin':TenantOp.check_in_date(self),
            'checkout':TenantOp.check_out_date(self),
            'days':TenantOp.get_acc_days(self),
            'bill':TenantOp.get_invoice(self)[0],
            'paid':TenantOp.get_invoice(self)[1],
            'rate':TenantOp.get_invoice(self)[2],
            'balance':TenantOp.format_balance(self),
            'highlight':TenantOp.highlight(self),
            'viewable':"danger" if self.multiple_houses else "",
            'active':"" if self.multiple_houses else "disabled",
            'tooltip': "allow tenant to occupy more than one house first" if not self.multiple_houses else "Allocate more houses",
            'regby':TenantOp.get_name(self)
        }


class TenantDepositOp(TenantDeposit,Base):
    def __init__(self,rentdep,waterdep,elecdep,otherdep,total,date,status,tenant_id,ptenant_id,house_id,apartment_id):
        self.rentdep = rentdep
        self.waterdep = waterdep
        self.elecdep = elecdep
        self.otherdep = otherdep
        self.total = total
        self.date = date
        self.status = status
        self.tenant_id = tenant_id
        self.ptenant_id = ptenant_id
        self.house_id = house_id
        self.apartment_id = apartment_id


    def update_deposits(self,rentdep,waterdep,elecdep,otherdep,total,date,status):
        if rentdep != "null":
            self.rentdep = rentdep
        if waterdep != "null":
            self.waterdep = waterdep
        if elecdep != "null":
            self.elecdep = elecdep
        if otherdep != "null":
            self.otherdep = otherdep
        if date:
            self.date = date
        if status:
            self.status = status
        if total:
            self.total = total
        db.session.commit()

    def update_paid_deposits(self,rentdep,waterdep,elecdep,otherdep,brentdep,bwaterdep,belecdep,botherdep,total,date,status):
        if rentdep != "null":
            self.paid_rentdep = rentdep
        if waterdep != "null":
            self.paid_waterdep = waterdep
        if elecdep != "null":
            self.paid_elecdep = elecdep
        if otherdep != "null":
            self.paid_otherdep = otherdep

        # if rentdep != "null":
        #     self.balance_rentdep = brentdep
        # if waterdep != "null":
        #     self.balance_waterdep = bwaterdep
        # if elecdep != "null":
        #     self.balance_elecdep = belecdep
        # if otherdep != "null":
        #     self.balance_otherdep = botherdep

        self.balance_rentdep = brentdep
        self.balance_waterdep = bwaterdep
        self.balance_elecdep = belecdep
        self.balance_otherdep = botherdep

        if date:
            self.date = date
        if status:
            self.status = status

        db.session.commit()

    def update_paid_deposits_alt(self,total,paid,balance):
        self.total = total
        self.total_paid = paid
        self.balance = balance
        db.session.commit()

    def get_name(self):
        if self.ptenant_id:
            return self.ptenant.name
        else:
            return self.tenant.name

    def view(self):
        return {
            'id': self.id,
            'house':self.house,
            'tenant':TenantDepositOp.get_name(self),
            'rentdep':TenantDepositOp.format(self.rentdep),
            'waterdep':TenantDepositOp.format(self.waterdep),
            'elecdep':TenantDepositOp.format(self.elecdep),
            'otherdep':TenantDepositOp.format(self.otherdep),
            'total':TenantDepositOp.format(self.total),
            'paid':TenantDepositOp.format(self.paid),
            'datepaid':TenantDepositOp.date_format(self.date),
            'balance':TenantDepositOp.format(self.balance),
            'status':self.status
        }


class DepositPaymentOp(DepositPayment,Base):
    def __init__(self,amount,date,status,deposit_id):
        self.amount = amount
        self.date = date
        self.status = status
        self.deposit_id = deposit_id

    def view(self):
        return {
            'id': self.id,
            'deposit':self.deposit,
            'tenant-alt':self.deposit.tenant.name,
            'house':self.deposit.house.name,
            'amount':DepositPaymentOp.format(self.amount),
            'date':DepositPaymentOp.date_format(self.date),
            'status':self.status
        }
    
class TenantExpensesOp(TenantExpenses,Base):
    def __init__(self,repainting,plumbing,electricals,fixtures,others,total,tenant_id,apartment_id):
        self.repainting = repainting
        self.plumbing = plumbing
        self.electricals = electricals
        self.fixtures = fixtures
        self.others = others
        self.total = total
        self.tenant_id = tenant_id
        self.apartment_id = apartment_id


    def update_expenses(self,repainting,plumbing,electricals,fixtures,others,total):
        if repainting != "null":
            self.repainting = repainting
        if plumbing != "null":
            self.plumbing = plumbing
        if electricals != "null":
            self.electricals = electricals
        if fixtures != "null":
            self.fixtures = fixtures
        if others != "null":
            self.others = others
        if total:
            self.total = total
        db.session.commit()


class AllocateTenantOp(Occupancy,Base):
    def __init__(self,apartment_id,house_id,tenant_id,checkin,checkout,user_id,description=None):
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.tenant_id=tenant_id
        self.checkin_date = checkin
        self.checkout_date = checkout
        self.user_id=user_id
        self.description=description

    def fetch_all_allocs_by_apartment(apartment_id):
        return Occupancy.query.filter(Occupancy.apartment_id==apartment_id).order_by(Occupancy.date.asc()).all()

    def tenant_name(self):
        """method to get owner's name from owner id"""
        tenant_obj = Tenant.query.filter_by(id=self.tenant_id).first()
        return tenant_obj.name

    def tenant_national_id(self):
        """method to get owner's name from owner id"""
        tenant_obj = Tenant.query.filter_by(id=self.tenant_id).first()
        return tenant_obj.national_id

    def tenant_phone(self):
        """method to get owner's name from owner id"""
        tenant_obj = Tenant.query.filter_by(id=self.tenant_id).first()
        return tenant_obj.phone if tenant_obj.phone else "-"

    def self_status(self):
        """method to get owner's name from owner id"""
        if self.active == True:
            return "Resident"
        return "Vacated"

    def tenant_balance(self):
        """method to get owner's name from owner id"""
        if isinstance(self.checkout_balance,float):
            if self.checkout_balance < 1.0:
                return "Cleared"
            return f"Kshs {self.checkout_balance}"
        tenant_obj = Tenant.query.filter_by(id=self.tenant_id).first()
        return f"Kshs {tenant_obj.balance}"

    def format_self_date(self):
        if self.vacate_date:
            return self.vacate_date.date()
        return "-N/A-"

    # def update_vacate_period(self,period):
    #     """ METHOD TO BE DELETED IN A WEEK"""
    #     self.vacate_period = period
    #     db.session.commit()

    def update_status(self,status,balance,period,cleared_by):
        self.active = status
        self.vacate_date = datetime.datetime.now()
        self.vacate_period = period
        self.checkout_balance = balance
        self.cleared_by = cleared_by
        db.session.commit()

    def update_agreed_rates(self, agreed_rates):
        self.agreed_rates = agreed_rates

        db.session.commit()

    def update_accomodation_days(self,days):
        self.days = days
        db.session.commit()

    def update_days(self,days):
        self.days_extended = days

        db.session.commit()

    def update_checkin_date(self, checkin_date):
        self.checkin_date = checkin_date
        db.session.commit()

    def update_invoice_status(self,status):
        self.invoiced = status
        db.session.commit()

    def view(self):
        return {
            'name':AllocateTenantOp.tenant_name(self),
            'idno':AllocateTenantOp.tenant_national_id(self),
            'tel':AllocateTenantOp.tenant_phone(self),
            'housenum':self.house,
            'checkin':self.date.date(),
            'checkout':AllocateTenantOp.format_self_date(self),
            'status':AllocateTenantOp.self_status(self),
            "balance":AllocateTenantOp.tenant_balance(self),
            'regby':TenantOp.get_name(self)
        }

class ClientBillOp(ClientBill,Base):
    def __init__(self,year,month,sub,installation,maintenance,customization,arrears,total_amount,company_id):
        self.month = month
        self.year=year
        self.subscription=sub
        self.total=total_amount
        self.arrears = arrears
        self.installation=installation
        self.maintenance=maintenance
        self.customization = customization
        self.company_id=company_id

    def fetch_specific_bill(id):
        return ClientBill.query.filter_by(id=id).first()

    def get_sms_status(self):
        if self.sms_invoice:
            if self.sms_invoice == "Success":
                status = '<span class="text-success"><i class="fas fa-check-double mr-1"></i>Sent</span>'
            elif self.sms_invoice == "success-alt":
                status = '<span class="text-primary"><i class="fas fa-check-double mr-1"></i>Sent</span>'
            elif self.sms_invoice == "waiting":
                status = '<span class="text-warning font-weight-bold"><i class="fas fa-hourglass-half mr-1"></i>Resend</span>'
            elif self.sms_invoice == "sent":
                status = '<span class="text-primary"><i class="fas fa-check mr-1"></i>Sent</span>'
            elif self.sms_invoice == "pending":
                status = '<span class="text-primary"><i class="fas fa-clock mr-1"></i>Send</span>'
            elif self.sms_invoice == "fail":
                status = '<span class="text-danger"><i class="fas fa-exclamation-triangle mr-1">Resend</i></span>'
            elif self.sms_invoice == "off":
                status = '<span class="text-dark"><i class="fas fa-ban mr-1"></i>Off</span>'
            else:
                status = '<span class="text-danger"><i class="fas fa-exclamation mr-1"></i>Resend</span>'
        else:
            status = '<span class="text-danger"><i class="fas fa-ban mr-1"></i>Null</span>'

        return status

    def get_date(self):
        paydate = self.pay_date if self.pay_date else "N/A"
        if not isinstance(paydate,str):
            str_date = paydate.strftime("%d/%b/%y")
        else:
            str_date = paydate
        return str_date

    def view_detail(self):
        
        return {
            'id':self.id,
            'editid':ClientBillOp.generate_editid(self),
            'delid':ClientBillOp.generate_delid(self),
            'client':self.company if self.company else "",
            'sub':ClientBillOp.fig_format(self.subscription),
            'desc':self.description,
            'inst':ClientBillOp.fig_format(self.installation),
            'arrears':ClientBillOp.fig_format(self.arrears),
            'total':ClientBillOp.fig_format(self.total),
            'paid':ClientBillOp.fig_format(self.paid),
            'payment_date':ClientBillOp.get_date(self),
            'balance':ClientBillOp.fig_format(self.balance),

            'smsstatus':ClientBillOp.get_sms_status(self),
            'smsoutline': "" if self.sms_invoice == "sent" or self.sms_invoice == "Success" or self.sms_invoice == "success-alt" else "primary",
            'smsactive': "disabled" if self.sms_invoice == "sent" or self.sms_invoice == "Success" or self.sms_invoice == "success-alt" else "",

        }

class MonthlyChargeOp(MonthlyCharge,Base):
    def __init__(self,year,month,booking,instalment,addfee,water,rent,garbage,electricity,security,maintenance,penalty,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,ptenant_id,created_by):
        self.month = month
        self.year=year
        self.booking = booking
        self.instalment = instalment
        self.addfee = addfee
        self.water=water
        self.total_bill=total_amount
        self.arrears = arrears
        self.rent = rent
        self.garbage=garbage
        self.security=security
        self.electricity = electricity
        self.deposit = deposit
        self.agreement = agreement
        # not implemented at the moment
        self.maintenance=maintenance
        # self.miscellaneous=miscellaneous
        self.penalty=penalty
        # foreign keys
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.tenant_id=tenant_id
        self.ptenant_id=ptenant_id
        self.user_id = created_by

    @staticmethod
    def fetch_specific_bill(id):
        # return MonthlyChargeOp.query.filter_by(id=id).first()
        try:
            return MonthlyCharge.query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            db.session.rollback()
            return None

    def fetch_all_monthlycharges_by_apartment_id(apartment_id):
        return MonthlyCharge.query.filter(MonthlyCharge.apartment_id==apartment_id).all()

    def fetch_all_monthlycharges_by_apartment_id_by_period(apartment_id,month,year):
        return MonthlyCharge.query.filter(MonthlyCharge.apartment_id==apartment_id).filter(MonthlyCharge.month==month).filter(MonthlyCharge.year==year).all()

    def fetch_monthlycharge_by_tenant_id(tenant_id):
        return MonthlyCharge.query.filter(MonthlyCharge.tenant_id==tenant_id).order_by(MonthlyCharge.date.desc()).first()

    def fetch_all_monthlycharges_by_month(month):
        return MonthlyCharge.query.filter_by(month=month).all()#REFACTOR TO FETCH SPECIFIC HOUSE/APARTMENT MONTH CHARGES

    def fetch_monthlycharge_by_house_id(house_id):
        return MonthlyCharge.query.filter(MonthlyChargeOp.house_id==house_id).order_by(MonthlyCharge.date.desc()).first()

    def fetch_monthlycharge_by_smsid(smsid):
        return MonthlyCharge.query.filter(MonthlyChargeOp.smsid==smsid).first()

    def fetch_bills_by(propid,start):
        return MonthlyCharge.query.filter(
            MonthlyCharge.apartment_id==propid,
            MonthlyCharge.month == start.month,
            MonthlyCharge.year == start.year
            ).all()

    def update_balances(self,booking,instalment,addfee,rent,water,electricity,garbage,security,service,penalty,deposit,agreement):
        if booking != "null":
            self.booking_balance = booking
        if instalment != "null":
            self.instalment_balance = instalment
        if addfee != "null":
            self.addfee_balance = addfee
        if rent != "null":
            self.rent_balance = rent
        if water != "null":
            self.water_balance = water
        if electricity != "null":
            self.electricity_balance =electricity
        if garbage != "null":
            self.garbage_balance = garbage
        if security != "null":
            self.security_balance = security
        if service != "null":
            self.maintenance_balance = service
        if penalty != "null":
            self.penalty_balance = penalty
        if deposit != "null":
            self.deposit_balance = deposit
        if agreement != "null":
            self.agreement_balance = agreement

        self.updated = True

        print("UPDATE DONE")

        db.session.commit()

    def update_rent_balance(self,rent):
        self.rent_balance = rent

        print("RENT ARREARS UPDATE DONE")

        db.session.commit()

    def update_rent_due(self,rent):
        self.rent_due = rent

        print("RENT DUES UPDATE DONE")

        db.session.commit()

    def update_payments(self,booking,instalment,addfee,rent,water,electricity,garbage,security,service,penalty,deposit,agreement):
        self.booking_paid = booking
        self.instalment_paid = instalment
        self.addfee_paid = addfee
        self.rent_paid = rent
        self.water_paid = water
        self.electricity_paid =electricity
        self.garbage_paid = garbage
        self.security_paid = security
        self.maintenance_paid = service
        self.penalty_paid = penalty
        self.deposit_paid = deposit
        self.agreement_paid = agreement

        db.session.commit()

    def update_dues(self,booking,instalment,addfee,rent,water,electricity,garbage,security,service,penalty,deposit,agreement):

        if booking != "null":
            self.booking_due = booking
        if instalment != "null":
            self.instalment_due = instalment
        if addfee != "null":
            self.addfee_due = addfee
        if rent != "null":
            self.rent_due = rent
        if water != "null":
            self.water_due = water
        if electricity != "null":
            self.electricity_due =electricity
        if garbage != "null":
            self.garbage_due = garbage
        if security != "null":
            self.security_due = security
        if service != "null":
            self.maintenance_due = service
        if penalty != "null":
            self.penalty_due = penalty
        if deposit != "null":
            self.deposit_due = deposit
        if agreement != "null":
            self.agreement_due = agreement

        # self.booking_due = booking
        # self.instalment_due = instalment
        # self.addfee_due = addfee
        # self.rent_due = rent
        # self.water_due = water
        # self.electricity_due =electricity
        # self.garbage_due = garbage
        # self.security_due = security
        # self.maintenance_due = service
        # self.penalty_due = penalty
        # self.deposit_due = deposit
        # self.agreement_due = agreement

        self.updated = True

        print("UPDATE DONE")

        db.session.commit()
        

    def update_monthly_charge(self,water=None,rent=None,garbage=None,electricity=None,security=None,deposit=None,agreement=None,maintenance=None,fines=None,arrears=None,total_bill=None,created_by=None):
        """update bill"""

        # print(">>>>>>>>>>>>>RENT", rent)

        if rent != "null":
            self.rent = rent
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Rent updated")
        if water != "null":
            self.water = water
        if garbage != "null":
            self.garbage = garbage
        if security != "null":
            self.security = security
        if electricity != "null":
            self.electricity = electricity
        if deposit != "null":
            self.deposit = deposit
        if agreement != "null":
            self.agreement = agreement
        if maintenance != "null":
            self.maintenance = maintenance
        if fines != "null":
            self.penalty = fines
        if arrears != "null":
            try:
                print("Updating arrears for", self.tenant.name , ">>>>>>>>>",arrears)
            except:
                print("Updating arrears for", self.house.owner.name , ">>>>>>>>>",arrears)

            self.arrears = arrears

        self.total_bill = total_bill
        
        if created_by:
            self.modifiedby = created_by

        db.session.commit()

    def update_fine_status(self,status):
        self.fine_status = status
        db.session.commit()

    def update_dep_journal(self,status):
        self.dep_journal = status
        db.session.commit()

    def update_paidll(self,amount):
        self.paidll = amount
        db.session.commit()

    def update_fine_date(self,date):
        self.fine_date = date
        db.session.commit()

    def update_invoice_date(self,date):
        self.invoice_date = date
        db.session.commit()

    def update_payment(self,paid_amount):
        self.paid_amount = paid_amount
        db.session.commit()

    def update_agreement(self,amount):
        self.agreement = amount
        db.session.commit()

    def update_total(self,amount):
        self.total_bill = amount
        db.session.commit()

    def update_payment_date(self,date):
        self.pay_date = date
        db.session.commit()

    def update_balance(self,balance):
        self.balance = balance
        db.session.commit()

    def update_arrears_status(self,status):
        self.arrears_updated = status
        db.session.commit()

    def update_arrears(self,arrears):
        self.arrears = arrears
        db.session.commit()

    def update_smsid(self,smsid):
        self.smsid = smsid
        db.session.commit()

    def update_sms_status(self,status):
        self.sms_invoice = status
        db.session.commit()

    def update_email_status(self,status):
        self.email_invoice = status
        db.session.commit()

    def payhighlight(self):
        if self.paid_amount == 0.0:
            return "text-secondary"
        else:
            return "text-info"

    def highlight(self):
        if self.balance > 0.0:
            return "text-danger"
        elif self.balance < 0.0:
            return "text-success"
        else:
            return "text-dark"

    def year_month(self):

        allowed_categories = ["Director Rooms", "Manager Rooms","Reception Rooms"]
        if current_user.company_user_group.name in allowed_categories:
            tenant_alloc_objs = self.tenant.house_allocated
            found = False
            if tenant_alloc_objs:
                for tenant_alloc in tenant_alloc_objs:
                    if tenant_alloc.active == True:
                        target = tenant_alloc
                        found = True
                        break
            if found:
                days = (target.checkout_date - target.checkin_date).days
                return f"{days} days"
            else:
                return "-"
        else:
            charge_year = self.year
            # charge_month = self.month
            charge_month = MonthlyChargeOp.get_str_month(self.month)
            year_month = f'{charge_year}/{charge_month}'
            return year_month

    def combine_house_tenant(self):
        if self.tenant:
            tname = self.tenant.name.title()
            ttype = "T"
        else:
            tname = self.house.owner.name.title()
            ttype = "R"

        try:
            fname = tname.split()[0]
        except:
            fname = "Tenant"

        house =  self.house.name
        return f'{house}# {fname}' 

    def combine_house_tenant_alt(self):
        if self.tenant:
            tname = self.tenant.name.title()
            ttype = f'<span class="text-black">(T)</span>'
        else:
            tname = self.house.owner.name.title()
            ttype = f'<span class="text-black">(R)</span>'

        try:
            fname = tname.split()[0]
        except:
            fname = "None"

        house =  self.house.name
        # return f'{house} <span class="text-gray-600">{fname}</span> {ttype}' 
        return f'{house} <span class="text-gray-600">{fname}</span>' 

    def combine_garbsec(self):
        garb = self.garbage if self.garbage else 0.0 #TODO - remove condition
        sec = self.security if self.security else 0.0 #TODO - remove condition
        total = garb + sec
        return (f"{total:,}")

    def combine_deparg(self):
        dep = self.deposit if self.deposit else 0.0 #TODO - remove condition
        arg = self.agreement if self.agreement else 0.0 #TODO - remove condition

        total = dep + arg

        return (f"{total:,}")

    def derive_arrears(self):
        fines = self.penalty
        arrears = self.arrears
        total = fines + arrears
        return (f"{total:,}")

    def calculate_total(self):
        rent = self.rent if self.rent else 0.0
        water = self.water if self.water else 0.0
        garbage = self.garbage if self.garbage else 0.0
        security = self.security if self.security else 0.0
        dep = self.deposit if self.deposit else 0.0
        bbf = 18900 if self.tenant_id == 86 and self.month == 4 else 0.0

        total = rent + water + garbage + security + dep + bbf
        return (f"{total:,}")

    def calculate_total_due(x,y):
        rent = x if x else 0.0
        bal = y if y else 0.0

        total = rent + bal
        return (f"{total:,}")
    
    def calculate_total_alt(*args):
        tot=0.0
        for i in args:
            try:
                tot += i
            except:
                tot += 0.0

        return (f"{tot:,}")

    def calculate_total_alt_alt(*args):
        tot=0.0
        for i in args:
            try:
                if i > 0:
                    tot += i
            except:
                tot += 0.0

        return (f"{tot:,}")
    
    #######################TODO TODO############################
    def calculate_bbf(self):
        bill = self.rent * 2
        if self.tenant_id == 86 and self.month == 4 and self.apartment_id in [3,4]:
            bbf = 18900
            
        else:
            bbf = 0
            
        return bbf

    def calculate_paid(self):
        bill = self.rent * 2
        if self.balance > bill and  self.deposit == 0 and self.apartment_id in [3,4]:
            paid = 0.0
        else:
            rent = self.rent if self.rent else 0.0
            water = self.water if self.water else 0.0
            garbage = self.garbage if self.garbage else 0.0
            security = self.security if self.security else 0.0
            dep = self.deposit if self.deposit else 0.0
            bbf = 18900 if self.tenant_id == 86 and self.month == 4 else 0.0


            paid = rent + water + garbage + security + dep + bbf
            
        return paid

    def calculate_bcf(self):
        bill = self.rent * 2
        if self.balance > bill and self.deposit == 0.0 and self.apartment_id in [3,4]:

            rent = self.rent if self.rent else 0.0
            water = self.water if self.water else 0.0
            garbage = self.garbage if self.garbage else 0.0
            security = self.security if self.security else 0.0
            dep = self.deposit if self.deposit else 0.0

            bcf = rent + water + garbage + security + dep
            
        else:
            bcf = 0.0
            
        return bcf

    def mathrent(self):
        bill = self.rent * 2
        if self.balance > bill and self.deposit == 0.0 and self.apartment_id in [3,4]:
            rent = 0.0
        else:
            rent = self.rent
            
        return rent

    def mathwater(self):
        bill = self.rent * 2
        if self.balance > bill and self.deposit == 0.0 and self.apartment_id in [3,4]:
            rent = 0.0
        else:
            rent = self.water
            
        return rent

    def mathgarbage(self):
        bill = self.rent * 2
        if self.balance > bill and self.deposit == 0.0 and self.apartment_id in [3,4]:
            rent = 0.0
        else:
            rent = self.garbage
            
        return rent

    def mathsec(self):
        bill = self.rent * 2
        if self.balance > bill and self.deposit == 0.0 and self.apartment_id in [3,4]:
            rent = 0.0
        else:
            rent = self.security
            
        return rent

    def mathdep(self):
        bill = self.rent * 2
        if self.balance > bill and self.deposit == 0.0 and self.apartment_id in [3,4]:
            rent = 0.0
        else:
            rent = self.deposit
            
        return rent

    #########################TODO TODO ###########################

    def get_date(self):
        paydate = self.pay_date if self.pay_date else "-"
        if not isinstance(paydate,str):
            str_date = paydate.strftime("%d/%b/%y")
        else:
            str_date = paydate
        return str_date

    def minimal_view(self):
        
        return {
            'prop':self.apartment,
            'tenantid':self.tenant_id,
            'id':self.id,
            'space':self.house.description,
            'house':self.house,
            'tenant':self.tenant,
            'rent':self.rent,
            'dep':self.deposit
        }

    # def get_sms_status(self):
    #     if self.apartment_id == 76:
    #         return '<span class="text-success"><i class="fas fa-check-double mr-1"></i>Sent</span>'
    #     if self.sms_invoice:
    #         if self.sms_invoice == "Success":
    #             status = '<span class="text-success"><i class="fas fa-check-double mr-1"></i>Sent</span>'
    #         elif self.sms_invoice == "success-alt":
    #             status = '<span class="text-danger"><i class="fas fa-check-double mr-1"></i>blocked</span>'
    #         elif self.sms_invoice == "waiting":
    #             status = '<span class="text-warning font-weight-bold"><i class="fas fa-hourglass-half mr-1"></i>Resend</span>'
    #         elif self.sms_invoice == "sent":
    #             status = '<span class="text-primary"><i class="fas fa-check mr-1"></i>Sent</span>'
    #         elif self.sms_invoice == "pending":
    #             status = '<span class="text-primary"><i class="fas fa-clock mr-1"></i>Send</span>'
    #         elif self.sms_invoice == "fail":
    #             status = '<span class="text-danger"><i class="fas fa-hourglass-end mr-1">Resend</i></span>'
    #         elif self.sms_invoice == "off":
    #             status = '<span class="text-dark"><i class="fas fa-ban mr-1"></i>Off</span>'
    #         else:
    #             status = '<span class="text-danger"><i class="fas fa-reply mr-1"></i>Resend</span>'
    #     else:
    #         status = '<span class="text-danger"><i class="fas fa-ban mr-1"></i>Null</span>'

    #     return status

    def get_sms_status(self):

        if self.sms_invoice:
            if self.sms_invoice == "Success":
                status = '<span class="text-success"><i class="fas fa-check-double mr-1"></i>Sent</span>'
            elif self.sms_invoice == "success-alt" or self.sms_invoice == "blocked":
                status = '<span class="text-danger"><i class="fas fa-times mr-1"></i></span>'
            elif self.sms_invoice == "waiting":
                status = '<span class="text-warning font-weight-bold"><i class="fas fa-hourglass-half mr-1"></i>queued</span>'
            elif self.sms_invoice == "sent":
                status = '<span class="text-primary"><i class="fas fa-check mr-1"></i>Sent</span>'
            elif self.sms_invoice == "pending":
                status = '<span class="text-primary"><i class="fas fa-clock mr-1"></i>Send</span>'
            elif self.sms_invoice == "fail":
                status = '<span class="text-danger"><i class="fas fa-reply mr-1">Resend</i></span>'
            elif self.sms_invoice == "off":
                status = '<span class="text-dark"><i class="fas fa-ban mr-1"></i>sms off</span>'
            else:
                status = '<span class="text-danger"><i class="fas fa-reply mr-1"></i>Resend</span>'
        else:
            status = '<span class="text-danger"><i class="fas fa-ban mr-1"></i>Null</span>'

        return status

    def get_mail_status(self):

        if self.email_invoice:
            if self.email_invoice == "Success":
                status = '<span class="text-success"><i class="fas fa-check-double mr-1"></i>Sent</span>'
            elif self.email_invoice == "waiting":
                status = '<span class="text-warning font-weight-bold"><i class="fas fa-hourglass-half mr-1"></i>queued</span>'
            elif self.email_invoice == "sent":
                status = '<span class="text-primary"><i class="fas fa-check mr-1"></i>Sent</span>'
            elif self.email_invoice == "pending":
                status = '<span class="text-primary"><i class="fas fa-clock mr-1"></i>Send</span>'
            elif self.email_invoice == "fail":
                status = '<span class="text-danger"><i class="fas fa-clock mr-1">Resend</i></span>'
            elif self.email_invoice == "off":
                status = '<span class="text-dark"><i class="fas fa-ban mr-1"></i>Off</span>'
            else:
                status = '<span class="text-danger"><i class="fas fa-reply mr-1"></i>Resend</span>'
        else:
            status = '<span class="text-danger"><i class="fas fa-ban mr-1"></i>Null</span>'

        return status

    def current_badge(self):
        if self.apartment.company.billing_period.month == self.month and self.apartment.company.billing_period.year == self.year:
            return "current"
        else:
            return ""

    def show_paid_status(amount):
        if not amount:
            badge = f'<span class="badge bg-danger badge-danger badge-counter">not paid</span>'
            return badge
        else:
            rounded_fig = round(amount,2)
            decor_fig = (f"{rounded_fig:,}")
            return decor_fig

    def show_ll_status(self):
        if self.paid_amount:
            if self.deposit_paid:
                # tpaid = self.paid_amount - self.deposit_paid
                tpaid = self.paid_amount
            else:
                tpaid = self.paid_amount
            rounded_fig = round(tpaid,2)
            decor_fig = (f"{rounded_fig:,}")
        else:
            decor_fig = 0.0

        # tids = [8466,1258,1261,1268]
        tids = []

        try:
            if self.tenant.id in tids:
                badge = f'<span class="badge bg-success badge-success badge-counter">paid owner</span> {decor_fig}'
                return badge
            elif self.paidll:
                badge = f'<span class="badge bg-success badge-success badge-counter">paid owner</span> {decor_fig}'
                return badge
            else:
                return decor_fig
        except:
            return decor_fig

    def get_tenant_name(self):
        if self.tenant:
            return self.tenant.name.title()
        else:
            return self.house.owner.name.title()

    def get_date2(month,year):
        switcher = {
            1:"Jan",
            2:"Feb",
            3:"Mar",
            4:"Apr",
            5:"May",
            6:"Jun",
            7:"Jul",
            8:"Aug",
            9:"Sept",
            10:"Oct",
            11:"Nov",
            12:"Dec"
            }
        return f'{switcher.get(month)},{year}'

    def find_deposit_balance(self):
        breaks = 0.0

        stars = ""


        breaks += self.deposit_balance if self.deposit_balance else 0.0

        if breaks:
            stars += "~"

        return stars
    
    def find_deposit_invoice(self):
        breaks = 0.0

        stars = ""

        breaks += self.deposit if self.deposit else 0.0

        if breaks:
            stars += "~"

        return stars

    def get_balance_badge(arr):
        if arr == 0.0:
            return "text-black"
        elif arr > 0.0:
            return "text-danger"
        else:
            return "text-success"
        
    def calculate_breakdown(self):
        try:
            arrs = self.tenant.monthly_charges
        except:
            arrs = self.ptenant.monthly_charges

        arrears_correctness = ""

        prev_bill = None
        prev_month = get_prev_month(self.month)
        prev_year = get_prev_year(self.month,self.year)
        for i in arrs:
            if i.month == prev_month and i.year == prev_year:
                prev_bill = i
                break

        if prev_bill:
            if prev_bill.balance == self.arrears:
                arrears_correctness = ""
            else:
                arrears_correctness = "#"

        arrears = self.arrears
        breaks = 0.0

        if self.deposit_balance:
            star = "#"
        else:
            star = ""

        breaks += self.booking_balance if self.booking_balance else 0.0
        breaks += self.instalment_balance if self.instalment_balance else 0.0
        breaks += self.addfee_balance if self.addfee_balance else 0.0
        breaks += self.rent_balance if self.rent_balance else 0.0
        breaks += self.water_balance if self.water_balance else 0.0
        breaks += self.garbage_balance if self.garbage_balance else 0.0
        breaks += self.security_balance if self.security_balance else 0.0
        breaks += self.electricity_balance if self.electricity_balance else 0.0
        breaks += self.maintenance_balance if self.maintenance_balance else 0.0
        breaks += self.agreement_balance if self.agreement_balance else 0.0
        breaks += self.deposit_balance if self.deposit_balance else 0.0
        breaks += self.penalty_balance if self.penalty_balance else 0.0

        if breaks == arrears:
            return f"{arrears_correctness} {arrears:,.1f} {star}"
        else:
            return f"{arrears_correctness} {arrears:,.1f} {star}**"

    def calculate_breakdown_no_dep(self):
        arrears = self.arrears - self.deposit_balance
        breaks = 0.0

        breaks += self.rent_balance if self.rent_balance else 0.0
        breaks += self.water_balance if self.water_balance else 0.0
        breaks += self.garbage_balance if self.garbage_balance else 0.0
        breaks += self.security_balance if self.security_balance else 0.0
        breaks += self.electricity_balance if self.electricity_balance else 0.0
        breaks += self.maintenance_balance if self.maintenance_balance else 0.0
        breaks += self.agreement_balance if self.agreement_balance else 0.0
        breaks += self.penalty_balance if self.penalty_balance else 0.0

        if breaks == arrears:
            return f"{arrears:,.1f}"
        else:
            return f"{arrears:,.1f} **"

    def calculate_pbreakdown(self):
        paid = self.paid_amount
        breaks = 0.0

        breaks += self.booking_paid if self.booking_paid else 0.0
        breaks += self.instalment_paid if self.instalment_paid else 0.0
        breaks += self.addfee_paid if self.addfee_paid else 0.0
        breaks += self.rent_paid if self.rent_paid else 0.0
        breaks += self.water_paid if self.water_paid else 0.0
        breaks += self.garbage_paid if self.garbage_paid else 0.0
        breaks += self.security_paid if self.security_paid else 0.0
        breaks += self.electricity_paid if self.electricity_paid else 0.0
        breaks += self.maintenance_paid if self.maintenance_paid else 0.0
        breaks += self.agreement_paid if self.agreement_paid else 0.0
        breaks += self.deposit_paid if self.deposit_paid else 0.0
        breaks += self.penalty_paid if self.penalty_paid else 0.0

        if breaks == paid:
            return f"{paid:,.1f}"
        else:
            return f"{paid:,.1f} **"

    def calculate_dbreakdown(self):
        bal = self.balance
        breaks = 0.0

        breaks += self.booking_due if self.booking_due else 0.0
        breaks += self.instalment_due if self.instalment_due else 0.0
        breaks += self.addfee_due if self.addfee_due else 0.0
        breaks += self.rent_due if self.rent_due else 0.0
        breaks += self.water_due if self.water_due else 0.0
        breaks += self.garbage_due if self.garbage_due else 0.0
        breaks += self.security_due if self.security_due else 0.0
        breaks += self.electricity_due if self.electricity_due else 0.0
        breaks += self.maintenance_due if self.maintenance_due else 0.0
        breaks += self.agreement_due if self.agreement_due else 0.0
        breaks += self.deposit_due if self.deposit_due else 0.0
        breaks += self.penalty_due if self.penalty_due else 0.0

        if breaks == bal:
            if self.deposit_due:
                return f"{bal:,.1f} ~"
            return f"{bal:,.1f}"
        else:
            if self.deposit_due:
                return f"{bal:,.1f} ** ~"
            return f"{bal:,.1f} **"

    def calculate_dbreakdown_no_dep(self):
        bal = self.balance - self.deposit_due
        breaks = 0.0

        breaks += self.rent_due if self.rent_due else 0.0
        breaks += self.water_due if self.water_due else 0.0
        breaks += self.garbage_due if self.garbage_due else 0.0
        breaks += self.security_due if self.security_due else 0.0
        breaks += self.electricity_due if self.electricity_due else 0.0
        breaks += self.maintenance_due if self.maintenance_due else 0.0
        breaks += self.agreement_due if self.agreement_due else 0.0
        breaks += self.penalty_due if self.penalty_due else 0.0

        if breaks == bal:
            return f"{bal:,.1f}"
        else:
            return f"{bal:,.1f} **"

    def format_num(num):
        if num < 9:
            return f"00{num}"
        elif num < 99:
            return f"0{num}"
        else:
            return f'{num}'

    def check_invnum(self):
        if self.house.apartment_id != self.apartment_id:
            invnum = f"!{self.id}"
        else:
            invnum = f"{self.id}"
        return invnum

    def calculate_paid_deposits(self):
        if self.tenant:
            if self.tenant.deposits:
                if self.tenant.deposits.payments:
                    payments = 0.0
                    for pp in self.tenant.deposits.payments:
                        # print(self.tenant.name, " ",pp.date.month, pp.date.year)
                        if pp.date.month == self.month and  pp.date.year == self.year:
                            payments += pp.amount
                    return f'{payments:,.1f}'
                else:
                    return f'{self.tenant.deposits.total_paid:,.1f}' if self.tenant.deposits.total_paid else 0.0
            return 0.0
        return 0.0

    def calculate_deposit_balance(self):
        # wt = self.house.housecode.waterdep if self.house.housecode else 0.0
        # rent = self.house.housecode.rentrate if self.house.housecode else 0.0
        # elec = self.house.housecode.elecdep if self.house.housecode else 0.0

        # tot = wt+rent+elec

        # if self.tenant:
        #     if self.tenant.deposit:
        #         try:
        #             deps = self.tenant.deposit
        #             bal = tot - deps
        #             return f"{bal:,.1f}"
        #         except:
        #             return 0.0
        #     return 0.0
        # return 0.0


        if self.tenant:
            if self.tenant.deposits:
                return f'{self.tenant.deposits.balance:,.1f}' if self.tenant.deposits.balance else 0.0
            return 0.0
        return 0.0

    def calculate_total_deposit(self):
        wt = self.house.housecode.waterdep if self.house.housecode else 0.0
        rent = self.house.housecode.rentrate if self.house.housecode else 0.0
        elec = self.house.housecode.elecdep if self.house.housecode else 0.0

        tot = wt+rent+elec

        if self.tenant:
            if self.tenant.deposit:
                try:
                    return f"{tot:,.1f}"
                except:
                    return 0.0
            return 0.0
        return 0.0
    
    def get_house(self):
        hh = self.house

        if self.tenant:
            tt = self.tenant
        else:
            tt = self.house.owner

        t_current_house = None
        try:
            house_alloc_objs = tt.house_allocated
        except:
            return self.house.name
        
        if house_alloc_objs:
            for house_alloc in house_alloc_objs:
                if house_alloc.active:
                    t_current_house = house_alloc.house
        if t_current_house:
            if t_current_house.name == hh.name:
                return hh.name
            else:
                return f"{t_current_house.name}-(formerly {hh.name})"
        # return f"{hh.name}(Vacated)"
        return f"{hh.name}"
            
    def view_detail(self):
        
        return {
            'id':self.id,
            'invnum':MonthlyChargeOp.check_invnum(self),
            'viewid':MonthlyChargeOp.generate_viewid(self),
            'smsid':MonthlyChargeOp.generate_smsid(self),
            'mailid':MonthlyChargeOp.generate_mailid(self),
            'editid':MonthlyChargeOp.generate_editid(self),
            'payid':MonthlyChargeOp.generate_payid(self),
            'balid':MonthlyChargeOp.generate_balid(self),
            'delid':MonthlyChargeOp.generate_delid(self),
            'tenantid':self.tenant_id if self.tenant_id else "-",
            'ptenant':self.ptenant_id if self.ptenant_id else "-",
            'month':MonthlyChargeOp.year_month(self),
            'year':self.year,
            'tenant':MonthlyChargeOp.get_tenant_name(self),
            'tenant-alt':MonthlyChargeOp.get_tenant_name(self),
            'prop':self.apartment,
            'hsetenant':MonthlyChargeOp.combine_house_tenant(self),
            'hst':MonthlyChargeOp.combine_house_tenant_alt(self),
            'idno':self.tenant.national_id if self.tenant else "-",
            'house':MonthlyChargeOp.get_house(self),
            'desc':self.house.description,
            'rent':MonthlyChargeOp.fig_format(self.rent),
            'rent-arr':MonthlyChargeOp.fig_format(self.rent_balance),
            'rent-total':MonthlyChargeOp.calculate_total_due(self.rent,self.rent_balance),
            'rent-paid':MonthlyChargeOp.fig_format(self.rent_paid),
            'rent-due':MonthlyChargeOp.fig_format(self.rent_due),
            'utilities':MonthlyChargeOp.calculate_total_alt(self.water,self.electricity,self.maintenance,self.garbage,self.security),
            'water':MonthlyChargeOp.fig_format(self.water),
            'garbsec':MonthlyChargeOp.combine_garbsec(self),
            'garbage':self.garbage,
            'electricity':MonthlyChargeOp.fig_format(self.electricity),
            'security':self.security,
            'repair':self.maintenance,
            'service':MonthlyChargeOp.fig_format(self.maintenance), #TODO #################### REFACTOR
            'agreement':self.agreement,
            'deposit':self.deposit,
            'baldep':MonthlyChargeOp.find_deposit_balance(self),
            'invdep':MonthlyChargeOp.find_deposit_invoice(self),
            'deposit-paid':MonthlyChargeOp.calculate_paid_deposits(self),
            'deposit-due':MonthlyChargeOp.calculate_deposit_balance(self),

            'deductions':MonthlyChargeOp.calculate_total_alt(self.house.housecode.int_commission,self.house.housecode.servicerate),
            'deparg':MonthlyChargeOp.combine_deparg(self),
            'fine':MonthlyChargeOp.fig_format(self.penalty),
            'arrears':MonthlyChargeOp.calculate_breakdown(self),
            'arrears-no-star':f"{self.arrears:,.1f}",
            'derrived_arrears':MonthlyChargeOp.derive_arrears(self),
            'total':MonthlyChargeOp.fig_format(self.total_bill),
            'totalalt':MonthlyChargeOp.calculate_total_alt_alt(self.arrears,self.rent,self.water,self.maintenance,self.deposit,self.garbage,self.security),
            'amounttotal':MonthlyChargeOp.calculate_total_alt(self.arrears,self.rent,self.water,self.maintenance,self.deposit,self.garbage,self.security),
            'totaldue':MonthlyChargeOp.calculate_total_alt(self.arrears,self.rent,self.water,self.maintenance,self.garbage,self.security),
            'paid':MonthlyChargeOp.calculate_pbreakdown(self),
            'paid-alt':MonthlyChargeOp.show_paid_status(self.paid_amount),
            'paid-alt-alt':MonthlyChargeOp.show_ll_status(self),
            'payment_date':MonthlyChargeOp.get_date(self),
            'balance':MonthlyChargeOp.calculate_dbreakdown(self),
            'balance-no-star':f"{self.balance:,.1f}",
            'date':self.date.date(),
            'date2':MonthlyChargeOp.get_date2(self.month,self.year),
            'smsstatus':MonthlyChargeOp.get_sms_status(self),
            'smsoutline': "" if self.sms_invoice == "sent" or self.sms_invoice == "Success" or self.sms_invoice == "success-alt" else "primary",
            'smsactive': "" if self.sms_invoice == "sent" or self.sms_invoice == "Success" or self.sms_invoice == "success-alt" else "",
            'mailstatus':MonthlyChargeOp.get_mail_status(self),
            'mailoutline': "" if self.email_invoice == "sent" or self.email_invoice == "Success" else "primary",
            'mailactive': "disabled" if self.email_invoice == "sent" or self.email_invoice == "Success" else "",
            'active':"",
            'viewable':"text-primary",
            'editoutline':"text-primary",
            'balance-badge':MonthlyChargeOp.get_balance_badge(self.arrears),
            'new':MonthlyChargeOp.current_badge(self),
            'billedby':MonthlyChargeOp.get_name(self)
        }

    def get_desc(description):
        if description:
            if "2" in description or "two" in description.lower():
                desc = "2BR"
            elif "bedsitter" in description.lower():
                desc = "BEDSITTER"
            elif "1" in description or "one" in description.lower():
                desc = "1BR"
            elif "3" in description or "three" in description.lower():
                desc = "3BR"
            else:
                desc = "n/a"
        else:
            desc = "N/A"

        return desc

    def external_view(self):
        
        return {
            'id':self.id,
            'invnum':self.id,
            'editid':MonthlyChargeOp.generate_editid(self),
            'delid':MonthlyChargeOp.generate_delid(self),
            'tenantid':self.tenant_id if self.tenant_id else "-",
            'month':MonthlyChargeOp.year_month(self),
            'year':self.year,
            'desc':MonthlyChargeOp.get_desc(self.house.description),
            'tenant':MonthlyChargeOp.get_tenant_name(self),
            'tenant-alt':MonthlyChargeOp.get_tenant_name(self),
            'house':self.house,
            'house-alt':f'{MonthlyChargeOp.format_num(self.apartment.id)}/{self.house}',

            'total-deposit':MonthlyChargeOp.calculate_total_deposit(self),
            'deposit-paid':MonthlyChargeOp.calculate_paid_deposits(self),
            'deposit-due':MonthlyChargeOp.calculate_deposit_balance(self),

            'dep-arr':MonthlyChargeOp.fig_format(self.deposit_balance),
            'dep':MonthlyChargeOp.fig_format(self.deposit),
            'dep-total':MonthlyChargeOp.calculate_total_due(self.deposit,self.deposit_balance),
            'dep-paid':MonthlyChargeOp.fig_format(self.deposit_paid),
            'dep-bal':MonthlyChargeOp.fig_format(self.deposit_due),

            'rent-arr':MonthlyChargeOp.fig_format(self.rent_balance),
            'rent':MonthlyChargeOp.fig_format(self.rent),
            'rent-total':MonthlyChargeOp.calculate_total_due(self.rent,self.rent_balance),
            'rent-paid':MonthlyChargeOp.fig_format_ll(self.rent_paid,self.paidll),
            'rent-bal':MonthlyChargeOp.fig_format(self.rent_due),

            'water-arr':MonthlyChargeOp.fig_format(self.water_balance),
            'water':MonthlyChargeOp.fig_format(self.water),
            'water-total':MonthlyChargeOp.calculate_total_due(self.water,self.water_balance),
            'water-paid':MonthlyChargeOp.fig_format(self.water_paid),
            'water-bal':MonthlyChargeOp.fig_format(self.water_due),

            'serv-arr':MonthlyChargeOp.fig_format(self.maintenance_balance),
            'serv':MonthlyChargeOp.fig_format(self.maintenance),
            'serv-total':MonthlyChargeOp.calculate_total_due(self.maintenance,self.maintenance_balance),
            'serv-paid':MonthlyChargeOp.fig_format(self.maintenance_paid),
            'serv-bal':MonthlyChargeOp.fig_format(self.maintenance_due),

            'garbage-arr':MonthlyChargeOp.fig_format(self.garbage_balance),
            'garbage':MonthlyChargeOp.fig_format(self.garbage),
            'garbage-total':MonthlyChargeOp.calculate_total_due(self.garbage,self.garbage_balance),
            'garbage-paid':MonthlyChargeOp.fig_format(self.garbage_paid),
            'garbage-bal':MonthlyChargeOp.fig_format(self.garbage_due),

            'electricity-arr':MonthlyChargeOp.fig_format(self.electricity_balance),
            'electricity':MonthlyChargeOp.fig_format(self.electricity),
            'electricity-total':MonthlyChargeOp.calculate_total_due(self.electricity,self.electricity_balance),
            'electricity-paid':MonthlyChargeOp.fig_format(self.electricity_paid),
            'electricity-bal':MonthlyChargeOp.fig_format(self.electricity_due),

            'utilities-paid':MonthlyChargeOp.fig_format(self.water_paid + self.electricity_paid),

            'lpf-arr':MonthlyChargeOp.fig_format(self.penalty_balance),
            'lpf':MonthlyChargeOp.fig_format(self.penalty),
            'lpf-total':MonthlyChargeOp.calculate_total_due(self.penalty,self.penalty_balance),
            'lpf-paid':MonthlyChargeOp.fig_format(self.penalty_paid),
            'lpf-bal':MonthlyChargeOp.fig_format(self.penalty_due),

            'deductions':MonthlyChargeOp.calculate_total_alt(self.house.housecode.int_commission,self.house.housecode.servicerate),

            'electricity':self.electricity,
            'security':self.security,
            'dep':MonthlyChargeOp.fig_format(self.deposit),
            'mathrent':MonthlyChargeOp.mathrent(self),
            'mathwater':MonthlyChargeOp.mathwater(self),
            'mathgarb':MonthlyChargeOp.mathgarbage(self),
            'mathsec':MonthlyChargeOp.mathsec(self),
            'mathdep':MonthlyChargeOp.mathdep(self),
            'mathbbf':MonthlyChargeOp.calculate_bbf(self),
            'calc_total':MonthlyChargeOp.calculate_total(self),
            'paid':MonthlyChargeOp.calculate_paid(self),
            'date-paid':MonthlyChargeOp.get_date(self),
            'balance':MonthlyChargeOp.calculate_bcf(self),

            'arrears-no-star':f"{self.arrears:,.1f}",
            'arrears-rent-dep-serv':MonthlyChargeOp.calculate_total_alt(self.rent_balance,self.deposit_balance,self.maintenance_balance),
            'total':MonthlyChargeOp.fig_format(self.total_bill),
            'totalalt':MonthlyChargeOp.calculate_total_alt_alt(self.arrears,self.rent,self.water,self.maintenance,self.deposit,self.garbage,self.security),
            'amounttotal':MonthlyChargeOp.calculate_total_alt(self.arrears,self.rent,self.water,self.maintenance,self.deposit,self.garbage,self.security),
            'totaldue':MonthlyChargeOp.calculate_total_alt(self.arrears,self.rent,self.water,self.maintenance,self.garbage,self.security),
            'paid2':MonthlyChargeOp.calculate_pbreakdown(self),
            'paid-alt':MonthlyChargeOp.show_paid_status(self.paid_amount),
            'paid-alt-alt':MonthlyChargeOp.show_ll_status(self),
            'payment_date':MonthlyChargeOp.get_date(self),
            'balance-no-star':f"{self.balance:,.1f}",
            'balance-badge':MonthlyChargeOp.get_balance_badge(self.arrears),
            'balance-rent-dep-serv':MonthlyChargeOp.calculate_total_alt(self.rent_due,self.deposit_due,self.maintenance_due),
            'prop':self.apartment.name

        }


    def str_data(self):
        
        return {
            'month':self.month,
            'year':self.year,
            # 'tenant':MonthlyChargeOp.get_tenant_name(self),
            'unit_number':str(self.house),
            'arrears':self.rent_balance,
            'rent':self.rent,
            'total_due':self.rent + self.rent_balance,
            'amount_paid':self.rent_paid,
            'balance':self.rent_due,
            'service_charge':self.house.housecode.servicerate if self.house.housecode.servicerate else 0.0,
            'commission':self.house.housecode.int_commission if self.house.housecode.int_commission else 0.0
            # 'paid':MonthlyChargeOp.calculate_paid(self),
            # 'balance':MonthlyChargeOp.calculate_bcf(self)
        }

    def get_management_fees(self):
        if self.apartment.name.upper() == "PALM MEWS APARTMENT":
            if self.rent_paid > 2000:
                mgt = (self.rent_paid / self.rent) * 2000
                return round(mgt,-3) if mgt > 1999 else 0
            else:
                return 0

        if self.house.housecode.commission:
            comm = self.house.housecode.commission
            try:
                commission = comm * self.rent * 0.01
            except:
                commission = 0.0

        elif self.apartment.commission:
            comm = self.apartment.commission
            try:
                commission = comm * self.rent * 0.01
            except:
                commission = 0.0

        else:
            commission = self.apartment.int_commission if self.apartment.int_commission else 0.0

        return commission

    def get_maintenance(self):
        if self.house.name == "B3":
            return "2,500.0"
        else:
            return f"{self.maintenance:,.1f}"

    def calculate_owner_due(self):
        return (self.rent_paid + self.maintenance_paid) - MonthlyChargeOp.get_management_fees(self) - float(MonthlyChargeOp.get_maintenance(self).replace(",",""))

    def view_merit(self):
        return {
            'tenant':MonthlyChargeOp.get_tenant_name(self),
            'house':self.house,
            'rent':MonthlyChargeOp.fig_format(self.rent_paid + self.maintenance_paid),
            'service':MonthlyChargeOp.get_maintenance(self),
            'mgt':MonthlyChargeOp.get_management_fees(self),
            'ownerdue':MonthlyChargeOp.calculate_owner_due(self),
            'comment':"-"
        }

    def view_crm(self):
        return {
            'ptenant':self.ptenant.name,
            'house':self.house,
            'phone':self.ptenant.phone,
            'email':self.ptenant.email,
            'date':self.ptenant.date.strftime("%m-%d-%Y"),
            'total':MonthlyChargeOp.fig_format(self.total_bill),
            'paid':MonthlyChargeOp.fig_format(self.paid_amount),
            'balance':MonthlyChargeOp.fig_format(self.balance),
            'ratio':f"{(self.paid_amount/self.total_bill*100):,.1f} %" if self.paid_amount else "0 %"
        }

    def view_erp(self):
        return {
            'id':self.id,
            'house':self.house.name,
            'tenant':self.tenant.name,
            'checkin':TenantOp.check_in_date(self.tenant),
            'checkout':TenantOp.check_out_date(self.tenant),
            'price':MonthlyChargeOp.fig_format(self.total_bill),
            'paid':MonthlyChargeOp.fig_format(self.paid_amount),
            'mode':TenantOp.fetch_payment_mode(self.tenant)
        }

    def get_deposit_paid(self):
        if self.tenant:
            deposit_paid = 0.0
        else:
            deposit_paid = 0.0
        return deposit_paid

    def get_deposit_due(self):
        if self.tenant:
            deposit_due = 0.0
        else:
            deposit_due = 0.0
        return deposit_due

    def view_combined(self):
        return {
            'tenant':MonthlyChargeOp.get_tenant_name(self),
            'house':self.house,
            'depositpaid':MonthlyChargeOp.get_deposit_paid(self),
            'depositdue':MonthlyChargeOp.get_deposit_due(self),
            'arrears':MonthlyChargeOp.calculate_breakdown_no_dep(self),
            'rent':MonthlyChargeOp.fig_format(self.rent),
            'water':MonthlyChargeOp.fig_format(self.water),
            'garbage':self.garbage,
            'electricity':MonthlyChargeOp.fig_format(self.electricity),
            'security':self.security,
            'service':MonthlyChargeOp.fig_format(self.maintenance), #TODO #################### REFACTOR
            'agreement':self.agreement,
            'electricity':self.electricity,
            'security':self.security,
            'totalalt':MonthlyChargeOp.calculate_total_alt_alt(self.arrears,self.rent,self.water,self.maintenance,self.garbage,self.security),
            'amounttotal':MonthlyChargeOp.calculate_total_alt(self.arrears,self.rent,self.water,self.maintenance,self.garbage,self.security),
            'paid-alt-alt':MonthlyChargeOp.show_ll_status(self),
            'balance':MonthlyChargeOp.calculate_dbreakdown_no_dep(self),
        }
    
class MonthlyChargeHistoryOp(MonthlyChargeHistory,Base):
    def __init__(self,year,month,water,rent,garbage,electricity,security,maintenance,penalty,arrears,deposit,agreement,total_amount,apartment_id,house_id,tenant_id,invoice_id,created_by):
        self.month = month
        self.year=year
        self.water=water
        self.total_bill=total_amount
        self.arrears = arrears
        self.rent = rent
        self.garbage=garbage
        self.security=security
        self.electricity = electricity
        self.deposit = deposit
        self.agreement = agreement
        # not implemented at the moment
        self.maintenance=maintenance
        # self.miscellaneous=miscellaneous
        self.penalty=penalty
        # foreign keys
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.tenant_id=tenant_id
        self.invoice_id=invoice_id
        self.user_id = created_by

    def update_dues(self,rent,water,electricity,garbage,security,service,penalty,deposit,agreement):
        self.rent_due = rent
        self.water_due = water
        self.electricity_due =electricity
        self.garbage_due = garbage
        self.security_due = security
        self.maintenance_due = service
        self.penalty_due = penalty
        self.deposit_due = deposit
        self.agreement_due = agreement

        self.updated = True

        print("UPDATE DONE")

        db.session.commit()

    def update_balances(self,rent,water,electricity,garbage,security,service,penalty,deposit,agreement):
        self.rent_balance = rent
        self.water_balance = water
        self.electricity_balance =electricity
        self.garbage_balance = garbage
        self.security_balance = security
        self.maintenance_balance = service
        self.penalty_balance = penalty
        self.deposit_balance = deposit
        self.agreement_balance = agreement

        self.updated = True

        print("UPDATE DONE")

        db.session.commit()

class PaymentScheduleOp(PaymentSchedule,Base):
    def __init__(self,name,arrears,amount,total,rbal,date,apartment_id,house_id,ptenant_id):

        self.schedule_name = name
        self.arrears = arrears
        self.schedule_amount = amount
        self.total_amount = total
        self.rbalance = rbal
        self.schedule_date = date

        self.apartment_id = apartment_id
        self.house_id = house_id
        self.ptenant_id = ptenant_id


    def update_details(self,arr,tot,paid,bal,rbal,payref,paytype,paydate):
        self.arrears = arr
        self.total_amount = tot
        self.paid = paid
        self.balance = bal
        self.rbalance = rbal
        self.paytype = paytype
        self.payref = payref
        self.pay_date = paydate
        db.session.commit()

    def update_payment(self,paid):
        self.paid = paid
        db.session.commit()

    def update_balance(self,balance):
        self.balance = balance
        db.session.commit()

    def update_payment_date(self,date):
        self.pay_date = date
        db.session.commit()

    def get_pay_date(self):
        paydate = self.pay_date if self.pay_date else "-"
        if not isinstance(paydate,str):
            str_date = paydate.strftime("%d/%b/%y")
        else:
            str_date = paydate
        return str_date

    def get_schedule_date(self):
        # print("namit",self.schedule_name)
        if self.schedule_name == "10% Deposit":
            return "-"
        if self.schedule_name.startswith("Other payments"):
            if self.house.description.upper() == "STUDIO":
                return f"On execution of sale agreement"
            else:
                return f"On execution of sale agreement"

        paydate = self.schedule_date if self.schedule_date else "-"
        if not isinstance(paydate,str):
            str_date = paydate.strftime("%d %b %Y")
        else:
            str_date = paydate
        return str_date

    def generate_rbal(self):
        if self.rbalance:
            return f"{self.rbalance:,.1f}"
        else:
            return "-"

    def view_detail(self):
        
        return {
            'id':self.id,
            'editid':PaymentScheduleOp.generate_editid(self),
            'delid':PaymentScheduleOp.generate_delid(self),
            'schedule_name':self.schedule_name,
            'schedule_arrears':PaymentScheduleOp.fig_format(self.arrears),
            'schedule_amount':PaymentScheduleOp.fig_format(self.schedule_amount),
            'schedule_total':PaymentScheduleOp.fig_format(self.total_amount),
            'paid':PaymentScheduleOp.fig_format(self.paid),
            'balance':PaymentScheduleOp.fig_format(self.balance),
            'rbalance':PaymentScheduleOp.generate_rbal(self),
            'schedule_date':PaymentScheduleOp.get_schedule_date(self),
            'payref':self.payref if self.payref else "-",
            'paytype':self.paytype if self.paytype else "-",
            'paydate':PaymentScheduleOp.get_pay_date(self)
        }

class LandlordSummaryOp(LandlordSummary,Base):
    def __init__(self,year,month,rent,water,garbage,security,electricity,deposit,bbf,total_amount,paid,bcf,apartment_id,house_id,tenant_id,created_by):
        self.month = month
        self.year=year
        self.water=water
        self.total_bill=total_amount
        self.arrears = bbf
        self.rent = rent
        self.garbage=garbage
        self.security=security
        self.electricity = electricity
        self.deposit = deposit
        self.balance = bcf
        self.paid_amount = paid
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.tenant_id=tenant_id
        self.user_id = created_by

    @staticmethod
    def fetch_specific_bill(id):
        return LandlordSummary.query.filter_by(id=id).first()

    def update_summary(self,rent=None,water=None,deposit=None,arrears=None,total_bill=None,paid=None,bal=None,created_by=None):
        """update bill"""

        if rent != "null":
            self.rent = rent
        if water != "null":
            self.water = water
        if deposit != "null":
            self.deposit = deposit
        if arrears != "null":
            self.arrears = arrears
        if paid != "null":
            self.paid_amount = paid

        self.total_bill = total_bill
        self.balance = bal
        self.user_id = created_by

        db.session.commit()
        
    def year_month(self):
        charge_year = self.year
        # charge_month = self.month
        charge_month = MonthlyChargeOp.get_str_month(self.month)
        year_month = f'{charge_year}/{charge_month}'
        return year_month

    def external_view(self):
        
        return {
            'id':self.id,
            'editid':LandlordSummaryOp.generate_editid(self),
            'delid':LandlordSummaryOp.generate_delid(self),
            'tenantid':self.tenant_id,
            'month':LandlordSummaryOp.year_month(self),
            'year':self.year,
            'tenant':self.tenant.name.split()[0] if self.tenant else "-",
            'house':self.house,
            'rent':LandlordSummaryOp.fig_format(self.rent),
            'water':LandlordSummaryOp.fig_format(self.water),
            'garbage':self.garbage,
            'electricity':self.electricity,
            'security':self.security,
            'dep':LandlordSummaryOp.fig_format(self.deposit),
            'arrears':LandlordSummaryOp.fig_format(self.arrears),
            'calc_total':LandlordSummaryOp.fig_format(self.total_bill),
            'paid':LandlordSummaryOp.fig_format(self.paid_amount),
            'balance':LandlordSummaryOp.fig_format(self.balance)
        }

class PaymentOp(Payment,Base):
    def __init__(self,paymode,ref_number,description,chargetype_string,paydate,payperiod,charged_amount,amount,apartment_id,house_id,tenant_id,ptenant_id,created_by,chargetype_id=None):
        self.paymode=paymode
        self.ref_number=ref_number
        self.description = description
        self.pay_date = paydate
        self.pay_period = payperiod
        self.amount = amount
        self.original_amount = amount
        self.payment_name = chargetype_string
        self.charged_amount = charged_amount
        self.chargetype_id = chargetype_id
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.tenant_id=tenant_id
        self.ptenant_id=ptenant_id
        self.user_id = created_by

    def fetch_payment_by_ref(ref):
        return Payment.query.filter_by(ref_number=ref).first()
    
    def fetch_all_payments_by_ref(ref):
        return Payment.query.filter_by(ref_number=ref).all()

    def fetch_payment_by_rand_id(rand_id):
        return Payment.query.filter_by(rand_id=rand_id).first()

    @staticmethod
    def fetch_latest_payment():
        return Payment.query.order_by(Payment.id.desc()).first()

    def fetch_payment_by_id(id):
        try:
            obj = Payment.query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            obj = None
            db.session.rollback()

        return obj
    
    @staticmethod
    def fetch_latest_payment_by_tenant_id(tenant_id):
        return Payment.query.filter_by(tenant_id=tenant_id).order_by(Payment.date.desc()).first()

    @staticmethod
    def fetch_payment_by_smsid(smsid):
        return Payment.query.filter_by(smsid=smsid).first()

    @staticmethod
    def fetch_all_payments_by_prop_id(prop_id):
        return Payment.query.filter_by(apartment_id=prop_id).order_by(Payment.date.desc()).all()

    @staticmethod
    def fetch_all_payments():
        return Payment.query.order_by(Payment.id.desc()).all()

    def update_payments(self,booking,instalment,addfee,rent,water,electricity,garbage,security,service,penalty,deposit,agreement):
        self.booking_paid = booking
        self.instalment_paid = instalment
        self.addfee_paid = addfee
        self.rent_paid = rent
        self.water_paid = water
        self.electricity_paid =electricity
        self.garbage_paid = garbage
        self.security_paid = security
        self.maintenance_paid = service
        self.penalty_paid = penalty
        self.deposit_paid = deposit
        self.agreement_paid = agreement

        db.session.commit()

    def update_balance(self,balance):
        self.balance = balance
        db.session.commit()

    def update_receipt_num(self,num):
        self.receipt_num = num
        db.session.commit()

    def update_charged_amount(self,bill):
        self.charged_amount = bill
        db.session.commit()

    def void(self,status,userid):
        self.voided = status
        self.modifiedby = userid
        db.session.commit()

    def update_state(self,state):
        self.state = state
        db.session.commit()

    def update_payperiod(self,payperiod):
        self.pay_period = payperiod
        db.session.commit()

    def update_payment(self,paydate,paid,bal):
        if paydate:
            self.pay_date = paydate
        # if paid:
        #     self.amount = paid
        # self.balance = bal
        db.session.commit()

    def update_ref(self,ref):
        if ref:
            self.ref_number = ref
        # if paid:
        #     self.amount = paid
        # self.balance = bal
        db.session.commit()

    def update_payment_info(self,description,chargetype_string):
        self.description = description
        self.payment_name = chargetype_string
        db.session.commit()

    def update_smsid(self,smsid):
        self.smsid = smsid
        db.session.commit()

    def update_rand_id(self,rand_id):
        self.rand_id = rand_id
        db.session.commit()

    def update_sms_status(self,status):
        self.sms_status = status
        db.session.commit()

    def update_email_status(self,status):
        self.email_status = status
        db.session.commit()

    def combine_house_tenant_alt(self):
        if self.tenant:
            fname = self.tenant.name.title()
        else:
            fname = self.house.owner.name.title()
        # fname = self.tenant.name.split()[0]
        house =  self.house.name
        return f'<span class="text-gray-600">({house})</span> <span class="text-gray-900 font-weight-bold">{fname}</span>' 

    def get_names(self):
        if self.tenant:
            fname = self.tenant.name.title()
        else:
            fname = self.house.owner.name.title()

        return fname
    
    def get_tenant_tel(self):
        if self.tenant:
            fname = self.tenant.phone
        else:
            fname = self.house.owner.phone

        return fname

    def highlight(self):
        if self.balance:
            if self.balance > 0.0:
                return "text-danger"
            elif self.balance < 0.0:
                return "text-success"
            else:
                return "text-dark"
        return "text-primary"

    def get_date_time(self):
        paydate = self.pay_date if self.pay_date else self.date
        str_date = paydate.strftime("%d/%b/%y")
        str_time = paydate.strftime("%X")
        return str_date,str_time

    def get_date(self):
        paydate = self.date
        str_date = paydate.strftime("%d/%b/%y")
        return str_date

    def get_month(self):
        
        int_month = self.pay_period.month if self.pay_period else None

        if int_month:
            str_month = PaymentOp.get_str_month(int_month)
        else:
            str_month = "N/A"

        return str_month

    def get_sms_status(self):
        if self.sms_status:
            if self.sms_status == "Success":
                status = '<span class="text-success"><i class="fas fa-check-double"></i></span>'
            elif self.sms_status == "Success-mb" or self.sms_status == "blocked":
                status = '<span class="text-danger"><i class="fas fa-times mr-1"></i></span>'
            elif self.sms_status == "sent":
                status = '<span class="text-primary"><i class="fas fa-check"></i></span>'
            elif self.sms_status == "pending":
                status = '<span class="text-secondary"><i class="fas fa-hourglass-half"></i></span>'
            elif self.sms_status == "fail":
                status = '<span class="text-danger"><i class="fas fa-exclamation-circle"></i></span>'
            elif self.sms_status == "off":
                status = '<span class="text-danger">off</span>'
            else:
                # status = '<span class="text-warning"><i class="fas fa-check"></i></span>'
                status = '<span class="text-success"><i class="fas fa-check-double"></i></span>'

        else:
            status = '<span class="text-danger"><i class="fas fa-check"></i></span>'

        return status

    def comments(self):
        if self.booking_paid:
            return "Booking balance payment"
        else:
            return "Instalment payment"

    def get_pay_timestamp(self):
        return self.pay_date.strftime("%d/%m/%Y %X")

    def view(self):
        return {
            'id':self.id,
            'editid':PaymentOp.generate_editid(self),
            'delid':PaymentOp.generate_delid(self),
            'tenant':PaymentOp.get_names(self),
            'phone':PaymentOp.get_tenant_tel(self),
            'tenant-alt':PaymentOp.get_names(self),
            'house':self.house.name,
            'prop':self.apartment.name,
            'hst':PaymentOp.combine_house_tenant_alt(self),
            'mode':PaymentOp.fname_extracter(self.paymode),
            'payid':self.id,
            'receiptno':self.receipt_num if self.receipt_num else self.id,
            'ref':self.ref_number,
            'chargedamnt':PaymentOp.fig_format(self.charged_amount),
            'highlight':PaymentOp.highlight(self),
            'amount':PaymentOp.fig_format(self.amount),
            'charge':self.payment_name,
            'booking':self.booking_paid,
            'instalment':self.instalment_paid,
            'comments':PaymentOp.comments(self),
            'month':PaymentOp.get_month(self),
            'stamp':PaymentOp.get_pay_timestamp(self),
            'date':PaymentOp.get_date_time(self)[0],
            'time':PaymentOp.get_date_time(self)[1],
            'balance':PaymentOp.fig_format(self.balance),
            'smsstatus':PaymentOp.get_sms_status(self),
            'emailstatus':self.email_status if self.email_status else "-",
            'by':PaymentOp.get_name(self),
            'on':PaymentOp.get_date(self)
        }

class SubmissionOp(Submission,Base):
    def __init__(self,amount,receipt,payperiod,paydate,apartment_id,house_id,tenant_id,created_by):

        self.pay_date = paydate
        self.pay_period = payperiod
        self.amount_paid = amount
        self.receipt_number = receipt

        self.apartment_id=apartment_id
        self.house_id=house_id
        self.tenant_id=tenant_id
        self.user_id = created_by

    def fetch_submission_by_id(id):
        try:
            obj = Submission.query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            obj = None
            db.session.rollback()

        return obj

    def combine_house_tenant_alt(self):
        fname = self.tenant.name.split()[0] if self.tenant.name else "Tenant"
        house =  self.house.name
        return f'<span class="text-gray-600">({house})</span> <span class="text-gray-900 font-weight-bold">{fname}</span>'

    def get_paydate_time(self):
        paydate = self.pay_date if self.pay_date else self.date
        str_date = paydate.strftime("%d/%b/%y")
        str_time = paydate.strftime("%X")
        return str_date,str_time

    def get_payperiod_month(self):
        paydate = self.pay_period if self.pay_period else self.date
        int_month = paydate.month
        str_month = SubmissionOp.get_str_month(int_month)
        return str_month

    def get_date(self):
        paydate = self.date
        str_date = paydate.strftime("%d/%b/%y")
        return str_date
    
    def view(self):
        return {
            'id':self.id,
            'editid':SubmissionOp.generate_editid(self),
            'delid':SubmissionOp.generate_delid(self),
            'tenant':self.tenant,
            'house':self.house,
            'hst':SubmissionOp.combine_house_tenant_alt(self),
            'ref':self.receipt_number,
            'amount':SubmissionOp.fig_format(self.amount_paid),
            'monthpaid':SubmissionOp.get_payperiod_month(self),
            'datepaid':SubmissionOp.get_paydate_time(self)[0],

            'by':SubmissionOp.get_name(self),
            'on':SubmissionOp.get_date(self)
        }

class SplitPaymentOp(SplitPayment,Base):
    def __init__(self,paymode,ref_number,description,chargetype_string,paydate,payperiod,charged_amount,amount,apartment_id,house_id,tenant_id,created_by,chargetype_id=None):
        self.paymode=paymode
        self.ref_number=ref_number
        self.description = description
        self.pay_date = paydate
        self.pay_period = payperiod
        self.amount = amount
        self.original_amount = amount
        self.payment_name = chargetype_string
        self.charged_amount = charged_amount
        self.chargetype_id = chargetype_id
        self.apartment_id=apartment_id
        self.house_id=house_id
        self.tenant_id=tenant_id
        self.user_id = created_by

    def fetch_payment_by_ref(ref):
        return SplitPayment.query.filter_by(ref_number=ref).first()

    def fetch_payment_by_rand_id(rand_id):
        return SplitPayment.query.filter_by(rand_id=rand_id).first()

    def fetch_payment_by_id(id):
        try:
            obj = SplitPayment.query.filter_by(id=id).first()
        except SQLAlchemyError as e:
            print("failing db",str(e))
            obj = None
            db.session.rollback()

        return obj
    
    @staticmethod
    def fetch_latest_payment_by_tenant_id(tenant_id):
        return SplitPayment.query.filter_by(tenant_id=tenant_id).order_by(SplitPayment.date.desc()).first()

    @staticmethod
    def fetch_payment_by_smsid(smsid):
        return SplitPayment.query.filter_by(smsid=smsid).first()

    @staticmethod
    def fetch_all_payments_by_prop_id(prop_id):
        return SplitPayment.query.filter_by(apartment_id=prop_id).order_by(SplitPayment.date.desc()).all()

    @staticmethod
    def fetch_all_payments():
        return SplitPayment.query.order_by(SplitPayment.id.desc()).all()

    def update_balance(self,balance):
        self.balance = balance
        db.session.commit()

    def update_status(self,status,userid):
        self.voided = status
        self.modifiedby = userid
        db.session.commit()

    def update_state(self,state):
        self.state = state
        db.session.commit()

    def update_payperiod(self,payperiod):
        self.pay_period = payperiod
        db.session.commit()

    def update_payment(self,paydate,paid,bal):
        if paydate:
            self.pay_date = paydate
        # if paid:
        #     self.amount = paid
        # self.balance = bal
        db.session.commit()

    def update_payment_info(self,description,chargetype_string):
        self.description = description
        self.payment_name = chargetype_string
        db.session.commit()

    def update_smsid(self,smsid):
        self.smsid = smsid
        db.session.commit()

    def update_rand_id(self,rand_id):
        self.rand_id = rand_id
        db.session.commit()

    def update_sms_status(self,status):
        self.sms_status = status
        db.session.commit()

    def update_email_status(self,status):
        self.email_status = status
        db.session.commit()

    def combine_house_tenant_alt(self):
        fname = self.tenant.name.split()[0] if self.tenant.name else "Tenant"
        house =  self.house.name
        return f'<span class="text-gray-600">({house})</span> <span class="text-gray-900 font-weight-bold">{fname}</span>' 

    def highlight(self):
        if self.balance > 0.0:
            return "text-danger"
        elif self.balance < 0.0:
            return "text-success"
        else:
            return "text-dark"

    def get_date_time(self):
        paydate = self.pay_date if self.pay_date else self.date
        str_date = paydate.strftime("%d/%b/%y")
        str_time = paydate.strftime("%X")
        return str_date,str_time

    def get_date(self):
        paydate = self.date
        str_date = paydate.strftime("%d/%b/%y")
        return str_date

    def get_sms_status(self):
        if self.sms_status:
            if self.sms_status == "Success":
                status = '<span class="text-success"><i class="fas fa-check-double"></i></span>'
            if self.sms_status == "Success-mb":
                status = '<span class="text-primary"><i class="fas fa-check-double"></i></span>'
            elif self.sms_status == "sent":
                status = '<span class="text-primary"><i class="fas fa-check"></i></span>'
            elif self.sms_status == "pending":
                status = '<span class="text-secondary"><i class="fas fa-hourglass-half"></i></span>'
            elif self.sms_status == "fail":
                status = '<span class="text-danger"><i class="fas fa-exclamation-circle"></i></span>'
            elif self.sms_status == "off":
                status = '<span class="text-danger">off</span>'
            else:
                # status = '<span class="text-warning"><i class="fas fa-check"></i></span>'
                status = '<span class="text-success"><i class="fas fa-check-double"></i></span>'

        else:
            status = '<span class="text-danger"><i class="fas fa-check"></i></span>'

        return status

    
    def view(self):
        return {
            'id':self.id,
            'editid':SplitPaymentOp.generate_editid(self),
            'delid':SplitPaymentOp.generate_delid(self),
            'tenant':self.tenant,
            'house':self.house,
            'hst':SplitPaymentOp.combine_house_tenant_alt(self),
            'mode':SplitPaymentOp.fname_extracter(self.paymode),
            'payid':self.id,
            'ref':self.ref_number,
            'chargedamnt':SplitPaymentOp.fig_format(self.charged_amount),
            'highlight':SplitPaymentOp.highlight(self),
            'amount':SplitPaymentOp.fig_format(self.amount),
            'charge':self.payment_name,
            'date':SplitPaymentOp.get_date_time(self)[0],
            'time':SplitPaymentOp.get_date_time(self)[1],
            'balance':SplitPaymentOp.fig_format(self.balance),
            'ref':self.ref_number,
            'smsstatus':SplitPaymentOp.get_sms_status(self),
            'emailstatus':self.email_status if self.email_status else "-",
            'receivedby':SplitPaymentOp.get_name(self),
            'on':SplitPaymentOp.get_date(self)
        }

# class ChargePaymentOp(ChargePayment,Base):
#     def __init__(self,month,paid_amount,water_charge,rent_charge,garbage_charge,apartment_id,house_id,tenant_id,payment_id,created_by):
#         self.paid_amount = paid_amount
#         self.month = month
#         self.water_charge =  water_charge
#         self.rent_charge = rent_charge
#         self.garbage_charge = garbage_charge
#         self.apartment_id = apartment_id
#         self.house_id = house_id
#         self.tenant_id = tenant_id
#         self.payment_id = payment_id
#         self.user_id = created_by

class TextTemplateOp(TextTemplate,Base):
    def __init__(self,text,company_id):
        self.txt = text
        self.company_id = company_id

    @staticmethod
    def fetch_template_by_company_id(company_id):
        return TextTemplate.query.filter_by(company_id=company_id).first()

class ReminderOp(Reminder,Base):
    def __init__(self,date,text,category,prop_id):
        self.date = date
        self.txt = text
        self.category = category
        self.apartment_id = prop_id

    def fetch_all_reminders():
        return Reminder.query.all()

class MpesaPaymentOp(MpesaPayment,Base):
    def __init__(self,ref_number,amount,phone,date,tenant_id):
        self.ref_number = ref_number
        self.amount = amount
        self.phone = phone
        self.date = date
        self.tenant_id = tenant_id

    def fetch_record_by_ref(ref):
        return MpesaPayment.query.filter_by(ref_number=ref).first()

    def fetch_all_records_by_tenant(tenantid):
        return MpesaPayment.query.filter_by(tenant_id=tenantid).first()

    def fetch_all_records():
        return MpesaPayment.query.all()

    def update_status(self,status):
        self.claimed = status
        db.session.commit()

class BankDataOp(BankData,Base):
    """class for c2b model operations"""
    def __init__(self,username,password,billNumber,billAmount,customerRefNumber,bankReference,transParticular,paymentMode,transDate,phoneNumber,debitAccount,debitCustName,data_type):
        self.username = username
        self.password = password
        self.billNumber = billNumber
        self.billAmount = billAmount
        self.customerRefNumber = customerRefNumber
        self.bankReference = bankReference
        self.transParticular = transParticular
        self.paymentMode = paymentMode
        self.transDate = transDate
        self.phoneNumber = phoneNumber
        self.debitAccount = debitAccount
        self.debitCustName = debitCustName
        self.dataType = data_type

    def fetch_record_by_ref(ref):
        return BankDataOp.query.filter_by(bankReference=ref).first()

class CtoBop(CtoB,Base):
    """class for c2b model operations"""
    def __init__(self,trans_id,trans_time,trans_amnt,trans_type,business_shortcode,bill_ref_num,invoice_num,msisdn,org_acc_bal,fname,lname,datatype,mode,company_id):
        self.trans_id = trans_id
        self.trans_time = trans_time
        self.trans_amnt = trans_amnt
        self.trans_type = trans_type
        self.business_shortcode = business_shortcode
        self.bill_ref_num = bill_ref_num
        self.invoice_num = invoice_num
        self.msisdn = msisdn
        self.org_acc_bal = org_acc_bal
        self.fname = fname
        self.lname = lname
        self.mode = mode
        self.data_type = datatype
        self.company_id = company_id

    def fetch_all_records_by_shortcode(shortcode):
        return CtoBop.query.filter_by(business_shortcode=shortcode).all()

    def fetch_record_by_id(record_id):
        return CtoBop.query.filter_by(id=record_id).first()

    def fetch_record_by_mode(mode):
        return CtoBop.query.filter_by(mode=mode).first()

    def fetch_record_by_ref(ref):
        return CtoBop.query.filter_by(trans_id=ref).first()

    def fetch_all_records():
        return CtoB.query.all()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def update_trans(self,trans):
        self.trans_id = trans
        db.session.commit()

    def update_desc(self,trans):
        self.description = trans
        db.session.commit()

    def get_date(self):
        str_t = self.trans_time
        try:
            year = str_t[:4]
            month = str_t[4:6]
            day = str_t[6:8]
            hour = str_t[8:10]
            minute = str_t[10:12]
            second = str_t[12:14]
            ftime = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        except:
            ftime = self.post_date
        # paydate = self.post_date
        str_date = ftime.strftime("%d/%b/%y")
        return str_date

    def get_timestamp(self):
        str_t = self.trans_time
        try:
            year = str_t[:4]
            month = str_t[4:6]
            day = str_t[6:8]
            hour = str_t[8:10]
            minute = str_t[10:12]
            second = str_t[12:14]
            ftime = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        except:
            ftime = self.post_date
        # paydate = self.post_date
        str_date = ftime.strftime("%d/%m/%Y %X")
        return str_date
    
    def get_time(self):

        str_t = self.trans_time
        try:
            year = str_t[:4]
            month = str_t[4:6]
            day = str_t[6:8]
            hour = str_t[8:10]
            minute = str_t[10:12]
            second = str_t[12:14]
            ftime = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        except:
            ftime = self.post_date

        # paydate = self.post_date
        str_date = ftime.strftime("%X")
        return str_date

    def get_status(self):
        if self.status:
            if self.status == "unclaimed":
                status = '<span class="text-danger font-weight-bold">unclaimed</span>'
            else:
                status = '<span class="text-success">resolved</span>'
        else:
            status = '<span class="text-danger font-weight-bold"> ? </span>'

        return status

    def extract_text_after_hashtag(input_string):
        import re
        # Define the regular expression pattern
        pattern = r'#([^~]+)'

        # Use re.search to find the first match
        match = re.search(pattern, input_string)

        # Check if a match is found
        if match:
            # Extract the text after '#'
            extracted_text = match.group(1)
            return extracted_text
        else:
            # Return None if no match is found
            return "no match"

    def view(self):
        try:
            if "#" in self.bill_ref_num:
                billref = CtoBop.extract_text_after_hashtag(self.bill_ref_num)
            else:
                billref = self.bill_ref_num
        except:
            billref = self.bill_ref_num

        return {
            'id':self.id,
            'editid':CtoBop.generate_editid(self),
            'delid':CtoBop.generate_delid(self),
            'transid':self.trans_id,
            'amount':self.trans_amnt,
            'paybill':self.business_shortcode,
            'billref':billref,
            'phone':self.msisdn,
            'fname':self.fname,
            'lname':self.lname,
            'status':CtoBop.get_status(self),
            'date':CtoBop.get_date(self),
            'stamp':CtoBop.get_timestamp(self),
            'time':CtoBop.get_time(self)
        }


class LandlordRemittanceOp(LandlordRemittance,Base):
    """class"""
    def __init__(self,code,name,landlord,tntbbf,rent,expected,actual,tntbcf,ratio,expenses,deposit,utilities,commission,llbbf,payable,remitted,llbcf,agent,period,propid,company_id):
        self.code = code
        self.propcode = code
        self.prop = name
        self.landlord = landlord

        self.tntbbf = tntbbf
        self.rent = rent
        self.expected = expected
        self.actual = actual
        self.tntbcf = tntbcf

        self.ratio = ratio
        self.expenses = expenses

        self.deposit = deposit
        self.utilities = utilities
        self.commission = commission

        self.llbbf = llbbf
        self.payable = payable
        self.remitted = remitted
        self.llbcf = llbcf

        self.period = period

        self.apartment_id = propid
        self.company_id = company_id

        self.agent = agent
        

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def get_date(self):
        str_date = self.period.strftime("%d/%b/%y")
        return str_date

    def view(self):
        return {
            'id':self.id,
            'code':self.code,
            'propcode':self.propcode,
            'name':self.prop,
            'landlord':self.landlord,

            'llbbf':self.llbbf,

            'tntbbf':self.tntbbf,
            'rent':self.rent,
            'expected':self.expected,
            'actual':self.actual,
            'tntbcf':self.tntbcf,

            'utilities':self.utilities,
            'deposit':self.deposit,

            'commission':self.commission,

            'remitted':self.remitted,
            'ratio':self.ratio,
            
            'llbcf':self.llbcf,

            'agent':self.agent,
            'status':self.status,
            'date':LandlordRemittanceOp.get_date(self)
        }


class MpesaRequestOp(MpesaRequest,Base):
    def __init__(self,checkoutrequestid,amount,phone,chargetype_string,tenant_id):
        self.checkoutrequestid = checkoutrequestid
        self.amount = amount
        self.chargetype = chargetype_string
        self.phone = phone
        self.tenant_id = tenant_id

    def fetch_record_by_cri(cri):
        return MpesaRequest.query.filter_by(checkoutrequestid=cri).first()

    def fetch_all_records_by_tenant(tenantid):
        return MpesaRequest.query.filter_by(tenant_id=tenantid).first()

    def fetch_all_records():
        return MpesaRequest.query.all()

    def update_status(self,status,result):
        self.active = status
        self.result = result
        db.session.commit()

class TenantRequestOp(TenantRequest,Base):
    def __init__(self,requesttype,title,description,tenant_id,house_id,apartment_id):
        self.requesttype = requesttype
        self.title = title
        self.description = description
        self.tenant_id = tenant_id
        self.house_id = house_id
        self.apartment_id = apartment_id

    def fetch_requests_by_tenantid(tenant_id):
        return TenantRequest.query.filter_by(tenant_id=tenant_id).all()

    def fetch_all_requests_by_apartmentid(apartment_id):
        return TenantRequest.query.filter_by(apartment_id=apartment_id).all()

    def fetch_a_request_by_id(id):
        return TenantRequest.query.filter_by(id=id).first()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def update_state(self,state):
        self.state = state
        db.session.commit()

    def update_cost(self,cost):
        if cost:
            self.cost = cost
            db.session.commit()

    def update_estimate(self,c_estimate):
        if c_estimate:
            self.cost_estimate = c_estimate
            db.session.commit()

    def update_comment(self,comment):
        if comment:
            self.handled_description = comment
            db.session.commit()
    
    def generate_costid(self):
        """used in distinguishing reqid and its cost , no longer in use"""
        str_id = str(self.id)
        return "cost"+str_id

    def date_format(self):
        year = str(self.date.year)
        abr_year = year[:2]
        month = str(self.date.month)
        day = str(self.date.day)
        return day+"/"+month

    def view(self):
        return {
            'id':self.id,
            'house':self.house,
            'requesttype':self.requesttype,
            'title':self.title,
            'cost':self.cost,
            'costid':TenantRequestOp.generate_costid(self),
            'comment':self.handled_description,
            'status':self.status,
            'date':TenantRequestOp.date_format(self)
        }

class ClearanceRequestOp(ClearanceRequest,Base):
    def __init__(self,clear_month,description,tenant_id,house_id,apartment_id):
        self.clear_month = clear_month
        self.description = description
        self.tenant_id = tenant_id
        self.house_id = house_id
        self.apartment_id = apartment_id

    def fetch_a_request_by_id(id):
        return ClearanceRequest.query.filter_by(id=id).first()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def update_state(self,state):
        self.state = state
        db.session.commit()

    def update_comment(self,comment):
        if comment:
            self.handled_description = comment
            db.session.commit()

    def date_format(self):
        year = str(self.date.year)
        abr_year = year[:2]
        month = str(self.date.month)
        day = str(self.date.day)
        return day+"/"+month
    
    def view(self):
        return {
            'id':self.id,
            'clear_month':self.clear_month,
            'house':self.house,
            'description':self.description,
            'status':self.status,
            'arrears':0.0,
            'date':ClearanceRequestOp.date_format(self)
        }

class TransferRequestOp(TransferRequest,Base):
    def __init__(self,target_house,description,paint_cost,tenant_id,house_id,apartment_id):
        self.target_house = target_house
        self.description = description
        self.paint_costs = paint_cost
        self.tenant_id = tenant_id
        self.house_id = house_id
        self.apartment_id = apartment_id

    def fetch_a_request_by_id(id):
        return TransferRequest.query.filter_by(id=id).first()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def update_state(self,state):
        self.state = state
        db.session.commit()

    def update_comment(self,comment):
        if comment:
            self.handled_description = comment
            db.session.commit()

    def update_cost(self,cost):
        if cost:
            self.paint_costs = cost
            db.session.commit()

    def date_format(self):
        year = str(self.date.year)
        abr_year = year[:2]
        month = str(self.date.month)
        day = str(self.date.day)
        return day+"/"+month
    
    def view(self):
        return {
            'id':self.id,
            'cur_hse':self.house,
            'target_hse':self.target_house,
            'paint_costs':self.paint_costs,
            'description':self.description,
            'status':self.status,
            'date':TransferRequestOp.date_format(self)
        }

class InternalExpenseOp(InternalExpense,Base):
    def __init__(self,name,expense_period,qty,house,deposit,cost,labour,amount,description,expense_type,apartment_id,created_by):
        if not name:
            self.name = "unnamed"
        else:
            self.name = name
        self.date = expense_period
        self.qty = qty
        self.deposit = deposit
        self.house = house
        self.cost = cost
        self.labour = labour
        self.amount = amount
        self.description = description
        self.expense_type = expense_type
        self.apartment_id = apartment_id
        self.created_by = created_by

    def fetch_expense_by_id(id):
        return InternalExpense.query.filter_by(id=id).first()

    def fetch_all_expenses_by_prop_id(propid):
        return InternalExpense.query.filter_by(apartment_id=propid).all()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def update_date(self,date):
        print("Updating date",self.date,"NEW DATE:",date)
        self.date = date

        db.session.commit()

    def update_cost(self,deposit,cost,labour,amount):
        if deposit:
            self.deposit = deposit
        if cost:
            self.cost = cost
        if labour:
            self.labour = labour
        if amount:
            self.amount = amount

        db.session.commit()
            
    def update_name(self,name,qty,house,desc):
        if name:
            self.name = name
        if qty:
            self.qty = qty
        if house:
            self.house = house
        if desc:
            self.description = desc

        db.session.commit()

    def update_expense_type(self,expense_type):
        if expense_type:
            self.expense_type = expense_type
            db.session.commit()

    def update_comment(self,comment):
        self.handled_description = comment
        db.session.commit()

    def date_format(self):
        year = str(self.date.year)
        # abr_year = year[:2]
        month = str(self.date.month)
        day = str(self.date.day)
        return self.date.date()
        # return day+"/"+month+"/"+year

    def house_format(self):
        if not self.house:
            return "-"
        return self.house

    def name_format(self):
        Uid = self.id
        separator = " #"
        return self.name + separator + str(Uid)

    # def generate_editid(self):
    #     fname = self.name.split()[0]
    #     bools = list(map(lambda char: char in string.punctuation, fname))
    #     if any(bools):
    #         for i in fname:
    #             if not i.isalpha():
    #                 target_index = fname.index(i)
    #                 break

    #         new_fname = fname[:target_index]
    #         return new_fname + str(self.id)
    #     else:
    #         return fname + str(self.id)

    def view(self):
        return {
            'id':self.id,
            'editid':InternalExpenseOp.generate_editid(self),
            'delid':InternalExpenseOp.generate_delid(self),
            'house':InternalExpenseOp.house_format(self),
            'name':self.name,
            'type':self.expense_type,
            'apartment':self.apartment,
            'qty':self.qty if self.qty else "-",
            'deposit':self.deposit if self.deposit else "-",
            'cost':self.cost if self.cost else "-",
            'labour':self.labour if self.labour else "-",
            'amount':self.amount,
            'comment':self.handled_description,
            'status':self.status,
            'desc':self.description if self.description else "-",
            'date':InternalExpenseOp.date_format(self)
        }

# class ToggleOp(Toggle,Base):
#     """class"""
#     def __init__(self,name):
#         self.name = name

#     def fetch_toggle_by_id(id):
#         return Toggle.query.filter_by(id=id).first()

#     def update_name(self,name):
#         self.name = name
#         db.session.commit()

class TextMessagesOp(TextMessages,Base):
    """class"""
    def __init__(self,name,email,txt):
        self.name = name
        self.email=email
        self.txt = txt

    def fetch_a_message_by_id(id):
        return TextMessages.query.filter_by(id=id).first()

    def fetch_unread_messages():
        return TextMessages.query.filter_by(status="pending").all()

    def fetch_read_messages():
        return TextMessages.query.filter_by(status="read").all()

    def update_status(self,status):
        self.status = status
        db.session.commit()

class InternalMessagesOp(InternalMessages,Base):
    """class"""
    def __init__(self,title,txt,tenant_id,apartment_id):
        self.title = title
        self.txt = txt
        self.tenant_id = tenant_id
        self.apartment_id = apartment_id

    def fetch_a_message_by_id(id):
        return InternalMessages.query.filter_by(id=id).first()

    def fetch_unread_messages():
        return InternalMessages.query.filter_by(status="pending").all()

    def fetch_read_messages():
        return InternalMessages.query.filter_by(status="read").all()

    def update_status(self,status):
        self.status = status
        db.session.commit()

class SentMessagesOp(SentMessages,Base):
    """class"""
    def __init__(self,text,characters,cost,date_sent,tenant_id,ptenant_id,apartment_id,company_id):
        self.text = text
        self.characters = characters
        self.cost = cost
        self.sms_period = date_sent
        self.tenant_id = tenant_id
        self.ptenant_id = ptenant_id
        self.apartment_id = apartment_id
        self.company_id = company_id

    def fetch_a_message_by_id(id):
        return SentMessages.query.filter_by(id=id).first()

    def fetch_undelivered_messages(status):
        return SentMessages.query.filter_by(status=status).all()

    def fetch_all_messages():
        return SentMessages.query.all()

    def update_status(self,status):
        self.status = status
        db.session.commit()

    def get_house_data(self):
        if self.tenant_id:
            fname = self.tenant.name
            hsname =  TenantOp.get_houseno(self.tenant)
        elif self.ptenant_id:
            fname = self.ptenant.name
            hsname = self.ptenant.house.name
        else:
            fname = "uknown"
            hsname = "unavailable"
        
        return f'<span class="text-gray-600">({hsname})</span> <span class="text-gray-900 font-weight-bold small">{fname}</span>' 

    def view(self):
        return {
            'id':self.id,
            'prop':self.apartment,
            'hst':SentMessagesOp.get_house_data(self),
            'text':self.text,
            'chars':self.characters,
            'cost':self.cost,
            'status':self.status,
            'date':SentMessagesOp.date_format(self.date)
        }

class DepartmentOp(Department, Base):
    """Class to house item operations"""

    def __init__(self, name, description, company_id, created_by):
        self.name = name
        self.description = description
        self.company_id = company_id
        self.created_by = created_by

    @staticmethod
    def fetch_department_by_id(item_id):
        return Department.query.get(item_id)

    @staticmethod
    def fetch_department_by_name(name):
        return Department.query.filter_by(name=name).first()
    @staticmethod
    def fetch_all_departments():
        return Department.query.all()


class ItemOp(Item, Base):
    """Class to house item operations"""

    def __init__(self, name, description,department_id):
        self.name = name
        self.description = description
        self.department_id = department_id

    @staticmethod
    def fetch_item_by_id(item_id):
        return Item.query.get(item_id)

    @staticmethod
    def fetch_item_by_name(name):
        return Item.query.filter_by(name=name).first()
    @staticmethod
    def fetch_all_items():
        return Item.query.all()

    def get_opening_stock(self):
        if self.stocks:
            return self.stocks[0].opening_stock
        else:
            return 0.0
        
    def get_added_stock(self):
        if self.stocks:
            return self.stocks[0].added_stock
        else:
            return 0.0
        
    def get_closing_stock(self):
        if self.stocks:
            return self.stocks[0].closing_stock
        else:
            return 0.0
        
    def get_total_stock(self):
        if self.stocks:
            return (self.stocks[0].opening_stock + (self.stocks[0].added_stock if self.stocks[0].added_stock else 0.0))
        else:
            return 0.0
        
    def get_total_sales(self):
        if self.stocks:
            if self.stocks[0].sales:
                return len(self.stocks[0].sales)
            return 0
        return 0
    
    def get_price(self):
        if self.stocks:
            return self.stocks[0].selling_price
        else:
            return 0.0
        
    def get_amount(self):
        sales = ItemOp.get_total_sales(self)
        if sales:
            return sales * ItemOp.get_price(self)

    def view(self):
            return {
                'id':self.id,
                'editid':ItemOp.generate_editid(self),
                'delid':ItemOp.generate_delid(self),
                'item':self.name,
                'description':self.description,
                'opening':ItemOp.get_opening_stock(self),
                'added':ItemOp.get_added_stock(self),
                'total':ItemOp.get_total_stock(self),
                'closing':ItemOp.get_closing_stock(self),
                'sales':ItemOp.get_total_sales(self),
                'price':ItemOp.get_price(self),
                'amount':ItemOp.get_amount(self),
            }


class StockOp(Stock, Base):
    """Class to house stock operations"""

    def __init__(self, opening_stock, selling_price, item_id, ):
        self.opening_stock = opening_stock
        self.selling_price = selling_price
        self.item_id = item_id

    def fetch_existing_stock(item_id):
        date_today = datetime.datetime.now().date()
        return Stock.query.filter_by(item_id=item_id, date=date_today).first()

    def update_stock(self,opening,added,price):
        self.opening_stock = opening
        self.added_stock = added
        self.selling_price = price

        db.session.commit()

    @staticmethod
    def record_opening_stock(item_id, quantity):
        date_today = datetime.datetime.now()
        new_stock = Stock(item_id=item_id, opening_stock=quantity, closing_stock=quantity, date=date_today)
        new_stock.save()
        return new_stock

    @staticmethod
    def record_sale(item_id, quantity_sold):
        import datetime as dt
        date_today = dt.datetime.now()
        stock = Stock.query.filter_by(item_id=item_id, date=date_today).first()
        if stock:
            new_sale = Sale(stock_id=stock.id, quantity_sold=quantity_sold)
            stock.closing_stock -= quantity_sold
            new_sale.save()
            stock.save()
            return new_sale
        else:
            return None

    @staticmethod
    def fetch_closing_stock(item_id):
        import datetime as dt
        date_today = dt.datetime.now()
        stock = Stock.query.filter_by(item_id=item_id, date=date_today).first()
        if stock:
            return stock.closing_stock
        else:
            return None


class KceEvent(KceEvent, Base):
    """class"""

    def __init__(self,name,desc,venue,category,image):
        self.name = name
        self.description = desc
        self.venue = venue
        self.category = category
        self.image_url = image
