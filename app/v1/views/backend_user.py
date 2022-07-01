
from flask_restful import Resource
from flask_login import login_user,logout_user
from flask_login import login_required, current_user

from flask import render_template,Response,request,flash,redirect,url_for,abort,make_response,jsonify,session
from ..forms.forms import ModifyAccessRightForm
from ..forms.forms import UserRegForm

from app.v1.models.operations import *
from .helperfuncs import *
from app import db
from app import sms

from flask_cors import cross_origin
import jwt


#  Authentication 

class BUserLogin(Resource):
    """Handles login and access token generation."""

    @cross_origin()
    def post(self):
        if current_user.is_authenticated:
            return make_response(jsonify({
                'message': 'User already logged in',
            }), 200)

        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400
        400

        identity  = data.get('identifier')
        password=data.get('password')
        remember = False
        downtime = False

        print("Supplied logins >>>> ", "IDENTITY:",identity,"PASSW:",password)
        ### remember = True if request.form.get('remember') else False
        try:
            user = fetch_user(identity)
        except Exception as e:
            user = None
            downtime = True
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Login fail error",e)
            return make_response(jsonify({
                'message': 'Login fail error',
                'error':e
            }), 400)

        if user:
            if UserOp.password_is_valid(user,password):
                login_user(user, remember=remember)
                token = jwt.encode({'user_id': user.user_id}, os.getenv('SECRET_KEY'), 'HS256')
                return {
                    "message": "Success",
                    "token":token,
                    "status":200
                }
                

            return make_response(jsonify({
                'message': 'Check Email/Password'
            }), 400)
        elif downtime:
            response = sms.send("Login is experiencing issues", ["+254716674695"],sender)
            return make_response(jsonify({
                'message': 'Login failed, system undergoing maintenance!'
            }), 400)
        return make_response(jsonify({
                'message': 'It seems you have no account yet!.'
            }), 400)
 



class BUserLogout(Resource):
    @login_required
    def get(self):
        logout_user()
        return make_response(jsonify({
            'message': 'Logout Succesfull',
        }), 200)


# class BAdminRegisterUser(Resource):
#     """This class registers a new user --agents or caretakers."""

#     @login_required
#     def post(self):
#         """ Handle POST request for this view. Url ---> /signup """
#         companies = []
#         company_usergroups = ["Manager","Accounts"]
        
#         data = request.get_json()
#         if not data:
#             return jsonify({'msg': 'Missing JSON'}), 400

#         # form = UserRegForm()

#         # uniquename = form.data.get('owner')
#         # apartment = form.data.get('apartment')
#         company= data.get('company')
#         # ownerauto = request.form.get('ownerauto')

#         email= data.get('email')
#         name= data.get('name')
#         phone= data.get('phone')
#         national_id= data.get('national_id')
#         pass1 = data.get('p1')
#         pass2 = data.get('p2')
#         company_usergroup = data.get('usergroup')

#         # if ownerauto:
#         #     owner_id = OwnerOp.fetch_owner_by_uniquename(uniquename).id
#         #     apartments = ApartmentOp.fetch_all_apartments_by_owner(owner_id)
#         #     place_holder_item = '--Select Apartment--'
#         #     apartments.insert(0,place_holder_item)
#         #     form.apartment.choices = apartments
#         #     return render_template('allocapartmentoptions.html', form=form)

#         preventadmin = parse_for_admin(name)
#         if preventadmin:
#             return make_response(jsonify({
#                 'message': 'Please try a different name'
#             }), 204)

#         usercode = usercode_generator()

#         is_present  = UserOp.fetch_user_by_usercode(usercode)
#         if is_present:
#             usercode = usercode_generator()#generate code again

#         if not email:
#             username = username_extracter(name)
#             is_present2  = UserOp.fetch_user_by_username(username)
#             if is_present2:
#                 username = username_extracternum(name)#append random numbers to name
#                 is_present3 = UserOp.fetch_user_by_username(username)
#                 if is_present3:
#                     username = username_extracternum(name) #generate username again

