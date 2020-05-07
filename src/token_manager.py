import requests
from log_manager import logger
from models import db, User

from constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, USER_AGENT

# https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module


def request_token(code):
    req_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    resp = requests.post('https://www.reddit.com/api/v1/access_token', data=req_data, auth=(CLIENT_ID, CLIENT_SECRET), headers={'User-Agent': USER_AGENT})
    resp = resp.json()
    token = resp.get('access_token')
    refresh = resp.get('refresh_token')
    if token is None or refresh is None:
        logger.warning(f'COULD NOT GET TOKEN FOR CODE {code}: {resp}')
    else:
        logger.info(f'requested token from server and got {token} (refresh token: {refresh})')
    return (token, refresh)

def refresh_token(user):
    req_data = {
        'grant_type': 'refresh_token',
        'refresh_token': user.refresh_token
    }
    resp = requests.post('https://www.reddit.com/api/v1/access_token', data=req_data, auth=(CLIENT_ID, CLIENT_SECRET), headers={'User-Agent': USER_AGENT})
    resp = resp.json()
    token = resp.get('access_token')
    logger.info(f'[user {user.name}] requested a refreshed token from the server and got: {token}')
    return token

def whoami(t):
    headers = {'Authorization': f'Bearer {t}', 'User-Agent': USER_AGENT}
    resp = requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
    if resp.status_code >= 401:
        return None
    try:
        return resp.json().get('name')
    except:
        return None