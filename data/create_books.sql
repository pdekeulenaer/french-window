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
    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
