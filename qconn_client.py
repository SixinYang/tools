import socket
import select

LOCAL_HOST = '0.0.0.0'
LOCAL_PORT = 8080
REMOTE_HOST = '10.89.7.141'
REMOTE_PORT = 8000

def handle_new(client_socket):
    global sockets, pairs, clients

    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((REMOTE_HOST, REMOTE_PORT))
    sockets.append(remote_socket)
    sockets.append(client_socket)

    clients[remote_socket] = clients[client_socket]
    pairs[client_socket] = (remote_socket, " =>" )
    pairs[remote_socket] = (client_socket, " <= ")

def handle_data(sock):
    global pairs, clients
    data = sock.recv(4096)
    if not data:
        return
    remote, sign = pairs[sock]
    print(str(clients[sock]) + sign + str(data))
    remote.send(data)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCAL_HOST, LOCAL_PORT))
server.listen(5)

print(f"Listening on {LOCAL_HOST}:{LOCAL_PORT}, relaying to {REMOTE_HOST}:{REMOTE_PORT}")

sockets = [server]
clients = {}
pairs = {}

while True:
    rd, wr, er = select.select(sockets, [], [])
    for s in rd:
        if s == server:
            client_socket, addr = server.accept()

            clients[client_socket] = addr
            print("New socket: " + str(addr))
            handle_new(client_socket)
        else:
            handle_data(s)

print("EXIT")

