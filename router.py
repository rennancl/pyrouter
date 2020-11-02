import json
import socket
import sys
import threading
import time

from pprint import pprint
from routerclass import Router

def server(router, ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((ip, port))
    while True:
        data, address = server.recvfrom(4096)
        message = json.loads(data.decode())
        pprint(message)
        # if message["type"] == "update":
        #     router.update_routes(message)

        # if message["type"] == "trace":
        #     router.trace(message)

        # router.
        # server.sendto("Seja bem vindo !".encode(), address)

# def client_init(ip, port):
#     message = {"type": "trace",
#                "source": "127.0.1.1",
#                "destination": "127.0.1.2",
#                "hops": ["127.0.1.1", "127.0.1.5", "127.0.1.2"]}

#     client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     client.sendto(json.dumps(message).encode(), (ip, port))
#     buffer, server_address = client.recvfrom(4096)
#     client.close()
#     print("CLIENT", buffer)

def update_router(router, period):
    while True:
        time.sleep(period)
        router.update()

def main():
    connect_ip = sys.argv[1] #'127.0.1.8'
    period = int(sys.argv[2])
    startup = []
    if len(sys.argv) > 3:
        with open(sys.argv[3], "r") as cmds_file:
            startup = cmds_file.read().splitlines()

    port = 55151
    router = Router(connect_ip, port)


    # client_thread = threading.Thread(target=client_init, args=(connect_ip, port))
    server_thread = threading.Thread(target=server, args=(router, connect_ip, port))
    update_thread = threading.Thread(target=update_router, args=(router, period))
    update_thread.start()
    server_thread.start()
    # client_thread.start()


    while True:
        if startup:
            cmd = startup.pop(0)
        else:
            cmd = input()
        cmds = cmd.split()
        print(cmd)
        if cmds[0] == "add":
            ip = cmds[1]
            weight = cmds[2]
            router.add_address(ip, weight)
        elif cmds[0] == "del":
            ip = cmds[1]
            router.del_address(ip)
        elif cmds[0] == "trace":
            ip = cmds[1]
            router.trace(ip)
        else:
            print("Comando não reconhecido")


    # client_thread.join()
    server_thread.join()
    update_thread.join()


if __name__ == "__main__":
    main()
