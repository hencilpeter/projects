from windows.window_main import MenuBar
from util.util_config_reader import UtilConfigReader


def load_configuration():
    UtilConfigReader.load_configuration("./data/app_config.json")


if __name__ == "__main__":
    # load configurations
    load_configuration()

    # main window
    menubar = MenuBar(0)
    menubar.MainLoop()
