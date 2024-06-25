
def main():
    import os
    import smtplib
    import sys
    from datetime import datetime, timezone, timedelta
    
    from dotenv import load_dotenv
    load_dotenv()
    
    sys.path.append(os.getenv('PROJECT_PATH'))
    
    import django
    django.setup()
    
    from django.core.mail import send_mail
    from mailing.models import Mailing, MailingAttempt
        
    mailing = Mailing.objects.select_related('message').prefetch_related('clients').get(pk=98)
    emails = [client.email for client in mailing.clients.all()]

    start = mailing.start_time
    end = mailing.finish_time

    status = mailing.status

    if start.date() <= datetime.now().date() <= end and status not in ('p', 'f', 't'):

        mailing.status = 's'
        mailing.save()

        attempt = MailingAttempt(mailing=mailing)

        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.text,
                from_email=os.getenv('SMTP_USER'),
                recipient_list=emails,
                fail_silently=False
            )
            attempt.latest_attempt = datetime.now(timezone(timedelta(hours=3)))
            attempt.status = True
            attempt.response = 'Рассылка выполнена успешно'
        except smtplib.SMTPRecipientsRefused as err:
            attempt.status = False
            attempt.response = f'Все адреса некорректны: {err}'
        except smtplib.SMTPAuthenticationError:
            attempt.status = False
            attempt.response = 'Ошибка аутентификации. Обратитесь к админу'
        # а так же разные иные исключения
        
        except smtplib.SMTPException:
            attempt.status = False
            attempt.message = 'Ошибка системы'
        finally:
            attempt.save()

    if datetime.now().date() >= end:

        mailing.status = 'f'
        mailing.save()

main()
