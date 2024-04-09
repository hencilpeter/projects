import sqlite3

conn = sqlite3.connect('../data/marania_data.db')
print("Opened database successfully")

cursor = conn.execute("select * from address;")

column_names = [description[0] for description in cursor.description]
for row in cursor:
    for col_name in column_names:
        print("{} = {}".format(col_name, row[column_names.index(col_name)]))



conn.close()