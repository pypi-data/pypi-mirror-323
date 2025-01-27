#!/usr/bin/env python

import logging
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send(message, subject="", recipient=os.getenv("BM_RECIPIENT"), server=os.getenv("BM_SERVER"), port=os.getenv("BM_PORT"), user=os.getenv("BM_USER"),
         service=os.getenv("BM_SERVICE"),level="ERROR"):
    password=os.getenv("BM_PASSWORD")
    if subject == "":
        subject = f"{level} Message from {service}"
    service_snippet = f"+{service}@"
    if server is None: server="server59.hostfactory.ch"
    if port is None: port=465
    sender=user.replace("@", service_snippet)
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(server, port, context=context) as server:
            server.login(user, password)
            server.send_message(msg)
    except:
        logging.exception("could not send report")

if __name__ == "__main__":
    send("Greetings, This is a test Message")
