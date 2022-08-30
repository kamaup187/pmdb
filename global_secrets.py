
APP_SETTINGS="production"
DATABASE_URL="postgres:///kiotadb"
HEROKU_POSTGRESQL_AQUA_URL="postgres://bbgozuzflysbpp:52252c232a69248fcaa434826b26dc492160fb8c3648c03f1396115d1ccbf70@ec2-3-221-58-65.compute-1.amazonaws.com:5432/d97c9989tu9isf"
TEST_DATABASE_URL="postgresql:///testdb"
REDIS_URL="redis://localhost:6379"
REDISTOGO_URL=""
AVIV="REVER MWIMUTO LIMITE"
TARGET="lasshous"
INDEX="agentindex.html"
STAGING="True"

CLOUDINARY_URL="cloudinary://597783923547314:uoZkQ1VBpnG8nJbOCJ_TWieviMs@dmq9pwyon"

G_ACCOUNT_ALERTS="notifications.kiotapay@gmail.com"
G_ACCOUNT="kiotapay@gmail.com"
G_PASS="mnswpjyxdcvzbjes"

# G_ACCOUNT_ALERTS="koechpetersn@gmail.com"
# G_ACCOUNT="kodimannsoftware@gmail.com"
# G_PASS="ddtayrrpzvknubng"

SENDER_ID="KIOTAPAY"
SMS_API_KEY="4f501cae150c2bf1ac987dc89d8a724aedbea5b6d248dd3790c4ee7da421c957"
SMS_USERNAME="eapartment"

import sys
import datetime

original_stdout = sys.stdout # Save a reference to the original standard output

def lfile(*args):
    with open('logfile.txt', 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        full_str = ""
        for i in locals()['args']:
            str_print = str(i)
            full_str += str_print
        print(datetime.datetime.now(),":", full_str)
        sys.stdout = original_stdout # Reset the standard output to its original value