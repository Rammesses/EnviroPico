# configuration helper classes

import binascii
import configparser
import machine

DEFAULT_CONFIG_FILE = "config.ini"
MACHINE_ID = binascii.hexlify(machine.unique_id()).decode('utf-8')

class WifiConfiguration:
    ssid : str
    password: str

    def __init__(self):
        self.ssid = ''
        self.password = ''

    def isValid(self) -> bool:
        return (not self.ssid == '')   # type: ignore

class Configuration:

    wifi : WifiConfiguration
    name : str = 'EnviroPico_{MACHINE_ID}'

    def __init__(self):
        self.wifi = WifiConfiguration()

    def load(self, configfile : str) -> None:
        parser = configparser.ConfigParser()
        parser.read(configfile)

        self.wifi.ssid = parser.get('Wifi', 'ssid')
        self.wifi.password = parser.get('Wifi', 'password')
        