import os
from app import create_app

configuration = os.getenv('APP_SETTINGS')
# print(configuration, '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<')

app = create_app(configuration)

if __name__ == "__main__":
    app.run()