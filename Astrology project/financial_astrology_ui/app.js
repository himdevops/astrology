/* ═══════════════════════════════════════════════════════════════
   Financial Astrology Engine v3.0 — Dashboard JavaScript
   ══════════════════════════════════════════════════════════════ */

const API = '';  // Same origin

// ─── Tab Navigation ─────────────────────────────────────────
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    });
});

// Set today's date as default for type="date" (transit dates)
const today = new Date().toISOString().split('T')[0];
document.querySelectorAll('input[type="date"]').forEach(el => {
    if (!el.value) el.value = today;
});

// ─── DD-MM-YYYY Date Helpers ────────────────────────────────
// Convert DD-MM-YYYY → YYYY-MM-DD for API calls
function ddmmToApi(ddmm) {
    if (!ddmm) return '';
    var parts = ddmm.split('-');
    if (parts.length !== 3) return ddmm;
    return parts[2] + '-' + parts[1] + '-' + parts[0]; // YYYY-MM-DD
}
// Convert YYYY-MM-DD → DD-MM-YYYY for display
function apiToDdmm(api) {
    if (!api) return '';
    var parts = api.split('-');
    if (parts.length !== 3) return api;
    return parts[2] + '-' + parts[1] + '-' + parts[0];
}

// Auto-format DD-MM-YYYY as user types (add dashes automatically)
function setupDateInput(input) {
    input.addEventListener('input', function(e) {
        var v = this.value.replace(/[^0-9]/g, '');
        if (v.length > 8) v = v.slice(0, 8);
        if (v.length >= 5) {
            this.value = v.slice(0,2) + '-' + v.slice(2,4) + '-' + v.slice(4);
        } else if (v.length >= 3) {
            this.value = v.slice(0,2) + '-' + v.slice(2);
        } else {
            this.value = v;
        }
    });
    input.addEventListener('keydown', function(e) {
        // Allow backspace, delete, tab, arrows
        if ([8, 46, 9, 37, 39].indexOf(e.keyCode) !== -1) return;
        // Allow numbers only
        if ((e.keyCode < 48 || e.keyCode > 57) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
}
// Apply to all birth-date text inputs
document.querySelectorAll('.birth-date').forEach(setupDateInput);
// Also apply to master date
var masterDateEl = document.getElementById('master-date');
if (masterDateEl) setupDateInput(masterDateEl);

// ─── Master Birth Data Sync ────────────────────────────────
// All birth data fields across tabs (class-based)
function applyMasterToAll() {
    var name  = document.getElementById('master-name').value;
    var date  = document.getElementById('master-date').value;
    var time  = document.getElementById('master-time').value;
    var place = document.getElementById('master-place').value;

    document.querySelectorAll('.birth-name').forEach(function(el) { el.value = name; });
    document.querySelectorAll('.birth-date').forEach(function(el) { el.value = date; });
    document.querySelectorAll('.birth-time').forEach(function(el) { el.value = time; });
    document.querySelectorAll('.birth-place').forEach(function(el) { el.value = place; });
}

// Apply button
document.getElementById('master-apply-btn').addEventListener('click', applyMasterToAll);

// Also auto-apply when master fields change (live sync)
['master-name','master-date','master-time','master-place'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('change', applyMasterToAll);
});

// ─── API Helper ─────────────────────────────────────────────
async function apiCall(endpoint, body, resultEl) {
    resultEl.innerHTML = '<div class="loading">Calculating...</div>';
    try {
        const method = body ? 'POST' : 'GET';
        const opts = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) opts.body = JSON.stringify(body);
        const res = await fetch(API + endpoint, opts);
        const data = await res.json();
        console.log(`[API ${endpoint}]`, res.status, data);
        if (!res.ok) throw new Error(data.detail || JSON.stringify(data) || 'API Error');
        return data;
    } catch (e) {
        console.error(`[API ${endpoint}] ERROR:`, e);
        resultEl.innerHTML = `<div class="error-msg" style="color:#ff4444;padding:16px;font-size:1rem"><strong>Error:</strong> ${e.message}</div>`;
        return null;
    }
}

// ─── PREDICTION ─────────────────────────────────────────────
document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('predict-result');
    const body = {
        transit_date: document.getElementById('p-transit-date').value,
        transit_time: document.getElementById('p-transit-time').value,
        transit_place: document.getElementById('p-transit-place').value,
        ayanamsa: document.getElementById('p-ayanamsa').value,
    };
    const natalDate = document.getElementById('p-natal-date').value;
    if (natalDate) {
        body.natal_name = document.getElementById('p-natal-name').value;
        body.natal_date = ddmmToApi(natalDate);
        body.natal_time = document.getElementById('p-natal-time').value;
        body.natal_place = document.getElementById('p-natal-place').value;
    }

    const data = await apiCall('/predict', body, resultEl);
    if (!data) return;

    const pred = data.prediction || {};
    const signal = pred.prediction || {};
    const breakdown = pred.score_breakdown || {};
    const sectors = pred.sector_recommendations || {};
    const weekly = pred.weekly_outlook || [];
    const conf = pred.confidence || {};

    const signalClass = signal.direction?.includes('BULL') ? 'bullish' : signal.direction?.includes('BEAR') ? 'bearish' : 'neutral';
    const badgeClass = signal.signal?.includes('BUY') ? 'buy' : signal.signal?.includes('SELL') ? 'sell' : 'hold';

    resultEl.innerHTML = `
        <div class="signal-card ${signalClass}">
            <div class="signal-header">
                <div>
                    <h3 style="color:${signal.color||'#fff'}; font-size:1.4rem">${signal.signal || 'ANALYZING'}</h3>
                    <p style="color:var(--text-muted); font-size:0.85rem">${pred.prediction_date || ''} | ${pred.market || 'NSE/BSE'}</p>
                </div>
                <div class="score-display" style="color:${signal.color||'#fff'}">${(pred.overall_score * 100).toFixed(1)}%</div>
            </div>
            <p style="color:var(--text); margin-bottom:12px">${signal.nifty_bias || ''}</p>
            <p style="color:var(--text-muted); font-size:0.85rem">${signal.strategy || ''}</p>

            <div class="metrics-grid">
                <div class="metric"><div class="label">Confidence</div><div class="value gold">${conf.percent || 0}%</div></div>
                <div class="metric"><div class="label">Planet Score</div><div class="value">${breakdown.planetary_position_score?.toFixed(3) || '—'}</div></div>
                <div class="metric"><div class="label">Moon Nakshatra</div><div class="value">${breakdown.moon_nakshatra_score?.toFixed(3) || '—'}</div></div>
                <div class="metric"><div class="label">Dasha Score</div><div class="value">${breakdown.dasha_score?.toFixed(3) || '—'}</div></div>
                <div class="metric"><div class="label">Yoga Score</div><div class="value">${breakdown.yoga_score?.toFixed(3) || '—'}</div></div>
                <div class="metric"><div class="label">Transit Score</div><div class="value">${breakdown.transit_score?.toFixed(3) || '—'}</div></div>
            </div>
        </div>

        ${sectors.strong_buy?.length ? `
        <div class="card">
            <h2>Sector Recommendations</h2>
            <div style="margin-bottom:12px">
                <strong style="color:var(--green)">BUY:</strong>
                <div class="sector-tags">${sectors.strong_buy.map(s=>`<span class="sector-tag buy">${s}</span>`).join('')}</div>
            </div>
            ${sectors.hold?.length ? `<div style="margin-bottom:12px"><strong style="color:var(--orange)">HOLD:</strong><div class="sector-tags">${sectors.hold.map(s=>`<span class="sector-tag hold">${s}</span>`).join('')}</div></div>` : ''}
            ${sectors.avoid?.length ? `<div><strong style="color:var(--red)">AVOID:</strong><div class="sector-tags">${sectors.avoid.map(s=>`<span class="sector-tag avoid">${s}</span>`).join('')}</div></div>` : ''}
        </div>` : ''}

        ${weekly.length ? `
        <div class="card">
            <h2>7-Day Moon Nakshatra Outlook</h2>
            <div class="weekly-grid">
                ${weekly.map(d => `
                    <div class="day-cell" style="border-left: 3px solid ${d.signal_color}">
                        <div class="day-name">${d.day?.substring(0,3) || ''}</div>
                        <div style="color:var(--text-muted);font-size:0.7rem">${d.date?.substring(5) || ''}</div>
                        <div style="color:var(--gold);font-size:0.7rem;margin-top:4px">${d.nakshatra || ''}</div>
                        <div class="day-signal" style="color:${d.signal_color}">${d.nse_signal?.substring(0,10) || ''}</div>
                    </div>
                `).join('')}
            </div>
        </div>` : ''}

        ${pred.risk_factors?.length ? `
        <div class="card">
            <h2>Risk Factors</h2>
            <ul style="list-style:none;padding:0">${pred.risk_factors.map(r=>`<li style="color:var(--red);margin:6px 0;font-size:0.85rem">&#9888; ${r}</li>`).join('')}</ul>
        </div>` : ''}
    `;
});

// ─── PANCHANG ───────────────────────────────────────────────
document.getElementById('panchang-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('panchang-result');
    const data = await apiCall('/panchang', {
        date: document.getElementById('pc-date').value,
        time: document.getElementById('pc-time').value,
    }, resultEl);
    if (!data) return;

    const t = data.tithi || {};
    const n = data.nakshatra || {};
    const y = data.yoga || {};
    const k = data.karana || {};
    const v = data.vara || {};
    const f = data.financial_analysis || {};
    const m = data.muhurta || {};
    const chog = m.choghadiya || [];

    resultEl.innerHTML = `
        <div class="signal-card" style="border-left-color:${f.color || '#d4a843'}">
            <div class="signal-header">
                <div>
                    <h3 style="color:${f.color || '#d4a843'}">${f.signal || 'PANCHANG'}</h3>
                    <p style="color:var(--text-muted)">${data.date} | ${v.day} (${v.lord})</p>
                </div>
                <div class="score-display" style="color:${f.color || '#d4a843'}">${(f.combined_score * 100).toFixed(0)}%</div>
            </div>
            <p style="color:var(--text);margin-bottom:16px">${f.action || ''}</p>

            <div class="metrics-grid">
                <div class="metric"><div class="label">Tithi</div><div class="value gold">${t.tithi_name || ''}</div><div class="label">${t.paksha || ''} | ${t.nature || ''}</div></div>
                <div class="metric"><div class="label">Nakshatra</div><div class="value gold">${n.nakshatra_name || ''}</div><div class="label">Pada ${n.pada || ''}</div></div>
                <div class="metric"><div class="label">Yoga</div><div class="value gold">${y.yoga_name || ''}</div><div class="label">${y.signal || ''}</div></div>
                <div class="metric"><div class="label">Karana</div><div class="value ${k.is_vishti_bhadra?'red':'gold'}">${k.karana_name || ''}</div><div class="label">${k.is_vishti_bhadra ? 'VISHTI!' : 'Normal'}</div></div>
            </div>
        </div>

        <div class="card">
            <h2>Muhurta — Trading Windows</h2>
            <div class="metrics-grid">
                <div class="metric"><div class="label">Rahu Kalam</div><div class="value red">${m.rahu_kalam?.start || ''} - ${m.rahu_kalam?.end || ''}</div></div>
                <div class="metric"><div class="label">Gulika Kalam</div><div class="value red">${m.gulika_kalam?.start || ''} - ${m.gulika_kalam?.end || ''}</div></div>
                <div class="metric"><div class="label">Abhijit Muhurta</div><div class="value green">${m.abhijit_muhurta?.start || ''} - ${m.abhijit_muhurta?.end || ''}</div></div>
            </div>

            ${chog.length ? `
            <h3 style="color:var(--gold-light);margin-top:20px;font-size:0.95rem">Choghadiya</h3>
            <div class="choghadiya-grid">
                ${chog.map(c => `
                    <div class="choghadiya-slot" style="background:${c.color}15; border-color:${c.color}40">
                        <div style="font-weight:600;color:${c.color}">${c.name}</div>
                        <div style="font-size:0.75rem;color:var(--text-muted)">${c.start} - ${c.end}</div>
                        <div style="font-size:0.7rem;color:var(--text-dim);margin-top:4px">${c.quality}</div>
                    </div>
                `).join('')}
            </div>` : ''}
        </div>
    `;
});

// ─── BIRTH CHART ────────────────────────────────────────────
document.getElementById('chart-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('chart-result');
    const data = await apiCall('/chart', {
        name: document.getElementById('c-name').value,
        date: ddmmToApi(document.getElementById('c-date').value),
        time: document.getElementById('c-time').value,
        place: document.getElementById('c-place').value,
        ayanamsa: document.getElementById('c-ayanamsa').value,
    }, resultEl);
    if (!data) return;

    const asc = data.ascendant || {};
    const planets = data.planets || [];
    const nakshatras = data.planet_nakshatras || [];

    resultEl.innerHTML = `
        <div class="card">
            <h2>Birth Chart — ${data.name}</h2>
            <div class="metrics-grid">
                <div class="metric"><div class="label">Ascendant</div><div class="value gold">${asc.sign || ''}</div><div class="label">${asc.degree_in_sign?.toFixed(2) || ''}°</div></div>
            </div>
            <table class="data-table" style="margin-top:16px">
                <thead><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>Nakshatra</th><th>Pada</th><th>Sub-Lord</th><th>Retro</th></tr></thead>
                <tbody>
                    ${nakshatras.map(p => `
                        <tr>
                            <td style="font-weight:600">${p.planet}</td>
                            <td>${p.sign}</td>
                            <td>${p.longitude?.toFixed(2) || ''}°</td>
                            <td style="color:var(--gold)">${p.nakshatra || ''}</td>
                            <td>${p.pada || ''}</td>
                            <td>${p.sub_lord || ''}</td>
                            <td>${p.retrograde ? '<span style="color:var(--red)">R</span>' : ''}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
});

