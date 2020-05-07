import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from constants import SENDGRID_API_KEY, APP_URL
import urllib
from log_manager import logger

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# https://stackabuse.com/how-to-send-emails-with-gmail-using-python/
def send_welcome(addr, user, state):
    message = Mail(
        from_email='app.redditbi@gmail.com',
        to_emails=addr,
        subject='Please Confirm Email for RedditBI',
        html_content=f'Hello u/{user} and thank you for signing up for RedditBI. Please confirm your email by clicking <a href="{APP_URL}/confirm_account?name={user}&state={state}">here.</a>')
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)

def send_confirmed(addr, user):
    message = Mail(
        from_email='app.redditbi@gmail.com',
        to_emails=addr,
        subject='Please Confirm Email for RedditBI',
        html_content=f'Hello u/{user}, your email is now confirmed and your signup for RedditBI is complete. You can disable your account any time by visting <a href="{APP_URL}/delete">this link.</a>')
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)

def send_delete(addr, user):
    message = Mail(
        from_email='app.redditbi@gmail.com',
        to_emails=addr,
        subject='Please Confirm Email for RedditBI',
        html_content=f'Hello u/{user}. You have been removed from RedditBI. Sorry to see you go 😢')
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
    except Exception as e:
        print(e.message)



if __name__ == '__main__':
    send_welcome('djrletters@gmail.com')