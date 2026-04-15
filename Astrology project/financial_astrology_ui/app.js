/* ═══════════════════════════════════════════════════════════════
   Financial Astrology Engine v2.0 — Dashboard JavaScript
   ══════════════════════════════════════════════════════════════ */

// ── Helpers ──────────────────────────────────────────────────────

function getApiBase(inputId) {
  const val = document.getElementById(inputId)?.value?.trim().replace(/\/$/, '');
  return val || (window.location.protocol === 'file:' ? 'http://127.0.0.1:8001' : window.location.origin);
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

// ── Clock ────────────────────────────────────────────────────────

function updateClock() {
  const el = document.getElementById('currentTime');
  if (el) el.textContent = new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour12: false }) + ' IST';
}
updateClock();
setInterval(updateClock, 1000);

// Set today's date in all date inputs
document.addEventListener('DOMContentLoaded', () => {
  const today = new Date().toISOString().split('T')[0];
  ['p_transit_date', 'al_date'].forEach(id => {
    const el = document.getElementById(id);
    if (el && !el.value) el.value = today;
  });
});

// ═══════════════════════════════════════════════════════════════════
// 1. AUTO PREDICTION
// ═══════════════════════════════════════════════════════════════════

document.getElementById('predictForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('predictBtn');
  btn.disabled = true;
  showLoading('Running autonomous astrology prediction engine...');

  const body = {
    transit_date:  document.getElementById('p_transit_date').value,
    transit_time:  document.getElementById('p_transit_time').value,
    transit_place: document.getElementById('p_transit_place').value,
    ayanamsa:      document.getElementById('p_ayanamsa').value,
    days_ahead:    parseInt(document.getElementById('p_days_ahead').value),
  };

  const natalDate  = document.getElementById('p_natal_date').value;
  const natalTime  = document.getElementById('p_natal_time').value;
  const natalPlace = document.getElementById('p_natal_place').value;
  const natalName  = document.getElementById('p_natal_name').value;

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
    const base = getApiBase('c_apiBase');
    const data = await apiPost(base, '/chart', {
      name: document.getElementById('c_name').value,
      date: document.getElementById('c_date').value,
      time: document.getElementById('c_time').value,
      place: document.getElementById('c_place').value,
      ayanamsa: document.getElementById('c_ayanamsa').value,
    });
    renderChart(data);
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
    const base = getApiBase('d_apiBase');
    const body = {
      name: document.getElementById('d_name').value,
      date: document.getElementById('d_date').value,
      time: document.getElementById('d_time').value,
      place: document.getElementById('d_place').value,
      ayanamsa: document.getElementById('d_ayanamsa').value,
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
}


// ═══════════════════════════════════════════════════════════════════
// 4. DIVISIONAL CHARTS
// ═══════════════════════════════════════════════════════════════════

document.getElementById('divisionalForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('divStatus', 'loading', '⏳ Calculating divisional charts...');
  showLoading('Computing D-charts...');
  try {
    const base = getApiBase('dv_apiBase');
    const charts = Array.from(document.querySelectorAll('#tab-divisional input[type=checkbox]:checked')).map(c => c.value);
    const data = await apiPost(base, '/divisional', {
      name: document.getElementById('dv_name').value,
      date: document.getElementById('dv_date').value,
      time: document.getElementById('dv_time').value,
      place: document.getElementById('dv_place').value,
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
}


// ═══════════════════════════════════════════════════════════════════
// 5. ASHTAKAVARGA
// ═══════════════════════════════════════════════════════════════════

document.getElementById('ashtakavargaForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('avStatus', 'loading', '⏳ Computing Ashtakavarga...');
  showLoading('Computing Ashtakavarga and transit dates...');
  try {
    const base = getApiBase('av_apiBase');
    const body = {
      name: document.getElementById('av_name').value,
      date: document.getElementById('av_date').value,
      time: document.getElementById('av_time').value,
      place: document.getElementById('av_place').value,
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
}


// ═══════════════════════════════════════════════════════════════════
// 6. YOGAS
// ═══════════════════════════════════════════════════════════════════

document.getElementById('yogaForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  setStatus('yogaStatus', 'loading', '⏳ Detecting yogas...');
  showLoading('Scanning for financial yogas...');
  try {
    const base = getApiBase('y_apiBase');
    const data = await apiPost(base, '/yogas', {
      name: document.getElementById('y_name').value,
      date: document.getElementById('y_date').value,
      time: document.getElementById('y_time').value,
      place: document.getElementById('y_place').value,
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
    const base = getApiBase('al_apiBase');
    const body = {
      date: document.getElementById('al_date').value,
      time: document.getElementById('al_time').value,
      place: document.getElementById('al_place').value,
      days_ahead: parseInt(document.getElementById('al_days').value),
    };
    const nd = document.getElementById('al_natal_date').value;
    const nt = document.getElementById('al_natal_time').value;
    const np = document.getElementById('al_natal_place').value;
    if (nd && nt && np) { body.natal_date = nd; body.natal_time = nt; body.natal_place = np; }
    const data = await apiPost(base, '/transit-alerts', body);
    renderAlerts(data);
    setStatus('alertStatus', 'success', `✅ ${data.alerts?.total_alerts || 0} alerts generated`);
  } catch (err) {
    setStatus('alertStatus', 'error', '❌ ' + err.message);
  } finally { hideLoading(); }
}

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
}
