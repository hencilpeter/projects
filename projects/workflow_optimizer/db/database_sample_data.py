import sqlite3

conn = sqlite3.connect('../data/marania_data.db')

print("Opened database successfully")
conn.execute("Delete from employee")
conn.execute(
    "insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education "
    ",employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) "
    "values('MF0001','John ','Samuel','Daniel','M','1995-05-19','No Formal Education','2024-04-11','9999-12-31','Production',0,'DT101','Monthly','12000');");
conn.execute(
    "insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education "
    ",employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) "
    "values('MF0002','Leonard ','Lee','Jerald','M','2000-07-01','High School','2024-04-11','9999-12-31','Production',0,'DT102','Daily','200');");
conn.execute(
    "insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education "
    ",employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) "
    "values('MF0003','Prathima ','Venati','Anand','F','1990-01-30','High School','2024-04-11','9999-12-31','Production',0,'DT102','Daily','300');");
conn.execute(
    "insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education "
    ",employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) "
    "values('MF0004','Varun ','Reddy','Venkat','M','1992-02-11','Under Graduate','2024-04-11','9999-12-31','Production',0,'DT102','Daily','350');");
conn.execute(
    "insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education "
    ",employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) "
    "values('MF0005','Maheshwarai ','Vijayakumar','Swaminathan','M','2001-05-19','No Formal Education','2024-04-11','9999-12-31','Administration',0,'DT103','Daily','200');");
conn.execute(
    "insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education "
    ",employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) "
    "values('MF0006','Shruthi ','Gupta','Agarwal','M','2002-08-14','No Formal Education','2024-04-11','9999-12-31','Administration',0,'DT104','Daily','8000');");
conn.execute(
    "insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education "
    ",employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) "
    "values('MF0007','Richard ','John','Bennet','M','1999-09-22','No Formal Education','2024-04-11','9999-12-31','Human Resource',0,'DT104','Monthly','11000');");

# department - data
conn.execute("INSERT INTO department ( department_id, department_name ,description) \
      VALUES ('D101', 'Administration', 'Administration');");
conn.execute("INSERT INTO department ( department_id, department_name ,description) \
      VALUES ('D102', 'Production', 'Production');");
conn.execute("INSERT INTO department ( department_id, department_name ,description) \
      VALUES ('D103', 'Sales', 'Sales');");
conn.execute("INSERT INTO department ( department_id, department_name ,description) \
      VALUES ('D104', 'Accounts', 'Accounts');");
conn.execute("INSERT INTO department ( department_id, department_name ,description) \
      VALUES ('D105', 'Human Resource', 'Human Resource');");
conn.execute("INSERT INTO department ( department_id, department_name ,description) \
      VALUES ('D106', 'Marketing', 'Marketing');");
conn.execute("INSERT INTO department ( department_id, department_name ,description) \
       VALUES ('D107', 'Maintenance', 'Maintenance');");

# duty_catalog
conn.execute("INSERT INTO duty_catalog ( duty_code,duty_name,duty_description,salary_type,default_salary,default_department, default_resource_count) \
      VALUES ('DT101', 'supervision', 'Supervision','Monthly',10000,'Production',1);");
conn.execute("INSERT INTO duty_catalog ( duty_code,duty_name,duty_description,salary_type,default_salary,default_department, default_resource_count) \
      VALUES ('DT102', 'machine_operation', 'Machine Operation','Daily',300,'Production',2);");
conn.execute("INSERT INTO duty_catalog ( duty_code,duty_name,duty_description,salary_type,default_salary,default_department, default_resource_count) \
      VALUES ('DT103', 'bobbin_winding', 'Bobbin Winding','Daily',300,'Production',2);");
conn.execute("INSERT INTO duty_catalog ( duty_code,duty_name,duty_description,salary_type,default_salary,default_department, default_resource_count) \
      VALUES ('DT104', 'mending', 'Mending','Daily',300,'Production',2);");
conn.execute("INSERT INTO duty_catalog ( duty_code,duty_name,duty_description,salary_type,default_salary,default_department, default_resource_count) \
       VALUES ('DT105', 'manager', 'Manager','Monthly',10000,'Administration',2);");


# holidays
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240101', 'New Year', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240115', 'Pongal', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240126', 'Republic Day', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240329', 'Good Friday', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240402', 'Test1', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240410', 'Test2', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240501', 'May Day', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20240815', 'Indpendence Day', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20241111', 'Ayutha Pooja', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
      VALUES ('20241131', 'Deepavali', '');");
conn.execute("INSERT INTO company_holidays ( holiday_date, holiday_name, description) \
       VALUES ('20241225', 'Christmas', '');");

conn.commit()

conn.close()
