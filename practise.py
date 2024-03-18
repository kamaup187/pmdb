

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
# def name_standard(name):
#     try:
#         n1 = name.replace(" ","")
#         n2 = n1.upper()
#     except:
#         n2 = name
#     return n2

# n = name_standard("b211,b210")

# print(n)

# if "," in n:
#     n_units = n.split(",")
# else:
#     n_units = [n]


# print("yoyoyo",n_units)








# def split_text_by_keywords(extracted_text, keywords):
#     # Convert the extracted text and keywords to uppercase for case insensitivity
#     extracted_text_upper = extracted_text.upper()
#     keywords_upper = [keyword.upper() for keyword in keywords]

#     # Initialize variables to store the two parts
#     part1 = ""
#     part2 = ""

#     # Iterate through the keywords
#     for keyword in keywords_upper:
#         # Check if the keyword appears in the extracted text
#         if keyword in extracted_text_upper:
#             # Find the index of the keyword in the extracted text
#             index = extracted_text_upper.find(keyword)
#             if index != -1:
#                 # Split the text into two parts at the position of the keyword
#                 part1 = extracted_text[:index].strip()
#                 part2 = keyword
#                 break

#     return [part1, part2]

# # Example usage:
# extracted_text_1 = "101SC"
# extracted_text_2 = "SC101"
# keywords = ["KH", "LA", "KA", "LY", "MGA", "MVA", "MU", "NC", "PA", "SV", "SC", "TA"]

# result_1 = split_text_by_keywords(extracted_text_1, keywords)
# result_2 = split_text_by_keywords(extracted_text_2, keywords)

# print("Result for extracted_text_1:", result_1)
# print("Result for extracted_text_2:", result_2)


def split_text_by_keywords(extracted_text, keywords):
    # Convert the extracted text and keywords to uppercase for case insensitivity
    extracted_text_upper = extracted_text.upper()
    extracted_text = extracted_text.replace("HSE", "")
    extracted_text = extracted_text.replace("HS", "")
    keywords_upper = [keyword.upper() for keyword in keywords]

    # Initialize variables to store the two parts
    part1 = ""
    part2 = ""

    # Iterate through the keywords
    for keyword in keywords_upper:
        # Check if the keyword appears in the extracted text
        if keyword in extracted_text_upper:
            # Find the index of the keyword in the extracted text
            index = extracted_text_upper.find(keyword)
            if index != -1:
                # Check if the keyword is at the beginning of the extracted text
                if index == 0:
                    part1 = extracted_text[len(keyword):].strip()  # Remove keyword from part1
                else:
                    part1 = extracted_text[:index].strip()
                part2 = keyword
                break

    return [part1, part2]

# Example usage:
extracted_text_1 = "kh17"
extracted_text_2 = "17kh"
keywords = ["KH", "LA", "KA", "LY", "MGA", "MVA", "MU", "NC", "PA", "SV", "SC", "TA"]

result_1 = split_text_by_keywords(extracted_text_1, keywords)
result_2 = split_text_by_keywords(extracted_text_2, keywords)

print("Result for extracted_text_1:", result_1)
print("Result for extracted_text_2:", result_2)










