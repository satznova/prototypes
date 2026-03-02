# ─────────────────────────────────────────────────────────────
# STEP 1: Hello World
#
# Concepts covered:
#   - Creating a FastAPI app
#   - Defining GET endpoints
#   - Returning JSON automatically
#   - Auto-generated /docs
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI

# ── Create the app ────────────────────────────────────────────
# This is the object uvicorn refers to in: uvicorn main:app
# The title and description show up in /docs
app = FastAPI(
    title="My First FastAPI App",
    description="Learning FastAPI step by step",
    version="1.0.0",
    # openapi_url=None # To disable the Docs (diables docs, redoc, openapi.json)
)


# ── Define a route ────────────────────────────────────────────
# A "Route" is also commonly called an "Endpoint" or a "Path"
# @app.get("/") registers this function as the handler for GET /
# FastAPI automatically converts the returned dict to JSON
@app.get("/")
def root():
    return {"message": "Hello, FastAPI!"}


# ── Another route ─────────────────────────────────────────────
# You can have as many routes as you want
# FastAPI maps each path + HTTP method to exactly one function
@app.get("/hello")
def hello():
    return {"greeting": "Welcome to FastAPI"}


# ── Route with a simple value ─────────────────────────────────
# Not just dicts — you can return strings, numbers, lists, etc.
# FastAPI serializes them all to JSON automatically
@app.get("/items")
def list_items():
    return ["apple", "banana", "cherry"]


@app.get("/status")
def status():
    return {
        "status": "running",
        "version": "1.0.0",
        "framework": "FastAPI",
    }
