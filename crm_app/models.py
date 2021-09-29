import csv
import os
import json
from .constants import FieldTypes as FT
import psycopg2 as pg
from psycopg2.extras import DictCursor
from cfi_codes import property_ids


class CSVModel:
    '''CSV file storage'''
    fields = {
        'Property ID': {'req': True, 'type': FT.string_list, 'values': property_ids},
        'Landlord ID': {'req': True, 'type': FT.string},
        'Flat number': {'req': True, 'type': FT.string},
        'Address': {'req': True, 'type': FT.string},
        'Post code': {'req': True, 'type': FT.string},
        'City': {'req': True, 'type': FT.string},
        'First name': {'req': True, 'type': FT.string},
        'Last name': {'req': True, 'type': FT.string},
        'Email': {'req': True, 'type': FT.string},
        # this variable will need to be changed when the
        # list of documents sent by email is implemented
        'Document': {'req': True, 'type': FT.long_string},
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
        'Landlord ID': {'req': True, 'type': FT.string_list, 'values': []},
        'Property ID': {'req': True, 'type': FT.string_list, 'values': []},
        'Flat number': {'req': True, 'type': FT.string},
        'Address': {'req': True, 'type': FT.string},
        'Post code': {'req': True, 'type': FT.string},
        'City': {'req': True, 'type': FT.string},
        'First name': {'req': True, 'type': FT.string},
        'Last name': {'req': True, 'type': FT.string},
        'Email': {'req': True, 'type': FT.string},
        # this value is populated from the documents in the
        #  email attachments using the Microsoft Graph API
        'Document': {'req': True, 'type': FT.long_string},
    }

    # insert tenant in property
    tenants_insert_query = ('INSERT INTO tenants VALUES (%(Property ID)s, %(First name)s, '
                            '%(Last name)s, %(Email)s)')
    # update tenant in property
    tenants_update_query = ('UPDATE tenants SET first_name=%(First name)s, last_name=%(Last name)s, '
                            'email=%(Email)s WHERE prop_id = %(Property ID)s')

    # insert new property
    propriety_insert_query = ('INSERT INTO properties VALUES (%(Property ID)s, %(Landlord ID)s, '
                              '%(Flat number)s, %(Street)s, %(Post code)s, %(City)s)')
    # delete old property
    propriety_delete_query = ('DELETE FROM properties WHERE prop_id = %(Property ID)s')

    def __init__(self, host, database, user, password):
        self.connection = pg.connect(host=host, database=database, user=user,
                                     password=password, cursor_factory=DictCursor)
        landlords = self.query("SELECT id FROM landlords ORDER BY id")
        self.fields['Landlord ID']['values'] = [x['id'] for x in landlords]
        prop_ids = self.query("SELECT id FROM properties ORDER BY id")
        self.fields['Property ID']['values'] = [x['id'] for x in prop_ids]

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
        query = ('SELECT * FROM data_record_view '
                 'ORDER BY "Property ID"')
        return self.query(query)

    def get_record(self, prop_id):
        query = ('SELECT * FROM data_record_view '
                 'WHERE "Property ID" = %(prop_id)s')
        result = self.query(query, {"Property ID": prop_id})
        return result[0] if result else {}

    def save_record(self, record):
        # add or update tenant information
        first_name = record['First Name']
        last_name = record['Last Name']
        email = record['Email']
        prop_id = record['Property ID']

        # if the property exists, update the tenant information
        if self.get_record(prop_id, first_name, last_name, email):
            tenant_query = self.tenants_update_query
            self.last_write = 'update'
        # if the property exists but doesn't have tenant
        # information, associate it to the property data
        else:
            tenant_query = self.tenants_insert_query
            self.last_write = 'insert'

        self.query(tenant_query, record)

    def change_property_record(self, record):
        # add or update property information
        prop_id = record['Property ID']
        flat_number = record['Flat number']
        street = record['Street']
        city = record['City']
        post_code = record['Post code']

        # if record doesn't exists, add new property record
        if not self.get_record(prop_id, flat_number, street, city, post_code):
            property_query = self.propriety_insert_query
        # if record exists, remove old property record
        else:
            property_query = self.propriety_delete_query

        self.query(property_query, record)


class SettingsModel:
    '''A model for saving settings'''

    variables = {
        'db_host': {'type': 'str', 'value': 'localhost'},
        'db_name': {'type': 'str', 'value': 'dbase'},
    }

    def __init__(self, filename='settings.json', path='~'):
        # determine the file path
        self.filepath = os.path.join(os.path.expanduser(path), filename)
        # load in saved values
        self.load()

    def load(self):
        '''Load the settings from the file'''
        # if the file doesn't exist, return
        if not os.exists(self.filepath):
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

    def save(self, settings=None):
        json_string = json.dumps(self.variables)
        with open(self.filepath, 'w') as fh:
            fh.write(json_string)

    def set(self, key, value):
        if (
            key in self.variables and type(value).__name__ == self.variables[key]['type']
        ):
            self.variables[key]['value'] = value
        else:
            raise ValueError('Bad key or wrong variable type')
