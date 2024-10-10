"""Config flow for elternportal integration."""

from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback

from .const import (
    DOMAIN,

    CONF_REGISTER_START_MIN,
    CONF_REGISTER_START_MAX,
    CONF_REGISTER_DONE_TRESHOLD,
    CONF_SENSOR_REGISTER,
    CONF_SCHOOL,

    DEFAULT_REGISTER_START_MIN,
    DEFAULT_REGISTER_START_MAX,
    DEFAULT_REGISTER_DONE_TRESHOLD,
    DEFAULT_SENSOR_REGISTER,
)
from .api import ElternPortalAPI

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SCHOOL): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

_LOGGER = logging.getLogger(__name__)

class ElternPortalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """ElternPortal config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1
    
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        
        errors: dict = {}

        if user_input is not None:
            school=user_input[CONF_SCHOOL]
            username=user_input[CONF_USERNAME]
            password=user_input[CONF_PASSWORD]
            school = school.lower()
            username = username.lower()

            # Validate data using the API
            try:
                api = await self.hass.async_add_executor_job(
                    ElternPortalAPI, school, username, password
                )
                school_name = await api.async_school_name()
                _LOGGER.debug(f"{school_name}: Successfully added!")
            except:
                _LOGGER.exception(f"Setup of {school} failed")
                errors["base"] = "invalid_school"

            if not errors:
                # Set the unique ID for this config entry.
                await self.async_set_unique_id(f"{DOMAIN}_{school}")
                self._abort_if_unique_id_configured()

                # User is done, create the config entry.
                entry_data = {
                    CONF_SCHOOL: school,
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                }
                return self.async_create_entry(title=school_name, data=entry_data)


        return self.async_show_form(
            step_id="user",
            errors=errors,
            data_schema=CONFIG_SCHEMA,
        )
        
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""

        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""

        #_LOGGER.debug(f"User input of option flow: {user_input}")
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_REGISTER_START_MIN,
                        default=self.config_entry.options.get(CONF_REGISTER_START_MIN, DEFAULT_REGISTER_START_MIN),
                    ): int,
                    vol.Optional(
                        CONF_REGISTER_START_MAX,
                        default=self.config_entry.options.get(CONF_REGISTER_START_MAX, DEFAULT_REGISTER_START_MAX),
                    ): int,
                    vol.Optional(
                        CONF_REGISTER_DONE_TRESHOLD,
                        default=self.config_entry.options.get(CONF_REGISTER_DONE_TRESHOLD, DEFAULT_REGISTER_DONE_TRESHOLD),
                    ): int,
                    vol.Optional(
                        CONF_SENSOR_REGISTER,
                        default=self.config_entry.options.get(CONF_SENSOR_REGISTER, DEFAULT_SENSOR_REGISTER),
                    ): bool
                }
            ),
        )