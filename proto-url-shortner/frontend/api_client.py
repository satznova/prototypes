"""
api_client.py — Streamlit's only connection to the backend
-----------------------------------------------------------
This module is the ONLY place in the frontend that knows the
API exists. All HTTP calls live here — app.py never imports `requests` directly. app.py imports `requests` for parsing the response HTTP Errors

WHY THIS PATTERN?
  • Single place to change the base URL or auth headers
  • Easy to mock in tests (just replace this module)
  • app.py stays focused on UI, not network concerns
  • If the API contract changes, you fix it here only

SECRETS:
  Base URL is read from .streamlit/secrets.toml so it can
  differ between local dev and production without code changes.
"""

import requests
import streamlit as st

BASE_URL    = st.secrets["api"]["base_url"]
TIMEOUT     = st.secrets["api"]["create_short_url_timeout"] # Always set this — without it a slow API hangs the app forever

# Function is for internal use within this module only
def _headers() -> dict:
    """
    Central place to add auth headers.
    If you add JWT auth later, put it here:
      return {"Authorization": f"Bearer {st.session_state.token}"}
    """
    return {"Content-Type": "application/json"}


def post_long_url(data: dict) -> dict:
    """
    POST /create_short_code/
    Returns the created record on success.
    Raises requests.HTTPError on 4xx/5xx.
    """
    response = requests.post(
        url = f"{BASE_URL}/create_short_code",
        json = data,
        headers = _headers(),
        timeout=TIMEOUT
    )
    response.raise_for_status() # If request is unsuccessful (4xx client error or 5xx server error), it automatically raises an HTTPError exception
    return response.json()
