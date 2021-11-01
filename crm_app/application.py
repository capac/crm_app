import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from . import views as v
from . import models as m


class Application(tk.Tk):
    '''Application root window'''

    # supported platforms: macOS and Windows
    config_dirs = {
        'Darwin': '~/Library/Application Support',
        'Windows': '~/AppData/Local',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # application title
        self.title('CRM Application')
        self.resizable(width=False, height=False)

        # application name
        ttk.Label(self, text='Data Record List', font=('TkDefaultFont', 16)).grid(row=0, padx=60)

        self.inserted_rows = []
        self.updated_rows = []

        # filename variable
        datestring = datetime.today().strftime('%Y-%m-%d')
        default_filename = f'data_record_{datestring}.csv'
        self.filename = tk.StringVar(value=default_filename)

        # settings model and settings
        config_dir = self.config_dirs.get(platform.system(), '~')
        self.settings_model = m.SettingsModel(path=config_dir)
        self.load_settings()

        # setting style
        style = ttk.Style()
        theme = self.settings.get('theme').get()
        if theme in style.theme_names():
            style.theme_use(theme)

        # database login
        self.database_login()
        if not hasattr(self, 'data_model'):
            self.destroy()
            return

        # create data model
        self.callbacks = {
            # menu bar callbacks
            'file->add_property': self.open_add_property_window,
            'file->delete_property': self.open_delete_property_window,
            'file->import': self.on_file_import,
            'file->export': self.on_file_export,
            'file->quit': self.quit,
            # method callbacks
            'on_save': self.on_save,
            'on_save_property': self.save_property,
            'on_open_record': self.open_record,
        }

        menu = v.MainMenu(self, self.callbacks)
        self.config(menu=menu)

        # treeview record form
        self.recordlist = v.RecordList(self, self.callbacks,
                                       inserted=self.inserted_rows,
                                       updated=self.updated_rows,)
        self.recordlist.grid(row=1, padx=10, sticky='NSEW')
        self.recordlist.columnconfigure(0, weight=1)
        self.populate_recordlist()

        # data record form
        self.recordform = v.DataRecordForm(self, self.data_model.fields,
                                           self.callbacks)
        self.recordform.grid(row=2, padx=10, sticky='NSEW')
        self.recordform.columnconfigure(0, weight=1)

        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(row=3, padx=10, sticky=('WE'))
        self.statusbar.columnconfigure(0, weight=1)

        self.records_saved = 0

    def populate_recordlist(self):
        try:
            rows = self.data_model.get_all_records()
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem reading database',
                detail=str(e)
            )
        else:
            self.recordlist.populate(rows)

    def open_record(self, rowkey=None):
        '''Rowkey simply contains prop_id'''

        if rowkey is None:
            record = None
        else:
            try:
                # print(f'rowkey: {rowkey}')
                record = self.data_model.get_record(rowkey)
                # print(f'record: {record}')
            except Exception as e:
                messagebox.showerror(title='Error', message='Problem reading database',
                                     detail=str(e))
                return
        self.recordform.load_record(rowkey, record)
        self.recordform.tkraise()

    def on_save(self):
        '''Handles saves to the database button clicks'''

        # check for errors first
        errors = self.recordform.get_errors()
        if errors:
            message = 'Cannot save record'
            detail = 'The following fields have errors: \n * {}'.format('\n * '.join(errors.keys()))
            self.status.set(
                f'''Cannot save, error in fields: {', '.join(errors.keys())}'''
            )
            messagebox.showerror(title='Error', message=message, detail=detail)
            return False

        # get data
        data = self.recordform.get()
        try:
            self.data_model.change_tenant(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem saving record',
                detail=str(e)
            )
            self.status.set('Problem saving record')
        else:
            self.records_saved += 1
            self.status.set(f'{self.records_saved} record(s) saved this session')
            key = (data['Property ID'], data['First name'], data['Last name'], data['Email'])
            if self.data_model.last_write == 'update tenant':
                self.updated_rows.append(key)
            else:
                # new property with tenant added
                self.inserted_rows.append(key)
                # print(f'self.inserted_rows: {self.inserted_rows}')
            self.populate_recordlist()
            # reset form only when appending records
            if self.data_model.last_write == 'insert tenant':
                self.recordform.reset()

    def open_add_property_window(self):
        '''Opens window for addition of new property into database'''

        # opens window for new property entry
        window = tk.Toplevel(self)
        window.resizable(width=False, height=False)
        window.title('Add property')

        # property form
        self.propertyform = v.ChangePropertyForm(window, self.data_model.fields, self.callbacks)
        self.propertyform.grid(row=0, padx=5, sticky='W')
        self.propertyform.columnconfigure(0, weight=1)

        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(window, textvariable=self.status)
        self.statusbar.grid(row=1, padx=10, sticky=('WE'))
        self.statusbar.columnconfigure(0, weight=1)

    def save_property(self):
        '''Save new property to the database'''

        # check for errors first
        errors = self.propertyform.get_errors()
        if errors:
            message = 'Cannot save record'
            detail = 'The following fields have errors: \n * {}'.format('\n * '.join(errors.keys()))
            self.status.set(
                f'''Cannot save, error in fields: {', '.join(errors.keys())}'''
            )
            messagebox.showerror(title='Error', message=message, detail=detail)
            return False

        # get data
        data = self.propertyform.get()
        print(data)
        try:
            self.data_model.add_property(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem saving record',
                detail=str(e)
            )
            self.status.set('Problem saving record')
        else:
            self.records_saved += 1
            self.status.set(f'{self.records_saved} record(s) saved this session')
            key = (data['Property ID'], data['Landlord ID'], data['Flat number'],
                   data['Street'], data['Post code'], data['City'])
            if self.data_model.last_write == 'insert property':
                self.inserted_rows.append(key)
            self.populate_recordlist()
            # reset form only when appending records
            self.propertyform.reset()

    def open_delete_property_window():
        '''Opens window for removal of property from database'''

        pass

    def delete_property(self):
        '''Removes property from database'''

        pass

    # import records from CSV file to database
    def on_file_import(self):
        '''Handles the file->import action from the menu'''

        filename = filedialog.askopenfile(
            title='Select the file to import into the database',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
        )
        if filename:
            self.filename.set(filename)

    # save records to CSV file
    def on_file_export(self):
        '''Handles the file->export action from the menu'''

        filename = filedialog.asksaveasfile(
            title='Create the target file for saving records',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
        )
        if filename:
            self.filename.set(filename)

    def load_settings(self):
        '''Load settings into our self.settings dict'''

        vartypes = {
            'bool': tk.BooleanVar,
            'str': tk.StringVar,
            'int': tk.IntVar,
            'float': tk.DoubleVar
        }

        # create our dict of settings variables from the model's settings
        self.settings = {}
        for key, data in self.settings_model.variables.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])

        # put a trace on the variables so they get stored when changed
        for var in self.settings.values():
            var.trace('w', self.save_settings)

    def save_settings(self, *args):
        '''Save the current settings to a preferences file'''

        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())
        self.settings_model.save()

    def database_login(self):
        '''Try to login to the database and create self.data_model'''

        db_host = self.settings['db_host'].get()
        db_name = self.settings['db_name'].get()
        title = f'Login to {db_name} at {db_host}'
        error = ''
        while True:
            login = v.LoginDialog(self, title, error)
            if not login.result:
                break
            else:
                username, password = login.result
                try:
                    self.data_model = m.SQLModel(db_host, db_name, username, password)
                except m.pg.OperationalError:
                    error = 'Login failed'
                else:
                    break
