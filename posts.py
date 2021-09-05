from db import db
import users

import re
import validators

NORMAL_VALUE = 1
HIDDEN_VALUE = 2
DELETED_VALUE = 3

def is_valid_topic_title(title):
    return re.match("\\S", title) and len(title) < 128

def is_valid_topic_url(url):
    return re.match("\\w+", url) and len(url) > 2 and len(url) < 24

def is_valid_thread_title(title):
    return re.match("\\S", title) and len(title) < 128

def is_valid_thread_link(url):
    return validators.url(url)

def is_valid_post_content(content):
    return re.match("\\S", content) and len(content) < 1024

def create_thread(topic_url, title, url, content):
    sql = """
        WITH
        ins1 AS (
            INSERT INTO posts(user_id, created, status)
            VALUES (:user_id, NOW(), :status)
            RETURNING id
        )
        , ins2 AS (
            INSERT INTO content(content, edited, edited_by, post_id)
            VALUES (:content, NOW(), :user_id, (SELECT id FROM ins1))
            RETURNING post_id
        ), ins3 AS (
            INSERT INTO threads(topic_id, title, link, message_id)
            VALUES ((SELECT id FROM topics WHERE url = :topic_url), :title, :url, (SELECT id FROM ins1))
            RETURNING id
        )
        INSERT INTO thread_post(post_id, thread_id) VALUES ((SELECT id FROM ins1), (select id from ins3))
        RETURNING thread_id
        """

    try:
        result = db.session.execute(sql, {
            "user_id": users.user_id(),
            "content": content,
            "topic_url": topic_url,
            "title": title,
            "url": url,
            "status": NORMAL_VALUE
        })
        db.session.commit()

        return result.fetchone().thread_id
    except:
        return 0


def create_topic(url, title, description):
    if not is_valid_topic_url(url) or not is_valid_topic_title(title):
        return False

    sql = """
        INSERT INTO topics(url, title, description, created, owner_id)
        VALUES (:url, :title, :description, NOW(), :id)
        RETURNING id
        """

    result = db.session.execute(sql, {"url": url, "title": title, "description":description, "id": users.user_id()})
    db.session.commit()
    return result.fetchone().id

def get_threads(topic):
    sql = """
        SELECT threads.id, threads.title, threads.link, topics.url, users.username,
            posts.created, COUNT(thread_post.post_id) - 1 AS comment_count FROM threads
        LEFT JOIN topics ON threads.topic_id=topics.id
        LEFT JOIN posts ON threads.message_id=posts.id
        LEFT JOIN users ON posts.user_id=users.id
        LEFT JOIN thread_post ON thread_post.thread_id=threads.id
        WHERE posts.status!=:status AND topics.url=:topic
        GROUP BY threads.id, topics.url, users.username, posts.created
        ORDER BY posts.created DESC
        """
    result = db.session.execute(sql, {"topic": topic, "status": DELETED_VALUE})
    return result.fetchall()

def get_frontpage_threads():
    sql = """
        SELECT threads.id, threads.title, threads.link, topics.url, users.username,
            posts.created, COUNT(thread_post.post_id) - 1 AS comment_count FROM threads
        LEFT JOIN topics ON threads.topic_id=topics.id
        LEFT JOIN posts ON threads.message_id=posts.id
        LEFT JOIN users ON posts.user_id=users.id
        LEFT JOIN thread_post ON thread_post.thread_id=threads.id
        WHERE posts.status=:status
        GROUP BY threads.id, topics.url, users.username, posts.created
        ORDER BY posts.created DESC
        LIMIT 50
        """
    result = db.session.execute(sql, {"status": NORMAL_VALUE})
    return result.fetchall()

def get_thread(thread_id):
    sql = """
        SELECT posts.id, posts.status, users.username, posts.created, content.content,
            T1.title, T1.link, T1.message_id AS opener_id, topics.url, topics.title AS topic_title
        FROM (SELECT title, link, message_id, topic_id FROM threads WHERE threads.id = :thread_id) AS T1
        LEFT JOIN topics ON T1.topic_id = topics.id
        LEFT JOIN posts ON T1.message_id = posts.id
        LEFT JOIN content ON content.post_id = posts.id
        LEFT JOIN users ON posts.user_id = users.id
        ORDER BY content.edited DESC
        """
    result = db.session.execute(sql, {"thread_id": thread_id})
    return result.fetchone()

def thread_id_from_post_id(id):
    sql = """SELECT thread_id FROM thread_post WHERE post_id=:id"""
    result = db.session.execute(sql, {"id": id})
    return result.fetchone()[0]

