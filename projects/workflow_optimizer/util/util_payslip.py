# importing modules
import json

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
import os
import sys
import decimal
from util.util_config_reader import UtilConfigReader
from util.util_common import UtilCommon
from data_models.common_model import CommonModel
from util.util_common import UtilCommon
from collections import defaultdict
# initializing variables with values
# fileName = 'sample.pdf'
# documentTitle = 'sample'
# title = 'Technology'
# subTitle = 'The largest thing now!!'
# textLines = [
#     'Technology makes us aware of',
#     'the world around us.',
# ]

class UtilPayslip:

    salary_data_dict = defaultdict(lambda :-1)

    @staticmethod
    def load_all_salary_data(_sql_connection, _salary_month):
        salary_data_cursor = _sql_connection.get_table_data("select * from employee_salary_data where salary_month='{}';".format(_salary_month))
        salary_data_as_list = CommonModel.get_table_data_as_list(_data_cursor=salary_data_cursor)
        UtilPayslip.salary_data_dict = UtilCommon.get_dict_from_list(_list=salary_data_as_list, _dict_key="employee_number")



    @staticmethod
    def num2words(num):
        # #num = float(num)
        # int_part = int(num)
        # float_part = num - int_part
        # decimal_part = round(num - int(num),2)
        num = decimal.Decimal(num)
        decimal_part = round(num - int(num), 2)
        num = int(num)

        if decimal_part:
            # return num2words(num) + " point " + (" ".join(num2words(i) for i in str(decimal_part)[2:]))
            return "Rupees " + UtilPayslip.num2words(num) + " And " + (UtilPayslip.num2words(str(decimal_part)[2:])) + " paisa only"

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

        return UtilPayslip.num2words(num // pivot) + ' ' + above_100[pivot] + (
            '' if num % pivot == 0 else ' ' + UtilPayslip.num2words(num % pivot))

    @staticmethod
    def add_line_in_pdf(_pdf_object, _column, _row, _content, _row_decrement_value=None, _font_name=None, _font_size=None):
        if _font_name is not None and _font_size is not None:
            _pdf_object.setFont(_font_name, _font_size)

        if _row_decrement_value is not None:
            _row = _row - _row_decrement_value

        _pdf_object.drawString(_column, _row, _content)

        return _row


    @staticmethod
    def generate_payslip(_salary_dict, _sql_connection, _salary_month):
        if len(_salary_dict.keys()) == 0:
            return

        # load all salary data
        UtilPayslip.load_all_salary_data(_sql_connection=_sql_connection, _salary_month=_salary_month)

        for employee_number in _salary_dict:
            # salary_entry = json.loads(_salary_dict[employee_number])
            salary_entry = _salary_dict[employee_number]
            # print(employee_number)
            # print(salary_entry)
            payslip_file_name = UtilPayslip.get_pdf_filename(_employee_number = employee_number,
                                                             _salary_entry_dict=salary_entry)

            # creating a pdf object
            pdf_object = canvas.Canvas(payslip_file_name)
            company_name = UtilConfigReader.get_payslip_config("company_name")
            company_address = UtilConfigReader.get_payslip_config("company_address")
            payslip_month = "June 2024"

            pdfmetrics.registerFont(TTFont('TNR', 'times.ttf'))
            pdfmetrics.registerFont(TTFont('TNRB', 'timesbd.ttf'))
            pdfmetrics.registerFont(TTFont('couri', 'couri.ttf'))
            pdfmetrics.registerFont(TTFont('Times_new-Italic', 'timesi.ttf', subfontIndex=2))

            pdf_object.setFillColorRGB(0, 0, 255)
            pdf_object.setFont("Courier-Bold", 14)

            # add company name and address
            pdf_object.drawString(35, 780, company_name)
            current_line_row_line = 760
            # current_line_row_line = 760
            pdf_object.setFillColorRGB(0, 0, 0)
            pdf_object.setFont("Courier", 9)
            for address_line in company_address:
                pdf_object.drawString(35, current_line_row_line, address_line)
                current_line_row_line -= 13

            # company phone number and email address
            pdf_object.drawString(35, current_line_row_line, UtilConfigReader.get_payslip_config("phone_number"))
            current_line_row_line -= 9
            pdf_object.drawString(35, current_line_row_line, UtilConfigReader.get_payslip_config("company_email_id"))
            current_line_row_line -= 9
            pdf_object.drawString(35, current_line_row_line, UtilConfigReader.get_payslip_config("company_website"))

            # right side payslip - header
            pdf_object.setFillColorRGB(0, 0, 0)
            pdf_object.setFont("Courier-Bold", 14)
            pdf_object.drawString(390, 780, "Pay Advice")

            pdf_object.setFont("Times-Italic", 9)
            pdf_object.drawString(370, 770, str(UtilConfigReader.get_payslip_config("payslip_title")).format(payslip_month))

            pdf_object.setFont("Courier", 9)
            current_line_row_line -= 15
            pdf_object.drawString(35, current_line_row_line,
                                  "Employee Name : {} {}".format(salary_entry["first_name"], salary_entry["last_name"]))
            current_line_row_line -= 11
            pdf_object.drawString(35, current_line_row_line, "Employee Number: {}".format(employee_number))
            current_line_row_line -= 11
            pdf_object.drawString(35, current_line_row_line, "Date of Joining: {}".format(salary_entry["employment_start_date"]))
            current_line_row_line -= 11
            pdf_object.drawString(35, current_line_row_line,"Department : {}".format(salary_entry["department"]))

            # drawing a line
            current_line_row_line -= 5
            pdf_object.setFont("Courier-Bold", 14)
            pdf_object.line(30, current_line_row_line, 550, current_line_row_line)

            # Earnings
            current_line_row_line -= 20
            pdf_object.setFont("Courier-Bold", 14)
            pdf_object.drawString(35, current_line_row_line, "EARNINGS")
            pdf_object.setFont("Courier-Bold", 10)
            for employee_number in UtilPayslip.salary_data_dict.keys():
                print(employee_number)
                print(UtilPayslip.salary_data_dict[employee_number])
            item_number = 0
            total_earnings = 0
            # for earning_name in dict_earnings.keys():
            #     current_line_row_line -= 13
            #     item_number += 1
            #     pdf_object.drawString(45, current_line_row_line, "{}.{}".format(item_number, earning_name))
            #     temp_value = "{:.2f}".format(round(dict_earnings[earning_name][1], 2)).rjust(10, ' ')
            #     pdf_object.drawString(450, current_line_row_line, "{}".format(temp_value))
            #     total_earnings += dict_earnings[earning_name][1]
            #
            # total_earnings_rounded = round(total_earnings, 2)



            # saving the pdf
            pdf_object.save()

    @staticmethod
    def get_pdf_filename(_employee_number, _salary_entry_dict):
        file_name = "{}_{}_{}{}.pdf".format(_salary_entry_dict["salary_month"], _employee_number,
                                             _salary_entry_dict["first_name"], _salary_entry_dict["last_name"])
        return file_name



