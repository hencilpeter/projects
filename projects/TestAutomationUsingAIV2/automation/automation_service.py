from config.config_manager import ConfigurationManager
from util.common_util import CommonUtil
from sqlsrc.sql_manager import SqlManager
from sqlsrc.sql_dictionary_maker import SqlDictionaryMaker
from util.test_case_generation_util import TestCaseGenerationUtil
from collections import defaultdict
from openaisrc.openai_client import OpenAIClient
import os
from util.code_coverage_util import CodeCoverageUtil
from util.file_util import FileUtil
class AutomationService:
    def __init__(self, config_file):
        # load the configuration
        ConfigurationManager.load_configuration(config_file=config_file)
        self.sql_manager = SqlManager()
        self.openai_client = OpenAIClient.get_openai_client()

    def test_sql_scripts(self):
        db_name = CommonUtil.get_unique_database_name()
        print("db name : {}".format(db_name))

        # 1. get the sql dictionary
        sql_dictionary = SqlDictionaryMaker.get_sql_dictionary()
        print("1. sql dictionary constructed...")

        # 2. save the sql dictionary
        base_path = ConfigurationManager.get_common_config("test_code_base_path")
        result_folder = os.path.join(base_path, "extracted_scripts")
        SqlDictionaryMaker.save_dict_files(dict_sql_script=sql_dictionary, result_folder=result_folder)
        print("2. sql dictionary saved...")

        # 3. create test cases from sql dictionary
        dict_test_cases = defaultdict(lambda: -1)
        dict_test_cases.update({"unit_test_cases": "generate unit test for the given sql script using tsqlt framework"
                                })
        dict_test_case_scripts = TestCaseGenerationUtil.generate_test_cases(_dict_test_cases=dict_test_cases, _dict_sql_script = sql_dictionary,
                                                   _openai_client = self.openai_client)

        result_folder = os.path.join(base_path, "test_case_files")
        SqlDictionaryMaker.save_dict_files(dict_sql_script=dict_test_case_scripts, result_folder=result_folder)
        print("3. test cases have been generated via open ai...")

        # 4. clean the scripts for execution
        self.sql_manager.clean_sql_file_contents()
        print("4. test case files are cleaned for execution...")

        # 5. create test database (unique)
        self.sql_manager.create_database(database_name=db_name)
        print("5. test data base {} has been created...".format(db_name))

        # 6. enable clr and trustworthy, and deploy tsqlt
        self.sql_manager.deploy_tsqlt(database_name=db_name)
        print("6.  enabled clr and trustworthy...")

        # 7. deploy the sql scripts
        self.sql_manager.deploy_sql_dictionary_scripts(database_name=db_name, dict_sql_script=sql_dictionary)
        print("7. SQL scripts have been deployed...")

        # 8. execute the test cases
        self.sql_manager.execute_testcases(database_name=db_name)
        print("8. test cases are executed successfully..")

        # 9. Code Coverage (using SQL Cover)
        CodeCoverageUtil.generate_code_coverage_data(database_name=db_name)
        print("9. Code Coverage(SQL Cover) request triggered..")

        # 10. coverage result - recon step
        test_code_base_path = ConfigurationManager.get_common_config("test_code_base_path")
        code_coverage_result_file = os.path.join(test_code_base_path, "SQLCover", "code_coverage_result.txt")
        dict_code_coverage = FileUtil.get_code_coverage_dictionary(filename=code_coverage_result_file)
        print("10. Last executed test cases' code coverage details: ")
        print("Statement Count - {} , Covered Statement Count - {}, Code Coverage : {} %"
              .format(dict_code_coverage["StatementCount"], dict_code_coverage["CoveredStatementCount"],
                      (int(dict_code_coverage["CoveredStatementCount"])/int(dict_code_coverage["StatementCount"])) * 100 ))



