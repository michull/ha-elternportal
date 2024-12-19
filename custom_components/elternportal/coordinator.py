"""Data coordinator for elternportal integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from pyelternportal import ElternPortalAPI

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, LOGGER


class ElternPortalCoordinator(DataUpdateCoordinator[None]):
    """Custom coordinator for the elternportal integration."""

    def __init__(self, hass: HomeAssistant, api: ElternportalAPI) -> None:
        """Initialize elternportal coordinator."""
        LOGGER.debug("ElternPortalCoordinator.__init__")
        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL
        )
        self.api = api

    async def _async_setup(self) -> None:
        """Set up the coordinator"""
        LOGGER.debug("ElternPortalCoordinator._async_setup")

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        LOGGER.debug("ElternPortalCoordinator._async_update_data")
        await self.api.async_update()
