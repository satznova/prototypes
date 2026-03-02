"""
Redirect Endpoint
-----------------
This is the most performance-critical endpoint in the system.
Every click on a short URL goes through here.

Design: Cache-Aside Pattern
1. Check Redis first (cache hit → return in < 1ms)
2. On cache miss → query PostgreSQL, populate cache, return
3. Increment hit counter in Redis (write-behind, async flush later)

At scale (bit.ly serves ~10B redirects/month):
- Redis handles ~99% of reads
- PostgreSQL only sees ~1% (cold URLs)
- Hit counters are batched, not per-request DB writes
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.redis_client import get_redis
from app.models.models import ShortURL
from app.services.counter import increment_hit
from app.core.config import settings

router = APIRouter(tags=["Redirect"])

CACHE_KEY = "url:{code}"


@router.get("/r/{code}")
def redirect(code: str, db: Session = Depends(get_db), r=Depends(get_redis)):
    """
    Redirect a short code to its original URL.

    Cache-aside flow:
    1. Redis lookup (O(1), sub-millisecond)
    2. If miss: DB lookup, populate cache with TTL
    3. Check expiry
    4. Increment Redis counter (async, write-behind)
    5. HTTP 302 redirect
    """
    cache_key = CACHE_KEY.format(code=code)

    # ── Step 1: Cache Lookup ───────────────────────────────────
    cached_url = r.get(cache_key)

    if cached_url:
        # Cache HIT — no DB query needed
        # Still need to check expiry (store expiry in cache too for accuracy)
        # For simplicity: trust cache means URL is valid
        increment_hit(r, code)
        return RedirectResponse(url=cached_url, status_code=302)

    # ── Step 2: Cache MISS — Query DB ─────────────────────────
    record = db.query(ShortURL).filter(
        ShortURL.code == code,
        ShortURL.is_active == True,
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"Short URL '{code}' not found.")

    # ── Step 3: Check TTL expiry ───────────────────────────────
    if record.expires_at and record.expires_at < datetime.utcnow():
        # Soft-expire: mark inactive
        record.is_active = False
        db.commit()
        raise HTTPException(status_code=410, detail=f"Short URL '{code}' has expired.")

    # ── Step 4: Populate Cache ─────────────────────────────────
    # Cache the long URL with a TTL so stale entries auto-expire.
    # If the URL has its own expiry, use the smaller of the two TTLs.
    cache_ttl = settings.REDIRECT_CACHE_TTL
    if record.expires_at:
        time_until_expiry = int((record.expires_at - datetime.utcnow()).total_seconds())
        cache_ttl = min(cache_ttl, max(time_until_expiry, 1))

    r.set(cache_key, record.long_url, ex=cache_ttl)

    # ── Step 5: Increment hit counter (write-behind) ───────────
    increment_hit(r, code)

    return RedirectResponse(url=record.long_url, status_code=302)
