BEGIN TRANSACTION;
CREATE TABLE wishlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    publish_date DATE DEFAULT '1900-01-01',
    summary TEXT NULL,
    notes TEXT NULL,
    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE watchlist ( id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
author_id INTEGER NOT NULL);
CREATE TABLE users (id integer primary key autoincrement, name varchar(255), password varchar(255), email varchar(255), level varchar(255));
CREATE TABLE series (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255) NOT NULL, description TEXT NULL);
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NULL,
    isbn10 VARCHAR(25) NULL,
    isbn13 VARCHAR(25) NULL,
    publisher VARCHAR(255) NULL,
    publish_date DATE NULL,
    language VARCHAR(10) NULL,
    series_id INTEGER NOT NULL default -1,
    series_nr VARCHAR(10) default 1,
    is_series VARCHAR(10) default 'False',
    in_library INTEGER NULL default 1,
    in_wishlist INTEGER NULL default 0,
    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE authors
( id INTEGER PRIMARY KEY AUTOINCREMENT,
name VARCHAR(255));
COMMIT;
