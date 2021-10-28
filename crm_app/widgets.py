import tkinter as tk
from tkinter import ttk
from .constants import FieldTypes as FT


class ValidatedMixin:
    '''Adds a validation functionality to an input widget'''

    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        style = ttk.Style()
        widget_class = self.winfo_class()
        validated_style = 'ValidatedInput.' + widget_class
        style.map(
            validated_style,
            foreground=[('invalid', 'white'), ('!invalid', 'black')],
            fieldbackground=[('invalid', 'darkred'), ('!invalid', 'white')]
        )

        self.config(
            style=validated_style,
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    # valid event
    def _validate(self, proposed, current, char, event, index, action):
        '''
        The validation method, don't override this method,
        override the _key_validate and _focus_validate methods.
        '''

        self.error.set('')
        valid = True
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(proposed=proposed, current=current,
                                       char=char, event=event, index=index,
                                       action=action)
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    # invalid event
    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(proposed=proposed, current=current,
                              char=char, event=event, index=index,
                              action=action)

    def _focusout_invalid(self, **kwargs):
        '''Handle invalid data on a focus event'''

        pass

    def _key_invalid(self, **kwargs):
        ''''Handle invalid data on a key event. By default we want to do nothing'''

        pass

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid


class RequiredEntry(ValidatedMixin, ttk.Entry):
    '''A class requiring all entry fields to not be empty'''

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):
    '''A class requiring comboboxes to do the following:
         * If the proposed text matches no entries, it will be ignored,
         * when the proposed text matches a single entry, the widget is set to that value,
         * a delete or backspace clears the entire box.
    '''

    def _key_validate(self, proposed, action, **kwargs):
        valid = True
        # if the user tries to delete, just clear the field
        if action == '0':
            self.set('')
            return True

        # get our value list
        values = self.cget('values')
        # do a case-insensitive match against the entered text
        matching = [
            x for x in values if x.lower().startswith(proposed.lower())
        ]
        if len(matching) == 0:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid = False
        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class LabelInput(tk.Frame):
    '''A widget containing a label and input together'''

    field_types = {
        FT.string: (RequiredEntry, tk.StringVar),
        FT.string_list: (ValidatedCombobox, tk.StringVar),
        FT.long_string: (tk.Text, lambda: None),
    }

    def __init__(self, parent, label='', input_class=None, input_var=None,
                 input_args=None, label_args=None, field_spec=None, **kwargs):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        if field_spec:
            field_type = field_spec.get('type', FT.string)
            input_class = input_class or self.field_types.get(field_type)[0]
            var_type = self.field_types.get(field_type)[1]
            self.variable = input_var if input_var else var_type()
            # values
            if 'values' in field_spec and 'values' not in input_args:
                input_args['values'] = field_spec.get('values')
        else:
            self.variable = input_var

        if input_class == ttk.Button:
            input_args['text'] = label
            input_args['command'] = input_var
        else:
            self.label = ttk.Label(self, text=label, width=25, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_args['textvariable'] = self.variable

        self.input = input_class(self, **input_args)
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)
        # show actual error message
        self.error = getattr(self.input, 'error', tk.StringVar())
        self.error_label = ttk.Label(self, textvariable=self.error)
        self.error_label.grid(row=2, column=0, sticky=(tk.W + tk.E))

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
        if self.variable:
            self.variable.set(value, *args, **kwargs)
        elif type(self.input) == tk.Text:
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
        else:  # input must be an Entry-type widget with no variable
            self.input.delete(0, tk.END)
            self.input.insert('1.0', value)
