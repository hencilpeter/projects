import os


class FileUtil:
    @staticmethod
    def read_text_file(file_name):
        with open(file_name, 'r') as file:
            content = file.read()
        return content

    @staticmethod
    def save_file(file_name, data):
        with open(file_name, "w", encoding="UTF-8") as file:
            file.write(data)

    @staticmethod
    def create_folder(folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
