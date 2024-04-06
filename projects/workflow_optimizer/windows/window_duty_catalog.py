import wx

import wx.grid


class DutyCatalog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DutyManager.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("Duty Manager")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.grid_1 = wx.grid.Grid(self, wx.ID_ANY, size=(1, 1))
        self.grid_1.CreateGrid(250, 6)
        self.grid_1.SetRowLabelSize(30)
        self.grid_1.SetColLabelSize(30)
        self.grid_1.SetGridLineColour(wx.Colour(0, 127, 255))
        self.grid_1.SetSelectionMode(wx.grid.Grid.SelectRows)
        self.grid_1.SetColLabelValue(0, "Duty Code")
        self.grid_1.SetColSize(0, 80)
        self.grid_1.SetColLabelValue(1, "Duty Name")
        self.grid_1.SetColSize(1, 100)
        self.grid_1.SetColLabelValue(2, "Duty Description")
        self.grid_1.SetColSize(2, 150)
        self.grid_1.SetColLabelValue(3, "Salary Type")
        self.grid_1.SetColSize(3, 80)
        self.grid_1.SetColLabelValue(4, "Default Salary")
        self.grid_1.SetColSize(4, 90)
        self.grid_1.SetColLabelValue(5, "Default Department")
        self.grid_1.SetColSize(5, 120)
        self.grid_1.SetMinSize((700, 303))
        sizer_1.Add(self.grid_1, 1, wx.EXPAND, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.btn_cancel)

        self.btn_delete = wx.Button(self, wx.ID_ANY, "Delete Duty")
        self.btn_delete.SetDefault()
        sizer_2.Add(self.btn_delete, 0, 0, 0)

        self.btn_Save = wx.Button(self, wx.ID_SAVE, "")
        sizer_2.AddButton(self.btn_Save)

        sizer_2.Realize()

        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.SetAffirmativeId(self.btn_delete.GetId())
        self.SetEscapeId(self.btn_cancel.GetId())

        self.Layout()
        # end wxGlade

# end of class DutyManager

# class MyApp(wx.App):
#     def OnInit(self):
#         self.dialog = DutyManager(None, wx.ID_ANY, "")
#         self.SetTopWindow(self.dialog)
#         self.dialog.ShowModal()
#         self.dialog.Destroy()
#         return True
#
# # end of class MyApp
#
# if __name__ == "__main__":
#     app = MyApp(0)
#     app.MainLoop()
