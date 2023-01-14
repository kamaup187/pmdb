

# # Use the file name mbox-short.txt as the file name
# fname = input("Enter file name: ")
# fh = open(fname)
# count = 0
# total = 0
# for line in fh:
#     if not line.startswith("X-DSPAM-Confidence:") : continue
#     t=line.find("0")
#     number= float(line[t:])
#     count = count + 1
#     total = total + number

# average = total/count
# print ("Average spam confidence:",average)


# ###################################################################################################################################
# ############### This is the solution #############################################################################################
# fname = input("Enter file name: ")
# fh = open(fname)
# lst = list()                       # list for the desired output
# for line in fh:                    # to read every line of file romeo.txt
#     word= line.rstrip().split()    # to eliminate the unwanted blanks and turn the line into a list of words
#     for element in word:           # check every element in word    
#         if element in lst:         # if element is repeated
#             continue               # do nothing
#         else :                     # else if element is not in the list
#             lst.append(element)    # append     
# lst.sort()                         # sort the list (de-indent indicates that you sort when the loop ends)
# print (lst)                        # print the list

# ##################################################################################################################################
# # shulegrade
# # gradepage
# # shuletool
# # pagegrade
# # elimugrade

# class A:
#     id = 5

# bill = A()

# gg = f"app/temp/inv_{bill.id}.pdf"

# billid = gg.split("_")[1].rstrip(".pdf")

# import smtplib
# from email.mime.text import MIMEText
# from email.MIMEMultipart import MIMEMultipart
# from email.MIMEBase import MIMEBase
# from email import Encoders

# def send_mail_gmail(username,password,toaddrs_list,msg_text,fromaddr=None,subject="Test mail",attachment_path_list=None):

#     s = smtplib.SMTP('smtp.gmail.com:587')
#     s.starttls()
#     s.login(username, password)
#     #s.set_debuglevel(1)
#     msg = MIMEMultipart()
#     sender = fromaddr
#     recipients = toaddrs_list
#     msg['Subject'] = subject
#     if fromaddr is not None:
#         msg['From'] = sender
#     msg['To'] = ", ".join(recipients)
#     if attachment_path_list is not None:
#         for each_file_path in attachment_path_list:
#             try:
#                 file_name=each_file_path.split("/")[-1]
#                 part = MIMEBase('application', "octet-stream")
#                 part.set_payload(open(each_file_path, "rb").read())

#                 Encoders.encode_base64(part)
#                 part.add_header('Content-Disposition', 'attachment' ,filename=file_name)
#                 msg.attach(part)
#             except:
#                 print "could not attache file"
#     msg.attach(MIMEText(msg_text,'html'))
#     s.sendmail(sender, recipients, msg.as_string())



# print(list(range(1,(5+1))))

# import requests

# def inva_send_sms():

#     url = "https://vas.bulk.ke/api/PushSMS"

#     payload = {
#         "username": "invap_api",
#         "password": "kX3RXvn5xCdePhKos4ZHYmpdiyXhLqVm",
#         "shortcode": "INVA_PROPTS",
#         "mobile": "254716674695",
#         "message": "Hi Martin, this is message test from Peter"
#     }

#     try:
#         response = requests.post(url, json=payload)
#         print("ADVANTA sms sending successful")
#     except Exception as e:
#         response = ""
#         print("ADVANTA sms sending failed",e)

#     try:
#         print(response.json())
#         msgid = response.json()['referenceid']
#         print("ADVANTA sms response success")
#     except Exception as e:
#         print("ADVANTA sms response error",e)
#         msgid = ""

#     if msgid:
#         respdict = {
#         "apikey":"",
#         "partnerID":"",
#         "msgid":msgid
#         }
#     else:
#         respdict = None

#     return respdict



