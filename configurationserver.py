import network
import socket
import json
import uasyncio

CODE_200_OK : str = '200 OK'
CODE_404_NOTFOUND : str = '404 NOT FOUND'
CONTENT_TYPE_HTML : str = 'text/html'
CONTENT_TYPE_JSON : str = 'text/json'

class ConfigurationServer:

    DEFAULT_PORT : int = 80

    def __init__(self, ip, port : int = DEFAULT_PORT, setup_mode : bool = True) -> None:
        
        self.ip_address = ip
        self.port = port
        self.setup_mode = setup_mode

    def run(self):
        print(f'Starting webserver on {self.ip_address}:{self.port}')
        return uasyncio.start_server(self.serve, self.ip_address, self.port, backlog=100)

    async def serve(self, reader, writer):

        try:
            request = str(await reader.readline())
            print(f'Received request:\n{request}')

            response : str = ''
            responseCode : str = CODE_404_NOTFOUND
            contentType : str = CONTENT_TYPE_HTML

            if (request.find('POST /setup ') >= 0):
                print('POST setup data!')
                responseCode = CODE_200_OK

            elif (request.find('GET / ') >= 0):
                response = self.get_page('index')
                responseCode = CODE_200_OK

            elif (request.find('GET /api/details ') >= 0):
                response = self.get_details_json()
                responseCode = CODE_200_OK
                contentType = CONTENT_TYPE_JSON

            elif (request.find('GET /api/networks ') >= 0):
                response = self.get_networks_json()
                responseCode = CODE_200_OK
                contentType = CONTENT_TYPE_JSON

            elif (request.find('GET /api/sensors ') >= 0):
                response = self.get_sensors_json()
                responseCode = CODE_200_OK
                contentType = CONTENT_TYPE_JSON

            else:
                response = ""
                responseCode = "404 NOT FOUND"
            
            writer.write(f'HTTP/1.0 {responseCode}\r\nContent-type: {contentType}\r\n\r\n')
            writer.write(response)
            writer.write('\r\n\r\n')
            await writer.drain()

            print(f'Sent {len(response)} bytes.')

        except Exception as ex: 
            print(ex)
            pass # Let's just swallow any errors

        finally:
            reader.close()
            writer.close()

    def get_page(self, page) -> str:
        if (self.setup_mode):
            page = open(f"web/setup.html", "r")
        else:
            page = open(f"web/{page}.html", "r")
        html = page.read()
        page.close()

        return html

    def get_details_json(self) -> str:

        details = [
            { "name": "Board ID", "value" : "-board-id" },
            { "name": "Board Name", "value" : "-name-" },
            { "name": "Network", "value" : "-network-" },
            { "name": "IP Address", "value" : "172.16.0.1" }
        ]
        return json.dumps(details)

    def get_networks_json(self) -> str:

        networks = [
            "BT_123456",
            "VM-65431",
            "My Wifi Network",
            "Another Wifi Network",
            "DANGER, WILL ROBIMSON!"
        ]
        return json.dumps(networks);

    def get_sensors_json(self) -> str:

        sensors = [
            { "sensor_id": 1, "area": "Living Room", "temp": 19.8, "humidity": 65, "pin": 4 },
            { "sensor_id": 2, "area": "Kitchen", "temp": 21.6, "humidity": 66, "pin": 5 },
            { "sensor_id": 3, "area": "Bathroom", "temp": 23.0, "humidity": 97, "pin": 2 }
        ]
        return json.dumps(sensors)
