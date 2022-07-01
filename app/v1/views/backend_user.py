
from flask_restful import Resource
from flask_login import login_user,logout_user
from flask_login import login_required, current_user

from flask import render_template,Response,request,flash,redirect,url_for,abort,make_response,jsonify
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


class BAdminRegisterUser(Resource):
    """This class registers a new user --agents or caretakers."""

    @login_required
    def post(self):
        """ Handle POST request for this view. Url ---> /signup """
        companies = []
        company_usergroups = ["Manager","Accounts"]
        
        data = request.get_json()
        if not data:
            return jsonify({'msg': 'Missing JSON'}), 400

        # form = UserRegForm()

        # uniquename = form.data.get('owner')
        # apartment = form.data.get('apartment')
        company= data.get('company')
        # ownerauto = request.form.get('ownerauto')

        email= data.get('email')
        name= data.get('name')
        phone= data.get('phone')
        national_id= data.get('national_id')
        pass1 = data.get('p1')
        pass2 = data.get('p2')
        company_usergroup = data.get('usergroup')

        # if ownerauto:
        #     owner_id = OwnerOp.fetch_owner_by_uniquename(uniquename).id
        #     apartments = ApartmentOp.fetch_all_apartments_by_owner(owner_id)
        #     place_holder_item = '--Select Apartment--'
        #     apartments.insert(0,place_holder_item)
        #     form.apartment.choices = apartments
        #     return render_template('allocapartmentoptions.html', form=form)

        preventadmin = parse_for_admin(name)
        if preventadmin:
            return make_response(jsonify({
                'message': 'Please try a different name'
            }), 204)

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
            check_mail = UserOp.fetch_user_by_email(email) #email provided but lets check duplicates
            if check_mail:
                return make_response(jsonify({
                'message': 'Email taken, try a different one or leave blank!'
            }), 200)
            username = username_exctractermail(email)

        if not national_id:
            national_id = nationalid_generator()
            check_dup = TenantOp.fetch_tenant_by_nat_id(national_id)
            nat_id = nationalid_generator() if check_dup else national_id
        else:
            nat_id = national_id

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
            company_usergroup_obj = None
            company_obj = CompanyOp.fetch_company_by_name(company) 
            print("Available Groups>>>>>>>",company_obj.groups)
            for obj in company_obj.groups:
                if str(obj) == company_usergroup:
                    company_usergroup_obj = obj
            if company_usergroup_obj:
                company_usergroup_id = company_usergroup_obj.id
            try:
                new_user = UserOp(name,usercode,username,nat_id,phone,email,pass1,4,company_usergroup_id,company_obj.id,1)
                new_user.save()

                company_properties = company_obj.props
                for prop in company_properties:
                    UserOp.relate(new_user,prop)

                msg=f"Registered, Note usercode: {usercode} & username: {username}."
                flash(msg,"success")
                
            except Exception as e:
                print("Registration failed>>>",e)
                msg=f"Registration failed"
                flash(msg,"fail")

            return make_response(jsonify({
                'message': 'Check Email/Password'
            }), 204)

