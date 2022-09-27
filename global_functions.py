import os
import sys
import datetime
try:
    from do_secrets import LOCALENV
except ImportError:
    LOCALENV = os.getenv('LOCALENV')

original_stdout = sys.stdout # Save a reference to the original standard output

def lfile(*args):
    if LOCALENV:
        with open('logfile.txt', 'a') as f:
            sys.stdout = f # Change the standard output to the file we created.
            full_str = ""
            for i in locals()['args']:
                str_print = str(i)
                full_str += str_print
            print(datetime.datetime.now(),":", full_str)
            sys.stdout = original_stdout # Reset the standard output to its original value

def lfile2(*args):
    if LOCALENV:
        with open('logfiletwo.txt', 'a') as f:
            sys.stdout = f # Change the standard output to the file we created.
            full_str = ""
            for i in locals()['args']:
                str_print = str(i)
                full_str += str_print
            print(datetime.datetime.now(),":", full_str)
            sys.stdout = original_stdout # Reset the standard output to its original value