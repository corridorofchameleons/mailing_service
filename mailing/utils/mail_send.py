import os
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

PORT = 465
USER = os.getenv('SMTP_USER')
PASSWORD = os.getenv('SMTP_PASS')
HOST = 'smtp.yandex.ru'
SENDER = os.getenv('SMTP_USER')


def mail_send(subject: str, message: str, receivers: list[str],
              port=PORT, user=USER, password=PASSWORD, sender=SENDER, host=HOST):

    msg = MIMEText(message)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(receivers)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:

        try:
            server.login(user, password)
            server.sendmail(sender, receivers, msg.as_string())
            print('mail successfully sent')
        except smtplib.SMTPDataError as err:
            print('error', err)

    with open('/home/speedfreak/PycharmProjects/Mailing/mailing/scripts/log.txt', 'a') as f:
        f.write(f'mail "{subject}" sent at {datetime.now()}\n')