def get_replies(post_id):
    # Could also be done by using thread_post table but that's less interesting
    sql = """
        WITH RECURSIVE T1
            (id, user_id, parent_id, created, status, level)
        AS (
            SELECT id, user_id, parent_id, created, status, 1 FROM posts WHERE parent_id=:post_id
            UNION ALL
            SELECT posts.id, posts.user_id, posts.parent_id, posts.created, posts.status, T1.level + 1 FROM posts, T1
            WHERE posts.parent_id = T1.id
        )
        SELECT T2.content, username, T1.id, T1.parent_id, T1.status, T1.created, level FROM T1
        LEFT JOIN (SELECT DISTINCT ON (post_id) post_id, edited, content FROM content ORDER BY content.post_id, content.edited DESC) AS T2 ON T2.post_id = T1.id
        LEFT JOIN users ON users.id = T1.user_id
        """
    result = db.session.execute(sql, {"post_id": post_id})
    rows = result.fetchall()
    return rows

def get_post(post_id):
    sql = """
        SELECT posts.id, posts.status, users.username, posts.created, content.content,
            content.edited, thread_post.thread_id, threads.title, threads.link,
            threads.message_id AS opener_id, topics.url, topics.title AS topic_title FROM posts
        LEFT JOIN users ON users.id = posts.user_id
        LEFT JOIN content ON content.post_id = posts.id
        LEFT JOIN thread_post ON posts.id = thread_post.post_id
        LEFT JOIN threads ON thread_post.thread_id = threads.id
        LEFT JOIN topics ON threads.topic_id = topics.id
        WHERE posts.id=:id
        ORDER BY content.edited DESC
        """

    result = db.session.execute(sql, {"id": post_id})
    return result.fetchone()

def get_posts_by_user(username):
    user_id = users.id_from_username(username)
    # The outer query is only used to reorder the inner query.
    sql = """
        SELECT * FROM (
            SELECT DISTINCT ON (content.post_id) posts.id, posts.status, posts.created,
                users.username, content.content, content.edited, thread_post.thread_id,
                threads.title, threads.link, threads.message_id, topics.url FROM posts
            LEFT JOIN users ON users.id = posts.user_id
            LEFT JOIN content ON content.post_id = posts.id
            LEFT JOIN thread_post ON posts.id = thread_post.post_id
            LEFT JOIN threads ON thread_post.thread_id = threads.id
            LEFT JOIN topics ON threads.topic_id = topics.id
            WHERE users.id=:user_id AND posts.status!=:status
            ORDER BY content.post_id, content.edited DESC
        ) AS T
        ORDER BY T.created DESC
        """

    result = db.session.execute(sql, {"user_id": user_id, "status": DELETED_VALUE})
    return result.fetchall()

def update_post_content(post_id, content, editor_id):
    sql = """
        INSERT INTO content (content, edited, edited_by, post_id)
        VALUES (:content, NOW(), :editor_id, :post_id)
        """
    try:
        result = db.session.execute(sql, {"content": content, "post_id": post_id, "editor_id": editor_id})
        db.session.commit()
        return True
    except:
        return False

def reply(post_id, content):
    sql = """
        WITH
        ins1 AS (
            INSERT INTO posts(user_id, created, parent_id, status)
            VALUES (:user_id, NOW(), :post_id, :status)
            RETURNING id
        ), ins2 AS (
            INSERT INTO content(content, edited, edited_by, post_id)
            VALUES (:content, NOW(), :user_id, (SELECT id FROM ins1))
            RETURNING post_id
        )
        INSERT INTO thread_post(post_id, thread_id)
        VALUES (
            (SELECT id FROM ins1),
            (SELECT thread_id FROM thread_post WHERE post_id=:post_id)
        ) RETURNING post_id
        """

    result = db.session.execute(sql, {"user_id": users.user_id(), "post_id": post_id, "content": content, "status": NORMAL_VALUE})
    db.session.commit()
    return result.fetchone()

def delete(post_id):
    sql = """UPDATE posts SET status=:status WHERE posts.id=:post_id"""
    result = db.session.execute(sql, {"post_id": post_id, "status": DELETED_VALUE})
    db.session.commit()

def hide(post_id):
    sql = """UPDATE posts SET status=:status WHERE posts.id=:post_id"""
    result = db.session.execute(sql, {"post_id": post_id, "status": HIDDEN_VALUE})
    db.session.commit()

def is_opener(post_id):
    sql = """SELECT id FROM posts WHERE id=:post_id AND parent_id IS NULL"""
    result = db.session.execute(sql, {"post_id": post_id})
    return result.fetchone() != None

def get_topics():
    sql = "SELECT url, title, description FROM topics"
    result = db.session.execute(sql)
    return result.fetchall()