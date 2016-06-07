from django.core.management.base import BaseCommand, CommandError

from ... models import ContentTag
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
        for tag in defs.ARTICLEWARE_INITIAL_TAGS:
            obj, created = ContentTag.objects.get_or_create(name=tag)
            if created:
                count += 1
        if count > 0:
            self.stdout.write(self.style.SUCCESS('Successfully created {} tags'.format(count)))
        else:
            self.stdout.write(self.style.WARNING('Created no tags'.format(count)))
