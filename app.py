import streamlit as st

from src.database import (
    init_db,
    create_incident,
    get_all_incidents,
    update_incident,
    delete_incident,
)
from src.search import search_incidents
from src.ai import explain_similar_incidents
from src.sample_incidents import SAMPLE_INCIDENTS


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Afterimage",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

st.session_state.setdefault("use_sample_data", True)


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #f5f7f8;
        --surface: #ffffff;
        --text: #192f40;
        --muted: #718293;
        --border: #e1e8ed;
        --accent: #087f5b;
        --accent-hover: #066b4d;
        --accent-soft: #e8f5ef;
        --danger: #c43d4b;
    }

    /* Main application */
    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1440px;
        padding: 1.5rem 2.5rem 2rem;
        margin-top: 3rem; #Added to so stremline toolbar have space doent block our header
    }

    /* Typography */
    h1, h2, h3, h4 {
        color: var(--text) !important;
        letter-spacing: -0.035em;
    }

    h1 {
        font-size: 2.15rem !important;
        font-weight: 780 !important;
    }

    h2 {
        font-size: 1.65rem !important;
        font-weight: 730 !important;
    }

    h3 {
        font-size: 1.15rem !important;
        font-weight: 680 !important;
    }

    p, li, label {
        color: #34495a;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted) !important;
    }

    /* Application header */
    .app-brand {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.055em;
        color: var(--text);
        line-height: 1.2;
    }

    .app-brand-symbol {
        color: var(--accent);
    }

    .app-subtitle {
        color: var(--muted);
        font-size: 0.96rem;
        margin-top: 0.45rem;
    }

    .workspace-badge {
        display: inline-block;
        padding: 0.65rem 0.9rem;
        background: var(--accent-soft);
        color: var(--accent);
        border: 1px solid #c9e8d8;
        border-radius: 10px;
        font-size: 0.78rem;
        font-weight: 750;
        text-align: center;
        white-space: nowrap;
    }

    /* Separators */
    hr {
        border-color: var(--border) !important;
        margin: 1.5rem 0 !important;
    }

    /* Main navigation */
    div[role="radiogroup"] {
        gap: 0.5rem;
    }

    div[role="radiogroup"] label {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 9px;
        padding: 0.55rem 0.85rem;
        transition: border-color 0.15s ease,
                    background 0.15s ease;
    }

    div[role="radiogroup"] label:hover {
        border-color: var(--accent);
        background: var(--accent-soft);
    }

    /* Buttons */
    .stButton > button,
    .stFormSubmitButton > button {
        min-height: 2.65rem;
        border-radius: 9px;
        font-weight: 650;
        border: 1px solid #d5e0e7;
        transition: background 0.15s ease;
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"] {
        background: var(--accent);
        color: #ffffff;
        border-color: var(--accent);
    }

    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover {
        background: var(--accent-hover);
        color: #ffffff;
        border-color: var(--accent-hover);
    }

    /* Text inputs */
    .stTextInput input,
    .stTextArea textarea {
        background: #ffffff;
        color: var(--text);
        border: 1px solid #ccd7df;
        border-radius: 9px;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 1px var(--accent);
    }

    /* Dropdowns */
    div[data-baseweb="select"] > div {
        background: #ffffff;
        border-color: #ccd7df;
        border-radius: 9px;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 2px 6px rgba(25, 47, 64, 0.025);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-weight: 780;
    }

    /* Incident containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-testid="stExpander"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    [data-testid="stExpander"] summary {
        color: var(--text);
        font-weight: 650;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Progress bars */
    [data-testid="stProgress"] > div > div {
        background: var(--accent);
    }

    /* Links */
    .stApp a {
        color: var(--accent) !important;
    }

    /* Footer: compact, vertical, and consistent with the workspace */
    .afterimage-footer {
        position: relative;
        overflow: hidden;
        margin-top: 3rem;
        padding: 2.6rem 1.25rem 2.2rem;
        border: 1px solid #1d5945;
        border-top: 4px solid #2ca77b;
        border-radius: 15px 15px 10px 10px;
        background: linear-gradient(145deg, #143f31 0%, #102f27 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.55rem;
        text-align: center;
    }

    .footer-brand {
        color: #ffffff !important;
        font-size: 1.55rem;
        font-weight: 820;
        letter-spacing: -0.04em;
        line-height: 1.3;
        margin-bottom: 0.25rem;
    }

    .footer-description {
        color: #c5ded4 !important;
        font-size: 0.92rem;
        line-height: 1.55;
        margin: 0;
    }

    .footer-links {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-top: 0.85rem;
    }

    .footer-links a {
        display: inline-block;
        color: #a9e2c8 !important;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 0.15rem 0.4rem;
        transition: color 0.15s ease, transform 0.15s ease;
    }

    .footer-links a:hover {
        color: #ffffff !important;
        text-decoration: underline;
        transform: translateY(-1px);
    }

    /* Mobile */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.9rem 1.5rem;
        }

        .app-brand {
            font-size: 1.8rem;
        }

        .app-subtitle {
            font-size: 0.85rem;
        }

        h1 {
            font-size: 1.75rem !important;
        }

        h2 {
            font-size: 1.4rem !important;
        }

        h3 {
            font-size: 1.1rem !important;
        }

        /* Let navigation wrap on narrow screens */
        div[role="radiogroup"] {
            flex-wrap: wrap;
            gap: 0.4rem;
        }

        div[role="radiogroup"] label {
            padding: 0.45rem 0.55rem;
        }

        [data-testid="stMetric"] {
            padding: 0.8rem;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.8rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.35rem;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            width: 100%;
            min-height: 2.8rem;
        }

        .stTextInput input,
        .stTextArea textarea {
            font-size: 16px;
        }

        .workspace-badge {
            font-size: 0.7rem;
            padding: 0.5rem;
        }

        .afterimage-footer {
            align-items: center;
            padding: 2rem 1rem;
            text-align: center;
        }

        .footer-links {
            align-items: center;
            gap: 0.7rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FLASH MESSAGES
# ============================================================

if "flash_message" in st.session_state:
    st.success(st.session_state.pop("flash_message"))


# ============================================================
# HEADER
# ============================================================

header_col, badge_col = st.columns([3, 1])

with header_col:
    st.markdown(
        """
        <div class="app-brand">
            <span class="app-brand-symbol">◉</span> Afterimage
        </div>
        <div class="app-subtitle">
            IT incident intelligence · Local-first knowledge
        </div>
        """,
        unsafe_allow_html=True,
    )

with badge_col:
    st.markdown(
        """
        <div style="text-align: right; padding-top: 0.35rem;">
            <span class="workspace-badge">
                ● LOCAL WORKSPACE
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ============================================================
# NAVIGATION
# ============================================================

page = st.radio(
    "Navigate",
    [
        "Dashboard",
        "New Incident",
        "Search Knowledge",
        "Incident History",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="main_navigation",
)


# ============================================================
# SAMPLE DATA SELECTION
# ============================================================

# The toggle is displayed on the Dashboard.
# Its state remains available when navigating to other pages.

if page == "Dashboard":
    st.markdown("### Knowledge source")

    st.toggle(
        "Include Sample Knowledge Base",
        key="use_sample_data",
        help=(
            "ON: Search fictional sample incidents alongside your saved "
            "incidents. OFF: Use only incidents saved in your database."
        ),
    )

    if st.session_state["use_sample_data"]:
        st.info(
            "Sample knowledge is enabled. Fictional sample incidents "
            "are shown alongside your saved incidents. "
            "Samples are not inserted into your database."
        )
    else:
        st.caption(
            "Showing incidents saved in your local database."
        )


# Retrieve saved incidents and select the active dataset.
saved_incidents = get_all_incidents()

active_incidents = (
    SAMPLE_INCIDENTS + saved_incidents
    if st.session_state["use_sample_data"]
    else saved_incidents
)

# Clear previous search results when the source changes.
current_source = (
    "samples"
    if st.session_state["use_sample_data"]
    else "saved"
)

if st.session_state.get("active_data_source") != current_source:
    st.session_state["active_data_source"] = current_source
    st.session_state.pop("search_matches", None)
    st.session_state.pop("search_query", None)
    st.session_state.pop("ai_analysis", None)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    incidents = active_incidents

    st.markdown("## Incident overview")
    st.caption(
        "A quick view of the incidents available in your knowledge base."
    )

    total = len(incidents)

    open_count = sum(
        incident.get("status") == "Open"
        for incident in incidents
    )

    in_progress_count = sum(
        incident.get("status") == "In Progress"
        for incident in incidents
    )

    resolved_count = sum(
        incident.get("status") == "Resolved"
        for incident in incidents
    )

    # Responsive metric layout.
    metric_cols = st.columns(4)

    metric_cols[0].metric(
        "Total incidents",
        total,
    )

    metric_cols[1].metric(
        "Open",
        open_count,
    )

    metric_cols[2].metric(
        "In progress",
        in_progress_count,
    )

    metric_cols[3].metric(
        "Resolved",
        resolved_count,
    )

    st.divider()

    # Quick actions.
    st.markdown("### Quick actions")
    st.caption("Choose what you want to do next.")

    action_cols = st.columns(2)

    with action_cols[0]:
        with st.container(border=True):
            st.markdown("#### Search incident knowledge")
            st.write(
                "Find similar incidents and review previous "
                "troubleshooting and resolutions."
            )

            if st.button(
                "Search knowledge →",
                type="primary",
                key="dashboard_search",
                use_container_width=True,
            ):
                st.session_state["main_navigation"] = "Search Knowledge"
                st.rerun()

    with action_cols[1]:
        with st.container(border=True):
            st.markdown("#### Record an incident")
            st.write(
                "Document a technical issue, its symptoms, "
                "root cause, and resolution."
            )

            if st.button(
                "Create incident →",
                key="dashboard_new_incident",
                use_container_width=True,
            ):
                st.session_state["main_navigation"] = "New Incident"
                st.rerun()

    st.divider()

    # Recent incidents.
    st.markdown("### Recent incidents")
    st.caption("The latest incidents available in the active knowledge base.")

    if incidents:

        for incident in incidents[:5]:

            with st.container(border=True):

                record_id = incident.get("id")

                if record_id is not None:
                    heading = f"#{record_id} · {incident['title']}"
                else:
                    heading = f"Sample · {incident['title']}"

                st.markdown(f"**{heading}**")

                category = incident.get("category", "Other")
                status = incident.get("status", "Unknown")

                st.caption(f"{category} · {status}")

                description = incident.get("description", "")

                if description:
                    st.write(description)

                if incident.get("created_at"):
                    st.caption(
                        f"Created: {incident['created_at']}"
                    )

    else:

        st.info(
            "Your knowledge base is empty. Create your first incident "
            "or enable the Sample Knowledge Base above to explore examples."
        )

    st.divider()

    st.caption(
        "Your saved incidents remain in your local database. "
        "Sample incidents are kept separate. "
        "AI analysis uses your local Ollama model."
    )


# ============================================================
# NEW INCIDENT
# ============================================================

elif page == "New Incident":

    st.markdown("## Record an incident")

    st.caption(
        "Capture the issue and its resolution so it can help with future cases."
    )

    form_version = st.session_state.get(
        "new_incident_form_version",
        0,
    )

    with st.form(f"new_incident_form_{form_version}"):

        st.markdown("### Incident details")

        title = st.text_input(
            "Incident title *",
            placeholder="e.g., Warehouse printer jobs stuck in queue",
        )

        category = st.selectbox(
            "Category",
            [
                "Network",
                "Printer",
                "Hardware",
                "Software",
                "Account & Access",
                "Operating System",
                "Other",
            ],
        )

        description = st.text_area(
            "Issue description *",
            placeholder=(
                "Describe the issue, what is affected, "
                "and when it started."
            ),
        )

        symptoms = st.text_area(
            "Symptoms and error messages",
            placeholder="Describe error messages or observable symptoms.",
        )

        st.markdown("### Affected system and user")

        hostname = st.text_input(
            "Hostname / System Name",
            placeholder="e.g., WH-PC-014",
        )

        username = st.text_input(
            "Username",
            placeholder="e.g., user01",
        )

        trigger_context = st.text_area(
            "What was the user doing when the issue occurred?",
            placeholder="e.g., The issue started while printing a PDF.",
        )

        recent_changes = st.text_area(
            "Recent changes (if any)",
            placeholder=(
                "e.g., Windows update, new software, cable change."
            ),
        )

        st.markdown("### Diagnosis and resolution")

        root_cause = st.text_area(
            "Root cause (if known)",
            placeholder="Describe the suspected or confirmed root cause.",
        )

        resolution = st.text_area(
            "Resolution or troubleshooting performed",
            placeholder="Record the troubleshooting steps and final resolution.",
        )

        status = st.selectbox(
            "Status",
            ["Open", "In Progress", "Resolved"],
        )

        submitted = st.form_submit_button(
            "Save incident",
            type="primary",
            use_container_width=True,
        )

        if submitted:

            if not title.strip() or not description.strip():

                st.error(
                    "Please enter both a title and an issue description."
                )

            else:

                incident_id = create_incident(
                    title=title.strip(),
                    description=description.strip(),
                    category=category,
                    symptoms=symptoms.strip(),
                    root_cause=root_cause.strip(),
                    resolution=resolution.strip(),
                    hostname=hostname.strip(),
                    username=username.strip(),
                    trigger_context=trigger_context.strip(),
                    recent_changes=recent_changes.strip(),
                    status=status,
                )

                st.session_state["flash_message"] = (
                    f"Incident #{incident_id} — "
                    f"'{title.strip()}' added successfully!"
                )

                st.session_state["new_incident_form_version"] = (
                    form_version + 1
                )

                st.rerun()


# ============================================================
# SEARCH KNOWLEDGE
# ============================================================

elif page == "Search Knowledge":

    st.markdown("## Search incident knowledge")

    st.caption(
        "Describe the current issue to find similar historical incidents, "
        "then ask your local AI to analyze the matches."
    )

    if st.session_state["use_sample_data"]:
        st.info(
            "Sample knowledge is enabled. Search includes sample incidents "
            "and incidents saved in your database."
        )

    query = st.text_area(
        "Describe the issue",
        placeholder=(
            "Example: Warehouse printer is online but jobs remain "
            "stuck in the print queue."
        ),
        height=120,
        key="incident_search_input",
    )

    if st.button(
        "Find similar incidents",
        type="primary",
        use_container_width=True,
    ):

        if not query.strip():

            st.warning("Enter an issue description first.")

        else:

            matches = search_incidents(
                query.strip(),
                limit=5,
                incidents=active_incidents,
            )

            st.session_state["search_query"] = query.strip()
            st.session_state["search_matches"] = matches

            # Remove analysis from the previous search.
            st.session_state.pop("ai_analysis", None)

    if "search_matches" in st.session_state:

        matches = st.session_state["search_matches"]

        if matches:

            st.markdown("### Historical matches")

            for incident in matches:

                with st.container(border=True):

                    record_id = incident.get("id")

                    if record_id is not None:
                        heading = f"#{record_id} · {incident['title']}"
                    else:
                        heading = f"Sample · {incident['title']}"

                    st.markdown(f"#### {heading}")

                    category = incident.get("category", "Other")
                    status = incident.get("status", "Unknown")
                    score = float(
                        incident.get("similarity_score", 0)
                    )

                    st.caption(f"{category} · {status}")

                    st.progress(
                        max(0.0, min(1.0, score / 100)),
                        text=f"Match score · {score:.1f}%",
                    )

                    st.write(
                        incident.get("description", "")
                    )

                    if incident.get("symptoms"):

                        st.markdown("**Symptoms**")
                        st.write(incident["symptoms"])

                    if incident.get("root_cause"):

                        st.markdown("**Recorded root cause**")
                        st.write(incident["root_cause"])

                    if incident.get("resolution"):

                        st.markdown("**Recorded resolution**")
                        st.write(incident["resolution"])

                    matched_terms = incident.get("matched_terms", [])

                    if matched_terms:

                        st.caption(
                            "Matched terms: "
                            + ", ".join(matched_terms)
                        )

            st.divider()

            if st.button(
                "Analyze with local AI",
                type="primary",
                use_container_width=True,
            ):

                with st.spinner(
                    "Analyzing historical evidence with Ollama..."
                ):

                    analysis = explain_similar_incidents(
                        st.session_state["search_query"],
                        matches,
                    )

                st.session_state["ai_analysis"] = analysis

            if "ai_analysis" in st.session_state:

                st.markdown("### Afterimage AI analysis")

                st.markdown(
                    st.session_state["ai_analysis"]
                )

                st.caption(
                    "AI suggestions are based on retrieved records and "
                    "may be incomplete. Verify findings before acting."
                )

        else:

            st.info(
                "No relevant incidents found. Try describing the issue "
                "using different symptoms, error messages, or technical terms."
            )


# ============================================================
# INCIDENT HISTORY
# ============================================================

elif page == "Incident History":

    st.markdown("## Incident history")

    st.caption(
        "Browse, review, update, and delete your saved incident records."
    )

    incidents = active_incidents

    if not incidents:

        st.info(
            "No incidents available. Record your first incident "
            "or enable the Sample Knowledge Base on the Dashboard."
        )

    else:

        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Open", "In Progress", "Resolved"],
        )

        filtered = [
            incident
            for incident in incidents
            if (
                filter_status == "All"
                or incident.get("status") == filter_status
            )
        ]

        st.caption(
            f"Showing {len(filtered)} of {len(incidents)} incidents."
        )

        category_options = [
            "Network",
            "Printer",
            "Hardware",
            "Software",
            "Account & Access",
            "Operating System",
            "Other",
        ]

        status_options = [
            "Open",
            "In Progress",
            "Resolved",
        ]

        for incident in filtered:

            record_id = incident.get("id")

            display_id = (
                f"#{record_id}"
                if record_id is not None
                else "Sample"
            )

            with st.expander(
                f"{display_id} · {incident['title']} "
                f"— {incident.get('status', 'Unknown')}"
            ):

                st.write(
                    f"**Category:** {incident.get('category', 'Other')}"
                )

                st.write(
                    f"**Description:** "
                    f"{incident.get('description') or '—'}"
                )

                st.markdown("### Affected system and user")

                st.write(
                    f"**Hostname:** "
                    f"{incident.get('hostname') or 'Not provided'}"
                )

                st.write(
                    f"**Username:** "
                    f"{incident.get('username') or 'Not provided'}"
                )

                st.write(
                    f"**What happened:** "
                    f"{incident.get('trigger_context') or 'Not provided'}"
                )

                st.write(
                    f"**Recent changes:** "
                    f"{incident.get('recent_changes') or 'Not provided'}"
                )

                st.markdown("### Diagnosis and resolution")

                st.write(
                    f"**Symptoms:** "
                    f"{incident.get('symptoms') or '—'}"
                )

                st.write(
                    f"**Root cause:** "
                    f"{incident.get('root_cause') or '—'}"
                )

                st.write(
                    f"**Resolution:** "
                    f"{incident.get('resolution') or '—'}"
                )

                if incident.get("created_at"):

                    timestamp = f"Created: {incident['created_at']}"

                    if incident.get("updated_at"):
                        timestamp += (
                            f" · Updated: {incident['updated_at']}"
                        )

                    st.caption(timestamp)

            # Sample records have no database ID and cannot be edited.
            # Saved records remain editable even when samples are enabled.
            if record_id is not None:

                with st.form(f"edit_incident_{record_id}"):

                    st.markdown("**Edit incident**")

                    edit_title = st.text_input(
                        "Title",
                        value=incident.get("title", ""),
                        key=f"title_{record_id}",
                    )

                    edit_description = st.text_area(
                        "Description",
                        value=incident.get("description", ""),
                        key=f"description_{record_id}",
                    )

                    current_category = incident.get(
                        "category",
                        "Other",
                    )

                    category_index = (
                        category_options.index(current_category)
                        if current_category in category_options
                        else category_options.index("Other")
                    )

                    edit_category = st.selectbox(
                        "Category",
                        category_options,
                        index=category_index,
                        key=f"category_{record_id}",
                    )

                    edit_symptoms = st.text_area(
                        "Symptoms",
                        value=incident.get("symptoms") or "",
                        key=f"symptoms_{record_id}",
                    )

                    edit_root_cause = st.text_area(
                        "Root cause",
                        value=incident.get("root_cause") or "",
                        key=f"root_{record_id}",
                    )

                    edit_resolution = st.text_area(
                        "Resolution",
                        value=incident.get("resolution") or "",
                        key=f"resolution_{record_id}",
                    )

                    current_status = incident.get("status", "Open")

                    status_index = (
                        status_options.index(current_status)
                        if current_status in status_options
                        else 0
                    )

                    edit_status = st.selectbox(
                        "Status",
                        status_options,
                        index=status_index,
                        key=f"status_{record_id}",
                    )

                    save_edit = st.form_submit_button(
                        "Save changes",
                        use_container_width=True,
                    )

                    if save_edit:

                        if (
                            not edit_title.strip()
                            or not edit_description.strip()
                        ):

                            st.error(
                                "Title and description cannot be empty."
                            )

                        else:

                            update_incident(
                                record_id,
                                title=edit_title.strip(),
                                description=edit_description.strip(),
                                category=edit_category,
                                symptoms=edit_symptoms.strip(),
                                root_cause=edit_root_cause.strip(),
                                resolution=edit_resolution.strip(),
                                status=edit_status,
                            )

                            st.session_state["flash_message"] = (
                                f"Incident #{record_id} updated successfully."
                            )

                            st.rerun()

                delete_key = f"delete_{record_id}"
                confirm_key = f"confirm_delete_{record_id}"

                if st.button(
                    "Delete incident",
                    key=delete_key,
                ):

                    st.session_state["confirm_delete"] = record_id

                if st.session_state.get("confirm_delete") == record_id:

                    st.warning(
                        "Are you sure you want to permanently delete "
                        "this incident?"
                    )

                    confirm_col, cancel_col = st.columns(2)

                    with confirm_col:

                        if st.button(
                            "Confirm delete",
                            key=f"confirm_{record_id}",
                            type="primary",
                            use_container_width=True,
                        ):

                            delete_incident(record_id)

                            st.session_state.pop(
                                "confirm_delete",
                                None,
                            )

                            st.session_state["flash_message"] = (
                                f"Incident #{record_id} deleted."
                            )

                            st.rerun()

                    with cancel_col:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{record_id}",
                            use_container_width=True,
                        ):

                            st.session_state.pop(
                                "confirm_delete",
                                None,
                            )

                            st.rerun()

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <footer class="afterimage-footer">
        <div class="footer-brand">◉ Afterimage</div>
        <p class="footer-description">Built by Sumedh Suralkar</p>
        <p class="footer-description">Local-first IT incident knowledge</p>
        <nav class="footer-links" aria-label="Creator links">
            <a href="mailto:sumedhsuralkar@gmail.com">Email</a>
            <a href="https://github.com/sumedhx" target="_blank" rel="noopener noreferrer">GitHub Profile</a>
            <a href="https://github.com/sumedhx/afterimage" target="_blank" rel="noopener noreferrer">Source Code</a>
        </nav>
    </footer>
    """,
    unsafe_allow_html=True,
)
