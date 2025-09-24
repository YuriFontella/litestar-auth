CREATE TABLE IF NOT EXISTS sessions (
    uuid uuid PRIMARY KEY NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
    access_token text NOT NULL,
    user_agent text,
    ip varchar(255),
    revoked bool DEFAULT false,
    user_uuid uuid NOT NULL REFERENCES users (uuid) ON DELETE CASCADE,
    type varchar NOT NULL DEFAULT 'manual',
    date timestamp with time zone DEFAULT current_timestamp
);

ALTER TABLE sessions ADD CONSTRAINT uq_sessions_access_token UNIQUE (access_token);
