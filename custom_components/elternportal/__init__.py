"""Init of elternprotal integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from pyelternportal import ElternPortalAPI, VERSION
from pyelternportal.const import (
    CONF_APPOINTMENT_CALENDAR,
    CONF_APPOINTMENT_TRESHOLD_END,
    CONF_APPOINTMENT_TRESHOLD_START,
    CONF_BLACKBOARD_TRESHOLD,
    CONF_LETTER_TRESHOLD,
    CONF_MESSAGE_TRESHOLD,
    CONF_POLL_TRESHOLD,
    CONF_REGISTER_CALENDAR,
    CONF_REGISTER_SHOW_EMPTY,
    CONF_REGISTER_START_MAX,
    CONF_REGISTER_START_MIN,
    CONF_SICKNOTE_CALENDAR,
    CONF_SICKNOTE_TRESHOLD,
    DEFAULT_APPOINTMENT_CALENDAR,
    DEFAULT_APPOINTMENT_TRESHOLD_END,
    DEFAULT_APPOINTMENT_TRESHOLD_START,
    DEFAULT_BLACKBOARD_TRESHOLD,
    DEFAULT_LETTER_TRESHOLD,
    DEFAULT_MESSAGE_TRESHOLD,
    DEFAULT_POLL_TRESHOLD,
    DEFAULT_REGISTER_CALENDAR,
    DEFAULT_REGISTER_SHOW_EMPTY,
    DEFAULT_REGISTER_START_MAX,
    DEFAULT_REGISTER_START_MIN,
    DEFAULT_SICKNOTE_CALENDAR,
    DEFAULT_SICKNOTE_TRESHOLD,
)

from .const import (
    CONF_SECTION_APPOINTMENTS,
    CONF_SECTION_BLACKBOARDS,
    CONF_SECTION_LESSONS,
    CONF_SECTION_LETTERS,
    CONF_SECTION_MESSAGES,
    CONF_SECTION_POLLS,
    CONF_SECTION_REGISTERS,
    CONF_SECTION_SICKNOTES,
    DEFAULT_SECTION_APPOINTMENTS,
    DEFAULT_SECTION_BLACKBOARDS,
    DEFAULT_SECTION_LESSONS,
    DEFAULT_SECTION_LETTERS,
    DEFAULT_SECTION_MESSAGES,
    DEFAULT_SECTION_POLLS,
    DEFAULT_SECTION_REGISTERS,
    DEFAULT_SECTION_SICKNOTES,
    DOMAIN,
    LOGGER,
    PLATFORMS,
    CONF_SCHOOL,
)

from .coordinator import ElternPortalCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eltern-Portal from a config entry."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    LOGGER.debug("Setup of the config entry %s started", entry.entry_id)
    school: str = entry.data.get(CONF_SCHOOL)
    username: str = entry.data.get(CONF_USERNAME)
    LOGGER.debug("The school is %s", school)
    LOGGER.debug("The username is %s", username)

    # Initialize the API and coordinator.
    LOGGER.debug("The version of pyelternportal is %s", VERSION)
    session = async_get_clientsession(hass)
    api = ElternPortalAPI(session)
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
        CONF_APPOINTMENT_CALENDAR: entry.options.get(
            CONF_APPOINTMENT_CALENDAR, DEFAULT_APPOINTMENT_CALENDAR
        ),
        CONF_APPOINTMENT_TRESHOLD_END: entry.options.get(
            CONF_APPOINTMENT_TRESHOLD_END, DEFAULT_APPOINTMENT_TRESHOLD_END
        ),
        CONF_APPOINTMENT_TRESHOLD_START: entry.options.get(
            CONF_APPOINTMENT_TRESHOLD_START, DEFAULT_APPOINTMENT_TRESHOLD_START
        ),
        CONF_BLACKBOARD_TRESHOLD: entry.options.get(
            CONF_BLACKBOARD_TRESHOLD, DEFAULT_BLACKBOARD_TRESHOLD
        ),
        CONF_LETTER_TRESHOLD: entry.options.get(
            CONF_LETTER_TRESHOLD, DEFAULT_LETTER_TRESHOLD
        ),
        CONF_MESSAGE_TRESHOLD: entry.options.get(
            CONF_MESSAGE_TRESHOLD, DEFAULT_MESSAGE_TRESHOLD
        ),
        CONF_POLL_TRESHOLD: entry.options.get(
            CONF_POLL_TRESHOLD, DEFAULT_POLL_TRESHOLD
        ),
        CONF_REGISTER_CALENDAR: entry.options.get(
            CONF_REGISTER_CALENDAR, DEFAULT_REGISTER_CALENDAR
        ),
        CONF_REGISTER_START_MIN: entry.options.get(
            CONF_REGISTER_START_MIN, DEFAULT_REGISTER_START_MIN
        ),
        CONF_REGISTER_START_MAX: entry.options.get(
            CONF_REGISTER_START_MAX, DEFAULT_REGISTER_START_MAX
        ),
        CONF_REGISTER_SHOW_EMPTY: entry.options.get(
            CONF_REGISTER_SHOW_EMPTY, DEFAULT_REGISTER_SHOW_EMPTY
        ),
        CONF_SICKNOTE_CALENDAR: entry.options.get(
            CONF_SICKNOTE_CALENDAR, DEFAULT_SICKNOTE_CALENDAR
        ),
        CONF_SICKNOTE_TRESHOLD: entry.options.get(
            CONF_SICKNOTE_TRESHOLD, DEFAULT_SICKNOTE_TRESHOLD
        ),
    }
    api.set_option_data(options)

    try:
        await api.async_validate_config()
    except Exception as ex:
        LOGGER.exception(
            "Setup of school %s with username %s failed: %s", school, username, ex
        )
        return False

    coordinator = ElternPortalCoordinator(hass, api)

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.add_update_listener(async_reload_entry)
    LOGGER.debug("Setup of the config entry ended")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    LOGGER.debug("Unload of the config entry %s started", entry.entry_id)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    LOGGER.debug("Unload of the config entry ended")
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""

    LOGGER.debug("Reload of the config entry %s started", entry.entry_id)
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
    LOGGER.debug("Reload of the config entry ended")
