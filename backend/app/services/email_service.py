import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def _html_wrapper(title: str, body: str) -> str:
    return f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
    <div style="background:#1E3A5F;color:white;padding:16px;border-radius:8px 8px 0 0;">
        <h2 style="margin:0;">FACULTY Q</h2>
        <p style="margin:4px 0 0;font-size:12px;opacity:0.8;">Smart Faculty Scheduling & Reminder System</p>
    </div>
    <div style="border:1px solid #ddd;border-top:none;padding:20px;border-radius:0 0 8px 8px;">
        <h3 style="color:#1E3A5F;">{title}</h3>
        {body}
    </div>
    <p style="font-size:11px;color:#999;text-align:center;margin-top:16px;">
        This is an automated message from FACULTY Q. Do not reply.
    </p>
    </body></html>
    """

def send_email(to_email: str, subject: str, body: str, html: bool = False) -> bool:
    """Send email via SMTP. Returns True on success."""
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.warning("SMTP not configured. Email not sent to %s", to_email)
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
        logger.info("Email sent to %s", to_email)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to_email, str(e))
        return False

def send_class_reminder_email(to_email: str, faculty_name: str, subject_name: str,
                            period: int, class_name: str, section: str,
                            classroom: str, floor: str, time: str) -> bool:
    body = _html_wrapper("Class Reminder", f"""
        <p>Your class is starting in 5 minutes.</p>
        <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:4px 0;font-weight:bold;">Faculty:</td><td>{faculty_name}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Subject:</td><td>{subject_name}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Period:</td><td>{period}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Class:</td><td>{class_name} - Section {section}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Classroom:</td><td>{classroom}, Floor {floor}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Time:</td><td>{time}</td></tr>
        </table>
        <p style="margin-top:12px;color:#1E3A5F;font-weight:bold;">Please proceed to your classroom.</p>
    """)
    return send_email(to_email, f"Class Reminder: {subject_name}", body, html=True)

def send_deadline_reminder_email(to_email: str, student_name: str, title: str,
                                subject: str, faculty: str, deadline: str,
                                hours_remaining: int) -> bool:
    body = _html_wrapper("Assignment Deadline Reminder", f"""
        <p>Dear {student_name},</p>
        <p>This is a reminder that your assignment is due soon.</p>
        <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:4px 0;font-weight:bold;">Assignment:</td><td>{title}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Subject:</td><td>{subject}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Faculty:</td><td>{faculty}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Deadline:</td><td>{deadline}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Time remaining:</td><td>{hours_remaining} hour(s)</td></tr>
        </table>
        <p style="margin-top:12px;color:#d32f2f;font-weight:bold;">Please submit before the deadline.</p>
    """)
    return send_email(to_email, f"Deadline Reminder: {title}", body, html=True)

def send_substitution_email(to_email: str, recipient_name: str, original: str,
                           substitute: str, subject: str, date: str, period: int) -> bool:
    body = _html_wrapper("Substitute Faculty Update", f"""
        <p>Dear {recipient_name},</p>
        <p>Your class has a substitute faculty assigned.</p>
        <table style="width:100%;border-collapse:collapse;">
            <tr><td style="padding:4px 0;font-weight:bold;">Original Faculty:</td><td>{original}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Substitute Faculty:</td><td>{substitute}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Subject:</td><td>{subject}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Date:</td><td>{date}</td></tr>
            <tr><td style="padding:4px 0;font-weight:bold;">Period:</td><td>{period}</td></tr>
        </table>
    """)
    return send_email(to_email, f"Substitute Faculty Update: {subject}", body, html=True)