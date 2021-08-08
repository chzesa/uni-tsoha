from db import db

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

def is_valid_username(username):
	return True

def is_valid_password(pwd):
	return True

def login(username, pwd):
	sql = "SELECT id, pwd_hash FROM users WHERE username = :username;"
	result = db.session.execute(sql, { "username": username })
	user = result.fetchone()

	if user and check_password_hash(user.pwd_hash, pwd):
		session["csrf_token"] = secrets.token_hex(16)
		session["username"] = username
		session["user_id"] = user.id
		return True

	return False

def register(username, pwd):
	pwd_hash = generate_password_hash(pwd)

	try:
		sql = "INSERT INTO users (username, pwd_hash, created, is_admin) VALUES (:username, :password, NOW(), FALSE);"
		db.session.execute(sql, { "username": username, "password": pwd_hash })
		db.session.commit()
	except:
		return False

	return True

def logout():
	del session["csrf_token"]
	del session["username"]
	del session["user_id"]

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
	