# def num2words(num):
#     # #num = float(num)
#     # int_part = int(num)
#     # float_part = num - int_part
#     # decimal_part = round(num - int(num),2)
#     num = decimal.Decimal(num)
#     decimal_part = round(num - int(num),2)
#     num = int(num)
#
#     if decimal_part:
#         # return num2words(num) + " point " + (" ".join(num2words(i) for i in str(decimal_part)[2:]))
#         return "Rupees " + num2words(num) + " And " + (num2words(str(decimal_part)[2:])) + " paisa only"
#
#     under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven',
#                 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
#     tens = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
#     above_100 = {100: 'Hundred', 1000: 'Thousand', 100000: 'Lakhs', 10000000: 'Crores'}
#
#     if num < 20:
#         return under_20[num]
#
#     if num < 100:
#         return tens[num // 10 - 2] + ('' if num % 10 == 0 else ' ' + under_20[num % 10])
#
#     # find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
#     pivot = max([key for key in above_100.keys() if key <= num])
#
#     return num2words(num // pivot) + ' ' + above_100[pivot] + ('' if num % pivot == 0 else ' ' + num2words(num % pivot))


# def add_line_in_pdf(_column, _row, _content, _row_decrement_value=None, _font_name=None, _font_size=None):
#     if _font_name is not None and _font_size is not None:
#         pdf.setFont(_font_name, _font_size)
#
#     if _row_decrement_value is not None:
#         _row = _row - _row_decrement_value
#
#     pdf.drawString(_column, _row, _content)
#
#     return _row


dict_earnings = {
    'Week1-Salary': ["Dates: 2024-06-01, 2024-06-02. Worked days - 2", 900.4567],
    'Week2-Salary': ["Dates: 2024-06-01, 2024-06-02, 2024-06-03, 2024-06-04, 2024-06-05. Worked days - 5", 2500.2],
    'Incentives': ["", 1000],
    'Bonus': ["", 8000]}

