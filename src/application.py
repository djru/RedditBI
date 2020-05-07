from flask import Flask, redirect, render_template, send_from_directory, make_response, session, request, jsonify
import webbrowser
from constants import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SCOPE, JWT_SECRET, ENV
from helpers import make_rand
# import db
import time
import token_manager
import email_manager
import jwt
import urllib
from models import db, User

def rows_to_dict_arr(rows):
    return [dict((k,v) for (k,v) in u.__dict__.items() if k[0] != '_') for u in rows]


# https://uwsgi-docs.readthedocs.io/en/latest/AttachingDaemons.html
application = Flask(__name__, static_url_path='/static', static_folder='static')
application.secret_key = JWT_SECRET
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/Users.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(application)

# https://stackoverflow.com/questions/46540664/no-application-found-either-work-inside-a-view-function-or-push-an-application
with application.app_context():
    db.create_all()

# decorator that wraps protected endpoints
def authenticate(fn):
    def wrapper():
        jwt_token = request.cookies.get('jwt_token')
        if not jwt_token:
            return redirect('/')
        try:
            decoded = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
            user = User.query.filter_by(name=decoded.get('name')).first()
            if not user:
                resp = redirect('/')
                # if user doesn't exist, log them out
                resp.set_cookie('jwt_token', '', expires=0)
                return resp
            return fn(user)
        except:
            return redirect(f'/?msg={urllib.parse.quote("something went wrong, invalid")}')
    # https://stackoverflow.com/questions/17256602/assertionerror-view-function-mapping-is-overwriting-an-existing-endpoint-functi
    wrapper.__name__ = fn.__name__
    return wrapper


@application.route('/')
def home():
    jwt_token = request.cookies.get('jwt_token')
    if jwt_token:
        decoded = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        user = User.query.filter_by(name=decoded.get('name')).first()
        if user:
            return redirect('/me')
    return render_template('index.html', logged_in=False)


# AUTH
@application.route('/go')
def go():
    email = request.args.get('email')
    state = make_rand()
    session['email'] = email
    session['state'] = f'{state}_signup'
    return render_template('redirect.html', url=f'https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code&state={state}_signup&redirect_uri={REDIRECT_URI}&duration=permanent&scope={SCOPE}')

@application.route('/login')
def login():
    state = make_rand()
    return redirect(f'https://www.reddit.com/api/v1/authorize?client_id={CLIENT_ID}&response_type=code&state={state}_login&redirect_uri={REDIRECT_URI}&duration=permanent&scope={SCOPE}')

@application.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('jwt_token', '', expires=0)
    return resp

@application.route('/oauth_callback')
def oauth_callback():
    state = request.args.get('state')
    code = request.args.get('code')
    t, r = token_manager.request_token(code)
    name = token_manager.whoami(t)
    user = User.query.filter_by(name=name).first()
    if '_signup' in state:
        email = session.get('email')
        if state != session.get('state') or email != session.get('email'):
            return 'something went wrong'
        if user:
            encoded = jwt.encode({'name': user.name, 'email': user.email}, JWT_SECRET, algorithm='HS256')
            resp = make_response(redirect('/me'))
            resp.set_cookie('jwt_token', encoded)
            return resp
        u = User(state=state, code=code, token=t, refresh_token=r, name=name, email=email)
        db.session.add(u)
        db.session.commit()
        email_manager.send_welcome(email, name, state)
        encoded = jwt.encode({'name': name, 'email': email}, JWT_SECRET, algorithm='HS256')
        resp = make_response(redirect('/me'))
        resp.set_cookie('jwt_token', encoded)
        return resp

    elif '_login' in state:
        user = User.query.filter_by(name=name).first()
        if not user:
            return redirect(f'/?msg={urllib.parse.quote("User Not Found")}')
        else:
            encoded = jwt.encode({'name': user.name, 'email': user.email}, JWT_SECRET, algorithm='HS256')
            resp = make_response(redirect('/me'))
            resp.set_cookie('jwt_token', encoded)
            return resp
    else:
        return 'reddit auth failed'


# USER MANAGEMENT

@application.route('/delete')
@authenticate
def delete(user):
    db.session.delete(user)
    db.session.commit()
    email_manager.send_delete(user.email, user.name)
    resp = redirect(f'/?msg={urllib.parse.quote("Account Deleted")}')
    resp.set_cookie('jwt_token', '', expires=0)
    return resp

@application.route('/me')
@authenticate
def me(user):
    return render_template('me.html', user=user, email=user.email, name=user.name, logged_in=True, confirmed=(user.confirmed is not None))

@application.route('/confirm_account')
def confirm():
    state = request.args.get('state')
    name = request.args.get('name')
    user = User.query.filter_by(state=state).first()
    if user.name != name:
        return 'invalid'
    if user.confirmed == 'y':
        return 'already confirmed'
    else:
        user = User.query.get(user.id)
        user.confirmed = 'y'
        db.session.commit()
        email_manager.send_confirmed(user.email, name)
        encoded = jwt.encode({'name': user.name, 'email': user.email}, JWT_SECRET, algorithm='HS256')
        resp = make_response(redirect(f'/me?msg={urllib.parse.quote("email confirmed")}'))
        resp.set_cookie('jwt_token', encoded)
        return resp

@application.route('/send_confirm')
@authenticate
def send_confirm(user):
    email_manager.send_welcome(user.email, user.name, user.state)
    return redirect(f'/me?msg={urllib.parse.quote("Email Resent")}')

if __name__ == '__main__':
    webbrowser.open('127.0.0.1:8888', new=2)
    application.run(port='8888')
