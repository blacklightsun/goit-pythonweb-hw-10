from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel

from app.core.mail_config import mail_config

router = APIRouter()

class EmailSchema(BaseModel):
    fullname: str
    email: EmailStr


@router.post("/send-email")
async def send_in_background(background_tasks: BackgroundTasks, body: EmailSchema):
    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=[body.email],
        template_body={"fullname": body.fullname},
        subtype=MessageType.html
    )

    fm = FastMail(mail_config)

    background_tasks.add_task(fm.send_message, message, template_name="example_email.html")

    return {"message": "email has been sent"}
