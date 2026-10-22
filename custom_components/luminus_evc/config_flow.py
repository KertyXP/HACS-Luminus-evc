"""Config flow for Luminus EVC integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_SPOT_ID,
    CONF_USERNAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)
from .luminus_api import LuminusApiClient, LuminusAuthError, LuminusConnectionError

_LOGGER = logging.getLogger(__name__)


class LuminusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Luminus EVC."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD].strip()
            spot_id = str(user_input[CONF_SPOT_ID]).strip()
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

            # Prevent duplicate integration entries for the same wallbox spot ID
            await self.async_set_unique_id(f"luminus_evc_{spot_id}")
            self._abort_if_unique_id_configured()

            # Test credentials and spot ID
            session = async_get_clientsession(self.hass)
            client = LuminusApiClient(
                username=username,
                password=password,
                spot_id=spot_id,
                session=session,
            )

            try:
                await client.async_login()
                await client.async_fetch_data()
            except LuminusAuthError:
                errors["base"] = "invalid_auth"
            except LuminusConnectionError:
                errors["base"] = "cannot_connect"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during Luminus config flow: %s", ex)
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Luminus Wallbox ({spot_id})",
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_SPOT_ID: spot_id,
                        CONF_SCAN_INTERVAL: scan_interval,
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SPOT_ID, default="1234606393"): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=300)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow handler for this entry."""
        return LuminusOptionsFlowHandler(config_entry)


class LuminusOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Luminus EVC."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=300)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
