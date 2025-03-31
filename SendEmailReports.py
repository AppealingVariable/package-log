import smtplib
from email.message import EmailMessage
import packagelog
from pathlib import Path
import os
import keyring as kr

#uncomment the #set_creds() function in the CredMan.py file and run it in the terminal to set email and password
#also set the below information to appropriate values for your email provider
def get_creds(email):
    return kr.get_password("package_email", email)

email_address = 'example@example.com'
email_password = get_creds(email_address) #if you don't want to use the keyring library, just replace this with a string
smtp_server = 'smtp.example.com'
smtp_port = 587
default_to_email = 'example@example.com'
default_subject = 'Package Report'
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
