"""Platform for sensor integration."""

from __future__ import annotations

import datetime
import logging
import pytz

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ElternPortalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up entities from config entry."""
    
    _LOGGER.debug("Setup entities from config entry started")

    coordinator: ElternPortalCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for pupil_id in coordinator.api.pupils:
        _LOGGER.debug(f"pupil_id={pupil_id}")
        entities.append(ElternPortalSensor(coordinator, pupil_id))
        entities.append(ElternPortalElternbriefSensor(coordinator, pupil_id))
        entities.append(ElternPortalKlassenbuchSensor(coordinator, pupil_id))
        entities.append(ElternPortalTerminSensor(coordinator, pupil_id))
    
    async_add_entities(entities)
    _LOGGER.debug("Setup entities from config entry ended")


class ElternPortalSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        _LOGGER.debug(f"Setup sensor entry started")
        super().__init__(coordinator)
        self.api = coordinator.api
        self.pupil_id = pupil_id
        self.firstname = coordinator.api.pupils.get(pupil_id)["firstname"]

        self._attr_unique_id = f"{DOMAIN}_base_{pupil_id}"
        self._attr_name = f"Elternportal {self.firstname}"
        self._attr_icon = "mdi:account-school"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        _LOGGER.debug("Setup sensor entry ended")

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""
        return self.pupil_id in self.api.pupils

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        
        return self.api.pupils.get(self.pupil_id)["native_value"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""
        
        return self.api.pupils.get(self.pupil_id)


class ElternPortalElternbriefSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a Elternbrief Sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        _LOGGER.debug(f"Setup sensor elternbrief started")
        super().__init__(coordinator)
        self.api = coordinator.api
        self.pupil_id = pupil_id
        self.firstname = coordinator.api.pupils.get(pupil_id)["firstname"]

        self._attr_unique_id = f"{DOMAIN}_elternbrief_{pupil_id}"
        self._attr_name = f"Elternportal {self.firstname} Elternbrief"
        self._attr_icon = "mdi:email"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        _LOGGER.debug("Setup sensor elternbrief ended")

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""

        pupil = self.api.pupils.get(self.pupil_id)
        return pupil["letters"] is not None

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""

        pupil = self.api.pupils.get(self.pupil_id)
        letters = list(filter(lambda r: r["new"], pupil["letters"]))
        return len(letters)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        pupil = self.api.pupils.get(self.pupil_id)
        letters = list(filter(lambda r: r["new"], pupil["letters"]))
        letters.sort(key=lambda r: r["number"])
        return {
            "list": letters,
            "last_update": self.api.last_update,
        }


class ElternPortalKlassenbuchSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a Klassenbuch Sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        _LOGGER.debug(f"Setup sensor klassenbuch started")
        super().__init__(coordinator)
        self.api = coordinator.api
        self.pupil_id = pupil_id
        self.firstname = coordinator.api.pupils.get(pupil_id)["firstname"]

        self._attr_unique_id = f"{DOMAIN}_klassenbuch_{pupil_id}"
        self._attr_name = f"Elternportal {self.firstname} Klassenbuch"
        self._attr_icon = "mdi:briefcase"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        _LOGGER.debug("Setup sensor klassenbuch ended")

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""

        pupil = self.api.pupils.get(self.pupil_id)
        registers = pupil["registers"]
        return registers is not None

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""

        pupil = self.api.pupils.get(self.pupil_id)
        registers = pupil["registers"]
        treshold = datetime.date.today()
        registers = list(filter(lambda r: r["done"] > treshold, registers))
        return len(registers)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        pupil = self.api.pupils.get(self.pupil_id)
        registers = pupil["registers"]
        treshold = datetime.date.today()
        registers = list(filter(lambda r: r["done"] > treshold, registers))
        registers.sort(key=lambda r: r["done"])
        return {
            "list": registers,
            "last_update": self.api.last_update,
        }


class ElternPortalTerminSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a Termin Sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        _LOGGER.debug(f"Setup sensor termin started")
        super().__init__(coordinator)
        self.api = coordinator.api
        self.pupil_id = pupil_id
        self.firstname = coordinator.api.pupils.get(pupil_id)["firstname"]
        self.timezone = pytz.timezone("Europe/Berlin")

        self._attr_unique_id = f"{DOMAIN}_termin_{pupil_id}"
        self._attr_name = f"Elternportal {self.firstname} Termin"
        self._attr_icon = "mdi:clock"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        _LOGGER.debug("Setup sensor termin ended")

    @property
    def available(self) -> bool:
        """Could the device be accessed during the last update call."""

        pupil = self.api.pupils.get(self.pupil_id)
        return pupil["appointments"] is not None

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""

        pupil = self.api.pupils.get(self.pupil_id)
        end = datetime.date.today()
        end = datetime.datetime.combine(end, datetime.time.min)
        end = self.timezone.localize(end)
        start = datetime.date.today() + datetime.timedelta(days=6)
        start = datetime.datetime.combine(start, datetime.time.min)
        start = self.timezone.localize(start)
        appointments = list(filter(lambda a: a["start"] <= start and a["end"] > end, pupil["appointments"]))
        return len(appointments)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        pupil = self.api.pupils.get(self.pupil_id)
        end = datetime.date.today()
        end = datetime.datetime.combine(end, datetime.time.min)
        end = self.timezone.localize(end)
        start = datetime.date.today() + datetime.timedelta(days=6)
        start = datetime.datetime.combine(start, datetime.time.min)
        start = self.timezone.localize(start)
        appointments = list(filter(lambda a: a["start"] <= start and a["end"] > end, pupil["appointments"]))
        appointments.sort(key=lambda a: a["start"])
        return {
            "list": appointments,
            "last_update": self.api.last_update,
        }
