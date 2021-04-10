import socket, threading
import logging as log

class host: # host that receives connections and displays incoming messages
    def __init__(self):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ipPort = ("", 1111) # Elevated permissions required for ports 0-1024
        self.node.bind(ipPort)
        self.connections = []
        log.info(f"host socket started on {socket.gethostbyname(socket.gethostname())}")

    def acceptConnections(self):
        while True:
            self.node.listen(5)
            newConnection = self.node.accept() # Blocks until accepting a new connection
            log.debug(f"New connection {newConnection} accepted")
            self.connections.append(newConnection)
            always_receive = threading.Thread(target=self.receive_msg, args=[newConnection])
            always_receive.start()

    def receive_msg(self, conn):
        while True:
            data = conn[0].recv(1024).decode()
            print(data)
            log.debug(f"Received: {data}   From: {conn}")


class connectionNode: # For outgoing connections
    def __init__(self, ip, port):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipPort = (ip, int(port))
        self.connected = False
        try:
            self.node.connect(self.ipPort)
            log.debug(f"Connected to {self.ipPort}")
            self.connected = True
        except:
            log.warning(f"Could not connect to {self.ipPort}")
            del self

    def send_sms(self, message):
        self.node.send(message.encode())

    def main(self):
        while True:
            message = input()
            self.send_sms(message)