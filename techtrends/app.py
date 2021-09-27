#By: Charity Chepkirui
#Code References: Parts of code referenced from https://stackoverflow.com/questions/16061641/python-logging-split-between-stdout-and-stderr,
                  #Udacity Cloud Native course

import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from os import sys
from datetime import datetime
import logging


DB_CONN_COUNTER = 0

def initialize_logger():
    logger = logging.getLogger("__name__")
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)
    
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    logger.addHandler(stderr_handler)
    
    logging.basicConfig(
        format='%(levelname)s:%(name)s:%(asctime)s - %(message)s',
                level=logging.DEBUG
    )

     
# Function to get a database connection.
# This function connects to database with the name `database.db`

def get_db_connection():
    global DB_CONN_COUNTER 
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    DB_CONN_COUNTER += 1
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

    connection= get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    post_count = len(posts)
    connection.close()
    metrics= {"db_connection_count": DB_CONN_COUNTER, "post_count": post_count}
    return metrics
    

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
      app.logger.error("Article id {} requested does not exist!" .format(post['post_id']))
      return render_template('404.html'), 404
      
    else:
      app.logger.info("Article title {} Accessed Successfully!".format(post['title']))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('The About page has been Accessed successfully')
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
            app.logger.info('Article title %s created successfully!',title )
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":

   initialize_logger()
  
   app.run(host='0.0.0.0', port='3111')
