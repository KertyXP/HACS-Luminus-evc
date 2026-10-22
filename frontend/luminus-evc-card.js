/**
 * Luminus EVC Wallbox Lovelace Card
 * Custom card for Home Assistant & HACS
 */

class LuminusEvcCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = null;
  }

  setConfig(config) {
    if (!config) {
      throw new Error("Invalid configuration");
    }
    this._config = {
      title: config.title || "Luminus Wallbox",
      spot_id: config.spot_id || "",
      power_entity: config.power_entity || "",
      energy_entity: config.energy_entity || "",
      total_entity: config.total_entity || "",
      soc_entity: config.soc_entity || "",
      status_entity: config.status_entity || "",
      duration_entity: config.duration_entity || "",
      plugged_entity: config.plugged_entity || "",
      charging_entity: config.charging_entity || "",
      card_id_entity: config.card_id_entity || "",
      connector_entity: config.connector_entity || "",
      ...config,
    };
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.updateCard();
  }

  getCardSize() {
    return 4;
  }

  static getStubConfig(hass, entities) {
    const findEntity = (prefix, suffix) => {
      if (!entities) return "";
      const match = entities.find(e => e.includes(prefix) && e.includes(suffix));
      return match || "";
    };

    return {
      title: "Luminus Wallbox",
      power_entity: findEntity("luminus", "instant_power") || findEntity("luminus", "mom_power"),
      energy_entity: findEntity("luminus", "session_energy"),
      total_entity: findEntity("luminus", "total_consumption"),
      soc_entity: findEntity("luminus", "battery_state_of_charge") || findEntity("luminus", "soc"),
      status_entity: findEntity("luminus", "status"),
      duration_entity: findEntity("luminus", "session_duration"),
      charging_entity: findEntity("luminus", "charging"),
      plugged_entity: findEntity("luminus", "vehicle_connected"),
    };
  }

  // Auto-discover entities if not explicitly mapped
  _resolveEntities() {
    if (!this._hass) return {};
    const states = this._hass.states;
    const cfg = this._config;

    const findState = (explicitKey, fallbackSubstrings) => {
      if (explicitKey && states[explicitKey]) {
        return states[explicitKey];
      }
      for (const entityId of Object.keys(states)) {
        if (entityId.includes("luminus")) {
          const match = fallbackSubstrings.some(sub => entityId.includes(sub));
          if (match) return states[entityId];
        }
      }
      return null;
    };

    return {
      power: findState(cfg.power_entity, ["instant_power", "mom_power"]),
      energy: findState(cfg.energy_entity, ["session_energy"]),
      total: findState(cfg.total_entity, ["total_consumption"]),
      soc: findState(cfg.soc_entity, ["battery_state_of_charge", "soc"]),
      status: findState(cfg.status_entity, ["status", "notification"]),
      duration: findState(cfg.duration_entity, ["session_duration", "transaction_time"]),
      charging: findState(cfg.charging_entity, ["binary_sensor.luminus_wallbox_charging", "charging"]),
      plugged: findState(cfg.plugged_entity, ["binary_sensor.luminus_wallbox_vehicle_connected", "vehicle_connected"]),
      cardId: findState(cfg.card_id_entity, ["rfid_card", "card_id"]),
      connector: findState(cfg.connector_entity, ["connector"]),
    };
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          --luminus-bg: var(--ha-card-background, var(--card-background-color, #131722));
          --luminus-card-radius: var(--ha-card-border-radius, 16px);
          --luminus-primary: #10b981;
          --luminus-accent: #06b6d4;
          --luminus-glow: rgba(16, 185, 129, 0.25);
          --luminus-text: var(--primary-text-color, #f8fafc);
          --luminus-subtext: var(--secondary-text-color, #94a3b8);
          --luminus-surface: rgba(255, 255, 255, 0.04);
          --luminus-border: rgba(255, 255, 255, 0.08);
          font-family: var(--paper-font-body1_-_font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif);
          display: block;
        }

        .container {
          background: linear-gradient(135deg, rgba(19, 23, 34, 0.95), rgba(15, 20, 28, 0.98));
          border-radius: var(--luminus-card-radius);
          border: 1px solid var(--luminus-border);
          box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
          padding: 20px;
          color: var(--luminus-text);
          position: relative;
          overflow: hidden;
          box-sizing: border-box;
        }

        /* Ambient background glow */
        .ambient-glow {
          position: absolute;
          width: 250px;
          height: 250px;
          background: radial-gradient(circle, var(--ambient-color, rgba(16, 185, 129, 0.15)) 0%, transparent 70%);
          top: -80px;
          right: -80px;
          pointer-events: none;
          transition: background 0.8s ease;
          border-radius: 50%;
        }

        /* Header */
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .brand-info {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .brand-icon {
          width: 36px;
          height: 36px;
          background: linear-gradient(135deg, #10b981, #06b6d4);
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        .brand-icon svg {
          width: 20px;
          height: 20px;
          fill: #ffffff;
        }

        .title-group h2 {
          margin: 0;
          font-size: 1.05rem;
          font-weight: 600;
          letter-spacing: -0.01em;
          color: var(--luminus-text);
        }

        .title-group p {
          margin: 2px 0 0;
          font-size: 0.75rem;
          color: var(--luminus-subtext);
        }

        /* Status Badge */
        .status-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 0.78rem;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          background: var(--status-bg, rgba(16, 185, 129, 0.12));
          color: var(--status-color, #10b981);
          border: 1px solid var(--status-border, rgba(16, 185, 129, 0.3));
          transition: all 0.3s ease;
        }

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--status-color, #10b981);
          box-shadow: 0 0 8px var(--status-color, #10b981);
        }

        .pulsing {
          animation: pulse-dot 1.8s infinite;
        }

        @keyframes pulse-dot {
          0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
          70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
          100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Main Hero: Power display */
        .hero {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 16px 0;
          position: relative;
        }

        .power-gauge-wrap {
          position: relative;
          width: 170px;
          height: 170px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .power-svg {
          position: absolute;
          width: 100%;
          height: 100%;
          transform: rotate(-90deg);
        }

        .power-circle-bg {
          fill: none;
          stroke: rgba(255, 255, 255, 0.06);
          stroke-width: 10;
        }

        .power-circle-val {
          fill: none;
          stroke: url(#powerGradient);
          stroke-width: 10;
          stroke-linecap: round;
          stroke-dasharray: 440;
          stroke-dashoffset: 440;
          transition: stroke-dashoffset 1s ease-out;
        }

        .power-center {
          text-align: center;
          z-index: 2;
        }

        .power-number {
          font-size: 2.2rem;
          font-weight: 700;
          letter-spacing: -0.03em;
          color: var(--luminus-text);
          line-height: 1;
        }

        .power-unit {
          font-size: 0.85rem;
          font-weight: 500;
          color: var(--luminus-subtext);
          margin-top: 4px;
        }

        /* Flow animation beam */
        .flow-track {
          width: 100%;
          height: 4px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 2px;
          margin: 14px 0 6px;
          position: relative;
          overflow: hidden;
        }

        .flow-pulse {
          position: absolute;
          height: 100%;
          width: 25%;
          background: linear-gradient(90deg, transparent, #10b981, transparent);
          border-radius: 2px;
          opacity: 0;
        }

        .charging-flow .flow-pulse {
          opacity: 1;
          animation: flow-anim 1.5s linear infinite;
        }

        @keyframes flow-anim {
          0% { left: -30%; }
          100% { left: 110%; }
        }

        /* Metrics Grid */
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
          margin-top: 10px;
        }

        .metric-card {
          background: var(--luminus-surface);
          border: 1px solid var(--luminus-border);
          border-radius: 12px;
          padding: 12px 14px;
          display: flex;
          flex-direction: column;
          gap: 4px;
          transition: transform 0.2s ease, background 0.2s ease;
        }

        .metric-card:hover {
          background: rgba(255, 255, 255, 0.07);
          transform: translateY(-2px);
        }

        .metric-header {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.72rem;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          color: var(--luminus-subtext);
        }

        .metric-header svg {
          width: 14px;
          height: 14px;
          fill: currentColor;
          opacity: 0.8;
        }

        .metric-value-row {
          display: flex;
          align-items: baseline;
          gap: 4px;
        }

        .metric-val {
          font-size: 1.25rem;
          font-weight: 600;
          letter-spacing: -0.02em;
          color: var(--luminus-text);
        }

        .metric-unit {
          font-size: 0.75rem;
          color: var(--luminus-subtext);
        }

        /* Battery SOC Bar (if car reports battery %) */
        .soc-section {
          background: var(--luminus-surface);
          border: 1px solid var(--luminus-border);
          border-radius: 12px;
          padding: 12px 14px;
          margin-top: 12px;
        }

        .soc-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 0.75rem;
          color: var(--luminus-subtext);
          margin-bottom: 6px;
        }

        .soc-progress-bg {
          width: 100%;
          height: 8px;
          background: rgba(255, 255, 255, 0.06);
          border-radius: 4px;
          overflow: hidden;
        }

        .soc-progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #10b981, #06b6d4);
          border-radius: 4px;
          transition: width 0.6s ease;
        }

        /* Footer Info */
        .footer-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 14px;
          padding-top: 12px;
          border-top: 1px solid rgba(255, 255, 255, 0.05);
          font-size: 0.72rem;
          color: var(--luminus-subtext);
        }

        .footer-item {
          display: flex;
          align-items: center;
          gap: 5px;
        }

        .footer-item svg {
          width: 13px;
          height: 13px;
          fill: currentColor;
        }
      </style>

      <div class="container">
        <div class="ambient-glow" id="ambientGlow"></div>

        <!-- Header -->
        <div class="header">
          <div class="brand-info">
            <div class="brand-icon">
              <svg viewBox="0 0 24 24">
                <path d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3zm-1 14h2v2h-2v-2zm0-8h2v6h-2V8z"/>
              </svg>
            </div>
            <div class="title-group">
              <h2 id="cardTitle">${this._config.title || "Luminus Wallbox"}</h2>
              <p id="cardSub">${this._config.spot_id ? "Spot #" + this._config.spot_id : "EV Smart Charger"}</p>
            </div>
          </div>
          <div class="status-badge" id="statusBadge">
            <span class="status-dot" id="statusDot"></span>
            <span id="statusText">Prêt</span>
          </div>
        </div>

        <!-- Main Hero: Circular Power Gauge -->
        <div class="hero">
          <div class="power-gauge-wrap">
            <svg class="power-svg" viewBox="0 0 160 160">
              <defs>
                <linearGradient id="powerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#10b981" />
                  <stop offset="100%" stop-color="#06b6d4" />
                </linearGradient>
              </defs>
              <circle class="power-circle-bg" cx="80" cy="80" r="70"></circle>
              <circle class="power-circle-val" id="powerCircle" cx="80" cy="80" r="70"></circle>
            </svg>
            <div class="power-center">
              <div class="power-number" id="powerVal">0.0</div>
              <div class="power-unit">kW Instantané</div>
            </div>
          </div>
        </div>

        <!-- Flow beam animation -->
        <div class="flow-track" id="flowTrack">
          <div class="flow-pulse"></div>
        </div>

        <!-- Metrics Grid -->
        <div class="metrics-grid">
          <!-- Session Energy -->
          <div class="metric-card">
            <div class="metric-header">
              <svg viewBox="0 0 24 24"><path d="M13 2L3 14h8l-2 8 10-12h-8l2-8z"/></svg>
              <span>Session</span>
            </div>
            <div class="metric-value-row">
              <span class="metric-val" id="sessionEnergyVal">0.00</span>
              <span class="metric-unit">kWh</span>
            </div>
          </div>

          <!-- Total Historical Consumption -->
          <div class="metric-card">
            <div class="metric-header">
              <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/></svg>
              <span>Total Recharges</span>
            </div>
            <div class="metric-value-row">
              <span class="metric-val" id="totalEnergyVal">0.0</span>
              <span class="metric-unit">kWh</span>
            </div>
          </div>

          <!-- Charging Duration -->
          <div class="metric-card">
            <div class="metric-header">
              <svg viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
              <span>Durée</span>
            </div>
            <div class="metric-value-row">
              <span class="metric-val" id="durationVal">00:00</span>
            </div>
          </div>

          <!-- RFID Card / User -->
          <div class="metric-card">
            <div class="metric-header">
              <svg viewBox="0 0 24 24"><path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/></svg>
              <span>Badge / Utilisateur</span>
            </div>
            <div class="metric-value-row">
              <span class="metric-val" id="userVal" style="font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">Prêt</span>
            </div>
          </div>
        </div>

        <!-- Optional SOC Section -->
        <div class="soc-section" id="socSection" style="display: none;">
          <div class="soc-header">
            <span>Batterie Véhicule (SOC)</span>
            <strong id="socText">0%</strong>
          </div>
          <div class="soc-progress-bg">
            <div class="soc-progress-fill" id="socFill" style="width: 0%;"></div>
          </div>
        </div>

        <!-- Footer Info -->
        <div class="footer-info">
          <div class="footer-item" id="connectorFooter">
            <svg viewBox="0 0 24 24"><path d="M16 7V3h-2v4h-4V3H8v4c-1.66 0-3 1.34-3 3v5.5c0 1.93 1.57 3.5 3.5 3.5h.5v4h6v-4h.5c1.93 0 3.5-1.57 3.5-3.5V10c0-1.66-1.34-3-3-3z"/></svg>
            <span id="connectorVal">Type 2 (IEC-62196)</span>
          </div>
          <div class="footer-item">
            <span id="protocolVal">Luminus Cloud EVC</span>
          </div>
        </div>
      </div>
    `;
  }

  updateCard() {
    if (!this.shadowRoot || !this._hass) return;

    const entities = this._resolveEntities();
    const root = this.shadowRoot;

    // 1. Power
    const powerRaw = entities.power ? parseFloat(entities.power.state) : 0.0;
    const power = isNaN(powerRaw) ? 0.0 : powerRaw;
    const powerValEl = root.getElementById('powerVal');
    if (powerValEl) {
      powerValEl.textContent = power.toFixed(1);
    }

    // Gauge circle calculation (assume 11kW or 22kW max for gauge fullness)
    const maxKw = 11.0;
    const circle = root.getElementById('powerCircle');
    if (circle) {
      const circumference = 2 * Math.PI * 70; // ~439.8
      const ratio = Math.min(Math.max(power / maxKw, 0), 1);
      const offset = circumference * (1 - ratio);
      circle.style.strokeDashoffset = offset;
    }

    // 2. Session Energy
    const energyRaw = entities.energy ? parseFloat(entities.energy.state) : 0.0;
    const energyEl = root.getElementById('sessionEnergyVal');
    if (energyEl) {
      energyEl.textContent = isNaN(energyRaw) ? "0.00" : energyRaw.toFixed(2);
    }

    // 3. Total Consumption
    const totalRaw = entities.total ? parseFloat(entities.total.state) : 0.0;
    const totalEl = root.getElementById('totalEnergyVal');
    if (totalEl) {
      totalEl.textContent = isNaN(totalRaw) ? "0.0" : totalRaw.toFixed(1);
    }

    // 4. Duration
    const duration = entities.duration ? entities.duration.state : "00:00";
    const durEl = root.getElementById('durationVal');
    if (durEl) {
      durEl.textContent = duration && duration !== "unknown" ? duration : "00:00";
    }

    // 5. User / Card
    const cardId = entities.cardId ? entities.cardId.state : "";
    const userEl = root.getElementById('userVal');
    if (userEl) {
      userEl.textContent = cardId && cardId !== "unknown" && cardId !== "None" ? cardId : "Prêt";
    }

    // 6. Connector
    const conn = entities.connector ? entities.connector.state : "";
    const connEl = root.getElementById('connectorVal');
    if (connEl && conn && conn !== "unknown") {
      connEl.textContent = conn;
    }

    // 7. Status & Charging state
    const isCharging = (entities.charging && entities.charging.state === "on") || power > 0.05;
    const isPlugged = (entities.plugged && entities.plugged.state === "on") || isCharging;
    const rawStatus = entities.status ? entities.status.state : "";

    const statusBadge = root.getElementById('statusBadge');
    const statusDot = root.getElementById('statusDot');
    const statusText = root.getElementById('statusText');
    const flowTrack = root.getElementById('flowTrack');
    const ambientGlow = root.getElementById('ambientGlow');

    if (isCharging) {
      if (statusText) statusText.textContent = rawStatus && rawStatus !== "unknown" ? rawStatus : "En charge";
      if (statusBadge) {
        statusBadge.style.setProperty('--status-bg', 'rgba(16, 185, 129, 0.16)');
        statusBadge.style.setProperty('--status-color', '#10b981');
        statusBadge.style.setProperty('--status-border', 'rgba(16, 185, 129, 0.4)');
      }
      if (statusDot) statusDot.classList.add('pulsing');
      if (flowTrack) flowTrack.classList.add('charging-flow');
      if (ambientGlow) ambientGlow.style.setProperty('--ambient-color', 'rgba(16, 185, 129, 0.22)');
    } else if (isPlugged) {
      if (statusText) statusText.textContent = rawStatus && rawStatus !== "unknown" ? rawStatus : "Branché";
      if (statusBadge) {
        statusBadge.style.setProperty('--status-bg', 'rgba(59, 130, 246, 0.16)');
        statusBadge.style.setProperty('--status-color', '#3b82f6');
        statusBadge.style.setProperty('--status-border', 'rgba(59, 130, 246, 0.4)');
      }
      if (statusDot) statusDot.classList.remove('pulsing');
      if (flowTrack) flowTrack.classList.remove('charging-flow');
      if (ambientGlow) ambientGlow.style.setProperty('--ambient-color', 'rgba(59, 130, 246, 0.18)');
    } else {
      if (statusText) statusText.textContent = rawStatus && rawStatus !== "unknown" ? rawStatus : "Disponible";
      if (statusBadge) {
        statusBadge.style.setProperty('--status-bg', 'rgba(148, 163, 184, 0.12)');
        statusBadge.style.setProperty('--status-color', '#94a3b8');
        statusBadge.style.setProperty('--status-border', 'rgba(148, 163, 184, 0.25)');
      }
      if (statusDot) statusDot.classList.remove('pulsing');
      if (flowTrack) flowTrack.classList.remove('charging-flow');
      if (ambientGlow) ambientGlow.style.setProperty('--ambient-color', 'rgba(148, 163, 184, 0.08)');
    }

    // 8. SOC Section
    const socRaw = entities.soc ? parseFloat(entities.soc.state) : null;
    const socSection = root.getElementById('socSection');
    if (socSection) {
      if (socRaw !== null && !isNaN(socRaw) && socRaw > 0) {
        socSection.style.display = 'block';
        const socText = root.getElementById('socText');
        const socFill = root.getElementById('socFill');
        if (socText) socText.textContent = `${Math.round(socRaw)}%`;
        if (socFill) socFill.style.width = `${Math.min(Math.max(socRaw, 0), 100)}%`;
      } else {
        socSection.style.display = 'none';
      }
    }
  }
}

customElements.define('luminus-evc-card', LuminusEvcCard);

// Register custom card in Home Assistant's card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'luminus-evc-card',
  name: 'Luminus EVC Card',
  description: 'Modern animated dashboard card for Luminus EV Wallbox',
  preview: true,
  documentationURL: 'https://github.com/custom-components/luminus_evc',
});
