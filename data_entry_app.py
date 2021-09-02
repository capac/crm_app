import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import csv
from cfi_codes import property_ids


class LabelInput(tk.Frame):
    '''A widget containing a label and input together'''

    def __init__(self, parent, label='', input_class=ttk.Entry, input_var=None,
                 input_args=None, label_args=None, **kwargs):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = input_var

        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args['text'] = label
            input_args['variable'] = input_var
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args['textvariable'] = input_var

        self.input = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=(tk.E + tk.W))
        self.columnconfigure(0, weight=1)

    def grid(self, sticky=(tk.E + tk.W), **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            elif type(self.input) == tk.Text:
                return self.input.get('1.0', tk.END)
            else:
                return self.input.get()
        except (TypeError, tk.TclError):
            # happens when numeric fields are empty
            return ''

    def set(self, value, *args, **kwargs):
        if type(self.variable) == tk.BooleanVar:
            self.variable.set(bool(value))
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
        elif type(self.input) in (ttk.Checkbutton, ttk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == tk.Text:
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
        else:  # input must be an Entry-type widget with no variable
            self.input.delete(0, tk.END)
            self.input.insert('1.0', value)


class DataRecordForm(tk.Frame):
    '''The input form for our widgets'''

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # a dictionary to keep track of input widgets
        self.inputs = {}
        # property id codes for CFI
        officeinfo = tk.LabelFrame(self, text='Office information')

        # Office information
        self.inputs['property_id'] = LabelInput(officeinfo, 'Property ID',
                                                input_class=ttk.Combobox,
                                                input_var=tk.StringVar(),
                                                input_args={'values': property_ids()})
        self.inputs['property_id'].grid(row=0, column=0)
        self.inputs['landlord_company'] = LabelInput(officeinfo, 'Landlord company', input_var=tk.StringVar())
        self.inputs['landlord_company'].grid(row=0, column=1)
        officeinfo.grid(row=0, column=0, sticky=(tk.W + tk.E))

        # Property information
        propertyinfo = tk.LabelFrame(self, text='Property information')
        self.inputs['flat_num'] = LabelInput(propertyinfo, 'Flat number', input_var=tk.StringVar())
        self.inputs['flat_num'].grid(row=0, column=0)
        self.inputs['address'] = LabelInput(propertyinfo, 'Address', input_var=tk.StringVar())
        self.inputs['address'].grid(row=0, column=1)
        self.inputs['post_code'] = LabelInput(propertyinfo, 'Post code', input_var=tk.StringVar())
        self.inputs['post_code'].grid(row=0, column=2)
        self.inputs['city'] = LabelInput(propertyinfo, 'City', input_var=tk.StringVar())
        self.inputs['city'].grid(row=0, column=3)
        propertyinfo.grid(row=1, column=0, sticky=(tk.W + tk.E))

        # Tenant information
        tenantinfo = tk.LabelFrame(self, text='Tenant information')
        self.inputs['first_name'] = LabelInput(tenantinfo, 'First name', input_var=tk.StringVar())
        self.inputs['first_name'].grid(row=0, column=0)
        self.inputs['last_name'] = LabelInput(tenantinfo, 'Last name', input_var=tk.StringVar())
        self.inputs['last_name'].grid(row=0, column=1)
        self.inputs['email'] = LabelInput(tenantinfo, 'Email', input_var=tk.StringVar())
        self.inputs['email'].grid(row=0, column=2)
        tenantinfo.grid(row=2, column=0, sticky=(tk.W + tk.E))

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


class Application(tk.Tk):
    '''Application root window'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # application title
        self.title('Data Entry Form')
        self.resizable(width=False, height=False)
        # application name
        ttk.Label(self, text='Chalk Farm Investment Data Entry Form', font=('TkDefaultFont', 16)).grid(row=0)
        # data form
        self.recordform = DataRecordForm(self)
        self.recordform.grid(row=1, padx=10)
        # save button
        self.savebutton = ttk.Button(self, text='Save', command=self.on_save)
        self.savebutton.grid(row=2, padx=10, pady=(5, 0), sticky=(tk.E))
        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(row=3, padx=10, sticky=(tk.W + tk.E))

    def on_save(self):
        datestring = datetime.today().strftime('%Y-%m-%d')
        filename = f'data_record_{datestring}.csv'
        # does the file exist?
        newfile = not os.path.exists(filename)
        # get data
        data = self.recordform.get()
        # save to file
        with open(filename, 'a') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(data)


if __name__ == '__main__':
    app = Application()
    app.mainloop()
