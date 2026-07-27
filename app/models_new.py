from datetime import date, time

from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):

    recipient: EmailStr

    subject: str

    message: str

    attach_document: bool = False

    attachment_filename: str | None = None

    start_date: date

    end_date: date | None = None

    time: time

    repeat_interval: str

    max_occurrences: int | None = None


class AttachmentRequest(BaseModel):

    attachment_filename: str


class TemplateRequest(BaseModel):

    name: str

    subject: str

    body: str