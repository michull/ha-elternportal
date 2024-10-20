"""Data coordinator for elternportal integration."""

from __future__ import annotations

import logging
import pyelternportal

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
#from .api import ElternPortalAPI

_LOGGER = logging.getLogger(__name__)


class ElternPortalCoordinator(DataUpdateCoordinator[None]):
    """Custom coordinator for the elternportal integration."""

    def __init__(self, hass: HomeAssistant, api: pyelternportal.ElternportalAPI) -> None:
        """Initialize elternportal coordinator."""

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL
        )
        self.api = api

    async def _async_setup(self) -> None:
        """Set up the coordinator"""

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""

        await self.api.async_update()
