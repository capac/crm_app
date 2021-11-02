import csv
import os
import json
from .constants import FieldTypes as FT
import psycopg2 as pg
from psycopg2.extras import DictCursor
from cfi_codes import property_ids, landlord_company_ids


class CSVModel:
    '''CSV file storage'''

    fields = {
        'Property ID': {'req': True, 'type': FT.string_list, 'values': property_ids},
        'Landlord ID': {'req': True, 'type': FT.string_list, 'values': landlord_company_ids},
        'Flat number': {'req': True, 'type': FT.string},
        'Address': {'req': True, 'type': FT.string},
        'Post code': {'req': True, 'type': FT.string},
        'City': {'req': True, 'type': FT.string},
        'First name': {'req': True, 'type': FT.string},
        'Last name': {'req': True, 'type': FT.string},
        'Email': {'req': True, 'type': FT.string},
        # this variable will need to be changed when the
        # list of documents sent by email is implemented
        # 'Document': {'req': True, 'type': FT.long_string},
    }

    def __init__(self, filename):
        self.filename = filename

    def save_record(self, data):
        '''Save a dict of data to a CSV file'''

        newfile = not os.path.exists(self.filename)

        with open(self.filename, 'a') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=self.fields.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(data)


class SQLModel:
    '''SQL database values'''

    fields = {
        # these values are populated by the lookup tables:
        # landlords, properties and tenants
        'Property ID': {'req': True, 'type': FT.string},
        'Property ID Dropdown': {'req': True, 'type': FT.string_list, 'values': []},
        'Landlord ID': {'req': True, 'type': FT.string},
        'Flat number': {'req': True, 'type': FT.string},
        'Street': {'req': True, 'type': FT.string},
        'Post code': {'req': True, 'type': FT.string},
        'City': {'req': True, 'type': FT.string},
        'First name': {'req': True, 'type': FT.string},
        'Last name': {'req': True, 'type': FT.string},
        'Email': {'req': True, 'type': FT.string},
        # this value is populated from the documents in the
        #  email attachments using the Microsoft Graph API
        # 'Document': {'req': True, 'type': FT.long_string},
    }

    # insert tenant in existing property
    tenants_insert_query = ('INSERT INTO tenants VALUES (%(Property ID)s, '
                            '%(First name)s, %(Last name)s, %(Email)s) ')

    # update tenant in existing property
    tenants_update_query = ('UPDATE tenants SET first_name=%(First name)s, '
                            'last_name=%(Last name)s, email=%(Email)s WHERE '
                            'prop_id = %(Property ID)s')

    # insert new property, used rarely
    propriety_insert_query = ('INSERT INTO properties VALUES (%(Property ID)s, '
                              '%(Landlord ID)s, %(Flat number)s, %(Street)s, '
                              '%(Post code)s, %(City)s)')

    # delete old property, used rarely
    propriety_delete_query = ('DELETE FROM properties WHERE prop_id = %(Property ID)s')

    def __init__(self, host, database, user, password):
        self.connection = pg.connect(host=host, database=database, user=user,
                                     password=password, cursor_factory=DictCursor)
        # landlords = self.query("SELECT id FROM landlords ORDER BY id")
        # self.fields['Landlord ID']['values'] = [x['id'] for x in landlords]
        prop_ids = self.query("SELECT prop_id FROM properties ORDER BY prop_id")
        self.fields['Property ID Dropdown']['values'] = [x['prop_id'] for x in prop_ids]

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

    def get_all_records(self):
        query = ('SELECT * FROM prop_tenant_view '
                 'ORDER BY "Property ID"')
        return self.query(query)

    def get_record(self, prop_id):
        query = ('SELECT * FROM prop_tenant_view '
                 'WHERE "Property ID" = %(prop_id)s')
        result = self.query(query, {"prop_id": prop_id})
        return result[0] if result else {}

    def change_tenant(self, record):
        # add or update tenant information
        prop_id = record['Property ID']
        query = ('SELECT "First name", "Last name" FROM prop_tenant_view '
                 'WHERE "Property ID" = %(prop_id)s')
        results = self.query(query, {"prop_id": prop_id})
        first_name, last_name = results[0][0], results[0][1]
        # if the property exists but doesn't have any tenant
        # information, add tenant data to the property
        if (first_name is None and last_name is None):
            tenant_query = self.tenants_insert_query
            self.last_write = 'insert tenant'
        # if the property already contains a tenant, update
        # the property with the new tenant information
        else:
            tenant_query = self.tenants_update_query
            self.last_write = 'update tenant'

        self.query(tenant_query, record)

    def add_property(self, record):
        # add property information
        property_query = self.propriety_insert_query
        self.last_write = 'insert property'
        self.query(property_query, record)

    def delete_property(self, record):
        # delete property information
        property_query = self.propriety_delete_query
        self.query(property_query, record)


class SettingsModel:
    '''A model for saving settings'''

    variables = {
        # ('aqua', 'clam', 'alt', 'default', 'classic')
        'theme': {'type': 'str', 'value': 'aqua'},
        'db_host': {'type': 'str', 'value': 'localhost'},
        'db_name': {'type': 'str', 'value': 'housing_management'},
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
