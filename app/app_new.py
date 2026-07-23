from fastapi import FastAPI

from app.models_new import EmailRequest, TemplateRequest

from app.database_new import (
    send_to_sql,
    get_pending_emails,
    store_to_sql,
    retreive_templates,
    get_sent_emails,
    get_allemails,
    scheduled_emails_count,
    get_totalemails_count,
    sent_emails_count,
    failed_emails_count
)


app = FastAPI()


@app.post("/emails")
def schedule(data: EmailRequest):

    send_to_sql(data)

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

    return {
        "failed_count": failed_count
    }


@app.post("/templates")
def store_templates(template_data: TemplateRequest):

    store_to_sql(template_data)

    return {
        "message": "Templates saved successfully"
    }


@app.get("/templates/{template_id}")
def get_stored_templates(template_id: int):

    get_templates = retreive_templates(template_id)

    return {
        "subject": get_templates[0],
        "body": get_templates[1]
    }