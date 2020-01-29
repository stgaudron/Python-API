#!/usr/bin/python3
from flask import Flask, request, jsonify, json, render_template
import pymongo
from pymongo import MongoClient
from .Config import db
from bson.json_util import dumps
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask('My API')
app.config.from_pyfile('Config/db.py')
app.secret_key ='SECRET KEY'
client = MongoClient()
db = client.myApi
users = db.users

@app.route('/')
def welcome():
    return render_template('welcomeview.html')

@app.route('/users', methods=['GET'])
def get_users():
    users = db.users.find()
    resp = dumps(users)
    return resp


@app.route('/users', methods=['POST'])
def add_user():
    users = db.users
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    if username and email and password and request.method == 'POST':
        _hashed_password = generate_password_hash(password)
    user_id = users.insert({'username' : username, 'email' : email, 'pwd' : _hashed_password})
    new_user = users.find_one({'_id' : user_id})
    output = {'username' : new_user['username'], 'email' : new_user['email'], 'pwd' : new_user['pwd']}
    return jsonify({str(user_id) : output})

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    users = db.users
    u = users.find_one({'username' : username})
    _id = u.get('_id')
    if u :
        output = {'username' : u['username'], 'email' : u['email'], 'pwd' : u['pwd']}
    else:
        output = "No such username"
    return jsonify({str(_id) : output})

@app.route('/user/<id>', methods=['PUT'])
def modify_user(id):
    users = db.users
    _id = id
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    if username and email and password and request.method == 'PUT':
        _hashed_password = generate_password_hash(password)
    users.update_one({'_id' : ObjectId(_id)}, {'$set': {'username' : username, 'email' : email, 'pwd' : _hashed_password}})
    u = users.find_one({'username' : username})
    output = {'username' : u['username'], 'email' : u['email'], 'pwd' : u['pwd']}
    return jsonify({str(_id) : output})

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    users = db.users
    _id = id
    users.delete_one({'_id' : ObjectId(_id)})
    return 'deleted'


from .Controllers import usersController
app.register_blueprint(usersController.user_bp)

from .Controllers import articlesController
app.register_blueprint(articlesController.art_bp)

from .Controllers import commentsController
app.register_blueprint(commentsController.com_bp)
