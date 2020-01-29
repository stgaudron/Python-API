import functools
from flask import Blueprint, g, request, session, flash, jsonify
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import flask_login
import time
from bson.json_util import dumps
from bson.objectid import ObjectId



MONGO_URI='mongodb://localhost:27017/'
MONGO_DBNAME='myApi'
client = MongoClient()
db = client.myApi
comments = db.comments

com_bp = Blueprint('com_bp', __name__, url_prefix = '/article')

@com_bp.route('/<id>/comments', methods=['GET'])
def get_comments_by_article(id):
    comments = db.comments
    art_id = id
    c =  comments.find({'article' : art_id})
    resp = dumps(c)
    return resp

@com_bp.route('/<id>/comments', methods=['POST'])
def post_comment(id):
    comments = db.comments
    content = request.json['content']
    seconds = time.time()
    local_time = time.ctime(seconds)
    postDate = local_time
    author = session.get('username')
    art_id = id
    if content and request.method =='POST':
        com_id = comments.insert({'content' : content, 'created': local_time, 'author' : author, 'article' : art_id, 'modified' : None})
    else:
        return 'Missing Parameters'
    new_com = comments.find_one({'_id' : com_id})
    output = {'content' : new_com['content'], 'created' : new_com['created'], 'author' : new_com['author'], 'modified' : new_com['modified']}
    return jsonify({str(com_id) : output})

@com_bp.route('/comments/<author>', methods=['GET'])
def get_comments_by_author(author):
    comments = db.comments
    c = comments.find({'author' : author})
    resp = dumps(c)
    return resp

@com_bp.route('/comment/<id>', methods=['PUT'])
def edit_comment(id):
    comments = db.comments
    _id = id
    content = request.json['content']
    seconds = time.time()
    local_time = time.ctime(seconds)
    modificationDate = local_time
    c = comments.find_one({'_id' : ObjectId(_id)})
    author = session.get('username')
    if author != c['author']:
        return "Not allowed to edit others's comments"
    comments.update_one({'_id' : ObjectId(_id)}, {'$set' : {'content' : content, 'modified' : modificationDate}})
    c = comments.find_one({'_id' : ObjectId(_id)})
    output = {'content' : c['content'], 'author' : c['author'], 'created' : c['created'], 'modified' : c['modified']}
    return jsonify({str(_id) : output})

@com_bp.route('/comment/<id>', methods=['DELETE'])
def delete_comment(id):
    comments = db.comments
    _id = id
    comments.delete_one({'_id' : ObjectId(_id)})
    return 'deleted'
