CREATE TABLE users
(
	id SERIAL PRIMARY KEY
	, username TEXT UNIQUE NOT NULL
	, pwd_hash TEXT NOT NULL
	, created TIMESTAMP
	, is_admin BOOLEAN
);

CREATE TABLE topics
(
	id SERIAL PRIMARY KEY
	, url TEXT UNIQUE NOT NULL
	, title TEXT NOT NULL
	, description TEXT
	, created TIMESTAMP NOT NULL
	, owner_id INTEGER REFERENCES users(id) NOT NULL
);

CREATE TABLE post_status
(
	id INTEGER PRIMARY KEY
	, description TEXT NOT NULL
);

INSERT INTO post_status (id, description) VALUES(1, 'normal');
INSERT INTO post_status (id, description) VALUES(2, 'hidden');
INSERT INTO post_status (id, description) VALUES(3, 'deleted');

CREATE TABLE posts
(
	id SERIAL PRIMARY KEY
	, user_id INTEGER REFERENCES users(id) NOT NULL
	, parent_id INTEGER REFERENCES posts(id)
	, created TIMESTAMP NOT NULL
	, status INTEGER REFERENCES post_status(id) NOT NULL
);

CREATE TABLE threads
(
	id SERIAL PRIMARY KEY
	, topic_id INTEGER REFERENCES topics(id) NOT NULL
	, title TEXT NOT NULL
	, link TEXT
	, message_id INTEGER REFERENCES posts(id) NOT NULL
);

CREATE TABLE content
(
	id SERIAL PRIMARY KEY
	, content TEXT NOT NULL
	, edited TIMESTAMP NOT NULL
	, edited_by INTEGER REFERENCES users(id) NOT NULL
	, post_id INTEGER REFERENCES posts(id) NOT NULL
);

CREATE TABLE thread_post
(
	post_id INTEGER REFERENCES posts(id) NOT NULL
	, thread_id INTEGER REFERENCES threads(id) NOT NULL
	, PRIMARY KEY (post_id, thread_id)
);
