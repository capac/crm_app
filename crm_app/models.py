import csv
import os
from .constants import FieldTypes as FT
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
        'Documents': {'req': True, 'type': FT.long_string},
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
