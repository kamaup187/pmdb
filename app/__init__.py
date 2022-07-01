
import os

import africastalking
from flask import Flask
# from flask_rq2 import RQ
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import configurations
from flask_talisman import Talisman

import jwt
from flask_cors import CORS
from flask_session import Session



db = SQLAlchemy()
mail = Mail()
# rq = RQ()

# #sandbox keys
# username = "sandbox"
# api_key = "744ef1a5d352fb3edd3f66e6e93a1c0c1122c9918c176ac8a8c7baaab3f74a4c"

#production key
username = os.getenv('SMS_USERNAME')
api_key = os.getenv('SMS_API_KEY')

# username = "eapartmentapp"
# api_key = "d232d0d25c18be83717469452f76e60d7171cf1a5977619e93a23676fe4fc98b"

try:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
except:
    sms = None

from .v1.models.datamodel import *
from .v1 import version_one as v1

def create_app(configuration):

    app = Flask(__name__)
    Talisman(app,content_security_policy=None)


    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)


    
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>loading configurations<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",configuration)

    app.config.from_object(configurations[configuration])
    # app.config.from_object(os.environ['APP_SETTINGS'])

    app.config.from_mapping(
        CLOUDINARY_URL=os.environ.get('CLOUDINARY_URL') or 'Pegue a sua Key',
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app_context = app.app_context()
    app_context.push()
    app.register_blueprint(v1)
    with app.app_context():
        # Initialize globals/extensions in app context
        # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','HEROKU_POSTGRESQL_AQUA_URL')
        db.init_app(app)    

        login_manager = LoginManager()
        login_manager.login_view = 'api.userlogin'
        login_manager.init_app(app)

        mailusername = os.getenv('G_ACCOUNT')
        mailpassw = os.getenv('G_PASS')

        print("username: ",mailusername)
        print("password: ",mailpassw)

        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = mailusername
        app.config['MAIL_PASSWORD'] = mailpassw
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True

        #### CORS
        CORS(app, resources={r"/*": {"origins": "*"}})
        app.config['CORS_HEADERS'] = 'Content-Type'
        app.config['CORS_RESOURCES'] = {r"/*": {"origins": "*"}}

        # app.config['MAIL_SERVER']='mail.privateemail.com'
        # app.config['MAIL_PORT'] = 465
        # app.config['MAIL_USERNAME'] = 'info@kiotapay.com'
        # app.config['MAIL_PASSWORD'] = 'Still7waters'
        # app.config['MAIL_USE_TLS'] = False
        # app.config['MAIL_USE_SSL'] = True

        # app.config['MAIL_SERVER']='smtp.gmail.com'
        # app.config['MAIL_PORT'] = 465
        # app.config['MAIL_USERNAME'] = 'kiotapay@gmail.com'
        # app.config['MAIL_PASSWORD'] = 'mnswpjyxdcvzbjes'
        # app.config['MAIL_USE_TLS'] = False
        # app.config['MAIL_USE_SSL'] = True

        mail.init_app(app)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        try:
            user_obj = User.query.get(int(user_id))
            try:
                print (f">>>>>>>>>>>>>>>>>>> ACTIVE USER: {user_obj.company.name}: ({user_obj.name} - {user_obj.company_user_group}) <<<<<<<<<<<<<<<<<<")
            except:
                pass
            return user_obj
        except Exception as e:
            print(e)
        # User.query.filter_by(username=username).first()
    return app


    @login_manager.request_loader
    def load_user(request):
    
        auth =request.headers.get('Authorization')
        print(auth)
        if not auth: 
            return None
        decode =  jwt.decode(auth, os.getenv('SECRET_KEY'), algorithms=['HS256'])

        try:
            user_obj = User.query.get(int(decode['user_id']))
            try:
                print (f">>>>>>>>>>>>>>>>>>> ACTIVE USER: {user_obj.company.name}: ({user_obj.name} - {user_obj.company_user_group}) <<<<<<<<<<<<<<<<<<")
            except:
                pass
            return user_obj
        except Exception as e:
            print(e)

        
    return app







# ##############################################################################
# from rq import Queue
# from rq.job import Job
# from worker import conn

# q = Queue(connection=conn)

# from .v1.views.helperfuncs import mbogi

# from datetime import timedelta
# import time

# from rq.registry import ScheduledJobRegistry

# # job = q.enqueue_at( datetime.datetime(2021, 1, 26, 22, 57), mbogi)
# # job = mbog.enqueue_in(timedelta(seconds=10), mbogi)

# registry = ScheduledJobRegistry(queue=q)
# time.sleep(0.1)
# print('Number of jobs in registry before scheduling %s' % registry.count)

# if not registry.get_job_ids():
#     print("passing job")
#     job = q.enqueue_in(timedelta(seconds=10), mbogi)
#     print('Number of jobs in registry after job %s' % registry.count)
# else:
#     print("job exists already")

# # print('Number of jobs in registry after initial scheduler %s' % registry.count)
# # for job_id in registry.get_job_ids():
# #     if registry.count < 1:
# #         # registry.remove(job_id, delete_job=True)
# #         job = mbog.enqueue_in(timedelta(seconds=10), mbogi)
# #         print("Passing subsequent job")
# ##############################################################################

from rq import Queue
from rq.job import Job
from worker import conn
q = Queue(connection=conn)

from apscheduler.schedulers.background import BackgroundScheduler
sched = BackgroundScheduler(daemon=True)

import requests
from app.v1.views.helperfuncs import penalty_calculator,sendlogs

def scheduler():
    """ Function for test purposes. """
    print(">>>>>>>>>>>>>>>>>>BILLING PENALTIES HAS STARTED!")
    # try:
    #     notify = sms.send("Penalty time", ["+254716674695"],"KIOTAPAY")
    # except:
    #     pass

    # r =requests.get('http://127.0.0.1:3000/index')
    # print(r)

    props = []

    # props = [1,18,17,11,15,10]
    # # props = [22]
    # props = [1]

    penjob = q.enqueue_call(
        func=penalty_calculator, args=(props,), result_ttl=5000
    )


def userlogs():

    day = None

    # logsjob = q.enqueue_call(
    #     func=sendlogs, args=(day,), result_ttl=5000
    # )



# @sched.scheduled_job('cron', day_of_week='mon-sun', hour=22,minute=22)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')

sched.add_job(scheduler,'cron',id="101",replace_existing=True,hour='21', minute='01')

sched.add_job(userlogs,'cron',id="102",replace_existing=True,hour='18', minute='00')


# sched.add_job(scheduler,'interval',seconds=86400)
# sched.start()



sched.start()