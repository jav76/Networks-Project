import threading, sys, codecs
from pythonRSA import *
from networking import *
import logging as log

if __name__ == "__main__":
    log.basicConfig(filename='../log.txt', level=log.DEBUG)
    root = log.getLogger()
    root.setLevel(log.DEBUG)
    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(log.DEBUG)
    formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    try:
        portMapping()
    except Exception as e:
        log.warning(f"Could not start UPnP: {e}")
    log.debug("Hello networked world!")
    server = host()
    always_receive = threading.Thread(target=server.acceptConnections)
    always_receive.daemon = True
    always_receive.start()

    nodes = []
    currentNode = None

    """
    Current functionality:
    /chat {ip} will set {currentNode} to an existing connection with matching ip if it exists, or create a new connection otherwise
    After {currentNode} has been set, all inputs will be sent via that connection
    """
    while True:
        msg = input()
        if len(msg) > 0:
            if msg[0] == '/':

                if msg[1:5] == "chat": # /chat
                    args = msg[6:].split(" ")
                    name = args[0]
                    ip = args[0]
                    port = 1111
                    connected = False
                    if len(args) > 1:
                        port = args[1]
                    ipPort = (ip, port)

                    for i in nodes:
                        if i.ipPort[0] == ip:
                            currentNode = i
                            log.info(f"Now chatting with {(currentNode, i.ipPort)}")
                            connected = True

                    if not connected:
                        try:
                            socket.inet_aton(ip)
                            log.debug(f"{(ip, port)}")
                        except socket.error:
                            log.warning("Invalid ip/port")
                            continue
                        except Exception as e:
                            log.error(e)
                            continue

                        newNode = connectionNode(ip, port)
                        if newNode.connected:
                            nodes.append(newNode)
                            log.info(f"Connected to {(ip, port)}")
                            currentNode = newNode
                            log.info(f"Now chatting with {(currentNode, ipPort)}")
                            JSONdata = readJSON()
                            entryExists = False
                            for hosts in JSONdata["hosts"]:
                                if hosts["ip"] == ip and hosts["port"] == port and hosts["direction"] == "outgoing":
                                    entryExists = True
                                    log.debug(f"JSON entry for {ip} already exists.")
                                    break
                            if not entryExists:
                                hostname = ""
                                try:
                                    hostname = socket.gethostbyaddr(ip)[0]
                                except:
                                    pass
                                newEntry = {
                                    "ip" : ip,
                                    "name" : "",
                                    "hostName" : hostname,
                                    "port" : port,
                                    "pubKey" : "",
                                    "direction" : "outgoing"
                                }
                                JSONdata["hosts"].append(newEntry)
                                writeJSON(JSONdata)
                                log.debug(f"Wrote new JSON entry {newEntry}")
                            connected = True

                    log.debug(nodes)

                if msg[1:7] == "keygen": #/keygen
                    args = msg[8:].split(" ")
                    size = 4096
                    if args[0].isnumeric():
                        size = args[0]
                    genKeys(int(size))

                if msg[1:8] == "encrypt": #/encrypt
                    if currentNode:
                        if currentNode.encrypted:
                            currentNode.encrypted = False
                        else:
                            currentNode.encrypted = True

            else:
                if currentNode:
                    header = [
                        f"ENCRYPTED: {currentNode.encrypted} ",
                        f"MSG: "
                    ]
                    if currentNode.encrypted:
                        pubKey = ""
                        JSONdata = readJSON()
                        entryExists = False
                        for hosts in JSONdata["hosts"]:
                            if hosts["ip"] == currentNode.ipPort[0] and hosts["direction"] == "outgoing":
                                pubKey = hosts["pubKey"]
                                break
                        if len(pubKey) > 0:
                            encryptedMsg = encryptFromFile(msg, key = pubKey)
                            if encryptedMsg is not None:
                                msg = "".join(header) + str(codecs.encode(encryptedMsg, "hex").upper(), "utf-8")
                            else:
                                msg = "".join(header)
                        else:
                            print(f"No pubkey key for {currentNode.ipPort} exists")
                            continue

                        currentNode.send_msg(msg)
                    else:
                        msg = "".join(header) + msg
                        currentNode.send_msg(msg)
                    log.debug(f"Sent {msg} to {currentNode.ipPort}")


