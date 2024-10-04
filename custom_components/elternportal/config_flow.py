"""Config flow for elternportal integration."""

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN, CONF_SCHOOL
from .api import ElternPortalAPI

SCHOOL_SCHEMA = vol.Schema(
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
    
    async def async_step_user(self, user_input):
        
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
            data_schema=SCHOOL_SCHEMA,
        )
        
