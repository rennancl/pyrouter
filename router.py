import json
import socket
import sys
import threading
import time

from pprint import pprint

class Router:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.table = {self.ip: 0}
        self.routes = {self.ip: self.table}

    def add_address(self, ip, weight):
        self.table[ip] = weight

    def del_address(self, ip):
        del self.table[ip]
        del self.routes[ip]
        self.update_table()

    def update(self):
        message = {}
        message["type"] = "update"
        message["source"] = self.ip
        message["distances"] = self.table
        for ip in self.table.copy():
            message["destination"] = ip
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.sendto(json.dumps(message).encode(), (ip, self.port))
            client.close()

    def update_routes(self, message):
        if message["source"] in self.table:
            self.routes[message["source"]] = message["distances"]
        self.update_table()

    def update_table(self):
        dist, prev = self.get_routes()
        dist = {key: dist[key] for key in dist if dist[key] != float("inf") and key in self.table}
        self.routes[self.ip] = dist

    def get_routes(self):
        vertices = set()
        for vertex in self.routes:
            vertices.add(vertex)
            for neighbor in self.routes[vertex]:
                vertices.add(neighbor)

        vertices = list(vertices)
        dist = {vertex: float("inf") for vertex in vertices}
        prev = {vertex: 0 for vertex in vertices}
        dist[self.ip] = 0

        for _ in range(len(vertices) - 1):
            for u in self.routes:
                for v in self.routes[u]:
                    w = int(self.routes[u][v])
                    if dist[u] + w < dist[v]:
                        dist[v] = dist[u] + w
                        prev[v] = u

        return dist, prev

    def trace(self, message):
        message["hops"].append(self.ip)
        if self.ip == message["destination"]:
            new_message = {
                "type": "data",
                "destination": message["source"],
                "source": self.ip,
                "payload": json.dumps(message)
            }
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client.sendto(json.dumps(new_message).encode(), (new_message["destination"], self.port))
            client.close()
            return

        min_ = float("inf")
        for u in self.routes:
            for v in self.routes[u]:
                if v == message["destination"] and int(self.routes[u][v]) + int(self.table[u])  <= min_ and self.routes[u][v]:
                    vertex = u
                    min_ = int(self.routes[u][v]) + int(self.table[u])

        if vertex == self.ip:
            vertex = message["destination"]

        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(json.dumps(message).encode(), (vertex, self.port))
        client.close()

def server(router, ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((ip, port))
    while True:
        data, address = server.recvfrom(4096)
        message = json.loads(data.decode())

        if message["type"] == "update":
            router.update_routes(message)

        if message["type"] == "trace":
            router.trace(message)

        if message["type"] == "data":
            print(json.dumps(json.loads(message["payload"]), indent=4))

def update_router(router, period):
    while True:
        time.sleep(period)
        router.update()

def main():
    connect_ip = sys.argv[1]
    period = int(sys.argv[2])
    startup = []
    if len(sys.argv) > 3:
        with open(sys.argv[3], "r") as cmds_file:
            startup = cmds_file.read().splitlines()

    port = 55151
    router = Router(connect_ip, port)

    server_thread = threading.Thread(target=server, args=(router, connect_ip, port))
    update_thread = threading.Thread(target=update_router, args=(router, period))
    update_thread.start()
    server_thread.start()

    while True:
        if startup:
            cmd = startup.pop(0)
        else:
            cmd = input()
        cmds = cmd.split()
        if cmds[0] == "add":
            ip = cmds[1]
            weight = cmds[2]
            router.add_address(ip, weight)
        elif cmds[0] == "del":
            ip = cmds[1]
            router.del_address(ip)
        elif cmds[0] == "trace":
            ip = cmds[1]
            message = {
                "type": "trace",
                "source": connect_ip,
                "destination": ip,
                "hops": []
            }
            router.trace(message)
        elif cmds[0] == "print":
            pprint(router.table)
        elif cmds[0] == "printr":
            pprint(router.routes)
        else:
            print("Comando não reconhecido")

    server_thread.join()
    update_thread.join()

if __name__ == "__main__":
    main()
