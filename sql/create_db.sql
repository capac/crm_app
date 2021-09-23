-- lookup tables:
--   * landlords
--   * properties

CREATE TABLE landlords (
    id VARCHAR(10) UNIQUE NOT NULL,
    PRIMARY KEY(id)
    );
CREATE TABLE properties (
    id VARCHAR(10) UNIQUE NOT NULL,
    landlord_id VARCHAR(10) NOT NULL REFERENCES landlords(id),
    flat_num VARCHAR(4) NOT NULL,
    street VARCHAR(100) NOT NULL,
    post_code VARCHAR(16) NOT NULL,
    city VARCHAR(30) NOT NULL,
    PRIMARY KEY(id)
    );
CREATE TABLE tenants (
    id SERIAL UNIQUE NOT NULL,
    prop_id VARCHAR(10) NOT NULL REFERENCES properties(id),
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    email VARCHAR(60),
    PRIMARY KEY(id, prop_id)
    );
CREATE TABLE documents (
    id SERIAL UNIQUE NOT NULL,
    document VARCHAR(200),
    prop_id VARCHAR(10) NOT NULL REFERENCES properties(id),
    tenant_id SERIAL NOT NULL REFERENCES tenants(id),
    PRIMARY KEY(id)
    );
