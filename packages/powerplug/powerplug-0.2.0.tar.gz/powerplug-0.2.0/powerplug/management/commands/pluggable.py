from django.core.management.base import BaseCommand

from powerplug import config


class Command(BaseCommand):
    def handle(self, verbosity, **options):
        for entry_point in config.EntryPoints:
            self.stdout.write(self.style.SUCCESS(entry_point.label))
            for entry in entry_point.group():
                try:
                    entry.load()
                except ImportError as e:
                    self.stdout.write(self.style.ERROR("\t " + str(entry)))
                    if verbosity > 0:
                        self.stdout.write(self.style.ERROR(e))
                else:
                    print("\t", entry)
