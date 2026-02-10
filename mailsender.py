import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class HtmlSmtpMailer:
    def __init__(
        self,
        host,
        port,
        username,
        password,
        use_tls=True,
        logger: logging.Logger | None = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.logger = logger or logging.getLogger(__name__)

    def send_html(self, subject, html_body, from_email, to_emails):
        if isinstance(to_emails, str):
            to_emails = [to_emails]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = ", ".join(to_emails)
        msg.attach(MIMEText(html_body, "html"))

        try:
            self.logger.info("SMTP connection starting", extra={"host": self.host, "port": self.port})

            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                    self.logger.debug("STARTTLS enabled")

                server.login(self.username, self.password)
                self.logger.debug("SMTP login successful")

                server.sendmail(from_email, to_emails, msg.as_string())
                self.logger.info("Email sent successfully", extra={"to": to_emails})

        except smtplib.SMTPAuthenticationError as e:
            self.logger.error("SMTP authentication failed", exc_info=e)
            raise

        except smtplib.SMTPException as e:
            self.logger.error("SMTP error occurred", exc_info=e)
            raise

        except Exception as e:
            self.logger.exception("Unexpected error while sending email")
            raise
