from datetime import datetime


class CommonUtil:

    @staticmethod
    def get_unique_database_name(database_name_prefix="Automation_Test_DB_"):
        timestamp_now = datetime.now()
        return database_name_prefix + str(timestamp_now.strftime("%Y%m%d%H%M%S"))
