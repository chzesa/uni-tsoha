from db import db
import users

import re
import validators

def is_valid_topic_title(title):
	return title != "" and len(title) < 128

def is_valid_topic_url(url):
	return re.match("\\w+", url) and len(url) > 2 and len(url) < 24

def is_valid_thread_title(title):
	return title != "" and len(title) < 128

def is_valid_thread_link(url):
	return validators.url(url)

def is_valid_post_content(content):
	return len(content) < 1024

def create_thread(topic_url, title, url, content):
	sql = """WITH
		ins1 AS (
			INSERT INTO posts(user_id, created)
			VALUES (:user_id, NOW())
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
		RETURNING thread_id"""

	try:
		result = db.session.execute(sql, {"user_id": users.user_id(), "content": content, "topic_url": topic_url, "title": title, "url": url })
		db.session.commit()

		return result.fetchone().thread_id
	except:
		return 0


def create_topic(url, title, description):
	if not is_valid_topic_url(url) or not is_valid_topic_title(title):
		return False

	sql = """INSERT INTO topics(url, title, description, created, owner_id)
		VALUES (:url, :title, :description, NOW(), :id)
		RETURNING id"""

	result = db.session.execute(sql, {"url": url, "title": title, "description":description, "id": users.user_id()})
	db.session.commit()
	return result.fetchone().id

def get_threads(topic):
	sql = """SELECT threads.id, threads.title, threads.link FROM threads
		RIGHT JOIN (SELECT id FROM topics WHERE topics.url=:topic) AS T1 ON threads.topic_id = T1.id
		LEFT JOIN posts ON threads.message_id = posts.id
		ORDER BY posts.created DESC"""
	result = db.session.execute(sql, {"topic": topic})
	return result.fetchall()


def get_thread(thread_id):
	sql = """SELECT posts.id, users.username, content.content, T1.title, T1.link, topics.url, topics.title
		FROM (SELECT * FROM threads WHERE threads.id = :thread_id) AS T1
		LEFT JOIN topics ON T1.topic_id = topics.id
		LEFT JOIN posts ON T1.message_id = posts.id
		LEFT JOIN content ON content.post_id = posts.id
		LEFT JOIN users ON posts.user_id = users.id
		ORDER BY content.edited DESC"""
	result = db.session.execute(sql, {"thread_id": thread_id})
	row = result.fetchone()
	return {
		"post_id": row.id,
		"username": row.username,
		"content": row.content,
		"title": row[3],
		"link": row.link,
		"url": row.url,
		"topic_title": row[6]
	}

def thread_id_from_post_id(id):
	sql = """SELECT thread_id FROM thread_post WHERE post_id=:id"""
	result = db.session.execute(sql, {"id": id})
	return result.fetchone()[0]

def get_replies(post_id):
	sql = """SELECT content, username, T2.id FROM
		(SELECT content, user_id, T1.id FROM
			(SELECT id, user_id FROM posts WHERE posts.parent_id = :post_id) AS T1
			LEFT JOIN content ON T1.id = content.post_id
		) AS T2
		LEFT JOIN users ON users.id = T2.user_id"""
	result = db.session.execute(sql, {"post_id": post_id})
	rows = result.fetchall()
	return rows

def get_post(post_id):
	sql = """SELECT posts.id, username, content, edited FROM posts
		LEFT JOIN users ON users.id=posts.user_id
		LEFT JOIN content ON content.post_id = posts.id
		WHERE posts.id=:id"""

	result = db.session.execute(sql, {"id": post_id})
	return result.fetchone()

def get_posts_by_user(username):
	user_id = users.id_from_username(username)
	sql = """SELECT * FROM posts
		LEFT JOIN content ON content.post_id = posts.id
		LEFT JOIN thread_post ON thread_post.post_id = posts.id
		LEFT JOIN (
			SELECT threads.id, threads.title, url FROM threads
			LEFT JOIN topics ON threads.topic_id = topics.id
		)
		AS T1 ON T1.id = thread_post.thread_id
		WHERE user_id=:user_id
		ORDER BY posts.created DESC"""

	result = db.session.execute(sql, {"user_id": user_id})
	return result.fetchall()


def reply(post_id, content):
	sql = """WITH
		ins1 AS (
			INSERT INTO posts(user_id, created, parent_id)
			VALUES (:user_id, NOW(), :post_id)
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
		) RETURNING post_id"""

	result = db.session.execute(sql, {"user_id": users.user_id(), "post_id": post_id, "content": content})
	db.session.commit()
	return result.fetchone()

def is_opener(post_id):
	sql = """SELECT parent_id FROM posts WHERE id=:post_id AND parent_id=NULL"""
	result = db.session.execute(sql, {"post_id": post_id})
	return result.fetchone() == None

def get_topics():
	sql = "SELECT url, title, description FROM topics;"
	result = db.session.execute(sql)
	return result.fetchall()