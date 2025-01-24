import logging

from django.conf.urls import include, url
from rest_framework import routers

from powerplug.config import EntryPoints

logger = logging.getLogger(__name__)

router = routers.DefaultRouter(trailing_slash=False)
for entry in EntryPoints.REST.group():
    try:
        router.register(entry.name, entry.load())
    except ImportError:
        logger.exception("Error importing %s", entry.name)

app_name = "api"
urlpatterns = (url(r"^api/", include(router.urls)),)
