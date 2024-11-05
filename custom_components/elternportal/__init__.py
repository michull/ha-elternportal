"""Init of elternprotal integration."""

from __future__ import annotations

import logging

import pyelternportal
# from .pyelternportal import *  # local lib

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_REGISTER_SHOW_EMPTY,
    CONF_REGISTER_START_MAX,
    CONF_REGISTER_START_MIN,
    CONF_SECTION_APPOINTMENTS,
    CONF_SECTION_BLACKBOARDS,
    CONF_SECTION_LESSONS,
    CONF_SECTION_LETTERS,
    CONF_SECTION_MESSAGES,
    CONF_SECTION_POLLS,
    CONF_SECTION_REGISTERS,
    CONF_SECTION_SICKNOTES,
    DEFAULT_REGISTER_SHOW_EMPTY,
    DEFAULT_REGISTER_START_MAX,
    DEFAULT_REGISTER_START_MIN,
    DEFAULT_SECTION_APPOINTMENTS,
    DEFAULT_SECTION_BLACKBOARDS,
    DEFAULT_SECTION_LESSONS,
    DEFAULT_SECTION_LETTERS,
    DEFAULT_SECTION_MESSAGES,
    DEFAULT_SECTION_POLLS,
    DEFAULT_SECTION_REGISTERS,
    DEFAULT_SECTION_SICKNOTES,
    DOMAIN,
    PLATFORMS,
    CONF_SCHOOL,
)

# from .api import ElternPortalAPI
from .coordinator import ElternPortalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eltern-Portal from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    _LOGGER.debug("Setup of the config entry %s started", entry.entry_id)
    school: str = entry.data.get(CONF_SCHOOL)
    username: str = entry.data.get(CONF_USERNAME)
    _LOGGER.debug("The school is %s", school)
    _LOGGER.debug("The username is %s", username)

    # Initialize the API and coordinator.
    _LOGGER.debug("The version of pyelternportal is %s", pyelternportal.version)
    session = async_get_clientsession(hass)
    api = pyelternportal.ElternPortalAPI(session)
    config = {
        "school": entry.data.get(CONF_SCHOOL),
        "username": entry.data.get(CONF_USERNAME),
        "password": entry.data.get(CONF_PASSWORD),
    }
    api.set_config_data(config)
    options = {
        "appointment": entry.options.get(
            CONF_SECTION_APPOINTMENTS, DEFAULT_SECTION_APPOINTMENTS
        ),
        "blackboard": entry.options.get(
            CONF_SECTION_BLACKBOARDS, DEFAULT_SECTION_BLACKBOARDS
        ),
        "lesson": entry.options.get(CONF_SECTION_LESSONS, DEFAULT_SECTION_LESSONS),
        "letter": entry.options.get(CONF_SECTION_LETTERS, DEFAULT_SECTION_LETTERS),
        "message": entry.options.get(CONF_SECTION_MESSAGES, DEFAULT_SECTION_MESSAGES),
        "poll": entry.options.get(CONF_SECTION_POLLS, DEFAULT_SECTION_POLLS),
        "register": entry.options.get(
            CONF_SECTION_REGISTERS, DEFAULT_SECTION_REGISTERS
        ),
        "sicknote": entry.options.get(
            CONF_SECTION_SICKNOTES, DEFAULT_SECTION_SICKNOTES
        ),
        "register_start_min": entry.options.get(
            CONF_REGISTER_START_MIN, DEFAULT_REGISTER_START_MIN
        ),
        "register_start_max": entry.options.get(
            CONF_REGISTER_START_MAX, DEFAULT_REGISTER_START_MAX
        ),
        "register_show_empty": entry.options.get(
            CONF_REGISTER_SHOW_EMPTY, DEFAULT_REGISTER_SHOW_EMPTY
        ),
    }
    api.set_option_data(options)

    try:
        await api.async_validate_config()
    except:
        _LOGGER.exception(
            "Setup of school %s with username %s failed.", school, username
        )
        return False

    coordinator = ElternPortalCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.add_update_listener(async_reload_entry)
    _LOGGER.debug("Setup of the config entry ended")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    _LOGGER.debug("Unload of the config entry %s started", entry.entry_id)
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
