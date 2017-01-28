from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import os
import sendgrid
from sendgrid.helpers.mail import *
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
# TODO: fetch credentials instead of using string as credentials can change under some circumstances (see https://devcenter.heroku.com/articles/connecting-to-heroku-postgres-databases-from-outside-of-heroku)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = "postgres://inpbjnlkzqdkhf:d0a646187c72013be9247400d3abe35c4f3f0360ce657260758c455c9c147cf3@ec2-54-163-234-20.compute-1.amazonaws.com:5432/dfu8hu14lo03hn"
app.debug = True
app.test_request_context().push()
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
# TODO: make actual secret key for app.config
ts = URLSafeTimedSerializer('a really bad secret key')

from models import *
from database_utils import *

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/')
def index():
    return render_template('home.html')

@login_manager.user_loader
def load_user(user_id):
    #Given user_id, return the associated User object
    return Account.query.filter_by(username = user_id).one()

@app.route('/newComparison')
def newComparison():
    return render_template('newComparison.html')


# TODO: rename register and add_user functions to reduce confusion
@app.route('/profile')
@login_required
def profile_page():
    
    namelist = get_user_comparison_names(current_user.id)

    return render_template('profileHomePage.html', name_list=namelist)

@app.route('/myProfile')
@login_required
def myProfile_page():
    return render_template('myProfile.html')

@app.route('/forgotPassword')
def forgotPassword():
    return render_template('forgotPassword.html')

@app.route('/reset_password')
def reset_password():
    data = {}

    # TODO: change api key and move to env variable near final deploy
    emailOrUsername = request.args.get('emailOrUsername')
    try:
        user = Account.query.filter_by(username =emailOrUsername).one()
    except NoResultFound:
        #Search the email column
        try:
            user = Account.query.filter_by(email=emailOrUsername).one()
        except NoResultFound:
            #User not found, inform guest user
            data['error'] = "We couldn't find an associated email address."
            return jsonify(data)

    #User is populated at this point, grab email to send email to
    token = ts.dumps(user.email, salt='recover-key')
    recover_url = url_for('reset_with_token', token=token, _external=True)


    sg = sendgrid.SendGridAPIClient(apikey=os.environ['SENDGRID_API_KEY'])
    from_email = Email("admin@thecomparator.herokuapp.com")
    to_email = Email(user.email)
    subject = "TheComparator: Forgot your password?"
    content = Content("text/plain", "Follow this link to reset your password: " + recover_url)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())

    data['success'] = "You'll receive an email with a link to reset your password shortly."
    return jsonify(data)

@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    change_success = False
    try:
        # link expires after 24 hours (86400 seconds)
        email = ts.loads(token, salt="recover-key", max_age=86400)
        valid_link = True
    except:
        valid_link = False

    if request.method == 'POST':
        user = Account.query.filter_by(email=email).first_or_404()
        set_password(user.id, request.form['password'])
        change_success = True

    return render_template('reset_with_token.html', token=token, valid_link=valid_link, change_success=change_success)

# TODO: consider adding requirements to password (length, character types, etc.)
@app.route('/add_user')
def add_user():
    data = {}
    registerEmail = request.args.get('registerEmail')
    registerUsername = request.args.get('registerUsername')
    registerPassword = request.args.get('registerPassword')

    emailCheck = ""
    usernameCheck = ""
    try:
        emailCheck = Account.query.filter_by(email=registerEmail).one()
    except NoResultFound:
        pass

    try:
        usernameCheck = Account.query.filter_by(username=registerUsername).one()
    except NoResultFound:
        pass

    if emailCheck and usernameCheck:
        data['errorEmailUsername'] = "The email and username are already registered with an account."
    elif emailCheck:
        data['errorEmail'] = "The email is already registered with an account."
    elif usernameCheck:
        data['errorUsername'] = "The username is already registered with an account."

    if data:
        return jsonify(data)
    else:
        # data is empty, no duplicate usernames/emails
        register_user(registerEmail, registerUsername, registerPassword)
        return login_helper(registerUsername, registerPassword)

@app.route('/login')
def login():
    data = {}
    loginUsername = request.args.get('loginUsername')
    loginPassword = request.args.get('loginPassword')

    if validate_login(loginUsername, loginPassword):
        # Login successful
        user = Account.query.filter_by(username = loginUsername).one()
        login_user(user, remember=True)

        data['redirect'] = 'profile'
        return jsonify(data)
    else:
        # Login unsuccessful
        data['error'] = "We couldn't find that username and password."
        return jsonify(data)

def login_helper(loginUsername, loginPassword):
    data = {}

    if validate_login(loginUsername, loginPassword):
        # Login successful
        user = Account.query.filter_by(username = loginUsername).one()
        login_user(user, remember=True)

        data['redirect'] = 'profile'
        return jsonify(data)
    else:
        # Login unsuccessful
        data['error'] = "We couldn't find that username and password."
        return jsonify(data)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('home.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=port, debug=True)
