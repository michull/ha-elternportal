from __future__ import annotations

import datetime
import logging

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CALENDAR_APPOINTMENT,
    CONF_CALENDAR_REGISTER,
    DEFAULT_CALENDAR_APPOINTMENT,
    DEFAULT_CALENDAR_REGISTER,
    DOMAIN,
    FRIENDLY_NAME,
)
from .coordinator import ElternPortalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup elternportal calendar platform."""

    _LOGGER.debug("Setup elternportal calendar platform started")

    coordinator: ElternPortalCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for pupil_id in coordinator.api.pupils:
        if entry.options.get(CONF_CALENDAR_APPOINTMENT, DEFAULT_CALENDAR_APPOINTMENT):
            entities.append(ElternPortalAppointmentCalendar(coordinator, pupil_id))

        if entry.options.get(CONF_CALENDAR_REGISTER, DEFAULT_CALENDAR_REGISTER):
            entities.append(ElternPortalRegisterCalendar(coordinator, pupil_id))

    async_add_entities(entities, update_before_add=True)
    _LOGGER.debug("Setup elternportal calendar platform ended")


class ElternPortalAppointmentCalendar(
    CoordinatorEntity[ElternPortalCoordinator], CalendarEntity
):
    """Representation of a elternportal appointment calendar."""

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        """Initialize the elternportal appointment calendar."""

        _LOGGER.debug("Setup calendar appointment started")
        super().__init__(coordinator)

        firstname = coordinator.api.pupils.get(pupil_id).get("firstname")
        self.api = coordinator.api
        self.pupil_id = pupil_id

        self.entity_id = f"{Platform.CALENDAR}.{DOMAIN}_apppointment_{pupil_id}"
        self._attr_unique_id = f"{DOMAIN}_appointment_{pupil_id}"
        self._name = f"{FRIENDLY_NAME} Appointment {firstname}"
        self._icon = "mdi:school-outline"

        self._event = None
        self._events = []

        _LOGGER.debug("Setup calendar appointment ended")

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def event(self) -> CalendarEvent:
        """Return the next upcoming event."""
        return self._event

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""

        # Use the timezone of the start_date (or Home Assistant timezone)
        timezone = start_date.tzinfo or datetime.timezone.utc
        events_in_range = []
        for event in self._events:
            event_start = datetime.datetime(
                event.start.year, event.start.month, event.start.day
            ).replace(tzinfo=timezone)
            event_end = datetime.datetime(
                event.end.year, event.end.month, event.end.day
            ).replace(tzinfo=timezone)
            if event_start >= start_date and event_end <= end_date:
                events_in_range.append(event)

        return events_in_range

    async def async_update(self) -> None:
        """Update status."""

        _LOGGER.debug(f"ElternPortalAppointmentCalendar.async_update")
        self._events = []
        appointments = self.api.pupils[self.pupil_id]["appointments"]
        for appointment in appointments:
            # start, end, summary, description, location, uid, recurrence_id, rrule
            cevent = CalendarEvent(
                start=appointment["start"],
                end=appointment["end"] + datetime.timedelta(days=1),
                summary=appointment["title"],
            )
            self._events.append(cevent)

        if self._events:
            self._events.sort(key=lambda e: (e.end))
            now = datetime.datetime.now()

            for event in self._events:
                if event.end_datetime_local.astimezone() > now.astimezone():
                    self._event = event
                    break
        else:
            self._event = None


class ElternPortalRegisterCalendar(
    CoordinatorEntity[ElternPortalCoordinator], CalendarEntity
):
    """Representation of a elternportal register calendar."""

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        """Initialize the elternportal register calendar."""

        _LOGGER.debug(f"ElternPortalRegisterCalendar.__init__")
        super().__init__(coordinator)

        firstname = coordinator.api.pupils.get(pupil_id).get("firstname")
        self.api = coordinator.api
        self.pupil_id = pupil_id

        self._name = f"{FRIENDLY_NAME} Register {firstname}"
        self._icon = "mdi:school-outline"
        self._event = None
        self._events = []

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def event(self) -> CalendarEvent:
        """Return the next upcoming event."""
        return self._event

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""

        # Use the timezone of the start_date (or Home Assistant timezone)
        timezone = start_date.tzinfo or datetime.timezone.utc
        events_in_range = []
        for event in self._events:
            event_start = datetime.datetime(
                event.start.year, event.start.month, event.start.day
            ).replace(tzinfo=timezone)
            event_end = datetime.datetime(
                event.end.year, event.end.month, event.end.day
            ).replace(tzinfo=timezone)
            if event_start >= start_date and event_end <= end_date:
                events_in_range.append(event)

        return events_in_range

    async def async_update(self) -> None:
        """Update status."""

        self._events = []
        registers = self.api.pupils[self.pupil_id]["registers"]
        for register in registers:
            # start, end, summary, description, location, uid, recurrence_id, rrule
            cevent = CalendarEvent(
                start=register["start"],
                end=register["completion"] + datetime.timedelta(days=1),
                summary=(register["subject"] + ", " if register["subject"] else "")
                + register["teacher"],
                description=register["description"],
            )
            self._events.append(cevent)

        if self._events:
            self._events.sort(key=lambda e: (e.end))
            now = datetime.datetime.now()

            for event in self._events:
                if event.end_datetime_local.astimezone() > now.astimezone():
                    self._event = event
                    break
        else:
            self._event = None
