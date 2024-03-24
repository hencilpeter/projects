# https://www.geeksforgeeks.org/python-wxpython-module-introduction/
import wx
import datetime
import wx.adv
import wx.grid as gridlib
from data import table_data_reader
class MainWindow:
    def __init__(self):
        # data reader
        self.data_reader = table_data_reader.TableDataReader()
        # application object
        self.application = wx.App()

        # frame object
        self.frame = wx.Frame(None, title="TODO: Marania Filaments Office Application", size=(800, 600))
        panel = wx.Panel(self.frame)

        # text controls
        label_employee_number = wx.StaticText(panel, label="Employee Number : ", pos=(20, 20))
        label_first_name = wx.StaticText(panel, label="First Name : ", pos=(20, 45))
        label_last_name = wx.StaticText(panel, label="Last Name : ", pos=(20, 70))
        label_father_name = wx.StaticText(panel, label="Father Name : ", pos=(20, 95))
        label_sex = wx.StaticText(panel, label="Sex : ", pos=(20, 120))

        label_date_of_birth = wx.StaticText(panel, label="Date of Birth : ", pos=(20, 185))
        label_highest_education = wx.StaticText(panel, label="Highest Education : ", pos=(20, 210))
        label_employment_start_date = wx.StaticText(panel, label="Employment Start Date : ", pos=(20, 235))
        label_employment_end_date = wx.StaticText(panel, label="Employment End Date : ", pos=(20, 260))

        # input controls
        self.text_employee_number = wx.TextCtrl(panel, pos=(180, 20), size=(150, 23))
        self.text_first_name = wx.TextCtrl(panel, pos=(180, 45), size=(150, 23))
        self.text_last_name = wx.TextCtrl(panel, pos=(180, 70), size=(150, 23))
        self.text_father_name = wx.TextCtrl(panel, pos=(180, 95), size=(150, 23))

        lblList = ['Male', 'Female']
        self.rbox = wx.RadioBox(panel, label='Select Option', pos=(180, 120), choices=lblList,
                                majorDimension=1, style=wx.RA_SPECIFY_ROWS)

        date_date_of_birth = wx.adv.DatePickerCtrl(panel, wx.ID_ANY, wx.DefaultDateTime, pos=(180, 185), size=(150, 23))
        self.text_highest_education = wx.TextCtrl(panel, pos=(180, 210), size=(150, 23))
        date_employment_start_date = wx.adv.DatePickerCtrl(panel, wx.ID_ANY, wx.DefaultDateTime, pos=(180, 235),
                                                           size=(150, 23))
        date_employment_end_date = wx.adv.DatePickerCtrl(panel, wx.ID_ANY, wx.DefaultDateTime, pos=(180, 260),
                                                         size=(150, 23))

        # Address - begin
        address_group = wx.StaticBox(panel, -1, 'Address', pos=(10, 300), size=(360, 170))


        self.myAddressGrid = gridlib.Grid(panel, pos=(15, 320), size=(340, 140))  # width and height
        self.myAddressGrid.SetRowLabelSize(50)
        self.myAddressGrid.SetColLabelSize(25)


        dict_address = self.data_reader.get_mnemonic_table_data("address_id")
        choices_list = [value for key, value in dict_address.items()]

        address_fields_count =  len(choices_list)
        self.myAddressGrid.CreateGrid(address_fields_count, 2)

        self.myAddressGrid.SetColSize(0, 120)
        self.myAddressGrid.SetColSize(1, 150)


        choice_editor = wx.grid.GridCellChoiceEditor(choices_list, True)
        for row in range(0, address_fields_count):
            self.myAddressGrid.SetCellEditor(row, 0, choice_editor)
        self.myAddressGrid.SetColLabelValue(0, "Address Type:")
        self.myAddressGrid.SetColLabelValue(1, "Address Detail:")

        # Address - end


        # contact - start
        contact_group = wx.StaticBox(panel, -1, 'Contact', pos=(390, 180), size=(350, 180))

        self.mycontactGrid = gridlib.Grid(panel, pos=(410, 200), size=(320, 140))  # width and height
        self.mycontactGrid.SetRowLabelSize(50)
        self.mycontactGrid.SetColLabelSize(25)

        dict_contact = self.data_reader.get_mnemonic_table_data("contact_id")
        contact_choices_list = [value for key, value in dict_contact.items()]
        contact_row_count = len(contact_choices_list) * 3

        self.mycontactGrid.CreateGrid(contact_row_count, 2)

        self.mycontactGrid.SetColSize(0, 120)
        self.mycontactGrid.SetColSize(1, 130)

        contact_choice_editor = wx.grid.GridCellChoiceEditor(contact_choices_list, True)
        for row in range(0, address_fields_count ):
            self.mycontactGrid.SetCellEditor(row, 0, contact_choice_editor)
        self.mycontactGrid.SetColLabelValue(0, "Contact Type:")
        self.mycontactGrid.SetColLabelValue(1, "Contact Detail:")

        # contact - end


        # identity - start
        identity_group = wx.StaticBox(panel, -1, 'Identity', pos=(390, 370), size=(350, 160))

        self.myIdentityProofGrid = gridlib.Grid(panel, pos=(410, 390), size=(320, 123))  # width and height
        self.myIdentityProofGrid.SetRowLabelSize(50)
        self.myIdentityProofGrid.SetColLabelSize(25)

        dict_identity_proof = self.data_reader.get_mnemonic_table_data("identity_proof")
        identity_proof_choices_list = [value for key, value in dict_identity_proof.items()]
        identity_proof_row_count = len(identity_proof_choices_list)

        self.myIdentityProofGrid.CreateGrid(identity_proof_row_count, 3)
        self.myIdentityProofGrid.SetColSize(0, 90)
        self.myIdentityProofGrid.SetColSize(1, 120)
        self.myIdentityProofGrid.SetColSize(2, 60)

        identity_proof_choice_editor = wx.grid.GridCellChoiceEditor(identity_proof_choices_list, True)
        for row in range(0, identity_proof_row_count):
            self.myIdentityProofGrid.SetCellEditor(row, 0, identity_proof_choice_editor)
        self.myIdentityProofGrid.SetColLabelValue(0, "Identity Type:")
        self.myIdentityProofGrid.SetColLabelValue(1, "Number/ID:")
        self.myIdentityProofGrid.SetColLabelValue(2, "Url:")

        # identity - end

        # # Duty
        # duty_group = wx.StaticBox(panel, -1, 'Duty', pos=(270, 300), size=(240, 140))
        #
        # # compensation
        # compensation_group = wx.StaticBox(panel, -1, 'Compensation', pos=(500, 300), size=(240, 140))

        # button
        self.btnClose = wx.Button(panel, label="close", pos=(130, 510))
        self.btnSave = wx.Button(panel, label="save", pos=(210, 510))
        self.frame.Bind(wx.EVT_BUTTON, self.handle_close_button, self.btnClose)
        self.frame.Bind(wx.EVT_BUTTON, self.handle_Save_button, self.btnSave)


        # event handler
        self.frame.Bind(wx.adv.EVT_DATE_CHANGED, self.OnDateChanged, date_date_of_birth)
        self.frame.Bind(wx.adv.EVT_DATE_CHANGED, self.OnDateChanged, date_employment_start_date)
        self.frame.Bind(wx.adv.EVT_DATE_CHANGED, self.OnDateChanged, date_employment_end_date)

    def OnDateChanged(self, evt):
        sel_date = evt.GetDate()
        print(sel_date.Format("%d-%m-%Y"))

    def handle_close_button(self, event):
        self.frame.Close()

    def handle_Save_button(self, event):
        print("save Button Pressed....")
        print(self.text_employee_number.GetValue())

        insert_statement = """
        insert into
        employee(employee_number, first_name, last_name, father_name, sex, date_of_birth, education,
                 employment_start_date, employment_end_date)
        values('{}', '{}', '{}', '{}', '{}', '2020-12-12', 'PhD', '2020-12-12', '2020-12-12')
        """.format(self.text_employee_number.GetValue(), self.text_first_name.GetValue(),
                   self.text_last_name.GetValue(), self.text_father_name.GetValue(), 'M')

        self.data_reader.write_data(insert_statement)

        cursor = self.data_reader.get_table_data("select * from employee")
        for row in cursor:
            print(row)

  #save employee details



    def ShowWindow(self):
      self.frame.Show()
      self.application.MainLoop()


if __name__ == "__main__":
    main_window = MainWindow()
    main_window.ShowWindow()
