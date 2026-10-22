"""Home Assistant integration for Luminus EVC electric vehicle wallbox."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_SPOT_ID,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import LuminusDataUpdateCoordinator
from .luminus_api import LuminusApiClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
]

CARD_PATH = Path(__file__).parent / "frontend" / "luminus-evc-card.js"
URL_PATH = "/luminus_evc/luminus-evc-card.js"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Luminus EVC from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    spot_id = entry.data[CONF_SPOT_ID]
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    session = async_get_clientsession(hass)
    client = LuminusApiClient(
        username=username,
        password=password,
        spot_id=spot_id,
        session=session,
    )

    coordinator = LuminusDataUpdateCoordinator(
        hass=hass,
        client=client,
        scan_interval=scan_interval,
    )

    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms (sensor, binary_sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register static path and Lovelace card resource
    await _async_register_frontend_card(hass)

    # Register reload listener for option changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def _async_register_frontend_card(hass: HomeAssistant) -> None:
    """Register the static path and Lovelace resource for the card."""
    if not CARD_PATH.is_file():
        return

    # 1. Register static path with Home Assistant's web server
    if hasattr(hass.http, "async_register_static_paths"):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_PATH, str(CARD_PATH), cache_headers=False)]
        )
    else:
        hass.http.register_static_path(URL_PATH, str(CARD_PATH))

    # 2. Try to automatically register Lovelace resource
    try:
        lovelace = hass.data.get("lovelace")
        if lovelace and hasattr(lovelace, "resources"):
            resources = lovelace.resources
            if hasattr(resources, "async_items") and hasattr(resources, "async_create_item"):
                if not any(item.get("url") == URL_PATH for item in resources.async_items()):
                    await resources.async_create_item(
                        {"res_type": "module", "url": URL_PATH}
                    )
                    _LOGGER.info("Registered Lovelace resource: %s", URL_PATH)
    except Exception as err:
        _LOGGER.debug("Could not auto-register Lovelace resource: %s", err)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)
