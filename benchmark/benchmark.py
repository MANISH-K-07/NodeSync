import socket
import time
import statistics

HOST = "127.0.0.1"
PORT = 5000
REQUESTS = 50


def send_command(command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    start = time.time()
    sock.sendall(command.encode())
    sock.recv(1024)
    end = time.time()
    sock.close()
    return end - start


def benchmark(consistency):
    latencies = []

    send_command(f"CONSISTENCY {consistency}")

    for i in range(REQUESTS):
        latency = send_command(f"SET key{i} value{i}")
        latencies.append(latency)

    return latencies


if __name__ == "__main__":
    print("[Benchmark] Running Eventual Consistency test...")
    eventual = benchmark("eventual")

    print("[Benchmark] Running Strong Consistency test...")
    strong = benchmark("strong")

    print("\n======== RESULTS ========\n")
    print(f"Eventual Consistency:")
    print(f"  Avg latency: {statistics.mean(eventual):.4f}s")
    print(f"  Max latency: {max(eventual):.4f}s")

    print(f"\nStrong Consistency:")
    print(f"  Avg latency: {statistics.mean(strong):.4f}s")
    print(f"  Max latency: {max(strong):.4f}s")
    print("")
