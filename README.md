# Luminus EVC - Home Assistant Integration & Lovelace Card

Custom Home Assistant integration and modern Lovelace dashboard card for Luminus Electric Vehicle (EV) chargers / wallboxes.

![Luminus EVC](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-blue.svg)
![HACS](https://img.shields.io/badge/HACS-Ready-green.svg)
![Version](https://img.shields.io/badge/Version-1.1.0-blue.svg)

---

## ⚡ Features & Categorized Entities

- **Direct Cloud Integration**: Connects directly to `luminus.evc-net.com` without needing an intermediate Windows service or C# app.
- **UI Configuration Flow**: Setup with username, password, and wallbox Spot ID directly from the UI (**Settings → Devices & Services → Add Integration**).
- **Home Assistant Energy Dashboard Compatible**: Total consumption sensor (`SensorDeviceClass.ENERGY`, `TOTAL_INCREASING`) can be selected under **Settings → Dashboards → Energy → Individual Devices**.
- **24-Hour Charging Curve**: 15-minute interval kW history attached to `mom_power_kw` attributes (`history_labels`, `history_kw`).

### 📊 Primary Dashboard Entities
| Entity | Type | Unit | Description |
|---|---|---|---|
| `instant_power` | Sensor | `kW` | Current charging power (with 24h curve attributes) |
| `charging_current` | Sensor | `A` | Estimated charging current (Amps at 230V reference) |
| `session_energy` | Sensor | `kWh` | Energy delivered in current charging session |
| `total_consumption` | Sensor | `kWh` | Lifetime consumption (Energy Dashboard ready) |
| `battery_state_of_charge` | Sensor | `%` | Vehicle battery SOC (if reported by car/station) |
| `status` | Sensor | - | Formatted status ("Prêt", "En charge", "Branché") |
| `notification` | Sensor | - | Live station notification string |
| `charging` | Binary Sensor | - | Charging actively in progress |
| `vehicle_connected` | Binary Sensor | - | Vehicle plugged into wallbox |

### 🛠️ Diagnostic Category Entities (`EntityCategory.DIAGNOSTIC`)
| Entity | Type | Description |
|---|---|---|
| `past_consumption` | Sensor (`kWh`) | Total past consumption from historical records |
| `session_duration` | Sensor | Active transaction time (`01:23`) |
| `rfid_card` | Sensor | Badge RFID card ID |
| `user_name` | Sensor | Name of authorized user |
| `connector` | Sensor | Connector type (e.g. Type 2 IEC-62196) |
| `channel` | Sensor | Channel number (`1`) |
| `status_code` | Sensor | Raw numeric status code (`0`, `1`, `2`, `101`) |
| `availability_rate` | Sensor (`%`) | Wallbox availability / occupancy rate |
| `cloud_api_connected` | Binary Sensor | Luminus cloud API connectivity status |

### 🎛️ Control Buttons (`EntityCategory.CONFIG`)
| Entity | Description |
|---|---|
| `force_refresh` | Trigger an immediate cloud poll and sensor update |
| `restart_wallbox` | Soft reboot command sent to the wallbox via cloud API |

---

## 🎨 Bundled Lovelace Dashboard Card (`luminus-evc-card.js`)

The modern animated Lovelace card is **automatically bundled** with the integration!
- Live animated power gauge and energy flow beam.
- Dark glassmorphism aesthetics with pulsing status badge.
- Vehicle battery progress bar (SOC).
- Visual card picker integration in the Home Assistant dashboard editor.

---

## 🚀 Installation via HACS (Recommended)

1. In Home Assistant, open **HACS**.
2. Click the **three dots `⋮`** in the top-right corner $\rightarrow$ **Custom repositories**.
3. Add your repository URL:
   - **Repository**: `https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>`
   - **Category**: **Integration**
4. Click **Add**, find **Luminus EVC**, and click **Download** (`v1.1.0`).
5. **Restart Home Assistant**.
6. Go to **Settings → Devices & Services → Add Integration**, search for **Luminus EVC**, and enter your credentials.
7. Add the card to your dashboard:
   ```yaml
   type: custom:luminus-evc-card
   title: "Ma Borne Luminus"
   spot_id: "1234606393"
   ```
