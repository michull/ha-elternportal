"""Constants for elternportal integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.const import Platform

LOGGER = logging.getLogger(__name__)

DOMAIN: str = "elternportal"
ATTRIBUTION: str = "Data provided by art soft and more GmbH"
FRIENDLY_NAME: str = "Eltern-Portal"

CONF_SCHOOL: str = "school"


CONF_APPOINTMENT_CAL: str = "appointment_calendar"
DEFAULT_APPOINTMENT_CAL: bool = False

CONF_BLACKBOARD_TRESHOLD: str = "blackboard_treshold"
DEFAULT_BLACKBOARD_TRESHOLD: int = -7

CONF_LETTER_TRESHOLD: str = "letter_treshold"
DEFAULT_LETTER_TRESHOLD: int = -7

CONF_MESSAGE_TRESHOLD: str = "message_treshold"
DEFAULT_MESSAGE_TRESHOLD: int = -7

CONF_POLL_TRESHOLD: str = "poll_treshold"
DEFAULT_POLL_TRESHOLD: int = -7

CONF_REGISTER_CAL: str = "register_calendar"
DEFAULT_REGISTER_CAL: bool = False

CONF_REGISTER_START_MIN: str = "register_start_min"
DEFAULT_REGISTER_START_MIN: int = -6

CONF_REGISTER_START_MAX: str = "register_start_max"
DEFAULT_REGISTER_START_MAX: int = +2

CONF_REGISTER_SHOW_EMPTY: str = "register_show_empty"
DEFAULT_REGISTER_SHOW_EMPTY: bool = False

CONF_REGISTER_TRESHOLD: str = "register_treshold"
DEFAULT_REGISTER_TRESHOLD: int = +1

CONF_SICKNOTE_TRESHOLD: str = "sicknote_treshold"
DEFAULT_SICKNOTE_TRESHOLD: int = +1

DEFAULT_SCAN_INTERVAL: timedelta = timedelta(minutes=180)

PLATFORMS: list[Platform] = [Platform.CALENDAR, Platform.SENSOR]

CONF_SECTION_APPOINTMENTS: str = "section_appointments"
CONF_SECTION_BLACKBOARDS: str = "section_blackboards"
CONF_SECTION_LESSONS: str = "section_lessons"
CONF_SECTION_LETTERS: str = "section_letters"
CONF_SECTION_MESSAGES: str = "section_messages"
CONF_SECTION_POLLS: str = "section_polls"
CONF_SECTION_REGISTERS: str = "section_registers"
CONF_SECTION_SICKNOTES: str = "section_sicknotes"

DEFAULT_SECTION_APPOINTMENTS: bool = True
DEFAULT_SECTION_BLACKBOARDS: bool = False
DEFAULT_SECTION_LESSONS: bool = False
DEFAULT_SECTION_LETTERS: bool = True
DEFAULT_SECTION_MESSAGES: bool = False
DEFAULT_SECTION_POLLS: bool = False
DEFAULT_SECTION_REGISTERS: bool = False
DEFAULT_SECTION_SICKNOTES: bool = False

SENSOR_APPOINTMENT: str = "appointment"
SENSOR_BLACKBOARD: str = "blackboard"
SENSOR_LESSON: str = "lesson"
SENSOR_LETTER: str = "letter"
SENSOR_MESSAGE: str = "message"
SENSOR_POLL: str = "poll"
SENSOR_REGISTER: str = "register"
SENSOR_SICKNOTE: str = "sicknote"

CALENDAR_APPOINTMENT: str = "appointment"
CALENDAR_REGISTER: str = "register"
CALENDAR_SICKNOTE: str = "sicknote"
