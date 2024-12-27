"""Platform for calendar integration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pyelternportal import ElternPortalAPI, Student
from pyelternportal.const import (
    CONF_APPOINTMENT_CALENDAR,
    CONF_REGISTER_CALENDAR,
    CONF_SICKNOTE_CALENDAR,
)

from .const import (
    ATTRIBUTION,
    DOMAIN,
    LOGGER,
)
from .coordinator import ElternPortalCoordinator

CALENDAR_KEYS: list[str] = [
    CONF_APPOINTMENT_CALENDAR,
    CONF_REGISTER_CALENDAR,
    CONF_SICKNOTE_CALENDAR,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup elternportal calendar platform."""
    LOGGER.debug("Setup elternportal calendar platform started")
    coordinator: ElternPortalCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[CalendarEntity] = []
    for calendar_key in CALENDAR_KEYS:
        if coordinator.api.get_option_calendar(calendar_key):
            for student in coordinator.api.students:
                entities.append(
                    ElternPortalCalendar(coordinator, entry, student, calendar_key)
                )
    async_add_entities(entities, update_before_add=True)
    LOGGER.debug("Setup elternportal calendar platform ended")


class ElternPortalCalendar(CoordinatorEntity[ElternPortalCoordinator], CalendarEntity):
    """Calendar representation."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ElternPortalCoordinator,
        entry: ConfigEntry,
        student: Student,
        calendar_key: str,
    ) -> None:
        """Initialize the calendar."""
        LOGGER.debug(
            "Setup elternportal calendar %s %s started", student.firstname, calendar_key
        )
        super().__init__(coordinator)
        self.api: ElternPortalAPI = coordinator.api
        self.student_id: str = student.student_id
        self.calendar_key: str = calendar_key
        self.last_update: datetime = None
        calendar_text: str = calendar_key.rstrip("_calendar")

        self.entity_id = (
            f"{Platform.CALENDAR}.{DOMAIN}_{calendar_text}_{student.student_id}"
        )
        self._attr_unique_id = f"{entry.unique_id}_{calendar_text}_{student.student_id}"
        self._name = f"{student.firstname} {calendar_text.title()}"
        self._icon = "mdi:account-school"
        self._event: CalendarEvent = None
        self._events: list[CalendarEvent] = []

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id, student.student_id)},
            manufacturer=self.api.school_name,
            model=student.firstname,
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_attribution = ATTRIBUTION
        LOGGER.debug("Setting up calendar: %s", self._attr_unique_id)

    async def async_update(self) -> None:
        """Update status."""

        LOGGER.debug(
            "ElternPortalCalendar.async_update: %s(%s)",
            self.calendar_key,
            self.student_id,
        )
        self.update()

    def update(self) -> None:
        """Update status."""

        if not self.api.last_update or (self.last_update and self.last_update == self.api.last_update):
            return

        self._events = []

        # start, end, summary, description, location, uid, recurrence_id, rrule
        for student in self.api.students:
            if student.student_id == self.student_id:
                if self.calendar_key == CONF_APPOINTMENT_CALENDAR:
                    for appointment in student.appointments:
                        event = CalendarEvent(
                            start=appointment.start,
                            end=appointment.end + timedelta(days=1),
                            summary=appointment.title,
                            description=None,
                            location=None,
                        )
                        self._events.append(event)

                if self.calendar_key == CONF_REGISTER_CALENDAR:
                    for register in student.registers:
                        event = CalendarEvent(
                            start=register.start,
                            end=register.completion + timedelta(days=1),
                            summary=register.subject,
                            description=register.body,
                            location=None,
                        )
                        self._events.append(event)

                if self.calendar_key == CONF_SICKNOTE_CALENDAR:
                    for sicknote in student.sicknotes:
                        event = CalendarEvent(
                            start=sicknote.start,
                            end=sicknote.end + timedelta(days=1),
                            summary="Krankmeldung",
                            description=sicknote.comment,
                            location=None,
                        )
                        self._events.append(event)

        if self._events:
            self._events.sort(key=lambda e: e.end)
            now = datetime.now()
            for event in self._events:
                if event.end_datetime_local.astimezone() > now.astimezone():
                    self._event = event
                    break
        else:
            self._event = None

        self.last_update = self.api.last_update

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def event(self) -> CalendarEvent:
        """Return the next upcoming event."""
        self.update()
        return self._event

    # pylint: disable=unused-argument
    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""

        self.update()
        tzinfo = start_date.tzinfo or timezone.utc
        events_in_range: list[CalendarEvent] = []
        for event in self._events:
            event_start = datetime(
                event.start.year, event.start.month, event.start.day
            ).replace(tzinfo=tzinfo)
            event_end = datetime(
                event.end.year, event.end.month, event.end.day
            ).replace(tzinfo=tzinfo)
            if event_start >= start_date and event_end <= end_date:
                events_in_range.append(event)

        return events_in_range
