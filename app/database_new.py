import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

EMAILS_DB = DATA_DIR / "emails_new.db"
TEMPLATES_DB = DATA_DIR / "templates.db"


def send_to_sql(data):

    conn = sqlite3.connect(EMAILS_DB)

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
        status
    )
    VALUES(?,?,?,?,?,?,?)
    """,
    (
        data.recipient,
        data.subject,
        data.message,
        data.date.strftime("%d-%m-%Y"),
        data.time.strftime("%H:%M"),
        data.attach_document,
        "Pending"
    ))

    conn.commit()

    conn.close()


def get_pending_emails():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM emails
    WHERE status='Pending'
    """)

    emails = cursor.fetchall()

    print("Pending Emails:", emails)

    conn.close()

    return emails


def update_status(email_id):

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE emails
    SET status='Sent'
    WHERE id=?
    """, (email_id,))

    conn.commit()

    print(f"Email {email_id} marked as Sent")

    conn.close()


def update_status_failed(email_id):

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    UPDATE emails
    SET status='Failed'
    WHERE id=?
    """, (email_id,))

    conn.commit()

    print(f"Email {email_id} marked as Failed")

    conn.close()


def store_to_sql(template_data, attachment_path):

    conn = sqlite3.connect(TEMPLATES_DB)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS templates(
        template_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        attachment_path TEXT
    )
    """)

    cursor.execute("""
    INSERT INTO templates(
        template_id,
        name,
        subject,
        body,
        attachment_path
    )
    VALUES(?,?,?,?,?)
    """,
    (
        template_data.template_id,
        template_data.name,
        template_data.subject,
        template_data.body,
        attachment_path
    ))

    conn.commit()

    conn.close()


def retreive_templates(template_id):

    conn = sqlite3.connect(TEMPLATES_DB)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT subject, body
    FROM templates
    WHERE template_id = ?
    """, (template_id,))

    get_template = cursor.fetchone()

    conn.close()

    return get_template


def get_attachment_path(template_id):

    conn = sqlite3.connect(TEMPLATES_DB)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT attachment_path
    FROM templates
    WHERE template_id = ?
    """, (template_id,))

    attachment = cursor.fetchone()

    conn.close()

    if attachment:
        return attachment[0]

    return None


def failed_emails_count():

    conn = sqlite3.connect(EMAILS_DB)

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

    conn = sqlite3.connect(EMAILS_DB)

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

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM emails
    WHERE status='Sent'
    """)

    emails = cursor.fetchall()

    print("Sent emails are", emails)

    conn.close()

    return emails


def get_totalemails_count():

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(recipient)
    FROM emails
    """)

    total_emails = cursor.fetchone()[0]

    conn.close()

    return total_emails


def scheduled_emails_count():

    conn = sqlite3.connect(EMAILS_DB)

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

    conn = sqlite3.connect(EMAILS_DB)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM emails
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows