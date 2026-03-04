import redis

# Connect to Redis: Connect to local Redis instance
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# ── Strings ───────────────────────────────────────────────────
r.set("name", "Alice")
print(r.get("name"))           # Alice

r.set("session", "abc123", ex=60)   # expires in 60 seconds
print(r.ttl("session"))             # ~60

r.set("counter", 0)
r.incr("counter")
r.incr("counter")
print(r.get("counter"))        # 2

# ── Hashes ────────────────────────────────────────────────────
r.hset("user:1", mapping={"name": "Alice", "email": "alice@example.com", "age": "30"})
print(r.hget("user:1", "name"))      # Alice
print(r.hgetall("user:1"))           # {'name': 'Alice', 'email': '...', 'age': '30'}

# ── Lists ─────────────────────────────────────────────────────
r.rpush("queue", "task1", "task2", "task3")
print(r.lrange("queue", 0, -1))      # ['task1', 'task2', 'task3']
print(r.lpop("queue"))               # task1 (FIFO)

# ── Sets ──────────────────────────────────────────────────────
r.sadd("tags", "python", "fastapi", "docker", "python")  # python added once
print(r.smembers("tags"))            # {'python', 'fastapi', 'docker'}
print(r.sismember("tags", "java"))   # False

# ── Sorted Sets ───────────────────────────────────────────────
r.zadd("leaderboard", {"alice": 100, "bob": 250, "carol": 175})
print(r.zrevrange("leaderboard", 0, -1, withscores=True))
# [('bob', 250.0), ('carol', 175.0), ('alice', 100.0)]
