import threading, sys
from pythonRSA import *
from networking import *
import logging as log


if __name__ == "__main__":
    log.basicConfig(filename='log.txt', encoding='utf-8', level=log.DEBUG)
    root = log.getLogger()
    root.setLevel(log.DEBUG)
    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(log.INFO)
    formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    log.debug("Hello networked world!")
    server = host()
    always_receive = threading.Thread(target=server.acceptConnections)
    always_receive.daemon = True
    always_receive.start()

    nodes = []
    currentNode = None

    genKeys(2048)

    """
    Current functionality:
    Create a new outgoing connection with /connect {ip} {port}
    This new connection is added to {nodes} if the connection is successful.
    /chat {ip} will set {currentNode} to an existing connection with matching ip if it exists
    After {currentNode} has been set, all inputs will be sent via that connection
    """
    while True:
        msg = input()
        if len(msg) > 0:
            if msg[0] == '/':

                if msg[1:8] == "connect": # /connect
                    ipStart = msg.find(" ")
                    portStart = msg.find(" ", ipStart + 1)
                    ip = -1
                    port = 1111
                    if ipStart != -1:
                        if portStart != -1:
                            ip = msg[ipStart + 1: portStart]
                            port = msg[portStart + 1:]
                        else:
                            ip = msg[ipStart + 1:]
                    try:
                        socket.inet_aton(ip)
                        log.debug(f"{(ip, port)}")
                    except socket.error:
                        log.warning("Invalid ip/port")
                        continue

                    newNode = connectionNode(ip, port)
                    if newNode.connected:
                        nodes.append(newNode)
                        log.info(f"Connected to {(ip, port)}")
                    else:
                        log.warning(f"Could not connect to {(ip, port)}")
                    log.debug(nodes)

                if msg[1:5] == "chat": # /chat
                    ipStart = msg.find(" ")
                    if ipStart != -1:
                        ip = msg[ipStart + 1:]
                        for i in nodes:
                            if i.ipPort[0] == ip:
                                currentNode = i
                                log.info(f"Now chatting with {(currentNode, i.ipPort)}")

            else:
                if currentNode:
                    currentNode.send_sms(msg)


