# NodeSync Architecture

## High-Level Design

```
Client
|
v
Follower Node ----> Leader Node ----> Peer Nodes
_____________________________/
Replication
```


## Leader Election

- Every node sends heartbeats to peers
- Nodes maintain a live peer list
- The alive node with the highest ID becomes leader
- Leader role changes automatically on failure

## Fault Detection

- TCP heartbeat messages every 5 seconds
- Failed peers are marked DOWN
- Recovery is detected automatically

## Write Path

1. Client sends `SET` request
2. If node is follower → forwards to leader
3. Leader writes locally
4. Leader replicates write to alive peers

## Read Path

- Reads are served locally from any node
