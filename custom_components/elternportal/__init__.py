"""Init of elternprotal integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME
)
from homeassistant.core import HomeAssistant
#import homeassistant.helpers.config_validation as cv
#from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_SCHOOL,
    CONF_REGISTER_START_MIN,
    CONF_REGISTER_START_MAX,
    CONF_REGISTER_DONE_TRESHOLD,
)
from .api import ElternPortalAPI
from .coordinator import ElternPortalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug(f"Setup of the config entry {entry.entry_id} started")
    school: str = entry.data.get(CONF_SCHOOL)
    username: str = entry.data.get(CONF_USERNAME)
    _LOGGER.debug(f"The school is {school}")
    _LOGGER.debug(f"The username is {username}")

    # Initialize the API and coordinator.
    try:
        api = await hass.async_add_executor_job(ElternPortalAPI, entry.data, entry.options)
        coordinator = ElternPortalCoordinator(hass, api)
    except:
        _LOGGER.exception(f"Setup of school {school} with username {username} failed.")
        return False

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.add_update_listener(async_reload_entry)
    _LOGGER.debug("Setup of the config entry ended")
    return True

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug(f"Migrating {entry.title} from version {entry.version}.{entry.minor_version}")

    if entry.version > 1:
        # This means the user has downgraded from a future version
        return False

    _LOGGER.debug(f"Migration of {entry.title} to version {entry.version}.{entry.minor_version} successful")

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    _LOGGER.debug("Unload of the config entry {entry.entry_id} started")
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    _LOGGER.debug("Unload of the config entry ended")
    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""

    _LOGGER.debug("Reload of the config entry {entry.entry_id} started")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
    _LOGGER.debug("Reload of the config entry ended")
