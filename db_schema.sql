BEGIN;
-- fix permissions
GRANT USAGE ON SCHEMA public TO bip_rw, bip_ro;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
   GRANT SELECT ON TABLES TO bip_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bip_ro;
COMMIT;

BEGIN;

CREATE TABLE city (
  city_id SERIAL PRIMARY KEY,
  name varchar(50) -- the longest city name in PL has 31 characters
);

CREATE TABLE councillor (
  councillor_id SERIAL PRIMARY KEY,
  name varchar(256),
  city_id integer REFERENCES city
);

-- CREATE TABLE VoteTopic ();

CREATE TABLE council (
  council_id SERIAL PRIMARY KEY,
  city_id integer REFERENCES city,
  name text  -- "LIII sesja Rady Miasta"
);

CREATE TYPE openess_type_enum AS ENUM ('UNKNOWN', 'PUBLIC', 'SECRET');

CREATE TABLE vote_report (
  vote_report_id SERIAL PRIMARY KEY,
  council_id integer REFERENCES council,
  ordinal_number smallint,
  title text,

  vote_type openess_type_enum DEFAULT 'UNKNOWN',
  date_sec timestamp with time zone,
  entitle smallint DEFAULT 0,
  present smallint DEFAULT 0,
  absent smallint DEFAULT 0,
  UNIQUE (council_id, ordinal_number)  -- could not be two same voting at same council
);

CREATE TYPE vote_type_enum AS ENUM (
  'UNKNOWN', 'IN_FAVOR', 'AGAINST', 'ABSTAIN', 'NO_VOTE', 'ABSENT');

CREATE TABLE councillor_vote (
  councillor_vote_id SERIAL PRIMARY KEY,
  vote_report_id integer REFERENCES vote_report,  --which voting
  councillor_id integer REFERENCES councillor,  -- who
  ordinal_number smallint,
  vote vote_type_enum DEFAULT 'UNKNOWN',
  UNIQUE (vote_report_id, councillor_id)
);

COMMIT;