from datetime import date, time

from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):

    recipient: EmailStr
    subject: str
    message: str
    date: date
    time: time
    attach_document: bool = False
    attachment_filename: str | None = None


class TemplateRequest(BaseModel):

    name: str
    subject: str
    body: str


class AttachmentRequest(BaseModel):

    attachment_filename: str