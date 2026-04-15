/* ═══════════════════════════════════════════════════════════════
   Financial Astrology Engine v2.0 — Dashboard JavaScript
   ══════════════════════════════════════════════════════════════ */

// ── Helpers ──────────────────────────────────────────────────────

function getApiBase(inputId) {
  const val = document.getElementById(inputId)?.value?.trim().replace(/\/$/, '');
  return val || (window.location.protocol === 'file:' ? 'http://127.0.0.1:8010' : window.location.origin);
}

function setStatus(id, type, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = 'status-bar ' + type;
  el.textContent = msg;
}

function showLoading(msg = 'Calculating planetary positions...') {
  document.getElementById('loadingOverlay').style.display = 'flex';
  document.getElementById('loadingText').textContent = msg;
}

function hideLoading() {
  document.getElementById('loadingOverlay').style.display = 'none';
}

async function apiPost(base, endpoint, body) {
  const res = await fetch(`${base}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
  return data;
}

function scoreColor(score) {
  if (score >= 0.6) return '#00c851';
  if (score >= 0.3) return '#4caf50';
  if (score >= 0)   return '#8bc34a';
  if (score >= -0.3) return '#ff9800';
  if (score >= -0.6) return '#ff5722';
  return '#ff3d00';
}

function scoreBar(label, value, max = 1.0) {
  const pct = Math.min(100, Math.max(0, ((value + 1) / 2) * 100));
  const color = scoreColor(value);
  return `<div class="score-bar-row">
    <span class="score-bar-label">${label}</span>
    <div class="score-bar-track">
      <div class="score-bar-fill" style="width:${pct}%;background:${color}"></div>
    </div>
    <span class="score-bar-val" style="color:${color}">${value > 0 ? '+' : ''}${value.toFixed(3)}</span>
  </div>`;
}

function signalPill(signal, color) {
  const bg = color || scoreColor(0);
  return `<span class="signal-pill" style="background:${bg}22;color:${bg};border:1px solid ${bg}55">${signal}</span>`;
}

function formatDate(dateStr) {
  if (!dateStr || dateStr === 'CURRENT') return dateStr;
  try {
    return new Date(dateStr).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  } catch { return dateStr; }
}

// ── Tab Navigation ───────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-section').forEach(s => s.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

// ── Global Birth Details ──────────────────────────────────────────

function saveGlobalDetails() {
  const data = {
    name: document.getElementById('global_name').value,
    date: document.getElementById('global_date').value,
    time: document.getElementById('global_time').value,
    place: document.getElementById('global_place').value,
    ayanamsa: document.getElementById('global_ayanamsa').value,
  };
  localStorage.setItem('globalBirthDetails', JSON.stringify(data));
}

function loadGlobalDetails() {
  const data = JSON.parse(localStorage.getItem('globalBirthDetails') || '{}');
  return data;
}

function populateFormsFromGlobal() {
  const data = loadGlobalDetails();
  const fields = ['name', 'date', 'time', 'place', 'ayanamsa'];
  const prefixes = ['global', 'c', 'd', 'dv', 'av', 'y', 'al', 'p_natal', 'sbc'];

  fields.forEach(field => {
    prefixes.forEach(prefix => {
      const id = prefix === 'p_natal' ? `p_natal_${field}` : `${prefix}_${field}`;
      const el = document.getElementById(id);
      if (el && !el.value && data[field]) {
        el.value = data[field];
      }
    });
  });
}

function showResultPanel(panelId) {
  const panel = document.getElementById(panelId);
  if (panel) panel.style.display = 'block';
}

function clearResultPanel(panelId) {
  const panel = document.getElementById(panelId);
  if (panel) panel.style.display = 'none';
}

function clearGlobalDetails() {
  localStorage.removeItem('globalBirthDetails');
  const fields = ['global_name', 'global_date', 'global_time', 'global_place'];
  fields.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  populateFormsFromGlobal(); // Reset others if needed
}

function initInputCardToggles() {
  document.querySelectorAll('.input-card').forEach(card => {
    const titleElement = card.querySelector('.card-title');
    if (!titleElement) return;

    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'toggle-panel';
    toggle.textContent = 'Hide input panel';

    const bodyElements = [
      card.querySelector('.card-desc'),
      card.querySelector('form')
    ].filter(Boolean);

    toggle.addEventListener('click', () => {
      const collapsed = card.classList.toggle('collapsed');
      toggle.textContent = collapsed ? 'Show input panel' : 'Hide input panel';
      bodyElements.forEach(el => {
        el.style.display = collapsed ? 'none' : '';
      });
    });

    titleElement.insertAdjacentElement('afterend', toggle);
  });
}

// Set today's date in all date inputs
document.addEventListener('DOMContentLoaded', () => {
  const today = new Date().toISOString().split('T')[0];
  ['p_transit_date', 'al_date'].forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.value) el.value = today;
  });

  // Load and populate global details
  const data = loadGlobalDetails();
  Object.keys(data).forEach(key => {
    const el = document.getElementById(`global_${key}`);
    if (el) el.value = data[key] || '';
  });
  populateFormsFromGlobal();
  initInputCardToggles();
});

// Global form handlers
document.getElementById('globalForm').addEventListener('submit', (e) => {
  e.preventDefault();
  saveGlobalDetails();
  populateFormsFromGlobal();
  alert('Birth details saved and applied to all forms!');
});

document.getElementById('clearGlobal').addEventListener('click', () => {
  clearGlobalDetails();
  alert('Global birth details cleared.');
});

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.close-results');
  if (!btn) return;
  const target = btn.dataset.target;
  if (target) clearResultPanel(target);
});

// ── Clock ────────────────────────────────────────────────────────
// 1. AUTO PREDICTION
// ═══════════════════════════════════════════════════════════════════

document.getElementById('predictForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('predictBtn');
  btn.disabled = true;
  showLoading('Running autonomous astrology prediction engine...');

  const global = loadGlobalDetails();
  const body = {
    transit_date:  document.getElementById('p_transit_date').value,
    transit_time:  document.getElementById('p_transit_time').value,
    transit_place: document.getElementById('p_transit_place').value,
    ayanamsa:      document.getElementById('p_ayanamsa').value || global.ayanamsa,
    days_ahead:    parseInt(document.getElementById('p_days_ahead').value),
  };

  const natalDate  = document.getElementById('p_natal_date').value || global.date;
  const natalTime  = document.getElementById('p_natal_time').value || global.time;
  const natalPlace = document.getElementById('p_natal_place').value || global.place;
  const natalName  = document.getElementById('p_natal_name').value || global.name;

  if (natalDate && natalTime && natalPlace) {
    body.natal_date  = natalDate;
    body.natal_time  = natalTime;
    body.natal_place = natalPlace;
    body.natal_name  = natalName || 'User';
  }

  try {
    const base = getApiBase('p_apiBase');
    const data = await apiPost(base, '/predict', body);
    renderPrediction(data);
    document.getElementById('predictResults').style.display = 'block';
  } catch (err) {
    alert('Error: ' + err.message);
  } finally {
    btn.disabled = false;
    hideLoading();
  }
});

function renderPrediction(data) {
  const pred = data.prediction;
  if (!pred) return;

  const signal = pred.prediction || {};
  const score = pred.overall_score || 0;
  const color = signal.color || scoreColor(score);

  // Main signal card
  document.getElementById('signalEmoji').textContent = signal.emoji || '🔮';
  document.getElementById('signalLabel').textContent = signal.signal || '';
  document.getElementById('signalLabel').style.color = color;
  document.getElementById('signalDirection').textContent = signal.direction || '';
  document.getElementById('scoreValue').textContent = (score > 0 ? '+' : '') + score.toFixed(3);
  document.getElementById('scoreValue').style.color = color;
  document.getElementById('signalStrategy').textContent = signal.strategy || '';
  document.getElementById('signalNiftyBias').textContent = '📊 ' + (signal.nifty_bias || '');
  document.getElementById('mainSignalCard').style.borderColor = color;

  const conf = pred.confidence || {};
  document.getElementById('confidenceBadge').textContent =
    `Confidence: ${conf.level || ''} (${conf.percent || 0}%) — ${conf.note || ''}`;

  // Score breakdown
  const bd = pred.score_breakdown || {};
  document.getElementById('scoreBreakdown').innerHTML =
    scoreBar('Planetary Positions', bd.planetary_position_score || 0) +
    scoreBar('Moon Nakshatra',      bd.moon_nakshatra_score || 0) +
    scoreBar('Dasha Period',        bd.dasha_score || 0) +
    scoreBar('Active Yogas',        bd.yoga_score || 0) +
    scoreBar('Transit Alerts',      bd.transit_score || 0) +
    scoreBar('FINAL SCORE',         bd.final_weighted_score || 0);

  // Weekly outlook
  const weekly = pred.weekly_outlook || [];
  document.getElementById('weeklyOutlook').innerHTML = weekly.map(d => `
    <div class="week-day-card" style="border-color:${d.signal_color}44">
      <div class="week-day-name">${d.day?.slice(0,3)}</div>
      <div class="week-day-date">${formatDate(d.date)?.slice(0,6)}</div>
      <div class="week-nak" style="color:${d.signal_color}">${d.nakshatra}</div>
      <div class="fs-11 text-muted">${d.nakshatra_lord}</div>
      <div class="week-signal" style="background:${d.signal_color}22;color:${d.signal_color}">
        ${d.nse_signal?.split(' ')[0] || 'NEUTRAL'}
      </div>
    </div>`).join('');

  // Sectors
  const sectors = pred.sector_recommendations || {};
  document.getElementById('sectorRecs').innerHTML = `
    <div class="sector-col">
      <h4 class="text-green">✅ Strong Buy</h4>
      ${(sectors.strong_buy || []).map(s => `<span class="sector-tag sector-buy">${s}</span>`).join('')}
    </div>
    <div class="sector-col">
      <h4 class="text-yellow">🔆 Hold</h4>
      ${(sectors.hold || []).map(s => `<span class="sector-tag sector-hold">${s}</span>`).join('')}
    </div>
    <div class="sector-col">
      <h4 class="text-red">❌ Avoid</h4>
      ${(sectors.avoid || []).map(s => `<span class="sector-tag sector-avoid">${s}</span>`).join('')}
    </div>`;

  // Key events
  const events = pred.key_events || [];
  document.getElementById('keyEvents').innerHTML = events.length
    ? events.slice(0, 6).map(ev => `
      <div class="event-item" style="border-left-color:${scoreColor(ev.score || 0)}">
        <div class="event-date">${ev.type} · ${formatDate(ev.date)}</div>
        <div class="event-desc">${ev.description || ''}</div>
        <span class="event-signal" style="background:${scoreColor(ev.score||0)}22;color:${scoreColor(ev.score||0)}">${ev.signal || ''}</span>
      </div>`).join('')
    : '<p class="text-muted fs-12">No critical events in this period.</p>';

  // Dasha context
  const dc = pred.dasha_context;
  if (dc && dc.mahadasha) {
    document.getElementById('dashaContextCard').style.display = 'block';
    document.getElementById('dashaContext').innerHTML = `
      <div class="dasha-ctx-item">
        <div class="dasha-ctx-label">Mahadasha</div>
        <div class="dasha-ctx-value text-gold">${dc.mahadasha}</div>
        <div class="dasha-ctx-sub">${formatDate(dc.mahadasha_start)} → ${formatDate(dc.mahadasha_end)}</div>
      </div>
      <div class="dasha-ctx-item">
        <div class="dasha-ctx-label">Antardasha</div>
        <div class="dasha-ctx-value text-accent">${dc.antardasha || '—'}</div>
        <div class="dasha-ctx-sub">${dc.antardasha_start ? formatDate(dc.antardasha_start) + ' → ' + formatDate(dc.antardasha_end) : ''}</div>
      </div>
      <div class="dasha-ctx-item" style="grid-column:1/-1">
        <div class="dasha-ctx-label">Combined Score</div>
        <div class="dasha-ctx-value" style="color:${scoreColor(dc.combined_score||0)}">${dc.combined_score > 0 ? '+' : ''}${dc.combined_score?.toFixed(3) || '0'}</div>
        <div class="dasha-ctx-sub">${dc.market_outlook || ''}</div>
      </div>`;
  }

  // Risk factors
  const risks = pred.risk_factors || [];
  document.getElementById('riskFactors').innerHTML = risks.length
    ? risks.map(r => `<div class="risk-item">⚠️ ${r}</div>`).join('')
    : '<p class="text-muted fs-12">No major risk factors detected.</p>';
}


// ═══════════════════════════════════════════════════════════════════
// 2. BIRTH CHART
// ═══════════════════════════════════════════════════════════════════

document.getElementById('chartForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('chartStatus', 'loading', '⏳ Calculating birth chart...');
  showLoading();
  try {
    const global = loadGlobalDetails();
    const base = getApiBase('c_apiBase');
    const data = await apiPost(base, '/chart', {
      name: document.getElementById('c_name').value || global.name,
      date: document.getElementById('c_date').value || global.date,
      time: document.getElementById('c_time').value || global.time,
      place: document.getElementById('c_place').value || global.place,
      ayanamsa: document.getElementById('c_ayanamsa').value || global.ayanamsa,
    });
    renderChart(data);
    showResultPanel('chartResultPanel');
    setStatus('chartStatus', 'success', '✅ Chart calculated successfully');
  } catch (err) {
    setStatus('chartStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
});

function renderChart(data) {
  const el = document.getElementById('chartResults');
  const nak = {};
  (data.planet_nakshatras || []).forEach(n => { nak[n.planet] = n; });

  const rows = (data.planets || []).map(p => {
    const n = nak[p.planet] || {};
    return `<tr>
      <td><strong>${p.planet}</strong></td>
      <td>${p.sign}</td>
      <td>${p.degree_in_sign?.toFixed(2)}°</td>
      <td>${p.retrograde ? '<span class="retro-badge">℞</span>' : ''}</td>
      <td><span class="nak-badge">${n.nakshatra || ''}</span></td>
      <td>${n.lord || ''}</td>
      <td class="fs-11">${n.sub_lord || ''}</td>
      <td>${signalPill(n.nse_signal || '', scoreColor(n.financial_score || 0))}</td>
    </tr>`;
  }).join('');

  const asc = data.ascendant || {};
  el.innerHTML = `
    <div class="mb-8">
      <strong class="text-gold">Ascendant (Lagna):</strong>
      <span class="text-accent">${asc.sign}</span>
      ${asc.degree_in_sign?.toFixed(2)}° | ${nak[asc.sign]?.nakshatra || ''}
    </div>
    <div class="table-wrap">
      <table class="planet-table">
        <thead><tr>
          <th>Planet</th><th>Sign</th><th>Degree</th><th>℞</th>
          <th>Nakshatra</th><th>Lord</th><th>Sub-Lord</th><th>NSE Signal</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;
}


// ═══════════════════════════════════════════════════════════════════
// 3. DASHA
// ═══════════════════════════════════════════════════════════════════

document.getElementById('dashaForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('dashaStatus', 'loading', '⏳ Calculating Vimshottari Dasha...');
  showLoading('Computing dasha timeline...');
  try {
    const global = loadGlobalDetails();
    const base = getApiBase('d_apiBase');
    const body = {
      name: document.getElementById('d_name').value || global.name,
      date: document.getElementById('d_date').value || global.date,
      time: document.getElementById('d_time').value || global.time,
      place: document.getElementById('d_place').value || global.place,
      ayanamsa: document.getElementById('d_ayanamsa').value || global.ayanamsa,
    };
    const asOf = document.getElementById('d_as_of').value;
    if (asOf) body.as_of_date = asOf;
    const data = await apiPost(base, '/dasha', body);
    renderDasha(data);
    setStatus('dashaStatus', 'success', '✅ Dasha calculated');
  } catch (err) {
    setStatus('dashaStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
});

function renderDasha(data) {
  const el = document.getElementById('dashaResults');
  const current = data.current_dasha || {};
  const dd = data.dasha_data || {};

  let html = `<div class="card mb-8" style="background:rgba(240,192,64,0.08);border-color:var(--gold)">
    <div class="card-title">⭐ Currently Active Dasha</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
      <div>
        <div class="fs-11 text-muted">Mahadasha</div>
        <div class="text-gold fw-700" style="font-size:18px">${current.mahadasha || '—'}</div>
        <div class="fs-11 text-muted">${formatDate(current.mahadasha_start)} → ${formatDate(current.mahadasha_end)}</div>
      </div>
      <div>
        <div class="fs-11 text-muted">Antardasha</div>
        <div class="text-accent fw-700" style="font-size:15px">${current.antardasha || '—'}</div>
        <div class="fs-11 text-muted">${current.antardasha_start ? formatDate(current.antardasha_start) + ' → ' + formatDate(current.antardasha_end) : ''}</div>
      </div>
      <div>
        <div class="fs-11 text-muted">Pratyantar</div>
        <div class="fw-700" style="color:var(--accent2)">${current.pratyantar || '—'}</div>
        <div class="fs-11 text-muted">${current.pratyantar_start ? formatDate(current.pratyantar_start) : ''}</div>
      </div>
    </div>
    <div class="mt-8 fs-12 text-muted">${current.market_outlook || ''}</div>
    <div class="mt-4">Combined Score: <strong style="color:${scoreColor(current.combined_score||0)}">${current.combined_score > 0 ? '+' : ''}${current.combined_score?.toFixed(3) || '0'}</strong></div>
  </div>`;

  html += `<div class="fs-11 text-muted mb-8">Birth Nakshatra: <strong class="text-gold">${dd.birth_nakshatra || ''}</strong> · Lord: ${dd.birth_nakshatra_lord || ''} · Balance at birth: ${dd.balance_at_birth?.years?.toFixed(2) || ''} years</div>`;
  html += '<div class="dasha-timeline">';

  const today = new Date().toISOString().split('T')[0];
  (dd.dashas || []).forEach((maha, i) => {
    const isActive = maha.start_date <= today && today <= maha.end_date;
    const fin = maha.financial || {};
    const color = scoreColor(fin.score || 0);
    html += `
    <div class="maha-block ${isActive ? 'active-dasha' : ''}" style="border-left:4px solid ${color}">
      <div class="maha-header" onclick="this.nextElementSibling.classList.toggle('open')">
        <div>
          <span class="maha-name" style="color:${color}">${maha.mahadasha_lord}</span>
          ${isActive ? '<span style="font-size:10px;color:var(--gold);margin-left:8px">▶ ACTIVE</span>' : ''}
        </div>
        <div class="maha-dates">${formatDate(maha.start_date)} → ${formatDate(maha.end_date)} (${maha.duration_years?.toFixed(1)}y)</div>
        <div class="maha-score" style="color:${color}">${fin.score > 0 ? '+' : ''}${fin.score?.toFixed(2) || '0'}</div>
      </div>
      <div class="maha-body ${isActive ? 'open' : ''}">
        <div class="maha-desc">${fin.market_effect || ''}</div>
        <div class="fs-11 text-muted mb-8">Sectors: ${(fin.sectors || []).join(' · ')}</div>
        ${(maha.antardashas || []).map(antar => {
          const isAActive = antar.start_date <= today && today <= antar.end_date;
          const ac = scoreColor(antar.combined_score || 0);
          return `<div class="antar-row ${isAActive ? 'active-dasha' : ''}">
            <span class="antar-lord" style="color:${ac}">${antar.antardasha_lord}${isAActive ? ' ▶' : ''}</span>
            <span class="antar-dates">${formatDate(antar.start_date)} → ${formatDate(antar.end_date)}</span>
            <span class="antar-score" style="color:${ac}">${antar.combined_score > 0 ? '+' : ''}${antar.combined_score?.toFixed(2) || '0'}</span>
          </div>`;
        }).join('')}
      </div>
    </div>`;
  });
  html += '</div>';
  el.innerHTML = html;
  showResultPanel('dashaResultPanel');
}


// ═══════════════════════════════════════════════════════════════════
// 4. DIVISIONAL CHARTS
// ═══════════════════════════════════════════════════════════════════

document.getElementById('divisionalForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('divStatus', 'loading', '⏳ Calculating divisional charts...');
  showLoading('Computing D-charts...');
  try {
    const global = loadGlobalDetails();
    const base = getApiBase('dv_apiBase');
    const charts = Array.from(document.querySelectorAll('#tab-divisional input[type=checkbox]:checked')).map(c => c.value);
    const data = await apiPost(base, '/divisional', {
      name: document.getElementById('dv_name').value || global.name,
      date: document.getElementById('dv_date').value || global.date,
      time: document.getElementById('dv_time').value || global.time,
      place: document.getElementById('dv_place').value || global.place,
      charts,
    });
    renderDivisional(data);
    setStatus('divStatus', 'success', '✅ Divisional charts computed');
  } catch (err) {
    setStatus('divStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
});

function renderDivisional(data) {
  const el = document.getElementById('divResults');
  const c = data.charts || {};
  let html = '';

  if (c.d2_hora) {
    const fa = c.d2_hora.financial_analysis || {};
    html += `<div class="card mb-8">
      <h3 class="card-title">${c.d2_hora.chart}</h3>
      <p class="fs-12 text-muted mb-8">${c.d2_hora.description}</p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
        <div><div class="fs-11 text-muted">Active Income (Sun Hora)</div><div class="fw-700 text-gold">${fa.active_income_strength}</div><div class="fs-11">${c.d2_hora.sun_hora_planets?.join(', ')}</div></div>
        <div><div class="fs-11 text-muted">Passive Income (Moon Hora)</div><div class="fw-700 text-accent">${fa.passive_income_strength}</div><div class="fs-11">${c.d2_hora.moon_hora_planets?.join(', ')}</div></div>
      </div>
      <div class="signal-pill" style="background:#ffc10722;color:#ffc107;border:1px solid #ffc10744">${fa.wealth_indication}</div>
    </div>`;
  }

  if (c.d9_navamsha) {
    const fa = c.d9_navamsha.financial_analysis || {};
    const rows = (c.d9_navamsha.planets || []).map(p => `<tr>
      <td>${p.planet}</td><td>${p.d1_sign}</td><td class="text-accent">${p.d9_sign}</td>
      <td>${p.vargottama ? '<span style="color:#ffd700">★ Vargottama</span>' : ''}</td>
      <td class="fs-11">${p.d9_strength}</td>
    </tr>`).join('');
    html += `<div class="card mb-8">
      <h3 class="card-title">${c.d9_navamsha.chart}</h3>
      <p class="fs-12 text-muted mb-8">${c.d9_navamsha.description}</p>
      <div class="mb-8 fs-12"><strong class="text-gold">Navamsha Ascendant:</strong> ${c.d9_navamsha.navamsha_ascendant}</div>
      ${fa.vargottama_count > 0 ? `<div class="mb-8 fs-12 text-green">${fa.vargottama_note}</div>` : ''}
      <div class="table-wrap">
        <table class="planet-table">
          <thead><tr><th>Planet</th><th>D1 Sign</th><th>D9 Sign</th><th>Status</th><th>Strength</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
  }

  if (c.d10_dashamsha) {
    const fa = c.d10_dashamsha.financial_analysis || {};
    const rows = (c.d10_dashamsha.planets || []).map(p => `<tr>
      <td>${p.planet}</td><td>${p.d1_sign}</td><td class="text-accent">${p.d10_sign}</td>
      <td class="fs-11">${p.d10_strength}</td><td class="fs-11 text-muted">${p.career_note}</td>
    </tr>`).join('');
    html += `<div class="card mb-8">
      <h3 class="card-title">${c.d10_dashamsha.chart}</h3>
      <p class="fs-12 text-muted mb-8">${c.d10_dashamsha.description}</p>
      <div class="mb-8 fs-12"><strong class="text-gold">D10 Ascendant:</strong> ${c.d10_dashamsha.d10_ascendant} (Lord: ${c.d10_dashamsha.d10_asc_lord})</div>
      <div class="mb-8 signal-pill" style="background:#7c6cf722;color:var(--accent2);border:1px solid #7c6cf744">${fa.career_strength}</div>
      <div class="table-wrap">
        <table class="planet-table">
          <thead><tr><th>Planet</th><th>D1 Sign</th><th>D10 Sign</th><th>Strength</th><th>Career</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
  }

  el.innerHTML = html || '<p class="text-muted">No charts computed.</p>';
  showResultPanel('divResultPanel');
}

document.getElementById('sbcForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('sbcStatus', 'loading', '⏳ Casting Sarvatobhadra Chakra with Vedha/Latta analysis...');
  showLoading('Computing Sarvatobhadra Chakra + transit analysis...');
  try {
    const global = loadGlobalDetails();
    const base = getApiBase('sbc_apiBase');
    const today = new Date().toISOString().split('T')[0];
    const body = {
      name:     document.getElementById('sbc_name').value  || global.name,
      date:     document.getElementById('sbc_date').value  || global.date,
      time:     document.getElementById('sbc_time').value  || global.time,
      place:    document.getElementById('sbc_place').value || global.place,
      ayanamsa: document.getElementById('sbc_ayanamsa').value || global.ayanamsa || 'lahiri',
      transit_date:  document.getElementById('sbc_transit_date').value  || today,
      transit_time:  document.getElementById('sbc_transit_time').value  || '09:15',
      transit_place: document.getElementById('sbc_transit_place').value || 'Mumbai, Maharashtra, India',
    };
    const data = await apiPost(base, '/sarvatobhadra', body);
    renderSarvatobhadra(data);
    setStatus('sbcStatus', 'success', '✅ Sarvatobhadra Chakra with full Vedha/Latta analysis complete');
  } catch (err) {
    setStatus('sbcStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
});

// ─── SBC Constants ───────────────────────────────────────────────
const SBC_ZONE_STYLE = {
  outer:  { bg: '#1a3a1a', border: '#4caf50', text: '#a5d6a7' },   // green
  second: { bg: '#2a3a1a', border: '#8bc34a', text: '#dce775' },   // yellow-green
  third:  { bg: '#3a2a2a', border: '#f48fb1', text: '#f8bbd0' },   // pink
  fourth: { bg: '#1a2a3a', border: '#64b5f6', text: '#bbdefb' },   // blue
  center: { bg: '#3a2a00', border: '#ffd700', text: '#fff176' },   // gold
};

const PLANET_COLORS = {
  Sun:'#FFA500', Moon:'#C0C0C0', Mars:'#FF4444', Mercury:'#00CED1',
  Jupiter:'#FFD700', Venus:'#FF69B4', Saturn:'#4169E1',
  Rahu:'#8B008B', Ketu:'#808080',
};

const DIRECTION_LABELS = {
  0: '← EAST →', 8: '← WEST →',
};

function renderSarvatobhadra(data) {
  const el = document.getElementById('sbcResults');
  const grid = data.chakra_grid || [];
  const cells = data.chakra_cells || [];
  const moonNak = data.moon_nakshatra || {};
  const asc = data.ascendant || {};
  const planets = data.planet_positions || [];

  // Build lookup of which planets are at which grid cell
  const planetAtCell = {};
  cells.forEach(cell => {
    const pEntities = (cell.entities || []).filter(e => e.entity_type === 'special');
    if (pEntities.length) {
      planetAtCell[`${cell.row},${cell.col}`] = pEntities.map(e => e.name);
    }
  });

  // Render the 9×9 grid
  const gridRows = grid.map((row, rowIdx) => {
    const tds = row.map((cell, colIdx) => {
      const zone = cell.zone || 'inner';
      const style = SBC_ZONE_STYLE[zone] || SBC_ZONE_STYLE.center;
      const planetsHere = planetAtCell[`${cell.row},${cell.col}`] || [];
      const hasPlanet = planetsHere.length > 0;

      // Main label
      const label = cell.label && cell.label !== '·' ? cell.label : '';
      const baseEntity = (cell.entities || []).find(
        e => ['nakshatra','rashi','tithi','vara','corner'].includes(e.entity_type));
      const displayLabel = label || (baseEntity ? baseEntity.name : '·');

      // Planet badges
      const planetBadges = planetsHere.map(p =>
        `<div style="background:${PLANET_COLORS[p]||'#888'};color:#000;border-radius:3px;padding:1px 4px;font-size:9px;font-weight:700;margin-top:2px">${p}</div>`
      ).join('');

      const border = hasPlanet ? `2px solid ${PLANET_COLORS[planetsHere[0]]||'#ffd700'}` : `1px solid ${style.border}`;
      const bg = hasPlanet ? style.bg.replace('1a','2a') : style.bg;
      const shadow = hasPlanet ? `0 0 8px ${PLANET_COLORS[planetsHere[0]]}44` : 'none';

      return `<td style="
        background:${bg};border:${border};box-shadow:${shadow};
        padding:4px;vertical-align:top;text-align:center;
        min-width:70px;max-width:90px;height:60px;
        color:${style.text};font-size:10px;line-height:1.3;
        transition:all 0.2s;
      " title="${displayLabel} · ${zone}">
        <div style="font-weight:700;font-size:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${displayLabel}</div>
        <div style="font-size:9px;opacity:0.6">${zone}</div>
        ${planetBadges}
      </td>`;
    }).join('');

    // Add direction label row
    const dirLabel = DIRECTION_LABELS[rowIdx] || '';
    return `<tr>${tds}${dirLabel ? `<td style="padding:4px 8px;color:#888;font-size:10px;white-space:nowrap;vertical-align:middle">${dirLabel}</td>` : '<td></td>'}</tr>`;
  });

  // Column direction labels (NORTH = right, SOUTH = left)
  const colLabels = `<tr>
    <td style="text-align:center;color:#888;font-size:10px;padding:4px">↕ SOUTH</td>
    ${Array(7).fill('<td></td>').join('')}
    <td style="text-align:center;color:#888;font-size:10px;padding:4px">↕ NORTH</td>
    <td></td>
  </tr>`;

  // Occupied cells table
  const occupied = cells.filter(c => (c.entities||[]).some(e => e.entity_type === 'special'));
  const occupiedRows = occupied.length
    ? occupied.map(cell => {
        const pNames = (cell.entities||[]).filter(e=>e.entity_type==='special').map(e=>e.name);
        const baseNames = (cell.entities||[]).filter(e=>e.entity_type!=='special').map(e=>e.name).join(', ');
        const nak = (cell.entities||[]).find(e=>e.entity_type==='nakshatra');
        const badges = pNames.map(p =>
          `<span style="background:${PLANET_COLORS[p]||'#888'};color:#000;border-radius:10px;padding:2px 8px;font-size:10px;font-weight:700;margin:2px">${p}</span>`
        ).join('');
        return `<tr>
          <td>${nak ? `<strong>${nak.name}</strong>` : cell.label || `(${cell.row},${cell.col})`}</td>
          <td><span style="font-size:10px;opacity:0.7">${cell.zone}</span></td>
          <td>${baseNames || '–'}</td>
          <td>${badges}</td>
        </tr>`;
      }).join('')
    : `<tr><td colspan="4" class="text-muted">No natal planets placed on chakra cells.</td></tr>`;

  // Zone legend
  const legend = Object.entries(SBC_ZONE_STYLE).map(([zone, s]) =>
    `<span style="background:${s.bg};border:1px solid ${s.border};color:${s.text};padding:3px 10px;border-radius:4px;font-size:11px;margin-right:6px">${zone}</span>`
  ).join('');

  const sbc = data.sbc_analysis || {};
  const mktSignal = sbc.market_signal || {};
  const bindus = sbc.six_bindus || {};
  const navatara = sbc.navatara || {};
  const vedhaHits = sbc.all_vedha_hits || [];
  const lattaHits = sbc.all_latta_hits || [];
  const binduCells = sbc.bindu_cells || {};
  const vedhaOverlay = sbc.cells_under_vedha || {};
  const lattaOverlay = sbc.cells_with_latta || {};
  const binduAnalysis = sbc.bindu_analysis || [];
  const planetAnalyses = sbc.planet_analyses || [];

  // Build overlay lookups: "row,col" → info
  const overlayData = {};
  Object.values(binduCells).forEach(b => {
    const key = `${b.row},${b.col}`;
    overlayData[key] = overlayData[key] || {};
    overlayData[key].bindu = Object.entries(binduCells).find(([,v])=>v.row===b.row&&v.col===b.col)?.[0];
  });
  Object.entries(vedhaOverlay).forEach(([key,v]) => {
    overlayData[key] = overlayData[key] || {};
    overlayData[key].vedha = v.net;
    overlayData[key].vedha_planets = [...(v.malefic||[]), ...(v.benefic||[])];
  });
  Object.entries(lattaOverlay).forEach(([key,v]) => {
    overlayData[key] = overlayData[key] || {};
    overlayData[key].latta = v.planets;
  });

  // Render grid with overlays
  const gridRowsAdv = grid.map((row, rowIdx) => {
    const tds = row.map((cell, colIdx) => {
      const zone = cell.zone || 'inner';
      const style = SBC_ZONE_STYLE[zone] || SBC_ZONE_STYLE.center;
      const key = `${cell.row},${cell.col}`;
      const overlay = overlayData[key] || {};
      const planetsHere = planetAtCell[key] || [];
      const hasPlanet = planetsHere.length > 0;
      const isBindu = !!overlay.bindu;
      const hasLatta = overlay.latta?.length > 0;
      const vedhaNet = overlay.vedha;

      const label = cell.label && cell.label !== '·' ? cell.label : '';
      const baseEntity = (cell.entities||[]).find(e=>['nakshatra','rashi','tithi','vara','corner'].includes(e.entity_type));
      const displayLabel = label || (baseEntity ? baseEntity.name : '·');

      // Planet badges
      const pBadges = planetsHere.map(p =>
        `<div style="background:${PLANET_COLORS[p]||'#888'};color:#000;border-radius:3px;padding:1px 4px;font-size:9px;font-weight:700;margin-top:2px">${p}</div>`
      ).join('');

      // Bindu badge
      const binduBadge = isBindu
        ? `<div style="background:#ffd700;color:#000;border-radius:3px;padding:1px 4px;font-size:8px;font-weight:700;margin-top:2px">★${overlay.bindu?.slice(0,4)}</div>` : '';

      // Latta badge
      const lattaBadge = hasLatta
        ? `<div style="background:#ff00ff;color:#fff;border-radius:3px;padding:1px 4px;font-size:8px;font-weight:700;margin-top:2px">⚡${overlay.latta.join(',')}</div>` : '';

      // Border/bg based on overlay
      let border = `1px solid ${style.border}`;
      let bg = style.bg;
      let shadow = 'none';
      if (isBindu) { border = '2px solid #ffd700'; shadow = '0 0 10px #ffd70066'; bg = '#2a2000'; }
      if (hasPlanet) { border = `2px solid ${PLANET_COLORS[planetsHere[0]]||'#888'}`; shadow = `0 0 8px ${PLANET_COLORS[planetsHere[0]]}44`; }
      if (vedhaNet === 'malefic') { bg = 'rgba(255,61,0,0.2)'; }
      else if (vedhaNet === 'benefic') { bg = 'rgba(0,200,81,0.1)'; }
      if (hasLatta) { border = '2px solid #ff00ff'; }

      return `<td style="background:${bg};border:${border};box-shadow:${shadow};
        padding:4px;vertical-align:top;text-align:center;
        min-width:72px;max-width:90px;height:65px;
        color:${style.text};font-size:9px;line-height:1.3;position:relative"
        title="${displayLabel} [${zone}]${isBindu?' | ★'+overlay.bindu:''}${hasLatta?' | ⚡Latta':''}${vedhaNet?' | Vedha:'+vedhaNet:''}">
        <div style="font-weight:700;font-size:10px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:${style.text}">${displayLabel}</div>
        <div style="font-size:8px;opacity:0.5">${zone}</div>
        ${binduBadge}${pBadges}${lattaBadge}
      </td>`;
    }).join('');
    const dirLabel = DIRECTION_LABELS[rowIdx] || '';
    return `<tr>${tds}${dirLabel ? `<td style="padding:4px 8px;color:#888;font-size:10px;white-space:nowrap;vertical-align:middle">${dirLabel}</td>` : '<td></td>'}</tr>`;
  });

  // Bindu status section
  const binduStatusHtml = binduAnalysis.map(b => {
    const statusColor = b.status==='AFFLICTED'?'#ff5722':b.status==='PROTECTED'?'#00c851':b.status==='MIXED'?'#ffc107':'#888';
    return `<div style="background:var(--bg-input);border-radius:8px;padding:10px;border-left:4px solid ${statusColor};margin-bottom:6px">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div><strong style="color:${statusColor}">${b.bindu}</strong> <span class="fs-11 text-muted">— ${b.nakshatra}</span></div>
        <span style="background:${statusColor}22;color:${statusColor};padding:2px 8px;border-radius:10px;font-size:11px;font-weight:700">${b.status}</span>
      </div>
      <div class="fs-11 text-muted mt-4">${b.description}</div>
      ${b.afflicting_planets.length ? `<div class="fs-11 mt-4">⚠️ Afflicted by: ${b.afflicting_planets.map(p=>`<span style="color:${PLANET_COLORS[p]||'#ff5722'};font-weight:700">${p}</span>`).join(', ')}</div>` : ''}
      ${b.protecting_planets.length ? `<div class="fs-11 mt-4">✅ Protected by: ${b.protecting_planets.map(p=>`<span style="color:${PLANET_COLORS[p]||'#00c851'};font-weight:700">${p}</span>`).join(', ')}</div>` : ''}
      ${b.latta_hits > 0 ? `<div class="fs-11 mt-4" style="color:#ff00ff">⚡ Latta hits: ${b.latta_hits}</div>` : ''}
    </div>`;
  }).join('');

  // Latta summary
  const lattaHtml = lattaHits.length
    ? lattaHits.map(l => `
      <div style="background:var(--bg-input);border-radius:8px;padding:10px;border-left:4px solid #ff00ff;margin-bottom:6px">
        <div style="display:flex;justify-content:space-between">
          <strong><span style="color:${PLANET_COLORS[l.planet]||'#ff00ff'}">${l.planet}</span> ⚡ kicks → ${l.kicked_nak}</strong>
          <span style="font-size:10px;color:#ff00ff;font-weight:700">${l.severity}</span>
        </div>
        ${l.bindu_type ? `<div class="fs-11 mt-4" style="color:#ffd700">★ Hits ${l.bindu_type} Bindu</div>` : ''}
        <div class="fs-11 text-muted mt-4">${l.effect}</div>
        <div class="fs-11 mt-4" style="color:#ff9800">${l.nse_impact}</div>
      </div>`) .join('')
    : '<p class="fs-12 text-muted">No significant Latta active on personal nakshatras.</p>';

  // Vedha summary (top 8)
  const topVedhas = vedhaHits.slice(0, 8);
  const vedhaHtml = topVedhas.length
    ? topVedhas.map(v => {
        const c = v.nature==='papa_vedha' ? '#ff5722' : '#00c851';
        return `<div style="background:var(--bg-input);border-radius:6px;padding:8px 12px;border-left:3px solid ${c};margin-bottom:4px;font-size:11px">
          <span style="color:${PLANET_COLORS[v.planet]||c};font-weight:700">${v.planet}</span>
          ${v.nature==='papa_vedha'?'🔴 Papa':'🟢 Shubha'} Vedha on <strong>${v.to_entity}</strong>
          ${v.bindu_type ? `<span style="color:#ffd700"> (★${v.bindu_type})</span>` : ''}
          · <span style="opacity:0.7">${v.vedha_type}</span>
        </div>`;
      }).join('')
    : '<p class="fs-12 text-muted">No significant Vedha on personal nakshatras.</p>';

  // Navatara summary for transit planets
  const navataraRows = (data.transit_planets || []).map(tp => {
    const nt = navatara[tp.nakshatra] || {};
    const qColor = nt.quality==='auspicious'?'#00c851':nt.quality==='inauspicious'?'#ff5722':'#888';
    return `<tr>
      <td><span style="color:${PLANET_COLORS[tp.planet]||'#fff'};font-weight:700">${tp.planet}</span>${tp.retrograde?'<span class="retro-badge" style="margin-left:4px">℞</span>':''}</td>
      <td>${tp.nakshatra}</td>
      <td style="color:${qColor};font-weight:700">${nt.tara||'—'}</td>
      <td style="color:${qColor}">${nt.quality||'—'}</td>
      <td class="fs-11 text-muted">${nt.description||'—'}</td>
    </tr>`;
  }).join('');

  el.innerHTML = `
    <!-- Market Signal -->
    <div class="card mb-8" style="background:rgba(${mktSignal.color==='#00C851'?'0,200,81':mktSignal.color==='#FF3D00'?'255,61,0':'255,152,0'},0.1);border-color:${mktSignal.color||'#888'}">
      <div style="display:flex;align-items:center;gap:16px">
        <div style="font-size:28px">${mktSignal.signal?.includes('BULL')?'🚀':mktSignal.signal?.includes('BEAR')?'🔻':'⚖️'}</div>
        <div>
          <div style="font-size:20px;font-weight:700;color:${mktSignal.color}">${mktSignal.signal||'NEUTRAL'}</div>
          <div class="fs-12 text-muted">SBC Score: ${mktSignal.score||0} · ${mktSignal.action||''}</div>
          ${(mktSignal.warning_tips||[]).map(t=>`<div style="color:#ff9800;font-size:11px;margin-top:2px">⚠️ ${t}</div>`).join('')}
        </div>
        <div style="margin-left:auto;text-align:right;font-size:11px;color:var(--text-muted)">
          <div>Transit: ${data.transit_date||''}</div>
          <div>Janma Nak: <strong class="text-gold">${data.janma_nakshatra||''}</strong></div>
          ${sbc.malefic_vedha_count>0?`<div style="color:#ff5722">Papa Vedhas: ${sbc.malefic_vedha_count}</div>`:''}
          ${sbc.multiple_vedha_effect?`<div style="color:#ff3d00;font-weight:700">${sbc.multiple_vedha_effect}</div>`:''}
        </div>
      </div>
    </div>

    <!-- Zone Legend + Grid -->
    <div class="card mb-8">
      <div class="card-title">🌀 Sarvatobhadra Chakra — ${data.name||''}</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px">
        ${Object.entries(SBC_ZONE_STYLE).map(([z,s])=>`<span style="background:${s.bg};border:1px solid ${s.border};color:${s.text};padding:2px 8px;border-radius:4px;font-size:10px">${z}</span>`).join('')}
        <span style="background:#2a200022;border:2px solid #ffd700;color:#ffd700;padding:2px 8px;border-radius:4px;font-size:10px">★ Bindu</span>
        <span style="background:rgba(255,0,255,0.1);border:2px solid #ff00ff;color:#ff00ff;padding:2px 8px;border-radius:4px;font-size:10px">⚡ Latta</span>
        <span style="background:rgba(255,61,0,0.2);border:1px solid #ff5722;color:#ff5722;padding:2px 8px;border-radius:4px;font-size:10px">🔴 Papa Vedha</span>
        <span style="background:rgba(0,200,81,0.1);border:1px solid #00c851;color:#00c851;padding:2px 8px;border-radius:4px;font-size:10px">🟢 Shubha Vedha</span>
      </div>
      <p class="fs-11 text-muted mb-8">East=top · North=right · West=bottom · South=left</p>
      <div class="sbc-grid-wrap" style="overflow-x:auto">
        <table id="sbcChakraTable" style="border-collapse:collapse;table-layout:fixed">
          ${colLabels}
          <tbody>${gridRowsAdv.join('')}</tbody>
        </table>
      </div>
    </div>

    <!-- Six Bindus -->
    <div class="card mb-8">
      <h3 class="card-title">★ Six Personal Bindus (Sensitive Nakshatras)</h3>
      <p class="fs-11 text-muted mb-8">These 6 nakshatras are your most sensitive personal points. Malefic transits over them are warning signs; benefic transits are favorable periods.</p>
      ${binduStatusHtml}
    </div>

    <!-- Latta (Planetary Kicks) -->
    <div class="card mb-8">
      <h3 class="card-title">⚡ Active Latta (Planetary Kicks)</h3>
      <p class="fs-11 text-muted mb-8">Sun kicks 12th·Mars kicks 3rd·Jupiter kicks 6th·Saturn kicks 8th (forward) | Venus 5th·Mercury 7th·Rahu/Ketu 9th·Moon 22nd (backward)</p>
      ${lattaHtml}
    </div>

    <!-- Vedha Summary -->
    <div class="card mb-8">
      <h3 class="card-title">🔴🟢 Vedha Analysis (Significant Hits)</h3>
      ${vedhaHtml}
    </div>

    <!-- Navatara -->
    <div class="card mb-8">
      <h3 class="card-title">🌟 Navatara — Transit Planets in Your Star Cycle</h3>
      <div class="table-wrap">
        <table class="planet-table">
          <thead><tr><th>Planet</th><th>Nakshatra</th><th>Tara</th><th>Quality</th><th>Meaning</th></tr></thead>
          <tbody>${navataraRows}</tbody>
        </table>
      </div>
    </div>

    <!-- Natal Planets -->
    <div class="card mb-8">
      <h3 class="card-title">🪐 Natal Planets on Chakra</h3>
      <div class="table-wrap">
        <table class="planet-table">
          <thead><tr><th>Cell / Nakshatra</th><th>Zone</th><th>Base Entity</th><th>Planets</th></tr></thead>
          <tbody>${occupiedRows}</tbody>
        </table>
      </div>
    </div>
  `;
  showResultPanel('sbcResultPanel');

  // Remove stale table wrapper so canvas re-attaches cleanly
  const staleWrap = document.getElementById('sbcTableWrap');
  if (staleWrap) {
    const tbl = staleWrap.querySelector('#sbcChakraTable');
    if (tbl) staleWrap.parentNode.insertBefore(tbl, staleWrap);
    staleWrap.remove();
  }

  // Draw Vedha lines on Canvas after DOM renders
  setTimeout(() => drawSBCVedhaLines(data), 150);
}


// ── Interactive Canvas Vedha Line Renderer ────────────────────────────────────
// Hover = show lines temporarily  |  Click = pin/unpin lines
// ─────────────────────────────────────────────────────────────────────────────
function drawSBCVedhaLines(data) {
  const sbc           = data.sbc_analysis || {};
  const vedhaLinesAll = sbc.vedha_lines_all || [];
  const binduCells    = sbc.bindu_cells || {};

  // Remove existing canvas + tooltip
  ['sbcVedhaCanvas','sbcVedhaTooltip','sbcVedhaControls'].forEach(id => {
    const el = document.getElementById(id); if (el) el.remove();
  });
  if (!vedhaLinesAll.length) return;

  const table = document.getElementById('sbcChakraTable');
  if (!table) return;

  // Wrap table in relative container
  let tableWrapper = table.parentNode;
  if (!tableWrapper.id || tableWrapper.id !== 'sbcTableWrap') {
    const wrap = document.createElement('div');
    wrap.id = 'sbcTableWrap';
    wrap.style.cssText = 'position:relative; display:inline-block; min-width:100%';
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
    tableWrapper = wrap;
  }

  // Canvas — pointer-events ON (we need mouse events)
  const canvas = document.createElement('canvas');
  canvas.id = 'sbcVedhaCanvas';
  canvas.width  = table.offsetWidth  || table.scrollWidth;
  canvas.height = table.offsetHeight || table.scrollHeight;
  canvas.style.cssText = 'position:absolute;top:0;left:0;z-index:10;cursor:default;';
  tableWrapper.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  // Tooltip div
  const tooltip = document.createElement('div');
  tooltip.id = 'sbcVedhaTooltip';
  tooltip.style.cssText = `
    position:fixed; display:none; z-index:9999;
    background:rgba(10,11,20,0.95); border:1px solid #4a4e80;
    border-radius:8px; padding:10px 14px; max-width:280px;
    font-size:12px; color:#e2e4f0; pointer-events:none;
    box-shadow:0 4px 24px rgba(0,0,0,0.6);
  `;
  document.body.appendChild(tooltip);

  // ── Control buttons above the grid ──────────────────────────────
  const controls = document.createElement('div');
  controls.id = 'sbcVedhaControls';
  controls.style.cssText = `
    display:flex; gap:10px; flex-wrap:wrap; align-items:center;
    margin-bottom:10px; padding:8px 12px;
    background:var(--bg-card2,#161830); border:1px solid var(--border,#2a2e4a);
    border-radius:8px; font-size:11px;
  `;
  // Line-style legend items rendered as HTML (no canvas overlap)
  const legendItems = [
    { style:'border-top:2px solid #aaa',           label:'Direct (Dakshina)' },
    { style:'border-top:3.5px solid #aaa',         label:'Atichar (Vama)'    },
    { style:'border-top:2px dashed #aaa',          label:'Retrograde (Prishtha)' },
    { style:'border-top:4px double #aaa',          label:'Stationary (Sthana)'   },
    { style:'border:2px solid #ffd700;border-radius:50%;width:10px;height:10px;display:inline-block', label:'Bindu ★' },
  ];
  const legendHtml = legendItems.map(l =>
    `<span style="display:inline-flex;align-items:center;gap:5px;color:#aaa;white-space:nowrap">
      <span style="display:inline-block;width:28px;${l.style}"></span>${l.label}
    </span>`
  ).join('');
  controls.innerHTML = `
    <span style="color:#666;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.5px">Vedha Lines:</span>
    ${legendHtml}
    <span style="flex:1"></span>
    <span style="color:#8892b0;font-size:10px">Hover planet ● to preview · Click to pin 📌</span>
    <button id="sbcShowAll" style="background:#2a2e4a;border:1px solid #4a4e80;color:#e2e4f0;
      padding:3px 10px;border-radius:6px;font-size:11px;cursor:pointer">Show All</button>
    <button id="sbcClearAll" style="background:#2a2e4a;border:1px solid #4a4e80;color:#e2e4f0;
      padding:3px 10px;border-radius:6px;font-size:11px;cursor:pointer">Clear All</button>
  `;
  tableWrapper.parentNode.insertBefore(controls, tableWrapper);

  // ── Cell center (pixel-perfect via getBoundingClientRect) ───────
  function cellCenter(row, col) {
    const rows = table.querySelectorAll('tr');
    const domRow = rows[row + 1]; // row+1: skip the direction-labels row
    if (!domRow) return null;
    const td = domRow.querySelectorAll('td')[col];
    if (!td) return null;
    const cr = canvas.getBoundingClientRect();
    const tr = td.getBoundingClientRect();
    return { x: tr.left - cr.left + tr.width / 2, y: tr.top - cr.top + tr.height / 2 };
  }

  // ── Pre-compute planet dots (centers + hit radius) ──────────────
  const PLANET_RADIUS = 12;
  const planetDots = [];  // { planet, color, center, lineData, lineStyle, vedhaType, speed, retrograde }

  vedhaLinesAll.forEach(vl => {
    if (!vl || !vl.lines) return;
    const center = cellCenter(vl.position[0], vl.position[1]);
    if (!center) return;
    planetDots.push({
      planet:    vl.planet,
      color:     PLANET_COLORS[vl.planet] || '#888888',
      center,
      lines:     vl.lines,
      lineStyle: vl.line_style,
      vedhaType: vl.vedha_type,
      speed:     vl.speed,
      retrograde:vl.line_style === 'dashed',
      radius:    PLANET_RADIUS,
    });
  });

  // Bindu centers
  const binduDots = {};
  Object.entries(binduCells).forEach(([name, b]) => {
    const c = cellCenter(b.row, b.col);
    if (c) binduDots[name] = { ...c, nakshatra: b.nakshatra };
  });

  // ── State ───────────────────────────────────────────────────────
  let hoveredPlanet = null;
  const pinnedPlanets = new Set();

  // ── Drawing helpers ─────────────────────────────────────────────
  function applyLineStyle(lineStyle, color, alpha) {
    const hex = Math.round(alpha * 255).toString(16).padStart(2, '0');
    ctx.strokeStyle = color + hex;
    ctx.setLineDash([]);
    if      (lineStyle === 'dashed') { ctx.setLineDash([7, 5]); ctx.lineWidth = 1.8; }
    else if (lineStyle === 'thick')  { ctx.lineWidth = 3.0; }
    else if (lineStyle === 'double') { ctx.lineWidth = 4.0; }
    else                             { ctx.lineWidth = 1.8; }
  }

  function drawPlanetLines(dot, alpha) {
    dot.lines.forEach(line => {
      const from = cellCenter(line.from[0], line.from[1]);
      const to   = cellCenter(line.to[0],   line.to[1]);
      if (!from || !to) return;
      applyLineStyle(dot.lineStyle, dot.color, alpha);
      ctx.beginPath();
      ctx.moveTo(from.x, from.y);
      ctx.lineTo(to.x,   to.y);
      ctx.stroke();
    });
    ctx.setLineDash([]);
  }

  function drawPlanetDot(dot, isHovered, isPinned) {
    const { center: c, color, planet } = dot;
    const r = isHovered ? PLANET_RADIUS + 3 : PLANET_RADIUS;

    // Glow for hovered/pinned
    if (isHovered || isPinned) {
      ctx.shadowColor = color;
      ctx.shadowBlur  = isHovered ? 16 : 10;
    }

    // Filled circle for pinned, ring for normal
    ctx.beginPath();
    ctx.arc(c.x, c.y, r, 0, Math.PI * 2);
    if (isPinned) {
      ctx.fillStyle = color + 'cc';
      ctx.fill();
    }
    ctx.strokeStyle = color;
    ctx.lineWidth   = isPinned ? 2.5 : 2;
    ctx.stroke();

    ctx.shadowBlur = 0;
    ctx.shadowColor = 'transparent';

    // Pin indicator
    if (isPinned) {
      ctx.fillStyle = '#000000';
      ctx.font = 'bold 9px Inter,sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('📌', c.x, c.y + 3);
    }

    // Planet label above dot
    ctx.fillStyle = color;
    ctx.font = `bold ${isHovered ? 10 : 9}px Inter,sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText(planet.slice(0, 3), c.x, c.y - r - 4);
  }

  function drawBinduRings() {
    Object.entries(binduDots).forEach(([name, c]) => {
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = '#ffd700bb';
      ctx.lineWidth   = 1.5;
      ctx.beginPath();
      ctx.arc(c.x, c.y, 18, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = '#ffd70088';
      ctx.font = '7px Inter,sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('★' + name.slice(0, 4), c.x, c.y - 20);
    });
  }

  // Legend is now rendered as HTML in the controls bar above — nothing drawn on canvas

  // ── Main redraw ─────────────────────────────────────────────────
  function redraw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw lines for pinned planets (behind dots)
    planetDots.forEach(dot => {
      if (pinnedPlanets.has(dot.planet)) drawPlanetLines(dot, 0.75);
    });

    // Draw lines for hovered planet (on top of pinned, slightly brighter)
    if (hoveredPlanet) {
      const dot = planetDots.find(d => d.planet === hoveredPlanet);
      if (dot && !pinnedPlanets.has(hoveredPlanet)) drawPlanetLines(dot, 0.90);
    }

    // Draw bindu rings
    drawBinduRings();

    // Draw all planet dots
    planetDots.forEach(dot => {
      drawPlanetDot(
        dot,
        dot.planet === hoveredPlanet,
        pinnedPlanets.has(dot.planet)
      );
    });

  }

  // ── Mouse event helpers ─────────────────────────────────────────
  function canvasXY(e) {
    const r = canvas.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  }

  function hitPlanet(x, y) {
    for (const dot of planetDots) {
      const dx = x - dot.center.x, dy = y - dot.center.y;
      if (Math.sqrt(dx*dx + dy*dy) <= dot.radius + 4) return dot;
    }
    return null;
  }

  function showTooltip(dot, e) {
    const retro = dot.retrograde ? '℞ Retrograde' : 'Direct';
    const speed = dot.speed != null ? `${Math.abs(dot.speed).toFixed(4)}°/day` : '';
    const pinned = pinnedPlanets.has(dot.planet);
    tooltip.innerHTML = `
      <div style="font-weight:700;color:${dot.color};font-size:13px;margin-bottom:6px">
        ${dot.planet}  <span style="font-size:10px;color:#888">${retro}</span>
      </div>
      <div style="margin-bottom:4px"><span style="color:#888">Vedha Type:</span>
        <strong style="color:#a78bfa"> ${dot.vedhaType}</strong></div>
      <div style="margin-bottom:4px"><span style="color:#888">Speed:</span>
        <strong> ${speed}</strong></div>
      <div style="font-size:11px;color:#888;margin-top:6px;border-top:1px solid #2a2e4a;padding-top:6px">
        ${pinned ? '📌 Pinned — click to unpin' : '🖱️ Click to pin vedha lines'}
      </div>`;
    tooltip.style.display = 'block';
    tooltip.style.left = (e.clientX + 14) + 'px';
    tooltip.style.top  = (e.clientY - 10) + 'px';
  }

  function hideTooltip() {
    tooltip.style.display = 'none';
  }

  // ── Event listeners ─────────────────────────────────────────────
  canvas.addEventListener('mousemove', e => {
    const { x, y } = canvasXY(e);
    const hit = hitPlanet(x, y);
    const name = hit ? hit.planet : null;
    if (name !== hoveredPlanet) {
      hoveredPlanet = name;
      canvas.style.cursor = name ? 'pointer' : 'default';
      redraw();
    }
    if (hit) showTooltip(hit, e);
    else hideTooltip();
  });

  canvas.addEventListener('mouseleave', () => {
    hoveredPlanet = null;
    canvas.style.cursor = 'default';
    hideTooltip();
    redraw();
  });

  canvas.addEventListener('click', e => {
    const { x, y } = canvasXY(e);
    const hit = hitPlanet(x, y);
    if (!hit) return;
    if (pinnedPlanets.has(hit.planet)) pinnedPlanets.delete(hit.planet);
    else                               pinnedPlanets.add(hit.planet);
    showTooltip(hit, e);
    redraw();
  });

  // Control buttons
  document.getElementById('sbcShowAll')?.addEventListener('click', () => {
    planetDots.forEach(d => pinnedPlanets.add(d.planet));
    redraw();
  });
  document.getElementById('sbcClearAll')?.addEventListener('click', () => {
    pinnedPlanets.clear();
    redraw();
  });

  // Initial draw (only dots + bindus, no lines)
  redraw();
}


// ═══════════════════════════════════════════════════════════════════
// 5. ASHTAKAVARGA
// ═══════════════════════════════════════════════════════════════════

document.getElementById('ashtakavargaForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('avStatus', 'loading', '⏳ Computing Ashtakavarga...');
  showLoading('Computing Ashtakavarga and transit dates...');
  try {
    const global = loadGlobalDetails();
    const base = getApiBase('av_apiBase');
    const body = {
      name: document.getElementById('av_name').value || global.name,
      date: document.getElementById('av_date').value || global.date,
      time: document.getElementById('av_time').value || global.time,
      place: document.getElementById('av_place').value || global.place,
      days_ahead: parseInt(document.getElementById('av_days').value),
    };
    const fromDate = document.getElementById('av_from').value;
    if (fromDate) body.transit_from_date = fromDate;
    const data = await apiPost(base, '/ashtakavarga', body);
    renderAshtakavarga(data);
    setStatus('avStatus', 'success', '✅ Ashtakavarga computed');
  } catch (err) {
    setStatus('avStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
});

const SIGNS_ORDER = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];

function renderAshtakavarga(data) {
  const el = document.getElementById('avResults');
  const sav = data.sarvashtakavarga || {};
  const bav = sav.bhinnashtakavarga || {};
  const tp = data.transit_predictions || {};

  // SAV table
  let savHtml = `<div class="card mb-8">
    <h3 class="card-title">Sarvashtakavarga (Total SAV Scores)</h3>
    <p class="fs-12 text-muted mb-8">Strongest: <strong class="text-green">${sav.strongest_sign || ''}</strong> · Weakest: <strong class="text-red">${sav.weakest_sign || ''}</strong></p>
    <div class="table-wrap">
      <table class="av-table">
        <thead><tr><th>Sign</th>${SIGNS_ORDER.map(s => `<th>${s.slice(0,3)}</th>`).join('')}</tr></thead>
        <tbody>
          <tr><td class="fw-700">SAV</td>${SIGNS_ORDER.map(s => {
            const v = sav.sarvashtakavarga?.[s] || 0;
            const cls = v >= 30 ? 'av-score-high' : v <= 18 ? 'av-score-low' : 'av-score-mid';
            return `<td class="${cls}">${v}</td>`;
          }).join('')}</tr>
          ${Object.entries(bav).map(([planet, data]) =>
            `<tr><td>${planet}</td>${SIGNS_ORDER.map(s => {
              const v = data.scores?.[s] || 0;
              const cls = v >= 5 ? 'av-score-high' : v <= 2 ? 'av-score-low' : '';
              return `<td class="${cls}">${v}</td>`;
            }).join('')}</tr>`
          ).join('')}
        </tbody>
      </table>
    </div>
  </div>`;

  // Transit predictions
  const alerts = tp.transit_alerts || [];
  const summary = tp.summary || {};
  let transitHtml = `<div class="card">
    <h3 class="card-title">Transit Predictions with Ashtakavarga Scores (${tp.days_ahead || 0} days)</h3>
    ${summary.overall_outlook ? `<div class="mb-8 overall-badge" style="color:${scoreColor(summary.avg_transit_score||0)}">${summary.overall_outlook}: ${summary.recommendation}</div>` : ''}
    ${alerts.slice(0, 20).map(a => `
      <div class="av-transit-card" style="border-left-color:${a.market_impact?.color || '#666'}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div>
            <strong>${a.planet} → ${a.entering_sign}</strong>
            ${a.retrograde ? '<span class="retro-badge">℞</span>' : ''}
            <span class="fs-11 text-muted ml-8">${a.ingress_date}</span>
            ${a.exit_date ? `<span class="fs-11 text-muted"> → ${a.exit_date}</span>` : ''}
          </div>
          <div style="text-align:right">
            <div class="fw-700 fs-12" style="color:${a.market_impact?.color}">${a.nse_action || ''}</div>
            <div class="fs-11 text-muted">BAV: ${a.bav_score} · SAV: ${a.sav_score}</div>
          </div>
        </div>
        <div class="fs-11 text-muted mt-4">${a.bav_signal}</div>
      </div>`).join('')}
  </div>`;

  el.innerHTML = savHtml + transitHtml;
  showResultPanel('avResultPanel');
}


// ═══════════════════════════════════════════════════════════════════
// 6. YOGAS
// ═══════════════════════════════════════════════════════════════════

document.getElementById('yogaForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('yogaStatus', 'loading', '⏳ Detecting yogas...');
  showLoading('Scanning for financial yogas...');
  try {
    const global = loadGlobalDetails();
    const base = getApiBase('y_apiBase');
    const data = await apiPost(base, '/yogas', {
      name: document.getElementById('y_name').value || global.name,
      date: document.getElementById('y_date').value || global.date,
      time: document.getElementById('y_time').value || global.time,
      place: document.getElementById('y_place').value || global.place,
    });
    renderYogas(data);
    setStatus('yogaStatus', 'success', '✅ Yoga detection complete');
  } catch (err) {
    setStatus('yogaStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
});

function renderYogas(data) {
  const el = document.getElementById('yogaResults');
  const yogas = data.yogas || {};
  const signal = yogas.overall_signal || '';
  const color = yogas.signal_color || '#888';

  let html = `<div class="overall-badge" style="color:${color};background:${color}22;border-color:${color}55">
    ${signal} — Score: ${yogas.overall_yoga_score > 0 ? '+' : ''}${yogas.overall_yoga_score?.toFixed(3) || '0'}
  </div>
  <p class="fs-12 text-muted mb-8">${yogas.summary || ''}</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
    <div>
      <div class="fs-11 text-muted mb-4">Favorable Sectors</div>
      ${(yogas.favorable_sectors || []).map(s => `<span class="sector-tag sector-buy">${s}</span>`).join('')}
    </div>
    <div>
      <div class="fs-11 text-muted mb-4">Sectors to Avoid</div>
      ${(yogas.avoid_sectors || []).map(s => `<span class="sector-tag sector-avoid">${s}</span>`).join('')}
    </div>
  </div>`;

  if (yogas.positive_yogas?.length) {
    html += `<div class="section-title">✨ Positive Yogas (${yogas.positive_yogas.length})</div>`;
    html += yogas.positive_yogas.map(y => renderYogaCard(y)).join('');
  }
  if (yogas.negative_yogas?.length) {
    html += `<div class="section-title">⚠️ Challenging Yogas (${yogas.negative_yogas.length})</div>`;
    html += yogas.negative_yogas.map(y => renderYogaCard(y)).join('');
  }

  el.innerHTML = html;
  showResultPanel('yogaResultPanel');
}

function renderYogaCard(y) {
  const c = scoreColor(y.score || 0);
  return `<div class="yoga-card" style="border-left-color:${c}">
    <div class="yoga-name" style="color:${c}">${y.name}</div>
    <div class="yoga-sanskrit">${y.sanskrit || ''}</div>
    <div><span class="yoga-type" style="color:${c}">${y.type}</span> · <span class="fs-11 text-muted">Strength: ${y.strength}</span></div>
    <div class="yoga-impact">${y.financial_impact}</div>
    <span class="yoga-signal" style="background:${c}22;color:${c};border:1px solid ${c}44">${y.nse_signal}</span>
  </div>`;
}


// ═══════════════════════════════════════════════════════════════════
// 7. TRANSIT ALERTS
// ═══════════════════════════════════════════════════════════════════

document.getElementById('alertForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('alertStatus', 'loading', '⏳ Generating transit alerts...');
  showLoading('Scanning upcoming transits...');
  try {
    const global = loadGlobalDetails();
    const base = getApiBase('al_apiBase');
    const body = {
      date: document.getElementById('al_date').value,
      time: document.getElementById('al_time').value,
      place: document.getElementById('al_place').value,
      days_ahead: parseInt(document.getElementById('al_days').value),
    };
    const nd = document.getElementById('al_natal_date').value || global.date;
    const nt = document.getElementById('al_natal_time').value || global.time;
    const np = document.getElementById('al_natal_place').value || global.place;
    if (nd && nt && np) { body.natal_date = nd; body.natal_time = nt; body.natal_place = np; }
    const data = await apiPost(base, '/transit-alerts', body);
    renderAlerts(data);
    setStatus('alertStatus', 'success', `✅ ${data.alerts?.total_alerts || 0} alerts generated`);
  } catch (err) {
    setStatus('alertStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
});

function renderAlerts(data) {
  const el = document.getElementById('alertResults');
  const a = data.alerts || {};
  const outlook = a.market_outlook || '';
  const outlookColor = a.outlook_color || '#888';

  let html = `<div class="overall-badge mb-8" style="color:${outlookColor};background:${outlookColor}22;border-color:${outlookColor}55">
    ${outlook}
  </div>
  <p class="fs-12 text-muted mb-8">${a.recommendation || ''}</p>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px">
    <div><div class="fs-11 text-muted">Buy Sectors</div>${(a.nse_sectors?.buy||[]).map(s=>`<span class="sector-tag sector-buy">${s}</span>`).join('')}</div>
    <div><div class="fs-11 text-muted">Hold Sectors</div>${(a.nse_sectors?.hold||[]).map(s=>`<span class="sector-tag sector-hold">${s}</span>`).join('')}</div>
    <div><div class="fs-11 text-muted">Avoid Sectors</div>${(a.nse_sectors?.avoid||[]).map(s=>`<span class="sector-tag sector-avoid">${s}</span>`).join('')}</div>
  </div>`;

  const renderAlertItems = (items, title) => {
    if (!items?.length) return '';
    return `<div class="section-title">${title} (${items.length})</div>` +
      items.map(al => {
        const c = scoreColor(al.score || 0);
        return `<div class="alert-item" style="border-left-color:${c}">
          <div class="alert-planet">${al.planet || al.type}</div>
          <div class="alert-date">${al.type} · ${al.date === 'CURRENT' ? 'Active Now' : formatDate(al.date)}</div>
          <div class="alert-desc">${al.description}</div>
          ${al.action ? `<span class="alert-action" style="background:${c}22;color:${c}">${al.action}</span>` : ''}
        </div>`;
      }).join('');
  };

  html += renderAlertItems(a.high_priority_alerts,   '🔴 High Priority');
  html += renderAlertItems(a.medium_priority_alerts, '🟡 Medium Priority');
  html += renderAlertItems(a.low_priority_alerts,    '🟢 Low Priority');

  el.innerHTML = html;
  showResultPanel('alertResultPanel');
}
