"""Constants for elternportal integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "elternportal"
ATTRIBUTION = "Data provided by art soft and more GmbH"
FRIENDLY_NAME = "Eltern-Portal"

CONF_SCHOOL = "school"

CONF_REGISTER_START_MIN = "register_start_min"
DEFAULT_REGISTER_START_MIN = -6

CONF_REGISTER_START_MAX = "register_start_max"
DEFAULT_REGISTER_START_MAX = +2

CONF_REGISTER_COMPLETION_TRESHOLD = "register_completion_treshold"
DEFAULT_REGISTER_COMPLETION_TRESHOLD = +1

CONF_CALENDAR_APPOINTMENT = "calendar_appointment"
DEFAULT_CALENDAR_APPOINTMENT = False

CONF_CALENDAR_REGISTER = "calendar_register"
DEFAULT_CALENDAR_REGISTER = False

CONF_SENSOR_REGISTER = "sensor_register"
DEFAULT_SENSOR_REGISTER = False

DEFAULT_SCAN_INTERVAL = timedelta(minutes=180)

PLATFORMS = [Platform.CALENDAR, Platform.SENSOR]

CONF_SECTION_APPOINTMENTS = "section_appointments"
CONF_SECTION_LESSONS = "section_lessons"
CONF_SECTION_LETTERS = "section_letters"
CONF_SECTION_POLLS = "section_polls"
CONF_SECTION_REGISTERS = "section_registers" # /service/klassenbuch
CONF_SECTION_SICKNOTES = "section_sicknotes" # /meldungen/krankmeldung

DEFAULT_SECTION_APPOINTMENTS = True
DEFAULT_SECTION_LESSONS = False
DEFAULT_SECTION_LETTERS = True
DEFAULT_SECTION_POLLS = False
DEFAULT_SECTION_REGISTERS = False
DEFAULT_SECTION_SICKNOTES = False
