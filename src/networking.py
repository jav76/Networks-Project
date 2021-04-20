import socket, threading, upnpy
import logging as log

class host: # host that receives connections and displays incoming messages
    def __init__(self):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ipPort = ("", 1111) # Elevated permissions required for ports 0-1024
        self.node.bind(self.ipPort)
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
        if self.connected == False:
            try:
                self.node.connect(self.ipPort)
                log.debug(f"Connected to {self.ipPort}")
                self.connected = True
            except:
                log.warning(f"Could not connect to {self.ipPort}")
                del self

    def send_msg(self, message):
        self.node.send(message.encode())


def portMapping():
    upnp = upnpy.UPnP()
    devs = upnp.discover()
    log.debug(f"UPnP devices: {devs}")
    dev = upnp.get_igd()
    dev.get_services()
    service = dev['WANPPPConnection.1']
    service.get_actions()
    service.AddPortMapping.get_input_arguments()
    service.AddPortMapping(
        NewRemoteHost='',
        NewExternalPort=1111,
        NewProtocol='TCP',
        NewInternalPort=1111,
        NewInternalClient='127.0.0.1',
        NewEnabled=1,
        NewPortMappingDescription='Test port mapping entry from UPnPy.',
        NewLeaseDuration=0
    )
