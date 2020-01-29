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
articles = db.articles

art_bp = Blueprint('art_bp', __name__)

@art_bp.route('/articles', methods=['GET'])
def get_articles():
    articles = db.articles.find()
    resp = dumps(articles)
    return resp

@art_bp.route('/articles', methods=['POST'])
def write_article():
    articles = db.articles
    title = request.json['title']
    body = request.json['body']
    seconds = time.time()
    local_time = time.ctime(seconds)
    creationDate = local_time
    author = session.get('email')
    if title and body and request.method =='POST':
        art_id = articles.insert({'title' : title, 'body' : body, 'created': local_time, 'author' : author, 'modified' : None})
    else:
        return 'Missing Parameters'
    new_art = articles.find_one({'_id' : art_id})
    output = {'title' : new_art['title'], 'body' : new_art['body'], 'created' : new_art['created'], 'author' : new_art['author'], 'modified' : new_art['modified']}
    return jsonify({str(art_id) : output})

@art_bp.route('/article/<title>', methods=['GET'])
def get_article(title):
    articles = db.articles
    a = articles.find_one({'title' : title})
    art_id = a.get('_id')
    if a :
        output = {'title' : a['title'], 'body' : a['body'], 'created' : a['created'], 'author' : a['author'], 'modified': a['modified']}
    else:
        output = "No such article"
    return jsonify({str(art_id) : output})

@art_bp.route('/article/<id>', methods=['PUT'])
def modify_article(id):
    articles = db.articles
    _id = id
    title = request.json['title']
    body = request.json['body']
    seconds = time.time()
    local_time = time.ctime(seconds)
    modificationDate = local_time
    a = articles.find_one({'_id' : ObjectId(_id)})
    author = session.get('email')
    if author != a['author']:
        return 'Not allowed to modify others articles'
    articles.update_one({'_id' : ObjectId(_id)}, {'$set' : {'title' : title, 'body' : body, 'modified' : modificationDate}})
    a = articles.find_one({'_id' : ObjectId(_id)})
    output = {'title' : a['title'], 'body' : a['body'], 'author' : a['author'], 'created' : a['created'], 'modified' : a['modified']}
    return jsonify({str(_id) : output})

@art_bp.route('/article/<id>', methods=['DELETE'])
def delete_article(id):
    articles = db.articles
    _id = id
    articles.delete_one({'_id' : ObjectId(_id)})
    return 'deleted'
