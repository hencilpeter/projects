import wx
from windows.window_search_employee import WindowSearchEmployee
from windows.window_employee import WindowEmployee
from windows.window_duty_catalog import DutyCatalog
from windows.window_duty_allocation import DutyAllocation
from util.util_config_reader import UtilConfigReader
from db.sqlite_sqls import SqliteSqls

class WindowMain(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        # sqlite
        self.sqlite_sqls = SqliteSqls(db_file_name=UtilConfigReader.get_application_config("app_database_file_name"))

        self.SetSize((500, 400))
        self.SetTitle("TODO:Workflow Optimization...")

        # Menu Bar
        self.frame_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Search Employee", "Search Employee Details ")
        self.Bind(wx.EVT_MENU, self.handler_search_employee, item)
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Add/Update Employee", "Add or Update Employee Details")
        self.Bind(wx.EVT_MENU, self.handler_add_update_employee, item)
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Duty Catalog", "Duty Catalog")
        self.Bind(wx.EVT_MENU, self.handler_duty_catalog, item)
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Duty Allocation", "Duty Allocation")
        self.Bind(wx.EVT_MENU, self.handler_duty_allocation, item)
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Backup/Restore", "Backup/Restore")
        self.Bind(wx.EVT_MENU, self.handler_backup_restore, item)
        self.frame_menubar.Append(wxglade_tmp_menu, "Admin")
        wxglade_tmp_menu = wx.Menu()
        self.frame_menubar.Append(wxglade_tmp_menu, "View/Print")
        wxglade_tmp_menu = wx.Menu()
        self.frame_menubar.Append(wxglade_tmp_menu, "Exit")
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Close Application", "Close Application")
        self.Bind(wx.EVT_MENU, self.handler_exit_application, item)
        self.SetMenuBar(self.frame_menubar)
        # Menu Bar end
        self.Layout()

        # end wxGlade


    def handler_add_update_employee(self, event):  # wxGlade: MyFrame.<event_handler>
        dlg_employee = WindowEmployee(None, wx.ID_ANY, "")
        #         self.SetTopWindow(self.dlg_employee)
        dlg_employee.ShowModal()
        dlg_employee.Destroy()

    def handler_search_employee(self, event):
        search_employee = WindowSearchEmployee(None, wx.ID_ANY, "", _sqlite_sqls=self.sqlite_sqls)
        search_employee.ShowModal()
        search_employee.Destroy()

    def handler_duty_catalog(self, event):  # wxGlade: MyFrame.<event_handler>\
        dlg_duty_manager = DutyCatalog(None, wx.ID_ANY, "")
        dlg_duty_manager.ShowModal()
        dlg_duty_manager.Destroy()

    def handler_duty_allocation(self, event):  # wxGlade: MyFrame.<event_handler>
        dialog_duty_allocation = DutyAllocation(None, wx.ID_ANY, "")
        dialog_duty_allocation.ShowModal()
        dialog_duty_allocation.Destroy()

    def handler_backup_restore(self, event):
        print("Event handler 'handler_backup_restore' not implemented!")
        event.Skip()

    def handler_exit_application(self, event):  # wxGlade: MyFrame.<event_handler>
        print("closing the application...")
        self.Close()


# end of class MyFrame

class MenuBar(wx.App):
    def OnInit(self):
        self.frame = WindowMain(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MenuBar

# if __name__ == "__main__":
#     menubar = MenuBar(0)
#     menubar.MainLoop()
