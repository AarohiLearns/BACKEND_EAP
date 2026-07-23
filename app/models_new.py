from datetime import date, time
from pydantic import BaseModel
from pydantic import EmailStr 

class EmailRequest(BaseModel):
    recipient: EmailStr
    subject: str
    message: str
    date: date
    time: time
    attach_document: bool = False

class TemplateRequest(BaseModel):
    name: str
    subject: str
    body: str


  