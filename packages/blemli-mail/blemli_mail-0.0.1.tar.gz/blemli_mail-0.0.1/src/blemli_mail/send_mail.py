#!/usr/bin/env python

import smtplib, ssl
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os,logging

def send_mail(sender,recipient,subject,message,server,port,user,password):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(server,port, context=context) as server:
        server.login(user,password)
        server.send_message(msg)

def blemli_mail(subject,message):
    load_dotenv()
    recipient=os.getenv("RECIPIENT")
    sender=os.getenv("SENDER")
    server=os.getenv("SERVER")
    port=os.getenv("PORT")
    user=os.getenv("MAILUSER")
    password=os.getenv("MAILPASS")
    try: send_mail(sender,recipient,subject,message,server,port,user,password)
    except: logging.error("could not send report")

if __name__ == "__main__":
    blemli_mail("test","testmail")
