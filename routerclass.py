import socket
import json

class Router:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.table = {}
        self.routes = {}

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
        dist = {key: dist[key] for key in dist if dist[key] != float("inf")}
        # talvez filtrar ele mesmo e quem ele nao sabia até entao
        self.table.update(dist)

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

        while vertices:
            min_ = float("inf")
            for key in dist:
                if dist[key] <= min_ and key in  vertices:
                    min_ = dist[key]
                    u = key
            vertices = [vertex for vertex in vertices if vertex != u]
            if u in self.routes:
                for neighbor in self.routes[u]:
                    value = dist[u] + int(self.routes[u][neighbor])
                    if value < dist[neighbor]:
                        dist[neighbor] = value
                        prev[neighbor] = u

        return dist, prev

    def trace(self, message):
        dist, prev = self.get_routes()
        # usa o prev pra descobrir a rota la 

        #se for eu, eu retorno pro source a mensagem como data
        #senao, eu calculo a menor rota pro objetivo que eles querem
        #get_routes
        #e mando pra pessoa que ta nesse caminho ai pra chegar
        pass

        # nao sei se devo mandar um update assim que faco isso
        # ou depois na hora que da o tempo do periodo ele atuliza

        # print("Atualizando")

# A -> B 10
# A -> C 1
# C -> B 1