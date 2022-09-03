import json
import machine
import network
import socket
import uasyncio as asyncio

from machine import Pin
from picozero import pico_temp_sensor, pico_led
from time import sleep
from umqtt.simple import MQTTClient

class Device(dict):
    def __init__(self, identifiers, name, sw_version, model, manufacturer):
        super().__init__()

        self.name = name

        self["identifiers"] = identifiers
        self["name"] = name
        self["sw_version"] = sw_version
        self["model"] = model
        self["manufacturer"] = manufacturer
        
class Component:
    def __init__(self, name, read_function = None):
        self.component = name
        self.value_read_function = read_function

    def set_value_read_function(self, function):
        self.value_read_function = function
        
class Sensor(Component):
    def __init__(
        self,
        client: mqtt.Client,
        name,
        parent_device,
        unit_of_measurement,
        icon=None,
        topic_parent_level="",
        read_function = None
    ):
        super().__init__("sensor", read_function)

        self.client = client
        self.name = name
        self.parent_device = parent_device
        self.object_id = self.name.replace(" ", "_").lower()
        self.unit_of_measurement = unit_of_measurement
        self.icon = icon
        self.topic_parent_level = topic_parent_level
        self.topic = f"{self.parent_device.name}/{self.component}/{self.topic_parent_level}/{self.object_id}"
        self._send_config()
        
        self.last_value = None

    def _send_config(self):
        _config = {
            "~": self.topic,
            "name": self.name,
            "state_topic": "~/state",
            "unit_of_measurement": self.unit_of_measurement,
            "device": self.parent_device,
        }

        if self.icon:
            _config["icon"] = self.icon

        self.client.publish(
            f"{DISCOVERY_PREFIX}/{self.component}/{self.parent_device.name}/{self.object_id}/config",
            json.dumps(_config),
            retain=True,
        )

    
    def get_value(self):
        if self.last_value is None and self.value_read_function:
            self.last_value = self.value_read_function()
        return self.last_value
    
    def send(self, value=None, blocking=False):
        if value is None:
            if not self.value_read_function:
                raise ValueError("Set either value or value_read_function")

            publish_value = self.value_read_function()
        else:
            publish_value = value
            self.last_value = value

        self.client.publish(f"{self.topic}/state", str(publish_value))

# =============================================
# Now the real code!
# =============================================
            
# Basic config
device_type = 'environment_sensor'
device_location = 'garage'
unit_name = f'{device_location}_{device_type}'

# wlan config
wlan_ssid = '***********'
wlan_password = '***********'

# MQTT config
mqtt_server = 'xxx.xxx.xxx.xxx'
mqtt_port = 0
mqtt_client_id = unit_name
mqtt_send_topic = f'devices/{unit_name}/events/'
mqtt_heartbeat_topic = f'devices/_all/heartbeat/'
mqtt_listen_topic = f'devices/{unit_name}/commands/#'

# hardware setup
led = Pin('LED', Pin.OUT)
internal_temp_sensor_input = machine.ADC(4)
internal_temp_sensor_conversion_factor = 3.3 / (65535)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

# HomeAssistant setup
DISCOVERY_PREFIX = "homeassistant"
hass_device = Device(f'{unit_name}_001', unit_name, '220819-001', 'ES-PicoW', 'Perivor IoT Inc')

# Connect to WLAN
async def wlan_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wlan_ssid, wlan_password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        await asyncio.sleep_ms(1000)
    print(wlan.ifconfig())
    return wlan

# Connect to MQTT hub
async def mqtt_connect():
    client = MQTTClient(mqtt_client_id, mqtt_server, keepalive=3600)
    client.connect()
    print(f'Connected to IoT Hub MQTT Broker {mqtt_server} as {mqtt_client_id}...')
    return client

# Register devices with home assistant
async def homeassistant_connect(mqtt_client):
    
    internal_temp_sensor = Sensor(
        mqtt_client,
        "Temperature 1",
        parent_device=hass_device,
        unit_of_measurement="°C",
        topic_parent_level="internal",
        read_function = lambda : 27 - (internal_temp_sensor_input.read_u16() * internal_temp_sensor_conversion_factor - 0.706)/0.001721
    )

    return [ internal_temp_sensor ]

async def flash_led(period_ms):
    while True:
        led.on()
        await asyncio.sleep_ms(100)
        led.off()
        await asyncio.sleep_ms(period_ms)

async def report_sensors(sensors, period_ms):
    while True:
        for sensor in sensors:
            sensor_value = sensor.get_value()
            sensor.send()
        await asyncio.sleep_ms(period_ms)

async def report_heartbeat(mqtt_client, period_ms):
    while True:
        print('heartbeat...')
        mqtt_client.publish(mqtt_heartbeat_topic, f'{{"heartbeat": "{unit_name}"}}')
        await asyncio.sleep_ms(period_ms)
              
async def main():    
    wlan_client = await wlan_connect()
    mqtt_client = await mqtt_connect()
    sensors = await homeassistant_connect(mqtt_client)
    
    tasks = (flash_led(2000), report_sensors(sensors, 5000), report_heartbeat(mqtt_client, 30000))
    print('Running...')
    res = await asyncio.gather(*tasks)
    print(res)

asyncio.run(main())