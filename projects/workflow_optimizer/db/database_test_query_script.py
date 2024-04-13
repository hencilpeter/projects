import sqlite3

conn = sqlite3.connect('../data/marania_data.db')
print("Opened database successfully")
# conn.execute("delete from employee_duties;")
# conn.commit()
cursor = conn.execute("select * from employee_duties;")

column_names = [description[0] for description in cursor.description]
for row in cursor:
    for col_name in column_names:
        print("{} = {}".format(col_name, row[column_names.index(col_name)]))



conn.close()