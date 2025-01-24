import logging

from django.apps import AppConfig

from powerplug.config import EntryPoints

logger = logging.getLogger(__name__)


class PowerplugConfig(AppConfig):
    name = "powerplug"

    def ready(self):
        for entry in EntryPoints.SIGNAL.group():
            try:
                entry.load()
            except ImportError:
                logger.exception("Error importing %s", entry.name)
