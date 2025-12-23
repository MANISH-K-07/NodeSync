import socket
import threading
import sys
import time


class NodeServer:
    def __init__(self, host="127.0.0.1", port=5000, peers=None):
        self.host = host
        self.port = port
        self.data_store = {}
        self.peers = peers if peers else []
        self.peer_status = {peer: True for peer in self.peers}
        self.lock = threading.Lock()

    def handle_client(self, client_socket):
        with client_socket:
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    response = self.process_command(data.strip())
                    client_socket.sendall(response.encode())
                except:
                    break

    def process_command(self, command, replicate=True):
        parts = command.split(" ", 2)
        action = parts[0].upper()

        if action == "PING":
            return "PONG\n"

        if action == "SET" and len(parts) == 3:
            key, value = parts[1], parts[2]
            with self.lock:
                self.data_store[key] = value

            if replicate:
                self.replicate_to_peers(key, value)

            return f"OK: {key} set\n"

        if action == "GET" and len(parts) == 2:
            key = parts[1]
            with self.lock:
                if key in self.data_store:
                    return f"VALUE: {self.data_store[key]}\n"
            return "ERROR: Key not found\n"

        return "ERROR: Invalid command\n"

    def replicate_to_peers(self, key, value):
        for peer in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect(peer)
                sock.sendall(f"SET {key} {value}".encode())
                sock.close()

                if not self.peer_status.get(peer, True):
                    print(f"[RECOVERED] Peer {peer} is back UP")
                self.peer_status[peer] = True

            except:
                if self.peer_status.get(peer, True):
                    print(f"[FAILURE] Peer {peer} is DOWN")
                self.peer_status[peer] = False

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

                    if not self.peer_status.get(peer, True):
                        print(f"[RECOVERED] Peer {peer} is back UP")
                    self.peer_status[peer] = True

                except:
                    if self.peer_status.get(peer, True):
                        print(f"[FAILURE] Peer {peer} is DOWN")
                    self.peer_status[peer] = False

            time.sleep(5)

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"[NodeSync] Node running on {self.host}:{self.port}")
        print(f"[NodeSync] Peers: {self.peers}")

        heartbeat_thread = threading.Thread(
            target=self.heartbeat_monitor, daemon=True
        )
        heartbeat_thread.start()

        while True:
            client_socket, _ = server.accept()
            thread = threading.Thread(
                target=self.handle_client, args=(client_socket,)
            )
            thread.start()


if __name__ == "__main__":
    port = int(sys.argv[1])
    peers = []

    if len(sys.argv) > 2:
        for peer in sys.argv[2:]:
            host, p = peer.split(":")
            peers.append((host, int(p)))

    node = NodeServer(port=port, peers=peers)
    node.start()
