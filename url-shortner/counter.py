"""
Write-Behind Hit Counter
------------------------
This is a classic system design pattern for write-heavy metrics.

THE PROBLEM:
Every redirect increments a hit counter. At scale, a URL shortener
like bit.ly processes millions of redirects per second. If every
redirect did a DB UPDATE, the database would be the bottleneck.

THE SOLUTION — Write-Behind (aka Write-Back) Cache:
1. On each redirect: INCR the counter in Redis (in-memory, O(1), very fast)
2. Periodically (every 60s): flush Redis counters → batch UPDATE to PostgreSQL
3. Analytics reads from DB (eventually consistent, fine for dashboards)

KEY TRADEOFF:
- Hit counts are *eventually consistent* — up to 60s lag
- But redirect latency is minimal — no DB write on the hot path
- If Redis crashes before flush: we lose up to 60s of counter data (acceptable)

Redis key format: hits:{code}  →  integer count
"""
import logging
import redis
from sqlalchemy.orm import Session
from app.models.models import ShortURL

logger = logging.getLogger(__name__)

HIT_KEY_PREFIX = "hits:"
HIT_KEY_PATTERN = "hits:*"


def increment_hit(r: redis.Redis, code: str):
    """
    Increment hit counter in Redis. Called on every redirect.
    Redis INCR is atomic and O(1) — safe under high concurrency.
    """
    r.incr(f"{HIT_KEY_PREFIX}{code}")


def get_live_hit_count(r: redis.Redis, code: str, db_count: int) -> int:
    """
    Get the real-time hit count = DB count + Redis buffer.
    Use this for stats endpoints where accuracy matters.
    """
    redis_count = r.get(f"{HIT_KEY_PREFIX}{code}")
    buffer = int(redis_count) if redis_count else 0
    return db_count + buffer


def flush_counters_to_db(r: redis.Redis, db: Session):
    """
    Flush all Redis hit counters to PostgreSQL.

    Called periodically by a background job (Cloud Scheduler in GCP,
    or APScheduler locally). Uses a pipeline for efficiency.

    Process:
    1. Scan all hits:* keys in Redis
    2. For each key: GETDEL (atomic get + delete)
    3. Batch UPDATE to DB using the fetched counts
    """
    keys = r.keys(HIT_KEY_PATTERN)

    if not keys:
        logger.info("No counters to flush.")
        return

    logger.info(f"Flushing {len(keys)} counters to DB...")

    # Use pipeline for atomic multi-key operations
    pipe = r.pipeline()
    for key in keys:
        pipe.getdel(key)   # Atomic: get value AND delete key in one op
    counts = pipe.execute()

    flushed = 0
    for key, count in zip(keys, counts):
        if count is None:
            continue
        code = key.replace(HIT_KEY_PREFIX, "")
        increment = int(count)

        # Batch update — in production you'd use bulk UPDATE for efficiency
        db.query(ShortURL).filter(ShortURL.code == code).update(
            {ShortURL.hit_count: ShortURL.hit_count + increment}
        )
        flushed += 1

    db.commit()
    logger.info(f"✅ Flushed {flushed} counters to DB.")
