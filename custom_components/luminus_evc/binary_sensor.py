"""Binary sensors for Luminus EVC integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SPOT_ID, DOMAIN
from .coordinator import LuminusDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class LuminusBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Luminus binary sensor entities."""

    value_fn: Callable[[dict[str, Any]], bool]


BINARY_SENSOR_TYPES: tuple[LuminusBinarySensorEntityDescription, ...] = (
    # Primary user binary sensors
    LuminusBinarySensorEntityDescription(
        key="is_charging",
        name="Charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda data: bool(data.get("is_charging", False)),
    ),
    LuminusBinarySensorEntityDescription(
        key="is_plugged",
        name="Vehicle Connected",
        device_class=BinarySensorDeviceClass.PLUG,
        value_fn=lambda data: bool(data.get("is_plugged", False)),
    ),

    # Diagnostic binary sensors
    LuminusBinarySensorEntityDescription(
        key="cloud_connected",
        name="Cloud API Connected",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda data: bool(data.get("cloud_connected", True)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luminus EVC binary sensors."""
    coordinator: LuminusDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    spot_id = entry.data[CONF_SPOT_ID]

    entities = [
        LuminusBinarySensor(coordinator, description, spot_id)
        for description in BINARY_SENSOR_TYPES
    ]
    async_add_entities(entities)


class LuminusBinarySensor(
    CoordinatorEntity[LuminusDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of a Luminus EVC binary sensor."""

    entity_description: LuminusBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: LuminusDataUpdateCoordinator,
        description: LuminusBinarySensorEntityDescription,
        spot_id: str,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._spot_id = spot_id
        self._attr_unique_id = f"luminus_evc_{spot_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        connector = (
            self.coordinator.data.get("connector", "Type 2")
            if self.coordinator.data
            else "Type 2"
        )
        return DeviceInfo(
            identifiers={(DOMAIN, self._spot_id)},
            name=f"Luminus Wallbox {self._spot_id}",
            manufacturer="Luminus",
            model=f"Wallbox ({connector})",
            sw_version="Cloud EVC",
        )

    @property
    def is_on(self) -> bool:
        """Return true if binary sensor is on."""
        if not self.coordinator.data:
            return False
        return self.entity_description.value_fn(self.coordinator.data)
