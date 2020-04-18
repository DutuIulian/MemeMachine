import sys
import tkinter
import tkinter.messagebox
import tkinter.ttk
import tkinter.scrolledtext
from threading import Semaphore

import server_thread
import configuration_menu

class Main:

    def __init__(self):
        self.server_running = False
        self.server_thr = None
        self.new_log_list = []
        self.new_log_list_semaphore = Semaphore(1)
        self.job = None
        self.configuration_menu = None
        self.status_label = None
        self.logger_text = None

    def main(self):
        self.window = tkinter.Tk()
        self.window.title('Meme Machine')
        self.window.geometry('610x400')
        self.window.resizable(False, False)
        self.window.protocol('WM_DELETE_WINDOW', self.exit_server)

        frame = tkinter.Frame(self.window)
        self.configuration_menu = configuration_menu.ConfigurationMenu(frame)

        self.status_label = tkinter.Label(frame, text='Status: stopped', font=('Arial', 11))
        self.status_label.grid(columnspan=4, row=0, pady=15)

        start_button = tkinter.Button(frame, text='Start', command=self.start_server, width=10)
        start_button.grid(column=0, row=1, padx=2, pady=2)

        stop_button = tkinter.Button(frame, text='Stop', command=self.stop_server, width=10)
        stop_button.grid(column=1, row=1, padx=2, pady=2)

        configure_button = tkinter.Button(frame, text='Configure',
                                          command=self.configure_server, width=10)
        configure_button.grid(column=2, row=1, padx=2, pady=2)

        exit_button = tkinter.Button(frame, text='Exit', command=self.exit_server, width=10)
        exit_button.grid(column=3, row=1, padx=2, pady=2)
        frame.pack(expand=1, fill='y', pady=(20, 5))

        logger_frame = tkinter.Frame(self.window)
        self.logger_text = tkinter.scrolledtext.ScrolledText(logger_frame, height=15, width=70)
        self.logger_text.config(state=tkinter.DISABLED)
        self.logger_text.grid(columnspan=2, row=2, padx=2, pady=2)
        logger_frame.pack(expand=1, fill='y', pady=15)

        self.job = self.window.after(33, self.check_for_logs)
        self.window.mainloop()

    def start_server(self):
        if not self.server_running:
            if self.configuration_menu.are_settings_valid():
                try:
                    self.server_thr = server_thread.ServerThread(
                        self, self.configuration_menu, self.add_to_log)
                    self.server_running = True
                    self.server_thr.start()
                    self.status_label.config(text='Status: running')
                except:
                    tkinter.messagebox.showwarning(
                        'Server',
                        'Could not start server'
                    )
            else:
                tkinter.messagebox.showwarning(
                    'Configuration',
                    'The configuration is invalid. Please change it.'
                )

    def stop_server(self):
        if self.server_running:
            self.server_running = False
            self.status_label.config(text='Status: stopped')
            if self.server_thr:
                self.server_thr.join()

    def configure_server(self):
        if not self.server_running:
            self.configuration_menu.show()
        else:
            tkinter.messagebox.showwarning(
                'Server status',
                'The server is running. Stop it first.'
            )

    def exit_server(self):
        self.stop_server()
        if self.job:
            self.window.after_cancel(self.job)
            self.job = None
        sys.exit(0)

    def check_for_logs(self):
        self.new_log_list_semaphore.acquire()
        self.logger_text.config(state=tkinter.NORMAL)
        for message in self.new_log_list:
            self.logger_text.insert(tkinter.END, str(message) + '\n')
        self.logger_text.config(state=tkinter.DISABLED)
        if self.new_log_list:
            self.logger_text.see(tkinter.END)
            self.new_log_list.clear()
        self.new_log_list_semaphore.release()
        self.job = self.window.after(33, self.check_for_logs)

    def add_to_log(self, message):
        self.new_log_list_semaphore.acquire()
        self.new_log_list.append(message)
        self.new_log_list_semaphore.release()

if __name__ == '__main__':
    Main().main()
