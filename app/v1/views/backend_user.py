
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

        if not user:
            print("chelaaal")
            user = current_user
        
        usergroup_list = user.company.groups

        tenant_group = CompanyUserGroupOp.fetch_usergroup_by_name("Tenant")
        try:
            usergroup_list.remove(tenant_group)
        except:
            pass
        company_user_group ={
            'company_id':current_user.company_user_group.company_id, 
            'name': current_user.company_user_group.name,
             'description': current_user.company_user_group.description, 
            'id': current_user.company_user_group.id

        }
        userr= {
             'company_usergroup_id': current_user.company_usergroup_id, 
             'usercode': current_user.usercode, 
             'username':current_user.username,
             'id': current_user.id,
              'active': current_user.active, 
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

        # print(stringify_list_items(current_user))
  
        return make_response(jsonify({
            'message_user_': 'Account creation failed.',
            "groups":stringify_list_items(usergroup_list) if usergroup_list else "none" ,
            "user_status":"Active" if current_user.active else "Dormant",
            "savecontext":"Save Changes",
            "user":userr,
            "company":company,
            "company_user_group":company_user_group,

           

            }), 200)

    @login_required
    def post(self):
        #GLOBAL
        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400

        company = current_user.company

        userid = data.get('userid')#this will be selected within the form
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        national_id = data.get('natid')
        pass1 = data.get('pass1')
        pass2 = data.get('pass2')
        usergroup=data.get('usergroup')
        tenantcheck = data.get('tenantcheck')


        if not userid:
            print("chelaaal")
            update_user = current_user
        else:
            user_id = get_identifier(userid)
            update_user = UserOp.fetch_user_by_id(user_id)



        if tenantcheck:
            if update_user.user_group_id == 5:
                return make_response(jsonify({
                    'tentantname':update_user.name
                }))
                # return render_template("ajaxtenantuserupdate.html",tenantname=update_user.name)
            else:
                usergroup_list = company.groups
                for item in usergroup_list:
                    if item.name == "Tenant":
                        usergroup_list.remove(item)
                return make_response(jsonify({
                    'usergroup_option_list':usergroup_list
                }))
                # return render_template("restoreform.html",usergroup_option_list=usergroup_list)

        user_group_id=None

        if usergroup:
            # user_group_id = get_usergroup_id(usergroup)
            
            user_group_id = get_company_usergroup_id(usergroup,company)

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        
        if  validate_pass=="no match":
            flash("Passwords do not match!","fail")
            return redirect(url_for('api.updateuser'))

        modified_by = current_user.id
        company_id = None

        UserOp.update_user(update_user,name,phone,national_id,email,pass1,user_group_id,company_id,modified_by)
        
        return make_response(jsonify({
                    'message':'User info updated.',
                    'status':204
                }))
 


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
            print(co)
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



class BModifyAccessRight(Resource):
    """class"""
    @login_required
    def get(self):
        if current_user.username.startswith('qc'):
            pass
        else:
            user_group = current_user.company_user_group
            accessright = check_accessright(user_group,"grant_rights")
            if accessright != True:
                return make_response(jsonify({
                "message": "You have insufficient rights to access this form!",
                "name":current_user.name
    
            }), 400)    
        company = current_user.company
        groups = company.groups

        form = ModifyAccessRightForm()
        usergroup_list = stringify_list_items(groups)
        place_holder_item = '--Select Usergroup--'
        usergroup_list.insert(0,place_holder_item)
        form.usergroup.choices = usergroup_list


        data= {
            "name":current_user.name,
            # "option_list":groups,
            "logopath":logo(current_user.company)[0],
            "mobilelogopath":logo(current_user.company)[1],
            "name":current_user.name

        }

        return make_response(jsonify({
            "message": "success",
            "data":data
            }), 200)   

    
    @login_required
    def post(self):
        form = ModifyAccessRightForm()
        run = None#run value will be supplied by ajax request
        run2 = None
        usergroup =  form.data.get('usergroup')
        grouprole =  form.data.get('grouprole')
        accessright = request.form.get('access')
        # acc = form.data.get('accessright')

        run = request.form.get('run')
        run2 = request.form.get('run2')
        runcheckall = request.form.get('runcheckall')
        modified_by = current_user.id

        if not accessright:
            accessright = "False"

        access = return_bool(accessright)

        company = current_user.company
        groups = company.groups
        for group in groups:
            if str(group) == usergroup:
                usergroup_obj = group
                break
        # usergroup_obj = CompanyUserGroupOp.fetch_usergroup_by_name(usergroup)

        if usergroup and run:
            usergroup_id = usergroup_obj.id
            assigngrouproleobjs_list = fetch_all_assigned_roles(usergroup_id)
            return render_template('ajaxaccessrights.html',assigngrouproleobjs_list=assigngrouproleobjs_list)

        if runcheckall:
            usergroup_id = usergroup_obj.id
            if usergroup == "Administrator" and access == False:
                pass
            else:
                assigngrouproleobjs_list = fetch_all_assigned_roles(usergroup_id)
                for item in assigngrouproleobjs_list:
                    AssignGroupRoleOp.update_accessright(item,access,modified_by)
            new_assigngrouproleobjs_list = fetch_all_assigned_roles(usergroup_id)
            return render_template('ajaxaccessrights.html',assigngrouproleobjs_list=new_assigngrouproleobjs_list)

        assign_obj = get_group_role_assgn_obj(usergroup_obj,grouprole)
        if usergroup == "Administrator" and grouprole == "grant_rights":
            assign_obj = None
        
        if assign_obj:
            AssignGroupRoleOp.update_accessright(assign_obj,access,modified_by)
            msg = "Database update success"
            flash(msg,"success")
        else:
            msg = "Update failed"
            flash(msg,"fail")
        return redirect(url_for('api.modifyaccessright'))




class BRegisterUser(Resource):
    """This class registers a new user."""
    @login_required
    def post(self):
        """ Handle POST request for this view. Url ---> /signup """
        # if current_user.username.startswith('qc'):
        #     pass
        # else:
        #     user_group = current_user.company_user_group
        #     accessright = check_accessright(user_group,"add_user")
        #     if accessright != True:
        #         return make_response(jsonify({
        #         'message': 'You have insufficient rights to access this form!.',
        #         'name':current_user.name
        #     }), 404)
 

        props = fetch_all_apartments_by_user(current_user)

        # user_group_list = fetch_all_usergroups()
        # tenant_group = UserGroupOp.fetch_usergroup_by_name("Tenant")
        # user_group_list.remove(tenant_group)

        usergroups = ["Manager","Accounts","Caretaker"]

        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400

        print(data)

        prop = data.get('prop')
        email= data.get('email')
        name= data.get('name')
        phone = data.get('phone')
        national_id = data.get('national_id')
        pass1 = data.get('p1')
        pass2 = data.get('p2')
        usergroup = data.get('usergroup')
        created_by = current_user.id

        usercode = usercode_generator()
        is_present  = UserOp.fetch_user_by_usercode(usercode)
        if is_present:
            usercode = usercode_generator()#generate code again

        try:
            preventadmin = parse_for_admin(name)
            if preventadmin:
                return make_response(jsonify({'msg': 'Please try a different name'}))
            
            if not email:
                username = username_extracter(name)
                is_present2  = UserOp.fetch_user_by_username(username)
                if is_present2:
                    username = username_extracternum(name)#append random numbers to name
                    is_present3 = UserOp.fetch_user_by_username(username)
                    if is_present3:
                        username = username_extracternum(name) #generate username again

            else:
                check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
                if check_mail:
                    flash("Email taken, try a different one or leave blank!","fail")
                    return make_response(jsonify({'msg': 'Email taken, try a different one or leave blank!'}))
                username = username_exctractermail(email)
        except:
            flash("Check your inputs","fail")
            return make_response(jsonify({'msg': '"Check your inputs'}))
         

        if not national_id:
            national_id = nationalid_generator()
            check_dup = TenantOp.fetch_tenant_by_nat_id(national_id)
            nat_id = nationalid_generator() if check_dup else national_id
        else:
            nat_id = national_id

        validate_pass = ValidatePass.validate_password(pass1,pass2)
        if not validate_pass:
            flash("Please set a password!","fail")
            return make_response(jsonify({'msg': 'Please set a password!'}))
        elif validate_pass=="no match":
            flash("Passwords do not match","fail")
            return make_response(jsonify({'msg': 'Passwords do not match'}))
           
        else:
            company = current_user.company

            company_usergroup_obj = None
            for obj in company.groups:
                if str(obj) == usergroup:
                    company_usergroup_obj = obj
            if company_usergroup_obj:
                company_usergroup_id = company_usergroup_obj.id

            try:
                # REFACTOR REFACTOR 
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                # REFACTOR REFACTOR
                if usergroup == "Caretaker":
                    new_user = UserOp(name,usercode,username,nat_id,phone,email,pass1,6,company_usergroup_id,company.id,current_user.id)
                    new_user.save()
                else:
                    new_user = UserOp(name,usercode,username,nat_id,phone,email,pass1,4,company_usergroup_id,company.id,current_user.id)
                    new_user.save()

                if usergroup == "Caretaker":
                    prop_obj = ApartmentOp.fetch_apartment_by_name(prop)
                    UserOp.relate(new_user,prop_obj)
                    ApartmentOp.update_caretaker(prop_obj,username)
                else:
                    company_properties = company.props
                    for prop in company_properties:
                        UserOp.relate(new_user,prop)

                msg=f"Registered, Note usercode: {usercode} & username: {username}."
                flash(msg,"success")
            except:
                msg=f"Registration failed."
                flash(msg,"fail")

            return make_response(jsonify({'msg': msg}))