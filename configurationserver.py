import network
import socket

import uasyncio

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
            request = await reader.readline()
            print(f'Received request:\n{request}')

            request = str(request)

            if (request.find('POST /setup ') >= 0):
                print('POST setup data!')
                
            if (request.find('GET / ') >- 0 or 
                request.find('POST /setup ') >= 0):
                response = self.get_page('index')
            else:
                response = "Hello Pico"
            
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write(response)
            await writer.drain()

            print(f'Sent {len(response)} bytes.')

        except Exception as ex: 
            print(ex)
            pass # Let's just swallow any errors

        finally:
            reader.close()
            writer.close()

    def get_page(self, page):
        if (self.setup_mode):
            page = open(f"web/setup.html", "r")
        else:
            page = open(f"web/{page}.html", "r")
        html = page.read()
        page.close()

        return html