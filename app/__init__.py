
import os

import africastalking
from flask import Flask,request
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import *
from flask_talisman import Talisman
from flask_migrate import Migrate
from flask_socketio import SocketIO

import jwt
from flask_cors import CORS

from global_functions import *

# try:
#     from do_secrets import *
# except ImportError:
#     SMS_USERNAME = None
#     SMS_API_KEY = None
#     G_ACCOUNT = None
#     G_PASS = None


db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
# socketio = SocketIO(debug=True,cors_allowed_origins='*',async_mode='eventlet') 
# socketio = SocketIO(async_mode='eventlet')
socketio = SocketIO() 


# rq = RQ()


username = os.getenv('SMS_USERNAME') or SMS_USERNAME
api_key = os.getenv('SMS_API_KEY') or SMS_API_KEY


try:
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS
except:
    sms = None

from .v1.models.datamodel import *
from .v1 import version_one as v1
# from .v2 import version_two as v2



def create_app(*args):

    print("INITIATING APPLICATION ...")

    print("Printing LELUT: ",os.getenv('LELUT'))
    print("Printing PCHOMOSNET: ",os.getenv('PCHOMOSNET'))
    print("Printing CHEMOSI: ",os.getenv('CHEMOSI'))

    try:
        from do_secrets import APP_SETTINGS
        # print("FETCHING APP SECRETS FILE")
    except ImportError:
        # print("FETCHING APP SECRETS FROM ENVIRONMENT")
        APP_SETTINGS = os.getenv('APP_SETTINGS')

    configuration = os.getenv('APP_SETTINGS') or APP_SETTINGS

    print("EARLY CONFIG >>>",configuration)

    if args:
        print("EARLY CONFIG >>>",configuration)
        for arg in args:
            configuration = arg
            break
    else:
        print("USING ENV CONFIG >>>",configuration)


    print("NOW CONFIG >>>",configuration)

    app = Flask(__name__)
    Talisman(app,content_security_policy=None)    
    
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>loading configurations<<<<<<<<<<<<<<<<<<<<<<",configuration)

    app.config.from_object(configurations[configuration])
    # app.config.from_object(os.environ['APP_SETTINGS'])

    app.config.from_mapping(
        CLOUDINARY_URL=os.environ.get('CLOUDINARY_URL') or 'cloudinary://597783923547314:uoZkQ1VBpnG8nJbOCJ_TWieviMs@dmq9pwyon',
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app_context = app.app_context()
    app_context.push()
    app.register_blueprint(v1) 
    # app.register_blueprint(v2)
    with app.app_context():
        # Initialize globals/extensions in app context
        # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','HEROKU_POSTGRESQL_AQUA_URL')
        db.init_app(app)
        migrate.init_app(app, db)  

        login_manager = LoginManager()
        login_manager.login_view = 'api.userlogin'
        login_manager.init_app(app)

        mailusername = os.getenv('G_ACCOUNT') or G_ACCOUNT
        mailpassw = os.getenv('G_PASS') or G_PASS

        # app.config['MAIL_SERVER']='smtp.gmail.com'
        # app.config['MAIL_PORT'] = 465
        # app.config['MAIL_USERNAME'] = mailusername
        # app.config['MAIL_PASSWORD'] = mailpassw
        # app.config['MAIL_USE_TLS'] = False
        # app.config['MAIL_USE_SSL'] = True

        #### CORS
        CORS(app, resources={r"/*": {"origins": "*"}})
        app.config['CORS_HEADERS'] = 'Content-Type'
        app.config['CORS_RESOURCES'] = {r"/*": {"origins": "*"}}

        app.config['SECRET_KEY'] = '2b5f7b9b23c54f557b42c8f0fc6d22d3d922f607d3c9075b'

        # app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable caching for static files

        app.config['MAIL_SERVER']='smtp.gmail.com'
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USERNAME'] = 'kiotapay@gmail.com'
        app.config['MAIL_PASSWORD'] = 'mnswpjyxdcvzbjes'
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True

        # app.config['MAIL_SERVER']='smtp.sendgrid.net'
        # app.config['MAIL_PORT'] = 465
        # app.config['MAIL_USERNAME'] = 'apikey'
        # app.config['MAIL_PASSWORD'] = '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'
        # app.config['MAIL_USE_TLS'] = False
        # app.config['MAIL_USE_SSL'] = True

        socketio.init_app(app) 
        mail.init_app(app)    
    
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        try:
            user_obj = User.query.get(int(user_id))
            try:
                print (f">>>>>>>>>>>>>>>>>>> ACTIVE USER: {user_obj.company.name}: ({user_obj.name} - {user_obj.company_user_group}) <<<<<<<<<<<<<<<<<<")
                log = f">>>>>>>>>>>>>>>>>>> ACTIVE USER: {user_obj.company.name}: ({user_obj.name} - {user_obj.company_user_group}) <<<<<<<<<<<<<<<<<<"
                lfile(log)
            except:
                pass
            return user_obj
        except Exception as e:
            print(e)
        user = User.query.filter_by(username=username).first()
        if user:
            return user
        else:
            return None
    


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

# import requests
from app.v1.views.helperfuncs import penalty_calculator,sendlogs

def scheduler():
    """ Function for test purposes. """
    print(">>>>>>>>>>>>>>>>>>BILLING PENALTIES HAS STARTED!")
    try:
        notify = sms.send("Penalty time", ["+254716674695"],"KIOTAPAY")
    except:
        pass

    # r =requests.get('http://127.0.0.1:3000/index')
    # print(r)

    props = []

    # props = [1,18,17,11,15,10]
    # # props = [22]
    # props = [1]
    props = [91,92,484,93]

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

# sched.add_job(scheduler,'cron',id="101",replace_existing=True,hour='21', minute='01')
# sched.add_job(scheduler,'cron',id="101",replace_existing=True,hour='6', minute='40')

sched.add_job(userlogs,'cron',id="102",replace_existing=True,hour='18', minute='00')


# sched.add_job(scheduler,'interval',seconds=86400)
# sched.start()



sched.start()