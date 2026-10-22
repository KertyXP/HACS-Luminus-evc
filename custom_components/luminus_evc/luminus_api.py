"""Async API client for Luminus EVC."""
from __future__ import annotations

import json
import logging
import urllib.parse
from typing import Any

import aiohttp

from .const import AJAX_URL, BASE_URL, LOGIN_URL, STATUS_MAP

_LOGGER = logging.getLogger(__name__)


class LuminusAuthError(Exception):
    """Exception raised when authentication fails."""


class LuminusConnectionError(Exception):
    """Exception raised when connection or communication fails."""


class LuminusApiClient:
    """API client to communicate with luminus.evc-net.com."""

    def __init__(
        self,
        username: str,
        password: str,
        spot_id: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize the client."""
        self._username = username
        self._password = password
        self._spot_id = str(spot_id).strip()
        self._session = session
        self._owns_session = False
        self._logged_in = False

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp ClientSession."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                }
            )
            self._owns_session = True
        return self._session

    async def async_close(self) -> None:
        """Close the session if owned."""
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    async def async_login(self) -> bool:
        """Authenticate with the Luminus portal."""
        session = await self._get_session()
        _LOGGER.debug("Authenticating Luminus EVC user %s", self._username)

        try:
            # 1. Access login page to establish initial session/cookies
            async with session.get(LOGIN_URL, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status >= 500:
                    raise LuminusConnectionError(f"Server error on login page: {resp.status}")

            # 2. Submit credentials
            payload = {
                "emailField": self._username,
                "passwordField": self._password,
                "Login": "Log in",
            }
            async with session.post(
                LOGIN_URL,
                data=payload,
                allow_redirects=False,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                _LOGGER.debug("Login POST returned status %s", resp.status)
                # Successful login results in a 302 redirect to /Overview
                if resp.status in (301, 302):
                    loc = resp.headers.get("Location", "")
                    if "/Login" not in loc:
                        self._logged_in = True
                        _LOGGER.debug("Luminus EVC login successful, redirect: %s", loc)
                        return True

                # If status is 200 without redirect, credentials were likely invalid
                text = await resp.text()
                if "Login" in text or "emailField" in text:
                    raise LuminusAuthError("Invalid username or password for Luminus EVC.")

                self._logged_in = True
                return True

        except (aiohttp.ClientError, TimeoutError) as err:
            raise LuminusConnectionError(f"Connection failed during login: {err}") from err

    async def async_fetch_data(self) -> dict[str, Any]:
        """Fetch all data from the Luminus API (auto re-authenticating if needed)."""
        try:
            return await self._async_query_api()
        except LuminusAuthError:
            # Session might have expired; try logging in once more
            _LOGGER.info("Luminus session expired or empty, re-authenticating...")
            await self.async_login()
            return await self._async_query_api()

    async def _async_query_api(self) -> dict[str, Any]:
        """Perform the actual API queries."""
        session = await self._get_session()
        if not self._logged_in:
            await self.async_login()

        # 1. Query DashboardAsyncService (occupancy, current, totalUsage)
        dashboard_req = {
            "0": {
                "handler": "\\LMS\\EV\\AsyncServices\\DashboardAsyncService",
                "method": "occupancy",
                "params": {"mode": 7, "rechargeSpotIds": [self._spot_id], "maxCache": 600},
            },
            "1": {
                "handler": "\\LMS\\EV\\AsyncServices\\DashboardAsyncService",
                "method": "current",
                "params": {"mode": 1, "rechargeSpotIds": [self._spot_id]},
            },
            "2": {
                "handler": "\\LMS\\EV\\AsyncServices\\DashboardAsyncService",
                "method": "totalUsage",
                "params": {
                    "mode": "rechargeSpot",
                    "rechargeSpotIds": [self._spot_id],
                    "maxCache": 3600,
                },
            },
        }

        # 2. Query RechargeSpotsAsyncService (overview)
        overview_req = {
            "0": {
                "handler": "\\LMS\\EV\\AsyncServices\\RechargeSpotsAsyncService",
                "method": "overview",
                "params": {"rechargeSpotId": self._spot_id},
            }
        }

        dash_url = f"{AJAX_URL}?requests={urllib.parse.quote(json.dumps(dashboard_req))}"
        overview_url = f"{AJAX_URL}?requests={urllib.parse.quote(json.dumps(overview_req))}"

        try:
            async with session.get(dash_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise LuminusConnectionError(f"Dashboard query returned status {resp.status}")
                dash_data = await resp.json(content_type=None)

            async with session.get(overview_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    raise LuminusConnectionError(f"Overview query returned status {resp.status}")
                overview_data = await resp.json(content_type=None)

        except (aiohttp.ClientError, TimeoutError) as err:
            raise LuminusConnectionError(f"Error querying Luminus API: {err}") from err

        # If overview_data is empty array [], session likely timed out
        if not overview_data or not isinstance(overview_data, list) or len(overview_data) == 0:
            self._logged_in = False
            raise LuminusAuthError("Luminus session invalid (received empty response).")

        return self._parse_response(dash_data, overview_data)

    def _parse_response(
        self, dash_data: Any, overview_data: Any
    ) -> dict[str, Any]:
        """Parse raw API responses into structured sensor attributes."""
        # Overview element
        overview_item: dict[str, Any] = {}
        if (
            isinstance(overview_data, list)
            and len(overview_data) > 0
            and isinstance(overview_data[0], list)
            and len(overview_data[0]) > 0
            and isinstance(overview_data[0][0], dict)
        ):
            overview_item = overview_data[0][0]

        # Dashboard elements: [occupancy_list, current_dataset, total_usage]
        past_consumption_kwh = 0.0
        past_consumption_raw = ""
        past_consumption_unit = "kWh"
        if isinstance(dash_data, list) and len(dash_data) >= 3 and isinstance(dash_data[2], dict):
            usage_obj = dash_data[2]
            past_consumption_raw = str(usage_obj.get("number", "0"))
            past_consumption_unit = str(usage_obj.get("unit", "kWh"))
            past_consumption_kwh = self._parse_kwh(past_consumption_raw, past_consumption_unit)

        # Overview properties
        channel = overview_item.get("CHANNEL", "1")
        connector = overview_item.get("CONNECTOR", "Type 2")
        mom_power_kw = self._to_float(overview_item.get("MOM_POWER_KW"), default=0.0)
        soc = self._to_float_or_none(overview_item.get("SOC"))
        session_energy_kwh = self._to_float(
            overview_item.get("TRANS_ENERGY_DELIVERED_KWH"), default=0.0
        )
        transaction_time = overview_item.get("TRANSACTION_TIME_H_M") or ""
        event_data = overview_item.get("EVENT_DATA") or ""
        card_id = overview_item.get("CARDID") or ""
        customer_name = overview_item.get("CUSTOMER_NAME") or ""
        is_self = bool(overview_item.get("IS_SELF", False))
        status_code = str(overview_item.get("STATUS", "0"))
        notification = str(overview_item.get("NOTIFICATION", "")).strip()
        icon = overview_item.get("ICON") or "fa fa-car"

        status_text = STATUS_MAP.get(status_code, notification or "Unknown")

        # Computed fields
        is_charging = status_code == "2" or (mom_power_kw is not None and mom_power_kw > 0.05)
        is_plugged = status_code in ("1", "2", "3") or bool(notification and "prêt" not in notification.lower() and status_code != "0")
        total_consumption_kwh = round(past_consumption_kwh + session_energy_kwh, 2)

        return {
            "spot_id": self._spot_id,
            "channel": channel,
            "connector": connector,
            "mom_power_kw": mom_power_kw,
            "soc": soc,
            "session_energy_kwh": session_energy_kwh,
            "transaction_time": transaction_time,
            "event_data": event_data,
            "card_id": card_id,
            "customer_name": customer_name,
            "is_self": is_self,
            "status_code": status_code,
            "status_text": status_text,
            "notification": notification,
            "icon": icon,
            "is_charging": is_charging,
            "is_plugged": is_plugged,
            "past_consumption_kwh": past_consumption_kwh,
            "past_consumption_unit": past_consumption_unit,
            "total_consumption_kwh": total_consumption_kwh,
        }

    @staticmethod
    def _parse_kwh(number_str: str, unit: str) -> float:
        """Parse number string (e.g. '6,054') and unit ('MWh' / 'kWh') into kWh."""
        cleaned = number_str.strip().replace(" ", "").replace(",", ".")
        try:
            val = float(cleaned)
        except ValueError:
            return 0.0

        if unit.upper() == "MWH":
            return round(val * 1000.0, 2)
        return round(val, 2)

    @staticmethod
    def _to_float(val: Any, default: float = 0.0) -> float:
        """Safely convert value to float."""
        if val is None or val == "":
            return default
        try:
            return float(str(val).replace(",", "."))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _to_float_or_none(val: Any) -> float | None:
        """Safely convert value to float or return None."""
        if val is None or val == "":
            return None
        try:
            return float(str(val).replace(",", "."))
        except (ValueError, TypeError):
            return None