// ─── SHADBALA ───────────────────────────────────────────────
document.getElementById('shadbala-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('shadbala-result');
    const data = await apiCall('/shadbala', {
        name: document.getElementById('sb-name').value,
        date: ddmmToApi(document.getElementById('sb-date').value),
        time: document.getElementById('sb-time').value,
        place: document.getElementById('sb-place').value,
    }, resultEl);
    if (!data) return;

    const sb = data.shadbala || {};
    const planets = sb.planets || {};
    const ranking = sb.ranking || [];
    const summary = sb.financial_summary || {};

    resultEl.innerHTML = `
        <div class="signal-card">
            <h3 style="color:var(--gold-light)">Shadbala — Planetary Strength</h3>
            <p style="color:var(--text-muted);margin:8px 0">${summary.outlook || ''}</p>
            <div class="metrics-grid">
                <div class="metric"><div class="label">Strongest</div><div class="value green">${sb.strongest_planet || ''}</div></div>
                <div class="metric"><div class="label">Weakest</div><div class="value red">${sb.weakest_planet || ''}</div></div>
                <div class="metric"><div class="label">Strong Planets</div><div class="value gold">${sb.strong_planets?.length || 0}/7</div></div>
            </div>
        </div>

        <div class="card">
            <h2>Planetary Strength Ranking</h2>
            <table class="data-table">
                <thead><tr><th>Planet</th><th>Rupas</th><th>Required</th><th>Ratio</th><th>Strength</th><th>Financial Signal</th></tr></thead>
                <tbody>
                    ${ranking.map(r => {
                        const p = planets[r.planet] || {};
                        const fi = p.financial_impact || {};
                        const color = r.ratio >= 1.0 ? 'var(--green)' : r.ratio >= 0.7 ? 'var(--orange)' : 'var(--red)';
                        return `<tr>
                            <td style="font-weight:600">${r.planet}</td>
                            <td style="color:${color}">${r.rupas}</td>
                            <td>${p.required_rupas || ''}</td>
                            <td style="color:${color}">${r.ratio}x</td>
                            <td>${p.strength_label || ''}</td>
                            <td style="font-size:0.8rem">${fi.action || ''}</td>
                        </tr>`;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
});

// ─── ASHTAKAVARGA ────────────────────────────────────────────
document.getElementById('ashtakavarga-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('ashtakavarga-result');
    const data = await apiCall('/ashtakavarga', {
        name: document.getElementById('av-name').value,
        date: ddmmToApi(document.getElementById('av-date').value),
        time: document.getElementById('av-time').value,
        place: document.getElementById('av-place').value,
        days_ahead: parseInt(document.getElementById('av-days-ahead').value) || 180,
    }, resultEl);
    if (!data) return;

    console.log('Ashtakavarga data:', data); // Debug log

    // Remove debug display and implement proper display
    const savData = data.sarvashtakavarga || {};
    const sav = savData.sarvashtakavarga || {};
    const bav = data.bhinnashtakavarga || {};
    const transits = data.transit_predictions || [];

    resultEl.innerHTML = `
        <div class="signal-card">
            <h3 style="color:var(--gold-light)">🔢 Ashtakavarga Analysis</h3>
            <div class="metrics-grid">
                <div class="metric"><div class="label">SAV Average</div><div class="value gold">${savData.average || 0}</div></div>
                <div class="metric"><div class="label">Strongest Sign</div><div class="value green">${savData.strongest_sign || ''}</div></div>
                <div class="metric"><div class="label">Weakest Sign</div><div class="value red">${savData.weakest_sign || ''}</div></div>
            </div>
        </div>

        <div class="card">
            <h2>Sarvashtakavarga (Total Scores)</h2>
            <table class="data-table">
                <thead><tr><th>Sign</th><th>Score</th><th>Strength</th><th>Signal</th></tr></thead>
                <tbody>
                    ${Object.entries(sav).filter(([key]) => 
                        ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'].includes(key)
                    ).map(([sign, score]) => {
                        const strength = score >= 35 ? 'VERY STRONG' : score >= 28 ? 'STRONG' : score >= 21 ? 'MODERATE' : 'WEAK';
                        const color = score >= 35 ? 'var(--green)' : score >= 28 ? 'var(--gold)' : score >= 21 ? 'var(--orange)' : 'var(--red)';
                        const signal = savData.sav_signals?.[sign] || 'NEUTRAL';
                        const signalColor = signal.includes('BULLISH') ? 'var(--green)' : signal.includes('BEARISH') ? 'var(--red)' : 'var(--orange)';
                        return `<tr>
                            <td style="font-weight:600">${sign}</td>
                            <td style="color:${color};font-weight:600">${score}</td>
                            <td>${strength}</td>
                            <td style="color:${signalColor};font-weight:600">${signal}</td>
                        </tr>`;
                    }).join('')}
                </tbody>
            </table>
        </div>

        ${transits.length ? `
        <div class="card">
            <h2>Transit Predictions (${transits.length} events)</h2>
            <div class="transit-grid">
                ${transits.slice(0, 10).map(t => `
                    <div class="transit-item" style="border-left: 3px solid ${t.market_signal === 'BUY' ? 'var(--green)' : t.market_signal === 'SELL' ? 'var(--red)' : 'var(--orange)'}">
                        <div class="transit-date">${t.date}</div>
                        <div class="transit-event">${t.planet} enters ${t.sign}</div>
                        <div class="transit-signal" style="color:${t.market_signal === 'BUY' ? 'var(--green)' : t.market_signal === 'SELL' ? 'var(--red)' : 'var(--orange)'}">${t.market_signal}</div>
                        <div class="transit-reason" style="font-size:0.75rem;color:var(--text-muted)">${t.reason}</div>
                    </div>
                `).join('')}
            </div>
        </div>` : ''}
    `;
});

// ─── SARVATOBHADRA ───────────────────────────────────────────
document.getElementById('sarvatobhadra-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('sarvatobhadra-result');
    const data = await apiCall('/sarvatobhadra', {
        name: document.getElementById('sbc-name').value,
        date: ddmmToApi(document.getElementById('sbc-date').value),
        time: document.getElementById('sbc-time').value,
        place: document.getElementById('sbc-place').value,
        ayanamsa: document.getElementById('sbc-ayanamsa').value,
        transit_date: document.getElementById('sbc-transit-date').value || null,
        transit_time: document.getElementById('sbc-transit-time').value || null,
        transit_place: document.getElementById('sbc-transit-place').value || null,
    }, resultEl);
    if (!data) return;

    const sbc = data.sbc_analysis || {};
    const mkt = sbc.market_signal || {};
    const moonNak = data.moon_nakshatra || {};
    const vedhaHits = sbc.all_vedha_hits || sbc.vedha_hits || [];
    const lattaHits = sbc.all_latta_hits || sbc.latta_hits || [];
    const sixBindus = sbc.six_bindus || {};
    const binduAnalysis = sbc.bindu_analysis || {};
    const navatara = sbc.navatara || {};
    const vedhaLinesAll = sbc.vedha_lines_all || sbc.vedha_lines || [];
    const transitPlanets = data.transit_planets || [];
    const natalPlanets = data.planet_positions || [];
    const grid = data.chakra_grid || [];

    /* ── Latta fallback descriptions (used if backend data missing) ── */
    const LATTA_EFFECTS_UI = {
        Sun: "Financial loss; setbacks from authority",
        Moon: "Excessive financial loss; emotional disturbances",
        Mars: "Wounds, injuries, property disputes",
        Mercury: "Loss of position, status, reputation",
        Jupiter: "Loss of wisdom, prestige, good fortune",
        Venus: "Quarrels, discord, relationship disruptions",
        Saturn: "Disease, sorrow, chronic delays, legal issues",
        Rahu: "Grief, unhappiness, deception, shocks",
        Ketu: "Confusion, accidents, hidden problems"
    };
    const LATTA_NSE_UI = {
        Sun: "PSU/Govt stocks impacted; avoid large trades",
        Moon: "Consumer/FMCG stocks down; market weak",
        Mars: "Defense/Real estate under pressure",
        Mercury: "IT/Telecom underperformance",
        Jupiter: "Banking/Finance sector risk",
        Venus: "FMCG/Luxury sector volatile",
        Saturn: "Infrastructure/Oil sustained pressure",
        Rahu: "Tech/Foreign stocks crash risk",
        Ketu: "Pharma/Chemicals uncertain"
    };

    /* ── Build nakshatra→cell position map from grid data ───── */
    const nakCellMap = {};
    for (let r = 0; r < grid.length; r++) {
        for (let c = 0; c < (grid[r]||[]).length; c++) {
            const cell = grid[r][c];
            (cell.entities || []).forEach(function(e) {
                if (e.entity_type === 'nakshatra') {
                    nakCellMap[e.name] = [r, c];
                    nakCellMap[e.name.toLowerCase()] = [r, c];
                }
            });
        }
    }

    /* ── Place transit planets onto grid cells (they aren't in chakra_grid) */
    transitPlanets.forEach(function(tp) {
        var nak = tp.nakshatra;
        var pos = nakCellMap[nak] || nakCellMap[(nak||'').toLowerCase()];
        if (!pos || !grid[pos[0]]) return;
        var cell = grid[pos[0]][pos[1]];
        if (!cell.entities) cell.entities = [];
        var already = cell.entities.some(function(e){ return e.name === tp.planet && e.entity_type === 'special'; });
        if (!already) {
            cell.entities.push({
                name: tp.planet,
                entity_type: 'special',
                meta: { source: 'transit', nakshatra: nak, sign: tp.sign, retrograde: tp.retrograde, speed: tp.speed }
            });
        }
    });

    /* ── Mark natal planets with source tag ──────────────────── */
    for (let r = 0; r < grid.length; r++) {
        for (let c = 0; c < (grid[r]||[]).length; c++) {
            (grid[r][c].entities || []).forEach(function(e) {
                if (e.entity_type === 'special' && (!e.meta || !e.meta.source)) {
                    if (!e.meta) e.meta = {};
                    e.meta.source = 'natal';
                }
            });
        }
    }

    /* ── Helpers ─────────────────────────────────────────────── */
    const PLANET_ABBR = {Sun:'Su',Moon:'Mo',Mars:'Ma',Mercury:'Me',Jupiter:'Ju',Venus:'Ve',Saturn:'Sa',Rahu:'Ra',Ketu:'Ke'};
    const BENEFICS = new Set(['Jupiter','Venus','Mercury','Moon']);
    function abbr(n){ return PLANET_ABBR[n] || n.slice(0,2); }
    function isBenefic(n){ return BENEFICS.has(n); }
    function natalBadgeColor(n){
        if(n==='Sun') return '#2255aa';
        return isBenefic(n) ? '#1a6699' : '#334488';
    }
    function transitBadgeColor(n){
        if(n==='Sun') return '#e67700';
        return isBenefic(n) ? '#1a8c1a' : '#cc1a1a';
    }
    function shortenName(name){
        let s = name;
        if(s.length>14) s = s.replace('Shukla ','S.').replace('Krishna ','K.').replace('Uttara ','U.').replace('Purva ','P.').replace('Bhadrapada','Bhadra');
        return s;
    }

    /* ── Zone / entity-type colour maps (Parashara's Light palette) */
    const ZONE_BG   = { outer:'#d8c8f0', second:'#f5e6a3', third:'#f8f0a0', fourth:'#a8e6a0', center:'#ffe0b0' };
    const ZONE_TEXT  = { outer:'#3a2878', second:'#6b4e00', third:'#6b4e00', fourth:'#1a5a10', center:'#8b4513' };
    const TYPE_BG    = { nakshatra:'#d8c8f0', rashi:'#f5e6a3', tithi:'#f5c09a', vara:'#a8e6a0', corner:'#e8e0d0', special:'#ffe0b0', empty:'#f8f4ee' };
    const TYPE_TEXT   = { nakshatra:'#3a2878', rashi:'#6b4e00', tithi:'#7a3a10', vara:'#1a5a10', corner:'#555', special:'#8b4513', empty:'#999' };

    /* ── Navatara quality colour map ─────────────────────────── */
    const NAVATARA_COLOR = {
        'Janma':'#ff6b6b','Sampat':'#51cf66','Vipat':'#ff4444','Kshema':'#69db7c',
        'Pratyari':'#ff8787','Sadhaka':'#40c057','Vadha':'#e03131','Mitra':'#2f9e44',
        'Ati Mitra':'#087f5b','Parama Mitra':'#099268',
        'janma':'#ff6b6b','sampat':'#51cf66','vipat':'#ff4444','kshema':'#69db7c',
        'pratyari':'#ff8787','sadhaka':'#40c057','vadha':'#e03131','mitra':'#2f9e44',
        'ati_mitra':'#087f5b','parama_mitra':'#099268'
    };

    /* ── 16 Svaras (vowels) at diagonal positions per Khemraj Shloka 5 ─ */
    /* ── 20 Consonant aksharas on second ring per Shloka 7 ───────────── */
    const SBC_AKSHARAS = {
        // ── 16 Svaras (vowels) at diagonals ──
        '0,0':'अ', '1,1':'उ', '2,2':'ऌ', '3,3':'ओ',   // ईशान (NE)
        '0,8':'आ', '1,7':'ऊ', '2,6':'ॡ', '3,5':'औ',   // अग्नि (SE)
        '8,8':'इ', '7,7':'ऋ', '6,6':'ए', '5,5':'अं',   // नैऋत्य (SW)
        '8,0':'ई', '7,1':'ॠ', '6,2':'ऐ', '5,3':'अः',   // वायव्य (NW)
        '4,4':'✦',                                       // Brahma center
        // ── 20 Consonants (second ring, replacing rashi names) ──
        '1,2':'अ', '1,3':'व', '1,4':'क', '1,5':'ह', '1,6':'ड',  // East/पूर्व
        '2,7':'म', '3,7':'ट', '4,7':'प', '5,7':'र', '6,7':'त',  // दक्षिण
        '7,6':'न', '7,5':'य', '7,4':'भ', '7,3':'ज', '7,2':'ख',  // पश्चिम/West
        '6,1':'ग', '5,1':'स', '4,1':'द', '3,1':'च', '2,1':'ल'   // उत्तर/North
    };
    /* Set of ALL akshara positions (svaras + consonants) */
    const SBC_SVARA_SET = new Set(Object.keys(SBC_AKSHARAS));

    /* ── Nakshatra Pada Sounds (syllables for each pada 1-4) ─── */
    const PADA_SOUNDS = {
        'Ashwini':['Chu','Che','Cho','La'], 'Bharani':['Li','Lu','Le','Lo'],
        'Krittika':['Aa','Ei','Ou','Ae'], 'Rohini':['O','Va','Vi','Vu'],
        'Mrigashira':['Ve','Vo','Ka','Ki'], 'Ardra':['Ku','Gha','Ng','Chha'],
        'Punarvasu':['Ke','Ko','Ha','Hi'], 'Pushya':['Hu','He','Ho','Da'],
        'Ashlesha':['Di','Du','De','Do'], 'Magha':['Ma','Mi','Mu','Me'],
        'P.Phalguni':['Mo','Ta','Ti','Tu'], 'Purva Phalguni':['Mo','Ta','Ti','Tu'],
        'U.Phalguni':['Te','To','Pa','Pi'], 'Uttara Phalguni':['Te','To','Pa','Pi'],
        'Hasta':['Pu','Sha','Na','Tha'], 'Chitra':['Pe','Po','Ra','Ri'],
        'Swati':['Ru','Re','Ro','Ta'], 'Vishakha':['Ti','Tu','Te','To'],
        'Anuradha':['Na','Ni','Nu','Ne'], 'Jyeshtha':['No','Ya','Yi','Yu'],
        'Mula':['Ye','Yo','Bha','Bhi'],
        'P.Ashadha':['Bhu','Dha','Pha','Dha'], 'Purva Ashadha':['Bhu','Dha','Pha','Dha'],
        'U.Ashadha':['Bhe','Bho','Ja','Ji'], 'Uttara Ashadha':['Bhe','Bho','Ja','Ji'],
        'Abhijit':['Ju','Je','Jo','Gha'],
        'Shravana':['Khi','Khu','Khe','Kho'], 'Dhanishtha':['Ga','Gi','Gu','Ge'],
        'Shatabhisha':['Go','Sa','Si','Su'],
        'P.Bhadrapada':['Se','So','Da','Di'], 'Purva Bhadrapada':['Se','So','Da','Di'],
        'U.Bhadrapada':['Du','Tha','Jha','Da'], 'Uttara Bhadrapada':['Du','Tha','Jha','Da'],
        'Revati':['De','Tho','Cha','Chi']
    };

    /* ── Outer-ring nakshatra order for info strips ──────────── */
    const TOP_NAK   = ['Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha'];
    const RIGHT_NAK = ['Magha','P.Phalguni','U.Phalguni','Hasta','Chitra','Swati','Vishakha'];
    /* Bottom row: grid col1=Shravana → col7=Anuradha (left to right) */
    const BOT_NAK   = ['Shravana','Abhijit','U.Ashadha','P.Ashadha','Mula','Jyeshtha','Anuradha'];
    /* Left col: grid row1=Bharani → row7=Dhanishtha (top to bottom) */
    const LEFT_NAK  = ['Bharani','Ashwini','Revati','U.Bhadrapada','P.Bhadrapada','Shatabhisha','Dhanishtha'];

    /* ── Build a set of afflicted (row,col) for vedha ────────── */
    const afflictedSet = new Set();
    vedhaHits.forEach(v => {
        const tp = v.to_pos || v.target_pos;
        if(tp) afflictedSet.add(tp[0]+','+tp[1]);
    });

    /* ── Build a set of latta-affected nakshatra names ───────── */
    const lattaNakSet = new Set();
    lattaHits.forEach(l => { if(l.kicked_nakshatra) lattaNakSet.add(l.kicked_nakshatra); });

    /* ── Build navatara map (nakshatra name -> {tara, tara_number, quality}) */
    const navataraMap = {};
    Object.entries(navatara).forEach(([nak, info]) => { navataraMap[nak] = info; });

    /* ── Helper: get navatara info for a nakshatra name ──────── */
    function getNavataraFor(nakName){
        var info = navataraMap[nakName];
        if(!info) {
            var alt = Object.keys(navataraMap).find(function(k){ return k.replace(/\s+/g,'').toLowerCase() === nakName.replace(/[\s.]+/g,'').toLowerCase(); });
            if(alt) info = navataraMap[alt];
        }
        return info;
    }

    /* ── Build pada-vedha map: which nakshatra+pada has a transit planet ── */
    var padaVedhaMap = {}; // key: "NakName" -> set of padas with transit planets
    var transitPlanetsArr = data.transit_planets || [];
    transitPlanetsArr.forEach(function(tp){
        var nak = tp.nakshatra;
        if(!nak) return;
        // Check if this nakshatra is vedha-afflicted
        var isAfflicted = vedhaHits.some(function(v){ return v.planet === tp.planet; });
        if(!padaVedhaMap[nak]) padaVedhaMap[nak] = {};
        // We don't have per-pada vedha, but mark which pada the transit planet is in
        // (from the grid cell data or transit planet data)
    });
    // Build from vedha hits: mark afflicted nakshatras (both source and target)
    var vedhaAffectedNaks = new Set();
    vedhaHits.forEach(function(v){
        if(v.from_nak) vedhaAffectedNaks.add(v.from_nak);
        if(v.to_entity) vedhaAffectedNaks.add(v.to_entity);
        // Also add the transit planet's nakshatra
        if(v.planet){
            var tp = transitPlanetsArr.find(function(t){ return t.planet === v.planet; });
            if(tp && tp.nakshatra) vedhaAffectedNaks.add(tp.nakshatra);
        }
    });

    /* ── Fuzzy nakshatra match for vedha set ──────────────────── */
    var NAK_FULL_NAMES = {
        'P.Bhadrapada':'Purva Bhadrapada','U.Bhadrapada':'Uttara Bhadrapada',
        'P.Phalguni':'Purva Phalguni','U.Phalguni':'Uttara Phalguni',
        'P.Ashadha':'Purva Ashadha','U.Ashadha':'Uttara Ashadha',
        'Mrigashira':'Mrigashira','Krittika':'Krittika','Rohini':'Rohini',
        'Ardra':'Ardra','Punarvasu':'Punarvasu','Pushya':'Pushya','Ashlesha':'Ashlesha',
        'Magha':'Magha','Hasta':'Hasta','Chitra':'Chitra','Swati':'Swati','Vishakha':'Vishakha',
        'Anuradha':'Anuradha','Jyeshtha':'Jyeshtha','Mula':'Mula','Abhijit':'Abhijit',
        'Shravana':'Shravana','Dhanishtha':'Dhanishtha','Shatabhisha':'Shatabhisha',
        'Revati':'Revati','Ashwini':'Ashwini','Bharani':'Bharani'
    };
    function isNakVedhaAffected(shortName){
        if(vedhaAffectedNaks.has(shortName)) return true;
        var full = NAK_FULL_NAMES[shortName];
        if(full && vedhaAffectedNaks.has(full)) return true;
        // Also try fuzzy: strip dots/spaces
        var clean = shortName.replace(/[\s.]+/g,'').toLowerCase();
        var found = false;
        vedhaAffectedNaks.forEach(function(n){
            if(n.replace(/[\s.]+/g,'').toLowerCase() === clean) found = true;
        });
        return found;
    }

    /* ── Build info strip HTML for a list of nakshatras ──────── */
    /* Kansal-style with GRID ALIGNMENT:
       - Spacer cells/rows for corner positions (grid cols 0,8 / rows 0,8)
       - Each nak's 4 padas align exactly with its grid cell
       Horizontal: 1 spacer col + 7×4 pada cols + 1 spacer col = matches 9 grid cols
       Vertical:   1 spacer row + 7×4 pada rows + 1 spacer row = matches 9 grid rows */
    function buildInfoStrip(nakList, orientation, side){
        var isVert = orientation === 'vertical';
        var isLeft = side === 'left';

        if(isVert){
            /* ── Vertical strips — aligned with grid rows 1-7 ───── */
            /* Each nak → 4 sub-rows. Spacer rows at top/bottom for corner rows. */
            var numCols = isLeft ? 3 : 3; /* Nak | T# | Pada  OR  Pada | T# | Nak */
            var html = '<table class="sbc-strip-vtable">';

            /* Top spacer row — matches grid row 0 (corner) */
            html += '<tr class="sbc-vstrip-spacer"><td colspan="'+numCols+'" style="height:calc(100%/9)"></td></tr>';

            /* 7 nakshatras × 4 sub-rows each */
            nakList.forEach(function(nak){
                var navInfo = getNavataraFor(nak);
                var taraNum = navInfo ? (navInfo.tara_number || '—') : '—';
                var taraName = navInfo ? (navInfo.tara || '') : '';
                var quality = navInfo ? (navInfo.quality || 'neutral') : 'neutral';
                var qColor = quality === 'auspicious' ? '#22aa22' : quality === 'inauspicious' ? '#dd3333' : '#aa8800';
                var shortNak = nak.length > 9 ? nak.slice(0,8)+'.' : nak;
                var isVedha = isNakVedhaAffected(nak);
                var taraSign = quality === 'auspicious' ? '+' : quality === 'inauspicious' ? '-' : '';
                var padaSounds = PADA_SOUNDS[nak] || PADA_SOUNDS[NAK_FULL_NAMES[nak]] || ['1','2','3','4'];
                var vedCls = isVedha ? ' sbc-sv-vedha' : '';

                for(var p = 0; p < 4; p++){
                    var pCls = isVedha ? ' sbc-pada-hit' : '';
                    html += '<tr class="sbc-sv-subrow'+vedCls+'">';
                    if(isLeft){
                        if(p === 0){
                            html += '<td class="sbc-sv-nak" rowspan="4" title="'+nak+'">'+shortNak+'</td>';
                            html += '<td class="sbc-sv-tara" rowspan="4" style="color:'+qColor+'" title="'+taraName+'">'+taraNum+taraSign+'</td>';
                        }
                        html += '<td class="sbc-sv-pada'+pCls+'" title="Pada '+(p+1)+'">'+padaSounds[p]+'</td>';
                    } else {
                        html += '<td class="sbc-sv-pada'+pCls+'" title="Pada '+(p+1)+'">'+padaSounds[p]+'</td>';
                        if(p === 0){
                            html += '<td class="sbc-sv-tara" rowspan="4" style="color:'+qColor+'" title="'+taraName+'">'+taraNum+taraSign+'</td>';
                            html += '<td class="sbc-sv-nak" rowspan="4" title="'+nak+'">'+shortNak+'</td>';
                        }
                    }
                    html += '</tr>';
                }
            });

            /* Bottom spacer row — matches grid row 8 (corner) */
            html += '<tr class="sbc-vstrip-spacer"><td colspan="'+numCols+'" style="height:calc(100%/9)"></td></tr>';

            html += '</table>';
            return html;
        }

        /* ── Horizontal strips — aligned with grid cols 1-7 ───── */
        /* Layout: 1 spacer col (for corner col 0) + 7×4 pada cols + 1 spacer col (corner col 8)
           Total: 30 sub-cols. Spacer = 4/30 width, each pada = 1/30 width → alignment matches. */
        var html = '<table class="sbc-strip-table sbc-strip-subcol">';

        /* Colgroup for precise widths:
           - 1 spacer col = 1/9 of width
           - 28 pada cols = 7/9 of width (each = 1/36)
           - 1 spacer col = 1/9 of width */
        html += '<colgroup>';
        html += '<col class="sbc-sh-spacer-col">';
        for(var i = 0; i < 28; i++) html += '<col class="sbc-sh-pada-col">';
        html += '<col class="sbc-sh-spacer-col">';
        html += '</colgroup>';

        /* Nak header row */
        html += '<tr>';
        html += '<td class="sbc-sh-corner" rowspan="4"></td>';
        nakList.forEach(function(nak){
            var shortNak = nak.length > 9 ? nak.slice(0,8)+'.' : nak;
            html += '<td class="sbc-sh-hdr sbc-sh-nak" colspan="4" title="'+nak+'">'+shortNak+'</td>';
        });
        html += '<td class="sbc-sh-corner" rowspan="4"></td>';
        html += '</tr>';

        /* Tara# row */
        html += '<tr>';
        nakList.forEach(function(nak){
            var navInfo = getNavataraFor(nak);
            var taraNum = navInfo ? (navInfo.tara_number || '—') : '—';
            var quality = navInfo ? (navInfo.quality || 'neutral') : 'neutral';
            var qColor = quality === 'auspicious' ? '#22aa22' : quality === 'inauspicious' ? '#dd3333' : '#aa8800';
            var taraName = navInfo ? (navInfo.tara || '') : '';
            var taraSign = quality === 'auspicious' ? '+' : quality === 'inauspicious' ? '-' : '';
            html += '<td class="sbc-sh-cell sbc-sh-tara" colspan="4" style="color:'+qColor+'" title="'+taraName+'">'+taraNum+taraSign+'</td>';
        });
        html += '</tr>';

        /* Pada sound row */
        html += '<tr>';
        nakList.forEach(function(nak){
            var isVedha = isNakVedhaAffected(nak);
            var padaSounds = PADA_SOUNDS[nak] || PADA_SOUNDS[NAK_FULL_NAMES[nak]] || ['1','2','3','4'];
            for(var p = 0; p < 4; p++){
                var padaCls = isVedha ? ' sbc-pada-hit' : '';
                html += '<td class="sbc-sh-cell sbc-sh-pada'+padaCls+'" title="'+nak+' Pada '+(p+1)+'">'+padaSounds[p]+'</td>';
            }
        });
        html += '</tr>';

        /* Pada number row */
        html += '<tr>';
        nakList.forEach(function(nak){
            var isVedha = isNakVedhaAffected(nak);
            for(var p = 1; p <= 4; p++){
                var padaCls = isVedha ? ' sbc-pada-hit' : '';
                html += '<td class="sbc-sh-cell sbc-sh-padnum'+padaCls+'" title="Pada '+p+'">'+p+'</td>';
            }
        });
        html += '</tr>';

        html += '</table>';
        return html;
    }

    const sigColor = mkt.color || '#d4a843';

    /* ══════════════════════════════════════════════════════════
       Render the entire SBC section (Parashara's Light 9.0 style)
       ══════════════════════════════════════════════════════════ */
    resultEl.innerHTML = `
        <style>
            /* ── Toggle / Options Bar ─────────────────────────── */
            .sbc-options-panel{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-bottom:16px;padding:10px 12px;background:rgba(26,26,46,0.6);border:1px solid rgba(212,168,67,0.3);border-radius:6px}
            .sbc-opt-label{display:flex;align-items:center;gap:4px;font-size:0.78rem;color:#c8b880;cursor:pointer;user-select:none;padding:3px 8px;border-radius:4px;transition:all .2s}
            .sbc-opt-label:hover{background:rgba(212,168,67,0.12)}
            .sbc-opt-label input[type=checkbox]{accent-color:#d4a843;width:14px;height:14px;cursor:pointer}

            /* ── Grid Layout Container ────────────────────────── */
            .sbc-master-wrap{max-width:860px;margin:0 auto}
            .sbc-chart-area{display:grid;grid-template-columns:auto 1fr auto;grid-template-rows:auto 1fr auto;gap:0}

            /* ── Info Strips ──────────────────────────────────── */
            .sbc-strip-top,.sbc-strip-bottom{grid-column:2/3}
            .sbc-strip-left{grid-column:1/2;grid-row:2/3;display:flex;align-items:stretch}
            .sbc-strip-right{grid-column:3/4;grid-row:2/3;display:flex;align-items:stretch}

            /* Vertical strip (left/right) — aligned with grid rows */
            .sbc-strip-vtable{border-collapse:collapse;border-spacing:0;width:auto;height:100%}
            .sbc-strip-vtable td{padding:0px 2px;border:1px solid rgba(212,168,67,0.12);vertical-align:middle;line-height:1.15}
            .sbc-vstrip-spacer td{border:none;background:transparent}
            .sbc-sv-nak{font-weight:600;color:#e0d8c0;font-size:0.55rem;white-space:nowrap;padding:1px 3px;text-align:center}
            .sbc-strip-left .sbc-sv-nak{text-align:right}
            .sbc-strip-right .sbc-sv-nak{text-align:left}
            .sbc-sv-tara{font-weight:700;font-size:0.55rem;text-align:center;padding:1px 2px}
            .sbc-sv-pada{font-size:0.52rem;color:#c8b880;background:rgba(255,255,255,0.02);text-align:center;padding:0px 2px;white-space:nowrap}
            .sbc-sv-subrow{}
            .sbc-sv-vedha td{background:rgba(255,0,0,0.06)}
            .sbc-pada-hit{background:rgba(255,50,50,0.2)!important;color:#ff6666!important;font-weight:700;border-color:rgba(255,60,60,0.3)!important}

            /* Horizontal strip (top/bottom) — aligned with grid cols via colgroup */
            .sbc-strip-table{width:100%;border-collapse:collapse;border-spacing:0;table-layout:fixed}
            .sbc-strip-table td{padding:2px 1px;text-align:center;font-size:0.55rem;border:1px solid rgba(212,168,67,0.1)}
            .sbc-sh-spacer-col{width:calc(100% / 9)}
            .sbc-sh-pada-col{width:calc(100% / 36)}
            .sbc-sh-corner{border:none;background:transparent;padding:0}
            .sbc-sh-hdr{background:rgba(26,26,46,0.9);color:#d4a843;font-weight:700;font-size:0.58rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:3px 1px}
            .sbc-sh-cell{color:#c8b880;font-size:0.52rem}
            .sbc-sh-tara{font-weight:700;font-size:0.55rem}
            .sbc-sh-pada{color:#c8b880;font-size:0.50rem;background:rgba(255,255,255,0.02);padding:1px 0}
            .sbc-sh-padnum{color:#888;font-size:0.46rem;background:rgba(212,168,67,0.05);padding:1px 0}

            /* ── Grid Wrapper ─────────────────────────────────── */
            .sbc-grid-wrap{position:relative;grid-column:2/3;grid-row:2/3}
            .sbc-grid{display:grid;grid-template-columns:repeat(9,1fr);gap:0;border:2px solid #8b7040;position:relative;z-index:1}

            /* ── Cells ────────────────────────────────────────── */
            .sbc-cell{border:1px solid rgba(0,0,0,0.18);padding:2px 1px;text-align:center;min-height:64px;min-width:64px;display:flex;flex-direction:column;justify-content:center;align-items:center;position:relative;transition:all .15s;cursor:default}
            .sbc-cell:hover{filter:brightness(1.08);z-index:5}
            .sbc-cell .cell-name{font-weight:700;line-height:1.12;word-break:break-word}
            .sbc-cell .cell-akshara{font-size:0.65rem;color:rgba(0,0,0,0.4);font-weight:600;position:absolute;top:1px;left:3px;pointer-events:none}
            .sbc-cell .planet-badges{display:flex;flex-wrap:wrap;gap:2px;justify-content:center;margin-top:2px}
            .sbc-cell .planet-badge{font-size:0.58rem;color:#fff;padding:1px 4px;font-weight:700;display:inline-block;line-height:1.3;letter-spacing:0.3px}
            .sbc-transit-click{cursor:pointer;transition:transform .15s,box-shadow .15s}
            .sbc-transit-click:hover{transform:scale(1.25);box-shadow:0 0 6px rgba(255,204,0,0.8)}
            .sbc-transit-click.sbc-selected{transform:scale(1.3);box-shadow:0 0 10px rgba(255,255,0,1);outline:2px solid #fff}
            .sbc-cell .latta-badge{position:absolute;top:1px;right:2px;width:14px;height:14px;background:#ff8c00;color:#fff;font-size:0.5rem;font-weight:900;line-height:14px;text-align:center;border-radius:2px;z-index:3;display:none}
            .sbc-cell.latta-active .latta-badge{display:block}
            .sbc-cell.vedha-hit{box-shadow:inset 0 0 0 2px #ff0000}
            .sbc-cell.navatara-on .navatara-stripe{display:block}
            .sbc-cell .navatara-stripe{position:absolute;bottom:0;left:0;right:0;height:5px;display:none;z-index:2;border-radius:0 0 1px 1px}

            /* ── SVG Vedha Overlay ─────────────────────────────── */
            .sbc-vedha-svg{position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:4}

            /* ── Legend ────────────────────────────────────────── */
            .sbc-legend{display:flex;gap:14px;justify-content:center;margin-top:14px;font-size:0.72rem;flex-wrap:wrap;color:var(--text-muted,#aaa)}
            .sbc-legend-dot{display:inline-block;width:13px;height:13px;vertical-align:middle;border-radius:2px;margin-right:3px;border:1px solid rgba(0,0,0,0.2)}

            /* ── Info Cards ────────────────────────────────────── */
            .sbc-info-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}
            @media(max-width:700px){.sbc-info-grid{grid-template-columns:1fr} .sbc-grid{min-width:520px}}
        </style>

        <!-- SBC Chakra Card -->
        <div class="card">
            <h2 style="text-align:center;margin-bottom:4px">Sarvatobhadra Chakra</h2>
            <div style="text-align:center;font-size:0.78rem;color:var(--text-muted);margin-bottom:12px">
                Moon: <strong>${(moonNak.nakshatra || moonNak)}</strong> | Janma: <strong>${data.janma_nakshatra || '—'}</strong>
            </div>

            <!-- Options Panel -->
            <div class="sbc-options-panel" id="sbc-options-panel">
                <label class="sbc-opt-label"><input type="checkbox" data-layer="natal" checked> Show natal planets</label>
                <label class="sbc-opt-label"><input type="checkbox" data-layer="transit" checked> Show transit planets</label>
                <label class="sbc-opt-label"><input type="checkbox" data-layer="vedha" checked> Show Vedha lines</label>
                <label class="sbc-opt-label"><input type="checkbox" data-layer="latta" checked> Show Latta</label>
                <label class="sbc-opt-label"><input type="checkbox" data-layer="navatara"> Show Navatara colors</label>
                <label class="sbc-opt-label"><input type="checkbox" data-layer="aksharas" checked> Show Devanagari</label>
                <label class="sbc-opt-label"><input type="checkbox" data-layer="tarabala" checked> Show Tarabala</label>
            </div>

            <div style="overflow-x:auto">
                <div class="sbc-master-wrap">
                    <div class="sbc-chart-area">
                        <!-- Top Info Strip -->
                        <div class="sbc-strip-top" id="sbc-strip-top"></div>
                        <!-- Left Info Strip -->
                        <div class="sbc-strip-left" id="sbc-strip-left"></div>
                        <!-- Main Grid -->
                        <div class="sbc-grid-wrap" id="sbc-grid-wrap">
                            <div class="sbc-grid" id="sbc-chakra-grid"></div>
                            <svg class="sbc-vedha-svg" id="sbc-vedha-svg"></svg>
                        </div>
                        <!-- Right Info Strip -->
                        <div class="sbc-strip-right" id="sbc-strip-right"></div>
                        <!-- Bottom Info Strip -->
                        <div class="sbc-strip-bottom" id="sbc-strip-bottom"></div>
                    </div>
                </div>

                <!-- Legend -->
                <div class="sbc-legend">
                    <span><span class="sbc-legend-dot" style="background:#d8c8f0"></span>Nakshatra</span>
                    <span><span class="sbc-legend-dot" style="background:#f5e6a3"></span>Rashi</span>
                    <span><span class="sbc-legend-dot" style="background:#a8e6a0"></span>Vara</span>
                    <span><span class="sbc-legend-dot" style="background:#ffe0b0"></span>Center</span>
                    <span><span class="sbc-legend-dot" style="background:#1a8c1a"></span>Benefic</span>
                    <span><span class="sbc-legend-dot" style="background:#cc1a1a"></span>Malefic</span>
                    <span><span class="sbc-legend-dot" style="background:#ff8c00"></span>Latta</span>
                </div>
            </div>
        </div>

        <!-- Market Signal Card -->
        <div class="signal-card" style="border-left-color:${sigColor}">
            <div class="signal-header">
                <div>
                    <h3 style="color:${sigColor}">${mkt.signal || 'SARVATOBHADRA'}</h3>
                    <div style="font-size:0.9rem;color:var(--text-muted)">${mkt.action || ''}</div>
                </div>
                <div class="signal-score">${sbc.sbc_score ?? mkt.score ?? 0}</div>
            </div>
            <div class="signal-details">
                <div class="detail-item"><strong>Moon Nakshatra:</strong> ${(moonNak.nakshatra || moonNak)} (Pada ${moonNak.pada || '—'}, Lord: ${moonNak.lord || '—'})</div>
                <div class="detail-item"><strong>Janma Nakshatra:</strong> ${data.janma_nakshatra || ''}</div>
                <div class="detail-item"><strong>Vedha Hits:</strong> ${vedhaHits.length}</div>
                <div class="detail-item"><strong>Active Lattas:</strong> ${lattaHits.length}</div>
            </div>
            ${mkt.warning_tips?.length ? '<div style="margin-top:8px">' + mkt.warning_tips.map(function(w){ return '<p style="color:var(--red);margin:4px 0">&#9888; '+w+'</p>'; }).join('') + '</div>' : ''}
        </div>

        <!-- Info Cards Grid -->
        <div class="sbc-info-grid">
            <!-- Six Bindus -->
            <div class="card">
                <h2>Six Personal Bindus</h2>
                <table class="data-table">
                    <thead><tr><th>Bindu</th><th>Nakshatra</th><th>Status</th></tr></thead>
                    <tbody>
                        ${Object.entries(sixBindus).map(function([key, val]){
                            var st = (binduAnalysis[key] && binduAnalysis[key].status) || '—';
                            var stColor = st === 'AFFLICTED' ? 'var(--red)' : st === 'PROTECTED' ? 'var(--green)' : 'var(--gold)';
                            return '<tr><td style="font-weight:600">'+key+'</td><td>'+(val && val.nakshatra ? val.nakshatra : val || '—')+'</td><td style="color:'+stColor+'">'+st+'</td></tr>';
                        }).join('')}
                    </tbody>
                </table>
            </div>

            <!-- Latta Analysis — All planets with full kick details -->
            <div class="card">
                <h2>Latta Analysis</h2>
                <p style="font-size:0.78rem;color:var(--text-muted);margin-bottom:8px">
                    Each planet kicks a specific nakshatra at a fixed offset. Retrograde reverses the kick direction.
                </p>
                <table class="data-table">
                    <thead><tr>
                        <th>Planet</th>
                        <th>Transiting</th>
                        <th>Dir</th>
                        <th>Kicks Nakshatra</th>
                        <th>Severity</th>
                        <th>Effect</th>
                        <th>NSE Impact</th>
                    </tr></thead>
                    <tbody>
                        ${(function(){
                            var pa = sbc.planet_analyses || [];
                            if(!pa.length) return '<tr><td colspan="7" style="color:var(--text-muted)">No planet data available</td></tr>';
                            return pa.map(function(p){
                                var lt = p.latta || {};
                                if(!lt.kicked_nakshatra) return '';
                                /* Check if this latta actually hits a bindu or inauspicious tara */
                                var hits = p.latta_hits || [];
                                var severity = hits.length ? hits[0].severity : 'LOW';
                                var binduHit = hits.length ? hits[0].bindu_type : '';
                                var taraHit = hits.length ? hits[0].tara : '';
                                var sevColor = severity === 'CRITICAL' ? '#ff3d00' : severity === 'HIGH' ? 'var(--red)' : severity === 'MODERATE' ? 'var(--gold)' : '#888';
                                var dirIcon = lt.direction === 'forward' ? '→' : '←';
                                var dirLabel = lt.direction === 'forward' ? 'Fwd ' + dirIcon : 'Bwd ' + dirIcon;
                                if(p.retrograde) dirLabel += ' (R)';
                                var kickLabel = lt.kicked_nakshatra;
                                if(binduHit) kickLabel += ' <span style="color:var(--red);font-weight:700">(' + binduHit + ')</span>';
                                else if(taraHit) kickLabel += ' <span style="color:var(--gold);font-size:0.75rem">(' + taraHit + ')</span>';
                                var nature = p.nature || 'malefic';
                                var planetColor = nature === 'benefic' ? 'var(--green)' : 'var(--red)';
                                return '<tr>' +
                                    '<td style="font-weight:600;color:' + planetColor + '">' + p.planet + '</td>' +
                                    '<td>' + (p.nakshatra || '—') + '</td>' +
                                    '<td style="font-family:monospace">' + dirLabel + '</td>' +
                                    '<td>' + kickLabel + '</td>' +
                                    '<td style="color:' + sevColor + ';font-weight:600">' + severity + '</td>' +
                                    '<td style="font-size:0.82rem">' + (lt.effect || LATTA_EFFECTS_UI[p.planet] || '—') + '</td>' +
                                    '<td style="font-size:0.78rem;color:var(--text-muted)">' + (lt.nse_impact || LATTA_NSE_UI[p.planet] || '—') + '</td>' +
                                '</tr>';
                            }).filter(Boolean).join('');
                        })()}
                    </tbody>
                </table>
                ${lattaHits.length ? '<div style="margin-top:8px;padding:6px 10px;background:rgba(255,60,0,0.08);border:1px solid rgba(255,60,0,0.2);border-radius:4px"><span style="color:var(--red);font-weight:700">⚠ Active Latta Hits: ' + lattaHits.length + '</span> — ' + lattaHits.map(function(l){ return '<b>' + l.planet + '</b> kicks <b>' + (l.kicked_nak || l.kicked_nakshatra) + '</b>' + (l.bindu_type ? ' (' + l.bindu_type + ' bindu)' : ''); }).join(', ') + '</div>' : ''}</div>
        </div>

        <!-- ═══ ADVANCED SBC v3.5 — Transit Planets with Graha Bala & Nature ═══ -->
        <div class="card">
            <h2>Transit Planets — Graha Bala & Nature</h2>
            <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">
                Dynamic nature per Khemraj Shlokas 55-56. Graha Bala = Sign strength × Motion multiplier (Shlokas 161-167).
            </p>
            <table class="data-table">
                <thead><tr>
                    <th>Planet</th><th>Nakshatra</th><th>Sign</th><th>Nature</th><th>Reason</th>
                    <th>Vedha Mode</th><th>Graha Bala</th><th>Sign Rel.</th><th>Motion</th>
                </tr></thead>
                <tbody>
                    ${(sbc.planet_analyses || []).map(function(p){
                        var gb = p.graha_bala || {};
                        var nd = p.nature_detail || {};
                        var natureColor = p.nature === 'benefic' ? 'var(--green)' : 'var(--red)';
                        var reason = nd.reason || 'inherent';
                        var reasonLabel = reason === 'ksheena_chandra' ? 'क्षीण Moon (waning)' :
                                          reason === 'krura_yukta_budha' ? 'क्रूरयुक्त (malefic conj.)' :
                                          reason === 'inherent' ? '—' : reason;
                        var balaVal = gb.graha_bala != null ? gb.graha_bala.toFixed(2) : '—';
                        var balaColor = gb.graha_bala >= 1.5 ? '#22cc44' : gb.graha_bala >= 0.75 ? 'var(--gold)' : gb.graha_bala >= 0.25 ? '#ff8c00' : 'var(--red)';
                        var modeLabel = p.vedha_mode === 'three_way' ? '3-Way (all dirs)' :
                                        p.vedha_mode === 'sthana' ? 'Sthana (max)' :
                                        p.vedha_mode === 'front' ? 'Front (nearest)' :
                                        p.vedha_mode === 'left' ? 'Left (fast)' :
                                        p.vedha_mode === 'right' ? 'Right (retro)' : p.vedha_mode || '—';
                        return '<tr>' +
                            '<td style="font-weight:700;color:' + natureColor + '">' + p.planet +
                                (p.retrograde ? ' <span style="color:var(--red);font-size:0.7rem">R</span>' : '') + '</td>' +
                            '<td>' + (p.nakshatra || '—') + '</td>' +
                            '<td>' + (p.sign || '—') + '</td>' +
                            '<td style="color:' + natureColor + ';font-weight:600;text-transform:uppercase">' + (p.nature || '—') + '</td>' +
                            '<td style="font-size:0.78rem">' + reasonLabel + '</td>' +
                            '<td style="font-size:0.78rem">' + modeLabel + '</td>' +
                            '<td style="font-weight:700;color:' + balaColor + '">' + balaVal + '</td>' +
                            '<td style="font-size:0.78rem">' + (gb.sign_relation || '—') + '</td>' +
                            '<td style="font-size:0.78rem">' + (gb.motion || '—') + '</td>' +
                        '</tr>';
                    }).join('')}
                </tbody>
            </table>
        </div>

        <!-- ═══ Vedha Analysis with Temporal States ═══ -->
        ${vedhaHits.length ? '<div class="card"><h2>Vedha Analysis — Temporal States</h2>' +
            '<p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">' +
            'Dagdha (दग्ध) = past/fading | Jwalita (ज्वलित) = present/active | Dhumita (धूमित) = future/building — Shlokas 103-106</p>' +
            '<table class="data-table"><thead><tr><th>Planet</th><th>From Nak</th><th>Vedha Entity</th><th>Direction</th><th>Mode</th><th>Nature</th><th>Temporal</th><th>Strength</th></tr></thead><tbody>' +
            vedhaHits.slice(0,25).map(function(v){
                var ts = v.temporal_state || {};
                var tsState = ts.state || '—';
                var tsHindi = ts.state_hindi || '';
                var tsColor = tsState === 'jwalita' ? '#ff3d00' : tsState === 'dhumita' ? 'var(--gold)' : tsState === 'dagdha' ? '#888' : '#555';
                var tsIcon = tsState === 'jwalita' ? '🔥' : tsState === 'dhumita' ? '💨' : tsState === 'dagdha' ? '⚫' : '';
                var natureColor = v.nature === 'papa_vedha' ? 'var(--red)' : 'var(--green)';
                var natureLabel = v.nature === 'papa_vedha' ? 'Papa (पाप)' : 'Shubha (शुभ)';
                var modeLabel = v.vedha_mode === 'three_way' ? '3-Way' : v.vedha_mode === 'front' ? 'Front' :
                                v.vedha_mode === 'left' ? 'Left' : v.vedha_mode === 'right' ? 'Right' :
                                v.vedha_mode === 'sthana' ? 'Sthana' : v.vedha_speed_type || '—';
                var mult = v.strength_multiplier != null ? v.strength_multiplier.toFixed(2) + 'x' : '—';
                return '<tr>' +
                    '<td style="font-weight:600">' + (v.planet || '—') + '</td>' +
                    '<td>' + (v.from_nak || '—') + '</td>' +
                    '<td>' + (v.to_entity || '—') + (v.bindu_type ? ' <span style="color:var(--red);font-weight:700">(' + v.bindu_type + ')</span>' : '') + '</td>' +
                    '<td>' + (v.vedha_direction || '—') + '</td>' +
                    '<td>' + modeLabel + '</td>' +
                    '<td style="color:' + natureColor + '">' + natureLabel + '</td>' +
                    '<td style="color:' + tsColor + ';font-weight:600">' + tsIcon + ' ' + tsState + (tsHindi ? ' (' + tsHindi + ')' : '') + '</td>' +
                    '<td style="font-weight:600">' + mult + '</td>' +
                '</tr>';
            }).join('') + '</tbody></table>' +
            (vedhaHits.length > 25 ? '<p style="color:var(--text-muted);margin-top:8px;font-size:0.8rem">Showing 25 of ' + vedhaHits.length + ' vedha hits</p>' : '') +
        '</div>' : ''}

        <!-- ═══ Ubhayato Vedha — Double-Sided Malefic Detection ═══ -->
        ${(function(){
            var uv = sbc.ubhayato_vedha || [];
            if(!uv.length) return '';
            return '<div class="card" style="border-left:3px solid var(--red)">' +
                '<h2 style="color:var(--red)">⚠ Ubhayato Vedha — Double-Sided Malefic</h2>' +
                '<p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">' +
                'Shloka 220: When 2+ malefic planets vedha the same entity from opposite sides → maximum destruction signal.</p>' +
                '<table class="data-table"><thead><tr><th>Entity</th><th>Malefic Planets</th><th>Directions</th><th>Type</th><th>Severity</th><th>Financial Signal</th></tr></thead><tbody>' +
                uv.map(function(u){
                    var sevColor = u.severity === 'EXTREME' ? '#ff3d00' : 'var(--red)';
                    var typeLabel = u.is_true_ubhayato ? 'Ubhayato (उभयतो)' : 'Multi-Malefic';
                    return '<tr>' +
                        '<td style="font-weight:700">' + u.entity + '</td>' +
                        '<td style="color:var(--red)">' + u.planets.join(', ') + '</td>' +
                        '<td>' + u.directions.join(', ') + '</td>' +
                        '<td style="font-weight:600">' + typeLabel + '</td>' +
                        '<td style="color:' + sevColor + ';font-weight:700;font-size:0.9rem">' + u.severity + '</td>' +
                        '<td style="font-size:0.78rem">' + (u.financial || '—') + '</td>' +
                    '</tr>';
                }).join('') + '</tbody></table></div>';
        })()}

        <!-- ═══ 8 Upagraha Sub-Planets ═══ -->
        ${(function(){
            var upas = sbc.upagrahas || [];
            var upaHits = sbc.upagraha_hits || [];
            if(!upas.length) return '';
            return '<div class="card">' +
                '<h2>8 Upagraha — Sub-Planets from Sun</h2>' +
                '<p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">' +
                'Shlokas 250-260: Shadow sub-planets calculated from Sun\'s nakshatra. All malefic — add affliction points.</p>' +
                '<table class="data-table"><thead><tr><th>Upagraha</th><th>Nakshatra</th><th>Offset</th><th>Effect</th><th>Financial</th><th>Bindu Hit</th></tr></thead><tbody>' +
                upas.map(function(u){
                    var hit = upaHits.find(function(h){ return h.upagraha === u.name; });
                    var hitLabel = hit ? '<span style="color:var(--red);font-weight:700">' + (hit.bindu_type || hit.tara || 'YES') + '</span>' : '<span style="color:#666">—</span>';
                    var rowStyle = hit ? 'background:rgba(255,0,0,0.05)' : '';
                    return '<tr style="' + rowStyle + '">' +
                        '<td style="font-weight:600;color:var(--gold)">' + u.name + '</td>' +
                        '<td>' + u.nakshatra + '</td>' +
                        '<td>' + u.offset_from_sun + ' from Sun</td>' +
                        '<td style="font-size:0.78rem">' + u.effect + '</td>' +
                        '<td style="font-size:0.78rem;color:var(--text-muted)">' + u.financial + '</td>' +
                        '<td>' + hitLabel + '</td>' +
                    '</tr>';
                }).join('') + '</tbody></table>' +
                (upaHits.length ? '<div style="margin-top:8px;padding:6px 10px;background:rgba(255,140,0,0.08);border:1px solid rgba(255,140,0,0.2);border-radius:4px">' +
                    '<span style="color:#ff8c00;font-weight:700">⚠ ' + upaHits.length + ' Upagraha hitting sensitive points</span></div>' : '') +
            '</div>';
        })()}

        <!-- ═══ Commodity & Sector Impact Map ═══ -->
        <div class="card">
            <h2>Commodity & Sector Impact</h2>
            <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">
                Shlokas 245-246: Malefic vedha → commodities expensive. Benefic vedha → commodities cheap. Per-planet sector mapping.
            </p>
            <table class="data-table">
                <thead><tr><th>Planet</th><th>Nature</th><th>Commodities</th><th>NSE Sectors</th><th>Impact</th></tr></thead>
                <tbody>
                    ${(sbc.planet_analyses || []).map(function(p){
                        var cm = p.commodity || {};
                        if(!cm.commodities) return '';
                        var natureColor = p.nature === 'benefic' ? 'var(--green)' : 'var(--red)';
                        var impact = p.nature === 'benefic' ? (cm.benefic_effect || '—') : (cm.malefic_effect || '—');
                        return '<tr>' +
                            '<td style="font-weight:600;color:' + natureColor + '">' + p.planet + '</td>' +
                            '<td style="color:' + natureColor + ';text-transform:uppercase;font-weight:600;font-size:0.78rem">' + (p.nature || '—') + '</td>' +
                            '<td style="font-size:0.78rem">' + (cm.commodities || []).join(', ') + '</td>' +
                            '<td style="font-size:0.78rem;color:var(--gold)">' + (cm.nse_sectors || []).join(', ') + '</td>' +
                            '<td style="font-size:0.78rem">' + impact + '</td>' +
                        '</tr>';
                    }).filter(Boolean).join('')}
                </tbody>
            </table>
        </div>
    `;

    /* ══════════════════════════════════════════════════════════
       Populate Info Strips (Tarabala / Nakshatra info around grid)
       ══════════════════════════════════════════════════════════ */
    var stripTop = document.getElementById('sbc-strip-top');
    var stripBot = document.getElementById('sbc-strip-bottom');
    var stripLeft = document.getElementById('sbc-strip-left');
    var stripRight = document.getElementById('sbc-strip-right');
    if(stripTop) stripTop.innerHTML = buildInfoStrip(TOP_NAK, 'horizontal', 'top');
    if(stripBot) stripBot.innerHTML = buildInfoStrip(BOT_NAK, 'horizontal', 'bottom');
    if(stripLeft) stripLeft.innerHTML = buildInfoStrip(LEFT_NAK, 'vertical', 'left');
    if(stripRight) stripRight.innerHTML = buildInfoStrip(RIGHT_NAK, 'vertical', 'right');

    /* ══════════════════════════════════════════════════════════
       Build the interactive 9x9 SBC Grid (Parashara's Light style)
       ══════════════════════════════════════════════════════════ */
    const gridEl = document.getElementById('sbc-chakra-grid');
    if (!gridEl || grid.length !== 9) return;

    for (let r = 0; r < 9; r++) {
        for (let c = 0; c < 9; c++) {
            const cell = grid[r][c];
            const entities = cell.entities || [];
            const mainEnt = entities.find(function(e){ return e.entity_type !== 'special'; }) || entities[0];
            const planets = entities.filter(function(e){ return e.entity_type === 'special'; });
            const type = mainEnt ? mainEnt.entity_type : 'empty';
            const name = (mainEnt ? mainEnt.name : '') || cell.label || '';
            const zone = cell.zone || '';
            const isCenter = (r === 4 && c === 4);

            /* Determine background: prefer zone, fall back to entity type */
            const bg = isCenter ? '#ffe0b0' : (ZONE_BG[zone] || TYPE_BG[type] || '#f8f4ee');
            const tc = isCenter ? '#8b4513' : (ZONE_TEXT[zone] || TYPE_TEXT[type] || '#333');

            const el = document.createElement('div');
            el.className = 'sbc-cell';
            el.dataset.row = r;
            el.dataset.col = c;
            el.style.background = bg;

            /* Vedha affliction highlight */
            if (afflictedSet.has(r+','+c)) {
                el.classList.add('vedha-hit');
            }

            /* Latta check (match by nakshatra name in this cell) */
            const hasLatta = (type === 'nakshatra' && lattaNakSet.has(name));
            if (hasLatta) el.classList.add('latta-active');

            /* Navatara stripe color */
            var navInfo = getNavataraFor(name);
            var navColor = '';
            if (navInfo) {
                var tara = navInfo.tara || navInfo.quality || '';
                navColor = NAVATARA_COLOR[tara] || NAVATARA_COLOR[tara.toLowerCase()] || '#888';
            }

            /* Shorten display name */
            var nameShort = shortenName(name);
            var fs = nameShort.length > 10 ? '0.55rem' : nameShort.length > 7 ? '0.6rem' : '0.68rem';

            /* Build cell inner HTML */
            var html = '';

            /* Devanagari svara/akshara — at diagonal positions, the vowel IS the main label */
            var aksharaKey = r+','+c;
            var isSvaraCell = SBC_SVARA_SET.has(aksharaKey);

            if (isSvaraCell && SBC_AKSHARAS[aksharaKey]) {
                /* Akshara cell: show Devanagari character as the prominent main label */
                var svara = SBC_AKSHARAS[aksharaKey];
                html += '<div class="cell-name sbc-svara-main" style="font-size:0.82rem;font-weight:700;color:#8b1a1a">'+svara+'</div>';
                /* Show underlying entity name below (nakshatra/corner etc) */
                var subEnt2 = entities.find(function(e){ return e.entity_type !== 'akshara' && e.entity_type !== 'special' && e.entity_type !== 'corner'; });
                var subName = subEnt2 ? shortenName(subEnt2.name) : '';
                if (subName && subName !== svara) {
                    html += '<div class="cell-sub" style="font-size:0.42rem;color:'+tc+';opacity:0.55">'+subName+'</div>';
                }
            } else if (type === 'rashi') {
                /* Rashi cell (3rd ring): show abbreviated name + Hindi name */
                var rashiEnt = entities.find(function(e){ return e.entity_type === 'rashi'; });
                var rashiShort = shortenName(name);
                var hindiName = (rashiEnt && rashiEnt.meta && rashiEnt.meta.hindi) || '';
                html += '<div class="cell-name" style="font-size:0.7rem;font-weight:700;color:#6b4e00">'+rashiShort+'</div>';
                if (hindiName) {
                    html += '<div class="cell-sub" style="font-size:0.55rem;color:#6b4e00;font-weight:600;opacity:0.85">'+hindiName+'</div>';
                }
            } else if (type === 'vara') {
                /* Vara cell: show weekday(s) + tithi group info */
                var varaEnts = entities.filter(function(e){ return e.entity_type === 'vara'; });
                var dayNames = varaEnts.map(function(e){ return e.name.substring(0,3); }).join(',');
                var groupLabel = (varaEnts.length && varaEnts[varaEnts.length-1].meta) ? varaEnts[varaEnts.length-1].meta.group_label || '' : '';
                html += '<div class="cell-name" style="font-size:0.62rem;font-weight:700;color:#1a5a10">'+dayNames+'</div>';
                if (groupLabel) {
                    html += '<div class="cell-sub" style="font-size:0.40rem;color:#1a5a10;opacity:0.7;line-height:1.1">'+groupLabel+'</div>';
                }
            } else {
                /* Other cells: show name as before */
                html += '<div class="cell-name" style="font-size:'+fs+';color:'+tc+'">'+nameShort+'</div>';
            }

            /* Navatara tara number beneath name (for nakshatras) */
            if (type === 'nakshatra' && navInfo) {
                html += '<div class="sbc-tara-num" style="font-size:0.48rem;color:'+tc+';opacity:0.7">'+(navInfo.tara || '')+(navInfo.tara_number ? ' ('+navInfo.tara_number+')' : '')+'</div>';
            }

            /* Planet badges - separate natal and transit */
            if (planets.length) {
                html += '<div class="planet-badges">';
                planets.forEach(function(p){
                    var isNatal = p.meta && p.meta.source === 'natal';
                    if (isNatal) {
                        var pColor = natalBadgeColor(p.name);
                        html += '<span class="planet-badge sbc-natal-planet" style="background:'+pColor+';border-radius:50%;padding:1px 3px;border:2px solid #7799cc;" title="'+p.name+' (natal)">'+abbr(p.name)+'</span> ';
                    } else {
                        var pColor = transitBadgeColor(p.name);
                        html += '<span class="planet-badge sbc-transit-planet sbc-transit-click" data-planet="'+p.name+'" style="background:'+pColor+';border-radius:2px;padding:1px 4px;cursor:pointer;border:2px solid #ffcc00;" title="'+p.name+' (transit) — click to show vedha">'+abbr(p.name)+'</span> ';
                    }
                });
                html += '</div>';
            }

            /* Latta badge */
            html += '<div class="latta-badge">L</div>';

            /* Navatara stripe */
            html += '<div class="navatara-stripe" style="background:'+(navColor||'transparent')+'"></div>';

            /* Tooltip */
            var tooltip = name;
            if(navInfo) tooltip += ' | Tara: '+(navInfo.tara||'')+(navInfo.tara_number?' (#'+navInfo.tara_number+')':'');
            if(hasLatta) tooltip += ' | LATTA';
            if(afflictedSet.has(r+','+c)) tooltip += ' | VEDHA';
            el.title = tooltip;

            el.innerHTML = html;
            gridEl.appendChild(el);
        }
    }

    /* ══════════════════════════════════════════════════════════
       Draw Vedha Lines (SVG overlay)
       ══════════════════════════════════════════════════════════ */
    function drawVedhaLines() {
        var svg = document.getElementById('sbc-vedha-svg');
        if (!svg) return;
        var wrap = document.getElementById('sbc-grid-wrap');
        var gEl = document.getElementById('sbc-chakra-grid');
        if (!gEl) return;

        requestAnimationFrame(function(){
            var gRect = gEl.getBoundingClientRect();
            var wRect = wrap.getBoundingClientRect();
            svg.setAttribute('viewBox', '0 0 ' + gRect.width + ' ' + gRect.height);
            svg.style.width = gRect.width + 'px';
            svg.style.height = gRect.height + 'px';
            svg.style.left = (gRect.left - wRect.left) + 'px';
            svg.style.top = (gRect.top - wRect.top) + 'px';
            svg.innerHTML = '';

            var cellW = gRect.width / 9;
            var cellH = gRect.height / 9;

            /* Flatten vedha_lines_all: each entry has {planet, nature, lines:[{from,to,type}]} */
            var flatLines = [];
            vedhaLinesAll.forEach(function(pl){
                var nature = pl.nature || 'malefic';
                var isPapa = (nature === 'malefic' || nature === 'papa');
                var lineStyle = pl.line_style || 'solid';
                (pl.lines || []).forEach(function(seg){
                    flatLines.push({ from: seg.from, to: seg.to, isPapa: isPapa, lineStyle: lineStyle, planet: pl.planet });
                });
            });

            /* Fallback: use vedha hits if vedha_lines_all was empty */
            if (!flatLines.length && vedhaHits.length) {
                vedhaHits.forEach(function(v){
                    if (v.from_pos && v.to_pos) {
                        flatLines.push({
                            from: v.from_pos, to: v.to_pos,
                            isPapa: (v.nature === 'papa_vedha'),
                            lineStyle: 'solid', planet: v.planet
                        });
                    }
                });
            }

            flatLines.forEach(function(vl){
                if (!vl.from || !vl.to) return;
                var x1 = vl.from[1] * cellW + cellW/2;
                var y1 = vl.from[0] * cellH + cellH/2;
                var x2 = vl.to[1] * cellW + cellW/2;
                var y2 = vl.to[0] * cellH + cellH/2;

                var color = vl.isPapa ? '#ff2222' : '#22cc44';
                var line = document.createElementNS('http://www.w3.org/2000/svg','line');
                line.setAttribute('x1', x1);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                line.setAttribute('stroke', color);
                line.setAttribute('stroke-width', vl.isPapa ? '2' : '1.5');
                line.setAttribute('stroke-opacity', '0.5');
                line.setAttribute('stroke-linecap', 'round');
                if(vl.lineStyle === 'dashed' || !vl.isPapa) line.setAttribute('stroke-dasharray', '6,3');
                if(vl.lineStyle === 'thick') line.setAttribute('stroke-width', '3');
                svg.appendChild(line);
            });
        });
    }
    drawVedhaLines();
    window.addEventListener('resize', drawVedhaLines);

    /* ══════════════════════════════════════════════════════════
       Toggle layer visibility (checkbox-based)
       ══════════════════════════════════════════════════════════ */
    document.querySelectorAll('#sbc-options-panel input[type=checkbox]').forEach(function(cb){
        cb.addEventListener('change', function(){
            var layer = cb.dataset.layer;
            var on = cb.checked;

            if (layer === 'vedha') {
                var svg = document.getElementById('sbc-vedha-svg');
                if (svg) svg.style.display = on ? '' : 'none';
                document.querySelectorAll('.sbc-cell.vedha-hit').forEach(function(c){
                    c.style.boxShadow = on ? 'inset 0 0 0 2px #ff0000' : 'none';
                });
            }
            if (layer === 'latta') {
                document.querySelectorAll('.sbc-cell.latta-active .latta-badge').forEach(function(b){
                    b.style.display = on ? 'block' : 'none';
                });
            }
            if (layer === 'navatara') {
                document.querySelectorAll('.sbc-cell').forEach(function(c){
                    if (on) c.classList.add('navatara-on');
                    else c.classList.remove('navatara-on');
                });
            }
            if (layer === 'transit') {
                document.querySelectorAll('.sbc-transit-planet').forEach(function(b){
                    b.style.display = on ? '' : 'none';
                });
            }
            if (layer === 'natal') {
                document.querySelectorAll('.sbc-natal-planet').forEach(function(b){
                    b.style.display = on ? '' : 'none';
                });
            }
            if (layer === 'aksharas') {
                document.querySelectorAll('.sbc-akshara-layer').forEach(function(a){
                    a.style.display = on ? '' : 'none';
                });
            }
            if (layer === 'tarabala') {
                document.querySelectorAll('.sbc-tara-num').forEach(function(t){
                    t.style.display = on ? '' : 'none';
                });
                /* Toggle info strip VISIBILITY (not display) to keep layout stable.
                   Using visibility:hidden preserves the element's space in the CSS Grid,
                   so the main grid + vedha label don't shift position. */
                ['sbc-strip-top','sbc-strip-bottom','sbc-strip-left','sbc-strip-right'].forEach(function(id){
                    var el = document.getElementById(id);
                    if(el) {
                        el.style.visibility = on ? '' : 'hidden';
                        el.style.opacity = on ? '1' : '0';
                        el.style.pointerEvents = on ? '' : 'none';
                    }
                });
            }
        });
    });

    /* ══════════════════════════════════════════════════════════
       Transit planet click → show per-planet vedha lines
       ══════════════════════════════════════════════════════════ */
    var selectedTransitPlanet = null;

    function drawVedhaForPlanet(planetName) {
        var svg = document.getElementById('sbc-vedha-svg');
        if (!svg) return;
        var wrap = document.getElementById('sbc-grid-wrap');
        var gEl = document.getElementById('sbc-chakra-grid');
        if (!gEl) return;

        requestAnimationFrame(function(){
            var gRect = gEl.getBoundingClientRect();
            var wRect = wrap.getBoundingClientRect();
            svg.setAttribute('viewBox', '0 0 ' + gRect.width + ' ' + gRect.height);
            svg.style.width = gRect.width + 'px';
            svg.style.height = gRect.height + 'px';
            svg.style.left = (gRect.left - wRect.left) + 'px';
            svg.style.top = (gRect.top - wRect.top) + 'px';
            svg.innerHTML = '';

            var cellW = gRect.width / 9;
            var cellH = gRect.height / 9;

            /* Filter vedha lines for this planet only */
            var planetLines = [];
            var matchedPlanet = null;
            vedhaLinesAll.forEach(function(pl){
                if (pl.planet !== planetName) return;
                matchedPlanet = pl;
                var nature = pl.nature || 'malefic';
                var isPapa = (nature === 'malefic' || nature === 'papa');
                var lineStyle = pl.line_style || 'solid';
                (pl.lines || []).forEach(function(seg){
                    planetLines.push({ from: seg.from, to: seg.to, isPapa: isPapa, lineStyle: lineStyle });
                });
            });

            /* Fallback: filter vedha hits for this planet */
            if (!planetLines.length) {
                vedhaHits.forEach(function(v){
                    if (v.planet !== planetName) return;
                    if (v.from_pos && v.to_pos) {
                        planetLines.push({
                            from: v.from_pos, to: v.to_pos,
                            isPapa: (v.nature === 'papa_vedha'),
                            lineStyle: 'solid'
                        });
                    }
                });
            }

            planetLines.forEach(function(vl){
                if (!vl.from || !vl.to) return;
                var x1 = vl.from[1] * cellW + cellW/2;
                var y1 = vl.from[0] * cellH + cellH/2;
                var x2 = vl.to[1] * cellW + cellW/2;
                var y2 = vl.to[0] * cellH + cellH/2;

                var color = vl.isPapa ? '#ff2222' : '#22cc44';
                var sw = '2.5';
                if (vl.lineStyle === 'thick') sw = '3.5';
                if (vl.lineStyle === 'double') sw = '4';
                if (vl.lineStyle === 'dotted') sw = '2';
                var line = document.createElementNS('http://www.w3.org/2000/svg','line');
                line.setAttribute('x1', x1);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                line.setAttribute('stroke', color);
                line.setAttribute('stroke-width', sw);
                line.setAttribute('stroke-opacity', '0.75');
                line.setAttribute('stroke-linecap', 'round');
                if (vl.lineStyle === 'dashed') line.setAttribute('stroke-dasharray', '8,4');
                if (vl.lineStyle === 'double') line.setAttribute('stroke-dasharray', '2,3');
                if (vl.lineStyle === 'dotted') line.setAttribute('stroke-dasharray', '3,3');
                svg.appendChild(line);
            });

            /* Show vedha type label below the grid — anchored to sbc-master-wrap (NOT inside the CSS Grid) */
            var vedhaLabel = document.getElementById('sbc-vedha-label');
            if (!vedhaLabel) {
                vedhaLabel = document.createElement('div');
                vedhaLabel.id = 'sbc-vedha-label';
                vedhaLabel.style.cssText = 'text-align:center;padding:6px;font-size:12px;color:#d4a843;margin-top:4px;';
                /* Insert into sbc-master-wrap (parent of sbc-chart-area) so it stays stable when info strips toggle */
                var masterWrap = wrap.closest('.sbc-master-wrap');
                if (masterWrap) {
                    var chartArea = masterWrap.querySelector('.sbc-chart-area');
                    if (chartArea && chartArea.nextSibling) {
                        masterWrap.insertBefore(vedhaLabel, chartArea.nextSibling);
                    } else {
                        masterWrap.appendChild(vedhaLabel);
                    }
                } else {
                    /* Fallback: insert after the chart area parent */
                    wrap.parentNode.parentNode.appendChild(vedhaLabel);
                }
            }
            if (matchedPlanet) {
                var mode = matchedPlanet.vedha_mode || matchedPlanet.vedha_side || 'both';
                var sideLabel = mode === 'front' ? 'Front Vedha (सामने — nearest only)' :
                                mode === 'left'  ? 'Left Vedha (बाई — fast, full line)' :
                                mode === 'right' ? 'Right Vedha (दाहिनी — retro, full line)' :
                                mode === 'sthana' ? 'Sthana Vedha (stationary — full, max power)' :
                                matchedPlanet.vedha_type || '3-Way Vedha (all directions)';
                vedhaLabel.innerHTML = '<b>' + planetName + '</b>: ' + sideLabel +
                    ' | Lines: ' + matchedPlanet.lines.length +
                    ' | Strength: ' + (matchedPlanet.strength_multiplier || 1.0) + 'x';
            }

            /* Show vedha checkbox SVG if hidden */
            svg.style.display = '';
        });
    }

    document.getElementById('sbc-result').addEventListener('click', function(e) {
        var badge = e.target.closest('.sbc-transit-click');
        if (!badge) return;

        var planetName = badge.getAttribute('data-planet');
        if (!planetName) return;

        /* Deselect all first */
        document.querySelectorAll('.sbc-transit-click.sbc-selected').forEach(function(b){
            b.classList.remove('sbc-selected');
        });

        if (selectedTransitPlanet === planetName) {
            /* Clicking same planet again → deselect, restore all vedha lines */
            selectedTransitPlanet = null;
            var lbl = document.getElementById('sbc-vedha-label');
            if (lbl) lbl.innerHTML = '';
            drawVedhaLines();
        } else {
            /* Select this planet → draw only its vedha lines */
            selectedTransitPlanet = planetName;
            badge.classList.add('sbc-selected');
            drawVedhaForPlanet(planetName);
        }
    });

    /* ══════════════════════════════════════════════════════════
       Legend: Natal vs Transit badges
       ══════════════════════════════════════════════════════════ */
    var legendHtml = '<div style="margin-top:10px;padding:8px 12px;background:#1a1a2e;border:1px solid #333;border-radius:6px;display:flex;gap:18px;align-items:center;flex-wrap:wrap;font-size:12px;color:#ccc;">';
    legendHtml += '<span style="font-weight:600;color:#fff;">Legend:</span>';
    legendHtml += '<span><span style="display:inline-block;width:16px;height:16px;background:#3366aa;border-radius:50%;border:2px solid #7799cc;vertical-align:middle;margin-right:4px;"></span> Natal</span>';
    legendHtml += '<span><span style="display:inline-block;width:16px;height:16px;background:#dd4400;border-radius:2px;border:2px solid #ffcc00;vertical-align:middle;margin-right:4px;"></span> Transit <span style="color:#aaa;font-size:10px;">(click for vedha)</span></span>';
    legendHtml += '<span><span style="display:inline-block;width:16px;height:2px;background:#ff2222;vertical-align:middle;margin-right:4px;"></span> Papa Vedha</span>';
    legendHtml += '<span><span style="display:inline-block;width:16px;height:2px;background:#22cc44;vertical-align:middle;margin-right:4px;"></span> Shubha Vedha</span>';
    legendHtml += '<span style="color:#888;font-size:10px;">Lines: ── full | ╌╌ retro | ━━ fast | ··· front</span>';
    legendHtml += '</div>';
    var gridWrap = document.getElementById('sbc-grid-wrap');
    if (gridWrap) gridWrap.insertAdjacentHTML('afterend', legendHtml);
});

// ─── STRENGTH CALENDAR ───────────────────────────────────────
document.getElementById('strength-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('strength-result');
    const data = await apiCall('/strength-calendar', {
        name: document.getElementById('sc-name').value,
        date: ddmmToApi(document.getElementById('sc-date').value),
        time: document.getElementById('sc-time').value,
        place: document.getElementById('sc-place').value,
        calendar_type: document.getElementById('sc-calendar-type').value,
        days_ahead: parseInt(document.getElementById('sc-days-ahead').value) || 30,
    }, resultEl);
    if (!data) return;

    const calendar = data.calendar_data || {};

    if (calendar.daily_data) {
        resultEl.innerHTML = `
            <div class="card">
                <h2>Daily Strength Calendar (30 Days)</h2>
                <div class="calendar-grid">
                    ${calendar.daily_data.map(day => `
                        <div class="calendar-day" style="border: 1px solid var(--border); padding: 8px; margin: 2px;">
                            <div class="day-date" style="font-weight: bold;">${day.date}</div>
                            <div class="day-sav" style="color: ${day.sav >= 28 ? 'var(--green)' : day.sav >= 24 ? 'var(--gold)' : 'var(--red)'}">SAV: ${day.sav}</div>
                            <div class="day-strong" style="font-size: 0.8rem;">Strong: ${day.strong_planets?.join(', ') || 'None'}</div>
                            <div class="day-recommendation" style="font-size: 0.7rem; color: var(--text-muted);">${day.recommendation || ''}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else if (calendar.monthly_data) {
        resultEl.innerHTML = `
            <div class="card">
                <h2>Monthly Strength Summary</h2>
                <table class="data-table">
                    <thead><tr><th>Month</th><th>Avg SAV</th><th>Strong Planets</th><th>Recommendation</th></tr></thead>
                    <tbody>
                        ${calendar.monthly_data.map(month => `
                            <tr>
                                <td style="font-weight:600">${month.month}</td>
                                <td style="color:${month.avg_sav >= 28 ? 'var(--green)' : month.avg_sav >= 24 ? 'var(--gold)' : 'var(--red)'}">${month.avg_sav}</td>
                                <td>${month.strong_planets?.join(', ') || ''}</td>
                                <td style="font-size:0.8rem">${month.recommendation || ''}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } else if (calendar.yearly_data) {
        resultEl.innerHTML = `
            <div class="card">
                <h2>Yearly Planetary Strength Ranking</h2>
                <table class="data-table">
                    <thead><tr><th>Planet</th><th>Strength Score</th><th>Rating</th><th>Financial Impact</th></tr></thead>
                    <tbody>
                        ${calendar.yearly_data.map(planet => `
                            <tr>
                                <td style="font-weight:600">${planet.planet}</td>
                                <td style="color:${planet.strength_score >= 80 ? 'var(--green)' : planet.strength_score >= 60 ? 'var(--gold)' : 'var(--red)'}">${planet.strength_score}%</td>
                                <td>${planet.rating || ''}</td>
                                <td style="font-size:0.8rem">${planet.financial_impact || ''}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
});

// ─── KP SYSTEM ──────────────────────────────────────────────
document.getElementById('kp-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('kp-result');
    const body = {
        name: document.getElementById('kp-name').value,
        date: ddmmToApi(document.getElementById('kp-date').value),
        time: document.getElementById('kp-time').value,
        place: document.getElementById('kp-place').value,
        ayanamsa: 'krishnamurti',
    };
    const transitDate = document.getElementById('kp-transit-date').value;
    if (transitDate) body.transit_date = transitDate;

    const data = await apiCall('/kp', body, resultEl);
    if (!data) return;

    const kp = data.kp_analysis || {};
    const cuspal = kp.cuspal_sublords || [];
    const fin = kp.financial_analysis || {};
    const rp = kp.ruling_planets || {};

    resultEl.innerHTML = `
        <div class="signal-card">
            <h3 style="color:var(--gold-light)">KP Financial Analysis</h3>
            <p style="color:var(--text);margin:8px 0">${fin.overall_verdict || ''}</p>
            <div class="metric" style="display:inline-block;margin-top:8px"><div class="label">KP Score</div><div class="value gold">${(fin.avg_score * 100).toFixed(0)}%</div></div>
        </div>

        <div class="card">
            <h2>Cuspal Sub-Lords</h2>
            <table class="data-table">
                <thead><tr><th>House</th><th>Sign</th><th>Sign Lord</th><th>Star Lord</th><th>Sub Lord</th><th>Financial Relevance</th></tr></thead>
                <tbody>
                    ${cuspal.map(c => `
                        <tr style="${[2,5,7,10,11].includes(c.house)?'background:rgba(212,168,67,0.05)':''}">
                            <td style="font-weight:600;color:${[2,5,7,10,11].includes(c.house)?'var(--gold)':'var(--text)'}">${c.house}</td>
                            <td>${c.sign}</td>
                            <td>${c.sign_lord}</td>
                            <td>${c.star_lord}</td>
                            <td style="color:var(--gold)">${c.sub_lord}</td>
                            <td style="font-size:0.75rem;color:var(--text-muted)">${c.financial_relevance || ''}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>

        ${rp ? `
        <div class="card">
            <h2>Ruling Planets</h2>
            <div class="metrics-grid">
                <div class="metric"><div class="label">Day Lord</div><div class="value gold">${rp.day_lord || ''}</div></div>
                <div class="metric"><div class="label">Primary RPs</div><div class="value">${rp.ruling_planets?.primary?.join(', ') || '—'}</div></div>
                <div class="metric"><div class="label">Timing Signal</div><div class="value">${rp.financial_timing?.signal || ''}</div></div>
            </div>
        </div>` : ''}
    `;
});

// ─── DASHA ──────────────────────────────────────────────────
document.getElementById('dasha-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('dasha-result');
    const data = await apiCall('/dasha', {
        name: document.getElementById('d-name').value,
        date: ddmmToApi(document.getElementById('d-date').value),
        time: document.getElementById('d-time').value,
        place: document.getElementById('d-place').value,
    }, resultEl);
    if (!data) return;

    const dd = data.dasha_data || {};
    const current = data.current_dasha || {};
    const dashas = dd.dashas || [];

    resultEl.innerHTML = `
        <div class="signal-card">
            <h3 style="color:var(--gold-light)">Current Dasha Period</h3>
            <div class="metrics-grid">
                <div class="metric"><div class="label">Mahadasha</div><div class="value gold">${current.mahadasha || ''}</div><div class="label">${current.mahadasha_start || ''} → ${current.mahadasha_end || ''}</div></div>
                <div class="metric"><div class="label">Antardasha</div><div class="value">${current.antardasha || ''}</div><div class="label">${current.antardasha_start || ''} → ${current.antardasha_end || ''}</div></div>
                <div class="metric"><div class="label">Pratyantar</div><div class="value">${current.pratyantar || ''}</div></div>
                <div class="metric"><div class="label">Combined Score</div><div class="value ${current.combined_score > 0.5 ? 'green' : current.combined_score < 0 ? 'red' : 'gold'}">${current.combined_score?.toFixed(2) || ''}</div></div>
            </div>
            <p style="color:var(--text-muted);margin-top:12px;font-size:0.85rem">${current.market_outlook || ''}</p>
        </div>

        <div class="card">
            <h2>Mahadasha Timeline</h2>
            <table class="data-table">
                <thead><tr><th>Lord</th><th>Start</th><th>End</th><th>Years</th><th>Score</th><th>Sectors</th></tr></thead>
                <tbody>
                    ${dashas.map(d => {
                        const fin = d.financial || {};
                        return `<tr style="border-left:3px solid ${fin.color||'#888'}">
                            <td style="font-weight:600;color:${fin.color||'#fff'}">${d.mahadasha_lord}</td>
                            <td>${d.start_date}</td>
                            <td>${d.end_date}</td>
                            <td>${d.duration_years?.toFixed(1) || ''}</td>
                            <td style="color:${fin.score > 0.5 ? 'var(--green)' : fin.score < 0 ? 'var(--red)' : 'var(--text)'}">${fin.score?.toFixed(2) || ''}</td>
                            <td style="font-size:0.75rem">${fin.sectors?.join(', ') || ''}</td>
                        </tr>`;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
});

// ─── BACKTEST ───────────────────────────────────────────────
document.getElementById('backtest-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('backtest-result');
    const body = {
        ticker: document.getElementById('bt-ticker').value,
        start_date: document.getElementById('bt-start').value,
        signal_type: document.getElementById('bt-signal').value,
    };
    const endDate = document.getElementById('bt-end').value;
    if (endDate) body.end_date = endDate;

    const data = await apiCall('/backtest', body, resultEl);
    if (!data) return;

    const risk = data.risk_metrics || {};
    const assess = data.assessment || {};
    const monthly = data.monthly_summary || [];
    const dist = data.signal_distribution || {};

    const gradeColor = assess.grade === 'A' ? 'var(--green)' : assess.grade === 'B' ? '#8BC34A' : assess.grade === 'C' ? 'var(--orange)' : 'var(--red)';

    resultEl.innerHTML = `
        <div class="signal-card ${data.cumulative_return_pct > 0 ? 'bullish' : 'bearish'}">
            <div class="signal-header">
                <div>
                    <h3 style="color:var(--gold-light)">Backtest Results — ${data.type?.replace('backtest_', '').replace(/_/g, ' ').toUpperCase() || ''}</h3>
                    <p style="color:var(--text-muted)">${data.total_trading_days || 0} trading days analyzed</p>
                </div>
                <div class="score-display" style="color:${gradeColor}">${assess.grade || '?'}</div>
            </div>
            <p style="color:var(--text);margin-bottom:4px">${assess.verdict || ''}</p>

            <div class="metrics-grid">
                <div class="metric"><div class="label">Hit Ratio</div><div class="value ${data.hit_ratio_pct >= 55 ? 'green' : 'red'}">${data.hit_ratio_pct?.toFixed(1) || 0}%</div></div>
                <div class="metric"><div class="label">Cumulative Return</div><div class="value ${data.cumulative_return_pct > 0 ? 'green' : 'red'}">${data.cumulative_return_pct?.toFixed(2) || 0}%</div></div>
                <div class="metric"><div class="label">Sharpe Ratio</div><div class="value gold">${risk.sharpe_ratio?.toFixed(2) || '—'}</div></div>
                <div class="metric"><div class="label">Max Drawdown</div><div class="value red">-${risk.max_drawdown_pct?.toFixed(2) || 0}%</div></div>
                <div class="metric"><div class="label">Win/Loss</div><div class="value">${risk.win_loss_ratio?.toFixed(2) || '—'}</div></div>
                <div class="metric"><div class="label">Signals</div><div class="value">${data.signals_generated || 0}</div></div>
            </div>
        </div>

        ${monthly.length ? `
        <div class="card">
            <h2>Monthly Breakdown</h2>
            <table class="data-table">
                <thead><tr><th>Month</th><th>Days</th><th>Signals</th><th>Correct</th><th>Hit %</th><th>Return %</th></tr></thead>
                <tbody>
                    ${monthly.map(m => `
                        <tr>
                            <td style="font-weight:600">${m.month}</td>
                            <td>${m.trading_days}</td>
                            <td>${m.signals}</td>
                            <td>${m.correct}</td>
                            <td style="color:${m.hit_ratio >= 55 ? 'var(--green)' : m.hit_ratio < 45 ? 'var(--red)' : 'var(--text)'}">${m.hit_ratio}%</td>
                            <td style="color:${m.monthly_return_pct > 0 ? 'var(--green)' : 'var(--red)'}">${m.monthly_return_pct > 0 ? '+' : ''}${m.monthly_return_pct}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>` : ''}
    `;
});

// ─── Kaksha Ashtakavarga ────────────────────────────────────
document.getElementById('kaksha-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const mode = document.getElementById('kk-mode').value;
    const body = {
        name: document.getElementById('kk-name').value,
        date: ddmmToApi(document.getElementById('kk-date').value),
        time: document.getElementById('kk-time').value,
        place: document.getElementById('kk-place').value,
        ayanamsa: document.getElementById('kk-ayanamsa').value,
        transit_date: document.getElementById('kk-transit-date').value || undefined,
        transit_time: document.getElementById('kk-transit-time').value,
        transit_place: document.getElementById('kk-transit-place').value,
    };
    if (mode === 'timeline') body.days = parseInt(document.getElementById('kk-days').value) || 30;
    const endpoint = mode === 'daily' ? '/kaksha/daily' : '/kaksha/timeline';
    const el = document.getElementById('kaksha-result');
    const data = await apiCall(endpoint, body, el);
    if (!data) return;

    if (mode === 'daily') {
        const pw = data.planet_kaksha || [];
        const hourly = data.hourly_moon_kaksha || [];
        const best = data.best_windows || [];
        const avoid = data.avoid_windows || [];
        const ov = data.overall || {};
        const qColor = ov.score >= 0.25 ? 'var(--green)' : ov.score < -0.1 ? 'var(--red)' : 'var(--gold)';
        el.innerHTML = `
            <div class="card">
                <h2>Day Signal: <span style="color:${qColor}">${ov.signal || '—'}</span> (${ov.score})</h2>
                <p>Transit: ${data.transit?.date} — ${data.transit?.place}</p>
            </div>
            <div class="card">
                <h2>Planet Kaksha Windows</h2>
                <table class="data-table">
                    <thead><tr><th>Planet</th><th>Sign</th><th>Kaksha Lord</th><th>BAV</th><th>SAV</th><th>Bindu</th><th>Score</th><th>Quality</th></tr></thead>
                    <tbody>${pw.map(p => `
                        <tr>
                            <td style="font-weight:600">${p.planet}</td>
                            <td>${p.sign} ${p.degree_dms}</td>
                            <td>${p.kaksha_lord} (#${p.kaksha_index})</td>
                            <td>${p.bav_score}</td><td>${p.sav_score}</td>
                            <td style="color:${p.bindu ? 'var(--green)' : 'var(--red)'}">${p.bindu}</td>
                            <td style="color:${p.score >= 0.25 ? 'var(--green)' : p.score < -0.1 ? 'var(--red)' : 'var(--text)'}">${p.score}</td>
                            <td>${p.quality}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
            <div class="card">
                <h2>Best Moon Windows</h2>
                <div class="metrics-grid">${best.map(w => `
                    <div class="metric"><div class="label">${w.time}</div><div class="value green">${w.score} — ${w.kaksha_lord}</div></div>
                `).join('')}</div>
            </div>
            <div class="card">
                <h2>Avoid Windows</h2>
                <div class="metrics-grid">${avoid.map(w => `
                    <div class="metric"><div class="label">${w.time}</div><div class="value red">${w.score} — ${w.kaksha_lord}</div></div>
                `).join('')}</div>
            </div>
            <div class="card">
                <h2>Hourly Moon Kaksha</h2>
                <table class="data-table">
                    <thead><tr><th>Time</th><th>Sign</th><th>Kaksha Lord</th><th>Bindu</th><th>Score</th><th>Quality</th></tr></thead>
                    <tbody>${hourly.map(h => `
                        <tr>
                            <td style="font-weight:600">${h.time}</td>
                            <td>${h.sign} ${h.degree_dms}</td>
                            <td>${h.kaksha_lord}</td>
                            <td>${h.bindu}</td>
                            <td style="color:${h.score >= 0.25 ? 'var(--green)' : h.score < -0.1 ? 'var(--red)' : 'var(--text)'}">${h.score}</td>
                            <td>${h.quality}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } else {
        // Timeline mode
        const days = data.days || [];
        const bestD = data.best_days || [];
        const worstD = data.worst_days || [];
        el.innerHTML = `
            <div class="card">
                <h2>Kaksha Timeline — ${data.days_count} days from ${data.start_date}</h2>
                <div class="metrics-grid">
                    <div class="metric"><div class="label">Best Day</div><div class="value green">${bestD[0]?.date || '—'} (${bestD[0]?.score || '—'})</div></div>
                    <div class="metric"><div class="label">Worst Day</div><div class="value red">${worstD[0]?.date || '—'} (${worstD[0]?.score || '—'})</div></div>
                </div>
            </div>
            <div class="card">
                <h2>Daily Scores</h2>
                <table class="data-table">
                    <thead><tr><th>Date</th><th>Day</th><th>Score</th><th>Signal</th><th>Best Planet</th><th>Weakest</th><th>Moon Kaksha</th></tr></thead>
                    <tbody>${days.map(d => `
                        <tr>
                            <td style="font-weight:600">${d.date}</td>
                            <td>${d.weekday}</td>
                            <td style="color:${d.score >= 0.25 ? 'var(--green)' : d.score < -0.1 ? 'var(--red)' : 'var(--text)'}">${d.score}</td>
                            <td>${d.signal}</td>
                            <td>${d.best_planet}</td>
                            <td>${d.weakest_planet}</td>
                            <td>${d.moon_kaksha?.kaksha_lord || '—'} (${d.moon_kaksha?.quality || '—'})</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
});

// ─── SBC Daily Signal ───────────────────────────────────────
document.getElementById('sbc-signal-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const body = {
        name: document.getElementById('ss-name').value,
        date: ddmmToApi(document.getElementById('ss-date').value),
        time: document.getElementById('ss-time').value,
        place: document.getElementById('ss-place').value,
        ayanamsa: document.getElementById('ss-ayanamsa').value,
        transit_date: document.getElementById('ss-transit-date').value || undefined,
        transit_time: document.getElementById('ss-transit-time').value,
        transit_place: document.getElementById('ss-transit-place').value,
    };
    const el = document.getElementById('sbc-signal-result');
    const data = await apiCall('/sbc/daily-signal', body, el);
    if (!data) return;

    const lattas = data.active_lattas || [];
    const vedhaNaks = data.active_vedha_naks || [];
    const mkt = data.market_signal || {};
    const signal = mkt.signal || '—';
    const action = mkt.action || '—';
    const score = data.overall_score ?? mkt.score ?? '—';
    const sigColor = mkt.color || (signal.includes('BULL') ? 'var(--green)' : signal.includes('BEAR') ? 'var(--red)' : 'var(--gold)');
    const warnings = mkt.warning_tips || [];

    el.innerHTML = `
        <div class="card">
            <h2>SBC Market Signal: <span style="color:${sigColor}">${signal}</span></h2>
            <div class="metrics-grid">
                <div class="metric"><div class="label">Janma Nakshatra</div><div class="value">${data.janma_nakshatra || '—'}</div></div>
                <div class="metric"><div class="label">Transit Date</div><div class="value">${data.transit_date || '—'}</div></div>
                <div class="metric"><div class="label">Overall Score</div><div class="value" style="color:${sigColor}">${score}</div></div>
                <div class="metric"><div class="label">Action</div><div class="value gold">${action}</div></div>
            </div>
            ${warnings.length ? `<div style="margin-top:12px">${warnings.map(w => `<p style="color:var(--red);margin:4px 0">⚠ ${w}</p>`).join('')}</div>` : ''}
        </div>
        ${lattas.length ? `
        <div class="card">
            <h2>Active Lattas</h2>
            <table class="data-table">
                <thead><tr><th>Planet</th><th>Kicks Nakshatra</th><th>Tara</th><th>Quality</th><th>Severity</th><th>Effect</th></tr></thead>
                <tbody>${lattas.map(l => `
                    <tr>
                        <td style="font-weight:600">${l.planet}</td>
                        <td>${l.kicked || '—'}</td>
                        <td>${l.tara || '—'}</td>
                        <td>${l.quality || '—'}</td>
                        <td style="color:${l.severity === 'HIGH' ? 'var(--red)' : 'var(--gold)'}">${l.severity || '—'}</td>
                        <td>${l.effect || '—'}</td>
                    </tr>`).join('')}
                </tbody>
            </table>
        </div>` : '<div class="card"><h2>No Active Lattas</h2><p>No significant Latta afflictions today.</p></div>'}
        ${vedhaNaks.length ? `
        <div class="card">
            <h2>Afflicted Vedha Nakshatras</h2>
            <p>${vedhaNaks.join(', ')}</p>
        </div>` : ''}
    `;
});
