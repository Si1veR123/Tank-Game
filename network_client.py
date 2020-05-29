import socket, re


class Network:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = self.get_server_ip()
        self.port = int(input('Port: '))
        self.addr = (self.server, self.port)
        self.player = self.connect()

    def get_server_ip(self):
        while True:
            ip_selection = input('Enter ip or use default (d): ')
            if ip_selection == 'd':
                return '192.168.1.118'
            else:
                match = r'[0-9]{3}\.[0-9]{3}\.[0-9]{1}\.[0-9]{3}'
                valid = re.match(match, ip_selection)
                if valid:
                    return ip_selection
                else:
                    print('Invalid ip')

    def connect(self):
        while True:
            try:
                self.socket.connect(self.addr)
                return self.receive()
            except:
                print('Error Connecting')
                quit()

    def receive(self):
        return self.socket.recv(100).decode()

    def send(self, data: str):
        self.socket.send(data.encode())
