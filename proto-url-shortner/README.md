# URL Shortener — System Design Prototype

A production-like URL shortener covering core system design concepts hands-on.

## Architecture

```
Streamlit UI (Port 8501)
        ↓
FastAPI REST API (Port 8000)
        ↓
PostgreSQL (Cloud SQL)  ←→  Redis (Hot URL Cache + Hit Counter Buffer)
```

## Key Concepts Covered

| Concept | Where |
|---------|-------|
| **Hashing & Collision handling** | `services/shortener.py` — Base62 encoding of auto-increment ID |
| **Read-heavy caching** | Redis cache on every redirect — DB only on cache miss |
| **Write-behind counter** | Hit counts buffered in Redis, flushed to DB periodically |
| **TTL / Expiry** | URLs can have optional expiry dates |
| **Idempotency** | Same long URL always returns the same short code |
| **Custom aliases** | Users can request a custom short code |
| **Analytics** | Per-URL hit counts, top URLs leaderboard |

## Why Base62 over MD5?

MD5/SHA hashing requires collision checks and is unpredictable in length.
Base62 encoding of an auto-increment DB ID is:
- Guaranteed unique (ID is unique)
- Short (6 chars handles 56 billion URLs)
- No collision possible
- Sortable by creation time

## Project Structure

```
url-shortener/
├── app/
│   ├── main.py
│   ├── api/routes/
│   │   ├── urls.py          # Create, list, delete short URLs
│   │   └── redirect.py      # The core redirect endpoint
│   ├── core/
│   │   ├── config.py
│   │   └── redis_client.py
│   ├── db/
│   │   ├── database.py
│   │   └── init_db.py
│   ├── models/models.py
│   ├── schemas/schemas.py
│   └── services/
│       ├── shortener.py     # Base62 encoding + URL creation logic
│       └── counter.py       # Write-behind hit counter (Redis → DB)
├── streamlit_app/app.py
├── infra/
│   ├── Dockerfile.api
│   ├── docker-compose.yml
│   └── cloudbuild.yaml
└── requirements.txt
```

## Getting Started

```bash
# 1. Start all services
docker-compose -f infra/docker-compose.yml up

# 2. Seed DB schema
docker-compose exec api python -m app.db.init_db

# 3. Open UI
open http://localhost:8501

# 4. API docs
open http://localhost:8000/docs
```

## Key Design Decisions to Explore

1. **Cache-aside pattern**: Try disabling Redis and observe the latency difference
2. **Write-behind counters**: Hit counts are eventually consistent — by design
3. **Custom aliases**: What happens when two users request the same custom alias?
4. **TTL expiry**: Create a URL with 1-minute TTL and watch it expire
5. **Hot URL problem**: The same short URL cached in Redis handles millions of reads
