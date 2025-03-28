import smtplib
from email.message import EmailMessage
import packagelog
from pathlib import Path
import os
import json

#edit email_info_example.json to have correct info and change name to email_info.json
#alternatively, change info in MakeJSON.py and run it
with open('email_info.json') as f:
    json_string = json.load(f)
email_dict = json.loads(json_string)

# Set up email account information (I was too lazy to replace everything with the dictionary info in the code
email_address = email_dict['email_address']
email_password = email_dict['email_password']
smtp_server = email_dict["smtp_server"]
smtp_port = email_dict["smtp_port"]
default_to_email = email_dict['default_to_email']
default_subject = email_dict['default_subject']
#
default_file_name = Path(os.path.expanduser('~')) / 'Documents' / f'Report_{packagelog.time_string()}.csv'

def save_then_email(headers, data, file_name=default_file_name, subject=default_subject, send_to=default_to_email):
    packagelog.save_report(headers=headers, data=data, file_name=file_name, send_email=True)
    send_email(subject=subject, send_to=send_to, file=file_name)

def send_email(subject, send_to, file):
    # Create email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = send_to
    msg.set_content('Package Log Report')
    with open(file, 'rb') as f:
        file_data = f.read()
    msg.add_attachment(file_data, maintype='text', subtype='plain', filename=f'Report {packagelog.today_date_string()}.csv')

    # Send email message
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.send_message(msg)
