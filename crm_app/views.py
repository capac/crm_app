import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.simpledialog import Dialog
from . import widgets as w
from cfi_codes import property_ids, landlord_company_ids


class MainMenu(tk.Menu):
    '''The Application's main menu'''

    def __init__(self, parent, settings, callbacks, *args, **kwargs):
        '''Constructor for MainMenu

        arguments:
            parent - the parent widget
            callbacks - a dict containing Python callbacks
            settings - dict to save user settings
        '''
        super().__init__(parent, *args, **kwargs)
        self.settings = settings

        # the file menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Import file'+chr(8230),
            command=callbacks['file->import']
            )
        file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Export file'+chr(8230),
            command=callbacks['file->export']
            )
        file_menu.add_separator()
        file_menu.add_command(
            label='Quit',
            command=callbacks['file->quit']
            )
        self.add_cascade(label='File', menu=file_menu)

        # the help menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='About'+chr(8230), command=self.show_about)
        self.add_cascade(label='Help', menu=help_menu)

    def show_about(self):
        '''Show the about dialog'''
        about_message = 'Data Query Application'
        about_details = ('Customer relationship management \
                         application for the query of tenant \
                         information by property identification.\n\n\
                         For assistance please contact the author.')
        messagebox.showinfo(title='About', message=about_message, detail=about_details)


class DataRecordForm(tk.Frame):
    '''The input form for our widgets'''

    def __init__(self, parent, fields, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.settings = settings
        self.callbacks = callbacks

        # a dictionary to keep track of input widgets
        self.inputs = {}
        # property id codes for CFI
        officeinfo = tk.LabelFrame(self, text='Office information')

        # Office information
        self.inputs['Property ID'] = w.LabelInput(officeinfo, 'Property ID',
                                                  field_spec=fields['Property ID'],
                                                  input_args={'values': property_ids()})
        self.inputs['Property ID'].grid(row=0, column=0)
        self.inputs['Landlord ID'] = w.LabelInput(officeinfo, 'Landlord ID',
                                                  field_spec=fields['Landlord ID'],
                                                  input_args={'values': landlord_company_ids()})
        self.inputs['Landlord ID'].grid(row=0, column=1)
        officeinfo.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # Property information
        propertyinfo = tk.LabelFrame(self, text='Property information')
        self.inputs['Flat number'] = w.LabelInput(propertyinfo, 'Flat number',
                                                  field_spec=fields['Flat number'])
        self.inputs['Flat number'].grid(row=0, column=0)
        self.inputs['Street'] = w.LabelInput(propertyinfo, 'Street',
                                             field_spec=fields['Street'])
        self.inputs['Street'].grid(row=0, column=1)
        self.inputs['Post code'] = w.LabelInput(propertyinfo, 'Post code',
                                                field_spec=fields['Post code'])
        self.inputs['Post code'].grid(row=0, column=2)
        self.inputs['City'] = w.LabelInput(propertyinfo, 'City',
                                           field_spec=fields['City'])
        self.inputs['City'].grid(row=0, column=3)
        propertyinfo.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # Tenant information
        tenantinfo = tk.LabelFrame(self, text='Tenant information')
        self.inputs['First name'] = w.LabelInput(tenantinfo, 'First name',
                                                 field_spec=fields['First name'])
        self.inputs['First name'].grid(row=0, column=0)
        self.inputs['Last name'] = w.LabelInput(tenantinfo, 'Last name',
                                                field_spec=fields['Last name'])
        self.inputs['Last name'].grid(row=0, column=1)
        self.inputs['Email'] = w.LabelInput(tenantinfo, 'Email',
                                            field_spec=fields['Email'])
        self.inputs['Email'].grid(row=0, column=2)
        tenantinfo.grid(row=2, column=0, sticky=(tk.W + tk.E))

        # Document information sent by email
        emaildocumentinfo = tk.LabelFrame(self, text='Document information')
        self.inputs['Documents'] = w.LabelInput(emaildocumentinfo, 'List of documents sent by email',
                                                input_class=tk.Text,
                                                input_args={'width': 110, 'height': 10})
        self.inputs['Documents'].grid(row=0, column=0)
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


class LoginDialog(Dialog):
    def __init__(self, parent, title, error=''):
        self.pw = tk.StringVar()
        self.user = tk.StringVar()
        self.error = tk.StringVar(value=error)
        super().__init__(parent, title=title)

    def body(self, parent):
        lf = tk.Frame(self)
        ttk.Label(lf, text='Login to database', font='Sans 20').grid()
        if self.error.get():
            tk.Label(lf, textvariable=self.error, bg='darkred', fg='white').grid()
        ttk.Label(lf, text='User name:').grid()
        self.username_inp = ttk.Entry(lf, textvariable=self.user)
        self.username_inp.grid()
        ttk.Label(lf, text='Password:').grid()
        self.password_inp = ttk.Entry(lf, show='*', textvariable=self.pw)
        self.password_inp.grid()
        lf.pack()
        return self.username_inp

    def apply(self):
        self.result = (self.user.get(), self.pw.get())
