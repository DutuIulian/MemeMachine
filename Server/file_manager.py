from pathlib import Path
import random
import os
import shutil
import ntpath

class FileManager:
    def __init__(self):
        self.file = None

    def open_random_file(self, folders, extensions):
        self.file = open(FileManager.get_random_file(folders, extensions), 'rb')
        if not self.file:
            raise Exception()

    def get_file_path(self):
        return str(self.file.name)

    def read(self):
        return self.file.read(65535)

    @classmethod
    def get_random_file(cls, folders, extensions):
        file_list = []
        for folder in folders:
            for extension in extensions:
                file_list.extend(list(Path(folder).rglob('*.' + extension)))
        file_list = list(dict.fromkeys(file_list))

        if not file_list:
            return None

        while True:
            rand = random.randint(0, len(file_list) - 1)
            if os.path.isfile(file_list[rand]):
                return file_list[rand]

    def close_file(self):
        self.file.close()

    @classmethod
    def move_file(cls, source, destination):
        try:
            Path(destination).mkdir(parents=True, exist_ok=True)
            shutil.move(source, destination)
            file_name = ntpath.basename(Path(source))
            return os.path.join(os.path.abspath(destination), file_name)
        except:
            return None
