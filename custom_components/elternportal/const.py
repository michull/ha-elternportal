"""Constants for elternportal integration."""

from __future__ import annotations

import datetime

from homeassistant.const import Platform

DOMAIN = "elternportal"
ATTRIBUTION = "Data provided by art soft and more GmbH"
FRIENDLY_NAME = "Eltern-Portal"

CONF_SCHOOL = "school"

CONF_REGISTER_START_MIN: str = "register_start_min"
DEFAULT_REGISTER_START_MIN: int = -6

CONF_REGISTER_START_MAX: str = "register_start_max"
DEFAULT_REGISTER_START_MAX: int = +2

CONF_REGISTER_COMPLETION_TRESHOLD: str = "register_completion_treshold"
DEFAULT_REGISTER_COMPLETION_TRESHOLD: int = +1

CONF_REGISTER_SHOW_EMPTY: str = "register_show_empty"
DEFAULT_REGISTER_SHOW_EMPTY: bool = False

CONF_CALENDAR_APPOINTMENT: str = "calendar_appointment"
DEFAULT_CALENDAR_APPOINTMENT: bool = False

CONF_CALENDAR_REGISTER: str = "calendar_register"
DEFAULT_CALENDAR_REGISTER: bool = False

CONF_SENSOR_REGISTER: str = "sensor_register"
DEFAULT_SENSOR_REGISTER: bool = False

DEFAULT_SCAN_INTERVAL: datetime.timedelta = datetime.timedelta(minutes=180)

PLATFORMS = [Platform.CALENDAR, Platform.SENSOR]

CONF_SECTION_APPOINTMENTS: str = "section_appointments"
CONF_SECTION_BLACKBOARDS: str = "section_blackboards"
CONF_SECTION_LESSONS: str = "section_lessons"
CONF_SECTION_LETTERS: str = "section_letters"
CONF_SECTION_POLLS: str = "section_polls"
CONF_SECTION_REGISTERS: str = "section_registers"  # /service/klassenbuch
CONF_SECTION_SICKNOTES: str = "section_sicknotes"  # /meldungen/krankmeldung

DEFAULT_SECTION_APPOINTMENTS: bool = True
DEFAULT_SECTION_BLACKBOARDS: bool = False
DEFAULT_SECTION_LESSONS: bool = False
DEFAULT_SECTION_LETTERS: bool = True
DEFAULT_SECTION_POLLS: bool = False
DEFAULT_SECTION_REGISTERS: bool = False
DEFAULT_SECTION_SICKNOTES: bool = False
