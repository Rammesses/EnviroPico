import uasyncio as asyncio
import configuration
import network
import flasher

from configuration import Configuration
from configurationserver import ConfigurationServer

WIFI_MODE_UNKNOWN = 0
WIFI_MODE_CLIENT = 1
WIFI_MODE_ACCESSPOINT = 2

FLASH_AP = '.- .--.'
FLASH_IF = '.. ..-.'
FLASH_MQTT = '-- --.- - -'
FLASH_WS = '.-- ...'
FLASH_OK = '--- -.-'
FLASH_BAD = '-... .- -..'
FLASH_CFG = '\'-.-. ..-. --.'

class EnviroPico:

    DEFAULT_AP_SSID = f'EnviroPico_{configuration.MACHINE_ID}'
    DEFAULT_AP_PWD = 'EnviroPico'

    wifiMode = WIFI_MODE_UNKNOWN

    def __init__(self):
        # export stuff here!
        __all__ = ["bootstrap"]
        self.flasher = flasher.Flasher()
        return

    def bootstrap(self) -> None:
        print(f'Bootstrapping EnviroPico {configuration.MACHINE_ID}')
        try:
            asyncio.run(self.main())
        finally:
            asyncio.new_event_loop()

    async def main(self)-> None:

        flasher = asyncio.create_task(self.flasher.run())

        config = Configuration()
        self.flasher.set_pattern(FLASH_CFG)
        config.load(configuration.DEFAULT_CONFIG_FILE)

        wlan : network.WLAN = None  # type: ignore
        
        if (config.wifi.isValid()):
            self.flasher.set_pattern(FLASH_IF)
            wlan = await self.connect_to_wifi(config.wifi.ssid, config.wifi.password)
        
        if (wlan == None or  # type: ignore
            wlan.status() != network.STAT_GOT_IP):  # type: ignore
            print('No Wifi configuration - running in AP mode')
            self.flasher.set_pattern(FLASH_AP)
            wlan = await self.connect_as_ap()

        print(wlan.ifconfig())

        self.flasher.set_pattern(FLASH_WS)

        (ip, subnet, gateway, dns) = wlan.ifconfig()
        configServer = ConfigurationServer(ip, ConfigurationServer.DEFAULT_PORT, self.isSetupMode())

        webserver = asyncio.create_task(configServer.run())

        self.flasher.set_pulse(1000)

        await asyncio.gather(
            webserver,
            flasher)
        
    async def connect_as_ap(self) -> network.WLAN:
        # Set up AP mode

        ap = network.WLAN(network.AP_IF)
        ap.config(ssid=self.DEFAULT_AP_SSID, key=self.DEFAULT_AP_PWD) 
        ap.active(True)

        while (not ap.active):
            pass

        print("Access point active")

        self.wifiMode = WIFI_MODE_ACCESSPOINT

        return ap

    async def connect_to_wifi(self, ssid : str, password : str) -> network.WLAN:

        print(f'Connecting to {ssid}...')
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)

        # Wait for connect or fail
        max_wait : int = 10
        print('Waiting for connection.', end='')
        while (max_wait):
            if (wlan.status() in {network.STAT_IDLE, network.STAT_CONNECTING }):   # type: ignore
                break
            max_wait -= 1  # type: ignore
            print(f'.', end='')
            await asyncio.sleep(1)

        # Handle connection error
        if (wlan.status() != network.STAT_GOT_IP):  # type: ignore
            raise RuntimeError('WiFi connection failed')
        else:
            print(f' Connected.')

        self.wifiMode = WIFI_MODE_CLIENT
        return wlan

    def isSetupMode(self):
        return (not self.wifiMode == WIFI_MODE_CLIENT)   # type: ignore