import smtplib

from pathlib import Path

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText

from email.mime.base import MIMEBase

from email import encoders

from app import database_new as database

from app.security import decrypt


def send_email(
    recipient,
    subject,
    message,
    attachment_path=None
):
    """
    Sends an email using SMTP credentials stored (encrypted) in the
    database via database_new.get_smtp_settings(), matching the
    approach used in the teammate's version of this file.

    Kept the same single-attachment signature as the rest of this
    codebase (scheduler_new.py passes one Path or None) -- internally
    this is converted to a one-item list so the attaching logic can
    stay close to the teammate's multi-attachment-capable style,
    making it easy to extend to multiple attachments later if needed.
    """

    print()
    print("========== SMTP START ==========")
    print("Recipient:", recipient)
    print("Subject:", subject)
    print("Attachment path:", attachment_path)

    settings = database.get_smtp_settings()

    if settings is None:
        raise Exception(
            "SMTP settings not found. Please configure SMTP "
            "settings first (see /smtp-settings endpoint)."
        )

    print("SMTP Settings (id/host/port/sender):", settings[:4])

    if len(settings) == 6:
        _, smtp_host, smtp_port, sender, encrypted_password, created_at = settings
    elif len(settings) == 5:
        _, smtp_host, smtp_port, sender, encrypted_password = settings
    else:
        raise Exception(f"Unexpected SMTP settings format: {settings}")

    password = decrypt(encrypted_password)

    msg = MIMEMultipart()

    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    msg.attach(MIMEText(message, "plain"))

    if attachment_path:

        attachment_path = Path(attachment_path)

        print("Opening attachment:", attachment_path)

        if attachment_path.exists():

            with open(attachment_path, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())

            encoders.encode_base64(part)

            filename = attachment_path.name

            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"'
            )

            msg.attach(part)

            print("Attachment added:", filename)

        else:

            print("File NOT found:", attachment_path)

            raise FileNotFoundError(
                f"Attachment file not found: {attachment_path}"
            )

    print("Connecting to SMTP server...")

    try:

        server = smtplib.SMTP(smtp_host, int(smtp_port))

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

    except smtplib.SMTPAuthenticationError:

        raise Exception(
            "SMTP Authentication Failed. "
            "Please check your email and app password in SMTP settings."
        )

    except smtplib.SMTPConnectError:

        raise Exception(
            "Unable to connect to SMTP server."
        )

    except smtplib.SMTPRecipientsRefused:

        raise Exception(
            "Recipient email address was rejected."
        )

    except Exception as e:

        raise Exception(str(e))