dict_deductions = {'Salary Advance': ["", 800.0],
                   'PF Contributions': ["", 90]}

# image = "C:\\Users\\User\\Documents\\GitHub\\projects\\duty_roster_scheduler\\scheduler\\lion.jpeg"
#
#

#
# add_line_in_pdf(50, current_line_row_line,
#                 "( Total Earning - Rs {} )".format("{:.2f}".format(total_earnings_rounded).rjust(10, ' ')),
#                 _row_decrement_value=13)
#
# current_line_row_line -= 20
# pdf.line(30, current_line_row_line, 550, current_line_row_line)
#
# # Deductions
# current_line_row_line -= 20
# pdf.drawString(35, current_line_row_line, "DEDUCTIONS")
# item_number = 0
# total_deductions = 0
#
# for deduction_name in dict_deductions.keys():
#     item_number += 1
#     current_line_row_line = add_line_in_pdf(45, current_line_row_line, "{}.{}".format(item_number, deduction_name),
#                                             _row_decrement_value=13)
#     temp_value = "{:.2f}".format(round(dict_deductions[deduction_name][1], 2)).rjust(10, ' ')
#     current_line_row_line = add_line_in_pdf(450, current_line_row_line, "{}".format(temp_value))
#
#     total_deductions += dict_deductions[deduction_name][1]
#
# total_deductions_rounded = round(total_deductions, 2)
#
# current_line_row_line = add_line_in_pdf(50, current_line_row_line, "( Total Deductions - Rs {} )".format(
#     "{:.2f}".format(total_deductions_rounded).rjust(10, ' ')), _row_decrement_value=13)
#
# current_line_row_line -= 20
# pdf.line(30, current_line_row_line, 550, current_line_row_line)
#
# current_line_row_line -= 15
# net_pay = total_earnings_rounded - total_deductions_rounded
#
#
# add_line_in_pdf(50, current_line_row_line,
#                 "Net Pay ( Rs. {} - Rs. {} )  : Rs.{} ".format(total_earnings_rounded, total_deductions_rounded,
#                                                                net_pay),
#                 _row_decrement_value=13)
#
# amount_in_words = num2words(net_pay)
# current_line_row_line = add_line_in_pdf(50, current_line_row_line, "Amount in Words  :",
#                                         _row_decrement_value=30)
#
# # current_line_row_line = add_line_in_pdf(110, current_line_row_line, "{}".format(amount_in_words),
# #                                         _row_decrement_value=10, _font_name="Courier-Bold", _font_size=8)
#
# current_line_row_line -= 20
# text = pdf.beginText(110, current_line_row_line)
# text.setFont("Courier", 12)
# text.setFillColor(colors.black)
# len_text = len(amount_in_words)
# net_pay_words = amount_in_words.split(" ")
# line_max_length = 60
# current_line_text = ''
# for word in net_pay_words:
#     if len(current_line_text) >= line_max_length:
#         text.textLine(current_line_text)
#         current_line_text = ''
#     current_line_text += word + ' '
# text.textLine(current_line_text)
# pdf.drawText(text)
#
# current_line_row_line -= 70
# #pdf.line(30, current_line_row_line, 550, current_line_row_line)
# pdf.setFont("Courier-Bold", 24)
# pdf.drawCentredString(300, current_line_row_line, "**********")
#
#
# # creating the title by setting it's font
# # and putting it on the canvas
# pdf.setFont('Courier', 36)
# # pdf.drawCentredString(300, 770, title)
#
# # creating the subtitle by setting it's font,
# # colour and putting it on the canvas
# pdf.setFillColorRGB(0, 0, 255)
# pdf.setFont("Courier-Bold", 24)
# # pdf.drawCentredString(290, 720, subTitle)
#
# # drawing a line
# # pdf.line(30, 710, 550, 710)
#
# # creating a multiline text using
# # textline and for loop
# text = pdf.beginText(40, 680)
# text.setFont("Courier", 18)
# text.setFillColor(colors.red)
#
# for line in textLines:
#     text.textLine(line)
# # pdf.drawText(text)
#
# # drawing a image at the
# # specified (x.y) position
# # pdf.drawInlineImage(image, 130, 400)
#
# # saving the pdf
# pdf.save()
