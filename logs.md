# NodeSync Runtime Logs

This document explains how to interpret NodeSync’s runtime logs and
how they reflect internal distributed system behavior.

NodeSync logs are timestamped and tagged to make system events
easy to follow during execution.

---

## Log Format

Each log entry follows the format:

- HH:MM:SS [TAG ] message

Example:

```
17:09:47 [NodeSync  ] Node 5000 running on 127.0.0.1:5000
```

- **Timestamp**: Local wall-clock time when the event occurred
- **Tag**: Type of system event
- **Message**: Human-readable description

---

## Log Tags

### `[NodeSync]`

Emitted during node startup and initialization.

Example:

```
17:08:04 [NodeSync  ] Node 5002 running on 127.0.0.1:5002
17:08:04 [NodeSync  ] Peers: [('127.0.0.1', 5000), ('127.0.0.1', 5001)]
```

---

### `[FAILURE]`

Indicates a peer node has become unreachable.
This is detected via missed heartbeat responses.

Example:

```
17:08:04 [FAILURE   ] Peer ('127.0.0.1', 5000) is DOWN
```

---

### `[RECOVERED]`

Emitted when a previously failed node becomes reachable again.

Example:

```
17:08:31 [RECOVERED ] Peer ('127.0.0.1', 5001) is back UP
```


---

### `[ELECTION]`

Indicates that a new leader has been elected.
Leader election occurs when peer liveness changes.

Example:

```
16:55:24 [ELECTION  ] New leader elected: 5002
```

---

## Example Failure Scenario

Below is a typical sequence when a leader node fails:

```
16:55:32 [NodeSync  ] Node 5001 running on 127.0.0.1:5001
16:55:32 [NodeSync  ] Peers: [('127.0.0.1', 5000), ('127.0.0.1', 5002)]
16:55:34 [ELECTION  ] New leader elected: 5002
16:56:03 [FAILURE   ] Peer ('127.0.0.1', 5002) is DOWN
16:56:03 [ELECTION  ] New leader elected: 5001
```


This sequence demonstrates:
1. Failure detection via heartbeat timeout
2. Automatic leader re-election
3. Continued system operation without manual intervention

---

## Why Logs Matter

In distributed systems, logs are essential for:
- Understanding failure propagation
- Measuring recovery time
- Debugging replication behavior
- Reasoning about event ordering

NodeSync’s logs are intentionally simple and readable,
making system behavior transparent during experimentation.

---

## Notes

- Logs are emitted synchronously using standard output
- No external logging frameworks are used
- Timestamping enables temporal reasoning about events
