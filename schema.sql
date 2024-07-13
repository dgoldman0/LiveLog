DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS blogs;
DROP TABLE IF EXISTS articles;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    access_key TEXT NOT NULL,
    salt TEXT NOT NULL
);

CREATE TABLE blogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL DEFAULT '',
    subtitle TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    tldr TEXT NOT NULL DEFAULT '',
    saved_title TEXT NOT NULL DEFAULT '',
    saved_subtitle TEXT NOT NULL DEFAULT '',
    saved_content TEXT NOT NULL DEFAULT '',
    author_id INTEGER NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    draft BOOLEAN DEFAULT TRUE,
    last_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    blog_id INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (blog_id) REFERENCES blogs (id)
);

-- A list of additional authors for an article (only one primary author but multiple co-authors are allowed)
CREATE TABLE article_coauthors (
    article_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- A list of tags for an article
CREATE TABLE article_tags (
    article_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles (id)
);
