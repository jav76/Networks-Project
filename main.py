import socket, threading, time


class host: # host that receives connections and displays incoming messages
    def __init__(self):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ipPort = ("", 111)
        self.node.bind(ipPort)
        self.connections = []
        print(f"host socket started on {socket.gethostbyname(socket.gethostname())}")

    def acceptConnections(self):
        while True:
            self.node.listen(5)
            newConnection = self.node.accept() # Blocks until accepting a new connection
            print(f"New connection {newConnection} accepted")
            self.connections.append(newConnection)
            always_receive = threading.Thread(target=self.receive_sms, args=[newConnection])
            always_receive.start()

    def receive_sms(self, conn):
        while True:
            data = conn[0].recv(1024).decode()
            print(f"Received: {data}   From: {conn}")


class connectionNode: # For outgoing connections
    def __init__(self, ip, port):
        self.node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipPort = (ip, int(port))
        self.connected = False
        try:
            self.node.connect(self.ipPort)
            print(f"Connected to {self.ipPort}")
            self.connected = True
        except:
            print(f"Could not connect to {self.ipPort}")
            del self

    def send_sms(self, message):
        self.node.send(message.encode())

    def main(self):
        while True:
            message = input()
            self.send_sms(message)




if __name__ == "__main__":
    print("Hello networked world!")
    server = host()
    always_receive = threading.Thread(target=server.acceptConnections)
    always_receive.daemon = True
    always_receive.start()

    nodes = []
    currentNode = None

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
                    port = 22
                    if ipStart != -1:
                        if portStart != -1:
                            ip = msg[ipStart + 1: portStart]
                            port = msg[portStart + 1:]
                        else:
                            ip = msg[ipStart + 1:]
                    try:
                        socket.inet_aton(ip)
                        print(f"{(ip, port)}")
                    except socket.error:
                        print("Invalid ip/port")
                        continue

                    newNode = connectionNode(ip, port)
                    if newNode.connected:
                        nodes.append(newNode)
                        newNode.send_sms("test message")
                    print(nodes)

                if msg[1:5] == "chat": # /chat
                    ipStart = msg.find(" ")
                    if ipStart != -1:
                        ip = msg[ipStart + 1:]
                        for i in nodes:
                            if i.ipPort[0] == ip:
                                currentNode = i
                                print(f"Now chatting with {(currentNode, i.ipPort)}")

            else:
                if currentNode:
                    currentNode.send_sms(msg)


