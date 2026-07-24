import sqlite3

from pathlib import Path


BASE_DIR = Path(__file__).parent.parent

DATA_DIR = BASE_DIR / "data"

EMAILS_DB = DATA_DIR / "emails_new.db"

TEMPLATES_DB = DATA_DIR / "templates.db"


def send_to_sql(
    data,
    attachment_path=None
):

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emails(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipient TEXT,
        subject TEXT,
        message TEXT,
        date TEXT,
        time TEXT,
        attach_document INTEGER,
        attachment_path TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO emails(
        recipient,
        subject,
        message,
        date,
        time,
        attach_document,
        attachment_path,
        status
    )
    VALUES(?,?,?,?,?,?,?,?)
    """,
    (
        data.recipient,
        data.subject,
        data.message,
        data.date.strftime(
            "%d-%m-%Y"
        ),
        data.time.strftime(
            "%H:%M"
        ),
        data.attach_document,
        attachment_path,
        "Pending"
    ))

    conn.commit()

    conn.close()


def get_pending_emails():

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM emails
    WHERE status='Pending'
    """)

    emails = cursor.fetchall()
    print("Pending emails:", emails)

    conn.close()

    return emails


def update_status(
    email_id
):

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE emails
    SET status='Sent'
    WHERE id=?
    """,
    (email_id,))

    conn.commit()

    conn.close()


def update_status_failed(
    email_id
):

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE emails
    SET status='Failed'
    WHERE id=?
    """,
    (email_id,))

    conn.commit()

    conn.close()


def store_to_sql(
    template_data
):

    conn = sqlite3.connect(
        TEMPLATES_DB
    )

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
    INSERT INTO templates(
        name,
        subject,
        body
    )
    VALUES(?,?,?)
    """,
    (
        template_data.name,
        template_data.subject,
        template_data.body
    ))

    conn.commit()

    conn.close()


def retreive_templates(
    template_id
):

    conn = sqlite3.connect(
        TEMPLATES_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT subject, body
    FROM templates
    WHERE id=?
    """,
    (template_id,))

    template = cursor.fetchone()

    conn.close()

    return template


def failed_emails_count():

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(status)
    FROM emails
    WHERE status='Failed'
    """)

    failed = cursor.fetchone()[0]

    conn.close()

    return failed


def sent_emails_count():

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(status)
    FROM emails
    WHERE status='Sent'
    """)

    sent = cursor.fetchone()[0]

    conn.close()

    return sent


def get_sent_emails():

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM emails
    WHERE status='Sent'
    """)

    emails = cursor.fetchall()

    conn.close()

    return emails


def get_totalemails_count():

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(recipient)
    FROM emails
    """)

    total_emails = cursor.fetchone()[0]

    conn.close()

    return total_emails


def scheduled_emails_count():

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(status)
    FROM emails
    WHERE status='Pending'
    """)

    scheduled_emails = cursor.fetchone()[0]

    conn.close()

    return scheduled_emails


def get_allemails():

    conn = sqlite3.connect(
        EMAILS_DB
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM emails
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows