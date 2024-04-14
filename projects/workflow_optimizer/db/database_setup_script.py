import sqlite3

conn = sqlite3.connect('../data/marania_data.db')

print("Opened database successfully")

# create tables and populate data for mnemonic_data table
conn.execute("DROP TABLE IF EXISTS mnemonic_data;")
conn.execute('''CREATE TABLE mnemonic_data
         (id INT PRIMARY KEY     NOT NULL,
         mnemonic_id_group     TEXT    NOT NULL,
         mnemonic_id           TEXT    NOT NULL,
         description           TEXT    NOT NULL);
         ''')

conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (1, 'address_id', 'door_number', 'Door Number');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (2, 'address_id', 'street_name1', 'Street Name 1');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (3, 'address_id', 'street_name2', 'Street Name 2');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (4, 'address_id', 'city', 'City');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (5, 'address_id', 'district', 'District');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (6, 'address_id', 'state', 'State');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (7, 'address_id', 'country', 'Country');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (8, 'address_id', 'pin', 'Pin');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (9, 'duty_shift_id', 'morning_shift', 'Morning Shift');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (10, 'duty_shift_id', 'evening_shift', 'Evening Shift');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (11, 'duty_shift_id', 'night_shift', 'Night Shift');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (12, 'duty_shift_id', 'normal_shift', 'Normal Shift');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (13, 'duty_shift_id', 'adhoc', 'AD-Hoc');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (14, 'duty_shift_timing', 'morning_time', '6 am to 2 pm ');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (15, 'duty_shift_timing', 'evening_time', '2 pm to 8 pm ');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (16, 'duty_shift_timing', 'night_time', '8 pm to 6 am');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (17, 'duty_shift_timing', 'normal_time', '8 am to 6 pm ');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (18, 'duty_shift_timing', 'adhoc_time', 'any time ');");

# contact
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (19, 'contact_id', 'mobile_number', 'Mobile Number');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (20, 'contact_id', 'phone_number', 'Phone Number');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (21, 'contact_id', 'email_id', 'Email ID');");

# identity proof
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (22, 'identity_proof', 'aadhaar', 'Aadhaar');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (23, 'identity_proof', 'passport ', 'Passport ');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (24, 'identity_proof', 'election_card', 'Election Card');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (25, 'identity_proof', 'driving_license', 'Driving License');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (26, 'identity_proof', 'ration_card', 'Ration Card');");

# qualification
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (27, 'qualification', 'no_formal_education', 'No Formal Education');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (28, 'qualification', 'primary', 'Primary School');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (29, 'qualification', 'high_school', 'High School');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (30, 'qualification', 'secondary_school', 'Secondary School');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (31, 'qualification', 'under_graduate', 'Under Graduate');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (32, 'qualification', 'post_graduate', 'Post Graduate');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (33, 'qualification', 'doctorate', 'Doctorate');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (34, 'qualification', 'other', 'Other');");

# number of leaves
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (35, 'number_of_leaves', 'zero', '0');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (36, 'number_of_leaves', 'one', '1');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (37, 'number_of_leaves', 'two', '2');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (38, 'number_of_leaves', 'three', '3');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (39, 'number_of_leaves', 'four', '4');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (40, 'number_of_leaves', 'five', '5');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (41, 'number_of_leaves', 'six', '6');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (42, 'number_of_leaves', 'seven', '7');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (43, 'number_of_leaves', 'eight', '8');");

# salary type
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (44, 'salary_type', 'daily', 'Daily');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
      VALUES (45, 'salary_type', 'weekly', 'Weekly');");
conn.execute("INSERT INTO mnemonic_data (id,mnemonic_id_group,mnemonic_id,description) \
       VALUES (46, 'salary_type', 'monthly', 'Monthly');");

conn.execute("DROP TABLE IF EXISTS employee;")
conn.execute('''CREATE TABLE employee
         (id INTEGER PRIMARY KEY AUTOINCREMENT,
		 employee_number TEXT    NOT NULL,
		 first_name  TEXT    NOT NULL,
		 last_name  TEXT    NOT NULL,
		 father_name  TEXT    NOT NULL,
		 sex CHAR NOT NULL, 
		 date_of_birth DATE,
		 education   TEXT    NOT NULL,
		 employment_start_date DATE,
		 employment_end_date DATE,
		 department   TEXT    NOT NULL,
         leaves_per_month INT, 
         primary_duty_code   TEXT    NOT NULL,
         salary_type_code  TEXT    NOT NULL,
         salary  DOUBLE 
		  );
		 ''')

conn.execute("DROP TABLE IF EXISTS address;")
conn.execute('''CREATE TABLE address
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     employee_number TEXT    NOT NULL,
     address_type  TEXT    NOT NULL,
    address_value  TEXT    NOT NULL,
    start_date DATE,
    end_date DATE);
''')

conn.execute("DROP TABLE IF EXISTS contact;")
conn.execute('''CREATE TABLE contact
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     employee_number TEXT    NOT NULL,
     contact_type  TEXT    NOT NULL,
    contact_value  TEXT    NOT NULL,
    start_date DATE,
    end_date DATE,
    note  TEXT    NOT NULL);
''')

conn.execute("DROP TABLE IF EXISTS identity;")
conn.execute('''CREATE TABLE identity
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     employee_number TEXT    NOT NULL,
     identity_type  TEXT    NOT NULL,
     identity_value TEXT    NOT NULL,
     start_date DATE,
     end_date DATE
     );
''')

conn.execute("DROP TABLE IF EXISTS department;")
conn.execute('''CREATE TABLE department
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     department_id TEXT    NOT NULL,
     department_name  TEXT    NOT NULL,
     description TEXT    NOT NULL,
     minimum_resource_count INTEGER
     );
''')

conn.execute("DROP TABLE IF EXISTS duty_catalog;")
conn.execute('''CREATE TABLE duty_catalog
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     duty_code TEXT    NOT NULL,
     duty_name  TEXT    NOT NULL,
     duty_description TEXT    NOT NULL,
     salary_type TEXT    NOT NULL,
     default_salary DOUBLE,
     default_department TEXT    NOT NULL,
     default_resource_count INTEGER
     );
''')

conn.execute("DROP TABLE IF EXISTS employee_duties;")
conn.execute('''CREATE TABLE employee_duties
    (employee_number TEXT    NOT NULL,
     duty_date  TEXT    NOT NULL,
     duty_description TEXT  NULL
     );
''')

conn.execute("DROP TABLE IF EXISTS company_holidays;")
conn.execute('''CREATE TABLE company_holidays
    (holiday_date TEXT    NOT NULL,
     holiday_name  TEXT    NOT NULL,
     description TEXT  NULL
     );
''')


conn.commit()

conn.close()
