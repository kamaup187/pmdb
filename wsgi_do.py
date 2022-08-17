import os
from app import create_app
from app.v1.views.secrets import *
# from dapp import create_dapp

configuration = os.getenv('APP_SETTINGS') or APP_SETTINGS

app = create_app(configuration)
# app = create_dapp()


if __name__ == "__main__":
    app.run()