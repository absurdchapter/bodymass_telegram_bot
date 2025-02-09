--
-- File generated with SQLiteStudio v3.4.15 on Thu Feb 6 16:49:53 2025
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: users_challenges
CREATE TABLE IF NOT EXISTS users_challenges (
    user_id       TEXT (32) PRIMARY KEY
                            UNIQUE ON CONFLICT REPLACE,
    is_active     INTEGER   NOT NULL,
    start_date    DATE      NOT NULL,
    end_date      DATE      NOT NULL,
    start_weight  REAL      NOT NULL,
    target_weight REAL      NOT NULL
);


-- Table: users_conversation
CREATE TABLE IF NOT EXISTS users_conversation (
    user_id            TEXT (32) UNIQUE ON CONFLICT REPLACE,
    conversation_state TEXT
);


-- Table: users_language
CREATE TABLE IF NOT EXISTS users_language (
    user_id  TEXT (32) PRIMARY KEY
                       UNIQUE ON CONFLICT REPLACE,
    language TEXT (32) NOT NULL
);


-- Table: users_mass
CREATE TABLE IF NOT EXISTS users_mass (
    record_id INTEGER,
    user_id   TEXT (32),
    date      DATE      NOT NULL,
    body_mass REAL,
    PRIMARY KEY (
        record_id AUTOINCREMENT
    ),
    CONSTRAINT user_date_constraint UNIQUE (
        user_id,
        date
    )
    ON CONFLICT REPLACE
);


-- Index: user_id_idx
CREATE INDEX IF NOT EXISTS user_id_idx ON users_mass (
    user_id
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
