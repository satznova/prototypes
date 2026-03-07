import redis
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_user(user_id: int):
    cache_key = f"user:{user_id}"

    # Step 1: Check Redis
    cached = r.get(cache_key)
    if cached:
        print("Cache HIT")
        return cached

    # Step 2: Cache miss — simulate DB query (slow)
    print("Cache MISS — querying DB...")
    time.sleep(1)                          # simulates DB latency
    user_data = f"Alice (id={user_id})"   # pretend this came from DB

    # Step 3: Store in Redis with 5 minute TTL
    r.set(cache_key, user_data, ex=300)

    return user_data

# First call — slow (DB query)
print(get_user(1))

# Second call — instant (Redis cache)
print(get_user(1))