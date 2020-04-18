import tkinter
import pathlib
import os

from certificate_factory import *

class CertificateManager:
    def __init__(self, parent, update_paths_function):
        self.update_paths_function = update_paths_function
        self.top = tkinter.Toplevel(parent)
        self.top.title('Certificate generation')
        width = 400
        height = 150
        x = (parent.winfo_screenwidth() // 2) - (width // 2)
        y = (parent.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.top.resizable(False, False)

        main_frame = tkinter.Frame(self.top)

        #host name
        first_row_frame = tkinter.Frame(main_frame)
        tkinter.Label(first_row_frame, text='Hostname').grid(row=0, column=0, padx=5)
        self.hostname_entry = tkinter.Entry(first_row_frame, width=35)
        self.hostname_entry.grid(row=0, column=1, columnspan=2)
        first_row_frame.grid(row=0, column=0, pady=5, sticky=tkinter.W)

        #key size and days valid
        second_row_frame = tkinter.Frame(main_frame)
        tkinter.Label(second_row_frame, text='Key size').pack(padx=5, side=tkinter.LEFT)
        self.key_size_entry = tkinter.Entry(second_row_frame, width=7)
        self.key_size_entry.insert(tkinter.END, '2048')
        self.key_size_entry.pack(padx=5, side=tkinter.LEFT)

        tkinter.Label(second_row_frame, text='Days valid').pack(padx=5, side=tkinter.LEFT)
        self.days_valid_entry = tkinter.Entry(second_row_frame, width=7)
        self.days_valid_entry.pack(padx=5, side=tkinter.RIGHT)
        second_row_frame.grid(row=1, column=0, pady=5, sticky=tkinter.W)

        #submit
        tkinter.Button(main_frame, text='Submit',
                       command=self.generate, width=15).grid(row=2, column=0)
        main_frame.pack(pady=25)
        self.top.grab_set()

    @classmethod
    def is_of_type(cls, string_variable, type_to_check):
        try:
            type_to_check(string_variable)
            return True
        except:
            return False

    def generate(self):
        if not self.hostname_entry.get():
            tkinter.messagebox.showwarning(
                'Configuration', 'Enter hostname'
            )

        if not CertificateManager.is_of_type(self.key_size_entry.get(), int) \
                or int(self.key_size_entry.get()) <= 0:
            tkinter.messagebox.showwarning(
                'Configuration', 'Invalid key size'
            )
            return

        if not CertificateManager.is_of_type(self.days_valid_entry.get(), float) \
                 or float(self.days_valid_entry.get()) <= 0:
            tkinter.messagebox.showwarning(
                'Configuration', 'Invalid number of days valid'
            )
            return

        try:
            CertificateFactory.create_self_signed_cert(int(self.key_size_entry.get()),
                                                       self.hostname_entry.get(),
                                                       float(self.days_valid_entry.get()))
            tkinter.messagebox.showinfo(
                'Configuration', 'The certificate was created'
            )
        except:
            tkinter.messagebox.showwarning(
                'Configuration', 'An error occurred'
            )

        directory = str(pathlib.Path(__file__).parent.absolute())
        self.update_paths_function(os.path.join(directory, CERT_FILE),
                                   os.path.join(directory, KEY_FILE))

        self.top.destroy()
