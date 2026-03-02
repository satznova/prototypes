# ─────────────────────────────────────────────────────────────
# STEP 2: Path Parameters & Query Parameters
#
# Concepts covered:
#   - Path parameters  → /users/{user_id}
#   - Query parameters → /search?q=hello&limit=10
#   - Type annotations → FastAPI validates and converts automatically
#   - Optional params  → with default values
#   - Enum params      → restrict to allowed values
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from enum import Enum
from typing import Optional

app = FastAPI(title="Path & Query Params")


# ── PATH PARAMETERS ───────────────────────────────────────────
# Curly braces in the path = path parameter.
# The function argument name must match exactly.
# FastAPI automatically parses it from the URL.

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # Type annotation int → FastAPI validates and converts automatically.
    # If you pass /users/abc → 422 Unprocessable Entity (not a valid int)
    # If you pass /users/42  → user_id = 42 (integer, not string)
    return {"user_id": user_id, "name": f"User number {user_id}"}


@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    # Multiple path parameters — all captured by position in the path
    return {
        "user_id": user_id,
        "post_id": post_id,
        "title": f"Post {post_id} by User {user_id}",
    }

# ── ROUTE ORDER MATTERS ────────────────────────────────────────
# FastAPI matches routes TOP TO BOTTOM.
# Put specific routes BEFORE parameterized ones, or they'll never match.

@app.get("/users/me")      # TRY these scenarios: Put this BEFORE and AFTER /users/{user_id}
def get_current_user():    # If /users/{user_id} came first, "me" would be treated as a user_id (and fail int conversion)
    return {"user": "me"}

# Try swapping the order of these two routes — see what breaks.


# ── QUERY PARAMETERS ──────────────────────────────────────────
# Any function parameter NOT in the path = query parameter automatically.
# Accessed as: /search?q=python&limit=5

@app.get("/search")
def search(q: str, limit: int = 10):
    # q      → required query param (no default = required)
    # limit  → optional query param (has default = optional)
    # URL: /search?q=python        → q="python", limit=10
    # URL: /search?q=python&limit=5 → q="python", limit=5
    # URL: /search                 → 422 error (q is required)
    return {
        "query": q,
        "limit": limit,
        "results": [f"Result {i} for '{q}'" for i in range(1, limit + 1)],
    }


# ── OPTIONAL QUERY PARAMETERS ─────────────────────────────────
# Use Optional[type] = None to make a query param truly optional

@app.get("/products")
def list_products(
    category: Optional[str] = None,   # Optional — defaults to None
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20,                   # Optional with default
):
    # URL: /products                          → all products
    # URL: /products?category=electronics    → filter by category
    # URL: /products?min_price=10&max_price=100

    # Simulate filtering
    products = [
        {"id": 1, "name": "Laptop",  "category": "electronics", "price": 999.0},
        {"id": 2, "name": "T-Shirt", "category": "clothing",    "price": 25.0},
        {"id": 3, "name": "Book",    "category": "education",   "price": 15.0},
        {"id": 4, "name": "Phone",   "category": "electronics", "price": 699.0},
    ]

    if category:
        products = [p for p in products if p["category"] == category]
    if min_price is not None:
        products = [p for p in products if p["price"] >= min_price]
    if max_price is not None:
        products = [p for p in products if p["price"] <= max_price]

    return {"total": len(products), "products": products[:limit]}


# ── ENUM PARAMETERS ───────────────────────────────────────────
# Restrict a parameter to a fixed set of allowed values.
# FastAPI validates automatically — invalid values return 422.

class SortOrder(str, Enum):
    asc  = "asc"
    desc = "desc"

class Category(str, Enum):
    electronics = "electronics"
    clothing    = "clothing"
    education   = "education"

@app.get("/sorted-products")
def sorted_products(
    sort_by: SortOrder = SortOrder.asc,
    category: Optional[Category] = None,
):
    # URL: /sorted-products?sort_by=asc
    # URL: /sorted-products?sort_by=invalid → 422 error automatically
    # In /docs, these show up as dropdowns (not free-text fields)
    return {
        "sort_by": sort_by,
        "category": category,
        "note": "Enums appear as dropdowns in /docs — try it!",
    }


# ── MIX: PATH + QUERY ─────────────────────────────────────────
@app.get("/users/{user_id}/orders")
def get_user_orders(
    user_id: int,               # path param
    status: Optional[str] = None,  # query param
    limit: int = 10,            # query param
):
    # URL: /users/42/orders?status=pending&limit=5
    return {
        "user_id": user_id,
        "status_filter": status,
        "limit": limit,
        "orders": [{"id": i, "status": status or "all"} for i in range(1, limit + 1)],
    }


# ── HTTP ERRORS ───────────────────────────────────────────────
# HTTPException raises proper HTTP error responses

@app.get("/items/{item_id}")
def get_item(item_id: int):
    items = {1: "Apple", 2: "Banana", 3: "Cherry"}

    if item_id not in items:
        # Returns: HTTP 404 with JSON body {"detail": "Item not found"}
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    return {"id": item_id, "name": items[item_id]}
