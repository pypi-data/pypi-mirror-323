import logging

try:
    from importlib_metadata import entry_points
except ImportError:
    from importlib.metadata import entry_points
from importlib import metadata

from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class EntryPoints(models.TextChoices):
    APPS = "powerplug.apps", _("Installed Apps")
    REST = "powerplug.rest", _("Installed APIs")
    SIGNAL = "powerplug.signal", _("Installed Signals")
    TASK = "powerplug.task", _("Installed Tasks")
    URLS = "powerplug.urls", _("Installed URLs")
    CONTEXT = "powerplug.context", _("Installed context processor")

    def group(self) -> metadata.EntryPoints:
        return entry_points(group=self.value)

    def load(self):
        for entry in self.group():
            yield entry.load()


def customize_apps(orignal_settings, index=0):
    for entry in EntryPoints.APPS.group():
        if entry.module not in orignal_settings["INSTALLED_APPS"]:
            orignal_settings["INSTALLED_APPS"].insert(index, entry.module)


def customize_context(original_settings):
    for template in original_settings["TEMPLATES"]:
        for entry in EntryPoints.CONTEXT.group():
            try:
                template["OPTIONS"]["context_processors"].append(entry.module)
            except KeyError:
                logger.warning("Unable to update template with %s", entry)
