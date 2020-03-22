from flask import Flask, redirect, render_template
from flask import request
import webbrowser
from constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, REDIS_URL
from helpers import make_rand
import db
import token_manager
import redis

application = Flask(__name__, static_url_path='')
redis = r = redis.Redis(host=REDIS_URL, port=6379, db=0, decode_responses=True)

@application.route('/')
def home():
    return render_template('index.html')


@application.route('/login')
def reddit():
    return redirect(f'https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code&state={make_rand()}&redirect_uri={REDIRECT_URI}&duration=permanent&scope={SCOPE}')

@application.route('/go')
def go():
    email = request.args.get('email')
    state = make_rand()
    # hang on to this after the sing in is done
    # TODO redis prefix
    # TODO redis expiration
    redis.set(state, email)
    return redirect(f'https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code&state={state}&redirect_uri={REDIRECT_URI}&duration=permanent&scope={SCOPE}')

# todo user view

@application.route('/token')
def token():
    return 'Hello World!'

@application.route('/oauth_callback')
def oauth_callback():
    state = request.args.get('state')
    code = request.args.get('code')
    email = redis.get(state)
    if email:
        t, r = token_manager.request_token(code)
        name = token_manager.whoami(t)
        if not db.get_user_by_name(name):
            # TODO create and update in one
            id = db.create_user(state, code)
            redis.delete(state)
            db.update_user(id, ('token', 'refresh_token', 'name', 'email'), (t, r, name, email))
            # TODO EMAILER
            return render_template('callback.html', code=code, state=state, name=name, email=email)
        else:
            # log
            return 'error, user already registered'
    else:
        return 'error, already submitted'


if __name__ == '__main__':
    webbrowser.open('127.0.0.1:8888', new=2)
    application.run(port='8888')
