import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from . import views as v
from . import models as m
from . import network as n


class Application(tk.Tk):
    '''Application root window'''

    # supported platforms: macOS and Windows
    config_dirs = {
        'Darwin': "~/Library/Application Support/CRMApp",
        'Windows': "~/AppData/Local/CRMApp",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # application title
        self.title('CRM Application')
        self.resizable(width=False, height=False)

        # application name
        ttk.Label(self, text='Tenant Record List', font=('TkDefaultFont', 16)).grid(row=0, padx=60)

        self.inserted_rows = []
        self.updated_rows = []

        # default name for filename
        datestring = datetime.today().strftime("%Y-%m-%d")
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
            # method callbacks
            'on_update': self.on_update,
            'on_add_property': self.add_property,
            'on_delete_property': self.delete_property,
            'on_open_record': self.open_record,
            'on_show_documents': self.show_documents,
            'on_retrieve_emails': self.retrieve_remote_emails,
            'on_print_list': self.print_list,
            'on_show_number_of_properties_by_landlord': self.show_number_of_properties_by_landlord,
            'on_show_occupancy_in_properties': self.show_occupancy_in_properties,
        }

        menu = v.MainMenu(self, self.callbacks)
        self.config(menu=menu)

        # create database and tables if non-existent
        self.data_model.create_db_and_tables()

        # treeview record form
        self.recordlist = v.RecordList(self, self.callbacks,
                                       inserted=self.inserted_rows,
                                       updated=self.updated_rows,)
        self.recordlist.grid(row=1, padx=10, sticky='NSEW')
        self.recordlist.columnconfigure(0, weight=1)
        self.populate_recordlist()

        # attachment option for data form and document list
        self.attachment_option = tk.BooleanVar()

        # data record form
        self.recordform = v.DataRecordForm(self, self.data_model.fields,
                                           self.callbacks, self.attachment_option)
        self.recordform.grid(row=2, padx=10, sticky='NSEW')
        self.recordform.columnconfigure(0, weight=1)

        # refresh screen to update recordlist / recordform, solution found below:
        # https://stackoverflow.com/questions/44768319/tkinter-label-not-appearing
        self.update()

        # status bar
        self.main_status = tk.StringVar()
        self.main_statusbar = ttk.Label(self, textvariable=self.main_status)
        self.main_statusbar.grid(row=3, padx=10, sticky=('WE'))
        self.main_statusbar.columnconfigure(0, weight=1)

        self.records_saved = 0
        self.records_updated = 0
        self.records_deleted = 0

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
        '''rowkey is simply prop_id, while data contains the information for the prop_id'''

        if rowkey is None:
            data = None
        else:
            try:
                data = self.data_model.get_record(rowkey)
                self.recordform.load_record(rowkey, data)
                self.recordform.tkraise(aboveThis=self.recordlist)
            except Exception as e:
                messagebox.showerror(title='Error', message='Problem reading database',
                                     detail=str(e))
                return

    def on_update(self):
        '''Handles tenant updates to database'''

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
            self.data_model.add_tenant(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem saving record',
                detail=str(e)
            )
            self.main_status.set('Problem saving record')
        else:
            self.records_updated += 1
            self.main_status.set(f'{self.records_updated} record(s) updated this session')
            key = (data['Property ID'], data['First name'], data['Last name'], data['Email'])
            # old property with updated tenant
            if self.data_model.last_write == 'update tenant':
                self.updated_rows.append(key)
            # new property with added tenant
            elif self.data_model.last_write == 'insert tenant':
                self.inserted_rows.append(key)
            self.populate_recordlist()

    def open_add_property_window(self):
        '''Opens window for addition of new property into database'''

        # opens window for new property entry
        self.property_window = tk.Toplevel(self)
        self.property_window.resizable(width=False, height=False)
        self.property_window.title('Add property')

        # property form
        self.propertyform = v.AddPropertyForm(self.property_window, self.data_model.fields, self.callbacks)
        self.propertyform.grid(row=0, padx=5, sticky='W')
        self.propertyform.columnconfigure(0, weight=1)

        # status bar
        self.prop_status = tk.StringVar()
        self.statusbar = ttk.Label(self.property_window, textvariable=self.prop_status)
        self.statusbar.grid(row=1, padx=10, sticky=('WE'))
        self.statusbar.columnconfigure(0, weight=1)

    def add_property(self):
        '''Save new property to the database'''

        # check for errors first
        errors = self.propertyform.get_errors()
        if errors:
            message = 'Cannot save record'
            detail = 'The following fields have errors: \n * {}'.format('\n * '.join(errors.keys()))
            self.prop_status.set(
                f'''Cannot save, error in fields: {', '.join(errors.keys())}'''
            )
            messagebox.showerror(title='Error', message=message, detail=detail)
            return False

        # get data
        data = self.propertyform.get()
        try:
            self.data_model.add_property(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem saving record',
                detail=str(e)
            )
            self.main_status.set('Problem saving record')
        else:
            self.records_saved += 1
            self.main_status.set(f'{self.records_saved} record(s) added this session')
            key = (data['Property ID'], data['Landlord ID'], data['Flat number'],
                   data['Street'], data['Post code'], data['City'])
            if self.data_model.last_write == 'insert property':
                self.inserted_rows.append(key)
            # reset form only when appending records
            self.propertyform.reset()
            self.populate_recordlist()
            self.property_window.destroy()

    def open_delete_property_window(self):
        '''Opens window for removal of property from database'''

        # opens window for new property entry
        self.delete_window = tk.Toplevel(self)
        self.delete_window.resizable(width=False, height=False)
        self.delete_window.title('Delete property')

        # get property data
        try:
            records = self.data_model.get_all_records()
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem reading database',
                detail=str(e)
            )
        else:
            updated_property_ids = [record[0] for record in records]

        # property form
        self.deletepropertyform = v.DeletePropertyForm(self.delete_window,
                                                       self.data_model.fields,
                                                       self.callbacks, updated_property_ids)
        self.deletepropertyform.grid(row=0, padx=5, sticky='W')
        self.deletepropertyform.columnconfigure(0, weight=1)

    def delete_property(self):
        '''Removes property from database'''

        # get data
        data = self.deletepropertyform.get()
        try:
            self.data_model.delete_property(data)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem deleting record',
                detail=str(e)
            )
            self.main_status.set('Problem deleting record')
        else:
            self.records_deleted += 1
            self.main_status.set(f'{self.records_deleted} record(s) deleted this session')
            self.populate_recordlist()
            self.delete_window.destroy()

    def retrieve_remote_emails(self):
        '''Retrieve emails from remote Microsoft server'''

        self.retrieve_emails(self.recipient_email)
        rows = self.data_model.get_documents_by_email(self.recipient_email,
                                                      self.attachment_option.get())
        self.documentform.populate(rows)

    def populate_documentlist(self):
        '''Opens list of documents sent by email, first from local database,
           else it retrieves the emails from Microsoft Outlook / Office365 /
           Exchange account.
        '''

        self.recipient_email = self.recordform.inputs['Email'].get()
        self.recipient_email = self.recipient_email if self.recipient_email else None

        # Microsoft Outlook/Office365/Exchange account email
        self.sent_email_account = self.settings_model.variables['account_email']['value']

        # populates document list with sent emails from 'docuemnts' table in database
        if self.recipient_email:
            rows = self.data_model.get_documents_by_email(self.recipient_email,
                                                          self.attachment_option.get())
        else:
            messagebox.showerror(
                title='Error',
                message='Please select recipient')
            return
        if rows:
            self.documentform.populate(rows)
        else:
            try:
                # retrieves email(s) from Microsoft Outlook/Office365/Exchange account
                self.retrieve_remote_emails()
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem fetching email(s)',
                    detail=str(e)
                )
                self.docs_status.set('Problem fetching email(s)')

        # status on sent email retrieval
        emails_loaded = str(self.documentform.count)
        retrieved_message = f'''Retrieved emails sent from {self.sent_email_account} to {self.recipient_email}, '''
        status_message = f'''{emails_loaded} email(s) listed in this session.'''
        docs_message = f'{retrieved_message}{status_message}'
        self.main_status.set(docs_message)
        self.docs_status.set(docs_message)

    def show_documents(self):
        '''Opens window showing list of documents to tenants'''

        # opens window for new property entry
        self.docs_window = tk.Toplevel(self)
        self.docs_window.resizable(width=False, height=False)
        self.docs_window.title('Document list')

        # document form
        self.documentform = v.DocumentList(self.docs_window, self.callbacks,
                                           self.attachment_option)
        self.documentform.grid(row=0, padx=5, sticky='NSEW')

        # status bar
        self.docs_status = tk.StringVar()
        self.docs_statusbar = ttk.Label(self.docs_window, textvariable=self.docs_status)
        self.docs_statusbar.grid(row=1, padx=10, sticky=(tk.W + tk.E))
        self.docs_statusbar.columnconfigure(0, weight=1)

        # populate the treeview with documents
        self.populate_documentlist()

    def print_list(self):
        '''Save list of documents sent by email to file'''

        filename = filedialog.asksaveasfilename(
            title='Select the target file for saving records',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
        )
        if filename:
            self.filename.set(filename)
            try:
                document_keys = m.CSVModel.document_fields.keys()
                rows = self.documentform.save_documentlist_to_file()
                documents_list = list({key: value for key, value in zip(document_keys, row)} for row in rows)
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem writing to file',
                    detail=str(e)
                )
            else:
                self.docs_status.set(f'Saved data to {self.filename.get()}')
                csv_write = m.CSVModel(filename=self.filename.get(), filepath=None)
                csv_write.save_record(documents_list, csv_write.document_fields.keys())

    def retrieve_emails(self, email):
        '''Retrieve list of documents sent by email'''

        try:
            sent_docs = n.RetrieveSentDocuments(self.settings)
            messagebox.showinfo(
                title='Retrieving email(s)',
                message=f'''Retrieving email(s) sent from {self.sent_email_account}
                            to {self.recipient_email}.
                            \n Press button to continue.''',
            )
            sent_docs.get(tenant_email=email)
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message='Problem retrieving email(s)',
                details=str(e)
            )
        else:
            for email in sent_docs.emails:
                self.data_model.insert_retrieved_documents(email)

    # import records from CSV file to database
    def on_file_import(self):
        '''Handles the file->import action from the menu'''

        filename = filedialog.askopenfilename(
            title='Select the file to import into the database',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
        )
        if filename:
            self.filename.set(filename)
            try:
                csv_read = m.CSVModel(filename=self.filename.get(),
                                      filepath=None)
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem reading file',
                    detail=str(e)
                )
            else:
                records = csv_read.get_all_records()
                for row in records:
                    self.data_model.add_landlords(row)
                for row in records:
                    self.data_model.add_property(row)
                    self.data_model.add_tenant(row)
                self.main_status.set(f'''Loaded data into {self.settings['db_name'].get()}''')
                self.populate_recordlist()

    # save records to CSV file
    def on_file_export(self):
        '''Handles the file->export action from the menu'''

        filename = filedialog.asksaveasfilename(
            title='Select the target file for saving records',
            defaultextension='.csv',
            filetypes=[('Comma-Separated Values', '*.csv *.CSV')]
        )
        if filename:
            self.filename.set(filename)
            try:
                rows = self.data_model.get_all_records()
            except Exception as e:
                messagebox.showerror(
                    title='Error',
                    message='Problem reading database',
                    detail=str(e)
                )
            else:
                self.main_status.set(f'Saved data to {self.filename.get()}')
                csv_write = m.CSVModel(filename=self.filename.get(),
                                       filepath=None)
                csv_write.save_record(rows, csv_write.fields.keys())

    def show_number_of_properties_by_landlord(self):
        popup = tk.Toplevel()
        bar_chart = v.BarChartView(popup,
                                   "Landlord",
                                   "Number of properties",
                                   "Number of properties by landlord")
        bar_chart.pack(fill='both', expand=True)
        data = self.data_model.get_properties_by_landlord()
        bar_chart.draw_bar_chart(data)

    def show_occupancy_in_properties(self):
        popup = tk.Toplevel()
        bar_chart = v.BarChartView(popup,
                                   "Street",
                                   "Number of properties",
                                   "Occupancy")
        bar_chart.pack(fill='both', expand=True)
        data = self.data_model.get_occupancy_by_building()
        bar_chart.draw_bar_chart(data)

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
