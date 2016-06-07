from django.core.management.base import BaseCommand, CommandError

from ... models import CategoryTag
from ... import defaults as defs


class Command(BaseCommand):
    help = 'Loads initial article categories'

    def add_arguments(self, parser):
        parser.add_argument('--load',
            action='store_true',
            dest='load',
            default=False,
            help='Loads initial categories')

    def handle(self, *args, **options):
        if not options['load']:
            return
        count = 0
        for category in defs.ARTICLEWARE_INITIAL_CATEGORIES:
            obj, created = CategoryTag.objects.get_or_create(name=category)
            if created:
                count += 1
        if count > 0:
            self.stdout.write(self.style.SUCCESS('Successfully created {} categories'.format(count)))
        else:
            self.stdout.write(self.style.WARNING('Created no categories'.format(count)))
