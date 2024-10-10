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
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    FRIENDLY_NAME,
    CONF_SENSOR_REGISTER
)
from .coordinator import ElternPortalCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up entities from config entry."""
    
    _LOGGER.debug("Setup entities from config entry started")

    coordinator: ElternPortalCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for pupil_id in coordinator.api.pupils:
        #_LOGGER.debug(f"pupil_id={pupil_id}")
        entities.append(ElternPortalSensor(coordinator, pupil_id))
        if entry.options.get(CONF_SENSOR_REGISTER):
            entities.append(ElternPortalRegisterSensor(coordinator, pupil_id))
    
    async_add_entities(entities)
    _LOGGER.debug("Setup entities from config entry ended")


class ElternPortalSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a Sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        _LOGGER.debug(f"Setup sensor entry started")
        super().__init__(coordinator)

        firstname = coordinator.api.pupils.get(pupil_id).get("firstname")
        self.api = coordinator.api
        self.pupil_id = pupil_id

        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_base_{pupil_id}"
        self._attr_unique_id = f"{DOMAIN}_base_{pupil_id}"
        self._attr_name = f"{FRIENDLY_NAME} {firstname}"
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


class ElternPortalRegisterSensor(CoordinatorEntity[ElternPortalCoordinator], SensorEntity):
    """Representation of a register sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ElternPortalCoordinator, pupil_id: str) -> None:
        _LOGGER.debug(f"Setup sensor register started")
        super().__init__(coordinator)

        firstname = coordinator.api.pupils.get(pupil_id).get("firstname")
        self.api = coordinator.api
        self.pupil_id = pupil_id

        self.entity_id = f"{Platform.SENSOR}.{DOMAIN}_register_{pupil_id}"
        self._attr_unique_id = f"{DOMAIN}_register_{pupil_id}"
        self._attr_name = f"{FRIENDLY_NAME} {firstname} Class Register"
        self._attr_icon = "mdi:briefcase"
        self._attr_native_unit_of_measurement = None
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT

        _LOGGER.debug("Setup sensor register ended")

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
        treshold = datetime.date.today() + datetime.timedelta(days=0)
        registers = list(filter(lambda register: register["done"] > treshold, registers))
        return len(registers)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the sensor."""

        pupil = self.api.pupils.get(self.pupil_id)
        registers = pupil["registers"]
        treshold = datetime.date.today()
        registers = list(filter(lambda register: register["done"] > treshold, registers))
        registers.sort(key=lambda register: (register["done"], register["start"]))
        return {
            "list": registers,
            "last_update": self.api.last_update,
        }
