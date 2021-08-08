from db import db
import users

import validators

def is_valid_topic_title(title):
	return True

def is_valid_topic_url(url):
	return True

def is_valud_thread_title(title):
	return True

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
		)
		INSERT INTO threads(topic_id, title, link, message_id)
		VALUES ((SELECT id FROM topics WHERE url = :topic_url), :title, :url, (SELECT id FROM ins1))
		RETURNING id"""

	try:
		result = db.session.execute(sql, {"user_id": users.user_id(), "content": content, "topic_url": topic_url, "title": title, "url": url })
		db.session.commit()

		return result.fetchone().id
	except:
		return 0


def create_topic(url, title, description):
	if not is_valid_topic_url(url) or not is_valid_topic_title(title):
		return False
	sql = """INSERT INTO topics(url, title, description, created, owner_id)
		VALUES (:url, :title, :description, NOW(), :id);"""

	try:
		result = db.session.execute(sql, {"url": url, "title": title, "description":description, "id": users.user_id()})
		db.session.commit()
		return True
	except:
		return False

def get_threads(topic):
	sql = """SELECT * FROM threads
		RIGHT JOIN (SELECT id FROM topics WHERE topics.url=:topic) AS T1 ON threads.topic_id = T1.id"""
	result = db.session.execute(sql, {"topic": topic})
	return result.fetchall()


def get_posts(thread_id):
	return False

def get_topics():
	sql = "SELECT * FROM topics;"
	result = db.session.execute(sql)
	return result.fetchall()