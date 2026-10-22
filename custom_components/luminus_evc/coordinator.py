"""DataUpdateCoordinator for Luminus EVC integration."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN
from .luminus_api import LuminusApiClient, LuminusAuthError, LuminusConnectionError

_LOGGER = logging.getLogger(__name__)


class LuminusDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Luminus EVC data from the portal."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LuminusApiClient,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{client._spot_id}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Luminus EVC API."""
        try:
            return await self.client.async_fetch_data()
        except LuminusAuthError as err:
            raise UpdateFailed(f"Authentication error with Luminus EVC: {err}") from err
        except LuminusConnectionError as err:
            raise UpdateFailed(f"Connection error with Luminus EVC: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error communicating with Luminus EVC: {err}") from err
