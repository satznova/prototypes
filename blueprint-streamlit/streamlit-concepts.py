import streamlit as st
from datetime import date

# ======================================================================================================================
# CONCEPT 1: st.set_page_config
# This must be the FIRST Streamlit call in your script. It controls the browser tab title, icon, and layout width.
# layout="wide" gives you more horizontal space.
# ======================================================================================================================
st.set_page_config(
    page_title="<Page Title Here>",
    page_icon="🤟",
    #layout="centered",
    layout = "wide",
)

# ============================================================
# CONCEPT 2: st.session_state
# Streamlit re-runs the entire script on every interaction. session_state is a persistent dictionary that survives re-runs.
# Use it to store submissions, flags, or any data you want to keep between interactions.
# We initialize keys here so they always exist.
# ============================================================
if "submissions" not in st.session_state:
    st.session_state.submissions = []

if "submitted" not in st.session_state:
    st.session_state.submitted = False


# ======================================================================================================================
# CONCEPT 3: st.title, st.markdown, st.caption
# These are simple display elements. Streamlit supports Markdown natively in most text elements.
# ======================================================================================================================
st.title("🤟 Blueprint Streamlit Form") # <h1>
st.caption("A Streamlit learning blueprint — every widget is annotated!")

# Divider between sections
st.divider()


# ======================================================================================================================
# CONCEPT 4: st.form
# A form groups widgets together. The script does NOT re-run when you interact with a widget inside a form — it only
# re-runs when the submit button is clicked.
# This is the right choice when you have multiple inputs that should be submitted together.
# Use: `with st.form("unique_key"):` as a context manager.
# ======================================================================================================================
with st.form("registration_form"):

    st.subheader("Personal Details") # <h3>

    # --------------------------------------------------------
    # CONCEPT 5: st.columns
    # Splits the layout into side-by-side columns.
    # st.columns(2) returns a list of 2 column objects.
    # Use `with col:` to place widgets inside a column.
    # --------------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        # ----------------------------------------------------
        # CONCEPT 6: st.text_input
        # A single-line text box. Returns the current string value.
        # `placeholder` shows greyed-out hint text.
        # ----------------------------------------------------
        first_name = st.text_input(
            "First Name",
            placeholder="e.g. Jane"
        )

    with col2:
        last_name = st.text_input(
            "Last Name",
            placeholder="e.g. Doe"
        )

    email = st.text_input(
        "Email Address",
        placeholder="jane.doe@example.com"
    )

    # --------------------------------------------------------
    # CONCEPT 7: st.date_input
    # A date picker widget. Returns a Python `datetime.date`.
    # `max_value` restricts the selectable range.
    # --------------------------------------------------------
    dob = st.date_input(
        "Date of Birth",
        value=date(1990, 1, 1),
        min_value=date(1920, 1, 1),
        max_value=date.today()
    )

    st.divider()
    st.subheader("Preferences")

    # --------------------------------------------------------
    # CONCEPT 8: st.selectbox
    # A dropdown with a single selection.
    # The second argument is the list of options.
    # Returns the selected value.
    # --------------------------------------------------------
    country = st.selectbox(
        "Country",
        options=["India", "United States", "United Kingdom", "Germany", "Australia", "Other"]
    )

    # --------------------------------------------------------
    # CONCEPT 9: st.multiselect
    # Like selectbox but allows multiple selections.
    # Returns a list of selected values.
    # `default` pre-selects items on first load.
    # --------------------------------------------------------
    interests = st.multiselect(
        "Areas of Interest",
        options=["Technology", "Finance", "Healthcare", "Education", "Design", "Science", "Sports", "Arts"],
        default=["Technology"]
    )

    # --------------------------------------------------------
    # CONCEPT 10: st.radio
    # Shows options as radio buttons (single choice).
    # `horizontal=True` lays them out in a row.
    # --------------------------------------------------------
    experience = st.radio(
        "Experience Level",
        options=["Beginner", "Intermediate", "Advanced"],
        horizontal=True
    )

    # --------------------------------------------------------
    # CONCEPT 11: st.slider
    # A numeric slider. Works for int, float, and even dates.
    # Returns the selected value.
    # --------------------------------------------------------
    age_pref = st.slider(
        "Preferred newsletter frequency (emails/month)",
        min_value=0,
        max_value=10,
        value=2
    )

    # --------------------------------------------------------
    # CONCEPT 12: st.checkbox
    # A simple boolean toggle. Returns True or False.
    # --------------------------------------------------------
    agree = st.checkbox("I agree to the terms and conditions")

    # --------------------------------------------------------
    # CONCEPT 13: st.form_submit_button
    # This is the submit trigger for the form.
    # It MUST be inside the `with st.form(...)` block.
    # Returns True only on the run immediately after clicking.
    # use_container_width=True stretches button to full width.
    # --------------------------------------------------------
    submitted = st.form_submit_button(
        "Submit Registration",
        use_container_width=True,
        type="primary"   # "primary" = filled blue, "secondary" = outline
    )


