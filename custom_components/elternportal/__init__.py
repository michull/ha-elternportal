"""Init of elternprotal integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_SCAN_INTERVAL,
    CONF_PASSWORD,
    CONF_USERNAME
)
from homeassistant.core import HomeAssistant
#import homeassistant.helpers.config_validation as cv
#from homeassistant.helpers.typing import ConfigType

from .const import (
	DOMAIN,
	CONF_SCHOOL,
	PLATFORMS,
)
from .api import ElternPortalAPI
from .coordinator import ElternPortalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    
    _LOGGER.info(f"Setup a config entry {entry.entry_id} started")
    school: str = entry.data[CONF_SCHOOL]
    username: str = entry.data[CONF_USERNAME]
    password: str = entry.data[CONF_PASSWORD]

    _LOGGER.debug(f"The school is {school}")
    _LOGGER.debug(f"The username is {username}")

    # Initialize the API and coordinator.
    try:
        api = await hass.async_add_executor_job(ElternPortalAPI, school, username, password)
        coordinator = ElternPortalCoordinator(hass, api)
    except:
        _LOGGER.exception(f"Setup of school {school} with username {username} failed.")
        return False

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Setup a config entry ended")
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug(f"Migrating {config_entry.title} from version {config_entry.version}.{config_entry.minor_version}")

    if config_entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    _LOGGER.debug(f"Migration of {config_entry.title} to version {config_entry.version}.{config_entry.minor_version} successful")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    _LOGGER.info("Unload a config entry started")
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    _LOGGER.info("Unload a config entry ended")
    return unload_ok
