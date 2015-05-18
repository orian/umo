-- after running psql
CREATE USER bip_rw WITH PASSWORD 'biprw';
CREATE USER bip_ro WITH PASSWORD 'bipro';

CREATE DATABASE template_utf8 WITH TEMPLATE=template0 ENCODING='UTF8';
CREATE DATABASE bip TEMPLATE=template_utf8 WITH OWNER=bip_rw;

GRANT CONNECT ON DATABASE bip TO bip_rw, bip_ro;
GRANT ALL ON DATABASE bip TO bip_rw;