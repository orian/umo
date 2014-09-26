BEGIN;

CREATE TABLE city (
  city_id SERIAL PRIMARY KEY,
  name varchar(50), -- the longest city name in PL has 31 characters
);

CREATE TABLE councillor (
  councillor_id SERIAL PRIMARY KEY,
  name varchar(256),
  city_id integer REFERENCES city;
);

-- CREATE TABLE VoteTopic ();

CREATE TABLE council (
  council_id SERIAL PRIMARY KEY,
  name text  -- "LIII sesja Rady Miasta"
);

CREATE TYPE openess_type_enum AS ENUM ('UNKNOWN', 'PUBLIC', 'SECRET');

CREATE TABLE vote_report (
  vote_report_id SERIAL PRIMARY KEY,
  council_id integer FOREIGN KEY council,
  ordinal_number smallint,
  title text,

  vote_type openess_type_enum DEFAULT 'UNKNOWN',
  date_sec timestamp with time zone,
  entitle smallint DEFAULT 0,
  present smallint DEFAULT 0,
  absent smallint DEFAULT 0
);

CREATE TYPE vote_type_enum AS ENUM (
  'UNKNOWN', 'IN_FAVOR', 'AGAINST', 'ABSTAIN', 'NO_VOTE', 'ABSENT');

CREATE TABLE councillor_vote (
  councillor_vote_id SERIAL PRIMARY KEY,
  council_id integer FOREIGN KEY council,
  ordinal_number smallint,
  vote vote_type_enum DEFAULT UNKNOWN
);

COMMIT;