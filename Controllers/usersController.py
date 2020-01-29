import functools
from flask import Blueprint, g, request, session, flash, jsonify
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.json_util import dumps
from bson.objectid import ObjectId


MONGO_URI='mongodb://localhost:27017/'
MONGO_DBNAME='myApi'
SESSION_TYPE = 'redis'
client = MongoClient()
db = client.myApi
user_bp = Blueprint('user_bp', __name__, url_prefix='/auth')

@user_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        users = db.users
        email = request.json['email']
        password = request.json['password']
        u = users.find_one({'email' : email})
        _hashed_password = generate_password_hash(password)
        error = None
        if u is None:
            error = 'Non Valid Email'
        elif not check_password_hash(_hashed_password, password):
            error = 'Incorrect password'
            return error
        if error is None:
            session.clear()
            session['email'] = u['email']
            session['username'] = u['username']
            return 'logged in'

        flash (error)
        return 'wrong method'
