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
    for pupil in coordinator.api.pupils:
        entities.append(ElternPortalSensor(coordinator, pupil))
        if entry.options.get(CONF_SENSOR_REGISTER, DEFAULT_SENSOR_REGISTER):
            completion_treshold: int = entry.options.get(
                CONF_REGISTER_COMPLETION_TRESHOLD, DEFAULT_REGISTER_COMPLETION_TRESHOLD
            )
            entities.append(
                ElternPortalRegisterSensor(coordinator, pupil, completion_treshold)
            )

    async_add_entities(entities, update_before_add=False)
    _LOGGER.debug("Setup elternportal sensor platform ended")


class ElternPortalSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: ElternPortalCoordinator, pupil: pyelternportal.Pupil
    ) -> None:
        _LOGGER.debug("Setup sensor entry started")
        super().__init__(coordinator)

        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_base_{pupil.pupil_id}"
        self._attr_unique_id = f"{DOMAIN}_base_{pupil.pupil_id}"
        self._attr_name = f"{FRIENDLY_NAME} {pupil.firstname}"
        self._attr_icon = "mdi:account-school"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        self.api: pyelternportal.ElternPortalAPI = coordinator.api
        self.pupil: pyelternportal.Pupil = pupil

        _LOGGER.debug("Setup sensor entry ended")

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        return self.pupil is not None

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""

        return self.pupil.get_count()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        return {
            "pupil_id": self.pupil.pupil_id,
            "fullname": self.pupil.fullname,
            "firstname": self.pupil.firstname,
            "lastname": self.pupil.lastname,
            "classname": self.pupil.classname,
            "appointments": self.pupil.appointments,
            "lessons": self.pupil.lessons,
            "letters": self.pupil.letters,
            "polls": self.pupil.polls,
            "registers": self.pupil.registers,
            "sicknotes": self.pupil.sicknotes,
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
        pupil: pyelternportal.Pupil,
        completion_treshold: int,
    ) -> None:
        _LOGGER.debug("Setup sensor register started")
        super().__init__(coordinator)

        self.api: pyelternportal.ElternPortalAPI = coordinator.api
        self.pupil: pyelternportal.Pupil = pupil
        self.completion_treshold: int = completion_treshold

        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_register_{pupil.pupil_id}"
        self._attr_unique_id = f"{DOMAIN}_register_{pupil.pupil_id}"
        self._attr_name = f"{FRIENDLY_NAME} {pupil.firstname} Class Register"
        self._attr_icon = "mdi:briefcase"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        _LOGGER.debug("Setup sensor register ended")

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""

        return self.pupil.registers is not None

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""

        treshold = datetime.date.today() + datetime.timedelta(
            days=self.completion_treshold
        )
        registers = list(
            filter(lambda register: register.completion > treshold, self.pupil.registers)
        )
        return len(registers)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        treshold = datetime.date.today() + datetime.timedelta(
            days=self.completion_treshold
        )
        registers: list[pyelternportal.Register] = list(
            filter(lambda register: register.completion >= treshold, self.pupil.registers)
        )
        registers.sort(key=lambda register: (register.completion, register.start))
        return {
            "registers": registers,
            "last_update": self.api.last_update,
        }
