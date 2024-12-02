"""Platform for calendar integration."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pyelternportal import ElternPortalAPI, Student

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CALENDAR_APPOINTMENT,
    CALENDAR_REGISTER,
    CALENDAR_SICKNOTE,
    DOMAIN,
    LOGGER,
)
from .coordinator import ElternPortalCoordinator

CALENDAR_KEYS: list[str] = [
    CALENDAR_APPOINTMENT,
    CALENDAR_REGISTER,
    CALENDAR_SICKNOTE,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup elternportal calendar platform."""

    LOGGER.debug("Setup elternportal calendar platform started")
    coordinator: ElternPortalCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[CalendarEntity] = []
    for calendar_key in CALENDAR_KEYS:
        # if coordinator.api.get_option(calendar_key.rstrip("s")):
        if calendar_key == CALENDAR_APPOINTMENT:  # FixMe
            for student in coordinator.api.students:
                entities.append(
                    ElternPortalCalendar(coordinator, entry, student, calendar_key)
                )
    async_add_entities(entities, update_before_add=True)
    LOGGER.debug("Setup elternportal calendar platform ended")


class ElternPortalCalendar(CoordinatorEntity[ElternPortalCoordinator], CalendarEntity):
    """Sensor representation."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ElternPortalCoordinator,
        entry: ConfigEntry,
        student: Student,
        calendar_key: str,
    ) -> None:
        """Initialize the sensor."""
        LOGGER.debug(
            "Setup elternportal calendar %s %s started", student.firstname, calendar_key
        )
        super().__init__(coordinator)
        self.api: ElternPortalAPI = coordinator.api
        self.student_id: str = student.student_id
        self.calendar_key: str = calendar_key

        self.entity_id = (
            f"{Platform.CALENDAR}.{DOMAIN}_{calendar_key}_{student.student_id}"
        )
        self._attr_unique_id = f"{entry.unique_id}_{calendar_key}_{student.student_id}"
        self._name = f"{student.firstname} {calendar_key}"
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

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        LOGGER.debug("ElternPortalCalendar.name")
        return self._name

    @property
    def event(self) -> CalendarEvent:
        """Return the next upcoming event."""
        LOGGER.debug("ElternPortalCalendar.event")
        return self._event

    # pylint: disable=unused-argument
    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        LOGGER.debug(
            "ElternPortalCalendar.async_get_events: len(self._events)=%d",
            len(self._events),
        )
        LOGGER.debug(
            "ElternPortalCalendar.async_get_events: start=%s, end=%s",
            start_date,
            end_date,
        )

        tzinfo = start_date.tzinfo or timezone.utc
        LOGGER.debug("ElternPortalCalendar.async_get_events: timezone=%s", tzinfo)
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

        LOGGER.debug(
            "ElternPortalCalendar.async_get_events: len(events_in_range)=%d",
            len(events_in_range),
        )
        return events_in_range

    async def async_update(self) -> None:
        """Update status."""

        LOGGER.debug(
            "ElternPortalCalendar.async_update: %s(%s)",
            self.calendar_key,
            self.student_id,
        )
        self._events = []

        # start, end, summary, description, location, uid, recurrence_id, rrule
        for student in self.api.students:
            if student.student_id == self.student_id:
                if self.calendar_key == CALENDAR_APPOINTMENT:
                    LOGGER.debug(
                        "ElternPortalCalendar.async_update: len(student.appointments)=%d",
                        len(student.appointments),
                    )
                    for appointment in student.appointments:
                        event = CalendarEvent(
                            start=appointment.start,
                            end=appointment.end + timedelta(days=1),
                            summary=appointment.title,
                            description=None,
                            location=None,
                        )
                        self._events.append(event)
                        LOGGER.debug("ElternPortalCalendar.fill_events: %s", event)

                if self.calendar_key == CALENDAR_REGISTER:
                    for register in student.registers:
                        event = CalendarEvent(
                            start=register.start,
                            end=register.completion + timedelta(days=1),
                            summary=register.title,
                            description=register.body,
                            location=None,
                        )
                        self._events.append(event)

                if self.calendar_key == CALENDAR_SICKNOTE:
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
