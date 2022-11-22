import base64

from flask import Blueprint, render_template, redirect, session, request, url_for
from flask_login import LoginManager, login_required, logout_user
from http import HTTPStatus
import pymongo
from classes.User import User
from datetime import datetime
import dateutil.parser
import pytz
import hashlib
import dateutil.parser
import jwt
from dateutil.relativedelta import relativedelta
from bson.objectid import ObjectId

api = Blueprint('api', __name__, url_prefix='/api', static_folder='api/static')
login_manager = LoginManager(api)
myclient = pymongo.MongoClient("mongodb://mongouser:123321@localhost:27017/")
# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["PersonalTrainer"]
users_table = mydb["Users"]
login_logs_table = mydb["LoginLogs"]
videos_table = mydb["Videos"]
promo_codes_table = mydb["PromoCodes"]


@login_manager.user_loader
def load_user(username):
    return users_table.find_one({"_id": username})


@api.route("/logout")
@login_required
def logout():
    logout_user()
    return HTTPStatus.OK


@login_manager.request_loader
def load_user_from_request(request):

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


@api.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        json_request = request.get_json()
        username = json_request.get("username")
        password = json_request.get("password")

        hashed_password = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            password.encode('utf-8'), # Convert the password to bytes
            username.encode('utf-8'), # Provide the salt
            100000, # It is recommended to use at least 100,000 iterations of SHA-256
            dklen=128 # Get a 128 byte key
        )
        user = users_table.find_one({"_id": username})
        if user:
            if hashed_password == user["password"]:
                del user['password']
                session["user"] = user
                update_last_login_time(user)
                login_logs_table.insert_one({"username": username, "time": datetime.now()})
                return user
            else:
                login_logs_table.insert_one({"username": username, "errorMessage": "Wrong Password", "time": datetime.now()})
                return "Wrong Password"
        else:
            return "User Not Found"
    else:
        return render_template("login.html")


def update_last_login_time(user_dict):
    user_filter = {'_id': user_dict.get('_id')}
    newvalues = {"$set": {"lastLoginDate": datetime.now()}}
    users_table.update_one(user_filter, newvalues)
