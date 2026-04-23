[![progress-banner](https://backend.codecrafters.io/progress/redis/91d0bce7-1108-4da3-980e-0fae5bb1b897)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

# Redis Server — Built from Scratch in Python

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![asyncio](https://img.shields.io/badge/asyncio-native-green)
![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)
![CodeCrafters](https://img.shields.io/badge/CodeCrafters-Build%20Your%20Own%20Redis-orange)

> A fully async, Redis-compatible TCP server implemented from scratch in Python — no external libraries, no frameworks, just `asyncio` and raw RESP protocol parsing.

Built as part of the [CodeCrafters "Build Your Own Redis"](https://codecrafters.io/challenges/redis) challenge to deeply understand how Redis works under the hood: event loops, binary protocols, concurrent connection handling, and in-memory data structures.

---

## Quick Demo

```
$ ./your_program.sh &
Server is open on port 6379

$ redis-cli PING
PONG

$ redis-cli SET name "arsham"
OK

$ redis-cli GET name
"arsham"

$ redis-cli SET session "abc123" PX 5000
OK
# (key expires automatically after 5 seconds)

$ redis-cli RPUSH mylist "go" "python" "rust"
(integer) 3

$ redis-cli LRANGE mylist 0 -1
1) "go"
2) "python"
3) "rust"

$ redis-cli LPUSH mylist "c"
(integer) 4

$ redis-cli LPOP mylist
"c"
```

---

## Why I Built This

I wanted to understand how Redis achieves such high throughput with a single thread. The answer — an event loop with async I/O — is easy to say but hard to truly grasp until you've built it yourself.

This project forced me to:
- Parse a binary protocol by hand, byte by byte
- Handle multiple TCP clients concurrently without threads
- Implement expiry using async tasks instead of polling
- Think like a systems programmer, not just an application developer

---

## Architecture

```
┌──────────────┐      RESP over TCP      ┌────────────────────────────────────┐
│  redis-cli   │ ─────────────────────►  │          asyncio TCP Server        │
│  (or any     │                         │  ┌──────────────────────────────┐  │
│   client)    │ ◄─────────────────────  │  │     _handle_client()         │  │
└──────────────┘      RESP response      │  │  (one coroutine per client)  │  │
                                         │  └──────────────┬───────────────┘  │
                                         │                 │                  │
                                         │  ┌──────────────▼───────────────┐  │
                                         │  │       _parse_resp()          │  │
                                         │  │  (hand-rolled RESP parser)   │  │
                                         │  └──────────────┬───────────────┘  │
                                         │                 │                  │
                                         │  ┌──────────────▼───────────────┐  │
                                         │  │        _dispatch()           │  │
                                         │  │  (command router)            │  │
                                         │  └──────────┬──────┬────────────┘  │
                                         │             │      │               │
                                         │  ┌──────────▼──┐ ┌▼─────────────┐ │
                                         │  │ String store│ │  List store  │ │
                                         │  │  (dict)     │ │   (dict)     │ │
                                         │  └─────────────┘ └─────────────┘ │
                                         └────────────────────────────────────┘
```

**Key design decisions:**

| Decision | Rationale |
|---|---|
| Single `asyncio` event loop | Mirrors how real Redis avoids locking overhead — one thread, non-blocking I/O |
| Hand-rolled RESP parser | Forces understanding of the protocol at the byte level, no magic |
| `asyncio.create_task` for TTL | Key expiry is non-blocking — no polling loop, no timer threads |
| Zero external dependencies | Pure stdlib keeps the focus on fundamentals |

---

## Implemented Commands

| Category | Command | Description |
|---|---|---|
| **Core** | `PING` | Heartbeat check, returns `PONG` |
| **Core** | `ECHO <msg>` | Returns the message as a bulk string |
| **Strings** | `SET <key> <value>` | Store a key-value pair |
| **Strings** | `SET <key> <value> EX <secs>` | Store with second-level TTL |
| **Strings** | `SET <key> <value> PX <ms>` | Store with millisecond-level TTL |
| **Strings** | `GET <key>` | Retrieve a value, returns nil if missing or expired |
| **Lists** | `RPUSH <key> <v> [v ...]` | Append one or more elements to the tail |
| **Lists** | `LPUSH <key> <v> [v ...]` | Prepend one or more elements to the head |
| **Lists** | `LRANGE <key> <start> <stop>` | Get a subrange (supports `-1` for end) |
| **Lists** | `LPOP <key> [count]` | Remove and return element(s) from the head |
| **Lists** | `LLEN <key>` | Return the number of elements in a list |

---

## CodeCrafters Roadmap

The full [CodeCrafters Redis course](https://app.codecrafters.io/courses/redis/overview) covers every major Redis subsystem. Here's where this project stands and what's coming next:

### Core & Strings
- [x] `PING`, `ECHO`
- [x] `SET`, `GET`
- [x] Key expiry (`EX`, `PX`)

### Lists
- [x] `RPUSH`, `LPUSH`
- [x] `LRANGE`, `LPOP`, `LLEN`
- [ ] `RPOP`
- [ ] `BLPOP`, `BRPOP` (blocking pop with timeout)

### Streams
- [ ] `XADD` — append entry to a stream with auto/partial ID generation
- [ ] `XRANGE` — query entries with `-` / `+` range operators
- [ ] `XREAD` — read from one or multiple streams
- [ ] `XREAD BLOCK` — blocking reads with `$` (new entries only)

### Sorted Sets
- [ ] `ZADD` — add members with scores
- [ ] `ZRANK` — rank of a member
- [ ] `ZRANGE` — range query with negative index support
- [ ] `ZCARD` — count members
- [ ] `ZSCORE` — retrieve a member's score
- [ ] `ZREM` — remove members

### Transactions
- [ ] `MULTI` / `EXEC` — queue and atomically execute a block of commands
- [ ] `DISCARD` — cancel a queued transaction
- [ ] `INCR` — atomic integer increment
- [ ] `WATCH` / `UNWATCH` — optimistic locking on keys

### Pub/Sub
- [ ] `SUBSCRIBE` — subscribe to one or multiple channels
- [ ] `PUBLISH` — broadcast a message to a channel
- [ ] `UNSUBSCRIBE` — leave channels
- [ ] `PING` in subscribed mode

### Geospatial
- [ ] `GEOADD` — store coordinates with validation
- [ ] `GEOPOS` — retrieve stored coordinates
- [ ] `GEODIST` — distance between two points
- [ ] `GEORADIUS` — search within a radius

### Authentication & ACL
- [ ] `AUTH` — password-based authentication
- [ ] `ACL WHOAMI` / `ACL GETUSER`
- [ ] Default user with `nopass` flag

### Replication
- [ ] Port configuration, `INFO` command (master/replica mode)
- [ ] Replication ID and offset tracking
- [ ] 3-stage handshake protocol
- [ ] Empty RDB transfer to replicas
- [ ] Multi-replica command propagation
- [ ] `ACK` response, `WAIT` command

### Persistence — RDB (Snapshot)
- [ ] File configuration and loading
- [ ] Read single / multiple keys from `.rdb` file
- [ ] String value persistence with expiry timestamps

### Persistence — AOF (Append-Only File)
- [ ] Configuration flags and directory setup
- [ ] Manifest file generation
- [ ] Writing and filtering write commands
- [ ] AOF replay on startup

---

## Getting Started

**Prerequisites:** Python 3.14+, [`uv`](https://github.com/astral-sh/uv)

```bash
# Clone the repo
git clone https://github.com/arsham/codecrafters-redis-python
cd codecrafters-redis-python

# Start the server (runs on localhost:6379)
./your_program.sh

# In another terminal — use any Redis client
redis-cli PING
redis-cli SET hello world
redis-cli GET hello
```

The server binds to `localhost:6379` by default — the same port as a real Redis instance.

---

## Technical Highlights

**RESP Protocol parsing by hand**

Redis clients communicate using the [Redis Serialization Protocol (RESP)](https://redis.io/docs/reference/protocol-spec/). Rather than using a library, the parser is written from scratch:

```python
def _parse_resp(self, raw: str) -> list[str]:
    # "*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"  ->  ["SET", "foo", "bar"]
    parts = raw.split("\r\n")
    element_count = int(parts[0][1:])  # "*3" -> 3
    tokens = []
    i = 1
    for _ in range(element_count):
        tokens.append(parts[i + 1])    # skip the $length line, take the value
        i += 2
    return tokens
```

**Non-blocking TTL with async tasks**

Key expiry doesn't poll — it schedules a coroutine that sleeps for the TTL duration and then deletes the key. No background threads, no timer heap:

```python
async def _expire_key(self, key, unit, duration):
    seconds = float(duration)
    if unit == "PX":
        seconds /= 1000
    await asyncio.sleep(seconds)
    if key in self.store:
        del self.store[key]

# When SET receives EX/PX:
asyncio.create_task(self._expire_key(key, tokens[3], tokens[4]))
```

**Concurrent clients, one thread**

`asyncio.start_server` spawns a new coroutine per connection. All clients are handled by a single event loop — exactly how Redis itself works:

```python
server = await asyncio.start_server(self._handle_client, self.host, self.port)
await server.serve_forever()
```

---

## What I Learned

- **Event loops aren't magic** — they're a `select`/`epoll` call wrapped in a scheduler. Once you build one (or build on top of one at this level), the mental model clicks permanently.
- **Redis's single-threaded design is a feature** — by eliminating locking entirely, it achieves predictable latency and high throughput for the common case.
- **Protocol design matters** — RESP is simple but deliberate. The length-prefixed bulk strings avoid ambiguity that a naive newline-delimited format would create.
- **Async TTL > polling TTL** — scheduling a sleeping coroutine is lighter and more precise than a background thread running `time.sleep` in a loop.

---

*Built with the [CodeCrafters](https://codecrafters.io) "Build Your Own Redis" challenge.*
