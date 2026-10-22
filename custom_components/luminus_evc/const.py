"""Constants for the Luminus EVC integration."""

DOMAIN = "luminus_evc"

# Configuration keys
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SPOT_ID = "spot_id"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL = 30  # seconds
MIN_SCAN_INTERVAL = 10  # seconds

# API URLs
BASE_URL = "https://luminus.evc-net.com"
LOGIN_URL = f"{BASE_URL}/Login/Login"
AJAX_URL = f"{BASE_URL}/api/ajax"

# Status code mappings
STATUS_MAP = {
    "0": "Available",
    "1": "Connected",
    "2": "Charging",
    "3": "Finishing",
    "4": "Reserved",
    "9": "Error",
}
