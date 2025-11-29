from collections import defaultdict

from openaisrc.openai_client import OpenAIClient
from util.file_util import FileUtil

from util.test_case_generation_util import TestCaseGenerationUtil

output_folder = "sample_code\\output\\"
if __name__ == '__main__':
    client = OpenAIClient.get_openai_client()
    source_code = FileUtil.read_text_file(file_name="sample_code\\add_two_num.py")

    dict_test_cases = defaultdict(lambda: -1)
    dict_test_cases.update({"unit test cases": "write all unit test cases in python:",
                            "performance test cases": "write the performance tests  for the code in python:",
                            "mock test cases": "write the mock tests for the code in python:",
                            "integration test cases": "write all integration test cases in python:",
                            "edge-case test cases": "write the edge-case test cases in python:",
                            "functional test cases": "write all functional test cases in python:"
                            })
    FileUtil.create_folder(output_folder)
    TestCaseGenerationUtil.generate_test_cases(_dict_test_cases=dict_test_cases, _source_code=source_code,
                                               _openai_client=client, _output_folder=output_folder)
