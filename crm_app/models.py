import csv
import os
import json
import subprocess
from .constants import FieldTypes as FT
import psycopg2 as pg
from psycopg2.extras import DictCursor


class SQLModel:
    '''SQL database values'''

    fields = {
        # value for 'DeletePropertyForm' class
        'Property ID Dropdown': {'req': True, 'type': FT.string_list, 'values': []},
        # these values are populated by the lookup tables:
        # landlords
        'Property ID': {'req': True, 'type': FT.string},
        'Landlord ID': {'req': True, 'type': FT.string},
        'Number properties in building': {'req': True, 'type': FT.string},
        'Number properties in building Spinbox': {'req': True, 'type': FT.integer},
        # properties
        'Flat number': {'req': True, 'type': FT.string},
        'Street': {'req': True, 'type': FT.string},
        'Post code': {'req': True, 'type': FT.string},
        'City': {'req': True, 'type': FT.string},
        # tenants
        'First name': {'req': True, 'type': FT.string},
        'Last name': {'req': True, 'type': FT.string},
        'Email': {'req': True, 'type': FT.string},
    }

    # create user and database if not existing
    subprocess.run('createuser -s crm', shell=True, stderr=subprocess.DEVNULL)
    subprocess.run('createdb -O crm housing_management', shell=True, stderr=subprocess.DEVNULL)

    # create tables if not existing
    create_ll_table_command = ('CREATE TABLE IF NOT EXISTS landlords '
                               '(ll_id VARCHAR(6) UNIQUE NOT NULL, '
                               'PRIMARY KEY(ll_id))')

    create_pr_table_command = ('CREATE TABLE IF NOT EXISTS properties '
                               '(prop_id VARCHAR(7) UNIQUE NOT NULL, '
                               'll_id VARCHAR(6) NOT NULL REFERENCES '
                               'landlords(ll_id) ON DELETE CASCADE ON UPDATE CASCADE, '
                               'num_prop_building INT NOT NULL, '
                               'flat_num VARCHAR(3) NOT NULL, '
                               'street VARCHAR(60) NOT NULL, '
                               'post_code VARCHAR(10) NOT NULL, '
                               'city VARCHAR(20) NOT NULL, '
                               'PRIMARY KEY(prop_id))')

    create_tn_table_command = ('CREATE TABLE IF NOT EXISTS tenants '
                               '(prop_id VARCHAR(7) NOT NULL REFERENCES '
                               'properties(prop_id) ON DELETE CASCADE ON UPDATE CASCADE, '
                               'first_name VARCHAR(20), '
                               'last_name VARCHAR(20), '
                               'email VARCHAR(60), '
                               'PRIMARY KEY(email))')

    create_dc_table_command = ('CREATE TABLE IF NOT EXISTS documents '
                               '(subject VARCHAR(200), '
                               'recipient VARCHAR(60) NOT NULL REFERENCES '
                               'tenants(email) ON DELETE CASCADE ON UPDATE CASCADE, '
                               'date_sent TIMESTAMP, '
                               'date_retrieved TIMESTAMP, '
                               'attachments VARCHAR(200), '
                               'PRIMARY KEY(date_sent))')

    create_prop_tenant_view_command = ('CREATE OR REPLACE VIEW prop_tenant_view AS '
                                       '(SELECT pr.prop_id AS "Property ID", '
                                       'pr.ll_id AS "Landlord ID", '
                                       'pr.num_prop_building AS "Number properties in building", '
                                       'pr.flat_num AS "Flat number", '
                                       'pr.street AS "Street", '
                                       'pr.post_code AS "Post code", '
                                       'pr.city AS "City", '
                                       'tn.first_name AS "First name", '
                                       'tn.last_name AS "Last name", '
                                       'tn.email AS "Email" '
                                       'FROM properties AS pr '
                                       'LEFT JOIN tenants AS tn '
                                       'ON pr.prop_id = tn.prop_id)')

    create_doc_tenant_view_command = ('CREATE OR REPLACE VIEW doc_tenant_view AS '
                                      '(SELECT tn.prop_id AS "Property ID", '
                                      'tn.first_name AS "First name", '
                                      'tn.last_name AS "Last name", '
                                      'dc.recipient AS "Recipient", '
                                      'dc.subject AS "Subject", '
                                      'dc.date_sent AS "Date sent", '
                                      'dc.date_retrieved AS "Date retrieved", '
                                      'dc.attachments AS "Attachments" '
                                      'FROM documents AS dc '
                                      'JOIN tenants AS tn '
                                      'ON dc.recipient = tn.email)')

    # insert tenant in existing property
    tenants_insert_query = ('INSERT INTO tenants VALUES (%(Property ID)s, '
                            '%(First name)s, %(Last name)s, %(Email)s) ')

    # update tenant in existing property
    tenants_update_query = ('UPDATE tenants SET first_name=%(First name)s, '
                            'last_name=%(Last name)s, email=%(Email)s WHERE '
                            'prop_id = %(Property ID)s')

    # insert new property, used rarely
    propriety_insert_query = ('INSERT INTO properties VALUES (%(Property ID)s, '
                              '%(Landlord ID)s, %(Number properties in building)s, '
                              '%(Flat number)s, %(Street)s, %(Post code)s, %(City)s)')

    # insert new landlord, used only on initial CRM app setup
    landlords_insert_query = ('INSERT INTO landlords (ll_id) VALUES (%(Landlord ID)s)')

    # retrieve and insert new emails in documents table
    documents_insert_query = ('INSERT INTO documents (subject, recipient, date_sent, '
                              'date_retrieved, attachments) VALUES (%(Subject)s, '
                              '%(Recipient)s, %(Date sent)s, CURRENT_TIMESTAMP(0), '
                              '%(Attachments)s) ON CONFLICT (date_sent) DO UPDATE '
                              'SET date_retrieved = CURRENT_TIMESTAMP(0)')

    remove_old_emails_query = ('DELETE FROM documents WHERE date_retrieved < (SELECT '
                               'MIN(date_retrieved) FROM documents WHERE recipient = '
                               '%(Recipient)s) AND recipient = %(Recipient)s')

    # delete old property, used rarely
    propriety_delete_query = ('DELETE FROM properties WHERE prop_id = %(Property ID)s')

    def __init__(self, host, database, user, password):
        self.connection = pg.connect(host=host, database=database, user=user,
                                     password=password, cursor_factory=DictCursor)

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, parameters)
        except (pg.Error) as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()
            if cursor.description is not None:
                return cursor.fetchall()

    # only upon first run of the crm application
    def create_db_and_tables(self):
        '''Creates database and tables if they don't already exist'''

        self.query(self.create_ll_table_command)
        self.query(self.create_pr_table_command)
        self.query(self.create_tn_table_command)
        self.query(self.create_dc_table_command)
        self.query(self.create_prop_tenant_view_command)
        self.query(self.create_doc_tenant_view_command)

        # parses property values once database, tables and views exist
        prop_ids = self.query("SELECT prop_id FROM properties ORDER BY prop_id")
        self.fields['Property ID Dropdown']['values'] = [x['prop_id'] for x in prop_ids]

    def get_all_records(self):
        query = ('SELECT * FROM prop_tenant_view '
                 'ORDER BY "Property ID"')
        return self.query(query)

    def get_record(self, prop_id):
        query = ('SELECT * FROM prop_tenant_view '
                 'WHERE "Property ID" = %(prop_id)s')
        result = self.query(query, {"prop_id": prop_id})
        return result[0] if result else {}

    def add_tenant(self, record):
        # add or update tenant information
        prop_id = record['Property ID']
        results = self.get_record(prop_id)
        first_name, last_name = results[7], results[8]
        # if the property exists but doesn't have any tenant
        # information, add tenant data to the property
        if (first_name is None and last_name is None):
            tenant_query = self.tenants_insert_query
            self.last_write = 'insert tenant'
        # if the property already contains a tenant, update
        # the property with the new tenant information
        elif (isinstance(first_name, str) and isinstance(last_name, str)):
            tenant_query = self.tenants_update_query
            self.last_write = 'update tenant'

        self.query(tenant_query, record)

    def add_property(self, record):
        # add property information
        property_query = self.propriety_insert_query
        self.last_write = 'insert property'
        self.query(property_query, record)

    def add_landlords(self, record):
        # add property information
        landlords_query = self.landlords_insert_query
        try:
            self.query(landlords_query, record)
        # landlord(s) are already present in the database
        except pg.IntegrityError:
            pass

    def delete_property(self, record):
        # delete property information
        property_query = self.propriety_delete_query
        self.query(property_query, record)

    def insert_retrieved_documents(self, email):
        # insert retrieved email(s) in documents table
        self.query(self.documents_insert_query, email)
        # remove email(s) from  documents table that are
        # no longer present on server
        self.query(self.remove_old_emails_query, email)

    def get_documents_by_email(self, email, attachments):
        # retrieves list of documents by email
        if attachments:
            query = ('SELECT * FROM doc_tenant_view WHERE "Recipient" = %(email)s '
                     'AND "Attachments" IS NOT NULL ORDER BY "Date sent"')
            results = self.query(query, {"email": email, 'attachments': attachments})
        else:
            query = ('SELECT * FROM doc_tenant_view WHERE "Recipient" = %(email)s '
                     'ORDER BY "Date sent"')
            results = self.query(query, {"email": email})
        return results if results else {}

    def get_properties_by_landlord(self):
        query = ('SELECT "Landlord ID" AS "Landlord", COUNT("Property ID") '
                 'AS "Number of properties" FROM prop_tenant_view '
                 'GROUP BY "Landlord ID"')
        return self.query(query)

    def get_occupancy_by_building(self):
        query = ('SELECT "Street", COUNT("Street") AS "Number of occupied properties", '
                 'MIN("Number properties in building") AS "Total properties", '
                 '100*ROUND(CAST(COUNT("Street") AS DECIMAL)/MIN("Number properties '
                 'in building"), 2) AS "Occupancy (%)" FROM prop_tenant_view GROUP BY "Street"')
        return self.query(query)


