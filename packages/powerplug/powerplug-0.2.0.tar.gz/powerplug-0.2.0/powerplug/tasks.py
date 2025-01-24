"""
Entry point for Celery tasks
"""

import logging

from powerplug.config import EntryPoints

logger = logging.getLogger(__name__)

for entry in EntryPoints.TASK.group():
    try:
        entry.load()
    except ImportError:
        logger.exception("Error importing %s", entry.name)
    else:
        logger.debug("Loaded %s", entry)
