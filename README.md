# NodeSync

NodeSync is a fault-tolerant distributed key-value store built in Python that demonstrates core distributed systems concepts including replication, leader election, failure detection, and automatic failover.

This project was built as a learning-oriented yet production-inspired system to explore how real-world distributed databases maintain availability and consistency under failures.

---

## ✨ Features

- Distributed key-value storage using TCP sockets
- Multi-node replication
- Heartbeat-based failure detection
- Leader election (Raft-lite)
- Leader-based writes with automatic forwarding
- Automatic leader re-election on node failure
- Concurrent client handling using threads

---

## 🏗️ Architecture Overview

- Each node runs an independent TCP server
- Nodes communicate peer-to-peer
- One node acts as the **leader**
- All `SET` operations go through the leader
- Followers forward writes to the leader
- Writes are replicated to all alive peers
- Heartbeats continuously monitor node health
- Leader is re-elected automatically on failure

Leader election is deterministic:  
➡️ the alive node with the **highest port number** becomes leader.

Read detailed **NodeSync Architecture** at [Architecture.md](https://github.com/MANISH-K-07/NodeSync/blob/main/Architecture.md)

## 📁 Project Structure

```
NodeSync/
├── nodes/
│ └── node.py            # Distributed node implementation
│   └── init.py
├── client/
│ └── init.py
├── main.py
├── README.md
└── requirements.txt
```

---

## 🚀 Running the System

### Start 3 nodes (example)

```
python nodes/node.py 5000 127.0.0.1:5001 127.0.0.1:5002
python nodes/node.py 5001 127.0.0.1:5000 127.0.0.1:5002
python nodes/node.py 5002 127.0.0.1:5000 127.0.0.1:5001
```
The node with the highest port becomes leader.

## 🧪 Client Interaction (PowerShell Example)

```
$client = New-Object System.Net.Sockets.TcpClient("127.0.0.1", 5002)
$stream = $client.GetStream()
$writer = New-Object System.IO.StreamWriter($stream)
$reader = New-Object System.IO.StreamReader($stream)
$writer.AutoFlush = $true

$writer.WriteLine("SET hello world")
$reader.ReadLine()

$writer.WriteLine("GET hello")
$reader.ReadLine()
```

## 🔁 Consistency Modes

NodeSync supports **runtime-switchable consistency models**, allowing experimentation with CAP trade-offs.

### Available Modes

- **Eventual consistency** (default)  
  - Writes are replicated asynchronously  
  - Lower latency  
  - Temporary inconsistencies may occur

- **Strong consistency** (quorum-based)  
  - Leader waits for acknowledgements from a majority of nodes  
  - Higher latency  
  - Linearizable writes as long as quorum is available

### Switching Consistency at Runtime

Consistency can be changed dynamically using a client command:

```
CONSISTENCY eventual
CONSISTENCY strong
```

The consistency mode applies to the node receiving the command (typically the leader).

### Example (PowerShell)

```
$writer.WriteLine("CONSISTENCY strong")
$reader.ReadLine()

$writer.WriteLine("SET key value")
$reader.ReadLine()
```

If quorum cannot be reached in strong mode, the write fails with:
```
FAIL: quorum not reached
```
This enables direct comparison of consistency-performance trade-offs.

## 📊 Performance Benchmarking

NodeSync was benchmarked under both eventual and strong consistency modes.

Results show that quorum-based strong consistency increases write latency due to replica acknowledgements, while eventual consistency provides lower latency.

- Detailed observations & results are available in [benchmark/RESULTS.md](https://github.com/MANISH-K-07/NodeSync/blob/main/benchmark/RESULTS.md).

### CLI Results:

```
python benchmark/benchmark.py
```

```
[Benchmark] Running Eventual Consistency test...
[Benchmark] Running Strong Consistency test...

======== RESULTS ========

Eventual Consistency:
  Avg latency: 0.0139s
  Max latency: 0.0371s

Strong Consistency:
  Avg latency: 0.0153s
  Max latency: 0.0429s
```

## 🔥 Fault Tolerance Demo

 1. Kill the leader node
 2. Remaining nodes elect a new leader automatically
 3. Writes continue without downtime

---

## 🧠 Distributed Systems: Key Concepts Demonstrated

- Replication
- Leader election
- Failover
- Heartbeats
- Eventual consistency
- Concurrency control

## 📌 Future Improvements

- Persistent write-ahead logs
- Strong consistency using Raft log replication
- Sharding and partitioning
- Performance benchmarking and metrics
- Client library abstraction

---

## 📚 Why This Project Matters

NodeSync demonstrates hands-on understanding of distributed systems fundamentals commonly taught in graduate-level courses, including fault tolerance, leader-based coordination, and replication strategies.