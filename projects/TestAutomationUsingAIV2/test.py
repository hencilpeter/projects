test_script = """
/*
commented data1
*/
test data
/*
commented data2
*/
"""

# is_comment_exist = True
# while is_comment_exist:
#     start_comment_loc = test_script.find("/*")
#     end_comment_loc = test_script.find("*/")
#     if 0 < start_comment_loc < end_comment_loc:
#         commented_data = test_script[start_comment_loc: end_comment_loc + 2]
#         test_script = test_script.replace(test_script[start_comment_loc: end_comment_loc + 2], '')
#     else:
#         is_comment_exist = False
#
# print(test_script)



import subprocess
p = subprocess.Popen(["C:\\Users\\User\\Documents\\GitHub\\projects\\TestAutomationUsingAIV2\\testdata\SQLCover\\RunSQLCover.cmd"], cwd="C:\\Users\\User\\Documents\\GitHub\\projects\\TestAutomationUsingAIV2\\testdata\\SQLCover")
p.wait()