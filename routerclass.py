import socket
import json

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
            print("achoo")
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

        print("quero mandar pra vc:", vertex)
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(json.dumps(message).encode(), (vertex, self.port))
        client.close()


        # vertices = set()
        # for vertex in self.routes:
        #     vertices.add(vertex)
        #     for neighbor in self.routes[vertex]:
        #         vertices.add(neighbor)

        # vertices = list(vertices)
        # dist = {vertex: float("inf") for vertex in vertices}
        # prev = {vertex: 0 for vertex in vertices}
        # dist[self.ip] = 0

        # while vertices:
        #     min_ = float("inf")
        #     for key in dist:
        #         if dist[key] <= min_ and key in vertices:
        #             min_ = dist[key]
        #             u = key
        #     vertices = [vertex for vertex in vertices if vertex != u]
        #     if u in self.routes:
        #         print(u, self.routes)
        #         for neighbor in self.routes[u]:
        #             value = dist[u] + int(self.routes[u][neighbor])
        #             if value < dist[neighbor]:
        #                 dist[neighbor] = value
        #                 prev[neighbor] = u

        # return dist, prev