import time

from datetime import datetime, timedelta

from pathlib import Path

from app.database_new import (
    get_pending_emails,
    update_status,
    update_status_failed,
    update_attachment_details,
    create_next_recurring_email
)

from app.smtp import send_email


BASE_DIR = Path(__file__).parent.parent

REPORTS_FOLDER = BASE_DIR / "Reports"

ARCHIVE_FOLDER = BASE_DIR / "Archive"


last_occurrences = {}


def get_interval_seconds(repeat_interval):

    intervals = {
        "2 Minutes": 2 * 60,
        "Hourly": 60 * 60,
        "Daily": 24 * 60 * 60
    }

    return intervals.get(repeat_interval)


def add_interval(current_datetime, repeat_interval):
    """
    Returns the next scheduled datetime by adding the interval
    to the CURRENT scheduled datetime (never to 'now'). This is
    the core fix for the recurring-time bug: each next occurrence
    is calculated from the row that was just sent, not left as a
    stale copy of the original time.
    """

    interval_seconds = get_interval_seconds(repeat_interval)

    if interval_seconds is None:
        return None

    return current_datetime + timedelta(seconds=interval_seconds)


def get_report_files_by_addition_order():
    """
    Returns files in the Reports folder ordered by the time they
    were ADDED to the folder (creation time), NOT by filename.
    """

    if not REPORTS_FOLDER.exists():
        return []

    files = [f for f in REPORTS_FOLDER.iterdir() if f.is_file()]

    def added_time(f):
        stat = f.stat()
        return (stat.st_ctime, stat.st_mtime)

    return sorted(files, key=added_time)


def get_automatic_attachment():

    files = get_report_files_by_addition_order()

    if files:
        return files[0]

    return None


def get_next_attachment(current_filename):

    files = get_report_files_by_addition_order()

    for index, file in enumerate(files):

        if file.name == current_filename:

            if index + 1 < len(files):
                return files[index + 1]

            return None

    return None


def archive_file(attachment_path):

    ARCHIVE_FOLDER.mkdir(exist_ok=True)

    archive_path = ARCHIVE_FOLDER / attachment_path.name

    attachment_path.rename(archive_path)


def resolve_next_attachment(current_attachment_filename):

    if current_attachment_filename:

        next_file = get_next_attachment(current_attachment_filename)

        if next_file is not None:
            return next_file

        return None

    return get_automatic_attachment()


