import sqlite3

conn = sqlite3.connect('../data/marania_data.db')

print("Opened database successfully")
conn.execute("Delete from employee")
conn.execute("insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education ,employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) values('MF0001','John ','Samuel','Daniel','M','1995-05-19','No Formal Education','2024-04-11','9999-12-31','Production',0,'DT101','Daily','12000');");
conn.execute("insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education ,employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) values('MF0002','Leonard ','Lee','Jerald','M','2000-07-01','High School','2024-04-11','9999-12-31','Production',0,'DT102','Daily','200');");
conn.execute("insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education ,employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) values('MF0003','Prathima ','Venati','Anand','F','1990-01-30','High School','2024-04-11','9999-12-31','Production',0,'DT102','Daily','300');");
conn.execute("insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education ,employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) values('MF0004','Varun ','Reddy','Venkat','M','1992-02-11','Under Graduate','2024-04-11','9999-12-31','Production',0,'DT102','Daily','350');");
conn.execute("insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education ,employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) values('MF0005','Maheshwarai ','Vijayakumar','Swaminathan','M','2001-05-19','No Formal Education','2024-04-11','9999-12-31','Administration',0,'DT103','Daily','200');");
conn.execute("insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education ,employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) values('MF0006','Shruthi ','Gupta','Agarwal','M','2002-08-14','No Formal Education','2024-04-11','9999-12-31','Administration',0,'DT104','Monthly','8000');");
conn.execute("insert into employee(employee_number,first_name,last_name,father_name,sex,date_of_birth,education ,employment_start_date,employment_end_date,department,leaves_per_month,primary_duty_code,salary_type_code,salary) values('MF0007','Richard ','John','Bennet','M','1999-09-22','No Formal Education','2024-04-11','9999-12-31','Human Resource',0,'DT104','Monthly','11000');");


conn.commit()

conn.close()
