DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS blogs;
DROP TABLE IF EXISTS articles;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    access_key TEXT NOT NULL,
    salt TEXT NOT NULL
);

-- Keeps a list of blogs. A user can have multiple blogs.
CREATE TABLE blogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Keeps a list of articles. The saved_* fields are used to store the last saved state of the article in case the user wants to revert to a previous version.
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL DEFAULT '',
    subtitle TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    tldr TEXT NOT NULL DEFAULT '',
    evaluation TEXT NOT NULL DEFAULT '',
    score INTEGER NOT NULL DEFAULT 0,
    saved_title TEXT NOT NULL DEFAULT '',
    saved_subtitle TEXT NOT NULL DEFAULT '',
    saved_content TEXT NOT NULL DEFAULT '',
    author_id INTEGER NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    draft BOOLEAN DEFAULT TRUE,
    last_saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    blog_id INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (blog_id) REFERENCES blogs (id),
    FOREIGN KEY (author_id) REFERENCES users (id)
);

-- Keeps an ongoing list of article revisions and their date. PRIMARY KEY is a composite of article_id and revision_date
CREATE TABLE article_revisions (
    article_id INTEGER NOT NULL,
    revision_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL DEFAULT '',
    subtitle TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    tldr TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (article_id) REFERENCES articles (id),
    PRIMARY KEY (article_id, revision_date)
);

-- A list of additional authors for an article (only one primary author but multiple co-authors are allowed)
CREATE TABLE article_coauthors (
    article_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- A list of all tags
CREATE TABLE tags (
    tag TEXT NOT NULL,
    PRIMARY KEY (tag)
);

-- A list of articles by tag
CREATE TABLE article_tags (
    tag TEXT NOT NULL,
    article_id INTEGER NOT NULL,
    FOREIGN KEY (tag) REFERENCES tags (tag),
    FOREIGN KEY (article_id) REFERENCES articles (id)
);