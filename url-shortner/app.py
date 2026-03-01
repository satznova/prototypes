"""
URL Shortener UI — Streamlit
-----------------------------
Covers all the key flows:
- Shorten a URL (with optional custom alias + TTL)
- Click a short URL and watch the counter increment
- View live stats (DB count vs Redis buffer)
- See top URLs leaderboard
- Manually flush Redis counters to DB

💡 Learning exercises:
1. Create a URL, click it multiple times, check stats — see Redis buffer vs DB count
2. Click 'Flush Counters' and watch DB count catch up
3. Create a URL with 1-hour TTL — observe it expires
4. Try the same long URL twice — see idempotency in action
5. Try a custom alias that's already taken — see 409 conflict
"""
import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="URL Shortener", layout="wide")
st.title("🔗 URL Shortener — System Design Prototype")

# Sidebar
st.sidebar.header("👤 User")
user_id = st.sidebar.text_input("User ID", value="user_alice")
st.sidebar.markdown("---")
st.sidebar.markdown("**Key Concepts**")
st.sidebar.markdown("""
- 🔑 **Base62** encoding of DB ID
- 🏎️ **Cache-aside** for redirects
- 📊 **Write-behind** hit counter
- ♻️ **Idempotency** on same URL
- ⏰ **TTL** expiry support
""")


# ── Tab Layout ────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["✂️ Shorten URL", "📊 Stats & Analytics", "🏆 Top URLs"])


# ── Tab 1: Shorten ─────────────────────────────────────────────
with tab1:
    st.header("Create a Short URL")

    long_url = st.text_input("Long URL", placeholder="https://www.example.com/some/very/long/path")

    col1, col2 = st.columns(2)
    with col1:
        custom_alias = st.text_input("Custom Alias (optional)", placeholder="my-link")
    with col2:
        expires_hours = st.number_input("Expires in (hours, 0 = never)", min_value=0, value=0)

    if st.button("🔗 Shorten"):
        if not long_url:
            st.warning("Please enter a URL")
        else:
            payload = {
                "long_url": long_url,
                "user_id": user_id,
                "custom_alias": custom_alias or None,
                "expires_in_hours": expires_hours if expires_hours > 0 else None,
            }
            resp = requests.post(f"{API_URL}/urls/", json=payload)

            if resp.status_code in (200, 201):
                data = resp.json()
                st.success("✅ Short URL created!")
                st.markdown(f"### 👉 [{data['short_url']}]({data['short_url']})")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Short Code", data["code"])
                col_b.metric("Hit Count", data["hit_count"])
                col_c.metric("Expires At", str(data["expires_at"] or "Never"))

                st.caption(f"💡 Submit the same URL again — you'll get the same code (idempotency)!")
            elif resp.status_code == 409:
                st.error(f"❌ {resp.json()['detail']}")
            else:
                st.error(f"Error: {resp.text}")

    st.markdown("---")
    st.subheader("🔁 Test Idempotency")
    st.caption("Submit any URL twice to see that the same short code is returned")

    st.subheader("⏰ Test TTL Expiry")
    st.caption("Set expires_in_hours=1, wait a moment, then try to access the URL — you'll get a 410 Gone")


# ── Tab 2: Stats ───────────────────────────────────────────────
with tab2:
    st.header("URL Stats")
    st.caption("Live hit count = DB count + Redis buffer (before next flush)")

    code_input = st.text_input("Enter short code (e.g. 1, 2, fastapi)", placeholder="fastapi")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Get Stats"):
            if code_input:
                resp = requests.get(f"{API_URL}/urls/{code_input}/stats")
                if resp.status_code == 200:
                    data = resp.json()
                    st.markdown(f"**URL:** {data['long_url']}")
                    st.markdown(f"**Short:** {data['short_url']}")

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Live Hit Count", data["hit_count_live"], help="DB count + Redis buffer")
                    m2.metric("DB Hit Count", data["hit_count_db"], help="Last flushed count")
                    m3.metric("Redis Buffer", data["hit_count_live"] - data["hit_count_db"], help="Unflushed hits")

                    st.caption(f"Expires: {data['expires_at'] or 'Never'}")
                else:
                    st.error(resp.json().get("detail", "Not found"))

    with col2:
        if st.button("🔄 Simulate 10 Clicks"):
            if code_input:
                with st.spinner("Simulating clicks..."):
                    for _ in range(10):
                        requests.get(f"{API_URL}/r/{code_input}", allow_redirects=False)
                        time.sleep(0.05)
                st.success("Done! Check stats to see Redis buffer grow.")

    st.markdown("---")
    st.subheader("🔧 Admin: Flush Counters")
    st.caption("In production, Cloud Scheduler calls this every 60 seconds automatically")

    if st.button("💾 Flush Redis Counters → DB"):
        resp = requests.post(f"{API_URL}/urls/admin/flush-counters")
        if resp.status_code == 200:
            st.success("✅ Counters flushed! Refresh stats to see DB count updated.")
        else:
            st.error("Flush failed")


# ── Tab 3: Top URLs ────────────────────────────────────────────
with tab3:
    st.header("🏆 Most Clicked URLs")
    st.caption("Leaderboard based on DB hit_count (updated after each flush)")

    if st.button("🔄 Refresh Leaderboard"):
        pass

    resp = requests.get(f"{API_URL}/urls/top?limit=10")
    if resp.status_code == 200:
        urls = resp.json()
        if urls:
            for i, url in enumerate(urls, 1):
                with st.container():
                    col1, col2, col3 = st.columns([1, 5, 2])
                    col1.markdown(f"**#{i}**")
                    col2.markdown(f"[{url['short_url']}]({url['short_url']})  \n`{url['long_url'][:60]}...`" if len(url['long_url']) > 60 else f"[{url['short_url']}]({url['short_url']})  \n`{url['long_url']}`")
                    col3.metric("Hits", url["hit_count"])
        else:
            st.info("No URLs yet. Create some in the Shorten tab!")
    else:
        st.error("Could not load leaderboard")
