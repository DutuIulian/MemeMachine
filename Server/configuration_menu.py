import configparser
import tkinter
import tkinter.filedialog
import os
import json
import hashlib

from certificate_manager import CertificateManager

class ConfigurationMenu:
    def __init__(self, parent):
        self.configuration = configparser.ConfigParser()
        self.configuration.read('configuration.ini')
        if not self.configuration.has_section('SETTINGS'):
            self.configuration.add_section('SETTINGS')
        self.parent = parent
        self.top = None

    def are_settings_valid(self):
        if not self.configuration.has_option('SETTINGS', 'port') \
                or not ConfigurationMenu.is_of_type(self.configuration['SETTINGS']['port'], int):
            return False
        if not self.configuration.has_option('SETTINGS', 'queue_size') \
                or not ConfigurationMenu.is_of_type(self.configuration['SETTINGS']['queue_size'], int):
            return False
        if not self.configuration.has_option('SETTINGS', 'timeout') \
                or not ConfigurationMenu.is_of_type(self.configuration['SETTINGS']['timeout'], float):
            return False
        if not self.configuration.has_option('SETTINGS', 'ssl') \
                or not self.configuration['SETTINGS']['ssl'] in ['On', 'Off']:
            return False
        if self.configuration.has_option('SETTINGS', 'ssl') \
                and self.configuration['SETTINGS']['ssl'] == 'On' \
                and (not self.configuration.has_option('SETTINGS', 'certificate') \
                or not os.path.isfile(self.configuration['SETTINGS']['certificate'])):
            return False
        if self.configuration.has_option('SETTINGS', 'ssl') \
                and self.configuration['SETTINGS']['ssl'] == 'On' \
                and (not self.configuration.has_option('SETTINGS', 'key') \
                or not os.path.isfile(self.configuration['SETTINGS']['key'])):
            return False
        if not self.configuration.has_option('SETTINGS', 'folders') \
                or not json.loads(self.configuration['SETTINGS']['folders']):
            return False
        for folder in json.loads(self.configuration['SETTINGS']['folders']):
            if not os.path.isdir(folder):
                return
        if not self.configuration.has_option('SETTINGS', 'extensions') \
                or not json.loads(self.configuration['SETTINGS']['extensions']):
            return False
        if not self.configuration.has_option('SETTINGS', 'password_hash') \
                or not self.configuration['SETTINGS']['password_hash']:
            return False

        return True

    def get_parameter(self, key):
        return self.configuration['SETTINGS'][key]

    def show(self):
        self.build_menu()
        self.put_values_into_entries()

    def build_menu(self):
        self.top = tkinter.Toplevel(self.parent)
        self.top.title('Configuration')
        width = 900
        height = 520
        x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.top.resizable(False, False)
        main_frame = tkinter.Frame(self.top)

        #
        first_row_frame = tkinter.Frame(main_frame)
        tkinter.Label(first_row_frame, text='Port').pack(padx=5, side=tkinter.LEFT,
                                                         expand=True, fill=tkinter.BOTH)
        self.port_variable = tkinter.StringVar()
        port_entry = tkinter.Entry(first_row_frame, textvariable=self.port_variable, width=7)
        port_entry.pack(padx=5, side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        connection_queue_size_label = tkinter.Label(first_row_frame, text='Connection queue size')
        connection_queue_size_label.pack(padx=5, side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self.queue_size_variable = tkinter.StringVar()
        queue_size_entry = tkinter.Entry(first_row_frame,
                                         textvariable=self.queue_size_variable, width=5)
        queue_size_entry.pack(padx=5, side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        tkinter.Label(first_row_frame, text='Timeout (s)').pack(padx=5, side=tkinter.LEFT,
                                                                expand=True, fill=tkinter.BOTH)
        self.timeout_variable = tkinter.StringVar()
        timeout_entry = tkinter.Entry(first_row_frame, textvariable=self.timeout_variable, width=5)
        timeout_entry.pack(padx=5, side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        first_row_frame.grid(row=0, column=0, pady=(40, 5), sticky=tkinter.W)

        #
        second_row_frame = tkinter.Frame(main_frame)
        tkinter.Label(second_row_frame, text='SSL').pack(side=tkinter.LEFT, padx=5)
        self.ssl_variable = tkinter.StringVar()
        ssl_option_menu = tkinter.OptionMenu(second_row_frame, self.ssl_variable, *['On', 'Off'])
        ssl_option_menu.configure(width=5)
        ssl_option_menu.pack(side=tkinter.LEFT, padx=5)
        tkinter.Button(second_row_frame, text='Generate certificate',
                       command=lambda: CertificateManager(self.top, self.update_paths),
                       width=20).pack(side=tkinter.LEFT, padx=5)
        second_row_frame.grid(row=1, column=0, sticky=tkinter.W)

        #
        third_row_frame = tkinter.Frame(main_frame)
        tkinter.Label(third_row_frame, text='Certificate', width=8).pack(side=tkinter.LEFT, padx=5)
        self.certificate_variable = tkinter.StringVar()
        certificate_entry = tkinter.Entry(third_row_frame, width=80,
                                          textvariable=self.certificate_variable)
        certificate_entry.pack(side=tkinter.LEFT, padx=5)
        tkinter.Button(third_row_frame, text='Browse', width=10,
                       command=lambda: ConfigurationMenu.browse_file(self.certificate_variable, self.top)).pack(side=tkinter.LEFT, padx=5)
        third_row_frame.grid(row=2, column=0, sticky=tkinter.W)

        #
        fourth_row_frame = tkinter.Frame(main_frame)
        tkinter.Label(fourth_row_frame, text='Key', width=8).pack(side=tkinter.LEFT, padx=5)
        self.key_variable = tkinter.StringVar()
        key_entry = tkinter.Entry(fourth_row_frame, textvariable=self.key_variable, width=80)
        key_entry.pack(side=tkinter.LEFT, padx=5)
        browse_button = tkinter.Button(fourth_row_frame, text='Browse', width=10,
                                       command=lambda: ConfigurationMenu.browse_file(self.key_variable, self.top))
        browse_button.pack(side=tkinter.LEFT, padx=5)
        fourth_row_frame.grid(row=3, column=0, sticky=tkinter.W)

        #
        fifth_row_frame = tkinter.Frame(main_frame)
        tkinter.Label(fifth_row_frame, text='Password', width=8).pack(side=tkinter.LEFT, padx=5)
        self.password_variable = tkinter.StringVar()
        password_entry = tkinter.Entry(fifth_row_frame, width=20,
                                       textvariable=self.password_variable, show='*')
        password_entry.pack(side=tkinter.LEFT, padx=5)

        tkinter.Label(fifth_row_frame, text='Confirm', width=8).pack(side=tkinter.LEFT, padx=5)
        self.confirm_password_variable = tkinter.StringVar()
        confirm_password_entry = tkinter.Entry(fifth_row_frame, show='*', width=20,
                                               textvariable=self.confirm_password_variable)
        confirm_password_entry.pack(side=tkinter.LEFT, padx=5)
        change_password_button = tkinter.Button(fifth_row_frame, text='Change',
                                                command=self.change_password, width=10)
        change_password_button.pack(side=tkinter.LEFT, padx=5)
        fifth_row_frame.grid(row=4, column=0, sticky=tkinter.W)

        #
        sixth_row_frame = tkinter.Frame(main_frame)
        left_frame = tkinter.Frame(sixth_row_frame)
        tkinter.Label(left_frame, text='Folders').grid(columnspan=2, row=0, column=0, sticky='ew')
        self.folder_variable = tkinter.Variable()
        self.folder_list = tkinter.Listbox(left_frame, listvariable=self.folder_variable, width=80)
        self.folder_list.grid(columnspan=2, row=1, column=0, pady=5)
        tkinter.Button(left_frame, text='Browse',
                       command=lambda: ConfigurationMenu.browse_folder(self.folder_list, self.top)).grid(row=2, column=0, sticky='ew')
        remove_folder_button = tkinter.Button(left_frame, text='Remove',
                                              command=lambda: self.folder_list.delete(tkinter.ANCHOR))
        remove_folder_button.grid(row=2, column=1, sticky='ew')
        left_frame.grid(row=0, column=0, sticky='nw', padx=5)

        right_frame = tkinter.Frame(sixth_row_frame)
        tkinter.Label(right_frame, text='File extensions').grid(columnspan=2, row=0, column=0)
        self.extension_variable = tkinter.Variable()
        self.extension_list = tkinter.Listbox(right_frame, listvariable=self.extension_variable, width=20)
        self.extension_list.grid(columnspan=2, row=1, column=0, pady=5)
        extension_frame = tkinter.Frame(right_frame)
        extension_entry = tkinter.Entry(extension_frame, width=6)
        extension_entry.pack(side=tkinter.LEFT)
        add_extension_button = tkinter.Button(extension_frame, text='Add',
                                              command=lambda: self.add_extension(extension_entry))
        add_extension_button.pack(side=tkinter.LEFT)
        tkinter.Button(extension_frame, text='Remove', command=lambda: self.extension_list.delete(tkinter.ANCHOR)).pack(side=tkinter.RIGHT)
        extension_frame.grid(row=3, column=0)
        right_frame.grid(row=0, column=1, sticky='ne', padx=5)
        sixth_row_frame.grid(row=5, column=0, pady=20)

        #
        submit_button = tkinter.Button(main_frame, text='Submit', width=15,
                                       command=self.submit_configurations)
        submit_button.grid(row=7, column=0)
        main_frame.pack(fill='y', expand=True, pady=10)
        self.top.grab_set()

    def put_values_into_entries(self):
        ConfigurationMenu.try_to_call_function(lambda: self.port_variable.set(self.configuration['SETTINGS']['port']))
        ConfigurationMenu.try_to_call_function(lambda: self.queue_size_variable.set(self.configuration['SETTINGS']['queue_size']))
        ConfigurationMenu.try_to_call_function(lambda: self.timeout_variable.set(self.configuration['SETTINGS']['timeout']))
        try:
            self.ssl_variable.set(self.configuration['SETTINGS']['ssl'])
        except:
            self.ssl_variable.set('On')
        if self.ssl_variable.get() not in ['On', 'Off']:
            self.ssl_variable.set('On')
        ConfigurationMenu.try_to_call_function(lambda: self.certificate_variable.set(self.configuration['SETTINGS']['certificate']))
        ConfigurationMenu.try_to_call_function(lambda: self.key_variable.set(self.configuration['SETTINGS']['key']))
        try:
            for folder in json.loads(self.configuration['SETTINGS']['folders']):
                self.folder_list.insert('end', folder)
        except:
            pass
        try:
            for extension in json.loads(self.configuration['SETTINGS']['extensions']):
                self.extension_list.insert('end', extension)
        except:
            pass

    @classmethod
    def try_to_call_function(cls, function):
        try:
            function()
        except:
            pass

    def add_extension(self, extension_entry):
        if extension_entry.get():
            self.extension_list.insert('end', extension_entry.get())

    def browse_file(variable_to_update, top):
        file_name = tkinter.filedialog.askopenfilename(parent=top, title='Open')
        if file_name:
            variable_to_update.set(file_name)

    @classmethod
    def browse_folder(cls, list_to_update, top):
        folder_name = tkinter.filedialog.askdirectory(parent=top, title='Open')
        if folder_name:
            list_to_update.insert('end', folder_name)

    def change_password(self):
        password = self.password_variable.get().encode('utf-8')
        confirmed_password = self.confirm_password_variable.get().encode('utf-8')
        if password != confirmed_password:
            tkinter.messagebox.showwarning(
                'Configuration', 'The two passwords do not match'
            )
        elif not password:
            tkinter.messagebox.showwarning(
                'Configuration', 'Password can not be empty'
            )
        else:
            self.configuration['SETTINGS']['password_hash'] = hashlib.sha256(password).hexdigest()
            tkinter.messagebox.showinfo(
                'Password',
                'The password was changed'
            )

    def submit_configurations(self):
        if not ConfigurationMenu.is_of_type(self.port_variable.get(), int) or int(self.port_variable.get()) <= 0 or int(self.port_variable.get()) > 65535:
            tkinter.messagebox.showwarning(
                'Configuration', 'Invalid port'
            )
            return

        if not ConfigurationMenu.is_of_type(self.queue_size_variable.get(), int) or int(self.queue_size_variable.get()) <= 0:
            tkinter.messagebox.showwarning(
                'Configuration', 'Invalid queue size'
            )
            return

        if not ConfigurationMenu.is_of_type(self.timeout_variable.get(), float) or float(self.timeout_variable.get()) <= 0:
            tkinter.messagebox.showwarning(
                'Configuration', 'Invalid timeout'
            )
            return

        if self.ssl_variable.get() == 'On' and (not os.path.isfile(self.certificate_variable.get()) or not os.path.isfile(self.key_variable.get())):
            tkinter.messagebox.showwarning(
                'Configuration', 'Enter valid certificate and key'
            )
            return

        if not self.folder_variable.get():
            tkinter.messagebox.showwarning(
                'Configuration', 'Add a folder'
            )
            return

        for folder in self.folder_variable.get():
            if not os.path.isdir(folder):
                tkinter.messagebox.showwarning(
                    'Configuration', 'Invalid folder:\n' + folder
                )
                return

        if not self.folder_variable.get():
            tkinter.messagebox.showwarning(
                'Configuration', 'Add an extension'
            )
            return

        self.configuration['SETTINGS']['port'] = self.port_variable.get()
        self.configuration['SETTINGS']['queue_size'] = self.queue_size_variable.get()
        self.configuration['SETTINGS']['timeout'] = self.timeout_variable.get()
        self.configuration['SETTINGS']['ssl'] = self.ssl_variable.get()
        self.configuration['SETTINGS']['certificate'] = self.certificate_variable.get()
        self.configuration['SETTINGS']['key'] = self.key_variable.get()
        self.configuration['SETTINGS']['folders'] = json.dumps(self.folder_variable.get())
        self.configuration['SETTINGS']['extensions'] = json.dumps(self.extension_variable.get())

        if not self.configuration.has_option('SETTINGS', 'password_hash') or not self.configuration['SETTINGS']['password_hash']:
            tkinter.messagebox.showwarning(
                'Configuration', 'Set a password'
            )
            return

        with open('configuration.ini', 'w') as configuration_file:
            self.configuration.write(configuration_file)

        self.top.destroy()

    @classmethod
    def is_of_type(cls, string_variable, type_to_check):
        try:
            type_to_check(string_variable)
            return True
        except:
            return False

    def update_paths(self, certificate_path, key_path):
        self.certificate_variable.set(certificate_path)
        self.key_variable.set(key_path)
