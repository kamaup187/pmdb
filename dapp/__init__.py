
from flask import Flask


from .v1 import version_one as v1

def create_dapp():

    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app_context = app.app_context()
    app_context.push()
    app.register_blueprint(v1)

 
    return app







