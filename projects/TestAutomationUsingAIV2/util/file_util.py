import os
from distutils.dir_util import copy_tree
from collections import defaultdict


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

    @staticmethod
    def get_code_coverage_dictionary(filename):
        file_data = FileUtil.read_text_file(file_name=filename)

        file_lines = file_data.split("\n")
        print(file_lines)
        for line in file_lines:
            line = line.strip()

            if line == "" or "warning" in str(line).lower() or "-" in line or "\\" in line:
                continue

            split_line = line.split(" ")
            split_line = [item for item in split_line if len(item) > 0]
            break

        dict_code_coverage = defaultdict(lambda: -1)
        dict_code_coverage["StatementCount"] = split_line[0]
        dict_code_coverage["CoveredStatementCount"] = split_line[1]
        dict_code_coverage["HitCount"] = split_line[2]

        return dict_code_coverage
