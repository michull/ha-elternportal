"""Constants for elternportal integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "elternportal"
FRIENDLY_NAME = "Eltern-Portal"

CONF_SCHOOL = "school"

CONF_REGISTER_START_MIN = "register_start_min"
DEFAULT_REGISTER_START_MIN = -7

CONF_REGISTER_START_MAX = "register_start_max"
DEFAULT_REGISTER_START_MAX = +7

CONF_REGISTER_DONE_TRESHOLD = "register_done_treshold"
DEFAULT_REGISTER_DONE_TRESHOLD = 0

CONF_SENSOR_REGISTER = "sensor_register"
DEFAULT_SENSOR_REGISTER = False

DEFAULT_SCAN_INTERVAL = timedelta(minutes=180)

PLATFORMS = [Platform.SENSOR]
