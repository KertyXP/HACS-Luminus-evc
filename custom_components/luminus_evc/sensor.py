"""Sensors for Luminus EVC integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SPOT_ID, DOMAIN
from .coordinator import LuminusDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class LuminusSensorEntityDescription(SensorEntityDescription):
    """Class describing Luminus EVC sensor entities."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSOR_TYPES: tuple[LuminusSensorEntityDescription, ...] = (
    # ================= Primary User Dashboard Sensors =================
    LuminusSensorEntityDescription(
        key="mom_power_kw",
        name="Instant Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("mom_power_kw", 0.0),
    ),
    LuminusSensorEntityDescription(
        key="current_amps",
        name="Charging Current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("current_amps", 0.0),
    ),
    LuminusSensorEntityDescription(
        key="session_energy_kwh",
        name="Session Energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("session_energy_kwh", 0.0),
    ),
    LuminusSensorEntityDescription(
        key="total_consumption_kwh",
        name="Total Consumption",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("total_consumption_kwh", 0.0),
    ),
    LuminusSensorEntityDescription(
        key="soc",
        name="Battery State of Charge",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("soc"),
    ),
    LuminusSensorEntityDescription(
        key="status_text",
        name="Status",
        icon="mdi:ev-station",
        value_fn=lambda data: data.get("status_text", "Unknown"),
    ),
    LuminusSensorEntityDescription(
        key="notification",
        name="Notification",
        icon="mdi:message-badge-outline",
        value_fn=lambda data: data.get("notification", ""),
    ),

    # ================= Diagnostic Category Sensors =================
    LuminusSensorEntityDescription(
        key="past_consumption_kwh",
        name="Past Consumption",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("past_consumption_kwh", 0.0),
    ),
    LuminusSensorEntityDescription(
        key="transaction_time",
        name="Session Duration",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:timer-outline",
        value_fn=lambda data: data.get("transaction_time") or "00:00",
    ),
    LuminusSensorEntityDescription(
        key="card_id",
        name="RFID Card",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:smart-card-outline",
        value_fn=lambda data: data.get("card_id") or "None",
    ),
    LuminusSensorEntityDescription(
        key="customer_name",
        name="User Name",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:account",
        value_fn=lambda data: data.get("customer_name") or "None",
    ),
    LuminusSensorEntityDescription(
        key="connector",
        name="Connector",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:power-plug",
        value_fn=lambda data: data.get("connector", "Type 2"),
    ),
    LuminusSensorEntityDescription(
        key="channel",
        name="Channel",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:numeric",
        value_fn=lambda data: data.get("channel", "1"),
    ),
    LuminusSensorEntityDescription(
        key="status_code",
        name="Status Code",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:code-tags",
        value_fn=lambda data: data.get("status_code", "0"),
    ),
    LuminusSensorEntityDescription(
        key="occupancy_ready_pct",
        name="Availability Rate",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:chart-arc",
        suggested_display_precision=1,
        value_fn=lambda data: data.get("occupancy_ready_pct", 0.0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luminus EVC sensors based on config entry."""
    coordinator: LuminusDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    spot_id = entry.data[CONF_SPOT_ID]

    entities = [
        LuminusSensor(coordinator, description, spot_id)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class LuminusSensor(CoordinatorEntity[LuminusDataUpdateCoordinator], SensorEntity):
    """Representation of a Luminus EVC sensor."""

    entity_description: LuminusSensorEntityDescription

    def __init__(
        self,
        coordinator: LuminusDataUpdateCoordinator,
        description: LuminusSensorEntityDescription,
        spot_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._spot_id = spot_id
        self._attr_unique_id = f"luminus_evc_{spot_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this wallbox."""
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
    def native_value(self) -> Any:
        """Return native value of the sensor."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return 24h history attributes for instant power."""
        if not self.coordinator.data:
            return None

        if self.entity_description.key == "mom_power_kw":
            return {
                "history_labels": self.coordinator.data.get("history_labels", []),
                "history_kw": self.coordinator.data.get("history_kw", []),
            }

        return None
