from django.core.management.base import BaseCommand, CommandError
from mailing.models import Mailing
from mailing.utils.task_manager import TaskManager


class Command(BaseCommand):
    help = "Sends a message"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
            TaskManager.force_exec(mailing_id)
        except:
            raise CommandError('An error occured')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent "{mailing.name}"')
        )
