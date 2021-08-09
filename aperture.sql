CREATE TABLE IF NOT EXISTS guild_prefixes (
    guild_id NUMERIC NOT NULL PRIMARY KEY,
    prefix VARCHAR(5) NOT NULL,
    prefix_case_insensitive BOOLEAN NOT NULL
);