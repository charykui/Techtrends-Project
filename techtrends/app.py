#By: Charity Chepkirui
#Code References: Parts of code referenced from https://stackoverflow.com/questions/16061641/python-logging-split-between-stdout-and-stderr,
                  #Udacity Cloud Native course
                  #https://github.com/kevshakes/techtrends

import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import sys
import logging

logger = logging.getLogger('Project-Techtrends')
logger.setLevel(logging.DEBUG)
formatter= logging.Formatter('%(asctime)s -%(levelname)- %(message)s ')

print(logging.getLevelName(logger.level))
if logging.getLevelName(logger.level) == 'DEBUG':
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.getLevelName(logger.level))
    logger.addHandler(console_handler)
else:
    eh = logging.StreamHandler(sys.stderr)
    eh.setFormatter(formatter)
    eh.setLevel(logging.getLevelName(logger.level))
    logger.addHandler(eh)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

#check app health
@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Status request successfull')
    return response

@app.route('/metrics')
def metrics():
    response = app.response_class(
            response=json.dumps({"status":"success","data":{"db_connection_count":count(get_db_connection()),"post_count":count(get_post())}}),
            status=200,
            mimetype='application/json'
    )

    app.logger.info('Metrics request successfull')
    return response

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logger.error(
            'Article requested does not exist!'.format(id=post_id))
      return render_template('404.html'), 404
      
    else:
      logger.info('Article "{title}" retrieved Successfully!'.format(title=post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('The About page has been opened successfully')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info('Article "{title}" created successfully!'.format(title=title))
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
  # logging.basicConfig(filename='app.log',level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
