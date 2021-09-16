import tkinter as tk
from . import widgets as w
from cfi_codes import property_ids


class MainMenu(tk.Menu):
    '''The Application's main menu'''

    def __init__(self, parent, settings, callbacks, **kwargs):
        super().__init__(parent, **kwargs)

        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            label='Select file...',
            command=callbacks['file->open']
            )
        file_menu.add_separator()
        file_menu.add_command(
            label='Quit',
            command=callbacks['file->quit']
            )
        self.add_cascade(label='File', menu=file_menu)


class DataRecordForm(tk.Frame):
    '''The input form for our widgets'''

    def __init__(self, parent, fields, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # a dictionary to keep track of input widgets
        self.inputs = {}
        # property id codes for CFI
        officeinfo = tk.LabelFrame(self, text='Office information')

        # Office information
        self.inputs['property_id'] = w.LabelInput(officeinfo, 'Property ID',
                                                  field_spec=fields['Property ID'],
                                                  input_args={'values': property_ids()})
        self.inputs['property_id'].grid(row=0, column=0)
        self.inputs['landlord_company'] = w.LabelInput(officeinfo, 'Landlord company',
                                                       field_spec=fields['Landlord ID'])
        self.inputs['landlord_company'].grid(row=0, column=1)
        officeinfo.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # Property information
        propertyinfo = tk.LabelFrame(self, text='Property information')
        self.inputs['flat_num'] = w.LabelInput(propertyinfo, 'Flat number',
                                               field_spec=fields['Flat number'])
        self.inputs['flat_num'].grid(row=0, column=0)
        self.inputs['address'] = w.LabelInput(propertyinfo, 'Address',
                                              field_spec=fields['Address'])
        self.inputs['address'].grid(row=0, column=1)
        self.inputs['post_code'] = w.LabelInput(propertyinfo, 'Post code',
                                                field_spec=fields['Post code'])
        self.inputs['post_code'].grid(row=0, column=2)
        self.inputs['city'] = w.LabelInput(propertyinfo, 'City',
                                           field_spec=fields['City'])
        self.inputs['city'].grid(row=0, column=3)
        propertyinfo.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # Tenant information
        tenantinfo = tk.LabelFrame(self, text='Tenant information')
        self.inputs['first_name'] = w.LabelInput(tenantinfo, 'First name',
                                                 field_spec=fields['First name'])
        self.inputs['first_name'].grid(row=0, column=0)
        self.inputs['last_name'] = w.LabelInput(tenantinfo, 'Last name',
                                                field_spec=fields['Last name'])
        self.inputs['last_name'].grid(row=0, column=1)
        self.inputs['email'] = w.LabelInput(tenantinfo, 'Email',
                                            field_spec=fields['Email'])
        self.inputs['email'].grid(row=0, column=2)
        tenantinfo.grid(row=2, column=0, sticky=(tk.W + tk.E))

        # Document information sent by email
        emaildocumentinfo = tk.LabelFrame(self, text='Document information')
        self.inputs['email_documents'] = w.LabelInput(emaildocumentinfo, 'List of documents sent by email',
                                                      input_class=tk.Text,
                                                      input_args={'width': 110, 'height': 10})
        self.inputs['email_documents'].grid(row=0, column=0)
        emaildocumentinfo.grid(row=3, column=0, sticky=(tk.W + tk.E))

        # set default tk entry values to empty strings
        self.reset()

    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def reset(self):
        for widget in self.inputs.values():
            widget.set('')

    def get_errors(self):
        '''Get a list of field errors in the form'''

        errors = {}
        for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()
        return errors
