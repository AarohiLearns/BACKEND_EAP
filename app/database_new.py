import sqlite3

from pathlib import Path


BASE_DIR = Path(__file__).parent.parent

DATA_DIR = BASE_DIR / "data"

EMAILS_DB = DATA_DIR / "emails_new.db"

TEMPLATES_DB = DATA_DIR / "templates.db"


def create_emails_table():

    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        recipient TEXT,

        subject TEXT,

        message TEXT,

        attach_document INTEGER,

        attachment_path TEXT,

        attachment_filename TEXT,

        attachment_status TEXT,

        start_date TEXT,

        end_date TEXT,

        time TEXT,

        repeat_interval TEXT,

        status TEXT,

        max_occurrences INTEGER,

        occurrence_count INTEGER

    )
    """)

    conn.commit()

    conn.close()


def send_to_sql(
    data,
    attachment_path=None,
    attachment_filename=None,
    attachment_status=None
):

    create_emails_table()

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO emails(
        recipient, subject, message, attach_document,
        attachment_path, attachment_filename, attachment_status,
        start_date, end_date, time, repeat_interval, status,
        max_occurrences, occurrence_count
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
    (
        data.recipient,
        data.subject,
        data.message,
        int(data.attach_document),
        attachment_path,
        attachment_filename,
        attachment_status,
        data.start_date.strftime("%d-%m-%Y"),
        (data.end_date.strftime("%d-%m-%Y") if data.end_date else None),
        data.time.strftime("%H:%M"),
        data.repeat_interval,
        "Pending",
        data.max_occurrences,
        1
    ))

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    return new_id


def create_next_recurring_email(
    email,
    next_attachment_path,
    next_attachment_filename,
    next_attachment_status,
    next_date,
    next_time,
    next_occurrence_count
):
    """
    Creates the next recurring row.
    `next_date` / `next_time` MUST already be the correctly
    calculated next occurrence (current scheduled time + interval),
    computed by the caller (scheduler). This function does not
    do any date math itself.

    `next_occurrence_count` carries forward how many times this
    chain has now sent (including the one just sent), so the
    scheduler can compare it against max_occurrences on the next
    row too.
    """

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO emails(
        recipient, subject, message, attach_document,
        attachment_path, attachment_filename, attachment_status,
        start_date, end_date, time, repeat_interval, status,
        max_occurrences, occurrence_count
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
    (
        email[1],   # recipient
        email[2],   # subject
        email[3],   # message
        email[4],   # attach_document
        next_attachment_path,
        next_attachment_filename,
        next_attachment_status,
        next_date,
        email[9],   # end_date (unchanged)
        next_time,
        email[11],  # repeat_interval (unchanged)
        "Pending",
        email[13],  # max_occurrences (unchanged, carried forward)
        next_occurrence_count
    ))

    conn.commit()

    new_id = cursor.lastrowid

    conn.close()

    return new_id


def get_pending_emails():

    create_emails_table()

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM emails WHERE status='Pending'")

    emails = cursor.fetchall()

    conn.close()

    print()
    print("Pending emails:", emails)

    return emails


def update_status(email_id):

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("UPDATE emails SET status='Sent' WHERE id=?", (email_id,))

    conn.commit()

    print()
    print("DATABASE STATUS UPDATE")
    print("Email ID:", email_id)
    print("New Status: Sent")
    print("Rows Updated:", cursor.rowcount)

    conn.close()


def update_status_failed(email_id):

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("UPDATE emails SET status='Failed' WHERE id=?", (email_id,))

    conn.commit()

    print()
    print("DATABASE STATUS UPDATE")
    print("Email ID:", email_id)
    print("New Status: Failed")
    print("Rows Updated:", cursor.rowcount)

    conn.close()


def update_attachment_details(
    email_id,
    attachment_path,
    attachment_filename,
    attachment_status
):

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE emails
    SET attachment_path=?, attachment_filename=?, attachment_status=?
    WHERE id=?
    """,
    (attachment_path, attachment_filename, attachment_status, email_id))

    conn.commit()

    conn.close()


def store_to_sql(template_data):

    conn = sqlite3.connect(TEMPLATES_DB)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS templates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL
    )
    """)

    cursor.execute("""
    INSERT INTO templates(name, subject, body)
    VALUES(?,?,?)
    """,
    (template_data.name, template_data.subject, template_data.body))

    conn.commit()

    conn.close()


def retreive_templates(template_id):

    conn = sqlite3.connect(TEMPLATES_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT subject, body FROM templates WHERE id=?", (template_id,))

    template = cursor.fetchone()

    conn.close()

    return template


def failed_emails_count():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM emails WHERE status='Failed'")

    result = cursor.fetchone()[0]

    conn.close()

    return result


def sent_emails_count():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM emails WHERE status='Sent'")

    result = cursor.fetchone()[0]

    conn.close()

    return result


def get_sent_emails():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM emails WHERE status='Sent'")

    emails = cursor.fetchall()

    conn.close()

    return emails


def get_totalemails_count():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM emails")

    result = cursor.fetchone()[0]

    conn.close()

    return result


def scheduled_emails_count():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM emails WHERE status='Pending'")

    result = cursor.fetchone()[0]

    conn.close()

    return result


def get_allemails():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM emails")

    rows = cursor.fetchall()

    conn.close()

    return rows