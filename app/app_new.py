from fastapi import FastAPI

from app.models_new import (
    EmailRequest,
    TemplateRequest,
    AttachmentRequest,
    SmtpSettingsRequest
)

from pathlib import Path

from app.database_new import (
    send_to_sql,
    get_sent_emails,
    store_to_sql,
    retreive_templates,
    get_allemails,
    scheduled_emails_count,
    get_totalemails_count,
    sent_emails_count,
    failed_emails_count,
    get_pending_emails,
    save_smtp_settings,
    get_smtp_settings
)


app = FastAPI()


BASE_DIR = Path(__file__).parent.parent

REPORTS_FOLDER = BASE_DIR / "Reports"


def find_attachment(attachment_filename):

    matching_files = list(
        REPORTS_FOLDER.rglob(attachment_filename)
    )

    if not matching_files:
        return None

    selected_path = matching_files[0].resolve()

    reports_folder = REPORTS_FOLDER.resolve()

    if not selected_path.is_file():
        return None

    if reports_folder not in selected_path.parents:
        return None

    return selected_path


@app.post("/attachments/validate")
def validate_attachment(data: AttachmentRequest):

    selected_path = find_attachment(data.attachment_filename)

    if selected_path is None:

        return {
            "message": (
                "Please choose a file from the Reports folder."
            ),
            "attached": False
        }

    attachment_path = str(selected_path.relative_to(BASE_DIR))

    return {
        "message": "File attached successfully.",
        "attached": True,
        "attachment_path": attachment_path,
        "attachment_filename": selected_path.name
    }


@app.post("/emails")
def schedule(data: EmailRequest):

    attachment_path = None
    attachment_filename = None
    attachment_status = None

    if data.attach_document:

        if data.attachment_filename:

            selected_path = find_attachment(data.attachment_filename)

            if selected_path is None:

                return {
                    "message": (
                        "Please choose a file "
                        "from the Reports folder."
                    )
                }

            attachment_path = str(
                selected_path.relative_to(BASE_DIR)
            )

            attachment_filename = selected_path.name

            attachment_status = "Manual"

    send_to_sql(
        data,
        attachment_path,
        attachment_filename,
        attachment_status
    )

    return {
        "message": "Email Scheduled Successfully"
    }


@app.get("/emails")
def callallemails():

    all_emails = get_allemails()

    total_emails = get_totalemails_count()

    return all_emails, total_emails


@app.get("/emails/sent")
def callsent_emails():

    sent = get_sent_emails()

    sent_count = sent_emails_count()

    return sent, sent_count


@app.get("/emails/scheduled")
def callpendingemails():

    pending_emails = get_pending_emails()

    scheduled_count = scheduled_emails_count()

    return pending_emails, scheduled_count


@app.get("/emails/failed/count")
def get_failed_count():

    failed_count = failed_emails_count()

    return {"failed_count": failed_count}


@app.post("/smtp-settings")
def set_smtp_settings(data: SmtpSettingsRequest):

    save_smtp_settings(
        data.smtp_host,
        data.smtp_port,
        data.sender,
        data.password
    )

    return {
        "message": "SMTP settings saved successfully"
    }


@app.get("/smtp-settings/status")
def check_smtp_settings():

    settings = get_smtp_settings()

    if settings is None:

        return {
            "configured": False
        }

    return {
        "configured": True,
        "smtp_host": settings[1],
        "smtp_port": settings[2],
        "sender": settings[3]
    }


@app.post("/templates")
def store_templates(template_data: TemplateRequest):

    store_to_sql(template_data)

    return {"message": "Templates saved successfully"}


@app.get("/templates/{template_id}")
def get_stored_templates(template_id: int):

    get_templates = retreive_templates(template_id)

    return {
        "subject": get_templates[0],
        "body": get_templates[1]
    }