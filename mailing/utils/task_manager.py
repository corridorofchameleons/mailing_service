import os
import pathlib
import sys
from crontab import CronTab


class TaskManager:
    '''
    Класс управления рассылками
    '''

    __dir = pathlib.Path(__file__).parent.parent.resolve()

    @staticmethod
    def __set_filename(pk):
        '''
        Возвращает путь к файлу со скриптом конкретной рассылки
        '''
        return f'{TaskManager.__dir}/scripts/{pk}_script.py'

    @staticmethod
    def __create_script(pk):
        '''
        Создает текст скрипта
        '''
        text = f'''
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
        
    mailing = Mailing.objects.select_related('message').prefetch_related('clients').get(pk={pk})
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
            attempt.response = f'Все адреса некорректны: {{err}}'
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
'''

        with open(TaskManager.__set_filename(pk), 'w') as f:
            f.write(text)

    @staticmethod
    def __set_cron(pk, start, freq):
        '''
        Создает команду cron
        '''
        # путь к интерпретатору
        interpreter = sys.executable
        # путь к скрипту
        script = TaskManager.__set_filename(pk)

        cron_command = ' '.join([interpreter, script])

        minute = start.minute
        hour = start.hour
        weekday = start.weekday()
        day = start.day

        with CronTab(os.getenv('OS_USER')) as cr:
            job = cr.new(command=cron_command)
            job.minute.on(minute)
            job.hour.on(hour)

            # задает периодичность cron
            match freq:
                case 'd':
                    job.day.every(1)
                case 'w':
                    job.dow.on(weekday + 1)
                case 'm':
                    job.day.on(day)

    @staticmethod
    def create_task(pk, start, freq):
        '''
        Создает скрипт рассылки
        Записывает задачу в crontab
        '''

        # создание текста скрипта
        TaskManager.__create_script(pk)
        # добавление задачи в crontab
        TaskManager.__set_cron(pk, start, freq)

    @staticmethod
    def force_exec(pk):
        '''
        Производит рассылку принудительно
        '''
        file = TaskManager.__set_filename(pk)

        with open(file, 'r') as f:
            text = f.read()
        exec(text)
