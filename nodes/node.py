import socket
import threading
import sys


class NodeServer:
    def __init__(self, host="127.0.0.1", port=5000, peers=None):
        self.host = host
        self.port = port
        self.data_store = {}
        self.peers = peers if peers else []

    def handle_client(self, client_socket):
        with client_socket:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                response = self.process_command(data.strip())
                client_socket.sendall(response.encode())

    def process_command(self, command, replicate=True):
        parts = command.split(" ", 2)

        if len(parts) == 0:
            return "ERROR: Empty command\n"

        action = parts[0].upper()

        if action == "SET" and len(parts) == 3:
            key, value = parts[1], parts[2]
            self.data_store[key] = value

            if replicate:
                self.replicate_to_peers(key, value)

            return f"OK: {key} set\n"

        elif action == "GET" and len(parts) == 2:
            key = parts[1]
            if key in self.data_store:
                return f"VALUE: {self.data_store[key]}\n"
            return "ERROR: Key not found\n"

        else:
            return "ERROR: Invalid command\n"

    def replicate_to_peers(self, key, value):
        for peer in self.peers:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(peer)
                sock.sendall(f"SET {key} {value}".encode())
                sock.close()
            except Exception as e:
                print(f"[WARN] Failed to replicate to {peer}: {e}")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen()

        print(f"[NodeSync] Node running on {self.host}:{self.port}")
        print(f"[NodeSync] Peers: {self.peers}")

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
