-- lookup tables:
--   landlords
--   properties

CREATE TABLE IF NOT EXISTS landlords (
    ll_id VARCHAR(6) UNIQUE NOT NULL,
    PRIMARY KEY(ll_id)
    );

CREATE TABLE IF NOT EXISTS properties (
    prop_id VARCHAR(7) UNIQUE NOT NULL,
    ll_id VARCHAR(6) NOT NULL REFERENCES landlords(ll_id),
    flat_num VARCHAR(3) NOT NULL,
    street VARCHAR(60) NOT NULL,
    post_code VARCHAR(10) NOT NULL,
    city VARCHAR(20) NOT NULL,
    PRIMARY KEY(prop_id)
    );

CREATE TABLE IF NOT EXISTS tenants (
    prop_id VARCHAR(7) NOT NULL REFERENCES properties(prop_id),
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    email VARCHAR(60),
    PRIMARY KEY(email)
    );

CREATE TABLE IF NOT EXISTS documents (
    doc_id SERIAL UNIQUE NOT NULL,
    prop_id VARCHAR(7) NOT NULL REFERENCES properties(prop_id),
    email VARCHAR(60) NOT NULL REFERENCES tenants(email) ON UPDATE CASCADE,
    doc_title VARCHAR(200),
    PRIMARY KEY(doc_id)
    );

CREATE VIEW prop_tenant_view AS (
    SELECT pr.prop_id AS "Property ID",
           pr.ll_id AS "Landlord ID",
           pr.flat_num AS "Flat number",
           pr.street AS "Street",
           pr.post_code AS "Post code",
           pr.city AS "City",
           tn.first_name AS "First name",
           tn.last_name AS "Last name",
           tn.email AS "Email"
    FROM properties AS pr
        LEFT JOIN tenants AS tn
            ON pr.prop_id = tn.prop_id
            );

CREATE VIEW doc_tenant_view AS (
    SELECT dc.doc_id AS "Document ID",
           dc.prop_id AS "Property ID",
           tn.first_name AS "First name",
           tn.last_name AS "Last name",
           tn.email AS "Email",
           dc.doc_title AS "Document title"
    FROM documents AS dc
        JOIN tenants AS tn
        ON dc.email = tn.email
        );
