import logging

from django.urls import include, path

from powerplug.config import EntryPoints

logger = logging.getLogger(__name__)
urlpatterns = []
for entry in EntryPoints.URLS.group():
    try:
        urlpatterns.append(path(f"{entry.name}/", include(entry.module)))
    except ImportError:
        logger.exception("Error importing %s", entry.name)
