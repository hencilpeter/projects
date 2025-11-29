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


# import subprocess
# p = subprocess.Popen(["C:\\Users\\User\\Documents\\GitHub\\projects\\TestAutomationUsingAIV2\\testdata\SQLCover\\RunSQLCover.cmd"], cwd="C:\\Users\\User\\Documents\\GitHub\\projects\\TestAutomationUsingAIV2\\testdata\\SQLCover")
# p.wait()

file_data = '''      
Warnings StatementCount CoveredStatementCount HitCount
-------- -------------- --------------------- --------
                      7                     4        4
'''

print(file_data)
file_lines = file_data.split("\n")
print(file_lines)
for line in file_lines:
    line = line.strip()

    if line is "" or "warning" in str(line).lower() or "-" in line or "\\" in line:
        continue

    split_line = line.split(" ")
    split_line = [ item for item in split_line if len(item) > 0]
    print(split_line)