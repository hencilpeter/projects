import json


class ConfigReaderUtil:
    json_config = None

    @staticmethod
    def load_configuration(config_file_name):
        config_file_data = None
        with open(config_file_name, "r") as file:
            config_file_data = file.read()

        ConfigReaderUtil.json_config = json.loads(config_file_data)

    @staticmethod
    def get_config(configuration_name):
        return ConfigReaderUtil.json_config[configuration_name]
