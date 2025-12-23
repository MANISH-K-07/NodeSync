# NodeSync Performance Evaluation

## Setup
- Nodes: 3
- Leader-based replication
- TCP sockets
- Localhost testing

## Results

| Consistency Model | Avg Latency (s) | Max Latency (s) |
|------------------|-----------------|-----------------|
| Eventual         | 0.0139          | 0.0371          |
| Strong (Quorum)  | 0.0153          | 0.0429          |

## Observations

- Strong consistency introduces higher latency due to quorum acknowledgements.
- Eventual consistency provides faster writes at the cost of temporary inconsistency.
- Results align with theoretical CAP trade-offs.

## Conclusion

NodeSync demonstrates the practical performance impact of consistency choices in distributed systems.
