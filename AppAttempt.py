import socket
import select
import errno
import sys
import time
import os
from tqdm import tqdm


class App:
    IP = socket.gethostbyname(socket.gethostname())
    PORT = 9876

    TRANSFERPORT = 4456
    ADDR = (IP, TRANSFERPORT)

    def __init__(self,setting):
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 9876
        self.setting = setting

    def get_file(self):
            data = client_socket.recv(1024).decode("utf-8")
            item = data.split("_")
            FILENAME = item[0]
            FILESIZE = int(item[1])

            bar = tqdm(range(FILESIZE), f"Receiving {FILENAME}", unit="B", unit_scale=True,
                       unit_divisor=1024)
            with open(f"recv_{FILENAME}", "w") as f:
                while True:
                    data = client_socket.recv(1024).decode("utf-8")

                    if not data:
                        break

                    f.write(data)
                    bar.update(len(data))

    def send_file(self):
        FILENAME = input("Input file name:")
        FILESIZE = os.path.getsize(FILENAME)

        data = f"{FILENAME}_{FILESIZE}"
        client_socket.send(data.encode("utf-8"))

        bar = tqdm(range(FILESIZE), f"Sending {FILENAME}", unit="B", unit_scale=True, unit_divisor=1024)

        with open(FILENAME, "r") as f:
            while True:
                data = f.read(800000)
                if not data:
                    break
                client_socket.send(data.encode("utf-8"))
                bar.update(len(data))
    def datasend(self):
    def HostFunctions(self):
        global setting
        setting = "Host"
        HEADER_LENGTH = 10
        # IP = "127.0.0.1"
        # PORT = 1234

        IP = App.IP
        PORT = App.PORT

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((IP, PORT))

        server_socket.listen()
        print("[+] Listening...")
        sockets_list = [server_socket]

        clients = {}



        def receive_message(client_socket):
            try:
                message_header = client_socket.recv(HEADER_LENGTH)

                if not len(message_header):
                    return False

                message_length = int(message_header.decode("utf-8").strip())
                return {"header": message_header, "data": client_socket.recv(message_length)}

            except:
                return False

        while True:
            try:
                read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

                for notified_socket in read_sockets:
                    if notified_socket == server_socket:
                        client_socket, client_address = server_socket.accept()

                        user = receive_message(client_socket)
                        if user is False:
                            continue
                        sockets_list.append(client_socket)

                        clients[client_socket] = user

                        print(
                            f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

                    else:
                        message = receive_message(notified_socket)

                        if message is False:
                            print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                            sockets_list.remove(notified_socket)
                            del clients[notified_socket]
                            continue

                        user = clients[notified_socket]
                        print(
                            f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

                        if message['data'].decode('utf-8') == "testing":
                            print("test success")
                            # rudimentary test showing interalized function calls can be made possible through decoding
                            # can be fleshed out to include customizable ip/port input without much difficulty, this is just a
                            # baseline

                        if message['data'].decode('utf-8') == "quit":
                            client_socket.shutdown(socket.SHUT_RDWR)
                            client_socket.close()

                        if message['data'].decode('utf-8') == "swap":
                            server_socket.close()

                        if message['data'].decode('utf-8') == "send":
                            filetransfer()

                        for client_socket in clients:
                            if client_socket != notified_socket:
                                client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                for notified_socket in exception_sockets:
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]

            except Exception as e:
                break
                #sys.exit("Connection Termination Request Accepted from Peer")
        time.sleep(15)
        self.ClientFunctions()




    def ClientFunctions(self):
        HEADER_LENGTH = 10
        global setting
        setting = "Client"
        # IP = "127.0.0.1"
        # PORT = 1234

        IP = App.IP
        PORT = App.PORT

        # my_user = input("Username:\n")
        my_user = "Client"

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        client_socket.setblocking(False)

        username = my_user.encode("utf-8")
        username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
        client_socket.send(username_header + username)

        while True:
            message = input(f"{my_user} > ")

            if message == "kill" or message == "close" or message == "quit":
                message = message.encode("utf-8")
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)
                sys.exit("Connection terminated by own user")

            if message == "swap" or message == "switch":
                message = message.encode("utf-8")
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)
                time.sleep(10)
                self.HostFunctions()

            if message == "send":
                message = (message).encode("utf-8")
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)
                file_transfer()

            if message == message:
                message = str(message).encode("utf-8")
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
                client_socket.send(message_header + message)

            try:
                while True:
                    # receive messages from other connections
                    username_header = client_socket.recv(HEADER_LENGTH)
                    if not len(username_header):
                        print("Connection closed by the host")
                        self.HostFunctions()

                    username_length = int(username_header.decode("utf-8").strip())
                    username = client_socket.recv(username_length).decode("utf-8")

                    message_header = client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode("utf-8").strip())
                    message = client_socket.recv(message_length).decode("utf-8")

                    print(f"{username} > {message}")

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('reading error', str(e))
                    sys.exit()
                continue

            except Exception as e:
                print('General error', str(e))
                sys.exit()

    def Startup(self, x):
        options = ["host", "join", "quit"]
        if x in options:
            if x == "host":
                creation.HostFunctions()
                print(creation.setting)
            elif x == "join":
                creation.ClientFunctions()
            elif x == "quit":
                return
        else:
            y = input("Host a connection or join a connect? [host/join/quit]\n").lower().strip()
            self.Startup(y)




startup = input("Host a connection or join a connect? [host/join/quit]\n").lower().strip()
creation = App(startup)
creation.Startup(startup)