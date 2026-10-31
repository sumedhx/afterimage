import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "afterimage.db"


def get_connection():
    """Create a database connection and ensure the database directory exists."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Create the incidents table if it does not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                symptoms TEXT DEFAULT '',
                resolution TEXT DEFAULT '',
                root_cause TEXT DEFAULT '',
                hostname TEXT DEFAULT '',
                username TEXT DEFAULT '',
                trigger_context TEXT DEFAULT '',
                recent_changes TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Safely add new columns to existing databases.
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(incidents)")
        }

        new_columns = {
            "hostname": "TEXT DEFAULT ''",
            "username": "TEXT DEFAULT ''",
            "trigger_context": "TEXT DEFAULT ''",
            "recent_changes": "TEXT DEFAULT ''",
        }

        for column, column_type in new_columns.items():
            if column not in existing_columns:
                conn.execute(
                    f"ALTER TABLE incidents ADD COLUMN {column} {column_type}"
                )


def create_incident(
    title,
    description,
    category,
    symptoms="",
    resolution="",
    root_cause="",
    hostname="",
    username="",
    trigger_context="",
    recent_changes="",
    status="Open",
):
    """Save a new incident and return its ID."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO incidents (
                title, description, category, symptoms,
                resolution, root_cause, hostname, username,
                trigger_context, recent_changes, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, description, category, symptoms,
            resolution, root_cause, hostname, username,
            trigger_context, recent_changes, status
        ))

        return cursor.lastrowid


def get_incident(incident_id):
    """Retrieve one incident by ID."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM incidents WHERE id = ?",
            (incident_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_incidents():
    """Retrieve all incidents, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM incidents ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def update_incident(incident_id, **fields):
    """Update supported incident fields."""
    allowed_fields = {
        "title", 
        "description", 
        "category", 
        "symptoms",
        "resolution", 
        "root_cause", 
        "status",         
        "hostname",
        "username",
        "trigger_context",
        "recent_changes",
    }

    updates = {
        key: value for key, value in fields.items()
        if key in allowed_fields
    }

    if not updates:
        return False

    updates["updated_at"] = "CURRENT_TIMESTAMP"

    assignments = ", ".join(
        f"{column} = ?" if column != "updated_at"
        else "updated_at = CURRENT_TIMESTAMP"
        for column in updates
    )

    values = [
        value for column, value in updates.items()
        if column != "updated_at"
    ]
    values.append(incident_id)

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE incidents SET {assignments} WHERE id = ?",
            values
        )
        return cursor.rowcount > 0


def delete_incident(incident_id):
    """Delete an incident by ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM incidents WHERE id = ?",
            (incident_id,)
        )
        return cursor.rowcount > 0


def seed_demo_incidents():
    """Add fictional demo incidents if the database is empty."""
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM incidents"
        ).fetchone()[0]

    if count > 0:
        return 0

    demos = [
        {
            "title": "Printer jobs stuck in queue",
            "description": "Office printer is online, but documents remain in the print queue and do not print.",
            "category": "Printer",
            "symptoms": "Jobs show pending status. Restarting the printer did not resolve the issue.",
            "root_cause": "Fictional example: a stuck print spooler service.",
            "resolution": "Fictional example: clear the stuck queue, restart the Print Spooler service, and test with a new document.",
            "status": "Resolved",
        },
        {
            "title": "Warehouse access point intermittently disconnects",
            "description": "Users lose Wi-Fi connectivity in one warehouse area for short periods.",
            "category": "Network",
            "symptoms": "Intermittent ping timeouts and brief connection drops.",
            "root_cause": "Not confirmed in this example.",
            "resolution": "Check access point uptime, switch port errors, power, and connectivity logs before identifying the cause.",
            "status": "Resolved",
        },
        {
            "title": "Laptop internal display appears black",
            "description": "Laptop powers on, but the internal screen appears black. An external monitor displays Windows.",
            "category": "Hardware",
            "symptoms": "Faint image visible under a flashlight; external display works.",
            "root_cause": "Possible backlight or display assembly fault; not confirmed.",
            "resolution": "Check display diagnostics and cable connections. Refer for hardware inspection if the issue persists.",
            "status": "In Progress",
        },
        {
            "title": "Outlook desktop cannot sign in",
            "description": "User can access Outlook on the web but cannot sign in through the desktop application.",
            "category": "Software",
            "symptoms": "Desktop sign-in fails while browser access works.",
            "root_cause": "Not confirmed in this example.",
            "resolution": "Verify account status, licensing, application sign-in state, and authentication errors.",
            "status": "Open",
        },
        {
            "title": "PC cannot print to network printer",
            "description": "A workstation cannot reach a network printer even though both devices appear powered on.",
            "category": "Network",
            "symptoms": "Print jobs fail; workstation and printer may be on different IP subnets.",
            "root_cause": "Possible network routing or VLAN configuration issue; not confirmed.",
            "resolution": "Check the workstation IP, subnet mask, gateway, printer IP, VLAN, and network reachability.",
            "status": "Resolved",
        },
    ]

    for incident in demos:
        create_incident(**incident)

    return len(demos)