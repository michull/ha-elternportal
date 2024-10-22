"""Platform for sensor integration."""

from __future__ import annotations

import datetime
import logging
from typing import Any

import pyelternportal

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_REGISTER_COMPLETION_TRESHOLD,
    CONF_SENSOR_REGISTER,
    DEFAULT_REGISTER_COMPLETION_TRESHOLD,
    DEFAULT_SENSOR_REGISTER,
    DOMAIN,
    FRIENDLY_NAME,
)
from .coordinator import ElternPortalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup elternportal sensor platform."""

    _LOGGER.debug("Setup elternportal sensor platform started")

    coordinator: ElternPortalCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for student in coordinator.api.students:
        entities.append(ElternPortalSensor(coordinator, student))
        if entry.options.get(CONF_SENSOR_REGISTER, DEFAULT_SENSOR_REGISTER):
            completion_treshold: int = entry.options.get(
                CONF_REGISTER_COMPLETION_TRESHOLD, DEFAULT_REGISTER_COMPLETION_TRESHOLD
            )
            entities.append(
                ElternPortalRegisterSensor(coordinator, student, completion_treshold)
            )

    async_add_entities(entities, update_before_add=False)
    _LOGGER.debug("Setup elternportal sensor platform ended")


class ElternPortalSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: ElternPortalCoordinator, student: pyelternportal.Student
    ) -> None:
        _LOGGER.debug("ElternPortalSensor.__init__")
        super().__init__(coordinator)

        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_base_{student.student_id}"
        self._attr_unique_id = f"{DOMAIN}_base_{student.student_id}"
        self._attr_name = f"{FRIENDLY_NAME} {student.firstname}"
        self._attr_icon = "mdi:account-school"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        self.api: pyelternportal.ElternPortalAPI = coordinator.api
        self.student_id: str = student.student_id

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        for student in self.api.students:
            if student.student_id == self.student_id:
                return True
        return False

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        _LOGGER.debug("ElternPortalSensor.native_value")
        _LOGGER.debug("api=%s", self.api)
        _LOGGER.debug("student_id=%s", self.student_id)
        for student in self.api.students:
            if student.student_id == self.student_id:
                _LOGGER.debug("student=%s", student)
                _LOGGER.debug("registers=%s", student.registers)
                _LOGGER.debug("registers=%d", len(student.registers))
                return student.get_count()
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        for student in self.api.students:
            if student.student_id == self.student_id:
                return {
                    "student_id": student.student_id,
                    "fullname": student.fullname,
                    "firstname": student.firstname,
                    "lastname": student.lastname,
                    "classname": student.classname,
                    "appointments": student.appointments,
                    "lessons": student.lessons,
                    "letters": student.letters,
                    "polls": student.polls,
                    "registers": student.registers,
                    "sicknotes": student.sicknotes,
                    "last_update": self.api.last_update,
                }
        return {
            "student_id": self.student_id,
            "fullname": None,
            "firstname": None,
            "lastname": None,
            "classname": None,
            "appointments": None,
            "lessons": None,
            "letters": None,
            "polls": None,
            "registers": None,
            "sicknotes": None,
            "last_update": self.api.last_update,
        }


class ElternPortalRegisterSensor(
    CoordinatorEntity[ElternPortalCoordinator], SensorEntity
):
    """Representation of a register sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ElternPortalCoordinator,
        student: pyelternportal.Student,
        completion_treshold: int,
    ) -> None:
        _LOGGER.debug("ElternPortalRegisterSensor.__init__")
        super().__init__(coordinator)

        self.api: pyelternportal.ElternPortalAPI = coordinator.api
        self.student_id: str = student.student_id
        self.completion_treshold: int = completion_treshold

        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_register_{student.student_id}"
        self._attr_unique_id = f"{DOMAIN}_register_{student.student_id}"
        self._attr_name = f"{FRIENDLY_NAME} {student.firstname} Class Register"
        self._attr_icon = "mdi:briefcase"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        for student in self.api.students:
            if student.student_id == self.student_id:
                return True
        return False

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""

        treshold = datetime.date.today() + datetime.timedelta(
            days=self.completion_treshold
        )
        for student in self.api.students:
            if student.student_id == self.student_id:
                registers = list(
                    filter(
                        lambda register: register.completion > treshold, student.registers
                    )
                )
                return len(registers)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        treshold = datetime.date.today() + datetime.timedelta(
            days=self.completion_treshold
        )
        for student in self.api.students:
            if student.student_id == self.student_id:
                registers: list[pyelternportal.Register] = list(
                    filter(
                        lambda register: register.completion >= treshold,
                        student.registers,
                    )
                )
                registers.sort(
                    key=lambda register: (register.start, register.completion)
                )
                return {
                    "registers": registers,
                    "last_update": self.api.last_update,
                }
        return {
            "registers": None,
            "last_update": self.api.last_update,
        }
