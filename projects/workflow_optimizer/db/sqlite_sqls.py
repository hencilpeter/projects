import sqlite3
from collections import defaultdict


class SqliteSqls:
    def __init__(self, db_file_name):
        self.conn = sqlite3.connect(db_file_name)

    def __del__(self):
        self.conn.close()

    def get_table_data(self, query):
        cursor_result = self.conn.execute(query)
        return cursor_result

    def execute_and_commit_sql(self, sql):
        self.conn.execute(sql)
        self.conn.commit()

    def executescript_and_commit_sql(self, sql):
        self.conn.executescript(sql)
        self.conn.commit()

    def get_record_count(self, sql):
        cursor_result = self.conn.execute(sql)
        return cursor_result.fetchone()[0]

    def get_single_column_list(self, table_name, column_name):
        sql = "select {} from {}".format(column_name, table_name)
        cursor_result = self.conn.execute(sql)
        column_names = [description[0] for description in cursor_result.description]
        result = []
        for row in cursor_result:
            for col_name in column_names:
                result.append(row[column_names.index(col_name)])

        return result

    def get_mnemonic_table_data(self, mnemonic_id_group):
        query = "select mnemonic_id, description from mnemonic_data where mnemonic_id_group == '{}';".format(
            mnemonic_id_group)
        cursor_mnemonic_data = self.get_table_data(query=query)
        dict_mnemonic_data = defaultdict(lambda: -1)

        for row in cursor_mnemonic_data:
            dict_mnemonic_data[row[0]] = row[1]

        return dict_mnemonic_data

    def get_mnemonic_table_data_as_list(self, mnemonic_id_group):
        mnemonic_table_data = self.get_mnemonic_table_data(mnemonic_id_group=mnemonic_id_group)
        result_list = []
        for key in mnemonic_table_data.keys():
            result_list.append(mnemonic_table_data[key])
        return result_list

    def get_query_result(self, query):
        pass

    def write_data(self, insert_statement):
        self.execute_and_commit_sql(insert_statement)

