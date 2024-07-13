import sqlite3

DATABASE = 'blog.db'

# This system is a full search system. However it relies on title, subtitle, and tldr, and keywords.

def parse_query(query):
    return query.split(' ')