#         else:
#             check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
#             if check_mail:
#                 return make_response(jsonify({
#                 'message': 'Email taken, try a different one or leave blank!'
#             }), 200)
#             username = username_exctractermail(email)

#         if not national_id:
#             national_id = nationalid_generator()
#             check_dup = TenantOp.fetch_tenant_by_nat_id(national_id)
#             nat_id = nationalid_generator() if check_dup else national_id
#         else:
#             nat_id = national_id

#         validate_pass = ValidatePass.validate_password(pass1,pass2)
#         if not validate_pass:
#             return make_response(jsonify({
#                 'message': 'Please set a password!'
#             }), 200)
#         elif validate_pass=="no match":
#             return make_response(jsonify({
#                 'message': 'Passwords do not match'
#             }), 200)
#         else:
#             company_usergroup_obj = None
#             company_obj = CompanyOp.fetch_company_by_name(company) 
#             print("Available Groups>>>>>>>",company_obj.groups)
#             for obj in company_obj.groups:
#                 if str(obj) == company_usergroup:
#                     company_usergroup_obj = obj
#             if company_usergroup_obj:
#                 company_usergroup_id = company_usergroup_obj.id
#             try:
#                 new_user = UserOp(name,usercode,username,nat_id,phone,email,pass1,4,company_usergroup_id,company_obj.id,1)
#                 new_user.save()

#                 company_properties = company_obj.props
#                 for prop in company_properties:
#                     UserOp.relate(new_user,prop)

#                 msg=f"Registered, Note usercode: {usercode} & username: {username}."
#                 flash(msg,"success")
                
#             except Exception as e:
#                 print("Registration failed>>>",e)
#                 msg=f"Registration failed"
#                 flash(msg,"fail")

#             return make_response(jsonify({
#                 'message': 'Check Email/Password'
#             }), 204)

