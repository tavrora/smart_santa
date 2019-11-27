CREATE TABLE Users (
	id integer PRIMARY KEY AUTOINCREMENT,
	tg_id integer,
	username varchar,
	first_name varchar,
	last_name varchar,
	current_group varchar
);

CREATE TABLE Groups (
	id integer PRIMARY KEY AUTOINCREMENT,
	name varchar,
	link varchar,
	raffle boolean,
	leader_id integer
);

CREATE TABLE Relations_user_group (
	user_id integer,
	group_id integer,
	participation boolean,
	wish text
);

