# Luminus EVC - Home Assistant Integration & Lovelace Card

Custom Home Assistant integration and modern Lovelace dashboard card for Luminus Electric Vehicle (EV) chargers / wallboxes.

![Luminus EVC](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue.svg)
![HACS](https://img.shields.io/badge/HACS-Ready-green.svg)

---

## ⚡ Features

- **Direct Cloud Integration**: Connects to `luminus.evc-net.com` without needing an intermediate Windows service or C# app.
- **UI Configuration Flow**: Configure your username, password, and wallbox Spot ID directly from the Home Assistant UI (**Settings → Devices & Services → Add Integration**).
- **Comprehensive Sensors**:
  - ⚡ **Instant Power** (`sensor.luminus_wallbox_<id>_instant_power`) in kW
  - 🔋 **Session Energy** (`sensor.luminus_wallbox_<id>_session_energy`) in kWh
  - 📈 **Total Consumption** (`sensor.luminus_wallbox_<id>_total_consumption`) in kWh
  - 🚗 **Battery State of Charge (SOC)** (`sensor.luminus_wallbox_<id>_battery_state_of_charge`) in %
  - ⏱️ **Session Duration** (`sensor.luminus_wallbox_<id>_session_duration`)
  - 🏷️ **Status & Notification** (`sensor.luminus_wallbox_<id>_status`, `notification`)
  - 🪪 **RFID Card & User Name**
  - 🔌 **Connector Type** (e.g. Type 2 IEC-62196)
  - 🟢 **Binary Sensors**: Charging active (`binary_sensor.luminus_wallbox_<id>_charging`) & Vehicle connected (`binary_sensor.luminus_wallbox_<id>_vehicle_connected`)
- **Modern Lovelace Card (`luminus-evc-card.js`)**:
  - Live animated power gauge and energy flow beam.
  - Dark glassmorphism aesthetics with glowing status indicators.
  - Card picker integration in Home Assistant dashboard editor.

---

## 🚀 Installation

### Option 1: Direct Copy into Home Assistant (Fastest)

1. Copy the folder `custom_components/luminus_evc` into your Home Assistant's `/config/custom_components/` directory:
   ```text
   config/
   └── custom_components/
       └── luminus_evc/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           ├── coordinator.py
           ├── luminus_api.py
           ├── sensor.py
           ├── binary_sensor.py
           ├── const.py
           └── translations/
   ```
2. Restart Home Assistant.
3. In Home Assistant, go to **Settings → Devices & Services → Add Integration**.
4. Search for **Luminus EVC** and enter your credentials.

---

### Option 2: Add via HACS

1. Push this repository to GitHub.
2. In Home Assistant, open **HACS → Integrations → Custom repositories** (three dots top right).
3. Paste your GitHub repository URL and select category **Integration**.
4. Click **Download**, then restart Home Assistant.

---

## 🎨 Dashboard Card Installation

1. Copy `frontend/luminus-evc-card.js` into your Home Assistant's `/config/www/` folder.
2. In Home Assistant, go to **Settings → Dashboards → Resources** (three dots top right) and add:
   - **URL**: `/local/luminus-evc-card.js`
   - **Resource type**: `JavaScript Module`
3. Edit your dashboard, click **Add Card**, and choose **Custom: Luminus EVC Card** (or add manual YAML):
   ```yaml
   type: custom:luminus-evc-card
   title: "Ma Borne Luminus"
   spot_id: "1234606393"
   ```

---

## 🧪 Local Testing Studio

You can preview and test the card locally by opening `frontend/index.html` in any browser or running:
```bash
python -m http.server 8085 --directory frontend
```
Navigate to `http://localhost:8085` to test live presets (Idle, Plugged, Charging 3.7 kW, Fast 11 kW) and adjust all sliders.
