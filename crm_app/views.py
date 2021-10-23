import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.simpledialog import Dialog
from . import widgets as w
from cfi_codes import property_ids, landlord_company_ids


class MainMenu(tk.Menu):
    '''The Application's main menu'''

    def __init__(self, parent, callbacks, *args, **kwargs):
        '''Constructor for MainMenu

        arguments:
            parent - the parent widget
            callbacks - a dict containing Python callbacks
            settings - dict to save user settings
        '''
        super().__init__(parent, *args, **kwargs)

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

    def __init__(self, parent, fields, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
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

        # operations section
        self.savebutton = ttk.Button(self, text='Save',
                                     command=self.callbacks['on_save'])
        self.savebutton.grid(row=3, column=0, padx=10, pady=(10, 0), sticky=(tk.W))

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


class RecordList(tk.Frame):
    '''Display records in the database'''

    column_defs = {
        '#0': {'label': 'Row', 'anchor': tk.W},
        'Property ID': {'label': 'Property ID', 'anchor': tk.CENTER, 'width': 80},
        'Flat number': {'label': 'Flat number', 'width': 80},
        'Street': {'label': 'Street', 'width': 180},
        'Post code': {'label': 'Post code', 'anchor': tk.CENTER, 'width': 80},
        'City': {'label': 'City', 'width': 80},
        'First name': {'label': 'First name', 'width': 100},
        'Last name': {'label': 'Last name', 'width': 100},
        'Email': {'label': 'Email', 'width': 220},
    }
    default_width = 100
    default_minwidth = 20
    default_anchor = tk.W

    def __init__(self, parent, callbacks,
                 inserted, updated,
                 *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks
        self.inserted = inserted
        self.updated = updated
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # create treeview
        self.treeview = ttk.Treeview(self, columns=list(self.column_defs.keys())[1:],
                                     selectmode='browse')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.treeview.grid(row=0, column=0, sticky='NSEW')

        # hide first column
        self.treeview.config(show='headings')

        # configure scrollbar for the treeview
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                       command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)
        self.treeview.grid(row=0, column=0, sticky='NSEW')
        self.scrollbar.grid(row=0, column=1, sticky='NSEW')

        # configure treeview columns
        for name, definition in self.column_defs.items():
            label = definition.get('label', '')
            anchor = definition.get('anchor', self.default_anchor)
            minwidth = definition.get('minwidth', self.default_minwidth)
            width = definition.get('width', self.default_width)
            stretch = definition.get('stretch', False)
            self.treeview.heading(name, text=label, anchor=anchor)
            self.treeview.column(name, anchor=anchor, minwidth=minwidth,
                                 width=width, stretch=stretch)

        # configure row tags
        self.treeview.tag_configure('inserted', background='lightgreen')
        self.treeview.tag_configure('updated', background='lightblue')

        # bind double-clicks
        self.treeview.bind('<<TreeviewOpen>>', self.on_open_record)

    def populate(self, rows):
        '''Clear the treeview and write the supplied data rows to it'''

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for rowdata in rows:
            rowkey = (str(rowdata['Property ID']), str(rowdata['Flat number']),
                      str(rowdata['Street']), str(rowdata['Post code']),
                      str(rowdata['City']), str(rowdata['First name']),
                      str(rowdata['Last name']), str(rowdata['Email']))
            values = [rowdata[key] for key in valuekeys]
            if self.inserted and rowkey in self.inserted:
                tag = 'inserted'
            elif self.updated and rowkey in self.updated:
                tag = 'updated'
            else:
                tag = ''
            stringkey = '{}|{}|{}|{}|{}|{}|{}|{}'.format(*rowkey)
            self.treeview.insert('', 'end', iid=stringkey, text=stringkey,
                                 values=values, tag=tag)

            if len(rows) > 0:
                firstrow = self.treeview.identify_row(0)
                self.treeview.focus_set()
                self.treeview.selection_set(firstrow)
                self.treeview.focus(firstrow)

    def on_open_record(self, *args):

        selected_id = self.treeview.selection()[0]
        self.callbacks['on_open_record'](selected_id.split('|'))


class LoginDialog(Dialog):
    def __init__(self, parent, title, error=''):
        self.pw = tk.StringVar()
        self.user = tk.StringVar()
        self.error = tk.StringVar(value=error)
        super().__init__(parent, title=title)

    def body(self, parent):
        lf = tk.Frame(self)
        self.geometry('280x180')
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
