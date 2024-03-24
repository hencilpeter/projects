from html.html_file_parent import HtmlFileParent


class HtmlDutyViewer(HtmlFileParent):
    def __init__(self,_header_name, _footer):
        super().__init__( _header_name, _footer)

    def add_table_row_header_with_two_column(self, _col1_header, _col2_header):
        super().append_html_body(
            """
            <tr>
            <th>{}</th>
            <th>{}</th>
            </tr>
            """.format(_col1_header, _col2_header)
        )

    def add_table_row_values_with_two_column(self, _col1_value, _col2_value):
        super().append_html_body(
            """
           <tr>
            <td>{}</td>
            <td>{}</td>
          </tr>
            """.format(_col1_value, _col2_value)
        )

    def get_html_file_data(self):
        html_file_data = super().get_header() + "<table>" + super().get_file_body() + "</table>" + super().get_footer()

        return html_file_data

    def save_html_file(self, _file_name):
        html_file_data = self.get_html_file_data()

        with open(_file_name, mode="w") as file:
            file.write(html_file_data)