def scheduler():

    print("Scheduler Started")

    while True:

        try:

            emails = get_pending_emails()

            current_datetime = datetime.now()

            print()
            print("Checking database...")
            print("Current date and time:", current_datetime)

            for email in emails:

                email_id = email[0]

                try:

                    recipient = email[1]
                    subject = email[2]
                    message = email[3]
                    attach_document = bool(email[4])
                    attachment_path = email[5]
                    attachment_filename = email[6]
                    attachment_status = email[7]
                    start_date = email[8]
                    end_date = email[9]
                    scheduled_time = email[10]
                    repeat_interval = email[11]
                    max_occurrences = email[13]
                    occurrence_count = email[14] if email[14] is not None else 1

                    print()
                    print("----------------------------------------")
                    print("Processing Email ID:", email_id)
                    print("----------------------------------------")

                    start_datetime = datetime.strptime(
                        start_date + " " + scheduled_time,
                        "%d-%m-%Y %H:%M"
                    )

                    print("Scheduled time:", start_datetime)

                    if current_datetime < start_datetime:
                        print("Email is not due yet.")
                        continue

                    if end_date:

                        end_date_only = datetime.strptime(
                            end_date, "%d-%m-%Y"
                        ).date()

                        current_date_only = current_datetime.date()

                        if current_date_only > end_date_only:

                            print()
                            print("End date has completely passed.")

                            update_status(email_id)

                            print(
                                "Email marked as Sent because the "
                                "scheduling period ended."
                            )

                            continue

                    if repeat_interval == "Never":

                        occurrence_number = 0

                    else:

                        interval_seconds = get_interval_seconds(
                            repeat_interval
                        )

                        if interval_seconds is None:

                            print()
                            print(
                                "ERROR: Unknown repeat interval:",
                                repeat_interval
                            )

                            update_status_failed(email_id)

                            continue

                        elapsed_seconds = (
                            current_datetime - start_datetime
                        ).total_seconds()

                        occurrence_number = int(
                            elapsed_seconds // interval_seconds
                        )

                    if last_occurrences.get(email_id) == occurrence_number:

                        print("This occurrence was already processed.")
                        continue

                    actual_attachment_path = None
                    current_attachment_path = attachment_path
                    current_attachment_filename = attachment_filename
                    current_attachment_status = attachment_status

                    if attach_document:

                        if attachment_filename:

                            actual_attachment_path = (
                                BASE_DIR / attachment_path
                            )

                        else:

                            actual_attachment_path = (
                                get_automatic_attachment()
                            )

                            if actual_attachment_path:

                                current_attachment_path = str(
                                    actual_attachment_path.relative_to(
                                        BASE_DIR
                                    )
                                )

                                current_attachment_filename = (
                                    actual_attachment_path.name
                                )

                                current_attachment_status = "Automatic"

                    if attach_document and not actual_attachment_path:

                        raise FileNotFoundError(
                            "No attachment file was found."
                        )

                    print()
                    print("Attempting to send email...")
                    print("Recipient:", recipient)
                    print("Attachment:", actual_attachment_path)

                    send_email(
                        recipient,
                        subject,
                        message,
                        actual_attachment_path
                    )

                    print()
                    print("send_email() completed successfully.")

                    sent_attachment_filename = None
                    next_attachment_before_archive = None

                    if actual_attachment_path:

                        sent_attachment_filename = (
                            actual_attachment_path.name
                        )

                        # ---- FIX: determine the "next" file while
                        # the current one is STILL in the Reports
                        # folder. If we archive first, the current
                        # file disappears from the folder listing,
                        # and get_next_attachment() can no longer
                        # find its position to look one step ahead.
                        if repeat_interval != "Never" and attach_document:

                            next_attachment_before_archive = (
                                resolve_next_attachment(
                                    sent_attachment_filename
                                )
                            )

                        update_attachment_details(
                            email_id,
                            current_attachment_path,
                            current_attachment_filename,
                            current_attachment_status
                        )

                        archive_file(actual_attachment_path)

                        print()
                        print("Archived:", actual_attachment_path.name)

                    if repeat_interval == "Never":

                        update_status(email_id)

                        print("Email marked as Sent.")

                    else:

                        last_occurrences[email_id] = occurrence_number

                        next_datetime = add_interval(
                            start_datetime, repeat_interval
                        )

                        next_date_str = next_datetime.strftime("%d-%m-%Y")
                        next_time_str = next_datetime.strftime("%H:%M")

                        schedule_next = True

                        if end_date:

                            end_date_only = datetime.strptime(
                                end_date, "%d-%m-%Y"
                            ).date()

                            if next_datetime.date() > end_date_only:
                                schedule_next = False

                        if max_occurrences is not None:

                            if max_occurrences <= 0:

                                schedule_next = False

                                print()
                                print(
                                    "max_occurrences is 0 or less -- "
                                    "no further sends will be scheduled."
                                )

                            elif occurrence_count >= max_occurrences:

                                schedule_next = False

                                print()
                                print(
                                    "max_occurrences reached (",
                                    occurrence_count,
                                    "/",
                                    max_occurrences,
                                    ") -- stopping chain."
                                )

                        next_occurrence_count = occurrence_count + 1

                        if not schedule_next:

                            update_status(email_id)

                            print()
                            print(
                                "Recurring schedule ended "
                                "(next occurrence past end_date "
                                "or max_occurrences reached)."
                            )

                        elif attach_document:

                            # ---- NEXT ATTACHMENT: resolved earlier,
                            # BEFORE the current file was archived ----
                            next_attachment = next_attachment_before_archive

                            if next_attachment:

                                next_attachment_path = str(
                                    next_attachment.relative_to(BASE_DIR)
                                )

                                create_next_recurring_email(
                                    email,
                                    next_attachment_path,
                                    next_attachment.name,
                                    "Automatic",
                                    next_date_str,
                                    next_time_str,
                                    next_occurrence_count
                                )

                                print()
                                print(
                                    "Next attachment:",
                                    next_attachment.name
                                )
                                print(
                                    "Next scheduled time:",
                                    next_datetime
                                )

                                update_status(email_id)

                            else:

                                update_status(email_id)

                                print()
                                print("No more reports available.")

                        else:

                            create_next_recurring_email(
                                email,
                                None,
                                None,
                                None,
                                next_date_str,
                                next_time_str,
                                next_occurrence_count
                            )

                            print()
                            print("Next scheduled time:", next_datetime)

                            update_status(email_id)

                    print()
                    print("Email Sent Successfully")

                except Exception as error:

                    print()
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("EMAIL PROCESSING ERROR")
                    print("Email ID:", email_id)
                    print("Error Type:", type(error).__name__)
                    print("Error Message:", str(error))
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                    update_status_failed(email_id)

                    print("Email Sending Failed")

            print()
            print("Scheduler cycle completed.")
            print("Waiting 60 seconds...")

            time.sleep(60)

        except Exception as error:

            print()
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("SCHEDULER ERROR")
            print("Error Type:", type(error).__name__)
            print("Error Message:", str(error))
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            time.sleep(60)


if __name__ == "__main__":
    scheduler()