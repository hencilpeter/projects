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

# print(file_data)
# file_lines = file_data.split("\n")
# print(file_lines)
# for line in file_lines:
#     line = line.strip()
#
#     if line is "" or "warning" in str(line).lower() or "-" in line or "\\" in line:
#         continue
#
#     split_line = line.split(" ")
#     split_line = [ item for item in split_line if len(item) > 0]
#     print(split_line)
#
#
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(value, decimals=0):
    value = Decimal(str(value))
    rounding_format = '1.' + '0' * decimals
    return value.quantize(Decimal(rounding_format), rounding=ROUND_HALF_UP)

def round2(value):
    return Decimal(str(value)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)


taxable_value = Decimal(str(100))
cgst = Decimal(str(2.6))
sgst = Decimal(str(2.6))
igst = Decimal(str(2))

total_before_round = taxable_value + cgst + sgst + igst
# 4️⃣ Round Off
rounded_total =  round_half_up(total_before_round)
round_off = rounded_total - total_before_round

print(f"taxable_value : {taxable_value}")
print(f"cgst : {cgst}")
print(f"sgst : {sgst}")
print(f"total_before_round : {total_before_round}")
print(f"rounded_total : {rounded_total}")
print(f"round_off : {round_off}")

print(f"10.3 ==> {round_half_up(10.3)}")
print(f"10.4 ==> {round_half_up(10.4)}")
print(f"10.49 ==> {round_half_up(10.49)}")
print(f"10.5 ==> {round_half_up(10.5)}")
print(f"10.51 ==> {round_half_up(10.51)}")
print(f"10.7 ==> {round_half_up(10.7)}")
print(f"10.90 ==> {round_half_up(10.90)}")
print(f"10.99 ==> {round_half_up(10.99)}")
print("------------------------")
print(f"10.3 ==> {round_half_up(10.3).quantize(Decimal('0.00'))}")
print(f"10.4 ==>  {round_half_up(10.4).quantize(Decimal('0.00'))}")
print(f"10.49 ==> {round_half_up(10.49).quantize(Decimal('0.00'))}")
print(f"10.5 ==>  {round_half_up(10.5).quantize(Decimal('0.00'))}")
print(f"10.51 ==> {round_half_up(10.51).quantize(Decimal('0.00'))}")
print(f"10.7 ==>  {round_half_up(10.7).quantize(Decimal('0.00'))}")
print(f"10.90 ==> {round_half_up(10.90).quantize(Decimal('0.00'))}")
print(f"10.99 ==> {round_half_up(10.99).quantize(Decimal('0.00'))}")