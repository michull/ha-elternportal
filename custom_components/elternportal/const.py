"""Constants for elternportal integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "elternportal"

CONF_SCHOOL = "school"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=180)

PLATFORMS = [Platform.SENSOR]
