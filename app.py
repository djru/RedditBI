from flask import Flask, redirect, render_template, send_from_directory, make_response
from flask import request
import webbrowser
from constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, REDIS_URL, JWT_SECRET
from helpers import make_rand
import db
import token_manager
import redis
import email_manager
import jwt
import urllib

application = Flask(__name__, static_url_path='/static', static_folder='static')
redis = r = redis.Redis(host=REDIS_URL, port=6379, db=0, decode_responses=True)

@application.route('/')
def home():
    logged_in = False
    jwt_token = request.cookies.get('jwt_token')
    if jwt_token:
        try:
            jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
            logged_in = True
        except:
            pass
    return render_template('index.html', logged_in=logged_in)

@application.route('/go')
def go():
    email = request.args.get('email')
    state = make_rand()
    # TODO redis prefix
    # TODO redis expiration
    redis.set(f'{state}_signup', email)
    return redirect(f'https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code&state={state}_signup&redirect_uri={REDIRECT_URI}&duration=permanent&scope={SCOPE}')

@application.route('/login')
def login():
    state = make_rand()
    return redirect(f'https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code&state={state}_login&redirect_uri={REDIRECT_URI}&duration=permanent&scope={SCOPE}')

@application.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('jwt_token', '', expires=0)
    return resp


# todo user view


@application.route('/delete')
def delete():
    jwt_token = request.cookies.get('jwt_token')
    decoded = None
    if not jwt_token:
        return 'not logged in'
    try:
        decoded = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        return render_template('me.html', email=decoded.get('email'), name=decoded.get('name'), logged_in=True)
    except:
        return 'jwt invalid'
    # todo what if user not exist
    name = decoded.get('name')
    email = decoded.get('email')
    user = db.get_user_by_name(name)
    if not user:
        return 'user does not exist'
    db.delete_user_by_name(name)
    email_manager.send_delete(email, name)
    resp = make_response(f'deleted user {name}')
    resp.set_cookie('jwt_token', '', expires=0)
    return resp


@application.route('/check_token')
def check_token():
    jwt_token = request.cookies.get('jwt_token')
    if not jwt_token:
        return 'not logged in'
    try:
        decoded = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        return decoded
    except:
        return 'jwt invalid'

@application.route('/me')
def me():
    jwt_token = request.cookies.get('jwt_token')
    if not jwt_token:
        return 'not logged in'
    try:
        decoded = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        return render_template('me.html', email=decoded.get('email'), name=decoded.get('name'), logged_in=True)
    except:
        return 'jwt invalid'

@application.route('/oauth_callback')
def oauth_callback():
    state = request.args.get('state')
    code = request.args.get('code')
    t, r = token_manager.request_token(code)
    name = token_manager.whoami(t)
    user = db.get_user_by_name(name)
    if '_signup' in state:
        if user:
            # TODO log this
            # todo login, redirect to main with banner
            return redirect(f'/?msg={urllib.parse.quote("User Already Exists")}')
        email = redis.get(state)
        redis.delete(state)
        if not email:
            return 'signup expired'

        # TODO create and update in one
        id = db.create_user(state, code)
        db.update_user(id, ('token', 'refresh_token', 'name', 'email'), (t, r, name, email))
        email_manager.send_welcome(email, name)
        encoded = jwt.encode({'name': name, 'email': email}, JWT_SECRET, algorithm='HS256')
        resp = make_response(render_template('callback.html', code=code, state=state, name=name, email=email))
        resp.set_cookie('jwt_token', encoded)
        return resp

    elif '_login' in state:
        user = db.get_user_by_name(name)
        if not user:
            return redirect(f'/?msg={urllib.parse.quote("User Not Found")}')
        else:
            encoded = jwt.encode({'name': user.get('name'), 'email': user.get('email')}, JWT_SECRET, algorithm='HS256')
            resp = make_response(redirect('/me'))
            resp.set_cookie('jwt_token', encoded)
            return resp
    else:
        return 'reddit auth failed'



if __name__ == '__main__':
    webbrowser.open('127.0.0.1:8888', new=2)
    application.run(port='8888')
