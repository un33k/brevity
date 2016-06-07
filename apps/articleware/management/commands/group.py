from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import Group

from ... import defaults as defs


class Command(BaseCommand):
    help = 'Loads initial article admin groups'

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
        for name in defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN:
            obj, created = Group.objects.get_or_create(name=defs.ARTICLEWARE_GROUP_ARTICLE_ADMIN[name])
            if created:
                count += 1
        if count > 0:
            self.stdout.write(self.style.SUCCESS('Successfully created {} groups'.format(count)))
        else:
            self.stdout.write(self.style.WARNING('Created {} groups'.format(count)))
