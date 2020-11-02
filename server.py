import socket
import sys
import json
from pprint import pprint

port = int(sys.argv[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', port))
server.listen(5)

while True:
    conn, addr = server.accept()
    buffer = ''

    while True:
        #RECEIVE
        data = conn.recv(4096)
        if not data:
            break
        buffer = json.loads(data.decode())
        pprint(buffer)

        #SEND
        conn.send("Seja bem vindo !".encode())

    conn.close()
