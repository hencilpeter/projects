# importing modules

import decimal
import os.path
from collections import defaultdict
from datetime import datetime

from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from data_models.common_model import CommonModel
from util.util_common import UtilCommon
from util.util_config_reader import UtilConfigReader

import wx

class UtilPayslip:
    salary_data_dict = defaultdict(lambda: -1)

    @staticmethod
    def load_all_salary_data(_sql_connection, _salary_month):
        salary_data_cursor = _sql_connection.get_table_data(
            "select * from employee_salary_data where salary_month='{}';".format(_salary_month))
        salary_data_as_list = CommonModel.get_table_data_as_list(_data_cursor=salary_data_cursor)
        UtilPayslip.salary_data_dict = UtilCommon.get_dict_from_list(_list=salary_data_as_list,
                                                                     _dict_key="employee_number")

    @staticmethod
    def num2words(num):
        num = decimal.Decimal(num)
        decimal_part = round(num - int(num), 2)
        num = int(num)

        if decimal_part:
            return "Rupees " + UtilPayslip.num2words(num) + " And " + (
                UtilPayslip.num2words(str(decimal_part)[2:])) + " paisa only"

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
    def add_line_in_pdf(_pdf_object, _column, _row, _content, _row_decrement_value=None, _font_name=None,
                        _font_size=None, _fill_colour= None):
        if _font_name is not None and _font_size is not None:
            _pdf_object.setFont(_font_name, _font_size)

        if _fill_colour is not None and len(_fill_colour) == 3:
            _pdf_object.setFillColorRGB(_fill_colour[0], _fill_colour[1], _fill_colour[2])

        if _row_decrement_value is not None:
            _row = _row - _row_decrement_value

        _pdf_object.drawString(_column, _row, _content)

        return _row

    @staticmethod
    def add_multiline_string_in_pdf(_pdf_object, _column, _row, _content, _item_number):
        chunk_length = 60
        chunk_list = []
        for start_location in range(0, len(_content), chunk_length):
            end_location = len(_content) if start_location + chunk_length > len(
                _content) else start_location + chunk_length
            chunk_list.append(_content[start_location:end_location])

        _pdf_object.drawString(_column, _row, "{}.{}"
                               .format(_item_number, chunk_list[0]))

        for index in range(1, len(chunk_list)):
            _row -= 13
            _pdf_object.drawString(_column + 10, _row, "{}".format(chunk_list[index]))

        return _row

    @staticmethod
    def generate_payslip(_salary_dict, _sql_connection, _salary_month):
        if len(_salary_dict.keys()) == 0:
            return

        # load all salary data
        UtilPayslip.load_all_salary_data(_sql_connection=_sql_connection, _salary_month=_salary_month)
        salary_slip_count = 0
        for employee_number in _salary_dict:
            salary_entry = _salary_dict[employee_number]
            if not salary_entry["is_salary_data_available"]:
                continue
            payslip_file_name = UtilPayslip.get_pdf_filename(_employee_number=employee_number,
                                                             _salary_entry_dict=salary_entry)

            # creating a pdf object
            pdf_object = canvas.Canvas(payslip_file_name)
            company_name = UtilConfigReader.get_payslip_config("company_name")
            company_address = UtilConfigReader.get_payslip_config("company_address")

            salary_month = datetime.strptime(_salary_month, "%Y%m%d")
            payslip_month = salary_month.strftime("%B") + " " + str(salary_month.year)

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
            pdf_object.drawString(370, 770,
                                  str(UtilConfigReader.get_payslip_config("payslip_title")).format(payslip_month))

            pdf_object.setFont("Courier", 9)
            current_line_row_line -= 15
            pdf_object.drawString(35, current_line_row_line,
                                  "Employee Name : {} {}".format(salary_entry["first_name"], salary_entry["last_name"]))
            current_line_row_line -= 11
            pdf_object.drawString(35, current_line_row_line, "Employee Number: {}".format(employee_number))
            current_line_row_line -= 11
            pdf_object.drawString(35, current_line_row_line,
                                  "Date of Joining: {}".format(salary_entry["employment_start_date"]))
            current_line_row_line -= 11
            pdf_object.drawString(35, current_line_row_line, "Department : {}".format(salary_entry["department"]))

            # drawing a line
            current_line_row_line -= 5
            pdf_object.setFont("Courier-Bold", 14)
            pdf_object.line(30, current_line_row_line, 550, current_line_row_line)

            # Earnings
            current_line_row_line -= 20
            pdf_object.setFont("Courier-Bold", 14)
            pdf_object.drawString(35, current_line_row_line, "EARNINGS")
            pdf_object.setFont("Courier-Bold", 10)
            item_number = 0
            total_earnings = 0
            deductions = []
            for salary_entry_dict in UtilPayslip.salary_data_dict[employee_number]:
                if salary_entry_dict["entry_type"] != "earning":
                    deductions.append(salary_entry_dict)
                    continue

                current_line_row_line -= 13
                item_number += 1
                temp_current_line = current_line_row_line
                current_line_row_line = UtilPayslip.add_multiline_string_in_pdf(_pdf_object=pdf_object, _column=45,
                                                                                _row=current_line_row_line,
                                                                                _content=salary_entry_dict[
                                                                                    "description"],
                                                                                _item_number=item_number)

                temp_value = "{:.2f}".format(round(float(salary_entry_dict["amount"]), 2)).rjust(10, ' ')
                pdf_object.drawString(450, temp_current_line, "{}".format(temp_value))
                total_earnings += float(salary_entry_dict["amount"])

            total_earnings_rounded = round(total_earnings, 2)
            UtilPayslip.add_line_in_pdf(pdf_object, 50, current_line_row_line,
                                        "( Total Earning - Rs {} )".format(
                                            "{:.2f}".format(total_earnings_rounded).rjust(10, ' ')),
                                        _row_decrement_value=13)

            current_line_row_line -= 20
            pdf_object.line(30, current_line_row_line, 550, current_line_row_line)

            # Deductions
            current_line_row_line -= 20
            pdf_object.drawString(35, current_line_row_line, "DEDUCTIONS")

            item_number = 0
            total_deductions = 0
            for deduction in deductions:
                current_line_row_line -= 13
                item_number += 1
                temp_current_line = current_line_row_line
                current_line_row_line = UtilPayslip.add_multiline_string_in_pdf(_pdf_object=pdf_object, _column=45,
                                                                                _row=current_line_row_line,
                                                                                _content=salary_entry_dict[
                                                                                    "description"],
                                                                                _item_number=item_number)

                temp_value = "{:.2f}".format(round(float(salary_entry_dict["amount"]), 2)).rjust(10, ' ')
                pdf_object.drawString(450, temp_current_line, "{}".format(temp_value))
                total_deductions += float(salary_entry_dict["amount"])

            total_deductions_rounded = round(total_deductions, 2)

            current_line_row_line = UtilPayslip.add_line_in_pdf(pdf_object, 50, current_line_row_line,
                                                                "( Total Deductions - Rs {} )".format(
                                                                    "{:.2f}".format(total_deductions_rounded).rjust(10,
                                                                                                                    ' ')),
                                                                _row_decrement_value=13)

            current_line_row_line -= 20
            pdf_object.line(30, current_line_row_line, 550, current_line_row_line)

            current_line_row_line -= 15
            net_pay = total_earnings_rounded - total_deductions_rounded

            UtilPayslip.add_line_in_pdf(pdf_object, 50, current_line_row_line,
                                        "Net Pay ( Rs. {} - Rs. {} )  : Rs.{} ".format(total_earnings_rounded,
                                                                                       total_deductions_rounded,
                                                                                       net_pay),
                                        _row_decrement_value=13)

            amount_in_words = UtilPayslip.num2words(net_pay)
            current_line_row_line = UtilPayslip.add_line_in_pdf(pdf_object, 50, current_line_row_line,
                                                                "Amount in Words  :",
                                                                _row_decrement_value=30)

            current_line_row_line = UtilPayslip.add_line_in_pdf(pdf_object, 110, current_line_row_line,
                                                                "{}".format(amount_in_words if amount_in_words
                                                                            .startswith(
                                                                    "Rupees ") else "Rupees " + amount_in_words
                                                                                    + " only."),
                                                                _row_decrement_value=20, _font_name="Courier-Bold",
                                                                _font_size=14, _fill_colour=(0, 0, 255))

            current_line_row_line -= 70
            pdf_object.setFont("Courier-Bold", 24)
            pdf_object.setFillColorRGB(0, 0, 0)
            pdf_object.drawCentredString(300, current_line_row_line, "**********")

            # saving the pdf
            pdf_object.save()
            salary_slip_count += 1

        # message box
        dial = wx.MessageDialog(None, "There are {} Payslip(s) Saved Successfully...".format(salary_slip_count),
                                "Payslip", wx.OK | wx.STAY_ON_TOP | wx.CENTRE)
        dial.ShowModal()

    @staticmethod
    def get_pdf_filename(_employee_number, _salary_entry_dict):
        file_path = UtilConfigReader.get_application_config(configuration_name="out_payslip_files_path")
        file_name = "{}_{}_{}{}.pdf".format(_salary_entry_dict["salary_month"], _employee_number,
                                            _salary_entry_dict["first_name"], _salary_entry_dict["last_name"])
        return os.path.join(file_path, file_name)