# ======================================================================================================================
# CONCEPT 14: Post-submit logic (outside the form)
# Code here runs on every re-run, but we gate it with the `submitted` flag returned by form_submit_button.
# This is where you validate inputs and show feedback.
# ======================================================================================================================
if submitted:

    # --- Validation ---
    errors = []

    if not first_name.strip():
        errors.append("First name is required.")
    if not last_name.strip():
        errors.append("Last name is required.")
    if not email.strip() or "@" not in email:
        errors.append("A valid email address is required.")
    if not interests:
        errors.append("Please select at least one area of interest.")
    if not agree:
        errors.append("You must agree to the terms and conditions.")

    if errors:
        # ----------------------------------------------------
        # CONCEPT 15: st.error, st.warning, st.success, st.info
        # Coloured alert boxes. Use them to communicate status.
        # st.error  → red
        # st.warning → yellow
        # st.success → green
        # st.info   → blue
        # ----------------------------------------------------
        for err in errors:
            st.error(f"❌ {err}")

    else:
        # Build the record
        record = {
            "Name": f"{first_name.strip()} {last_name.strip()}",
            "Email": email.strip(),
            "Date of Birth": str(dob),
            "Country": country,
            "Interests": ", ".join(interests),
            "Experience": experience,
            "Newsletter freq": f"{age_pref}/month",
        }

        # Save to session_state
        st.session_state.submissions.append(record)
        st.session_state.submitted = True

        st.success("✅ Registration successful!")

        # ----------------------------------------------------
        # CONCEPT 16: st.json
        # Renders a Python dict or list as a collapsible
        # JSON viewer. Great for debugging or showing data.
        # ----------------------------------------------------
        st.json(record)


# ============================================================
# CONCEPT 17: st.expander
# A collapsible section. Hidden by default unless
# expanded=True. Great for secondary content.
# ============================================================
if st.session_state.submissions:
    with st.expander(
            f"📁 View all submissions ({len(st.session_state.submissions)})"
            #expanded=True
            ):

        # ----------------------------------------------------
        # CONCEPT 18: st.dataframe
        # Renders a list of dicts (or a pandas DataFrame)
        # as an interactive, sortable table.
        # use_container_width=True fills the column width.
        # ----------------------------------------------------
        st.dataframe(
            st.session_state.submissions,
            use_container_width=True
        )

        # ----------------------------------------------------
        # CONCEPT 19: st.button (outside a form)
        # A standalone button that triggers a re-run when
        # clicked. Returns True on the click run only.
        # Here we use it to clear the submission history.
        # ----------------------------------------------------
        if st.button("🗑️ Clear all submissions"):
            st.session_state.submissions = []
            # -------------------------------------------------
            # CONCEPT 20: st.rerun
            # Forces an immediate re-run of the script.
            # Useful after mutating session_state so the UI
            # reflects the change right away.
            # -------------------------------------------------
            st.rerun()

# Footer
st.divider()
st.caption("Built with [Streamlit](https://streamlit.io) • Learning example")

