import socket
import ssl
import json
from threading import Thread

import file_manager

class ServerThread(Thread):
    def __init__(self, main, configuration_menu, logger_function):
        Thread.__init__(self)
        self.main = main
        self.configuration_menu = configuration_menu
        self.logger_function = logger_function
        self.socket = socket.socket()
        if configuration_menu.get_parameter('ssl') == 'On':
            self.socket = ssl.wrap_socket(self.socket,
                                          keyfile=configuration_menu.get_parameter('key'),
                                          certfile=configuration_menu.get_parameter('certificate'),
                                          server_side=True)
        self.socket.settimeout(float(configuration_menu.get_parameter('timeout')))
        host = ''
        port = int(configuration_menu.get_parameter('port'))
        self.socket.bind((host, port))
        self.socket.listen(int(configuration_menu.get_parameter('queue_size')))

    def run(self):
        self.logger_function('Server started')
        while self.main.server_running:
            try:
                connection, address = self.socket.accept()
            except:
                continue

            self.logger_function('Received connection from ' + str(address))
            connection.settimeout(1)
            data = connection.recv(65535)
            configuration_password_hash = self.configuration_menu.get_parameter('password_hash')

            if data.startswith(b'GET_MEME'):
                self.logger_function('Meme was requested')
                password_hash, offset = ServerThread.parse_length_value_string(data,
                                                                               len('GET_MEME'))
                if not password_hash == configuration_password_hash.encode():
                    connection.send(b'WRONG_PASSWORD')
                    self.logger_function('Wrong password')
                else:
                    file_mngr = file_manager.FileManager()
                    folder_list = json.loads(self.configuration_menu.get_parameter('folders'))
                    extension_list = json.loads(self.configuration_menu.get_parameter('extensions'))
                    try:
                        file_mngr.open_random_file(folder_list, extension_list)
                        path = file_mngr.get_file_path().encode()
                        path_length = len(path)
                        connection.send(path_length.to_bytes(2, 'big') + path)
                        data = file_mngr.read()
                        while data:
                            connection.send(data)
                            data = file_mngr.read()
                        file_mngr.close_file()
                        self.logger_function('Sent meme')
                    except:
                        self.logger_function('Didn\'t find any memes to send')
            elif data.startswith(b'MOVE_FILE'):
                self.logger_function('File moving was requested')
                password_hash, offset = ServerThread.parse_length_value_string(data,
                                                                               len('MOVE_FILE'))
                if not password_hash == configuration_password_hash.encode():
                    connection.send('WRONG_PASSWORD')
                    self.logger_function('Wrong password')
                else:
                    source, offset = ServerThread.parse_length_value_string(data, offset)
                    destination, offset = ServerThread.parse_length_value_string(data, offset)
                    new_path = file_manager.FileManager.move_file(source.decode("utf-8"),
                                                                  destination.decode("utf-8"))
                    if new_path:
                        connection.send(new_path.encode())
                        self.logger_function('Moved successfully')
                    else:
                        connection.send(b'NOK')
                        self.logger_function('Moving failed')
            connection.close()
        self.socket.close()
        self.logger_function('Server stopped')

    @classmethod
    def parse_length_value_string(cls, data, offset):
        data = data[offset:]
        length = data[0] * 256 + data[1]
        return data[2:length+2], offset + length + 2
