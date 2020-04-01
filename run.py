from eve import Eve
from flask import send_from_directory, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import redis
import json

app = Eve(__name__, template_folder="templates", settings='settings.py')
app.config['DEBUG'] = True
r = redis.Redis(decode_responses=True)
mongo = MongoClient()
db = mongo.apitest
cache_posts_key = 'posts'
#db.posts.drop()
#r.delete(cache_posts_key)

def convert_redis_data(data):
    if type(data) is str:
        return json.loads(data)  
    elif type(data) is dict: 
        return json.dumps(data)


def edit_post_from_view(full_post):
    view_post = {}
    view_post['user'] = full_post['user']
    view_post['title'] = full_post['title']
    view_post['link'] = F"http://localhost:5000/post/{str(full_post['_id'])}"
    return view_post

def edit_posts_from_view(full_posts):
    view_posts = []
    for full_post in full_posts:
        view_posts.append(edit_post_from_view(full_post))
    return view_posts


@app.route('/')
def index():
    cache_posts = []
    if not r.lrange(cache_posts_key, 0, r.llen(cache_posts_key)):
        for post_db in db.posts.find():
            view_post = edit_post_from_view(post_db)
            str_post = convert_redis_data(view_post)
            r.rpush(cache_posts_key, str_post)
    if r.lrange(cache_posts_key, 0, r.llen(cache_posts_key)):
        for str_post in r.lrange(cache_posts_key, 0, r.llen(cache_posts_key)):
            dict_post = convert_redis_data(str_post)
            cache_posts.append(dict_post)
    return render_template('index.html', posts = cache_posts)

@app.route('/post')
def post():
    return render_template('post_form.html')

@app.route('/new_post', methods = ['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        new_post = {}
        for key, value in request.form.to_dict().items():
            if key == 'message' or key == 'tags':
                new_post[key] = []
                new_post[key].append(value)
            else:
                new_post[key] = value
        new_post['date'] = datetime.datetime.utcnow()
        db.posts.insert_one(new_post)
        cache_new_post = convert_redis_data(edit_post_from_view(new_post))
        r.rpushx(cache_posts_key, cache_new_post)
        return redirect(url_for('index'))

@app.route('/post/<id>', methods = ['GET', 'POST'])
def post_id(id):
    post = {}
    if request.method == 'GET':
        for key, value in db.posts.find_one({'_id': ObjectId(id)}).items():
            if key == 'message' or key == 'tags':    
                post[F'{key}_len'] = 0
                post[key] = ''
                for v in value:
                    if v != '':
                        post[F'{key}_len'] += 1 
                        post[key] += F'{v}, '
            elif key != 'message_len' or key != 'tags_len':
                post[key] = value 
        return render_template('post.html', post = post)
    if request.method == 'POST':
        new_data = request.form.to_dict()
        if new_data:
            db.posts.update({'_id' : ObjectId(id)}, {'$push' : {'tags' : new_data['tags']}})
            db.posts.update({'_id' : ObjectId(id)}, {'$push' : {'message' : new_data['message']}})
            return redirect(url_for('post_id', id = ObjectId(id)))

# start the app
if __name__ == '__main__':
    app.run()
