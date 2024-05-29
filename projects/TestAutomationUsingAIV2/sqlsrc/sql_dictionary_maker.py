from config.config_manager import ConfigurationManager
import os
from collections import defaultdict
from util.file_util import FileUtil
from datetime import datetime
import shutil

class SqlDictionaryMaker:

    @staticmethod
    def get_sql_dictionary():
        base_path = ConfigurationManager.get_common_config("test_code_base_path")
        folder_name = ConfigurationManager.get_common_config("test_code_folder")
        full_path = os.path.join(base_path, folder_name)
        dict_sql_script = defaultdict(lambda: -1)

        dict_sql_script["schema"] = defaultdict(lambda: -1)
        dict_sql_script["table"] = defaultdict(lambda: -1)
        dict_sql_script["stored_procedure"] = defaultdict(lambda: -1)

        for (root, dirs, filenames) in os.walk(full_path):
            for filename in filenames:
                filename_with_path = os.path.join(full_path, filename)
                SqlDictionaryMaker.process_sql_script(dict_sql_script=dict_sql_script, script_path=filename_with_path)

        return dict_sql_script

    @staticmethod
    def process_sql_script(dict_sql_script, script_path):
        file_data = FileUtil.read_text_file(file_name=script_path)
        content_list = file_data.split("GO")
        filename = FileUtil.get_filename(filename_fullpath=script_path)
        counter = 1
        for script_content in content_list:
            temp_filename = filename.split(".")[0] + "_" + str(datetime.now().strftime("%Y%m%d%H%M%S")) \
                            + "_" + str(counter) + "." + filename.split(".")[1]
            if "CREATE SCHEMA" in script_content:
                dict_sql_script["schema"][temp_filename] = script_content
                counter += 1
            elif "CREATE TABLE" in script_content:
                dict_sql_script["table"][temp_filename] = script_content
                counter += 1
            elif "CREATE PROCEDURE" in script_content:
                dict_sql_script["stored_procedure"][temp_filename] = script_content
                counter += 1

    @staticmethod
    def save_dict_files(dict_sql_script, result_folder):

        if os.path.exists(result_folder):
            shutil.rmtree(result_folder, ignore_errors=True)

        os.makedirs(result_folder)

        for dictionary_group_name in dict_sql_script:
            dict_group = dict_sql_script[dictionary_group_name]
            for key in dict_group.keys():
                FileUtil.save_file(os.path.join(result_folder, key), dict_group[key])
