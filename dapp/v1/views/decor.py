import sys
import datetime

original_stdout = sys.stdout # Save a reference to the original standard output

def lfile(*args):
    with open('logfile.txt', 'a') as f:
        sys.stdout = f # Change the standard output to the file we created.
        printout = ' '.join(locals()['args'])
        print(datetime.datetime.now(),":", printout)
        sys.stdout = original_stdout # Reset the standard output to its original value

