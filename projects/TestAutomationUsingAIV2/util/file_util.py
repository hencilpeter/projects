import os
from distutils.dir_util import copy_tree

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

    @staticmethod
    def get_filename(filename_fullpath):
        if len(filename_fullpath) == 0:
            return ""

        reverse_filename = str(filename_fullpath[::-1]).split("\\")[0]
        return reverse_filename[::-1]

    @staticmethod
    def copy_folder(source_directory, target_directory):
        if not os.path.exists(source_directory):
            raise Exception("source folder does not exist.")

        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        copy_tree(source_directory, target_directory)

