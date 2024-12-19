"""Config flow for elternportal integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from pyelternportal import (
    ElternPortalAPI,
    BadCredentialsException,
    CannotConnectException,
    ResolveHostnameException,
    StudentListException,
)
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
    CONF_REGISTER_TRESHOLD,
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
    DEFAULT_REGISTER_TRESHOLD,
    DEFAULT_SICKNOTE_CALENDAR,
    DEFAULT_SICKNOTE_TRESHOLD,
)

from .const import (
    CONF_SCHOOL,
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
)


class ElternPortalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """ElternPortal config flow."""

    VERSION: int = 1
    # MINOR_VERSION: int = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
        errors: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial step."""
        # errors: dict[str, Any] = {}
        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                api: ElternPortalAPI = ElternPortalAPI(session)
                api.set_config_data(user_input)
                await api.async_validate_config()
            except ResolveHostnameException as ex:
                LOGGER.exception("Cannot resolve hostname: %s", ex)
                errors[CONF_SCHOOL] = "cannot_resolve"
            except CannotConnectException as ex:
                LOGGER.exception("Cannot connect: %s", ex)
                errors[CONF_SCHOOL] = "cannot_connect"
            except BadCredentialsException as ex:
                LOGGER.exception("Bad credentials: %s", ex)
                errors[CONF_USERNAME] = "bad_credentials"
                errors[CONF_PASSWORD] = "bad_credentials"
            except StudentListException:
                LOGGER.exception("List of students is empty")
                errors["base"] = "students_empty"
            except Exception as ex:
                LOGGER.exception("Unknown error: %s", ex)
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
            vol.Required(
                CONF_SCHOOL,
                default=(user_input or {}).get(CONF_SCHOOL, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(
                CONF_USERNAME,
                default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(CONF_PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.PASSWORD,
                ),
            ),
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
    """Options flow handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""

        self._config_entry = config_entry
        self.section_input: dict[str, Any] = {}
        self.appointment_input: dict[str, Any] = {}
        self.register_input: dict[str, Any] = {}
        self.sicknote_input: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the main options."""

        errors = {}
        if user_input is not None:
            # Validate user input
            if (
                not user_input[CONF_SECTION_APPOINTMENTS]
                and not user_input[CONF_SECTION_BLACKBOARDS]
                and not user_input[CONF_SECTION_LESSONS]
                and not user_input[CONF_SECTION_LETTERS]
                and not user_input[CONF_SECTION_MESSAGES]
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
                default=self._config_entry.options.get(
                    CONF_SECTION_APPOINTMENTS, DEFAULT_SECTION_APPOINTMENTS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_BLACKBOARDS,
                default=self._config_entry.options.get(
                    CONF_SECTION_BLACKBOARDS, DEFAULT_SECTION_BLACKBOARDS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_LESSONS,
                default=self._config_entry.options.get(
                    CONF_SECTION_LESSONS, DEFAULT_SECTION_LESSONS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_LETTERS,
                default=self._config_entry.options.get(
                    CONF_SECTION_LETTERS, DEFAULT_SECTION_LETTERS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_MESSAGES,
                default=self._config_entry.options.get(
                    CONF_SECTION_MESSAGES,
                    DEFAULT_SECTION_MESSAGES,
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_POLLS,
                default=self._config_entry.options.get(
                    CONF_SECTION_POLLS,
                    DEFAULT_SECTION_POLLS,
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_REGISTERS,
                default=self._config_entry.options.get(
                    CONF_SECTION_REGISTERS, DEFAULT_SECTION_REGISTERS
                ),
            ): bool,
            vol.Optional(
                CONF_SECTION_SICKNOTES,
                default=self._config_entry.options.get(
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
        if user_input is not None:
            # Validate user input

            if not errors:
                self.appointment_input = user_input
                return await self.async_step_register()

        data_schema = {
            vol.Optional(
                CONF_APPOINTMENT_CALENDAR,
                default=self._config_entry.options.get(
                    CONF_APPOINTMENT_CALENDAR, DEFAULT_APPOINTMENT_CALENDAR
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
            return await self.async_step_sicknote()

        errors = {}
        if user_input is not None:
            # Validate user input
            if int(user_input[CONF_REGISTER_START_MIN]) > int(
                user_input[CONF_REGISTER_START_MAX]
            ):
                errors[CONF_REGISTER_START_MIN] = "register_start_min_max"
                errors[CONF_REGISTER_START_MAX] = "register_start_min_max"

            if not errors:
                self.register_input = user_input
                return await self.async_step_sicknote()

        data_schema = {
            vol.Optional(
                CONF_REGISTER_START_MIN,
                default=self._config_entry.options.get(
                    CONF_REGISTER_START_MIN, DEFAULT_REGISTER_START_MIN
                ),
            ): int,
            vol.Optional(
                CONF_REGISTER_START_MAX,
                default=self._config_entry.options.get(
                    CONF_REGISTER_START_MAX, DEFAULT_REGISTER_START_MAX
                ),
            ): int,
            vol.Optional(
                CONF_REGISTER_SHOW_EMPTY,
                default=self._config_entry.options.get(
                    CONF_REGISTER_SHOW_EMPTY, DEFAULT_REGISTER_SHOW_EMPTY
                ),
            ): bool,
            vol.Optional(
                CONF_REGISTER_CALENDAR,
                default=self._config_entry.options.get(
                    CONF_REGISTER_CALENDAR, DEFAULT_REGISTER_CALENDAR
                ),
            ): bool,
            vol.Optional(
                CONF_REGISTER_TRESHOLD,
                default=self._config_entry.options.get(
                    CONF_REGISTER_TRESHOLD,
                    DEFAULT_REGISTER_TRESHOLD,
                ),
            ): int,
        }

        return self.async_show_form(
            step_id="register", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_sicknote(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the sicknote options."""

        if not self.section_input[CONF_SECTION_SICKNOTES]:
            self.sicknote_input = {}
            return await self.async_step_finish()

        errors = {}
        if user_input is not None:
            # Validate user input

            if not errors:
                self.sicknote_input = user_input
                return await self.async_step_finish()

        data_schema = {
            vol.Optional(
                CONF_SICKNOTE_CALENDAR,
                default=self._config_entry.options.get(
                    CONF_SICKNOTE_CALENDAR, DEFAULT_SICKNOTE_CALENDAR
                ),
            ): bool,
        }

        return self.async_show_form(
            step_id="sicknote", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_step_finish(self) -> FlowResult:
        """Manage the option flow finish."""

        option_data = {
            CONF_APPOINTMENT_CALENDAR: self.appointment_input.get(CONF_APPOINTMENT_CALENDAR),
            CONF_APPOINTMENT_TRESHOLD_END: DEFAULT_APPOINTMENT_TRESHOLD_END,
            CONF_APPOINTMENT_TRESHOLD_START: DEFAULT_APPOINTMENT_TRESHOLD_START,
            CONF_BLACKBOARD_TRESHOLD: DEFAULT_BLACKBOARD_TRESHOLD,
            CONF_LETTER_TRESHOLD: DEFAULT_LETTER_TRESHOLD,
            CONF_MESSAGE_TRESHOLD: DEFAULT_MESSAGE_TRESHOLD,
            CONF_POLL_TRESHOLD: DEFAULT_POLL_TRESHOLD,
            CONF_REGISTER_CALENDAR: self.register_input.get(CONF_REGISTER_CALENDAR),
            CONF_REGISTER_SHOW_EMPTY: self.register_input.get(CONF_REGISTER_SHOW_EMPTY),
            CONF_REGISTER_START_MAX: self.register_input.get(CONF_REGISTER_START_MAX),
            CONF_REGISTER_START_MIN: self.register_input.get(CONF_REGISTER_START_MIN),
            CONF_REGISTER_TRESHOLD: self.register_input.get(CONF_REGISTER_TRESHOLD),
            CONF_SECTION_APPOINTMENTS: self.section_input.get(CONF_SECTION_APPOINTMENTS),
            CONF_SECTION_BLACKBOARDS: self.section_input.get(CONF_SECTION_BLACKBOARDS),
            CONF_SECTION_LESSONS: self.section_input.get(CONF_SECTION_LESSONS),
            CONF_SECTION_LETTERS: self.section_input.get(CONF_SECTION_LETTERS),
            CONF_SECTION_MESSAGES: self.section_input.get(CONF_SECTION_MESSAGES),
            CONF_SECTION_POLLS: self.section_input.get(CONF_SECTION_POLLS),
            CONF_SECTION_REGISTERS: self.section_input.get(CONF_SECTION_REGISTERS),
            CONF_SECTION_SICKNOTES: self.section_input.get(CONF_SECTION_SICKNOTES),
            CONF_SICKNOTE_CALENDAR: self.sicknote_input.get(CONF_SICKNOTE_CALENDAR),
            CONF_SICKNOTE_TRESHOLD: DEFAULT_SICKNOTE_TRESHOLD,
        }
        return self.async_create_entry(title="", data=option_data)
