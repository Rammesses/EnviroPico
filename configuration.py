# configuration helper classes

DEFAULT_CONFIG_FILE = "config.ini"

class WifiConfiguration:
    ssid : str
    password: str

    def __init__(self):
        self.ssid = ''
        self.password = ''

    def isValid(self) -> bool:
        return False

class Configuration:

    wifi : WifiConfiguration

    def __init__(self):
        self.wifi = WifiConfiguration()