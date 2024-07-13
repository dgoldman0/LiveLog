from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
import hashlib
import binascii
import llm.tags

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATABASE = 'blog.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
        db.commit()

@app.route('/')
def index():
    conn = get_db_connection()
    blogs = conn.execute('SELECT * FROM blogs').fetchall()
    conn.close()
    return render_template('index.html', blogs=blogs)

@app.route('/user/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        salted_password = request.form['password']
        salt = request.form['salt']

        if not username or not salted_password or not salt:
            flash('Username, password, and salt are required!')
        else:
            conn = get_db_connection()
            # Adds the user and considers teh access key the salted password
            conn.execute('INSERT INTO users (username, access_key, salt) VALUES (?, ?, ?)', (username, salted_password, salt))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

    # Generate a salt
    salt = binascii.hexlify(os.urandom(16)).decode()
    return render_template('register.html', salt=salt)

@app.route('/get_salt', methods=['POST'])
def get_salt():
    username = request.json['username']
    conn = get_db_connection()
    user = conn.execute('SELECT salt FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user:
        return jsonify({'salt': user['salt']})
    else:
        return jsonify({'error': 'User not found'}), 404
    
@app.route('/user/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        salted_password = request.form['password']

        if not username or not salted_password:
            flash('Username and password are required!')
        else:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            if user is None:
                flash('User not found!')
            else:
                if salted_password == user['access_key']:
                    session['user_id'] = user['id']
                    return redirect(url_for('index'))
                else:
                    flash('Invalid password!')

    return render_template('login.html')

@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    conn = get_db_connection()
    blog = conn.execute('SELECT * FROM blogs WHERE id = ?', (blog_id,)).fetchone()
    posts = conn.execute('SELECT * FROM articles WHERE blog_id = ? AND DRAFT = FALSE', (blog_id,)).fetchall()
    conn.close()
    if blog is None:
        return 'Blog not found!'
    return render_template('blog.html', blog=blog, posts=posts)

@app.route('/blog/create', methods=('GET', 'POST'))
def create_blog():
    if request.method == 'POST':
        name = request.form['name']
        user_id = session.get('user_id')

        if not name:
            flash('Name is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO blogs (name, user_id) VALUES (?, ?)', (name, user_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    if session.get('user_id') is None:
        return redirect(url_for('login'))
    return render_template('new_blog.html')

@app.route('/blog/<int:blog_id>/delete', methods=('POST',))
def delete_blog(blog_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM blogs WHERE id = ?', (blog_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/article/create', methods=('GET', ))
def create_article():
    if session.get('user_id') is None:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO articles (author_id) VALUES (?)', (user_id,))
    conn.commit()
    article_id = cursor.lastrowid
    conn.close()
    return redirect(url_for('draft_article', article_id=article_id))

@app.route('/article/<int:article_id>', methods=('GET',))
def view_article(article_id):
    conn = get_db_connection()
    # Need to adjust so that I get the blog id
    article = conn.execute('SELECT * FROM articles WHERE id = ?', (article_id,)).fetchone()
    # Check if article exists. 
    if article is None:
        return render_template('article_not_found.html')
    # Check if the article is in draft or not.
    if article['DRAFT']:
        if article['user_id'] != session.get('user_id'):
            return 'You are not authorized to view this draft!', 403
        return render_template('draft_article.html', article=article)
    # Check what blog the article belongs to, if any. Will be 0 if it doesn't belong to a blog.
    blog_id = conn.execute('SELECT blog_id FROM articles WHERE id = ?', (article_id,)).fetchone()
    conn.close()
    return render_template('article.html', article=article, blog_id=blog_id)

@app.route('/user/<int:user_id>/drafts', methods=('GET',))
def drafts(user_id):
    if session.get('user_id') is None:
        return redirect(url_for('login'))
    conn = get_db_connection()
    drafts = conn.execute('SELECT * FROM articles WHERE user_id = ? AND DRAFT = TRUE', (user_id,)).fetchall()
    conn.close()
    if session.get('user_id') is None:
        return redirect(url_for('login'))
    return render_template('drafts.html', drafts=drafts)

@app.route('/article/<int:article_id>/draft', methods=('GET', 'POST',))
def draft_article(article_id):
    conn = get_db_connection()
    article = conn.execute('SELECT * FROM articles WHERE id = ?', (article_id,)).fetchone()

    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        content = request.form.get('content')

        if title is None or content is None:
            return 'Title and Content are required!', 400
        
        conn.execute("UPDATE articles SET saved_title = ?, saved_subtitle = ?, saved_content = ?, last_saved = datetime('now') WHERE id = ?", (title, subtitle, content, article_id))
        conn.commit()
        conn.close()
        return 'Draft saved successfully', 200
    if session.get('user_id') is None:
        return redirect(url_for('login'))
    return render_template('edit_article.html', article=article)

@app.route('/article/<int:article_id>/post', methods=('POST',))
def post_article(blog_id, article_id):
    conn = get_db_connection()
    article = conn.execute('SELECT * FROM articles WHERE id = ?', (article_id,)).fetchone()

    title = article['saved_title']
    subtitle = article['saved_subtitle']
    content = article['saved_content']

    conn.execute('UPDATE articles SET title = ?, subtitle = ?, content = ? WHERE id = ?', (title, subtitle, content, article_id))
    # Remove old article tags and add generate new ones.
    conn.execute('DELETE FROM tags WHERE article_id = ?', (article_id,))
    tags = llm.tags.generate_tags(content)
    for tag in tags:
        conn.execute('INSERT INTO tags (article_id, tag) VALUES (?, ?)', (article_id, tag.strip()))
    conn.commit()
    conn.close()
    return 'Article posted successfully', 200

@app.route('/article/<int:post_id>/delete', methods=('POST',))
def delete_article(blog_id, article_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM article WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('blog', blog_id=blog_id))

if __name__ == '__main__':
    app.run(debug=True)