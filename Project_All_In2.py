import socket
import threading
import select
import errno
import sys
import time
import os
from tqdm import tqdm


class App:
    IP = socket.gethostbyname(socket.gethostname())
    PORT = 9876
    Transfer = 4456

    def __init__(self, setting):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 9876
        self.Transfer = 4456
        self.setting = setting
        self.cancel = ["quit", "kill", "stop", "terminate"]
        self.query = ["ask"]
        self.send = ["send", "transfer"]
        self.files = {}

    def host_mode(self):
        host = socket.gethostbyname(socket.gethostname())
        port = 59000

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        storage = {}
        users = []
        clients = []

        def broadcast(message):
            for x in storage:
                storage[x].send(message)

        def query():
            print("Query call")
            report = ""
            for x in self.files:
                report = report + "Name: " + x + "  Owner: " + self.files[x] + "\n"
            broadcast(report.encode('utf-8'))

        def fileRequest(name):
            if name in storage:
                print("File found.\n File list: " + self.files.keys() + "\n")
                storage[name].send("Are you willing to share your file?".encode('utf-8'))
                response = storage[name].recv(1024).decode('utf-8')

            else:
                broadcast("File not found\n".encode('utf-8'))

        def register(name, sender):
            print("Register call")
            self.files.update({name: sender})

        def deregister(name, sender):
            print(name, sender)
            print("Deregister call")
            print(self.files[name])
            if sender == self.files[name]:
                del self.files[name]

        def privatemessage(name, pm, requestee):
            if name in storage:
                storage[name].send(pm.encode('utf-8'))
            else:
                storage[requestee].send("User not available".encode('utf-8'))

        def handle_client(client):
            while True:
                try:
                    message = client.recv(1024).decode('utf-8')
                    contents = message.split("_")
                    # if contents[1] in self.send:
                    #    message = "User has requested file transfer" + "_" + contents[0].replace(":", "")
                    #    broadcast(message.encode('utf-8'), 1)
                    if contents[1] in self.query:
                        contents[0] = contents[0].replace(":", "")
                        response = client.recv(1024).decode('utf-8')
                        search = response.split("_")
                        query()

                    elif contents[1] == "request":
                        client.send('Enter the name of the request target: '.encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        target = response.split("_")
                        fileRequest(target[1])

                    elif contents[1] == "private":
                        client.send('Who would you like to send a Private Message to?'.encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        target = response.split("_")
                        client.send('What would you like to say?'.encode('utf-8'))
                        pmess = client.recv(1024).decode('utf-8')
                        pm = pmess.split("_")
                        privatemessage(target[1], pm[1], contents[0])

                    elif contents[1] in self.cancel:
                        client.send('shutdown'.encode('utf-8'))

                    elif contents[1] == "register":
                        client.send("What is the filename?".encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        contents[0] = contents[0].replace(":", "")
                        fileinfo = response.split("_")
                        if fileinfo[1] == "":
                            print("Invalid response")
                        register(fileinfo[1], contents[0])

                    elif contents[1] == "deregister":
                        client.send("What is the filename?".encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        contents[0] = contents[0].replace(":", "")
                        fileinfo = response.split("_")
                        if fileinfo[1] == "":
                            print("Invalid response")
                        deregister(fileinfo[1], contents[0])

                    else:
                        message = contents[0] + " " + contents[1]
                        broadcast(message.encode('utf-8'))

                except:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    user = users[index]
                    del storage[user]
                    broadcast(f'{user} has disconnected!'.encode('utf-8'))
                    users.remove(user)
                    break

        def receive():
            while True:
                print('Server is active [+]')
                client, address = server.accept()
                print(f'Connection active with {str(address)}')
                client.send('alias?'.encode('utf-8'))
                user = client.recv(1024).decode('utf-8')
                users.append(user)
                clients.append(client)
                storage.update({user: client})
                print(str(f"The username of this client is {user}"))
                broadcast(f"User [{user}] has connected".encode('utf-8'))
                client.send("\nConnection live!".encode('utf-8'))
                thread = threading.Thread(target=handle_client, args=(client,))
                thread.start()

        receive()

    def client_mode(self):
        IP = socket.gethostbyname(socket.gethostname())
        user = input('Create a username: ')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((IP, 59000))

        def client_receive():
            while True:
                try:
                    message = client.recv(1024).decode('utf-8')
                    if message == "alias?":
                        client.send(user.encode('utf-8'))
                    elif message == "shutdown":
                        sys.exit()
                    else:
                        print(message)
                except:
                    print("Error")
                    client.close()
                    break

        def client_send():
            while True:
                # data = f"{name}_{size}"
                text = input("")
                message = f'{user}:_{text}'
                client.send(message.encode('utf-8'))

        receive_thread = threading.Thread(target=client_receive)
        receive_thread.start()

        send_thread = threading.Thread(target=client_send)
        send_thread.start()

    def get_file(self, sender):
        data = sender.recv(1024).decode("utf-8")
        contents = data.split("_")
        name = contents[0]
        size = int(contents[1])

        #bar = tqdm(range(size), f"Receiving {name}", unit="B", unit_scale=True, unit_divisor=2048)
        with open(f"recv_{name}", "w") as f:
            while True:
                data = sender.recv(2048).decode("utf-8")

                if not data:
                    break

                f.write(data)
                #bar.update(len(data))

    def send_file(self, target):
        while True:
            name = input("\nInput file name: \n")
            if name in self.files:
                print("File found.")
                break
            else:
                print("File not found.\nFile list: ", list(self.files.keys()))

        size = os.path.getsize(name)
        data = f"{name}_{size}"
        target.send(data.encode("utf-8"))

        #bar = tqdm(range(size), f"Sending {name}", unit="B", unit_scale=True, unit_divisor=2048)
        with open(name, "r") as f:
            while True:
                data = f.read(2048)
                if not data:
                    break
                target.send(data.encode("utf-8"))
                #bar.update(len(data))

    def data_protocol(self):
        if self.setting == "host":
            receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            receiver.bind(('', self.Transfer))
            print("Host IP:", self.IP)
            receiver.listen()
            print("Awaiting Sender Connection...")

            sender, address = receiver.accept()
            print(f"Sender connected from {address[0]}:{address[1]}")
            self.get_file(sender)

            sender.close()
            receiver.close()
            time.sleep(10)

        if self.setting == "client":
            sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sender.connect((self.IP, self.Transfer))

            self.send_file(sender)

            sender.close()
            time.sleep(10)

    def fileList(self):
        all_files = os.listdir()
        txt_files = filter(lambda x: x[-4:] == '.txt', all_files)
        for x in txt_files:
            self.files.update({x: os.path.getsize(x)})

    def Startup(self, x):
        options = ["host", "join", "quit"]
        fileshare = input("Send/receive files? [yes/no]\n").lower().strip()

        if x in options:
            if x == "host" and fileshare == "yes":
                self.setting = "host"
                self.data_protocol()
                self.host_mode()
            elif x == "join" and fileshare == "yes":
                self.fileList()
                self.setting = "client"
                self.data_protocol()
                self.client_mode()
            if x == "host" and fileshare == "no":
                self.setting = "host"
                self.host_mode()
            elif x == "join" and fileshare == "no":
                self.setting = "client"
                self.client_mode()
            elif x == "quit":
                return
        else:
            y = input("Host a connection or join a connect? [host/join/quit]\n").lower().strip()
            self.Startup(y)


startup = input("Host a connection or join a connection? [host/join/quit]\n").lower().strip()
creation = App("created")
creation.Startup(startup)
