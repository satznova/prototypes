# URL Shortener — System Design Prototype

`Bit.ly` is a URL shortening service that converts long URLs into shorter, manageable links. 
It also provides analytics for the shortened URLs.

Build a production-like URL shortener covering core system design concepts hands-on.

## Functional Requirements

**Features of the System:** Features that the system should have to satisfy the User.

- Users should pass a long URL and get a shortened URL
  - Optional: Users can give Alias for the short URL
  - Optional: Users can specify Expiration date for the Shortened URL
- Users should able to access the original long URL by using the shortened URL (**Redirection**)

- For Same Long URL multiple short codes can be generated: Because different Users want different expiration date and independant analytics.
- OR we can Deduplicate can be done for an existing long URL return existing short code - this is a trades off Storage efficiency with above features.


## Non-Functional Requirements

**Qualities of the System:** Specifications about a system on how it operates.
**CAP Theorem:**  Availability >> Consistency | The systems can tolerate some inconsistency 

- Uniqueness of short URL
- Low Latency Redirection (<100ms)


## High-level Design

### Core Entities


### API
- Go one-by-one the Core requirements and define the APIs that are necessary to satisfy them

```
POST /create_short_code
GET /{short_code}
```

- POST:
  - Long URL, Optional: Alias, Expiration Date
  - To make an entry of long URL & short URL mapping in the Database

- GET:
  - GET the Long URL
  - Redirection with HTTP code 302


### Requirement 1: 


HTTP

- 404 Not Found: Resource might be temporarily unavailable
- 410 Gone: The requested resource is Gone for good and won't return

- 301 Permanent Redirect: Resources Permanently moved to target URL
  - Browsers cache this response. 
  - Subsequent Short URL requests directly goes to Long URL bypassing our server
- 302 Found: Resource is temporarily located at different URL
  - More control over redirect process - we can update Expire Links as needed
  - It prevents browser caching the redirect
  - Important: We can track Click Analytics for each short URL


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

```
my_app/
├── docker-compose.yml          ← spins up all 3 services
│
├── backend/                    ← FastAPI (owns DB)
│   ├── main.py                 ← app entry, mounts routers, CORS
│   ├── database.py             ← SQLAlchemy engine + connection pool
│   ├── models.py               ← ORM table definitions
│   ├── schemas.py              ← Pydantic request/response validation
│   ├── requirements.txt
│   ├── Dockerfile
│   └── routers/
│       └── registrations.py    ← POST, GET, DELETE endpoints
│
└── frontend/                   ← Streamlit (owns UI)
    ├── app.py                  ← UI only — zero SQL
    ├── api_client.py           ← only file that calls requests
    ├── requirements.txt
    ├── Dockerfile
    └── .streamlit/
        └── secrets.toml        ← API base URL
```

app.py          — Streamlit frontend 
api_client.py   — Streamlit's only connection to the backend


```shell
uvicorn routers/url_shortner:app --reload
streamlit run app.py
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
