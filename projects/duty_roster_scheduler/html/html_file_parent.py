class HtmlFileParent:
    def __init__(self, _header_name, _footer):
        self.file_header = self.get_default_header(_header_name)
        self.file_body = ""
        self.file_footer = self.get_default_footer(_footer)

    def get_default_header(self, _header_name):
        return """
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                table, th, td {{
                  border: 2px solid black;
                }}
                </style>
                </head>
                <body>
                
                <h1>{}</h1>
                """.format(_header_name)

    def get_default_footer(self, _footer):
        return """"
                <div class="footer">
                     <p>{}</p>
                    </div>
                """.format(_footer)
    def get_header(self):
        return self.file_header

    def get_footer(self):
        return self.file_footer

    def get_file_body(self):
        return self.file_body

    def append_html_body(self, _body):
        self.file_body = self.file_body  + _body
