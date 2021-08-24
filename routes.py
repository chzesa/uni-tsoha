from app import app
from flask import redirect, render_template, request, abort
import users
import posts

def error(msg, redirect):
	return render_template("error.html", msg=msg, redirect=redirect);

@app.route("/")
def index():
	return render_template("index.html", threads=posts.get_frontpage_threads())

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

@app.route("/user/<string:username>", methods=["GET"])
def view_profile(username):
	user_posts = posts.get_posts_by_user(username)
	return render_template("user.html", user_posts=user_posts)
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
		return redirect("/topic/" + url)

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
	if not opener:
		return abort(404)
	replies = posts.get_replies(opener["post_id"])
	return render_template("post.html", root=opener, replies=replies)

@app.route("/post/<int:id>", methods=["GET"])
def post(id):
	p = posts.get_post(id)
	if not p or p.status == posts.DELETED_VALUE:
		return error("Post does not exist or it has been deleted.", "/")

	replies = posts.get_replies(id)
	return render_template("post.html", root=p, replies=replies)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
	if not users.is_user():
		return redirect("/login")

	p = posts.get_post(id)
	if not p or p.status == posts.DELETED_VALUE:
		return error("Post does not exist or it has been deleted.", "/")

	if not p.username == users.user_name() and not users.is_admin():
		# TODO check if user has edit rights in sql statement
		return abort(403)

	if request.method == "GET":
		return render_template("edit.html", post=p)

	form = request.form
	if form["csrf_token"] != users.csrf_token():
		return abort(403)

	content = form["content"]

	if not posts.is_valid_post_content(content):
		return error("Replies must be under 1024 characters long.", "/")

	if not posts.update_post_content(id, content, users.user_id()):
		return abort(403)

	return redirect("/thread/" + str(p.thread_id))

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):
	if not users.is_user():
		return redirect("/login")

	p = posts.get_post(id)
	if not p or p.status == posts.DELETED_VALUE:
		return error("Post does not exist or it has been deleted.", "/")

	if not p.username == users.user_name() and not users.is_admin():
		# TODO check if user has edit rights in sql statement
		return abort(403)

	if request.method == "GET":
		return render_template("delete.html", post=p)

	if request.form["csrf_token"] != users.csrf_token():
		return abort(403)

	posts.delete(id)
	if posts.is_opener(id):
		return redirect("/topic/" + p.url)

	return redirect("/thread/" + str(p.thread_id))

@app.route("/hide/<int:id>", methods=["GET", "POST"])
def hide(id):
	if not users.is_user():
		return redirect("/login")

	p = posts.get_post(id)
	if not p or p.status == posts.DELETED_VALUE:
		return error("Post does not exist or it has been deleted.", "/")

	if not users.is_admin():
		# TODO check if user has edit rights in sql statement
		return abort(403)

	if request.method == "GET":
		return render_template("hide.html", post=p)

	if request.form["csrf_token"] != users.csrf_token():
		return abort(403)

	posts.hide(id)
	return redirect("/thread/" + str(p.thread_id))

@app.route("/reply/<int:id>", methods=["GET", "POST"])
def reply(id):
	if not users.is_user():
		return redirect("/login")

	p = posts.get_post(id)
	if not p or p.status == posts.DELETED_VALUE:
		return error("Post does not exist or it has been deleted.", "/")

	if request.method == "GET":
		return redirect("/post/" + str(id))

	form = request.form
	if form["csrf_token"] != users.csrf_token():
		return abort(403)

	content = form["content"]

	if not posts.is_valid_post_content(content):
		return error("Replies must be under 1024 characters long.", "/")

	reply_id = posts.reply(id, content)

	if not reply_id:
		return error("Failed to create thread", "/thread/" + str(p.thread_id))

	if not posts.is_opener(id):
		return redirect("/post/" + str(p.id))

	return redirect("/thread/" + str(p.thread_id))

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

	if not posts.is_valid_post_content(content):
		return error("Posts must have length under 1024 characters.", "/")

	if link == "" and content == "":
		return error("At least one of link and content must not be empty.", "/")

	thread_id = posts.create_thread(url, title, link, content)

	if thread_id != 0:
		return redirect("/thread/" + str(thread_id))

	return error("Failed to create thread.", "/")