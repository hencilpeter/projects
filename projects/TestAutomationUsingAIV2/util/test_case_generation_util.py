import os.path

from util.file_util import FileUtil

from config.config_manager import ConfigurationManager
from collections import defaultdict


class TestCaseGenerationUtil:
    @staticmethod
    def generate_test_cases(_dict_test_cases, _dict_sql_script, _openai_client):
        dict_processing_order = ConfigurationManager.get_processing_order()
        dict_test_cases_scripts = defaultdict(lambda: -1)
        dict_test_cases_scripts["table"] = defaultdict(lambda: -1)
        dict_test_cases_scripts["stored_procedure"] = defaultdict(lambda: -1)

        for test_case_name in _dict_test_cases.keys():
            for order in dict_processing_order.keys():
                if "table" in dict_processing_order[order] or "stored_procedure" in dict_processing_order[order]:
                    dict_sql = _dict_sql_script[dict_processing_order[order]]
                    for filename_key in dict_sql.keys():
                        response = _openai_client.chat.completions.create(model="gpt-3.5-turbo", messages=[
                            {"role": "system", "content": _dict_test_cases[test_case_name] + dict_sql[filename_key]}])
                        dict_test_cases_scripts[dict_processing_order[order]][filename_key] = response.choices[
                            0].message.content

        return dict_test_cases_scripts