class BUpdateUser(Resource):
    @login_required
    def get(self):
        """Handle GET request for this view. Url ---> /update/user"""

        userid = request.args.get('userid')

        user_id = get_identifier(userid)

        user = UserOp.fetch_user_by_id(user_id)

        company_user_group ={
            'company_id':current_user.company_user_group.company_id, 
            'name': current_user.company_user_group.name,
             'description': current_user.company_user_group.description, 
            'id': current_user.company_user_group.id

        }
        user= {
             'company_usergroup_id': current_user.company_usergroup_id, 
             'usercode': current_user.usercode, 
             'username':current_user.username,
             'id': current_user.id,
            #   'active': current_user.active, 
            'date': current_user.date, 
            'activation_link': current_user.activation_link, 
            'name':current_user.name, 
             'user_id': current_user.user_id, 
             'phone': current_user.phone, 
             'user_group_id': current_user.user_group_id, 
             'national_id': current_user.national_id,
             'company_id': current_user.company_id,
            'email': current_user.email
        }

        company ={
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


        # if not user:
        #     print("chelaaal")
        #     user = current_user

        # usergroup_list = user.company.groups

        # tenant_group = CompanyUserGroupOp.fetch_usergroup_by_name("Tenant")
        # try:
        #     usergroup_list.remove(tenant_group)
        # except:
        #     pass

        return make_response(jsonify({
            'message_user_': 'Account creation failed.',
            # "groups":usergroup_list,
            "user_status":"Active" if current_user.active else "Dormant",
            "savecontext":"Save Changes",
            "user":user,
            "company":company,
            "company_user_group":company_user_group
           

            }), 200)

    # @login_required
    # def post(self):
    #     #GLOBAL
    #     company = current_user.company

    #     userid = request.form.get('userid')#this will be selected within the form
    #     name = request.form.get('name')
    #     phone = request.form.get('phone')
    #     email = request.form.get('email')
    #     national_id = request.form.get('natid')
    #     pass1 = request.form.get('pass1')
    #     pass2 = request.form.get('pass2')
    #     usergroup=request.form.get('usergroup')

    #     tenantcheck = request.form.get('tenantcheck')


    #     if not userid:
    #         print("chelaaal")
    #         update_user = current_user
    #     else:
    #         user_id = get_identifier(userid)
    #         update_user = UserOp.fetch_user_by_id(user_id)



    #     if tenantcheck:
    #         if update_user.user_group_id == 5:
    #             return render_template("ajaxtenantuserupdate.html",tenantname=update_user.name)
    #         else:
    #             usergroup_list = company.groups
    #             for item in usergroup_list:
    #                 if item.name == "Tenant":
    #                     usergroup_list.remove(item)
    #             return render_template("restoreform.html",usergroup_option_list=usergroup_list)

    #     user_group_id=None

    #     if usergroup:
    #         # user_group_id = get_usergroup_id(usergroup)
            
    #         user_group_id = get_company_usergroup_id(usergroup,company)

    #     validate_pass = ValidatePass.validate_password(pass1,pass2)
        
    #     if  validate_pass=="no match":
    #         flash("Passwords do not match!","fail")
    #         return redirect(url_for('api.updateuser'))

    #     modified_by = current_user.id
    #     company_id = None

    #     UserOp.update_user(update_user,name,phone,national_id,email,pass1,user_group_id,company_id,modified_by)
        
    #     msg='User info updated.'
    #     flash(msg,"success")

    #     return redirect(url_for("api.updateuser"))




class BAdminCreateAgent(Resource):
    """class"""

    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400

        fname=data.get('fname')
        lname=data.get('lname')
        phone=data.get('tel')
        natid=data.get('natid')
        email=data.get('email')
        company_name = data.get('company')
        address = data.get('address')
        mail_box = data.get('mailbox')
        tel = data.get('company_tel')
        mail = data.get('company_mail')
        description = data.get('desc')
        pass1 = data.get('p1')
        pass2 = data.get('p2')

        created_by = 1
        usergroup_id = 3

        name = fname + " " + lname

        is_present  = UserOp.fetch_user_by_national_id(natid)
        
        if is_present:
            return make_response(jsonify({
                'message':'Account exists already'
            }), 200)

        if not natid:
            natid = nationalid_generator()
            check_dup = TenantOp.fetch_tenant_by_nat_id(natid)
            nat_id = nationalid_generator() if check_dup else natid
        else:
            nat_id = natid

        usercode = usercode_generator()
        is_present  = UserOp.fetch_user_by_usercode(usercode)
        if is_present:
            usercode = usercode_generator()#generate code again

        check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
        if check_mail:
            return make_response(jsonify({
                'message': 'Registration failed, email taken, try a different one'
            }), 200)
        username = username_exctractermail(email)

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        if not validate_pass:
            return make_response(jsonify({
                'message': 'Please set a password!'
            }), 200)
        elif validate_pass=="no match":
            return make_response(jsonify({
                'message': 'Passwords do not match'
            }), 200)
        else:
            co = CompanyOp.fetch_company_by_name(company_name)
            if not co:
                dir_group = None
                company_obj = CompanyOp(company_name,address,mail_box,mail,tel,description)
                company_obj.save()

                groups = ["Director","Manager","Property Agent","Accounts","Owner","Caretaker","Tenant"]
                for group in groups:
                    group_obj = CompanyUserGroupOp(group,"",company_obj.id)
                    group_obj.save()

                    if group == "Director":
                        dir_group = group_obj

                auto_assign_company_group_roles(company_name)

                user = UserOp(name,usercode,username,nat_id,phone,email,pass1,usergroup_id,dir_group.id,company_obj.id,created_by)
                user.save()

                return make_response(jsonify({
                'message': 'Account created successfully.'
            }), 200)

            else:
                return make_response(jsonify({
                'message': 'Account creation failed.'
            }), 200)



