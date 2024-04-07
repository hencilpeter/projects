import json


class UtilConfigReader:
    def __init__(self):
        self.dict_app_config = None

    @staticmethod
    def load_configuration(_config_file_name):
        config_file_data = None
        with open(_config_file_name, "r") as file:
            config_file_data = file.read()

        UtilConfigReader.dict_app_config = json.loads(config_file_data)

    @staticmethod
    def get_application_config(configuration_name):
        return UtilConfigReader.json_config[configuration_name]
