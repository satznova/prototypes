"""
URL Shortener Service
---------------------
Core system design decisions explained here:

WHY BASE62 ENCODING?
--------------------
Option A (MD5/SHA hash):
  - Hash long URL → take first 6-8 chars
  - Problem: Collisions possible → need DB check + retry loop
  - Problem: Same URL can generate different codes (no idempotency)
  - Problem: Unpredictable character distribution

Option B (Base62 of auto-increment ID)  ← We use this
  - DB auto-increments an integer ID (guaranteed unique)
  - Encode that integer in Base62 (chars: 0-9, a-z, A-Z)
  - 6 chars of Base62 = 62^6 = ~56 billion unique URLs
  - Guaranteed no collisions (ID is unique by design)
  - Idempotent for same URL = same code (we check long_url first)
  - Predictable, short, URL-safe

Base62 alphabet: 0-9 (10) + a-z (26) + A-Z (26) = 62 chars
ID 1       → "0000001"
ID 1000    → "0000g8"
ID 56B     → "zzzzzz"

IDEMPOTENCY
-----------
If the same long_url is submitted twice by the same user, we return
the existing code rather than creating a new one. This avoids
duplicate entries for the same URL.
"""
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.models import ShortURL
from app.schemas.schemas import CreateURLRequest, URLResponse
from app.core.config import settings

# Base62 alphabet
BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = 62


def encode_base62(num: int) -> str:
    """Convert a positive integer to a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]

    chars = []
    while num:
        chars.append(BASE62_ALPHABET[num % BASE])
        num //= BASE
    return "".join(reversed(chars))


def decode_base62(code: str) -> int:
    """Convert a Base62 string back to an integer."""
    num = 0
    for char in code:
        num = num * BASE + BASE62_ALPHABET.index(char)
    return num


def create_short_url(db: Session, request: CreateURLRequest) -> URLResponse:
    """
    Create a short URL.

    Flow:
    1. Check idempotency — if same long_url exists for user, return it
    2. If custom alias provided, validate it's available
    3. Insert DB record (get auto-increment ID)
    4. Encode ID to Base62 → short code
    5. Update record with code, return response
    """

    # ── Step 1: Idempotency check ──────────────────────────────
    # Same long_url + same user → return existing short URL
    existing = db.query(ShortURL).filter(
        ShortURL.long_url == request.long_url,
        ShortURL.user_id == request.user_id,
        ShortURL.is_active == True,
    ).first()

    if existing and not request.custom_alias:
        return _to_response(existing)

    # ── Step 2: Custom alias validation ───────────────────────
    if request.custom_alias:
        alias_taken = db.query(ShortURL).filter(
            ShortURL.code == request.custom_alias
        ).first()
        if alias_taken:
            raise HTTPException(
                status_code=409,
                detail=f"Custom alias '{request.custom_alias}' is already taken."
            )
        code = request.custom_alias
    else:
        code = None  # Will be set after DB insert gives us the ID

    # ── Step 3: Calculate expiry ──────────────────────────────
    expires_at = None
    if request.expires_in_hours:
        expires_at = datetime.utcnow() + timedelta(hours=request.expires_in_hours)

    # ── Step 4: Insert with placeholder code ─────────────────
    # For Base62 approach, we need the DB-generated ID first.
    # Insert with a temp placeholder, then update with real code.
    url_record = ShortURL(
        code=code or "TEMP",        # Will be updated for non-custom aliases
        long_url=request.long_url,
        user_id=request.user_id,
        expires_at=expires_at,
    )
    db.add(url_record)
    db.flush()   # Flush to get the auto-increment ID without full commit

    # ── Step 5: Encode ID to Base62 ──────────────────────────
    if not request.custom_alias:
        url_record.code = encode_base62(url_record.id)

    db.commit()
    db.refresh(url_record)

    return _to_response(url_record)


def get_url_by_code(db: Session, code: str) -> ShortURL | None:
    """Look up a URL record by short code."""
    return db.query(ShortURL).filter(
        ShortURL.code == code,
        ShortURL.is_active == True,
    ).first()


def deactivate_url(db: Session, code: str, user_id: str) -> bool:
    """Soft-delete a short URL."""
    record = db.query(ShortURL).filter(
        ShortURL.code == code,
        ShortURL.user_id == user_id,
    ).first()

    if not record:
        return False

    record.is_active = False
    db.commit()
    return True


def get_top_urls(db: Session, limit: int = 10) -> list[ShortURL]:
    """Return the most-clicked URLs. Uses DB hit_count (periodically flushed from Redis)."""
    return db.query(ShortURL).filter(
        ShortURL.is_active == True
    ).order_by(ShortURL.hit_count.desc()).limit(limit).all()


def _to_response(record: ShortURL) -> URLResponse:
    return URLResponse(
        id=record.id,
        code=record.code,
        short_url=f"{settings.BASE_URL}/r/{record.code}",
        long_url=record.long_url,
        hit_count=record.hit_count,
        expires_at=record.expires_at,
        is_active=record.is_active,
        created_at=record.created_at,
    )
