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


st.set_page_config(
    page_title="Afterimage",
    page_icon="◉",
    layout="wide",
)

init_db()


if "flash_message" in st.session_state:
    st.success(st.session_state.pop("flash_message"))

st.title("◉ Afterimage")
st.caption("IT knowledge that stays. Local-first incident memory, powered by open AI.")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "New Incident", "Search Knowledge", "Incident History"],
)

st.sidebar.divider()

use_sample_data = st.sidebar.toggle(
    "Use Sample Knowledge Base",
    value=True,
    help=(
        "ON: Browse and search fictional sample incidents. "
        "OFF: Use your actual saved incidents."
    ),
)

# Select the active dataset without inserting anything into SQLite.
saved_incidents = get_all_incidents()

active_incidents = (
    SAMPLE_INCIDENTS + saved_incidents
    if use_sample_data
    else saved_incidents
)

# Clear previous search results when the source changes.
current_source = "samples" if use_sample_data else "saved"

if st.session_state.get("active_data_source") != current_source:
    st.session_state["active_data_source"] = current_source
    st.session_state.pop("search_matches", None)
    st.session_state.pop("search_query", None)
    st.session_state.pop("ai_analysis", None)

if page == "Dashboard":
    incidents = active_incidents

    source_label = (
        "Sample Knowledge Base"
        if use_sample_data
        else "Your Incident Knowledge"
    )

    st.subheader(source_label)

    if use_sample_data:
        st.info(
            "Viewing fictional sample incidents. "
            "These records are not saved to your database."
        )

    total = len(incidents)
    open_count = sum(
        incident.get("status") == "Open"
        for incident in incidents
    )
    resolved_count = sum(
        incident.get("status") == "Resolved"
        for incident in incidents
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total incidents", total)
    col2.metric("Open", open_count)
    col3.metric("Resolved", resolved_count)

    st.divider()
    st.subheader("Recently recorded incidents")

    if incidents:
        for incident in incidents[:5]:
            with st.container(border=True):
                record_id = incident.get("id")

                if record_id is not None:
                    heading = f"#{record_id} · {incident['title']}"
                else:
                    heading = f"Sample · {incident['title']}"

                st.markdown(f"**{heading}**")

                caption_parts = [
                    incident.get("category", "Other"),
                    incident.get("status", "Unknown"),
                ]

                if incident.get("created_at"):
                    st.caption(
                        f"Created: {incident['created_at']}"
                        + (
                            f" · Updated: {incident['updated_at']}"
                            if incident.get("updated_at")
                            else ""
                        )
                    )

                st.caption(" · ".join(caption_parts))
                st.write(incident.get("description", ""))

    else:
        st.info(
            "No incidents recorded yet. "
            "Switch to Sample Knowledge Base to explore examples, "
            "or record your first incident."
        )

    st.divider()
    st.caption(
        "Your saved incidents remain in your local database. "
        "Sample incidents are kept separate. "
        "AI analysis uses your local Ollama model."
    )


elif page == "New Incident":
    st.subheader("Record an incident")
    st.write("Capture the issue and its resolution so it can help with future cases.")

    form_version = st.session_state.get("new_incident_form_version", 0)

    with st.form(f"new_incident_form_{form_version}"):
            title = st.text_input("Incident title *")
    
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
    
            description = st.text_area("Issue description *")
            symptoms = st.text_area("Symptoms and error messages")
    
            st.markdown("### Affected System & User Details")
    
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
                placeholder="e.g., Windows update, new software, cable change.",
            )
    
            st.markdown("### Diagnosis & Resolution")
    
            root_cause = st.text_area(
                "Root cause (if known)",
            )
    
            resolution = st.text_area(
                "Resolution or troubleshooting performed",
            )
    
            status = st.selectbox(
                "Status",
                ["Open", "In Progress", "Resolved"],
            )
    
            submitted = st.form_submit_button(
                "Save incident",
                type="primary",
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


elif page == "Search Knowledge":
    st.subheader("Search incident memory")
    st.write(
        "Describe the current issue to find similar historical incidents, "
        "then ask the local AI to analyze the matches."
    )

    query = st.text_area(
        "Describe the issue",
        placeholder=(
            "Example: Warehouse printer is online but jobs remain "
            "stuck in the print queue."
        ),
        height=120,
    )

    if st.button("Find similar incidents", type="primary"):
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
                    
                    st.markdown(f"**{heading}**")
                    st.caption(
                        f"{incident['category']} · {incident['status']} · "
                        f"Keyword similarity: {incident['similarity_score']}%"
                    )
                    st.write(incident["description"])

                    if incident.get("symptoms"):
                        st.markdown("**Symptoms**")
                        st.write(incident["symptoms"])

                    if incident.get("root_cause"):
                        st.markdown("**Recorded root cause**")
                        st.write(incident["root_cause"])

                    if incident.get("resolution"):
                        st.markdown("**Recorded resolution**")
                        st.write(incident["resolution"])

                    st.caption(
                        "Matched terms: "
                        + ", ".join(incident["matched_terms"])
                    )

            st.divider()

            if st.button("Analyze with local AI", type="primary"):
                with st.spinner("Analyzing historical evidence with Ollama..."):
                    analysis = explain_similar_incidents(
                        st.session_state["search_query"],
                        matches,
                    )
                st.session_state["ai_analysis"] = analysis

            if "ai_analysis" in st.session_state:
                st.markdown("### Afterimage AI analysis")
                st.markdown(st.session_state["ai_analysis"])
                st.caption(
                    "AI suggestions are based on retrieved records and "
                    "may be incomplete. Verify findings before acting."
                )

        else:
            st.info(
                "No keyword matches found. Try describing the issue using "
                "different symptoms, error messages, or technical terms."
            )


elif page == "Incident History":
    st.subheader("Incident history")

    incidents = active_incidents

    if not incidents:
        st.info("No incidents recorded yet.")
    else:
        filter_status = st.selectbox(
            "Filter by status",
            ["All", "Open", "In Progress", "Resolved"],
        )

        filtered = [
            incident for incident in incidents
            if filter_status == "All" or incident["status"] == filter_status
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
                st.write(f"**Category:** {incident['category']}")
                st.write(f"**Description:** {incident['description']}")
                st.markdown("### Affected System & User")
                
                st.write(
                    f"**Hostname:** {incident.get('hostname') or 'Not provided'}"
                )
                
                st.write(
                    f"**Username:** {incident.get('username') or 'Not provided'}"
                )
                
                st.write(
                    f"**What happened:** "
                    f"{incident.get('trigger_context') or 'Not provided'}"
                )
                
                st.write(
                    f"**Recent changes:** "
                    f"{incident.get('recent_changes') or 'Not provided'}"
                )
                st.write(f"**Symptoms:** {incident['symptoms'] or '—'}")
                st.write(f"**Root cause:** {incident['root_cause'] or '—'}")
                st.write(f"**Resolution:** {incident['resolution'] or '—'}")
                if incident.get("created_at"):
                    st.caption(
                        f"Created: {incident['created_at']}"
                        + (
                            f" · Updated: {incident['updated_at']}"
                            if incident.get("updated_at")
                            else ""
                        )
                    )

            if not use_sample_data:
                with st.form(f"edit_incident_{incident['id']}"):
                    st.markdown("**Edit incident**")

                    edit_title = st.text_input(
                        "Title",
                        value=incident["title"],
                        key=f"title_{incident['id']}",
                    )
                    edit_description = st.text_area(
                        "Description",
                        value=incident["description"],
                        key=f"description_{incident['id']}",
                    )
                    edit_category = st.selectbox(
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
                        index=(
                            [
                                "Network",
                                "Printer",
                                "Hardware",
                                "Software",
                                "Account & Access",
                                "Operating System",
                                "Other",
                            ].index(incident["category"])
                            if incident["category"] in [
                                "Network",
                                "Printer",
                                "Hardware",
                                "Software",
                                "Account & Access",
                                "Operating System",
                                "Other",
                            ]
                            else 6
                        ),
                        key=f"category_{incident['id']}",
                    )
                    edit_symptoms = st.text_area(
                        "Symptoms",
                        value=incident["symptoms"] or "",
                        key=f"symptoms_{incident['id']}",
                    )
                    edit_root_cause = st.text_area(
                        "Root cause",
                        value=incident["root_cause"] or "",
                        key=f"root_{incident['id']}",
                    )
                    edit_resolution = st.text_area(
                        "Resolution",
                        value=incident["resolution"] or "",
                        key=f"resolution_{incident['id']}",
                    )
                    edit_status = st.selectbox(
                        "Status",
                        ["Open", "In Progress", "Resolved"],
                        index=["Open", "In Progress", "Resolved"].index(
                            incident["status"]
                        ),
                        key=f"status_{incident['id']}",
                    )

                    save_edit = st.form_submit_button("Save changes")

                    if save_edit:
                        if not edit_title.strip() or not edit_description.strip():
                            st.error("Title and description cannot be empty.")
                        else:
                            update_incident(
                                incident["id"],
                                title=edit_title.strip(),
                                description=edit_description.strip(),
                                category=edit_category,
                                symptoms=edit_symptoms.strip(),
                                root_cause=edit_root_cause.strip(),
                                resolution=edit_resolution.strip(),
                                status=edit_status,
                            )
                            st.success("Incident updated.")
                            st.rerun()

                if st.button(
                    "Delete incident",
                    key=f"delete_{incident['id']}",
                ):
                    st.session_state["confirm_delete"] = incident["id"]

                if st.session_state.get("confirm_delete") == incident["id"]:
                    st.warning("Are you sure you want to delete this incident?")
                    confirm_col, cancel_col = st.columns(2)

                    if confirm_col.button(
                        "Confirm delete",
                        key=f"confirm_{incident['id']}",
                    ):
                        delete_incident(incident["id"])
                        st.session_state.pop("confirm_delete", None)
                        st.rerun()

                    if cancel_col.button(
                        "Cancel",
                        key=f"cancel_{incident['id']}",
                    ):
                        st.session_state.pop("confirm_delete", None)
                        st.rerun()


