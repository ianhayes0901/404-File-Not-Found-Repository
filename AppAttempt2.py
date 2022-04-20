import socket 
import select
import errno 
import sys


def ClientFunctions():
    HEADER_LENGTH = 10
    IP = "127.0.0.1"
    PORT = 1234 

    my_user = input("Username:\n")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP,PORT))
    client_socket.setblocking(False)

    username = my_user.encode("utf-8")
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(username_header+username)

    while True:
        message = input(f"{my_user} > ")

        if message: 
            message = message.encode("uft-8")
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
            client_socket.send(message_header + message)
        
        try:
            while True:
                #receive messages from other connections
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("connection closed by the host")
                    sys.exit()
                
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
            print('General error',str(e))
            sys.exit()
            
def HostFunctions():
    HEADER_LENGTH = 10 
    IP = "127.0.0.1"
    PORT = 1234

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((IP, PORT))

    server_socket.listen()

    sockets_list = [server_socket]

    clients = {}


    def receive_message(client_socket):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            
            if not len(message_header):
                return False

            message_length = int(message_header.decode("utf-8").strip())
            return{"header": message_header, "data": client_socket.recv(message_length)}

        except:
            return False  

    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()

                user = receive_message(client_socket)
                if user is False:
                    continue
                sockets_list.append(client_socket)

                clients[client_socket] = user

                print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")


            else: 
                message = receive_message(notified_socket)

                if message is False: 
                    print("Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue

                user = clients[notified_socket]
                print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

                for client_socket in clients:
                    if client_socket != notified_socket: 
                        client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]


def Startup():

    startup = input("Host a connection or join a connect? [host/join/quit]\n").lower().strip()

    if startup == "host":
        HostFunctions()
    elif startup == "join":
        ClientFunctions()
    elif startup == "quit":
        return
    else:
        Startup()

Startup()