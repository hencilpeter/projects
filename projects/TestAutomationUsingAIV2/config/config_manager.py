import yaml


class ConfigurationManager:
    config_data = None

    def __init__(self):
        pass

    @staticmethod
    def load_configuration(config_file):
        # load the configuration
        ConfigurationManager.config_data = ConfigurationManager.get_configuration(config_file=config_file)

    @staticmethod
    def get_configuration(config_file):
        config_data = None
        try:
            with open(config_file, 'r') as file:
                config_data = yaml.safe_load(file)
        except IOError as error:
            print("Unable to read the file. exception : {}".format(error))

        return config_data

    @staticmethod
    def get_sql_server_config(config_name):
        return ConfigurationManager.config_data["sql_server_database"][config_name]

    @staticmethod
    def get_common_config(config_name):
        return ConfigurationManager.config_data["common"][config_name]

    @staticmethod
    def get_processing_order():
        return ConfigurationManager.config_data["processing_order"]

