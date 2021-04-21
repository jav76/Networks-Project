import threading, sys
from pythonRSA import *
from networking import *
import logging as log

if __name__ == "__main__":
    log.basicConfig(filename='log.txt', level=log.DEBUG)
    root = log.getLogger()
    root.setLevel(log.DEBUG)
    handler = log.StreamHandler(sys.stdout)
    handler.setLevel(log.DEBUG)
    formatter = log.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    """ Encryption demo:
    teststr = "testing asdasdfasdfgdfghdfghdfghdfghdfghdfghdfghdfghdfghdfaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaghdfghdfghdfghdfghfasdfasdfasdfasfdf"
    pub, priv = genKeys(4096)
    enc = encrypt(teststr, pub)
    print(enc)
    print(decrypt(enc, priv))
    """

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
                        if i[0].ipPort[0] == ip or i[1] == name:
                            currentNode = i
                            log.info(f"Now chatting with {(currentNode, i[0].ipPort)}")
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
                            nodes.append((newNode, None))
                            log.info(f"Connected to {(ip, port)}")
                            currentNode = newNode
                            log.info(f"Now chatting with {(currentNode, ipPort)}")
                            connected = True

                    log.debug(nodes)

                if msg[1:7] == "keygen": #/keygen
                    args = msg[8:].split(" ")
                    size = 1024
                    if args[0].isnumeric():
                        size = args[0]
                    genKeys(int(size))

            else:
                if currentNode:
                    currentNode.send_msg(msg)


