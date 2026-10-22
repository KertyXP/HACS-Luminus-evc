"""Buttons for Luminus EVC integration."""
from __future__ import annotations

import logging
from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SPOT_ID, DOMAIN
from .coordinator import LuminusDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luminus EVC buttons."""
    coordinator: LuminusDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    spot_id = entry.data[CONF_SPOT_ID]

    entities = [
        LuminusRefreshButton(coordinator, spot_id),
        LuminusRebootButton(coordinator, spot_id),
    ]
    async_add_entities(entities)


class LuminusRefreshButton(CoordinatorEntity[LuminusDataUpdateCoordinator], ButtonEntity):
    """Button to manually force refresh Luminus EVC data."""

    def __init__(
        self,
        coordinator: LuminusDataUpdateCoordinator,
        spot_id: str,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self._spot_id = spot_id
        self._attr_unique_id = f"luminus_evc_{spot_id}_force_refresh"
        self._attr_name = "Force Refresh"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:refresh"
        self._attr_entity_category = EntityCategory.CONFIG

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

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Force refresh requested for Luminus Wallbox %s", self._spot_id)
        await self.coordinator.async_request_refresh()


class LuminusRebootButton(CoordinatorEntity[LuminusDataUpdateCoordinator], ButtonEntity):
    """Button to soft reboot the Luminus Wallbox via cloud action."""

    def __init__(
        self,
        coordinator: LuminusDataUpdateCoordinator,
        spot_id: str,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self._spot_id = spot_id
        self._attr_unique_id = f"luminus_evc_{spot_id}_reboot"
        self._attr_name = "Restart Wallbox"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:restart"
        self._attr_device_class = ButtonDeviceClass.RESTART
        self._attr_entity_category = EntityCategory.CONFIG

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

    async def async_press(self) -> None:
        """Handle reboot action press."""
        _LOGGER.info("Soft reboot command sent to Luminus Wallbox %s", self._spot_id)
        success = await self.coordinator.client.async_execute_action("SoftReset")
        if success:
            await self.coordinator.async_request_refresh()