class CSVModel:
    '''CSV file retrieval and storage'''

    fields = {
        'Property ID': {'req': True, 'type': FT.string},
        'Landlord ID': {'req': True, 'type': FT.string},
        'Number properties in building': {'req': True, 'type': FT.integer},
        'Flat number': {'req': True, 'type': FT.string},
        'Street': {'req': True, 'type': FT.string},
        'Post code': {'req': True, 'type': FT.string},
        'City': {'req': True, 'type': FT.string},
        'First name': {'req': True, 'type': FT.string},
        'Last name': {'req': True, 'type': FT.string},
        'Email': {'req': True, 'type': FT.string},
    }

    document_fields = {
        'Subject': {'req': True, 'type': FT.string},
        'Recipient': {'req': True, 'type': FT.string},
        'Date sent': {'req': True, 'type': FT.iso_date_string},
        'Attachment': {'req': True, 'type': FT.string},
    }

    def __init__(self, filename, filepath=None):

        if filepath:
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            self.filename = os.path.join(filepath, filename)
        else:
            self.filename = filename

    def get_all_records(self):
        '''Read in all records from the CSV and return a list'''

        if not os.path.exists(self.filename):
            return []

        with open(self.filename, 'r', encoding='utf-8') as fh:
            # turning fh into a list is necessary for our unit tests
            csvreader = csv.DictReader(list(fh.readlines()))
            missing_fields = set(self.fields.keys()) - set(csvreader.fieldnames)
            if len(missing_fields) > 0:
                raise Exception(
                    f'''File is missing fields: {', '.join(missing_fields)}'''
                )
            else:
                return list(csvreader)

    def save_record(self, rows, keys):
        '''Save a dict of data to a CSV file'''

        with open(self.filename, 'w') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=keys)
            csvwriter.writeheader()
            for row in rows:
                csvwriter.writerow(row)


