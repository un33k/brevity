from django.core.management.base import BaseCommand, CommandError

from ... models import TargetingTag
from ... import defaults as defs


class Command(BaseCommand):
    help = 'Loads initial article tags'

    def add_arguments(self, parser):
        parser.add_argument('--load',
            action='store_true',
            dest='load',
            default=False,
            help='Loads initial tags')

    def handle(self, *args, **options):
        if not options['load']:
            return
        count = 0
        for tag in defs.ARTICLEWARE_INITIAL_TARGETING_TAGS:
            obj, created = TargetingTag.objects.get_or_create(name=tag)
            if created:
                count += 1
        if count > 0:
            self.stdout.write(self.style.SUCCESS('Successfully created {} targeting tags'.format(count)))
        else:
            self.stdout.write(self.style.WARNING('Created no targeting tags'.format(count)))
