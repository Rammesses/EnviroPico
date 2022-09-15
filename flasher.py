# LED flash code support
import uasyncio as asyncio
from machine import Pin

FLASHMODE_NONE = 0
FLASHMODE_PULSE = 1
FLASHMODE_PATTERN = 2
FLASHMODE_SOLID = 3

MORSE_DOT_PERIOD = 200
MORSE_DASH_PERIOD = 400
MORSE_SPACE_PERIOD = 400
MORSE_GAP_PERIOD = 200
class Flasher:

    def __init__(self) -> None:
        self.led = Pin('LED', Pin.OUT)
        self.mode = FLASHMODE_PULSE
        self.period = 1000

    async def run(self) -> None:
        while (True):

            if (self.mode == FLASHMODE_NONE):  # type: ignore
                self.led.off()

            if (self.mode == FLASHMODE_SOLID):
                self.led.on()

            if (self.mode == FLASHMODE_PULSE):  # type: ignore
                self.led.toggle()

            if (self.mode == FLASHMODE_PATTERN):  # type: ignore
                await self.show_pattern(self.pattern)

            await asyncio.sleep_ms(self.period)

    def set_pattern(self, pattern : str) -> None:
        self.pattern = pattern
        self.mode = FLASHMODE_PATTERN

    def set_pulse(self, period : int) -> None:
        self.period = period
        self.mode = FLASHMODE_PULSE

    async def show_pattern(self, pattern : str) -> None:
        for c in pattern:
            if (c == '.'):
                self.led.on()
                await asyncio.sleep_ms(MORSE_DOT_PERIOD)
                self.led.off()

            if (c == '-'):
                self.led.on()
                await asyncio.sleep_ms(MORSE_DASH_PERIOD)
                self.led.off()

            if (c == ' '):
                self.led.off()
                await asyncio.sleep_ms(MORSE_SPACE_PERIOD)
            
            await asyncio.sleep_ms(MORSE_GAP_PERIOD)