import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from constants import GMAIL_USER, GMAIL_PASSWORD, APP_URL
import urllib

# https://stackabuse.com/how-to-send-emails-with-gmail-using-python/
def send_welcome(addr, user, state):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        state = urllib.parse.quote(state)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = addr
        msg['Subject'] = 'PLEASE CONFIRM Email for RedditBI'
        msg.attach(MIMEText(f'Hello u/{user} and thank you for signing up for RedditBI. Please confirm your email by clicking <a href="{APP_URL}/confirm_account?name={user}&state={state}">here.</a>', 'html'))
        server.sendmail(GMAIL_USER, addr, msg.as_string())
        server.close()

def send_confirmed(addr, user):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = addr
        msg['Subject'] = 'Thank you for confirming your email'
        msg.attach(MIMEText(f'Hello u/{user}, your email is now confirmed and your signup for RedditBI is complete. You can disable your account any time by visting <a href="{APP_URL}/delete">this link.</a>', 'html'))
        server.sendmail(GMAIL_USER, addr, msg.as_string())
        server.close()

def send_delete(addr, user):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = addr
        msg['Subject'] = 'You are now deleted from RedditBI'
        msg.attach(MIMEText(f'Hello u/{user}. You have been removed from RedditBI. Sorry to see you go 😢'))
        server.sendmail(GMAIL_USER, addr, msg.as_string())
        server.close()

if __name__ == '__main__':
    send_welcome('djrletters@gmail.com')