import socket, threading, upnpy, time, json, codecs
import logging as log
from pythonRSA import *

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
            log.debug(f"New connection {newConnection[1]} accepted")
            ipPort = newConnection[1]
            JSONdata = readJSON()
            entryExists = False
            for hosts in JSONdata["hosts"]:
                if hosts["ip"] == ipPort[0] and hosts["direction"] == "incoming":
                    entryExists = True
                    log.debug(f"JSON entry for {ipPort} already exists")
                    break
            if not entryExists:
                hostname = ""
                try:
                    hostname = socket.gethostbyaddr(ipPort[0])[0]
                except:
                    pass
                newEntry = {
                    "ip": ipPort[0],
                    "name": "",
                    "hostName": hostname,
                    "port": ipPort[1],
                    "pubKey": "",
                    "direction": "incoming"
                }
                JSONdata["hosts"].append(newEntry)
                writeJSON(JSONdata)
                log.debug(f"Wrote new JSON entry {newEntry}")

            self.connections.append(newConnection)
            always_receive = threading.Thread(target=self.receive_msg, args=[newConnection])
            always_receive.start()

    def receive_msg(self, conn):
        ipPort = conn[1]
        hostname = ""
        try:
            hostname = socket.gethostbyaddr(ipPort[0])[0]
        except:
            pass
        while True:
            data = conn[0].recv(2048).decode()
            args = data.split()
            encrypted = False
            if "ENCRYPTED:" in args:
                encryptStart = args.index("ENCRYPTED:")
                encrypted = eval(args[encryptStart + 1])
            if "MSG:" in args:
                msgStart = args.index("MSG:")

                timestamp = time.asctime().split()[3]
                if encrypted:
                    msg = "".join(args[msgStart + 1:])
                    msgEnc = codecs.decode(msg, "hex")
                    msgEncHex = msg
                    msg = decryptFromFile(msgEnc)
                    if msg is not None:
                        print(f"[{timestamp}] {hostname}: {msg}")
                    else:
                        print(f"[{timestamp}] {hostname}: {msgEncHex}")
                        print(f"[{timestamp}] {hostname}: {msgEnc}")
                else:
                    msgStart2 = data.find("MSG:")
                    msg = data[msgStart2 + 4:]
                    print(f"[{timestamp}] {hostname}: {msg}")

                log.debug(f"Received: {data}   From: {hostname} {ipPort}")



class connectionNode: # For outgoing connections
    def __init__(self, ip, port, encrypted = False):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipPort = (ip, int(port))
        self.connected = False
        self.encrypted = encrypted
        try:
            self.node.connect(self.ipPort)
            log.debug(f"Connected to {self.ipPort}")
            self.connected = True
        except:
            log.warning(f"Could not connect to {self.ipPort}")
            del self

    def send_msg(self, message):
        self.node.send(message.encode())

    def send_bytes(self, message):
        self.node.send(message)

def readJSON():
    try:
        with open("../known_hosts.json", mode="r") as f:
            data = json.loads(f.read())
            f.close()
            return data
    except FileNotFoundError:
        newDict = {
            "hosts": []
        }
        writeJSON(newDict)
        return readJSON()
    except Exception as e:
        log.error(f"Could not read JSON file {e}")
        return None

def writeJSON(outText):
    with open("../known_hosts.json", mode="w") as f:
        json.dump(outText, f, indent=4)
        f.close()
    return

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
