from app import app
from flask import redirect, render_template, request
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

@app.route("/topic/<string:url>")
def topic(url):
	threads = posts.get_threads(url)
	return render_template("topic.html", threads = threads, topic=url )

@app.route("/create_thread", methods=["GET", "POST"])
def create_thread():
	if not users.is_user():
		return redirect("/login")

	if request.method == "GET":
		return render_template("create_thread.html")

	if form["csrf_token"] != users.csrf_token():
		return abort(403)

	form = request.form
	topic = form["topic"]
	title = form["title"]
	url = form["url"]
	content = form["content"]

	post_id = posts.create_thread(topic, title, url, content)

	if post_id != 0:
		return redirect("/topic/" + topic)

	return error("Failed to create thread.", "/")