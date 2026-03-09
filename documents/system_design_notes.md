# System Design Notes

## Scalability

Scalability is the ability of a system to handle increased load without degrading performance. There are two main approaches:

**Vertical scaling** (scaling up): Adding more resources (CPU, RAM) to a single machine. Simple but limited by hardware ceilings. Good for databases that are hard to distribute.

**Horizontal scaling** (scaling out): Adding more machines to distribute the load. More complex but virtually unlimited. Requires careful design for data consistency and session management.

## Load Balancing

A load balancer distributes incoming traffic across multiple servers. Common algorithms include:

- **Round Robin**: Requests are distributed sequentially. Simple but doesn't account for server capacity.
- **Least Connections**: Routes to the server with fewest active connections. Better for varying request durations.
- **Weighted Round Robin**: Assigns weights based on server capacity. Useful for heterogeneous server pools.
- **IP Hash**: Routes based on client IP. Ensures session stickiness without cookies.

Health checks are essential: the load balancer must detect unhealthy servers and stop routing traffic to them. Use both active probes (periodic HTTP requests) and passive monitoring (tracking error rates).

## Caching

Caching stores frequently accessed data in fast storage to reduce latency and database load. Key strategies:

**Cache-aside** (lazy loading): Application checks cache first. On miss, loads from database and populates cache. Simple but risks stale data and cache stampede.

**Write-through**: Every write goes to both cache and database simultaneously. Ensures consistency but adds write latency.

**Write-behind**: Writes go to cache first, then asynchronously to database. Fast writes but risks data loss on cache failure.

Cache invalidation is one of the hardest problems in computer science. Use TTL (time-to-live) as a safety net, and event-driven invalidation for correctness.

**Redis** and **Memcached** are the most popular caching solutions. Redis offers richer data structures (sorted sets, streams) while Memcached is simpler and slightly faster for basic key-value operations.

## Database Sharding

Sharding partitions data across multiple database instances. Each shard holds a subset of the data.

**Hash-based sharding**: Use a hash function on a key (e.g., `user_id % num_shards`). Even distribution but resharding requires data migration.

**Range-based sharding**: Partition by value ranges (e.g., users A-M on shard 1, N-Z on shard 2). Can lead to hotspots if distribution is uneven.

**Directory-based sharding**: A lookup table maps keys to shards. Flexible but the directory becomes a single point of failure.

Challenges with sharding include cross-shard queries, maintaining referential integrity, and rebalancing when adding shards.

## CAP Theorem

The CAP theorem states that a distributed system can guarantee at most two of three properties:

- **Consistency**: Every read receives the most recent write.
- **Availability**: Every request receives a response (even if stale).
- **Partition tolerance**: The system operates despite network partitions.

Since network partitions are inevitable in distributed systems, the real choice is between CP (consistent but may be unavailable during partitions) and AP (available but may return stale data).

**CP systems** (e.g., MongoDB with majority reads, HBase): Preferred for financial transactions, inventory management.

**AP systems** (e.g., Cassandra, DynamoDB): Preferred for social feeds, analytics, shopping carts where eventual consistency is acceptable.

## Rate Limiting

Rate limiting controls the number of requests a client can make in a given time window. Essential for API protection and fair resource allocation.

Common algorithms: Token bucket (smooth, allows bursts), Sliding window (precise but memory-intensive), Fixed window (simple but allows boundary bursts).

Implement rate limiting at the API gateway level for global limits, and at the application level for per-user or per-endpoint limits.
