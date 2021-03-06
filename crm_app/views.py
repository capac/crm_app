import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.simpledialog import Dialog
from . import widgets as w
# matplotlib
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import use as mpl_use, pyplot as plt
mpl_use('TkAgg')
plt.style.use('ggplot')


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
            label='Add property'+chr(8230),
            command=callbacks['file->add_property']
            )
        file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Delete property'+chr(8230),
            command=callbacks['file->delete_property']
            )
        file_menu.add_separator()
        file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Import file with tenant data'+chr(8230),
            command=callbacks['file->import']
            )
        file_menu.add_command(
            # 8230: ASCII value for horizontal ellipsis
            label='Export file with tenant data'+chr(8230),
            command=callbacks['file->export']
            )
        self.add_cascade(label='File', menu=file_menu)
        file_menu.add_separator()
        stats_menu = tk.Menu(file_menu, tearoff=False)
        file_menu.add_cascade(label='Show statistics', menu=stats_menu)
        stats_menu.add_command(
            label='Show number of properties by landlord',
            command=callbacks['on_show_number_of_properties_by_landlord']
            )
        stats_menu.add_command(
            label='Show occupancy in buildings',
            command=callbacks['on_show_occupancy_in_properties']
            )

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
    '''The record form for our widgets'''

    def __init__(self, parent, fields, callbacks, input_var, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks
        self.input_var = input_var

        # a dictionary to keep track of input widgets
        self.inputs = {}

        # build the form
        self.record_label = ttk.Label(self)
        self.record_label.grid(row=0, column=0, padx=2, pady=(4, 0))

        # office information
        officeinfo = tk.LabelFrame(self, text='Office information', padx=5, pady=5)

        # line 1
        self.inputs['Property ID'] = w.LabelInput(officeinfo, 'Property ID',
                                                  field_spec=fields['Property ID'])
        self.inputs['Property ID'].grid(row=0, column=0)
        self.inputs['Landlord ID'] = w.LabelInput(officeinfo, 'Landlord ID',
                                                  field_spec=fields['Landlord ID'])
        self.inputs['Landlord ID'].grid(row=0, column=1)
        self.inputs['Number properties in building'] = \
            w.LabelInput(officeinfo, 'Number of properties in building',
                         field_spec=fields['Number properties in building'])
        self.inputs['Number properties in building'].grid(row=0, column=2)
        officeinfo.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # property information
        propertyinfo = tk.LabelFrame(self, text='Property information', padx=5, pady=5)

        # line 2
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
        propertyinfo.grid(row=2, column=0, sticky=(tk.W + tk.E))

        # tenant information
        tenantinfo = tk.LabelFrame(self, text='Tenant information', padx=5, pady=5)

        # line 3
        self.inputs['First name'] = w.LabelInput(tenantinfo, 'First name',
                                                 field_spec=fields['First name'])
        self.inputs['First name'].grid(row=0, column=0)
        self.inputs['Last name'] = w.LabelInput(tenantinfo, 'Last name',
                                                field_spec=fields['Last name'])
        self.inputs['Last name'].grid(row=0, column=1)
        self.inputs['Email'] = w.LabelInput(tenantinfo, 'Email',
                                            field_spec=fields['Email'])
        self.inputs['Email'].grid(row=0, column=2)
        tenantinfo.grid(row=3, column=0, sticky=(tk.W + tk.E))

        # command section
        command_section = tk.LabelFrame(self, text='Commands', padx=5, pady=5)
        self.updatebutton = w.LabelInput(command_section, 'Update tenant',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_update'])
        self.updatebutton.grid(row=0, column=0, padx=10, pady=(10, 0))
        self.documentsbutton = w.LabelInput(command_section, 'Show documents',
                                            input_class=ttk.Button,
                                            input_var=self.callbacks['on_show_documents'])
        self.documentsbutton.grid(row=0, column=1, padx=10, pady=(10, 0))
        # add checkbutton option for files with/without attachment
        self.attachmentoption = w.LabelInput(command_section, 'Select only email(s) with attachments',
                                             input_class=ttk.Checkbutton,
                                             input_var=self.input_var)
        self.attachmentoption.grid(row=0, column=2, padx=10, pady=(10, 0), sticky=tk.W)
        command_section.grid(row=4, column=0, sticky=(tk.W + tk.E))

    def get(self):
        '''Retrieve data from Tkinter and place it in regular Python objects'''

        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def get_errors(self):
        '''Get a list of field errors in the form'''

        errors = {}
        for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()
        return errors

    def load_record(self, rowkey, data=None):
        self.record_label.config(text='Property ID: {}'.format(rowkey))
        for key, widget in self.inputs.items():
            self.inputs[key].set(data.get(key, ''))
            try:
                widget.input.trigger_focusout_validation()
            except AttributeError:
                pass


class AddPropertyForm(tk.Frame):
    '''Widget input form for adding property'''

    def __init__(self, parent, fields, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks

        # a dictionary to keep track of input widgets
        self.inputs = {}

        # office information
        officeinfo = tk.LabelFrame(self, text='Office information', padx=5, pady=5)

        # line 1
        self.inputs['Property ID'] = w.LabelInput(officeinfo, 'Property ID',
                                                  field_spec=fields['Property ID'])
        self.inputs['Property ID'].grid(row=0, column=0)
        self.inputs['Landlord ID'] = w.LabelInput(officeinfo, 'Landlord ID',
                                                  field_spec=fields['Landlord ID'])
        self.inputs['Landlord ID'].grid(row=0, column=1)
        self.inputs['Number properties in building'] = \
            w.LabelInput(officeinfo, 'Number of properties in building',
                         field_spec=fields['Number properties in building Spinbox'])
        self.inputs['Number properties in building'].grid(row=0, column=2)
        officeinfo.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # property information
        propertyinfo = tk.LabelFrame(self, text='Property information', padx=5, pady=5)

        # line 2
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

        # command section
        command_section = tk.LabelFrame(self, text='Commands', padx=5, pady=5)
        self.savebutton = w.LabelInput(command_section, 'Add property',
                                       input_class=ttk.Button,
                                       input_var=self.callbacks['on_add_property'])
        self.savebutton.grid(row=0, column=0, padx=10, pady=(10, 0))
        command_section.grid(row=2, column=0, sticky=(tk.W + tk.E))

        # set default tk entry values to empty strings
        self.reset()

    def get(self):
        '''Retrieve data from Tkinter and place it in regular Python objects'''

        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def reset(self):
        '''Resets the form entries'''

        # clear all values
        for widget in self.inputs.values():
            widget.set('')

        self.focus_next_empty()

    def focus_next_empty(self):
        for labelwidget in self.inputs.values():
            if (labelwidget.get() == ''):
                labelwidget.input.focus()
                break

    def get_errors(self):
        '''Get a list of field errors in the form'''

        errors = {}
        for key, widget in self.inputs.items():
            if hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if widget.error.get():
                errors[key] = widget.error.get()
        return errors


class DeletePropertyForm(tk.Frame):
    '''Widget input form for deleting property'''

    def __init__(self, parent, fields, callbacks, updated_prop_ids, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks

        # a dictionary to keep track of input widgets
        self.inputs = {}

        # property information
        propertyinfo = tk.LabelFrame(self, text='Property information', padx=5, pady=5)

        # line 1
        self.inputs['Property ID'] = w.LabelInput(propertyinfo, 'Property ID',
                                                  field_spec=fields['Property ID Dropdown'],
                                                  input_args={'values': updated_prop_ids})
        self.inputs['Property ID'].grid(row=0, column=0)
        self.deletebutton = w.LabelInput(propertyinfo, 'Delete property',
                                         input_class=ttk.Button,
                                         input_var=self.callbacks['on_delete_property'])
        self.deletebutton.grid(row=0, column=1, padx=10, pady=(16, 0))
        propertyinfo.grid(row=0, column=0, sticky=tk.W)
        propertyinfo.columnconfigure(0, weight=1)

    def get(self):
        '''Retrieve data from Tkinter and place it in regular Python objects'''

        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data


class DocumentList(tk.Frame):
    '''Display documents sent to tenants'''

    column_defs = {
        '#0': {'label': 'Row', 'anchor': tk.W},
        'Subject': {'label': 'Subject', 'width': 400},
        'Recipient': {'label': 'Recipient', 'width': 220},
        'Date sent': {'label': 'Date sent', 'width': 180},
        'Date retrieved': {'label': 'Date retrieved', 'width': 180},
        'Attachments': {'label': 'Attachments', 'width': 260},
    }
    default_width = 100
    default_minwidth = 20
    default_anchor = tk.W

    def __init__(self, parent, callbacks, input_var, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.callbacks = callbacks
        self.input_var = input_var
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

        commandinfo = tk.LabelFrame(self, text='Commands', padx=5, pady=5)
        # add print button
        self.printbutton = w.LabelInput(commandinfo, 'Save list to file',
                                        input_class=ttk.Button,
                                        input_var=self.callbacks['on_print_list'])
        self.printbutton.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=tk.E)
        # add refresh button
        self.refreshbutton = w.LabelInput(commandinfo, 'Retrieve remote emails',
                                          input_class=ttk.Button,
                                          input_var=self.callbacks['on_retrieve_emails'])
        self.refreshbutton.grid(row=0, column=1, padx=10, pady=(10, 0), sticky=tk.W)
        # add checkbutton option for files with/without attachment
        self.attachmentoption = w.LabelInput(commandinfo, 'Select only email(s) with attachments',
                                             input_class=ttk.Checkbutton,
                                             input_var=self.input_var)
        self.attachmentoption.grid(row=0, column=2, padx=10, pady=(10, 0), sticky=tk.W)
        commandinfo.grid(row=1, column=0, columnspan=2, sticky=(tk.W + tk.E))

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

    def populate(self, rows):
        '''Clear the treeview and write the supplied data rows to it'''

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        # create striped row tags
        self.treeview.tag_configure('oddrow', background='white')
        self.treeview.tag_configure('evenrow', background='lightblue')

        valuekeys = list(self.column_defs.keys())[1:]
        row_count = 0
        for rowdata in rows:
            # if there are no attachments in the sent email
            att = rowdata['Attachments']
            split_attachments = att[1:-1].split(',') if isinstance(att, str) else None
            rowkey = (str(rowdata['Subject']), str(rowdata['Recipient']),
                      str(rowdata['Date sent']), str(rowdata['Date retrieved']),
                      str(rowdata['Attachments']))
            values = [rowdata[key] for key in valuekeys]
            stringkey = '{}|{}|{}|{}|{}'.format(*rowkey)
            if split_attachments is None:
                self.treeview.insert('', 'end', iid=stringkey, text=stringkey, values=values)
                row_count += 1
            # for email with one or more attachments
            else:
                for attach in split_attachments:
                    rowkey = (str(rowdata['Subject']), str(rowdata['Recipient']),
                              str(rowdata['Date sent']), str(attach))
                    stringkey = '{}|{}|{}|{}'.format(*rowkey)
                    values = [rowdata[key] for key in valuekeys[:-1]] + [attach]
                    if len(split_attachments) > 1:
                        self.treeview.insert('', 'end', iid=stringkey, text=stringkey, values=values, tags=('evenrow',))
                    else:
                        self.treeview.insert('', 'end', iid=stringkey, text=stringkey, values=values, tags=('oddrow',))
                    row_count += 1
        self.count = row_count

    def save_documentlist_to_file(self):
        '''Appends records from the document table to a Python list'''

        rows = []
        for rowkey in self.treeview.get_children():
            row = self.treeview.item(rowkey)['values']
            rows.append(row)
        return rows


class RecordList(tk.Frame):
    '''Display records in the database'''

    column_defs = {
        '#0': {'label': 'Row', 'anchor': tk.W},
        'Property ID': {'label': 'Property ID', 'anchor': tk.CENTER, 'width': 80},
        'Landlord ID': {'label': 'Landlord ID', 'anchor': tk.CENTER, 'width': 70},
        'Number properties in building': {'label': 'Number properties in building',
                                          'width': 175, 'anchor': tk.E},
        'Flat number': {'label': 'Flat number', 'width': 80, 'anchor': tk.E},
        'Street': {'label': 'Street', 'width': 175},
        'Post code': {'label': 'Post code', 'width': 80},
        'City': {'label': 'City', 'width': 80},
        'First name': {'label': 'First name', 'width': 115},
        'Last name': {'label': 'Last name', 'width': 110},
        'Email': {'label': 'Email', 'width': 225},
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
        self.treeview.tag_configure('inserted_tenant', background='lightgreen')
        self.treeview.tag_configure('inserted_property', background='lightsalmon')
        self.treeview.tag_configure('updated_tenant', background='deepskyblue')

        # bind selection
        self.treeview.bind('<<TreeviewSelect>>', self.on_open_record)

    def on_open_record(self, *args):
        try:
            selected_id = self.treeview.selection()[0]
            self.callbacks['on_open_record'](selected_id.split('|')[0])
        # quick fix when window loses focus and no line is selected,
        # a better fix is to find a way to keep the line selected
        except IndexError:
            pass

    def populate(self, rows):
        '''Clear the treeview and write the supplied data rows to it'''

        for row in self.treeview.get_children():
            self.treeview.delete(row)

        valuekeys = list(self.column_defs.keys())[1:]
        for rowdata in rows:
            rowkey_pr = (str(rowdata['Property ID']), str(rowdata['Landlord ID']),
                         str(rowdata['Number properties in building']),
                         str(rowdata['Flat number']),
                         str(rowdata['Street']),
                         str(rowdata['Post code']), str(rowdata['City']))
            rowkey_tn = (str(rowdata['Property ID']), str(rowdata['First name']),
                         str(rowdata['Last name']), str(rowdata['Email']))
            rowkey = rowkey_pr + rowkey_tn
            values = [rowdata[key] for key in valuekeys]
            if self.inserted and rowkey_tn in self.inserted:
                tag = 'inserted_tenant'
            elif self.updated and rowkey_tn in self.updated:
                tag = 'updated_tenant'
            elif self.inserted and rowkey_pr in self.inserted:
                tag = 'inserted_property'
            else:
                tag = ''
            stringkey = '{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(*rowkey)
            self.treeview.insert('', 'end', iid=stringkey, text=stringkey,
                                 values=values, tag=tag)

        # selects automatically the first row, to make selections keyboard-friendly
        if len(rows) > 0:
            firstrow = self.treeview.identify_row(0)
            self.treeview.focus_set()
            self.treeview.selection_set(firstrow)
            self.treeview.focus(firstrow)


class BarChartView(tk.Frame):
    '''Graphical plots showing some statistics on occupancy'''

    def __init__(self, parent, x_axis, y_axis, title):
        super().__init__(parent)
        self.figure = Figure(figsize=(8, 6), dpi=100, layout='tight')
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        # axes
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.axes.set_xlabel(x_axis, fontsize=14)
        self.axes.set_ylabel(y_axis, fontsize=14)
        self.axes.set_title(title, fontsize=16)

    def draw_bar_chart(self, data):
        labels, prime_values, *secondary_values = zip(*data)
        self.bar = self.axes.bar(labels, prime_values, color=plt.cm.Paired.colors,
                                 edgecolor='k', label=labels, alpha=0.8)
        self.axes.legend(self.bar, labels)
        if secondary_values:
            top_values = np.array(secondary_values[0])-np.array(prime_values)
            self.bar = self.axes.bar(labels, top_values, bottom=prime_values,
                                     color=plt.cm.Paired.colors, edgecolor='k',
                                     label=labels, alpha=0.4)
            self.axes.legend(self.bar, [])
            text_loc = float(self.axes.yaxis.get_data_interval()[1])
            self.axes.set_ylim([0, text_loc+3])
            # annotate labels
            occupancy_values = [int(x) for x in secondary_values[1]]
            for x, y in zip(labels, occupancy_values):
                self.axes.annotate('{0:d}%'.format(y), xy=(x, text_loc+1.5),
                                   ha='center', size=12, color='k')
        plt.setp(self.axes.get_xticklabels(), ha="right",
                 rotation_mode="anchor",
                 rotation=45, fontsize=14)
        plt.setp(self.axes.get_yticklabels(), fontsize=14)


class LoginDialog(Dialog):
    def __init__(self, parent, title, error=''):
        self.pw = tk.StringVar()
        self.user = tk.StringVar()
        self.error = tk.StringVar(value=error)
        super().__init__(parent, title=title)

    def body(self, parent):
        lf = tk.Frame(self)
        self.geometry('280x180')
        ttk.Label(lf, text='Login to database',
                  font='Sans 20').grid(row=0)

        ttk.Style().configure('TEntry', background='white',
                              foreground='black')
        ttk.Style().configure('err.TLabel', background='darkred',
                              foreground='white')
        if self.error.get():
            ttk.Label(lf, textvariable=self.error,
                      style='err.TLabel').grid(row=1)
        ttk.Label(lf, text='User name:').grid(row=2)
        self.username_inp = ttk.Entry(lf, textvariable=self.user)
        self.username_inp.grid(row=3)
        ttk.Label(lf, text='Password:').grid(row=4)
        self.password_inp = ttk.Entry(lf, show='*', textvariable=self.pw)
        self.password_inp.grid(row=5)
        lf.pack()
        return self.username_inp

    def apply(self):
        self.result = (self.user.get(), self.pw.get())
