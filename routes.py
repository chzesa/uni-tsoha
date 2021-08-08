from app import app
from flask import redirect, render_template, request, abort
import users
import posts

def error(msg, redirect):
	return render_template("error.html");

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")

	if users.is_user():
		return abort(403)

	form = request.form
	user = form["username"]
	pwd = form["password"]
	pwd_confirm = form["password_confirm"]

	if pwd != pwd_confirm:
		return error("Passwords do not match.", "/")

	if not users.is_valid_username(user):
		return error("Invalid username.", "/")

	if not users.is_valid_password(pwd):
		return error("Invalid password.", "/")

	if users.register(user, pwd):
		return redirect("/")

	return error("Registration failed.", "/")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")

	if users.is_user():
		return abort(403)

	form = request.form
	user = form["username"]
	pwd = form["password"]

	if users.login(user, pwd):
		return redirect("/")
	
	return error("Login failed.", "/login");

@app.route("/logout", methods=["GET", "POST"])
def logout():
	users.logout()
	return redirect("/")

@app.route("/create_topic", methods=["GET", "POST"])
def create_topic():
	if not users.is_user():
		return redirect("/login")

	if request.method == "GET":
		return render_template("create_topic.html")

	form = request.form
	url = form["url"]
	title = form["title"]
	description = form["description"]

	if form["csrf_token"] != users.csrf_token():
		return abort(403)

	if not posts.is_valid_topic_url(url):
		return error("Invalid topic url.", "/")

	if not posts.is_valid_topic_title(title):
		return error("Invalid topic title.", "/")

	topic_id = posts.create_topic(url, title, description)
	if topic_id != 0:
		return redirect("/topic/" + str(topic_id))

	return error("Failed to create topic.", "/")

@app.route("/topics", methods=["GET"])
def topics():
	topics = posts.get_topics()
	return render_template("topics.html", topics = topics)

@app.route("/topic/<string:url>", methods=["GET"])
def topic(url):
	threads = posts.get_threads(url)
	return render_template("topic.html", threads = threads, topic=url )

@app.route("/thread/<int:id>", methods=["GET"])
def thread(id):
	opener = posts.get_thread(id)
	replies = posts.get_replies(opener["post_id"])
	return render_template("thread.html", opener=opener, replies=replies)

@app.route("/reply/<int:id>", methods=["POST"])
def reply(id):
	if not users.is_user():
		return redirect("/login")

	if not posts.is_opener(id):
		return abort(403)

	form = request.form
	if form["csrf_token"] != users.csrf_token():
		return abort(403)

	content = form["content"]

	if not posts.is_valid_post_content(content):
		return error("Replies must be under 1024 characters long.", "/")

	posts.reply(id, content)
	thread_id = posts.thread_id_from_opener_id(id)
	return redirect("/thread/" + str(thread_id))

@app.route("/create_thread/<string:url>", methods=["GET", "POST"])
def create_thread(url):
	if not users.is_user():
		return redirect("/login")

	if request.method == "GET":
		return render_template("create_thread.html", topic=url)

	form = request.form

	if form["csrf_token"] != users.csrf_token():
		return abort(403)

	title = form["title"]
	link = form["link"]
	content = form["content"]

	if not posts.is_valid_thread_title(title):
		return error("Invalid thread title.", "/")

	if link != "" and not posts.is_valid_thread_link(link):
		return error("Malformed link url", "/")

	if link == "" and not posts.is_valid_post_content(content):
		return error("Threads must have either a valid url or valid content")

	post_id = posts.create_thread(url, title, link, content)

	if post_id != 0:
		return redirect("/topic/" + url)

	return error("Failed to create thread.", "/")