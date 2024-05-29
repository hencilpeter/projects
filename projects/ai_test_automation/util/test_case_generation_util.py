import os.path

from util.file_util import FileUtil


class TestCaseGenerationUtil:
    @staticmethod
    def generate_test_cases(_dict_test_cases, _source_code, _openai_client, _output_folder):
        for test_case_name in _dict_test_cases.keys():
            response = _openai_client.chat.completions.create(model="gpt-3.5-turbo", messages=[
                {"role": "system", "content": _dict_test_cases[test_case_name] + _source_code}])
            FileUtil.save_file(os.path.join(_output_folder, test_case_name + ".py"),
                               response.choices[0].message.content)
