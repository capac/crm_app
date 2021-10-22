-- lookup tables:
--   landlords
--   properties

CREATE TABLE IF NOT EXISTS landlords (
    id VARCHAR(6) UNIQUE NOT NULL,
    PRIMARY KEY(id)
    );

CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR(7) UNIQUE NOT NULL,
    landlord_id VARCHAR(6) NOT NULL REFERENCES landlords(id),
    flat_num VARCHAR(2) NOT NULL,
    street VARCHAR(60) NOT NULL,
    post_code VARCHAR(10) NOT NULL,
    city VARCHAR(20) NOT NULL,
    PRIMARY KEY(id)
    );

CREATE TABLE IF NOT EXISTS tenants (
    id SERIAL UNIQUE NOT NULL,
    prop_id VARCHAR(7) NOT NULL REFERENCES properties(id),
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    email VARCHAR(60),
    PRIMARY KEY(id)
    );

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL UNIQUE NOT NULL,
    prop_id VARCHAR(10) NOT NULL REFERENCES properties(id),
    tenant_id SERIAL NOT NULL REFERENCES tenants(id),
    document VARCHAR(200),
    PRIMARY KEY(id)
    );

CREATE VIEW data_record_view AS (
    SELECT pr.id AS "Property ID",
           pr.flat_num AS "Flat number",
           pr.street AS "Street",
           pr.post_code AS "Post code",
           pr.city AS "City",
           tn.first_name AS "First name",
           tn.last_name AS "Last name",
           tn.email AS "Email"
    FROM tenants AS tn
        JOIN properties AS pr
            ON tn.prop_id = pr.id
    );
