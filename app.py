from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from data import get_db_connection
import os
import json
import hashlib
import binascii
import llm.articles
import llm.assistant

app = Flask(__name__)
app.secret_key = 'super secret key 12294ffee'

def init_db():
    with app.app_context():
        db = get_db_connection()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf8'))
        # Create a default user. Requires generating a salt and hashing the password.
        salt = binascii.hexlify(os.urandom(16)).decode()
        data = "password" + salt

        # Perform a single SHA-256 hash
        hashed_password = hashlib.sha256(data.encode()).hexdigest()
        db.execute('INSERT INTO users (username, access_key, salt) VALUES (?, ?, ?)', ('admin', hashed_password, salt))
        db.commit()
        db.close()

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

@app.route('/user/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Primary assistant endpoint for web interface. Returns text or markdown, not HTML.
@app.route('/assistant/history', methods=('GET', ))
def get_conversation_history():
    user_id = session.get('user_id')
    if user_id is None:
        return 'User not logged in!', 404
    return llm.assistant.get_conversation_history(user_id)

@app.route('/assistant/message', methods=('POST', ))
def process_message():
    user_id = session.get('user_id')
    if user_id is None:
        return 'User not logged in!', 404
    
    input_text = request.form['user_input']

    response = llm.assistant.process_input(user_id, input_text)
    return jsonify({'response': response})
    

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

# List all tags and their count
@app.route('/tags', methods=('GET',))
def tags():
    conn = get_db_connection()
    tags = conn.execute('SELECT tag, COUNT(article_id) as article_count FROM article_tags GROUP BY tag').fetchall()
    tags = [(tag['tag'], tag['article_count']) for tag in tags]
    conn.close()
    return render_template('tags.html', tags=tags)

# Get articles for a given tag and use the articles template to display them.
@app.route('/tag/<tag>', methods=('GET',))
def tag(tag):
    conn = get_db_connection()
    articles = conn.execute('SELECT articles.id, articles.title, articles.subtitle, articles.tldr FROM articles JOIN article_tags ON articles.id = article_tags.article_id WHERE article_tags.tag = ? AND articles.DRAFT = FALSE', (tag,)).fetchall()
    conn.close()
    return render_template('articles.html', articles=articles)

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
    author = conn.execute('SELECT username FROM users WHERE id = ?', (article['author_id'],)).fetchone()
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
    # Remove the evaluation if the user is not the author
    if session.get('user_id') != article['author_id']:
        article['evaluation'] = None
    return render_template('article.html', article=article, blog_id=blog_id, author=author, user_id = session.get('user_id'))

@app.route('/user/<int:user_id>/articles', methods=('GET',))
def articles(user_id):
    conn = get_db_connection()
    articles = conn.execute('SELECT id, title, subtitle, tldr FROM articles WHERE author_id = ? AND DRAFT = FALSE', (user_id,)).fetchall()
    conn.close()
    return render_template('articles.html', articles=articles)

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

# Going to need to use Celery because things like article evaluation and tag generation can take a long time.
@app.route('/article/<int:article_id>/post', methods=('POST',))
def post_article(article_id):
    conn = get_db_connection()
    article = conn.execute('SELECT * FROM articles WHERE id = ?', (article_id,)).fetchone()
    if article is None:
        return 'Article not found!', 404
    # Run a new query to see if there are any changes to the article title, subtitle, or content.
    if article['title'] == article['saved_title'] and article['subtitle'] == article['saved_subtitle'] and article['content'] == article['saved_content']:
        return 'No changes to post!', 304    
    title = article['saved_title']
    subtitle = article['saved_subtitle']
    content = article['saved_content']

    tldr = llm.articles.generate_tldr(content)
 
   # Build a dictionary of tags and how many articles they are associated with. We can do that by looking at article_tags.
    query = """
        SELECT tag, COUNT(article_id) as article_count
        FROM article_tags
        GROUP BY tag"""    
    results = conn.execute(query).fetchall()
    all_tags = {row[0]: row[1] for row in results}

    tags = llm.articles.generate_tags(content, all_tags)
 
    evaluation, score = llm.articles.evaluate_article(content)
    if score == 0:
        return 'Article quality is too low to post!', 400
    conn.execute('UPDATE articles SET title = ?, subtitle = ?, content = ?, tldr = ?, evaluation = ?, score = ?, DRAFT = FALSE WHERE id = ?', (title, subtitle, content, tldr, evaluation, score,  article_id))
    
    conn.execute('UPDATE articles SET title = ?, subtitle = ?, content = ?, tldr = ?, DRAFT = FALSE WHERE id = ?', (title, subtitle, content, tldr, article_id))
    # Remove old article tags and add generate new ones.
    conn.execute('DELETE FROM article_tags WHERE article_id = ?', (article_id,))
 
    for tag in tags:
        # Set article's tags
        conn.execute('INSERT INTO article_tags (article_id, tag) VALUES (?, ?)', (article_id, tag.strip()))
        # Add tag to main tag list if none.
        conn.execute('INSERT OR IGNORE INTO tags (tag) VALUES (?)', (tag.strip(),))
    # Add to revision history
    conn.execute('INSERT INTO article_revisions (article_id, title, subtitle, content, tldr) VALUES (?, ?, ?, ?, ?)', (article_id, title, subtitle, content, tldr))
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