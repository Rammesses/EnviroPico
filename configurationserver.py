import network
import socket

class ConfigurationServer:

    DEFAULT_PORT : int = 80

    def __init__(self, ip, port : int = DEFAULT_PORT, setup_mode : bool = True) -> None:
        
        self.ip_address = ip
        self.port = port
        self.setup_mode = setup_mode

    def run(self) -> None:

        addr = socket.getaddrinfo(self.ip_address, self.port)[0][-1]
        
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        
        print(f"Started webserver on {self.ip_address}:{self.port}.")
        
        # Listen for connections
        while True:
            try:
                cl, addr = s.accept()
                print('client connected from', addr)

                request = cl.recv(1024)
                print(request)

                request = str(request)

                if (request.find('POST /setup ')):
                    print('POST setup data!')
                    
                if (request.find('GET / ') or 
                    request.find('POST /setup ')):
                    response = self.get_page('index')
                else:
                    response = "Hello Pico"
                
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                cl.send(response)
                cl.close()
        
            except OSError as e:
                cl.close()
                print('connection closed')
    
    def get_page(self, page):
        if (self.setup_mode):
            page = open(f"web/setup.html", "r")
        else:
            page = open(f"web/{page}.html", "r")
        html = page.read()
        page.close()

        return html