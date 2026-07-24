import time

from datetime import datetime

from pathlib import Path

from app.database_new import (
    get_pending_emails,
    update_status,
    update_status_failed
)

from app.smtp import send_email


def get_automatic_attachment():

    project_folder = (
        Path(__file__).parent.parent
    )

    reports_folder = (
        project_folder / "Reports"
    )

    files = list(
        reports_folder.iterdir()
    )

    if files:

        return files[0]

    return None


def archive_file(
    attachment_path
):

    project_folder = (
        Path(__file__).parent.parent
    )

    archive_folder = (
        project_folder / "Archive"
    )

    archive_folder.mkdir(
        exist_ok=True
    )

    archive_path = (
        archive_folder /
        attachment_path.name
    )

    attachment_path.rename(
        archive_path
    )


def scheduler():

    print(
        "Scheduler Started"
    )

    while True:

        emails = get_pending_emails()

        print(
            "Checking database..."
        )

        current_datetime = datetime.now()

        for email in emails:

            email_id = email[0]

            recipient = email[1]

            subject = email[2]

            message = email[3]

            date = email[4]

            scheduled_time = email[5]

            attach_document = email[6]

            attachment_path = email[7]

            scheduled_datetime = datetime.strptime(
                date + " " + scheduled_time,
                "%d-%m-%Y %H:%M"
            )

            if current_datetime >= scheduled_datetime:

                try:

                    actual_attachment_path = None


                    # No attachment

                    if not attach_document:

                        actual_attachment_path = None


                    # Manual attachment

                    elif attachment_path:

                        actual_attachment_path = (

                            Path(__file__).parent.parent /

                            attachment_path

                        )


                    # Automatic attachment

                    else:

                        actual_attachment_path = (

                            get_automatic_attachment()

                        )


                    send_email(

                        recipient,

                        subject,

                        message,

                        actual_attachment_path

                    )


                    if actual_attachment_path:

                        archive_file(

                            actual_attachment_path

                        )


                    update_status(

                        email_id

                    )


                    print(

                        "Email Sent Successfully"

                    )

                except Exception as e:

                    print(

                        "SMTP Error:",

                        e

                    )

                    update_status_failed(

                        email_id

                    )

                    print(

                        "Email Sending Failed"

                    )

        time.sleep(

            60

        )


if __name__ == "__main__":

    scheduler()