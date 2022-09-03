import machine
import network
import socket
import uasyncio as asyncio

from machine import Pin
from picozero import pico_temp_sensor, pico_led
from time import sleep
from umqtt.simple import MQTTClient

# Basic config
unit_name = 'garage_environment_sensor'

# wlan config
wlan_ssid = '***********'
wlan_password = '************'

# MQTT config
mqtt_server = 'xxx.xxx.xxx.xxx'
mqtt_port = 0
mqtt_client_id = unit_name
mqtt_send_topic = f'devices/{unit_name}/events/'
mqtt_heartbeat_topic = f'devices/_all/heartbeat/'
mqtt_listen_topic = f'devices/{unit_name}/commands/#'

# hardware setup
led = Pin('LED', Pin.OUT)
internal_temp_sensor = machine.ADC(4)
internal_temp_sensor_conversion_factor = 3.3 / (65535)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

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
    
async def flash_led(period_ms):
    while True:
        led.on()
        await asyncio.sleep_ms(100)
        led.off()
        await asyncio.sleep_ms(period_ms)

async def report_sensor(mqtt_client, period_ms):
    while True:
        internal_temp_sensor_reading = internal_temp_sensor.read_u16() * internal_temp_sensor_conversion_factor
        internal_temperature = 27 - (internal_temp_sensor_reading - 0.706)/0.001721
        print(f'Internal temp sensor reported {internal_temperature}C')
        await asyncio.sleep_ms(period_ms)

async def report_heartbeat(mqtt_client, period_ms):
    while True:
        print('heartbeat...')
        mqtt_client.publish(mqtt_heartbeat_topic, f'{{"heartbeat": "{unit_name}"}}')
        await asyncio.sleep_ms(period_ms)
              
async def main():    
    wlan_client = await wlan_connect()
    mqtt_client = await mqtt_connect()
    
    tasks = (flash_led(2000), report_sensor(mqtt_client, 5000), report_heartbeat(mqtt_client, 30000))
    print('Running...')
    res = await asyncio.gather(*tasks)
    print(res)

asyncio.run(main())
