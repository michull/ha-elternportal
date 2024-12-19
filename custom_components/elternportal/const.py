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
