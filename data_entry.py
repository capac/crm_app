import tkinter as tk
from tkinter import ttk


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


class Application(tk.Tk):
    '''Application root window'''


if __name__ == '__main__':
    app = Application()
    app.mainloop()
