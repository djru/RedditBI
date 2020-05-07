import requests
from log_manager import logger
import token_manager
from models import db, User
import time
from constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, USER_AGENT

# https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module

def delete_comments(user):
    token = user.token
    headers = {'Authorization': f'Bearer {token}', 'User-Agent': USER_AGENT}
    resp = requests.get(f'https://oauth.reddit.com/user/{user.name}/comments', headers=headers)
    if resp.status_code >= 401:
        return None
    comments = resp.json().get('data').get('children')
    comments = [(c.get('data').get('id'), c.get('data').get('score')) for c in comments]
    comments = [c for c in comments if c[1] < -1]
    for id, s in comments:
        if s < -1:
            logger.info(f'deleting post {id} with score {s}')
            data = {'id': 't1_{id'}
            resp = requests.post('https://oauth.reddit.com/api/del', headers=headers, json=data)
            logger.info(resp.status_code)
            try:
                logger.info(resp.json())
            except:
                logger.info(resp.content)
    user.deleted_count = user.deleted_count + len(comments)
    db.session.commit()
    logger.info(f'[{user.get("name")}] deleted {len(comments)} comments')

    return True


if __name__ == '__main__':
    from application import application
    db.init_app(application)
    application.app_context().push()
    while True:
        for user in User.query.all():
            # perform delete and retry if the token is expired
            succ = delete_comments(user)
            if not succ:
                logger.info(f'[{user.name}] token expired, requesting a new one...')
                token = token_manager.refresh_token(user)
                user.token = token
                db.session.commit()
                delete_comments(user)
        time.sleep(60)


