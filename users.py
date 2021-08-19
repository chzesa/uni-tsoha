from db import db

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import re

def is_valid_username(username):
	return re.match("\\w+", username) and len(username) > 2 and len(username) < 20

def is_valid_password(pwd):
	return len(pwd) > 7 and len(pwd) < 20

def login(username, pwd):
	sql = "SELECT id, pwd_hash FROM users WHERE username = :username;"
	result = db.session.execute(sql, {"username": username})
	user = result.fetchone()

	if user and check_password_hash(user.pwd_hash, pwd):
		session["csrf_token"] = secrets.token_hex(16)
		session["username"] = username
		session["user_id"] = user.id
		return True

	return False

def register(username, pwd):
	pwd_hash = generate_password_hash(pwd)
	sql = """INSERT INTO users (username, pwd_hash, created, is_admin)
		VALUES (:username, :password, NOW(), FALSE);"""

	try:
		db.session.execute(sql, {"username": username, "password": pwd_hash})
		db.session.commit()
	except:
		return False

	return True

def id_from_username(username):
	sql = """SELECT id FROM users WHERE username=:username"""
	result = db.session.execute(sql, {"username": username})
	return result.fetchone()[0]

def logout():
	del session["csrf_token"]
	del session["username"]
	del session["user_id"]

def csrf_token():
	return session.get("csrf_token", "")

def user_id():
	return session.get("user_id", 0);

def user_name():
	return session.get("username", 0);

def is_user():
	return user_id() != 0

def is_admin():
	id = user_id()
	sql = "SELECT is_admin FROM users WHERE id=:id;"
	result = db.session.execute(sql, { "id": id })
	user = result.fetchone()
	return user and user.is_admin
	