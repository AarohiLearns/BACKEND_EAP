import smtplib

from pathlib import Path

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText

from email.mime.application import MIMEApplication


def send_email(
    recipient,
    subject,
    message,
    attachment_path=None
):

    print()
    print("========== SMTP START ==========")
    print("Recipient:", recipient)
    print("Subject:", subject)
    print("Attachment path:", attachment_path)

    smtp_host = "smtp.gmail.com"
    smtp_port = 587
    sender = "YOUR_USER_ID"
    password = "YOUR_APP_PASSWORD"

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(message, "plain"))

    if attachment_path:

        print("Opening attachment:", attachment_path)

        with open(attachment_path, "rb") as file:
            attachment = MIMEApplication(file.read())

        filename = Path(attachment_path).name

        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=filename
        )

        msg.attach(attachment)

        print("Attachment added:", filename)

    print("Connecting to SMTP server...")

    server = smtplib.SMTP(smtp_host, smtp_port)

    print("SMTP connection created.")

    server.ehlo()

    print("EHLO completed.")

    server.starttls()

    print("TLS started.")

    server.ehlo()

    print("Second EHLO completed.")

    print("Attempting SMTP login...")

    server.login(sender, password)

    print("SMTP login successful.")

    print("Sending email...")

    result = server.sendmail(
        sender,
        recipient,
        msg.as_string()
    )

    print("sendmail() returned:", result)

    print("SMTP server accepted the email.")

    server.quit()

    print("SMTP connection closed.")

    print("=========== SMTP END ===========")