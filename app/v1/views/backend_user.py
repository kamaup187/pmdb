
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