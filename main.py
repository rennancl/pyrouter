import json
import socket
import sys
import threading
import time

from pprint import pprint

def server_init(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((ip, port))
    while True:
        while True:
            #RECEIVE
            data, address = server.recvfrom(4096)
            if not data:
                break
            print("SERVER", json.loads(data.decode()))
            #SEND
            server.sendto("Seja bem vindo !".encode(), address)
            break
        break

def client_init(ip, port):
    message = {"type": "trace",
               "source": "127.0.1.1",
               "destination": "127.0.1.2",
               "hops": ["127.0.1.1", "127.0.1.5", "127.0.1.2"]}

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(json.dumps(message).encode(), (ip, port))
    buffer, server_address = client.recvfrom(4096)
    client.close()
    print("CLIENT", buffer)

def main():
    connect_ip = '127.0.1.8'
    port = 55151 #int(sys.argv[1])
    server_thread = threading.Thread(target=server_init, args=(ip, port))
    client_thread = threading.Thread(target=client_init, args=(ip, port))

    server_thread.start()
    client_thread.start()

    while True:
        cmd = input()
        cmds = cmd.split()
        if cmds[0] == "add":
            ip = cmds[1]
            weight = cmds[2]
        elif cmds[0] == "del":
            ip = cmds[1]
        else:
            print("Comando não reconhecido")


    client_thread.join()
    server_thread.join()


if __name__ == "__main__":
    main()
