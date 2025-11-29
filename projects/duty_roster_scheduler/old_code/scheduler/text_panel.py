import wx
import wx.html as html


class MainFrame(wx.Frame):
    """Create MainFrame class."""
    def __init__(self):
        """Initialise the class."""
        wx.Frame.__init__(self, None, -1, 'Demonstrate wxPython Html')
        self.panel = MainPanel(self)
        self.Centre()
        self.html_display.SetPage(self.raw_html())

    @staticmethod
    def raw_html():
        # html = ('<p><font color="#4C4C4C", size=2>What do we want: '
        #             '<font color="#FF0000">all</font>'
        #         '</p>')

        html = ("""
        <!DOCTYPE html>
<html>
<head>
<style>
table, th, td {
  border: 2px solid black;
}
</style>
</head>
<body>

<h1>The table element</h1>

<table>
  <tr>
    <th>Date</th>
    <th>Employee Names</th>
  </tr>
  <tr>
    <td>January</td>
    <td>$100, 200$100, 200$100, 200$100, 200$100, 200$100, 200$100, 200 <BR>$100, 200</td>

  </tr>
  <tr>
    <td>February</td>
    <td>$80</td>
  </tr>
</table>

</body>
</html>
""")
        return html


class MainPanel(wx.Panel):
    """Create a panel class to contain screen widgets."""
    def __init__(self, frame):
        """Initialise the class."""
        wx.Panel.__init__(self, frame)
        html_sizer = self._create_html_control(frame)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(html_sizer, flag=wx.ALL, border=10)
        self.SetSizerAndFit(main_sizer)

    def _create_html_control(self, frame):
        txt_style = wx.VSCROLL|wx.HSCROLL|wx.BORDER_SIMPLE
        frame.html_display = html.HtmlWindow(self, -1,
                                                size=(400, 200),
                                                style=txt_style)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(frame.html_display)
        return sizer


if __name__ == '__main__':
    """Run the application."""
    screen_app = wx.App()
    main_frame = MainFrame()
    main_frame.Show(True)
    screen_app.MainLoop()