-- lookup tables:
--   landlords
--   properties

CREATE TABLE IF NOT EXISTS landlords (
    ll_id VARCHAR(6) UNIQUE NOT NULL,
    PRIMARY KEY(ll_id)
    );

CREATE TABLE IF NOT EXISTS properties (
    prop_id VARCHAR(7) UNIQUE NOT NULL,
    ll_id VARCHAR(6) NOT NULL REFERENCES landlords(ll_id) ON DELETE CASCADE ON UPDATE CASCADE,
    flat_num VARCHAR(3) NOT NULL,
    street VARCHAR(60) NOT NULL,
    post_code VARCHAR(10) NOT NULL,
    city VARCHAR(20) NOT NULL,
    PRIMARY KEY(prop_id)
    );

CREATE TABLE IF NOT EXISTS tenants (
    prop_id VARCHAR(7) NOT NULL REFERENCES properties(prop_id) ON DELETE CASCADE ON UPDATE CASCADE,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    email VARCHAR(60),
    PRIMARY KEY(email)
    );

CREATE TABLE IF NOT EXISTS documents (
    doc_id SERIAL UNIQUE NOT NULL,
    subject VARCHAR(200),
    recipient VARCHAR(60) NOT NULL REFERENCES tenants(email) ON DELETE CASCADE ON UPDATE CASCADE,
    date_sent TIMESTAMP,
    attachments VARCHAR(200),
    PRIMARY KEY(date_sent)
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
           tn.prop_id AS "Property ID",
           tn.first_name AS "First name",
           tn.last_name AS "Last name",
           dc.subject AS "Subject",
           dc.recipient AS "Recipient",
           dc.date_sent AS "Date sent",
           dc.attachments AS "Attachments"
    FROM documents AS dc
        JOIN tenants AS tn
        ON dc.recipient = tn.email
        );
