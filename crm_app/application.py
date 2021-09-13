import tkinter as tk
from tkinter import ttk
from datetime import datetime
from . import views as v
from . import models as m


class Application(tk.Tk):
    '''Application root window'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # application title
        self.title('Data Entry Form')
        self.resizable(width=False, height=False)
        # application name
        ttk.Label(self, text='Chalk Farm Investment Data Query Form', font=('TkDefaultFont', 16)).grid(row=0)
        # data form
        self.recordform = v.DataRecordForm(self, m.CSVModel.fields)
        self.recordform.grid(row=1, padx=10)
        # save button
        self.savebutton = ttk.Button(self, text='Save to CSV', command=self.on_save)
        self.savebutton.grid(row=2, padx=10, pady=(10, 0), sticky=(tk.E))
        # status bar
        self.status = tk.StringVar()
        self.statusbar = ttk.Label(self, textvariable=self.status)
        self.statusbar.grid(row=3, padx=10, pady=(0, 10), sticky=(tk.W + tk.E))
        self.records_saved = 0

    def on_save(self):
        '''Handles save button clicks'''

        # check for errors first
        errors = self.recordform.get_errors()
        if errors:
            self.status.set(
                f'''Cannot save, error in fields: {', '.join(errors.keys())}'''
            )
            return False

        datestring = datetime.today().strftime('%Y-%m-%d')
        filename = f'data_record_{datestring}.csv'
        model = m.CSVModel(filename)
        # get data
        data = self.recordform.get()
        model.save_record(data)
        self.records_saved += 1
        self.status.set(f'{self.records_saved} record(s) saved this session')
        self.recordform.reset()
