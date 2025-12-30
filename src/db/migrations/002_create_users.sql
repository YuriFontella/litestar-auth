DROP TYPE IF EXISTS role_type CASCADE;
CREATE TYPE role_type AS ENUM ('USER', 'ADMIN');

CREATE TABLE IF NOT EXISTS users (
  uuid uuid PRIMARY KEY NOT NULL UNIQUE DEFAULT uuid_generate_v4(),
  name varchar NOT NULL,
  email varchar NOT NULL,
  password varchar NOT NULL,
  role role_type NOT NULL DEFAULT 'USER',
  avatar text,
  fingerprint integer NOT NULL,
  status bool DEFAULT true,
  created_at timestamp with time zone DEFAULT current_timestamp,
  updated_at timestamp with time zone DEFAULT current_timestamp
);

ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT uq_users_fingerprint UNIQUE (fingerprint);

CREATE INDEX IF NOT EXISTS users_index_email ON users (email ASC);
CREATE INDEX IF NOT EXISTS users_index_created_at ON users (created_at DESC);
CREATE INDEX IF NOT EXISTS users_index_status_created_at ON users (status, created_at DESC);
