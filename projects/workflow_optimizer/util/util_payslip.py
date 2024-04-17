# importing modules
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
import os
import sys

sys.path.append("/")
# sys.path.append("C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\util")
# sys.path.append("C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\scheduler")

# https://stackoverflow.com/questions/65168838/how-to-do-a-relative-import-when-using-pycharm-run-in-python-console

print(os.getcwd())
print("In module products __package__, __name__ ==", __package__, __name__)

from old_code.util.config_reader_util import ConfigReaderUtil

# initializing variables with values
fileName = 'sample.pdf'
documentTitle = 'sample'
title = 'Technology'
subTitle = 'The largest thing now!!'
textLines = [
    'Technology makes us aware of',
    'the world around us.',
]

import decimal


def num2words(num):
    # #num = float(num)
    # int_part = int(num)
    # float_part = num - int_part
    # decimal_part = round(num - int(num),2)
    num = decimal.Decimal(num)
    decimal_part = round(num - int(num),2)
    num = int(num)

    if decimal_part:
        # return num2words(num) + " point " + (" ".join(num2words(i) for i in str(decimal_part)[2:]))
        return "Rupees " + num2words(num) + " And " + (num2words(str(decimal_part)[2:])) + " paisa only"

    under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven',
                'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    above_100 = {100: 'Hundred', 1000: 'Thousand', 100000: 'Lakhs', 10000000: 'Crores'}

    if num < 20:
        return under_20[num]

    if num < 100:
        return tens[num // 10 - 2] + ('' if num % 10 == 0 else ' ' + under_20[num % 10])

    # find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
    pivot = max([key for key in above_100.keys() if key <= num])

    return num2words(num // pivot) + ' ' + above_100[pivot] + ('' if num % pivot == 0 else ' ' + num2words(num % pivot))


def add_line_in_pdf(_column, _row, _content, _row_decrement_value=None, _font_name=None, _font_size=None):
    if _font_name is not None and _font_size is not None:
        pdf.setFont(_font_name, _font_size)

    if _row_decrement_value is not None:
        _row = _row - _row_decrement_value

    pdf.drawString(_column, _row, _content)

    return _row


dict_earnings = {
    'Week1-Salary': ["Dates: 2024-06-01, 2024-06-02. Worked days - 2", 900.4567],
    'Week2-Salary': ["Dates: 2024-06-01, 2024-06-02, 2024-06-03, 2024-06-04, 2024-06-05. Worked days - 5", 2500.2],
    'Incentives': ["", 1000],
    'Bonus': ["", 8000]}

dict_deductions = {'Salary Advance': ["", 800.0],
                   'PF Contributions': ["", 90]}

image = "C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\scheduler\\lion.jpeg"

# creating a pdf object
pdf = canvas.Canvas(fileName)

# setting the title of the document
# pdf.setTitle(documentTitle)

ConfigReaderUtil.load_configuration(
    "/old_code/data\\payslip_config.json")
company_name = ConfigReaderUtil.get_config("company_name")
company_address = ConfigReaderUtil.get_config("company_address")
payslip_month = "June 2024"
print(str(ConfigReaderUtil.get_config("payslip_title")).format(payslip_month))
print(company_name)
print(company_address)

pdfmetrics.registerFont(TTFont('TNR', 'times.ttf'))
pdfmetrics.registerFont(TTFont('TNRB', 'timesbd.ttf'))
pdfmetrics.registerFont(TTFont('couri', 'couri.ttf'))
pdfmetrics.registerFont(TTFont('Times_new-Italic', 'timesi.ttf', subfontIndex=2))

pdf.setFillColorRGB(0, 0, 255)
pdf.setFont("Courier-Bold", 14)

# add company name and address
pdf.drawString(35, 780, company_name)
current_line_row_line = 760
# current_line_row_line = 760
pdf.setFillColorRGB(0, 0, 0)
pdf.setFont("Courier", 9)
for address_line in company_address:
    pdf.drawString(35, current_line_row_line, address_line)
    current_line_row_line -= 13

# company phone number and email address
pdf.drawString(35, current_line_row_line, ConfigReaderUtil.get_config("phone_number"))
current_line_row_line -= 9
pdf.drawString(35, current_line_row_line, ConfigReaderUtil.get_config("company_email_id"))
current_line_row_line -= 9
pdf.drawString(35, current_line_row_line, ConfigReaderUtil.get_config("company_website"))

# right side payslip - header
pdf.setFillColorRGB(0, 0, 0)
pdf.setFont("Courier-Bold", 14)
pdf.drawString(390, 780, "Pay Advice")

pdf.setFont("Times-Italic", 9)
pdf.drawString(370, 770, str(ConfigReaderUtil.get_config("payslip_title")).format(payslip_month))

emp_details = ConfigReaderUtil.get_config("employee_detail")
emp_name = "S. Joseph"
emp_id = "MF101"
emp_date_of_joining = "01-April-2024"
emp_department = "Administration"
ConfigReaderUtil.get_config("employee_detail")["emp_id"]

pdf.setFont("Courier", 9)
current_line_row_line -= 15
pdf.drawString(35, current_line_row_line,
               str(ConfigReaderUtil.get_config("employee_detail")["emp_name"]).format(emp_name))
current_line_row_line -= 11
pdf.drawString(35, current_line_row_line, str(ConfigReaderUtil.get_config("employee_detail")["emp_id"]).format(emp_id))
current_line_row_line -= 11
pdf.drawString(35, current_line_row_line,
               str(ConfigReaderUtil.get_config("employee_detail")["date_of_joining"]).format(emp_date_of_joining))
current_line_row_line -= 11
pdf.drawString(35, current_line_row_line,
               str(ConfigReaderUtil.get_config("employee_detail")["department"]).format(emp_department))

# drawing a line
current_line_row_line -= 5
pdf.setFont("Courier-Bold", 14)
pdf.line(30, current_line_row_line, 550, current_line_row_line)

# Earnings
current_line_row_line -= 20
pdf.setFont("Courier-Bold", 14)
pdf.drawString(35, current_line_row_line, "EARNINGS")
pdf.setFont("Courier-Bold", 10)
item_number = 0
total_earnings = 0
for earning_name in dict_earnings.keys():
    current_line_row_line -= 13
    item_number += 1
    pdf.drawString(45, current_line_row_line, "{}.{}".format(item_number, earning_name))
    temp_value = "{:.2f}".format(round(dict_earnings[earning_name][1], 2)).rjust(10, ' ')
    pdf.drawString(450, current_line_row_line, "{}".format(temp_value))
    total_earnings += dict_earnings[earning_name][1]

total_earnings_rounded = round(total_earnings, 2)

add_line_in_pdf(50, current_line_row_line,
                "( Total Earning - Rs {} )".format("{:.2f}".format(total_earnings_rounded).rjust(10, ' ')),
                _row_decrement_value=13)

current_line_row_line -= 20
pdf.line(30, current_line_row_line, 550, current_line_row_line)

# Deductions
current_line_row_line -= 20
pdf.drawString(35, current_line_row_line, "DEDUCTIONS")
item_number = 0
total_deductions = 0

for deduction_name in dict_deductions.keys():
    item_number += 1
    current_line_row_line = add_line_in_pdf(45, current_line_row_line, "{}.{}".format(item_number, deduction_name),
                                            _row_decrement_value=13)
    temp_value = "{:.2f}".format(round(dict_deductions[deduction_name][1], 2)).rjust(10, ' ')
    current_line_row_line = add_line_in_pdf(450, current_line_row_line, "{}".format(temp_value))

    total_deductions += dict_deductions[deduction_name][1]

total_deductions_rounded = round(total_deductions, 2)

current_line_row_line = add_line_in_pdf(50, current_line_row_line, "( Total Deductions - Rs {} )".format(
    "{:.2f}".format(total_deductions_rounded).rjust(10, ' ')), _row_decrement_value=13)

current_line_row_line -= 20
pdf.line(30, current_line_row_line, 550, current_line_row_line)

current_line_row_line -= 15
net_pay = total_earnings_rounded - total_deductions_rounded


add_line_in_pdf(50, current_line_row_line,
                "Net Pay ( Rs. {} - Rs. {} )  : Rs.{} ".format(total_earnings_rounded, total_deductions_rounded,
                                                               net_pay),
                _row_decrement_value=13)

amount_in_words = num2words(net_pay)
current_line_row_line = add_line_in_pdf(50, current_line_row_line, "Amount in Words  :",
                                        _row_decrement_value=30)

# current_line_row_line = add_line_in_pdf(110, current_line_row_line, "{}".format(amount_in_words),
#                                         _row_decrement_value=10, _font_name="Courier-Bold", _font_size=8)

current_line_row_line -= 20
text = pdf.beginText(110, current_line_row_line)
text.setFont("Courier", 12)
text.setFillColor(colors.black)
len_text = len(amount_in_words)
net_pay_words = amount_in_words.split(" ")
line_max_length = 60
current_line_text = ''
for word in net_pay_words:
    if len(current_line_text) >= line_max_length:
        text.textLine(current_line_text)
        current_line_text = ''
    current_line_text += word + ' '
text.textLine(current_line_text)
pdf.drawText(text)

current_line_row_line -= 70
#pdf.line(30, current_line_row_line, 550, current_line_row_line)
pdf.setFont("Courier-Bold", 24)
pdf.drawCentredString(300, current_line_row_line, "**********")



















# creating the title by setting it's font
# and putting it on the canvas
pdf.setFont('Courier', 36)
# pdf.drawCentredString(300, 770, title)

# creating the subtitle by setting it's font,
# colour and putting it on the canvas
pdf.setFillColorRGB(0, 0, 255)
pdf.setFont("Courier-Bold", 24)
# pdf.drawCentredString(290, 720, subTitle)

# drawing a line
# pdf.line(30, 710, 550, 710)

# creating a multiline text using
# textline and for loop
text = pdf.beginText(40, 680)
text.setFont("Courier", 18)
text.setFillColor(colors.red)

for line in textLines:
    text.textLine(line)
# pdf.drawText(text)

# drawing a image at the
# specified (x.y) position
# pdf.drawInlineImage(image, 130, 400)

# saving the pdf
pdf.save()
