import os
import pathlib
import sys
from datetime import datetime
from crontab import CronTab
from dotenv import load_dotenv

load_dotenv()


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
    def __create_script(pk, start, end, status, subject, text, receivers):
        '''
        Создает текст скрипта
        '''
        text = f'''
import sys
from datetime import datetime, timezone

sys.path.append('/home/speedfreak/PycharmProjects/Mailing')

from mailing.utils.mail_send import mail_send

start = datetime.fromisoformat('{start}')
end = datetime.fromisoformat('{end}')
status = '{status}'

subject = '{subject}'
message = \'\'\'{text}\'\'\'
recievers = {receivers}

if start.day <= datetime.now(timezone.utc).day <= end.day and status != 'f':

    mail_send(subject, message, recievers)

'''

        with open(TaskManager.__set_filename(pk), 'w') as f:
            f.write(text)

    @staticmethod
    def create_task(pk, subject, text, receivers, start, end, freq, status):
        '''
        Записывает новую задачу в crontab
        '''

        # создание текста скрипта
        TaskManager.__create_script(pk, start, end, status, subject, text, receivers)

        # создание команды cron
        interpreter = sys.executable
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
                    job.dow.on(weekday)
                case 'm':
                    job.day.on(day)
