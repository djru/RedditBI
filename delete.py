import requests
from log_manager import logger
import token_manager
import db
import time

from constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, USER_AGENT

# https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module


def delete(user):
    token = user.get('token')
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': USER_AGENT}
    resp = requests.get(f'https://oauth.reddit.com/user/{user.get("name")}/comments', headers=headers)
    if resp.status_code >= 401:
        return None
    comments = resp.json().get('data').get('children')
    comments = [(c.get('data').get('id'), c.get('data').get('score')) for c in comments]
    comments = [c for c in comments if c[1] < -1]
    for id, s in comments:
        if s < -1:
            logger.info(f'deleting post {id} with score {s}')
            data = {'id': 't1_{id'}
            resp = requests.get('https://oauth.reddit.com/api/del', headers=headers)
            logger.info(resp.status_code)
            try:
                logger.info(resp.json())
            except:
                logger.info(resp.content)
    db.update_user(user.get('id'), ('deleted_count',), (user.get('deleted_count') + len(comments),))
    logger.info(f'[{user.get("name")}] deleted {len(comments)} comments')

    return True


if __name__ == '__main__':
    while True:
        for user in db.get_all_users():
            # perform delete and retry if the token is expired
            succ = delete(user)
            if not succ:
                logger.info(f'[{user.get("name")}] token expired, requesting a new one...')
                token = token_manager.refresh_token(user)
                user['token'] = token
                delete(user)
        time.sleep(60)


