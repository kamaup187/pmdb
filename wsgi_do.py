# import os
# from app import create_app
from dapp import create_dapp

import sys

# configuration = os.getenv('APP_SETTINGS')
# if not configuration:
#     configuration = "production"

# app = create_app(configuration)
app = create_dapp()


if __name__ == "__main__":
    app.run()