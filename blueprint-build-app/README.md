

### Three Common Architectures
1. SIMPLE
   Streamlit ──────────────────► Postgres

2. STANDARD (most Production apps)
   Streamlit ──► REST/FastAPI ──► Postgres

3. FULL STACK (large teams)
   Streamlit ──► REST/FastAPI ──► Postgres
                     │
               Auth / Cache / Queue
               (JWT, Redis, Celery)



#### How to structure Architecture 2 (recommended for production)
my_app/
│
├── backend/                  # FastAPI — owns the DB
│   ├── main.py               # app entry point, mounts routers
│   ├── database.py           # DB connection pool (SQLAlchemy)
│   ├── models.py             # ORM table definitions
│   ├── schemas.py            # Pydantic request/response shapes
│   └── routers/
│       └── registrations.py  # POST /register, GET /registrations etc.
│
├── frontend/                 # Streamlit — owns the UI
│   ├── app.py                # main Streamlit app
│   └── api_client.py         # thin wrapper around requests calls
│
├── .streamlit/
│   └── secrets.toml          # API base URL + any tokens
│
└── docker-compose.yml        # spins up Postgres + FastAPI + Streamlit


