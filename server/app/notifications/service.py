from fastapi import BackgroundTasks

from app.core.config import settings
from app.core.errors import AppError


def ensure_resend_configured() -> None:
    if not settings.resend_api_key:
        raise AppError(
            code="EMAIL_NOT_CONFIGURED",
            message="Email service is not configured on the server.",
            status_code=503,
        )


def send_email(to: str, subject: str, html: str) -> None:
    ensure_resend_configured()

    from resend import Emails

    emails = Emails(api_key=settings.resend_api_key)

    emails.send(
        {
            "from": settings.email_from,
            "to": [to],
            "subject": subject,
            "html": html,
        },
    )


def send_complaint_status_email(
    background_tasks: BackgroundTasks,
    recipient_email: str,
    recipient_name: str,
    complaint_id: str,
    old_status: str,
    new_status: str,
    note: str | None,
) -> None:
    subject = f"Complaint #{complaint_id[:8]} status updated to {new_status}"

    html = f"""
    <p>Hi {recipient_name},</p>
    <p>The status of your complaint (<strong>#{complaint_id[:8]}</strong>) has changed:</p>
    <p><strong>{old_status}</strong> → <strong>{new_status}</strong></p>
    {f'<p><em>Note from admin: {note}</em></p>' if note else ''}
    <p>You can view the full details in the Society Maintenance Tracker.</p>
    <hr>
    <p style="font-size: 0.8em; color: #666;">This is an automated message. Please do not reply.</p>
    """

    background_tasks.add_task(
        _send_wrapped,
        recipient_email,
        subject,
        html,
    )


def send_important_notice_email(
    background_tasks: BackgroundTasks,
    recipients: list[tuple[str, str]],
    title: str,
    content: str,
) -> None:
    subject = f"Important Notice: {title}"

    for email, name in recipients:
        html = f"""
        <p>Hi {name},</p>
        <p>An important notice has been published:</p>
        <h3>{title}</h3>
        <p>{content}</p>
        <hr>
        <p style="font-size: 0.8em; color: #666;">This is an automated message. Please do not reply.</p>
        """

        background_tasks.add_task(
            _send_wrapped,
            email,
            subject,
            html,
        )


def _send_wrapped(to: str, subject: str, html: str) -> None:
    try:
        send_email(to, subject, html)
    except Exception as e:
        # Log but never re-raise; email failures must not roll back DB ops
        print(f"[email] failed to {to}: {e}")