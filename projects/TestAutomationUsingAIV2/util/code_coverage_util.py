from config.config_manager import ConfigurationManager
import os
from util.file_util import FileUtil
import subprocess
from pathlib import Path


class CodeCoverageUtil:
    @staticmethod
    def generate_code_coverage_data(database_name):
        build_base_path = ConfigurationManager.get_common_config("build_path")
        test_code_base_path = ConfigurationManager.get_common_config("test_code_base_path")
        source_directory = os.path.join(build_base_path, "SQLCover")
        target_directory = os.path.join(test_code_base_path, "SQLCover")
        FileUtil.copy_folder(source_directory=source_directory, target_directory=target_directory)
        CodeCoverageUtil.update_database_name(database_name=database_name,
                                              filename=os.path.join(target_directory, "RunSQLCover.ps1"))
        batch_command = os.path.join(target_directory, "RunSQLCover.cmd")
        CodeCoverageUtil.execute_sql_coverage(batch_file_name=batch_command)

    @staticmethod
    def update_database_name(database_name, filename):
        filedata = FileUtil.read_text_file(file_name=filename)
        filedata = filedata.format(database_name, database_name)
        FileUtil.save_file(file_name=filename, data=filedata)

    @staticmethod
    def execute_sql_coverage(batch_file_name):
        path = Path(batch_file_name)
        p = subprocess.Popen([batch_file_name], cwd=path.parent.absolute())
        p.wait()
