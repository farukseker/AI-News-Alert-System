import unittest
from unittest.mock import patch, MagicMock
import logging

from mailsender import HtmlSmtpMailer  # assume class is in mailer.py


class TestHtmlSmtpMailer(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("test_logger")
        self.mailer = HtmlSmtpMailer(
            host="smtp.test.com",
            port=587,
            username="user@test.com",
            password="secret",
            logger=self.logger,
        )

        self.subject = "Test Subject"
        self.html_body = "<h1>Hello</h1>"
        self.from_email = "from@test.com"
        self.to_emails = ["to@test.com"]

    @patch("smtplib.SMTP")
    def test_send_html_success(self, mock_smtp):
        smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = smtp_instance

        self.mailer.send_html(
            subject=self.subject,
            html_body=self.html_body,
            from_email=self.from_email,
            to_emails=self.to_emails,
        )

        smtp_instance.starttls.assert_called_once()
        smtp_instance.login.assert_called_once_with("user@test.com", "secret")
        smtp_instance.sendmail.assert_called_once()

    @patch("smtplib.SMTP")
    def test_authentication_error(self, mock_smtp):
        smtp_instance = MagicMock()
        smtp_instance.login.side_effect = Exception("auth failed")
        mock_smtp.return_value.__enter__.return_value = smtp_instance

        with self.assertRaises(Exception):
            self.mailer.send_html(
                subject=self.subject,
                html_body=self.html_body,
                from_email=self.from_email,
                to_emails=self.to_emails,
            )

    @patch("smtplib.SMTP")
    def test_sendmail_called_with_correct_args(self, mock_smtp):
        smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = smtp_instance

        self.mailer.send_html(
            subject=self.subject,
            html_body=self.html_body,
            from_email=self.from_email,
            to_emails="single@test.com",
        )

        smtp_instance.sendmail.assert_called()
        args, _ = smtp_instance.sendmail.call_args
        assert args[0] == self.from_email
        assert args[1] == ["single@test.com"]


if __name__ == "__main__":
    unittest.main()
