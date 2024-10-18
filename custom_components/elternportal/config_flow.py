"""Config flow for elternportal integration."""

from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector

from .const import (
    CONF_CALENDAR_APPOINTMENT,
    CONF_CALENDAR_REGISTER,
    CONF_REGISTER_COMPLETION_TRESHOLD,
    CONF_REGISTER_START_MAX,
    CONF_REGISTER_START_MIN,
    CONF_SCHOOL,
    CONF_SECTION_APPOINTMENTS,
    CONF_SECTION_LESSONS,
    CONF_SECTION_LETTERS,
    CONF_SECTION_POLLS,
    CONF_SECTION_REGISTERS,
    CONF_SECTION_SICKNOTES,
    CONF_SENSOR_REGISTER,
    DEFAULT_CALENDAR_APPOINTMENT,
    DEFAULT_CALENDAR_REGISTER,
    DEFAULT_REGISTER_COMPLETION_TRESHOLD,
    DEFAULT_REGISTER_START_MAX,
    DEFAULT_REGISTER_START_MIN,
    DEFAULT_SECTION_APPOINTMENTS,
    DEFAULT_SECTION_LESSONS,
    DEFAULT_SECTION_LETTERS,
    DEFAULT_SECTION_POLLS,
    DEFAULT_SECTION_REGISTERS,
    DEFAULT_SECTION_SICKNOTES,
    DEFAULT_SENSOR_REGISTER,
    DOMAIN,
)
from .api import (
    ElternPortalAPI,
    ResolveHostnameError,
    CannotConnectError,
    BadCredentialsError,
    PupilListError,
)

_LOGGER = logging.getLogger(__name__)


class ElternPortalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """ElternPortal config flow."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, Any] | None = None,
    ) -> FlowResult:

        errors = {}
        if user_input is not None:
            try:
                api = await self.hass.async_add_executor_job(ElternPortalAPI)
                await api.async_set_config_data(user_input)
                await api.async_validate_config_data()
            except ResolveHostnameError as ex:
                _LOGGER.exception(f"Cannot resolve hostname: {ex}")
                errors[CONF_SCHOOL] = "cannot_resolve"
            except CannotConnectError as ex:
                _LOGGER.exception(f"Cannot connect: {ex}")
                errors[CONF_SCHOOL] = "cannot_connect"
            except BadCredentialsError as ex:
                _LOGGER.exception(f"Bad credentials")
                errors[CONF_USERNAME] = "bad_credentials"
                errors[CONF_PASSWORD] = "bad_credentials"
            except PupilListError:
                _LOGGER.exception(f"List of pupils is empty")
                errors["base"] = "pupils_empty"
            except Exception as ex:
                _LOGGER.exception(f"Unknown error: {ex}")
                errors["base"] = "unknown_error"

            if not errors:
                await self.async_set_unique_id(f"{DOMAIN}_{api.school}")
                self._abort_if_unique_id_configured()

                config_data = {
                    CONF_SCHOOL: api.school,
                    CONF_USERNAME: api.username,
                    CONF_PASSWORD: api.password,
                }
                return self.async_create_entry(title=api.school_name, data=config_data)

        data_schema = {
            vol.Required(CONF_SCHOOL): str,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        }

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""

        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the main options."""

        errors = {}
        #_LOGGER.debug(f"User input of option flow (init): {user_input}")
        if user_input is not None:
            # Validate user input
            if (
                not user_input[CONF_SECTION_APPOINTMENTS]
                and not user_input[CONF_SECTION_LESSONS]
                and not user_input[CONF_SECTION_LETTERS]
                and not user_input[CONF_SECTION_POLLS]
                and not user_input[CONF_SECTION_REGISTERS]
                and not user_input[CONF_SECTION_SICKNOTES]
            ):
                errors["base"] = "sections_empty"

            if not errors:
                self.section_input = user_input
                return await self.async_step_appointment()

        data_schema = {
            vol.Optional(
                CONF_SECTION_APPOINTMENTS,
                default=self.config_entry.options.get(
                    CONF_SECTION_APPOINTMENTS, DEFAULT_SECTION_APPOINTMENTS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_LESSONS,
                default=self.config_entry.options.get(
                    CONF_SECTION_LESSONS, DEFAULT_SECTION_LESSONS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_LETTERS,
                default=self.config_entry.options.get(
                    CONF_SECTION_LETTERS, DEFAULT_SECTION_LETTERS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_POLLS,
                default=self.config_entry.options.get(
                    CONF_SECTION_POLLS,
                    DEFAULT_SECTION_POLLS,
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_REGISTERS,
                default=self.config_entry.options.get(
                    CONF_SECTION_REGISTERS, DEFAULT_SECTION_REGISTERS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_SICKNOTES,
                default=self.config_entry.options.get(
                    CONF_SECTION_SICKNOTES, DEFAULT_SECTION_SICKNOTES
                ),
            ): bool,
        }

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_appointment(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the appointment options."""

        if not self.section_input[CONF_SECTION_APPOINTMENTS]:
            self.appointment_input = {}
            return await self.async_step_register()

        errors = {}
        #_LOGGER.debug(f"User input of option flow (appointment): {user_input}")
        if user_input is not None:
            # Validate user input

            if not errors:
                self.appointment_input = user_input
                return await self.async_step_register()

        data_schema = {
            vol.Optional(
                CONF_CALENDAR_APPOINTMENT,
                default=self.config_entry.options.get(
                    CONF_CALENDAR_APPOINTMENT, DEFAULT_CALENDAR_APPOINTMENT
                ),
            ): bool,
        }

        return self.async_show_form(
            step_id="appointment", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_register(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the register options."""

        if not self.section_input[CONF_SECTION_REGISTERS]:
            self.register_input = {}
            return await self.async_step_finish()

        errors = {}
        #_LOGGER.debug(f"User input of option flow (register): {user_input}")
        if user_input is not None:
            # Validate user input
            if (
                user_input[CONF_REGISTER_START_MIN]
                > user_input[CONF_REGISTER_START_MAX]
            ):
                errors[CONF_REGISTER_START_MIN] = "register_start_min_max"
                errors[CONF_REGISTER_START_MAX] = "register_start_min_max"

            if not errors:
                self.register_input = user_input
                return await self.async_step_finish()

        data_schema = {
            vol.Optional(
                CONF_REGISTER_START_MIN,
                default=self.config_entry.options.get(
                    CONF_REGISTER_START_MIN, DEFAULT_REGISTER_START_MIN
                ),
            ): int,
            vol.Optional(
                CONF_REGISTER_START_MAX,
                default=self.config_entry.options.get(
                    CONF_REGISTER_START_MAX, DEFAULT_REGISTER_START_MAX
                ),
            ): int,
            vol.Optional(
                CONF_CALENDAR_REGISTER,
                default=self.config_entry.options.get(
                    CONF_CALENDAR_REGISTER, DEFAULT_CALENDAR_REGISTER
                ),
            ): bool,
            vol.Optional(
                CONF_SENSOR_REGISTER,
                default=self.config_entry.options.get(
                    CONF_SENSOR_REGISTER, DEFAULT_SENSOR_REGISTER
                ),
            ): bool,
            vol.Optional(
                CONF_REGISTER_COMPLETION_TRESHOLD,
                default=self.config_entry.options.get(
                    CONF_REGISTER_COMPLETION_TRESHOLD,
                    DEFAULT_REGISTER_COMPLETION_TRESHOLD,
                ),
            ): int,
        }

        return self.async_show_form(
            step_id="register", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_finish(self) -> FlowResult:
        """Manage the option flow finish."""

        option_data = {
            CONF_CALENDAR_APPOINTMENT: self.appointment_input.get(CONF_CALENDAR_APPOINTMENT),
            CONF_CALENDAR_REGISTER: self.register_input.get(CONF_CALENDAR_REGISTER),
            CONF_REGISTER_COMPLETION_TRESHOLD: self.register_input.get(CONF_REGISTER_COMPLETION_TRESHOLD),
            CONF_REGISTER_START_MAX: self.register_input.get(CONF_REGISTER_START_MAX),
            CONF_REGISTER_START_MIN: self.register_input.get(CONF_REGISTER_START_MIN),
            CONF_SECTION_APPOINTMENTS: self.section_input[CONF_SECTION_APPOINTMENTS],
            CONF_SECTION_LESSONS: self.section_input[CONF_SECTION_LESSONS],
            CONF_SECTION_LETTERS: self.section_input[CONF_SECTION_LETTERS],
            CONF_SECTION_POLLS: self.section_input[CONF_SECTION_POLLS],
            CONF_SECTION_REGISTERS: self.section_input[CONF_SECTION_REGISTERS],
            CONF_SECTION_SICKNOTES: self.section_input[CONF_SECTION_SICKNOTES],
            CONF_SENSOR_REGISTER: self.register_input.get(CONF_SENSOR_REGISTER),
        }
        #_LOGGER.debug(f"option_data={option_data}")
        return self.async_create_entry(title="", data=option_data)