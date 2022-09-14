# LED flash code support
import uasyncio as asyncio
from machine import Pin

FLASH_AP = '.- .--.'
FLASH_IF = '.. ..-.'
FLASH_MQTT = '-- --.- - -'
FLASH_RUN = '.-. ..- -.'
FLASH_OK = '--- -.-'
FLASH_BAD = '-... .- -..'

FLASHMODE_NONE = 0
FLASHMODE_PULSE = 1
FLASHMODE_PATTERN = 2

class Flasher:

    def __init__(self) -> None:
        self.led = Pin('LED', Pin.OUT)
        self.mode = FLASHMODE_PULSE
        self.period = 1000

    async def run(self) -> None:
        while (True):

            if (self.mode == FLASHMODE_NONE):  # type: ignore
                self.led.off()

            if (self.mode == FLASHMODE_PULSE):  # type: ignore
                self.led.toggle()

            if (self.mode == FLASHMODE_PATTERN):  # type: ignore
                # TODO Flash the pattern
                self.led.on()
                pass

            await asyncio.sleep_ms(self.period)

    def set_pattern(self, pattern : str) -> None:
        self.pattern = pattern
        self.mode = FLASHMODE_PATTERN

    def set_pulse(self, period : int) -> None:
        self.period = period
        self.mode = FLASHMODE_PULSE
