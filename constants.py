import os
ENV = os.environ.get('REDDIT_ENV', 'DEV')
SCOPE = 'identity,edit,history,read,modposts'
USER_AGENT = 'brigadeinsurance-pyscript'
SQLITE_FILE = 'Users.db'
CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
# TODO new email account
GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')
JWT_SECRET = os.environ.get('JWT_SECRET')
REDIS_URL = 'localhost'
if ENV == 'DEV':
    REDIRECT_URI = 'http://127.0.0.1:8888/oauth_callback'
elif ENV == 'PROD':
    REDIRECT_URI = 'http://redditbi.com/oauth_callback'