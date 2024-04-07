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
		 employment_end_date DATE );
		 ''')


conn.commit()

conn.close()