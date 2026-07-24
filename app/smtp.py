import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_email(
    recipient,
    subject,
    message,
    attachment_path=None
):

    smtp_host = "smtp.gmail.com"

    smtp_port = 587

    sender = "YOUR_USER_ID"

    password = "YOUR_APP_PASSWORD"

    msg = MIMEMultipart()

    msg["Subject"] = subject

    msg["From"] = sender

    msg["To"] = recipient

    msg.attach(
        MIMEText(message)
    )

    if attachment_path:

        with open(
            attachment_path,
            "rb"
        ) as file:

            attachment = MIMEApplication(
                file.read()
            )

        filename = attachment_path.name

        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=filename
        )

        msg.attach(
            attachment
        )

    server = smtplib.SMTP(
        smtp_host,
        smtp_port
    )

    server.ehlo()

    server.starttls()

    server.ehlo()

    server.login(
        sender,
        password
    )

    server.sendmail(
        sender,
        recipient,
        msg.as_string()
    )

    server.quit()