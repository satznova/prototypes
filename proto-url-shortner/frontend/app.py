"""
app.py — Streamlit frontend
-----------------------------
This file contains ONLY UI code.
It never touches SQL, psycopg2, or SQLAlchemy.
All data operations go through api_client.py.

RUN WITH:
  streamlit run app.py
"""

import streamlit as st
from datetime import date, timedelta

import requests
import api_client

st.set_page_config(
    page_title="URL Shortner",
    layout="centered",
)

st.title("URL Shortener") # <h1>
st.caption("URL Shortner - Optional: Alias and Expiration date are allowed")
st.header("URL Shortener")

# Divider between sections
st.divider()

with (st.form("url_shortner_form")):
    st.text("Long URL")

    long_url = st.text_input(
        "Long URL",
        placeholder="e.g. www.example.com"
    )

    st.subheader("Optional Fields") # <h3>

    col1, col2 = st.columns(2)

    with col1:
        alias = st.text_input(
            "Alias",
            placeholder="abc"
        )

    with col2:
        exp_dt = st.date_input(
            "Expiration Date",
            value=date.today() + timedelta(days=1),
            min_value=date.today() + timedelta(days=1),
            max_value=date.today() + timedelta(days=365)
        )

    submitted = st.form_submit_button(
        "Create Shortened URL",
        use_container_width=True,
        type="primary"   # "primary" = filled blue, "secondary" = outline
    )

    if submitted:
        with st.spinner("Creating Shortened URL..."):
            try:
                result = api_client.post_long_url({
                    "long_url": long_url,
                    "alias": alias,
                    #, "exp_dt": exp_dt.tostring()
                })
                # response = requests.post(
                #     url=CREATE_SHORT_URL_API,
                #     json={"long_url": long_url, "alias": alias}, #, "exp_dt": exp_dt.tostring()},
                #     timeout=10
                # )
                st.success(f"API returned {result}")
                st.json(result) # Display as pretty-printed, interactive JSON string
            except requests.HTTPError as e:
                #handle_api_error(e)
                st.error(f"API returned an error {e}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot reach the API. Is the backend running?")
            except requests.exceptions.Timeout:
                st.error("Request timed out.")
