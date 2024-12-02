"""Platform for sensor integration."""

from __future__ import annotations

from typing import Any

from pyelternportal import ElternPortalAPI, Student

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    DOMAIN,
    LOGGER,
    SENSOR_APPOINTMENT,
    SENSOR_BLACKBOARD,
    SENSOR_LESSON,
    SENSOR_LETTER,
    SENSOR_MESSAGE,
    SENSOR_POLL,
    SENSOR_REGISTER,
    SENSOR_SICKNOTE,
)
from .coordinator import ElternPortalCoordinator


SENSOR_KEYS: list[str] = [
    SENSOR_APPOINTMENT,
    SENSOR_BLACKBOARD,
    SENSOR_LESSON,
    SENSOR_LETTER,
    SENSOR_MESSAGE,
    SENSOR_POLL,
    SENSOR_REGISTER,
    SENSOR_SICKNOTE,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup elternportal sensor platform."""
    LOGGER.debug("Setup elternportal sensor platform started")
    coordinator: ElternPortalCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[ElternPortalSensor] = []
    for sensor_key in SENSOR_KEYS:
        if coordinator.api.get_option(sensor_key): # FixMe
            for student in coordinator.api.students:
                entities.append(
                    ElternPortalSensor(coordinator, entry, student, sensor_key)
                )
    async_add_entities(entities, update_before_add=True)
    LOGGER.debug("Setup elternportal sensor platform ended")


class ElternPortalSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Sensor representation."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ElternPortalCoordinator,
        entry: ConfigEntry,
        student: Student,
        sensor_key: str,
    ) -> None:
        """Initialize the sensor."""
        LOGGER.debug(
            "Setup elternportal sensor %s %s started", student.firstname, sensor_key
        )
        super().__init__(coordinator)
        self.api: ElternPortalAPI = coordinator.api
        self.student_id: str = student.student_id
        self.sensor_key: str = sensor_key

        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_{sensor_key}_{student.student_id}"
        self._attr_unique_id = f"{entry.unique_id}_{sensor_key}_{student.student_id}"
        self._attr_name = f"{student.firstname} {sensor_key}"
        self._attr_icon = "mdi:account-school"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id, student.student_id)},
            manufacturer=self.api.school_name,
            model=student.firstname,
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_attribution = ATTRIBUTION
        LOGGER.debug("Setting up sensor: %s", self._attr_unique_id)

    def get_elements(self) -> list[Any] | None:
        """Get elements"""
        for student in self.api.students:
            if student.student_id == self.student_id:
                if self.sensor_key==SENSOR_APPOINTMENT:
                    result = student.appointments

                if self.sensor_key==SENSOR_BLACKBOARD:
                    result = student.blackboards

                if self.sensor_key==SENSOR_LESSON:
                    result = student.lessons

                if self.sensor_key==SENSOR_LETTER:
                    result = student.letters

                if self.sensor_key==SENSOR_MESSAGE:
                    result = student.messages

                if self.sensor_key==SENSOR_POLL:
                    result = student.polls

                if self.sensor_key==SENSOR_REGISTER:
                    result = student.registers

                if self.sensor_key==SENSOR_SICKNOTE:
                    result = student.sicknotes

                return result

        LOGGER.error("Sensor %s: elements invalid", self._attr_unique_id)
        return None

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        elements = self.get_elements()
        return len(elements)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = {
            "elements": self.get_elements(),
            "last_update": self.api.last_update,
        }
        return data

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        for student in self.api.students:
            if student.student_id == self.student_id:
                return True
        return False
