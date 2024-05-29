import shutil

import pyodbc

from config.config_manager import ConfigurationManager
from sqlsrc.sql_dictionary_maker import SqlDictionaryMaker
import os
from util.file_util import FileUtil

class SqlManager:
    def __init__(self):
        self.dbuser = ConfigurationManager.get_sql_server_config("user")
        self.host_name = ConfigurationManager.get_sql_server_config("host_name")
        self.port = ConfigurationManager.get_sql_server_config("port")
        self.database = ConfigurationManager.get_sql_server_config("database")
        self.schema = ConfigurationManager.get_sql_server_config("schema")
        self.password = ConfigurationManager.get_sql_server_config("password")
        self.connection = self.get_connection()
        self.cursor = self.connection.cursor()

    def get_connection(self, database_name="master"):
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.host_name};DATABASE={database_name};UID={self.dbuser};PWD={self.password}'
        conn = pyodbc.connect(connection_string)
        return conn

    def create_database(self, database_name):
        sql_command = "CREATE DATABASE {}".format(database_name)
        self.connection.autocommit = True
        self.connection.execute(sql_command)

    def deploy_tsqlt(self, database_name):
        base_path = ConfigurationManager.get_common_config("test_code_base_path")
        full_path = os.path.join(base_path, "prerequisites")
        for (root, dirs, filenames) in os.walk(full_path):
            for filename in filenames:
                filename_with_path = os.path.join(root, filename)
                file_data = FileUtil.read_text_file(file_name=filename_with_path)
                self.execute_file_content(database_name=database_name, file_data=file_data)

    def execute_file_content(self, database_name, file_data):
        if len(file_data) == 0:
            return

        content_list = file_data.split("GO")

        for content in content_list:
            content = self.remove_comments(script=content)
            content = content.strip()
            if len(content) > 0:
                self.execute_script(database_name=database_name, script=content)

    def clean_sql_file_contents(self):
        base_path = ConfigurationManager.get_common_config("test_code_base_path")
        full_path = os.path.join(base_path, "test_case_files")
        clean_testcase_path =  os.path.join(base_path, "cleaned_test_case_files")
        if os.path.exists(clean_testcase_path):
            shutil.rmtree(clean_testcase_path)

        os.mkdir(clean_testcase_path)

        for (root, dirs, filenames) in os.walk(full_path):
            for filename in filenames:
                filename_with_path = os.path.join(root, filename)
                file_data = FileUtil.read_text_file(file_name=filename_with_path)
                is_comment_exist = True
                while is_comment_exist:
                    start_comment_loc = file_data.find("```sql")
                    end_comment_loc = file_data.find("```", start_comment_loc+6)
                    if 0 < start_comment_loc < end_comment_loc:
                        file_data = file_data[start_comment_loc+6: end_comment_loc]
                    else:
                        is_comment_exist = False

                new_file_path = os.path.join(clean_testcase_path, filename)
                FileUtil.save_file(file_name=new_file_path, data=file_data)




    def remove_comments(self, script):
        is_comment_exist = True
        while is_comment_exist:
            start_comment_loc = script.find("/*")
            end_comment_loc = script.find("*/")
            if 0 < start_comment_loc < end_comment_loc:
                script = script.replace(script[start_comment_loc: end_comment_loc + 2], '')
            else:
                is_comment_exist = False

        return script

    def deploy_sql_dictionary_scripts(self, database_name, dict_sql_script):
        dict_processing_order = ConfigurationManager.get_processing_order()
        for order in dict_processing_order.keys():
            dict_script = dict_sql_script[dict_processing_order[order]]
            for filename_key in dict_script.keys():
                sql_script = dict_script[filename_key]
                self.execute_script(database_name=database_name, script=sql_script)

    def execute_testcases(self, database_name):
        base_path = ConfigurationManager.get_common_config("test_code_base_path")
        full_path = os.path.join(base_path, "cleaned_test_case_files")
        for (root, dirs, filenames) in os.walk(full_path):
            for filename in filenames:
                filename_with_path = os.path.join(root, filename)
                file_data = FileUtil.read_text_file(file_name=filename_with_path)
                self.execute_file_content(database_name=database_name, file_data=file_data)

    def execute_script(self, database_name, script):
        connection = self.get_connection(database_name=database_name)
        connection.autocommit = True
        connection.setdecoding(pyodbc.SQL_CHAR, encoding='latin1')
        connection.setencoding('latin1')
        connection.cursor().execute(script)