class SettingsModel:
    '''A model for saving settings'''

    variables = {
        # ('aqua', 'clam', 'alt', 'default', 'classic')
        'theme': {'type': 'str', 'value': 'aqua'},
        'db_host': {'type': 'str', 'value': 'localhost'},
        'db_name': {'type': 'str', 'value': 'housing_management'},
        'client_id': {'type': 'str', 'value': None},
        'client_secret': {'type': 'str', 'value': None},
        'account_email': {'type': 'str', 'value': None},
    }

    def __init__(self, filename='settings.json', path='~'):
        # determine the file path
        self.filepath = os.path.join(os.path.expanduser(path), filename)

        # load in saved values
        self.load()

    def set(self, key, value):
        '''Set a variable value'''

        if (
            key in self.variables and type(value).__name__ == self.variables[key]['type']
        ):
            self.variables[key]['value'] = value
        else:
            raise ValueError('Bad key or wrong variable type')

    def save(self, settings=None):
        '''Save the current settings to the file'''

        json_string = json.dumps(self.variables)
        with open(self.filepath, 'w') as fh:
            fh.write(json_string)

    def load(self):
        '''Load the settings from the file'''

        # if the file doesn't exist, return
        if not os.path.exists(self.filepath):
            return
        # open the file and read the raw values
        with open(self.filepath, 'r') as fh:
            raw_values = json.loads(fh.read())
        # don't implicitly trust the raw values,
        # but only get known keys
        for key in self.variables:
            if key in raw_values and 'value' in raw_values[key]:
                raw_value = raw_values[key]['value']
                self.variables[key]['value'] = raw_value
