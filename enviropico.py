import uasyncio as asyncio
import binascii
import machine
import network

from configuration import Configuration

class EnviroPico:

    MACHINE_ID = binascii.hexlify(machine.unique_id()).decode('utf-8')
    DEFAULT_AP_SSID = f'EnviroPico_{MACHINE_ID}'

    def __init__(self):
        # export stuff here!
        __all__ = ["bootstrap"]
        return

    def bootstrap(self) -> None:
        print(f'Bootstrapping EnviroPico {self.MACHINE_ID}')
        try:
            asyncio.run(self.main())
        finally:
            asyncio.new_event_loop()

    async def main(self)-> None:

        config = Configuration()

        if (config.wifi.isValid()):
            print(f'Connecting to {config.wifi.ssid}...')
            await self.connect_to_wifi(config.wifi.ssid, config.wifi.password)
        else:
            print('No Wifi configuration - running in AP mode')
            await self.connect_as_ap()


    async def connect_as_ap(self) -> None:
        # Set up AP mode
        ap = network.WLAN(network.AP_IF)
        ap.config(ssid=self.DEFAULT_AP_SSID) 
        ap.active(True)

        while (not ap.active):
            pass

        print("Access point active")
        print(ap.ifconfig())

    async def connect_to_wifi(self, ssid : str, password : str) -> None:

        print(f'Connecting to {ssid}...')
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)

        # Wait for connect or fail
        max_wait : int = 10
        while (max_wait and not wlan.status() in { network.STAT_IDLE, network.STAT_CONNECTING } ):  # type: ignore
            max_wait -= 1  # type: ignore
            print('waiting for connection...')
            await asyncio.sleep(1)

        # Handle connection error
        if (wlan.status() != network.STAT_GOT_IP):  # type: ignore
            raise RuntimeError('WiFi connection failed')
        else:
            print(f'Connected to {ssid}.')
            print(wlan.ifconfig())