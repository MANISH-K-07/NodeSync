import socket
import threading
import sys
import time


class NodeServer:
    def __init__(self, host="127.0.0.1", port=5000, peers=None):
        self.host = host
        self.port = port
        self.node_id = port
        self.peers = peers if peers else []

        self.data_store = {}
        self.peer_status = {peer: True for peer in self.peers}
        self.leader_id = None
        self.lock = threading.Lock()

    # ---------------- CLIENT HANDLING ---------------- #

    def handle_client(self, client_socket):
        with client_socket:
            while True:
                try:
                    data = client_socket.recv(1024).decode().strip()
                    if not data:
                        break
                    response = self.process_command(data)
                    client_socket.sendall(response.encode())
                except:
                    break

    def process_command(self, command):
        parts = command.split(" ", 2)
        action = parts[0].upper()

        if action == "PING":
            return "PONG\n"

        if action == "LEADER":
            return f"LEADER {self.leader_id}\n"

        if action == "SET":
            if self.node_id != self.leader_id:
                return self.forward_to_leader(command)
            return self.handle_set(parts)

        if action == "GET" and len(parts) == 2:
            key = parts[1]
            with self.lock:
                if key in self.data_store:
                    return f"VALUE: {self.data_store[key]}\n"
            return "ERROR: Key not found\n"

        return "ERROR: Invalid command\n"

    def handle_set(self, parts):
        if len(parts) != 3:
            return "ERROR: Invalid SET\n"

        key, value = parts[1], parts[2]
        with self.lock:
            self.data_store[key] = value

        self.replicate_to_peers(key, value)
        return f"OK: {key} set by leader {self.node_id}\n"

    def forward_to_leader(self, command):
        try:
            leader = self.get_leader_address()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(leader)
            sock.sendall(command.encode())
            response = sock.recv(1024).decode()
            sock.close()
            return response
        except:
            return "ERROR: Leader unavailable\n"

    # ---------------- REPLICATION ---------------- #

    def replicate_to_peers(self, key, value):
        for peer in self.peers:
            if not self.peer_status.get(peer, False):
                continue
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect(peer)
                sock.sendall(f"SET {key} {value}".encode())
                sock.close()
            except:
                self.peer_status[peer] = False

    # ---------------- LEADER ELECTION ---------------- #

    def elect_leader(self):
        alive_nodes = [self.node_id]
        for peer, alive in self.peer_status.items():
            if alive:
                alive_nodes.append(peer[1])

        new_leader = max(alive_nodes)
        if new_leader != self.leader_id:
            print(f"[ELECTION] New leader elected: {new_leader}")
        self.leader_id = new_leader

    def get_leader_address(self):
        if self.leader_id == self.node_id:
            return (self.host, self.port)

        for peer in self.peers:
            if peer[1] == self.leader_id:
                return peer
        raise Exception("Leader not found")

    # ---------------- HEARTBEATS ---------------- #

    def heartbeat_monitor(self):
        while True:
            for peer in self.peers:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect(peer)
                    sock.sendall(b"PING")
                    sock.recv(1024)
                    sock.close()
                    self.peer_status[peer] = True
                except:
                    self.peer_status[peer] = False

            self.elect_leader()
            time.sleep(5)

    # ---------------- SERVER ---------------- #

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"[NodeSync] Node {self.node_id} running on {self.host}:{self.port}")
        print(f"[NodeSync] Peers: {self.peers}")

        heartbeat = threading.Thread(
            target=self.heartbeat_monitor, daemon=True
        )
        heartbeat.start()

        while True:
            client_socket, _ = server.accept()
            threading.Thread(
                target=self.handle_client, args=(client_socket,)
            ).start()


if __name__ == "__main__":
    port = int(sys.argv[1])
    peers = []

    if len(sys.argv) > 2:
        for peer in sys.argv[2:]:
            host, p = peer.split(":")
            peers.append((host, int(p)))

    node = NodeServer(port=port, peers=peers)
    node.start()
