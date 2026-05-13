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

// ─── Smart Time Input (accepts 24hr & AM/PM) ──────────────
// Parses any time string → "HH:MM" (24hr) for API
function parseTimeInput(val) {
    if (!val) return '';
    val = val.trim().toUpperCase();
    // Match patterns: "11:10 PM", "11:10PM", "23:10", "2310", "11 PM"
    var m = val.match(/^(\d{1,2})[:\.]?(\d{2})?\s*(AM|PM)?$/i);
    if (!m) return val; // can't parse, return as-is
    var h = parseInt(m[1], 10);
    var min = m[2] ? parseInt(m[2], 10) : 0;
    var ampm = m[3] ? m[3].toUpperCase() : null;
    if (ampm === 'PM' && h < 12) h += 12;
    if (ampm === 'AM' && h === 12) h = 0;
    return (h < 10 ? '0' : '') + h + ':' + (min < 10 ? '0' : '') + min;
}
// Auto-format on blur: normalize whatever the user typed to HH:MM
function setupTimeInput(input) {
    input.addEventListener('blur', function() {
        var parsed = parseTimeInput(this.value);
        if (parsed && parsed !== this.value) this.value = parsed;
    });
}
// Apply to all birth-time text inputs
document.querySelectorAll('.birth-time').forEach(setupTimeInput);
// Also apply to master time
var masterTimeEl = document.getElementById('master-time');
if (masterTimeEl) setupTimeInput(masterTimeEl);

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

// ─── ADVANCED MUHURTA ────────────────────────────────────────
var amPColor = function(n){
    var c = {Sun:'#FFA500',Moon:'#C0C0C0',Mars:'#FF4444',Mercury:'#00CED1',Jupiter:'#FFD700',Venus:'#FF69B4',Saturn:'#4169E1',Rahu:'#8B008B',Ketu:'#808080'};
    return c[n]||'#ccc';
};
document.getElementById('am-fetch').addEventListener('click', async function(){
    var resultEl = document.getElementById('am-result');
    resultEl.innerHTML = '<p style="color:var(--text-muted)">Analyzing muhurta...</p>';
    try {
        var amBody = {
            date: document.getElementById('am-date').value || body.date,
            time: document.getElementById('am-time').value || '09:15',
            place: document.getElementById('am-place').value || body.place,
            activity: document.getElementById('am-activity').value,
            birth_nakshatra: document.getElementById('am-birth-nak').value || null,
            birth_moon_sign: document.getElementById('am-birth-moon').value || null,
            ayanamsa: 'lahiri'
        };
        var resp = await fetch(API + '/muhurta/advanced', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(amBody)
        });
        if (!resp.ok) throw new Error('API error ' + resp.status);
        var d = await resp.json();
        var a = d.analysis || {};
        var fa = a.final_analysis || {};
        var ps = a.panchanga_shuddhi || {};
        var psum = d.panchanga_summary || {};
        var hora = d.hora || {};

        var h = '';

        /* ── Verdict Banner ── */
        var vBg = fa.verdict_type === 'excellent' ? 'rgba(0,200,100,0.15)' :
                  fa.verdict_type === 'good' ? 'rgba(0,200,100,0.10)' :
                  fa.verdict_type === 'mixed' ? 'rgba(255,193,7,0.12)' :
                  fa.verdict_type === 'bad' ? 'rgba(255,152,0,0.12)' : 'rgba(255,60,60,0.15)';
        h += '<div style="background:'+vBg+';border:2px solid '+(fa.color||'var(--gold)')+';border-radius:12px;padding:20px;text-align:center;margin-bottom:16px">';
        h += '<div style="font-size:0.82rem;color:var(--text-dim)">'+fa.activity+' ('+fa.activity_hi+')</div>';
        h += '<div style="font-size:0.78rem;color:var(--text-dim);margin-top:2px">'+d.date+' '+d.time+' | '+d.weekday+' ('+d.weekday_hi+')</div>';
        h += '<div style="font-size:2rem;font-weight:900;color:'+(fa.color||'var(--gold)')+';margin:8px 0;letter-spacing:1px">'+fa.verdict+'</div>';
        h += '<div style="font-size:0.88rem;color:var(--text-dim)">'+fa.verdict_hi+'</div>';
        h += '<div style="font-size:1.1rem;font-weight:700;color:'+(fa.color||'var(--gold)')+';margin-top:6px">Score: '+(fa.final_score*100).toFixed(0)+'%</div>';
        h += '</div>';

        /* ── Panchanga Summary ── */
        h += '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">';
        h += '<div class="metric"><div class="label">Tithi</div><div class="value gold">'+(psum.tithi||'')+'</div></div>';
        h += '<div class="metric"><div class="label">Nakshatra</div><div class="value gold">'+(psum.nakshatra||'')+'</div></div>';
        h += '<div class="metric"><div class="label">Yoga</div><div class="value gold">'+(psum.yoga||'')+'</div></div>';
        h += '<div class="metric"><div class="label">Karana</div><div class="value '+(psum.karana==='Vishti'?'red':'gold')+'">'+(psum.karana||'')+'</div></div>';
        h += '<div class="metric"><div class="label">Lagna</div><div class="value gold">'+(d.lagna_sign||'')+'</div></div>';
        h += '<div class="metric"><div class="label">Hora</div><div class="value" style="color:'+amPColor(hora.hora_lord)+'">'+(hora.hora_lord||'')+'</div><div class="label">'+(hora.good_for||'').substring(0,30)+'</div></div>';
        h += '</div>';

        /* ── Panchanga Shuddhi Table ── */
        h += '<h3 style="color:var(--gold-light);font-size:0.9rem;margin-top:14px">Panchanga Shuddhi — '+(ps.verdict||'')+'</h3>';
        h += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
        h += '<thead><tr><th>Element</th><th>Value</th><th>Nature</th><th>Pure?</th><th>Score</th><th>Note</th></tr></thead><tbody>';
        (ps.checks||[]).forEach(function(c){
            var rowBg = c.is_pure ? 'rgba(0,200,100,0.06)' : 'rgba(255,80,80,0.06)';
            h += '<tr style="background:'+rowBg+'">';
            h += '<td style="font-weight:700">'+c.element+' <span style="color:var(--text-dim);font-size:0.7rem">'+c.element_hi+'</span></td>';
            h += '<td style="font-weight:600">'+(c.value||'')+(c.value_hi?' ('+c.value_hi+')':'')+'</td>';
            h += '<td>'+(c.nature||'')+(c.nature_hi?' '+c.nature_hi:'')+'</td>';
            h += '<td style="font-weight:700;color:'+(c.is_pure?'var(--green)':'var(--red)')+'">'+( c.is_pure?'&#10003;':'&#10007;')+'</td>';
            h += '<td style="font-weight:600">'+(c.score>0?'+':'')+c.score.toFixed(1)+'</td>';
            h += '<td style="font-size:0.72rem;color:var(--text-dim)">'+c.note+'</td>';
            h += '</tr>';
        });
        h += '</tbody></table></div>';
        h += '<div style="font-size:0.82rem;margin-top:6px;font-weight:700;color:'+(ps.is_fully_pure?'var(--green)':'var(--gold)')+'">'+ps.pure_count+'/'+ps.total_elements+' Elements Pure — '+(ps.verdict_hi||'')+'</div>';

        /* ── Doshas ── */
        var doshas = a.doshas || [];
        if (doshas.length > 0) {
            h += '<h3 style="color:var(--red);font-size:0.9rem;margin-top:14px">&#9888; Doshas Detected ('+doshas.length+')</h3>';
            doshas.forEach(function(dd){
                var sevColor = dd.severity === 'Very High' ? '#ff3d00' : dd.severity === 'High' ? '#ff5722' : '#ff9800';
                h += '<div style="padding:8px 12px;background:rgba(255,60,60,0.08);border-left:3px solid '+sevColor+';border-radius:4px;margin-bottom:6px;font-size:0.82rem">';
                h += '<strong style="color:'+sevColor+'">'+dd.dosha+' ('+dd.dosha_hi+')</strong> <span style="color:var(--text-dim)">['+dd.severity+']</span>';
                h += '<div style="color:var(--text);margin-top:2px">'+dd.description+'</div>';
                h += '<div style="color:var(--text-dim);font-style:italic;font-size:0.75rem;margin-top:2px">Remedy: '+dd.remedy+'</div>';
                h += '</div>';
            });
        }

        /* ── Tara Bala ── */
        if (a.tara_bala) {
            var tb = a.tara_bala;
            var tbColor = tb.score >= 0 ? 'var(--green)' : 'var(--red)';
            h += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:14px">';
            h += '<div style="flex:1;min-width:240px;padding:12px;background:rgba(212,168,67,0.06);border:1px solid rgba(212,168,67,0.3);border-radius:8px">';
            h += '<div style="font-size:0.85rem;font-weight:700;color:var(--gold-light)">Tara Bala</div>';
            h += '<div style="font-size:1.3rem;font-weight:900;color:'+tbColor+';margin:4px 0">'+tb.tara_name+' ('+tb.tara_name_hi+')</div>';
            h += '<div style="font-size:0.78rem">Tara #'+tb.tara_number+' | Group '+tb.tara_group+' | '+tb.nature+'</div>';
            h += '<div style="font-size:0.78rem;color:var(--text-dim);margin-top:4px">'+tb.advice+'</div>';
            h += '<div style="font-size:0.72rem;color:var(--text-dim)">Birth: '+tb.birth_nakshatra+' → Transit: '+tb.transit_nakshatra+'</div>';
            h += '</div>';

            /* ── Chandra Bala ── */
            if (a.chandra_bala) {
                var cb = a.chandra_bala;
                var cbColor = cb.is_strong ? 'var(--green)' : 'var(--red)';
                h += '<div style="flex:1;min-width:240px;padding:12px;background:rgba(212,168,67,0.06);border:1px solid rgba(212,168,67,0.3);border-radius:8px">';
                h += '<div style="font-size:0.85rem;font-weight:700;color:var(--gold-light)">Chandra Bala</div>';
                h += '<div style="font-size:1.3rem;font-weight:900;color:'+cbColor+';margin:4px 0">'+cb.house_name+' ('+cb.house_name_hi+')</div>';
                h += '<div style="font-size:0.78rem">House '+cb.house_from_moon+' from Moon | '+cb.nature+'</div>';
                h += '<div style="font-size:0.78rem;color:var(--text-dim);margin-top:4px">'+cb.advice+'</div>';
                h += '<div style="font-size:0.72rem;color:var(--text-dim)">'+cb.birth_moon_sign+' → '+cb.transit_moon_sign+'</div>';
                h += '</div>';
            }
            h += '</div>';
        }

        /* ── Activity Fitness Table ── */
        h += '<h3 style="color:var(--gold-light);font-size:0.9rem;margin-top:14px">Activity Fitness: '+fa.activity+'</h3>';
        h += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
        h += '<thead><tr><th>Check</th><th>Value</th><th>Suitable?</th><th>Score</th></tr></thead><tbody>';
        if (a.nakshatra_fitness) {
            var nf = a.nakshatra_fitness;
            h += '<tr style="background:'+(nf.is_recommended?'rgba(0,200,100,0.06)':'rgba(255,80,80,0.06)')+'"><td>Nakshatra</td><td>'+nf.nakshatra+' ('+nf.classification+')</td>';
            h += '<td style="color:'+(nf.is_recommended?'var(--green)':'var(--red)')+'">'+( nf.is_recommended?'&#10003; Recommended':'&#10007; Not ideal')+'</td>';
            h += '<td>'+(nf.score>0?'+':'')+nf.score.toFixed(1)+'</td></tr>';
        }
        if (a.tithi_fitness) {
            var tf = a.tithi_fitness;
            h += '<tr style="background:'+(tf.is_recommended?'rgba(0,200,100,0.06)':'rgba(255,80,80,0.06)')+'"><td>Tithi</td><td>'+tf.paksha+' '+tf.tithi+'</td>';
            h += '<td style="color:'+(tf.is_recommended?'var(--green)':'var(--red)')+'">'+( tf.is_recommended?'&#10003; Suitable':'&#10007; Not ideal')+'</td>';
            h += '<td>'+(tf.score>0?'+':'')+tf.score.toFixed(1)+'</td></tr>';
        }
        if (a.vara_fitness) {
            var vf = a.vara_fitness;
            h += '<tr style="background:'+(vf.is_recommended?'rgba(0,200,100,0.06)':vf.is_avoided?'rgba(255,80,80,0.06)':'')+'"><td>Vara (Day)</td><td>'+vf.vara+'</td>';
            h += '<td style="color:'+(vf.is_recommended?'var(--green)':vf.is_avoided?'var(--red)':'var(--text)')+'">'+( vf.is_recommended?'&#10003; Good':vf.is_avoided?'&#10007; Avoid':'~ Neutral')+'</td>';
            h += '<td>'+(vf.score>0?'+':'')+vf.score.toFixed(1)+'</td></tr>';
        }
        if (a.lagna_shuddhi) {
            var ls = a.lagna_shuddhi;
            h += '<tr style="background:'+(ls.is_pure?'rgba(0,200,100,0.06)':'rgba(255,80,80,0.06)')+'"><td>Lagna</td><td>'+ls.lagna_sign+'</td>';
            h += '<td style="color:'+(ls.is_pure?'var(--green)':'var(--red)')+'">'+( ls.is_pure?'&#10003; Suitable':'&#10007; Not ideal')+'</td>';
            h += '<td>'+(ls.score>0?'+':'')+ls.score.toFixed(1)+'</td></tr>';
        }
        h += '</tbody></table></div>';

        /* ── Score Breakdown ── */
        h += '<h3 style="color:var(--gold-light);font-size:0.9rem;margin-top:14px">Score Breakdown</h3>';
        h += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px">';
        (fa.score_breakdown||[]).forEach(function(sb){
            var sbColor = sb.score >= 0.5 ? '#00c864' : sb.score >= 0 ? '#ffc107' : '#ff5722';
            h += '<div style="padding:6px 10px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:6px;font-size:0.75rem;min-width:120px">';
            h += '<div style="color:var(--text-dim)">'+sb.component+' ('+sb.weight+')</div>';
            h += '<div style="font-weight:700;color:'+sbColor+'">'+(sb.score>0?'+':'')+sb.score.toFixed(2)+'</div>';
            h += '</div>';
        });
        h += '</div>';

        /* ── Warnings & Positives ── */
        if (fa.positives && fa.positives.length) {
            h += '<div style="margin-top:8px">';
            fa.positives.forEach(function(p){
                h += '<div style="font-size:0.78rem;color:var(--green);margin-bottom:3px">&#10003; '+p+'</div>';
            });
            h += '</div>';
        }
        if (fa.warnings && fa.warnings.length) {
            h += '<div style="margin-top:6px">';
            fa.warnings.forEach(function(w){
                h += '<div style="font-size:0.78rem;color:var(--red);margin-bottom:3px">&#9888; '+w+'</div>';
            });
            h += '</div>';
        }

        /* ── Activity Notes ── */
        if (fa.activity_notes) {
            h += '<div style="margin-top:10px;padding:8px 12px;background:rgba(212,168,67,0.08);border-radius:6px;font-size:0.78rem;color:var(--text-dim);font-style:italic">';
            h += '<strong style="color:var(--gold)">Note:</strong> '+fa.activity_notes;
            h += '</div>';
        }

        resultEl.innerHTML = h;
    } catch(err) {
        resultEl.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
    }
});

// ─── AUTOMATED MUHURTA FINDER ──────────────────────────────
document.getElementById('mf-fetch').addEventListener('click', async () => {
    var resultEl = document.getElementById('mf-result');

    try {
        var data = await apiCall('/muhurta/find-dates', {
            activity: document.getElementById('mf-activity').value,
            start_date: document.getElementById('mf-date').value,
            person_name: document.getElementById('mf-name').value || '',
            months_ahead: parseInt(document.getElementById('mf-months').value),
            birth_nakshatra: document.getElementById('mf-nak').value || null,
            birth_moon_sign: document.getElementById('mf-moon').value || null,
            min_score: parseFloat(document.getElementById('mf-min-score').value),
            place: document.getElementById('mf-place').value,
        }, resultEl);

        if (!data) return; // apiCall already showed the error
        if (data.error) {
            resultEl.innerHTML = '<p style="color:var(--red)">Error: ' + data.error + '</p>';
            return;
        }

        var h = '';
        var pName = data.person_name ? data.person_name : '';
        var s = data.summary || {};

        // Header
        h += '<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);border:2px solid var(--gold);border-radius:12px;padding:20px;margin-bottom:16px">';
        h += '<h2 style="color:var(--gold);margin:0 0 8px">Muhurta Finder Results</h2>';
        if (pName) h += '<p style="color:var(--text);margin:2px 0"><strong>Person:</strong> ' + pName + '</p>';
        h += '<p style="color:var(--text);margin:2px 0"><strong>Activity:</strong> ' + (data.activity_name||data.activity) + ' (' + (data.activity_name_hi||'') + ')</p>';
        h += '<p style="color:var(--text);margin:2px 0"><strong>Range:</strong> ' + (data.search_range?data.search_range.start_date:'') + ' → ' + (data.search_range?data.search_range.end_date:'') + ' (' + (data.search_range?data.search_range.months:'') + ' months)</p>';
        if (data.birth_details && (data.birth_details.nakshatra || data.birth_details.moon_sign)) {
            h += '<p style="color:var(--text);margin:2px 0"><strong>Birth:</strong> ';
            if (data.birth_details.nakshatra) h += 'Nak: ' + data.birth_details.nakshatra + ' ';
            if (data.birth_details.moon_sign) h += 'Moon: ' + data.birth_details.moon_sign;
            h += '</p>';
        }
        h += '<p style="color:var(--text);margin:2px 0"><strong>Days Scanned:</strong> ' + (data.total_days_scanned||0) + '</p>';
        h += '</div>';

        // Summary chips
        h += '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px">';
        h += '<div style="background:#0a5c36;border-radius:8px;padding:10px 18px;text-align:center"><div style="font-size:1.6em;font-weight:700;color:#00ff88">' + (s.excellent||0) + '</div><div style="color:#aaa;font-size:0.8em">Excellent</div></div>';
        h += '<div style="background:#2a4a0a;border-radius:8px;padding:10px 18px;text-align:center"><div style="font-size:1.6em;font-weight:700;color:#88ff00">' + (s.good||0) + '</div><div style="color:#aaa;font-size:0.8em">Good</div></div>';
        h += '<div style="background:#4a3a0a;border-radius:8px;padding:10px 18px;text-align:center"><div style="font-size:1.6em;font-weight:700;color:#ffaa00">' + (s.average||0) + '</div><div style="color:#aaa;font-size:0.8em">Average</div></div>';
        h += '<div style="background:#4a0a0a;border-radius:8px;padding:10px 18px;text-align:center"><div style="font-size:1.6em;font-weight:700;color:#ff4444">' + (s.poor||0) + '</div><div style="color:#aaa;font-size:0.8em">Poor</div></div>';
        h += '</div>';

        // Store all dates globally for show more/less
        var allDates = data.all_dates || [];
        window._mfAllDates = allDates;
        window._mfShowAll = false;

        function renderMfDates(dates, showAll) {
            var out = '';
            if (dates.length === 0) {
                return '<p style="color:var(--text-dim)">No dates found matching the criteria. Try lowering the min score filter or extending the range.</p>';
            }
            var displayDates = showAll ? dates : dates.slice(0, 20);
            out += '<div style="display:grid;gap:12px">';
            for (var i = 0; i < displayDates.length; i++) {
                var d = displayDates[i];
                var sc = d.score || 0;
                var borderColor = sc >= 75 ? '#00ff88' : sc >= 50 ? '#88ff00' : sc >= 25 ? '#ffaa00' : '#ff4444';
                var bgGrad = sc >= 75 ? 'linear-gradient(135deg,#0a2e1a,#0a3e1a)' : sc >= 50 ? 'linear-gradient(135deg,#1a2e0a,#1a3e0a)' : sc >= 25 ? 'linear-gradient(135deg,#2e2a0a,#3e2a0a)' : 'linear-gradient(135deg,#2e0a0a,#3e0a0a)';
                var badge = sc >= 75 ? 'EXCELLENT' : sc >= 50 ? 'GOOD' : sc >= 25 ? 'AVERAGE' : 'AVOID';

                out += '<div style="background:' + bgGrad + ';border:1px solid ' + borderColor + ';border-radius:10px;padding:14px;position:relative">';
                out += '<div style="position:absolute;top:8px;right:10px;background:' + borderColor + ';color:#000;font-weight:700;font-size:0.75em;padding:2px 10px;border-radius:12px">#' + (i+1) + ' ' + badge + '</div>';

                out += '<div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">';
                out += '<div style="font-size:1.3em;font-weight:700;color:' + borderColor + '">' + d.date + '</div>';
                out += '<div style="color:var(--text-dim)">' + (d.weekday||'') + ' (' + (d.weekday_hi||'') + ')</div>';
                out += '<div style="background:rgba(255,255,255,0.1);border-radius:6px;padding:4px 10px;font-weight:700;color:' + borderColor + '">Score: ' + sc + '</div>';
                out += '</div>';

                out += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px;font-size:0.85em">';
                out += '<span style="background:rgba(255,215,0,0.15);padding:2px 8px;border-radius:4px;color:var(--gold)">' + (d.tithi||'') + '</span>';
                out += '<span style="background:rgba(0,206,209,0.15);padding:2px 8px;border-radius:4px;color:#00ced1">' + (d.nakshatra||'') + ' (' + (d.nakshatra_lord||'') + ')</span>';
                out += '<span style="background:rgba(255,105,180,0.15);padding:2px 8px;border-radius:4px;color:#ff69b4">Yoga: ' + (d.yoga||'') + '</span>';
                out += '<span style="background:rgba(100,149,237,0.15);padding:2px 8px;border-radius:4px;color:#6495ed">' + (d.karana||'') + '</span>';
                out += '<span style="background:rgba(255,165,0,0.15);padding:2px 8px;border-radius:4px;color:#ffa500">Moon: ' + (d.moon_sign||'') + '</span>';
                if (d.lagna_sign) out += '<span style="background:rgba(148,103,189,0.15);padding:2px 8px;border-radius:4px;color:#9467bd">Lagna: ' + d.lagna_sign + '</span>';
                out += '</div>';

                if (d.tara_bala || d.chandra_bala) {
                    out += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px;font-size:0.82em">';
                    if (d.tara_bala) {
                        var tb = d.tara_bala;
                        var tbColor = tb.is_good ? '#00ff88' : '#ff4444';
                        out += '<span style="color:' + tbColor + '">Tara: ' + (tb.tara_name||'') + ' (' + (tb.nature||'') + ')</span>';
                    }
                    if (d.chandra_bala) {
                        var cb = d.chandra_bala;
                        var cbColor = cb.is_strong ? '#00ff88' : '#ff4444';
                        out += '<span style="color:' + cbColor + '">Chandra Bala: House ' + (cb.house||'') + ' (' + (cb.strength||'') + ')</span>';
                    }
                    out += '</div>';
                }

                if (d.doshas && d.doshas.length > 0) {
                    out += '<div style="font-size:0.82em;margin-bottom:4px">';
                    for (var di = 0; di < d.doshas.length; di++) {
                        var ds = d.doshas[di];
                        var dsColor = ds.severity === 'high' ? '#ff4444' : ds.severity === 'medium' ? '#ffaa00' : '#ffcc00';
                        out += '<span style="color:' + dsColor + ';margin-right:8px">&#9888; ' + (ds.name||ds.dosha||'') + '</span>';
                    }
                    out += '</div>';
                }

                if (d.positives && d.positives.length > 0) {
                    out += '<div style="font-size:0.8em;color:#00ff88;margin-top:4px">';
                    for (var pi = 0; pi < Math.min(d.positives.length, 3); pi++) {
                        out += '&#10003; ' + d.positives[pi] + '  ';
                    }
                    if (d.positives.length > 3) out += '(+' + (d.positives.length-3) + ' more)';
                    out += '</div>';
                }
                if (d.warnings && d.warnings.length > 0) {
                    out += '<div style="font-size:0.8em;color:#ff6666;margin-top:2px">';
                    for (var wi = 0; wi < Math.min(d.warnings.length, 2); wi++) {
                        out += '&#10007; ' + d.warnings[wi] + '  ';
                    }
                    if (d.warnings.length > 2) out += '(+' + (d.warnings.length-2) + ' more)';
                    out += '</div>';
                }

                out += '</div>';
            }
            out += '</div>';

            // Show All / Show Top 20 toggle
            if (dates.length > 20) {
                out += '<div style="text-align:center;margin-top:14px">';
                if (showAll) {
                    out += '<button id="mf-toggle" class="btn-primary" style="font-size:0.9em;padding:8px 24px">Show Top 20 Only</button>';
                    out += '<p style="color:var(--text-dim);font-size:0.82em;margin-top:6px">Showing all ' + dates.length + ' dates</p>';
                } else {
                    out += '<button id="mf-toggle" class="btn-primary" style="font-size:0.9em;padding:8px 24px">Show All ' + dates.length + ' Dates</button>';
                    out += '<p style="color:var(--text-dim);font-size:0.82em;margin-top:6px">Showing top 20 of ' + dates.length + ' dates</p>';
                }
                out += '</div>';
            }
            return out;
        }

        h += renderMfDates(allDates, false);
        resultEl.innerHTML = h;

        // Attach toggle handler
        var toggleBtn = document.getElementById('mf-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                window._mfShowAll = !window._mfShowAll;
                // Re-render just the dates portion (keep header + summary)
                var headerEnd = resultEl.innerHTML.indexOf('<div style="display:grid;gap:12px">');
                if (headerEnd < 0) headerEnd = resultEl.innerHTML.indexOf('<p style="color:var(--text-dim)">No dates');
                var headerHtml = headerEnd > 0 ? resultEl.innerHTML.substring(0, headerEnd) : '';
                resultEl.innerHTML = headerHtml + renderMfDates(window._mfAllDates, window._mfShowAll);
                // Re-attach toggle
                var newToggle = document.getElementById('mf-toggle');
                if (newToggle) {
                    newToggle.addEventListener('click', arguments.callee);
                }
            });
        }
    } catch(err) {
        resultEl.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
    }
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
    const d1 = data.d1_chart || null;
    const d9 = data.d9_chart || null;

    /* ── Build Ascendant row for planet table ── */
    var ascNakRow = '';
    if (asc.longitude != null) {
        ascNakRow = `<tr style="background:rgba(212,168,67,0.08)">
            <td style="font-weight:700;color:#00FF88">Ascendant</td>
            <td>${asc.sign || ''}</td>
            <td>${asc.longitude?.toFixed(2) || ''}°</td>
            <td style="color:var(--gold)">—</td>
            <td>—</td>
            <td>—</td>
            <td>—</td>
        </tr>`;
    }

    /* ── D1 / D9 charts ── */
    var chartsHtml = '';
    if (d1 || d9) {
        chartsHtml = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px">';
        if (d1) {
            chartsHtml += '<div class="card"><h3 style="color:var(--gold-light);margin-bottom:8px">D-1 Rasi Chart</h3>';
            chartsHtml += '<div id="chart-d1-svg" style="display:flex;justify-content:center"></div></div>';
        }
        if (d9) {
            chartsHtml += '<div class="card"><h3 style="color:var(--gold-light);margin-bottom:8px">D-9 Navamsa Chart</h3>';
            chartsHtml += '<div id="chart-d9-svg" style="display:flex;justify-content:center"></div></div>';
        }
        chartsHtml += '</div>';
    }

    resultEl.innerHTML = `
        <div class="card">
            <h2>Birth Chart — ${data.name}</h2>
            <div class="metrics-grid">
                <div class="metric"><div class="label">Ascendant</div><div class="value gold">${asc.sign || ''}</div><div class="label">${asc.degree_in_sign?.toFixed(2) || ''}°</div></div>
            </div>
            <table class="data-table" style="margin-top:16px">
                <thead><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>Nakshatra</th><th>Pada</th><th>Sub-Lord</th><th>Retro</th></tr></thead>
                <tbody>
                    ${ascNakRow}
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
        ${chartsHtml}
    `;

    /* ── Render D1 / D9 SVGs ── */
    if (d1) {
        var d1El = document.getElementById('chart-d1-svg');
        if (d1El) d1El.innerHTML = drawNorthIndianSVG(d1, 420);
    }
    if (d9) {
        /* Normalize D9 data: backend uses navamsha_ascendant & d9_sign */
        var d9norm = {
            chart: d9.chart || 'D9 - Navamsha',
            ascendant: d9.ascendant || d9.navamsha_ascendant || '',
            planets: (d9.planets || []).map(function(p){
                return {
                    planet: p.planet,
                    sign: p.sign || p.d9_sign || '',
                    strength: p.strength || p.d9_strength || '',
                    retro: p.retro || false,
                };
            }),
        };
        var d9El = document.getElementById('chart-d9-svg');
        if (d9El) d9El.innerHTML = drawNorthIndianSVG(d9norm, 420);
    }
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

    /* ── Pada helpers for inner nakshatra boxes and line start points ── */
    function normalizeNakName(n){
        return (n || '').replace(/[\s.]+/g,'').toLowerCase();
    }
    function getPadaSounds(nak){
        return PADA_SOUNDS[nak] || PADA_SOUNDS[NAK_FULL_NAMES[nak]] || ['1','2','3','4'];
    }
    function getActivePadasForNak(nak){
        var clean = normalizeNakName(nak);
        var active = { transit:{}, natal:{} };
        (data.transit_planets || []).forEach(function(tp){
            if(normalizeNakName(tp.nakshatra) === clean && tp.pada){ active.transit[Number(tp.pada)] = tp.planet || true; }
        });
        (data.natal_planets || data.planets || []).forEach(function(np){
            if(normalizeNakName(np.nakshatra) === clean && np.pada){ active.natal[Number(np.pada)] = np.planet || true; }
        });
        return active;
    }
    function buildInnerPadaHtml(nak, row, col){
        var sounds = getPadaSounds(nak);
        var active = getActivePadasForNak(nak);
        /* Side columns (col 0 or 8) → vertical 2x2 layout; top/bottom rows → horizontal 4x1 */
        var isSideCol = (col === 0 || col === 8);
        var layoutCls = isSideCol ? 'sbc-inner-padas sbc-padas-vert' : 'sbc-inner-padas';
        var html = '<div class="'+layoutCls+'" title="Nakshatra padas">';
        for(var i=1;i<=4;i++){
            var cls = 'sbc-inner-pada';
            var label = sounds[i-1] || i;
            var tip = nak + ' Pada ' + i + ' (' + label + ')';
            if(active.transit[i]) { cls += ' active-transit'; tip += ' — transit ' + active.transit[i]; }
            else if(active.natal[i]) { cls += ' active-natal'; tip += ' — natal ' + active.natal[i]; }
            html += '<span class="'+cls+'" data-nak="'+nak+'" data-pada="'+i+'" title="'+tip+'"><span>'+label+'</span><span class="pno">P'+i+'</span></span>';
        }
        html += '</div>';
        return html;
    }
    function getTransitPadaForPlanet(planetName){
        var tp = (data.transit_planets || []).find(function(t){ return t.planet === planetName; });
        return tp && tp.pada ? Number(tp.pada) : null;
    }
    function pointInCellByPada(pos, pada, cellW, cellH){
        /* Use cell center so lines pass cleanly through grid corners */
        var r = pos[0], c = pos[1];
        return [c * cellW + cellW * 0.5, r * cellH + cellH * 0.5];
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
            .sbc-cell .sbc-inner-padas{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;width:92%;margin-top:2px;z-index:3;position:relative}
            .sbc-cell .sbc-inner-padas.sbc-padas-vert{grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(2,auto);width:85%}
            .sbc-cell .sbc-inner-pada{font-size:0.38rem;line-height:1.05;text-align:center;border:1px solid rgba(80,45,120,0.25);border-radius:2px;background:rgba(255,255,255,0.28);color:#4b2a78;font-weight:700;padding:1px 0;min-width:0}
            .sbc-cell .sbc-inner-pada .pno{display:block;font-size:0.34rem;opacity:0.75;color:#6b4e00}
            .sbc-cell .sbc-inner-pada.active-transit{background:rgba(255,204,0,0.55);border-color:#ffcc00;color:#8b1a1a;box-shadow:0 0 4px rgba(255,204,0,0.65)}
            .sbc-cell .sbc-inner-pada.active-natal{background:rgba(60,140,255,0.28);border-color:#4d8dff;color:#003c8f}

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
                <label class="sbc-opt-label"><input type="checkbox" data-layer="padas" checked> Show Pada inside Nakshatra boxes</label>
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
                        var cpvBadge = p.corner_pada_vedha ? ' <span title="Corner Pada Vedha (Shloka 52)" style="color:#ba68c8;font-size:0.65rem;font-weight:700">◈</span>' : '';
                        return '<tr>' +
                            '<td style="font-weight:700;color:' + natureColor + '">' + p.planet +
                                (p.retrograde ? ' <span style="color:var(--red);font-size:0.7rem">R</span>' : '') + cpvBadge + '</td>' +
                            '<td>' + (p.nakshatra || '—') + ' <span style="font-size:0.7rem;color:var(--text-dim)">P' + (p.pada||'?') + '</span></td>' +
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

        <!-- ═══ Vedha Count Analysis (Shlokas 107-109, 122-124) ═══ -->
        ${(function(){
            var vca = sbc.vedha_count_analysis || {};
            if (!vca.papa_vedha_count && !vca.shubha_vedha_count) return '';
            var papaEff = vca.papa_effect || {};
            var shubhaEff = vca.shubha_effect || {};
            var netColor = vca.net_assessment === 'EXTREME_DANGER' ? '#ff0000' :
                           vca.net_assessment === 'HIGH_DANGER' ? '#ff4444' :
                           vca.net_assessment === 'UNFAVORABLE' ? '#ff8c00' :
                           vca.net_assessment === 'HIGHLY_FAVORABLE' ? '#00e676' :
                           vca.net_assessment === 'FAVORABLE' ? '#66bb6a' : '#d4a843';
            return '<div class="card" style="border-color:' + netColor + '">' +
                '<h2>Vedha Count Analysis — Shlokas 107-109, 122-124</h2>' +
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">' +
                    '<div style="padding:10px;background:rgba(255,60,60,0.06);border:1px solid rgba(255,60,60,0.2);border-radius:6px">' +
                        '<div style="font-weight:700;color:var(--red);font-size:1.1rem">' + (vca.papa_vedha_count||0) + ' Papa Vedha</div>' +
                        (papaEff.effect ? '<div style="font-size:0.85rem;color:#ff8c00;font-weight:600">' + papaEff.effect + '</div>' : '') +
                        (papaEff.meaning ? '<div style="font-size:0.78rem;color:var(--text-muted)">' + papaEff.meaning + '</div>' : '') +
                        (papaEff.market ? '<div style="font-size:0.75rem;color:var(--red);margin-top:4px">' + papaEff.market + '</div>' : '') +
                        '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:4px">Planets: ' + (vca.papa_planets||[]).join(', ') + '</div>' +
                    '</div>' +
                    '<div style="padding:10px;background:rgba(40,200,60,0.06);border:1px solid rgba(40,200,60,0.2);border-radius:6px">' +
                        '<div style="font-weight:700;color:var(--green);font-size:1.1rem">' + (vca.shubha_vedha_count||0) + ' Shubha Vedha</div>' +
                        (shubhaEff.effect ? '<div style="font-size:0.85rem;color:#66bb6a;font-weight:600">' + shubhaEff.effect + '</div>' : '') +
                        (shubhaEff.meaning ? '<div style="font-size:0.78rem;color:var(--text-muted)">' + shubhaEff.meaning + '</div>' : '') +
                        (shubhaEff.market ? '<div style="font-size:0.75rem;color:var(--green);margin-top:4px">' + shubhaEff.market + '</div>' : '') +
                        '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:4px">Planets: ' + (vca.shubha_planets||[]).join(', ') + '</div>' +
                    '</div>' +
                '</div>' +
                '<div style="padding:8px 12px;background:rgba(212,168,67,0.08);border:1px solid rgba(212,168,67,0.2);border-radius:6px;text-align:center">' +
                    '<span style="font-weight:700;font-size:1rem;color:' + netColor + '">' + (vca.net_assessment||'').replace(/_/g,' ') + '</span>' +
                    '<div style="font-size:0.8rem;color:var(--text-muted)">' + (vca.net_description||'') + '</div>' +
                '</div>' +
            '</div>';
        })()}

        <!-- ═══ Moon Daily Vedha ═══ -->
        ${(function(){
            var mdv = sbc.moon_daily_vedha || {};
            if (!mdv.moon_nakshatra) return '';
            var outlookColor = mdv.daily_outlook && mdv.daily_outlook.indexOf('Positive') >= 0 ? 'var(--green)' :
                               mdv.daily_outlook && mdv.daily_outlook.indexOf('Negative') >= 0 ? 'var(--red)' : '#d4a843';
            var html = '<div class="card" style="border-color:' + outlookColor + '">' +
                '<h2>Moon Daily Vedha — ' + mdv.moon_nakshatra + ' (' + (mdv.moon_rashi||'') + ')</h2>' +
                '<div style="padding:8px 12px;background:rgba(212,168,67,0.08);border-radius:6px;margin-bottom:12px;text-align:center">' +
                    '<span style="font-weight:700;color:' + outlookColor + '">' + (mdv.daily_outlook||'') + '</span>' +
                    '<div style="font-size:0.78rem;color:var(--text-muted)">Shubha: ' + (mdv.shubha_vedha_on_moon||0) + ' | Papa: ' + (mdv.papa_vedha_on_moon||0) + '</div>' +
                '</div>';

            // Planets vedhing Moon
            var pvm = mdv.planets_vedhing_moon || [];
            if (pvm.length) {
                html += '<h3 style="font-size:0.85rem;margin-bottom:6px">Planets Casting Vedha on Moon</h3>' +
                '<table class="data-table"><thead><tr><th>Planet</th><th>From Nak</th><th>Type</th><th>Nature</th><th>Speed</th><th>Effect</th></tr></thead><tbody>';
                pvm.forEach(function(p){
                    var nc = p.is_benefic ? 'var(--green)' : 'var(--red)';
                    html += '<tr>' +
                        '<td style="font-weight:600;color:' + nc + '">' + p.planet + '</td>' +
                        '<td>' + p.from_nakshatra + '</td>' +
                        '<td style="font-size:0.78rem">' + p.vedha_type + '</td>' +
                        '<td style="color:' + nc + ';font-weight:600;text-transform:uppercase;font-size:0.78rem">' + p.nature + '</td>' +
                        '<td style="font-size:0.78rem">' + p.speed + (p.retrograde ? ' (R)' : '') + '</td>' +
                        '<td style="font-size:0.75rem">' + (p.effect||'') + '</td>' +
                    '</tr>';
                });
                html += '</tbody></table>';
            }

            // Moon's vedha targets
            var targets = mdv.vedha_targets || [];
            if (targets.length) {
                html += '<h3 style="font-size:0.85rem;margin:12px 0 6px">Moon Vedha Targets (' + targets.length + ' entities)</h3>' +
                '<div style="display:flex;flex-wrap:wrap;gap:4px">';
                targets.forEach(function(t){
                    var dirColor = t.direction === 'vama' ? '#66bb6a' : t.direction === 'dakshina' ? '#ef5350' : '#d4a843';
                    html += '<span style="padding:2px 8px;background:rgba(212,168,67,0.08);border:1px solid ' + dirColor + ';border-radius:4px;font-size:0.75rem">' +
                        t.entity + ' <span style="color:' + dirColor + ';font-size:0.68rem">(' + t.direction + ')</span></span>';
                });
                html += '</div>';
            }
            html += '</div>';
            return html;
        })()}

        <!-- ═══ Tatkalika Grahas — Shlokas 153-160 ═══ -->
        ${(function(){
            var tat = sbc.tatkalika_grahas || {};
            if (!tat.paksha && !tat.dina && !tat.kshana) return '';
            var html = '<div class="card">' +
                '<h2>Tatkalika Grahas — Temporal Planets (Shlokas 153-160)</h2>' +
                '<p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">' +
                'Paksha (fortnightly) from Sun, Dina (daily) from Moon, Kshana (momentary) from Sun. These temporal planets add vedha in their time periods.</p>';

            ['paksha', 'dina', 'kshana'].forEach(function(period){
                var planets = tat[period] || [];
                if (!planets.length) return;
                var label = period === 'paksha' ? 'Paksha (Fortnightly)' : period === 'dina' ? 'Dina (Daily)' : 'Kshana (Momentary)';
                var color = period === 'paksha' ? '#bb86fc' : period === 'dina' ? '#03dac6' : '#d4a843';
                html += '<h3 style="font-size:0.82rem;color:' + color + ';margin:10px 0 4px">' + label + '</h3>' +
                '<table class="data-table"><thead><tr><th>Planet</th><th>Nakshatra</th><th>Offset</th><th>From</th></tr></thead><tbody>';
                planets.forEach(function(p){
                    html += '<tr><td style="font-weight:600">' + p.planet + '</td>' +
                        '<td style="color:' + color + '">' + p.nakshatra + '</td>' +
                        '<td>' + p.offset + '</td>' +
                        '<td style="font-size:0.75rem;color:var(--text-dim)">' + p.from_nak + '</td></tr>';
                });
                html += '</tbody></table>';
            });
            html += '</div>';
            return html;
        })()}

        <!-- ═══ Planet Vedha Chooser ═══ -->
        <div class="card">
            <h2>Planet Vedha Detail — Choose Planet</h2>
            <p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">
                Select any transit planet to see all entities it vedhas, categorized by type and direction. For future Nifty implementation.
            </p>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">
                ${transitPlanets.map(function(tp){
                    var nc = BENEFICS.has(tp.planet) ? 'var(--green)' : 'var(--red)';
                    return '<button class="sbc-planet-vedha-btn" data-planet="' + tp.planet + '" style="padding:4px 12px;border:1px solid ' + nc + ';background:rgba(26,26,46,0.8);color:' + nc + ';border-radius:4px;cursor:pointer;font-weight:600;font-size:0.82rem">' +
                        tp.planet + ' <span style="font-size:0.7rem;opacity:0.7">(' + (tp.nakshatra||'').split(' ')[0] + ')</span></button>';
                }).join('')}
            </div>
            <div id="sbc-planet-vedha-result" style="min-height:40px"></div>
        </div>

        <!-- ═══ Vedha List — All 9 Planets + Lagna ═══ -->
        ${(function(){
            var vl = data.vedha_list;
            if (!vl || !vl.flat_list || !vl.flat_list.length) return '';
            var summary = vl.summary || {};
            var balColor = summary.balance === 'Strongly Negative' ? '#ff0000' :
                           summary.balance === 'Negative' ? '#ff4444' :
                           summary.balance === 'Neutral' ? '#d4a843' :
                           summary.balance === 'Positive' ? '#66bb6a' : '#00e676';

            var html = '<div class="card" style="border-left:3px solid ' + balColor + '">' +
                '<h2>Vedha List — Transit Planet Vedha to Nakshatras &amp; Planets</h2>' +
                '<p style="font-size:0.75rem;color:var(--text-muted);margin-bottom:8px">' +
                'Per Shlokas 19-47: Each transit planet vedhas specific nakshatras in Vama (Left), Dakshina (Right), Sammukha (Front) directions. ' +
                'Sun/Moon/Rahu/Ketu = 3-Way (all dirs). Others depend on speed.</p>';

            // Summary badges
            html += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px">' +
                '<div style="padding:8px 14px;background:rgba(255,60,60,0.06);border:1px solid rgba(255,60,60,0.2);border-radius:6px;text-align:center">' +
                    '<div style="font-weight:700;color:var(--red);font-size:1.1rem">' + (summary.papa_vedhas||0) + '</div>' +
                    '<div style="font-size:0.75rem;color:var(--text-muted)">Papa Vedhas</div></div>' +
                '<div style="padding:8px 14px;background:rgba(40,200,60,0.06);border:1px solid rgba(40,200,60,0.2);border-radius:6px;text-align:center">' +
                    '<div style="font-weight:700;color:var(--green);font-size:1.1rem">' + (summary.shubha_vedhas||0) + '</div>' +
                    '<div style="font-size:0.75rem;color:var(--text-muted)">Shubha Vedhas</div></div>' +
                '<div style="padding:8px 14px;background:rgba(212,168,67,0.08);border:1px solid rgba(212,168,67,0.2);border-radius:6px;text-align:center">' +
                    '<div style="font-weight:700;color:' + balColor + ';font-size:1.1rem">' + (summary.balance||'—') + '</div>' +
                    '<div style="font-size:0.75rem;color:var(--text-muted)">Net: ' + (summary.net_score >= 0 ? '+' : '') + (summary.net_score||0) + '</div></div>' +
            '</div>';

            // Planet-wise collapsible vedha table
            var planets = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'];
            var MALEFIC_SET = new Set(['Sun','Mars','Saturn','Rahu','Ketu']);

            planets.forEach(function(planet){
                var report = (vl.planet_reports || {})[planet];
                if (!report) return;
                var trad = report.traditional_vedha || {};
                var vedhaClass = report.vedha_classification || {};
                var isMalefic = MALEFIC_SET.has(planet);
                var nc = isMalefic ? 'var(--red)' : 'var(--green)';
                var natureLabel = isMalefic ? 'Papa' : 'Shubha';
                var tradPair = report.traditional_vedha_pair || {};

                html += '<details style="margin-bottom:6px;border:1px solid rgba(255,255,255,0.08);border-radius:6px;overflow:hidden">' +
                    '<summary style="padding:8px 12px;cursor:pointer;background:rgba(26,26,46,0.6);display:flex;align-items:center;gap:8px">' +
                        '<span style="font-weight:700;color:' + nc + ';font-size:0.95rem">' + planet + '</span>' +
                        '<span style="font-size:0.78rem;color:var(--text-muted)">' + (report.transit_nakshatra||'') + ' (' + (report.transit_rashi||'') + ')</span>' +
                        '<span style="font-size:0.72rem;padding:2px 6px;border-radius:3px;background:rgba(255,255,255,0.05);color:var(--text-dim)">' + (vedhaClass.type||'') + '</span>' +
                        '<span style="font-size:0.72rem;color:' + nc + '">' + natureLabel + '</span>' +
                        '<span style="margin-left:auto;font-size:0.75rem;color:var(--gold)">' + (trad.all_active_targets||[]).length + ' targets</span>' +
                    '</summary>' +
                    '<div style="padding:8px 12px;background:rgba(0,0,0,0.2)">';

                // Vedha info
                html += '<div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:6px">' +
                    'Vedha: <b>' + (vedhaClass.type||'') + '</b> | Strength: <b>' + (vedhaClass.strength||'') + '</b> | ' +
                    'Trad Pair: <b>' + (tradPair.partner_nakshatra||'None') + '</b></div>';

                // Direction-wise targets
                var dirs = [
                    {key: 'vama_targets', label: 'Vama (Left / baaI)', color: '#66bb6a'},
                    {key: 'dakshina_targets', label: 'Dakshina (Right / daahini)', color: '#ef5350'},
                    {key: 'sammukha_targets', label: 'Sammukha (Front / saamne)', color: '#d4a843'},
                ];
                dirs.forEach(function(d){
                    var targets = trad[d.key] || [];
                    if (!targets.length) return;
                    html += '<div style="margin-bottom:4px"><span style="font-size:0.75rem;font-weight:600;color:' + d.color + '">' + d.label + ':</span> ' +
                        '<span style="font-size:0.78rem">' + targets.join(', ') + '</span></div>';
                });

                // Affected natal planets
                var detail = trad.detail || [];
                var affected = detail.filter(function(e){ return e.affected_natal_planets && e.affected_natal_planets.length > 0; });
                if (affected.length) {
                    html += '<div style="margin-top:6px;padding:6px 8px;background:rgba(255,140,0,0.08);border:1px solid rgba(255,140,0,0.2);border-radius:4px">' +
                        '<span style="font-weight:700;color:#ff8c00;font-size:0.78rem">Natal Planets Affected:</span>';
                    affected.forEach(function(a){
                        a.affected_natal_planets.forEach(function(np){
                            html += '<div style="font-size:0.75rem;margin-top:2px;color:var(--text-dim)">' + np.effect + '</div>';
                        });
                    });
                    html += '</div>';
                }

                // Full target table
                if (detail.length) {
                    html += '<table class="data-table" style="margin-top:8px;font-size:0.78rem"><thead><tr>' +
                        '<th>Target Nak</th><th>Direction</th><th>Rashi</th><th>Nak Lord</th><th>Rashi Lord</th><th>Strength</th></tr></thead><tbody>';
                    detail.forEach(function(e){
                        var dirColor = e.direction_key === 'vama' ? '#66bb6a' : e.direction_key === 'dakshina' ? '#ef5350' : '#d4a843';
                        html += '<tr>' +
                            '<td style="font-weight:600">' + e.nakshatra + '</td>' +
                            '<td style="color:' + dirColor + '">' + (e.direction_key||'') + '</td>' +
                            '<td>' + (e.rashi||'') + '</td>' +
                            '<td>' + (e.nak_lord||'') + '</td>' +
                            '<td>' + (e.rashi_lord||'') + '</td>' +
                            '<td>' + (e.strength||'') + ' (' + (e.strength_multiplier||1) + 'x)</td></tr>';
                    });
                    html += '</tbody></table>';
                }
                html += '</div></details>';
            });

            // Lagna vedha
            var lagna = vl.lagna_report;
            if (lagna) {
                var lt = lagna.traditional_vedha || {};
                html += '<details style="margin-bottom:6px;border:1px solid rgba(41,128,185,0.3);border-radius:6px;overflow:hidden">' +
                    '<summary style="padding:8px 12px;cursor:pointer;background:rgba(26,26,46,0.6);display:flex;align-items:center;gap:8px">' +
                        '<span style="font-weight:700;color:#2980b9;font-size:0.95rem">Lagna (Ascendant)</span>' +
                        '<span style="font-size:0.78rem;color:var(--text-muted)">' + (lagna.lagna_nakshatra||'') + ' (' + (lagna.lagna_rashi||'') + ')</span>' +
                        '<span style="margin-left:auto;font-size:0.75rem;color:var(--gold)">' + (lt.all_targets||[]).length + ' targets</span>' +
                    '</summary>' +
                    '<div style="padding:8px 12px;background:rgba(0,0,0,0.2)">';

                // Direction targets
                if ((lt.vama_targets||[]).length)
                    html += '<div style="margin-bottom:4px"><span style="font-size:0.75rem;font-weight:600;color:#66bb6a">Vama:</span> ' + lt.vama_targets.join(', ') + '</div>';
                if ((lt.dakshina_targets||[]).length)
                    html += '<div style="margin-bottom:4px"><span style="font-size:0.75rem;font-weight:600;color:#ef5350">Dakshina:</span> ' + lt.dakshina_targets.join(', ') + '</div>';
                if ((lt.sammukha_targets||[]).length)
                    html += '<div style="margin-bottom:4px"><span style="font-size:0.75rem;font-weight:600;color:#d4a843">Sammukha:</span> ' + lt.sammukha_targets.join(', ') + '</div>';

                // Planets making vedha to lagna
                var pvl = lagna.planets_making_vedha_to_lagna || [];
                if (pvl.length) {
                    html += '<h3 style="font-size:0.82rem;margin:8px 0 4px">Planets Making Vedha to Lagna</h3>' +
                        '<table class="data-table" style="font-size:0.78rem"><thead><tr><th>Planet</th><th>From Nak</th><th>Direction</th><th>Nature</th><th>Effect</th></tr></thead><tbody>';
                    pvl.forEach(function(p){
                        var nc2 = p.nature === 'Papa' ? 'var(--red)' : 'var(--green)';
                        html += '<tr><td style="font-weight:600;color:' + nc2 + '">' + p.planet + '</td>' +
                            '<td>' + p.from_nakshatra + '</td><td>' + p.direction + '</td>' +
                            '<td style="color:' + nc2 + '">' + p.nature + '</td>' +
                            '<td style="font-size:0.75rem">' + (p.effect||'') + '</td></tr>';
                    });
                    html += '</tbody></table>';
                }
                html += '</div></details>';
            }

            html += '</div>';
            return html;
        })()}
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

            /* Four padas inside each nakshatra box, so vedha can be read pada → pada */
            if (type === 'nakshatra') {
                html += buildInnerPadaHtml(name, r, c);
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
                var sourcePada = getTransitPadaForPlanet(vl.planet);
                var p1 = pointInCellByPada(vl.from, sourcePada, cellW, cellH);
                var p2 = pointInCellByPada(vl.to, vl.to_pada || sourcePada, cellW, cellH);
                var x1 = p1[0], y1 = p1[1];
                var x2 = p2[0], y2 = p2[1];

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
            if (layer === 'padas') {
                document.querySelectorAll('.sbc-inner-padas').forEach(function(p){
                    p.style.display = on ? 'grid' : 'none';
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
                var sourcePada = getTransitPadaForPlanet(planetName);
                var p1 = pointInCellByPada(vl.from, sourcePada, cellW, cellH);
                var p2 = pointInCellByPada(vl.to, vl.to_pada || sourcePada, cellW, cellH);
                var x1 = p1[0], y1 = p1[1];
                var x2 = p2[0], y2 = p2[1];

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

    /* ══════════════════════════════════════════════════════════
       Planet Vedha Chooser — click a planet button to see its vedha detail
       ══════════════════════════════════════════════════════════ */
    document.querySelectorAll('.sbc-planet-vedha-btn').forEach(function(btn){
        btn.addEventListener('click', function(){
            var pName = this.dataset.planet;
            var resultDiv = document.getElementById('sbc-planet-vedha-result');
            if (!resultDiv) return;

            // Find the planet analysis from sbc data
            var pa = (sbc.planet_analyses || []).find(function(p){ return p.planet === pName; });
            if (!pa) { resultDiv.innerHTML = '<p style="color:var(--red)">No data for ' + pName + '</p>'; return; }

            // Highlight selected button
            document.querySelectorAll('.sbc-planet-vedha-btn').forEach(function(b){ b.style.opacity = '0.5'; });
            this.style.opacity = '1';

            var nc = pa.nature === 'benefic' ? 'var(--green)' : 'var(--red)';
            var gb = pa.graha_bala || {};
            var vedhaHitsP = pa.vedha_hits || [];
            var lattaHitsP = pa.latta_hits || [];

            var html = '<div style="border:1px solid ' + nc + ';border-radius:8px;padding:12px;background:rgba(26,26,46,0.5)">';
            html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">';
            html += '<div><span style="font-weight:700;font-size:1.1rem;color:' + nc + '">' + pName + '</span>';
            html += ' <span style="font-size:0.8rem;color:var(--text-muted)">in ' + pa.nakshatra + ' Pada ' + (pa.pada||'?') + ' (' + pa.sign + ')</span></div>';
            html += '<div style="text-align:right">';
            html += '<div style="font-size:0.78rem;color:' + nc + ';font-weight:600">' + (pa.vedha_speed_type||'') + '</div>';
            html += '<div style="font-size:0.72rem;color:var(--text-dim)">' + (pa.vedha_mode||'') + ' | Speed: ' + (pa.speed||0) + (pa.retrograde ? ' (R)' : '') + '</div>';
            html += '</div></div>';

            // Graha Bala
            html += '<div style="font-size:0.78rem;color:var(--text-muted);margin-bottom:8px">';
            html += 'Graha Bala: <span style="color:var(--gold);font-weight:600">' + (gb.graha_bala||'—') + '</span>';
            html += ' (' + (gb.sign_relation||'') + ' ' + (gb.sign_strength ? (gb.sign_strength*100).toFixed(0)+'%' : '') + ' × ' + (gb.motion||'') + ' ' + (gb.motion_multiplier||1) + '×)';
            html += '</div>';

            // Vedha hits
            if (vedhaHitsP.length) {
                html += '<h4 style="font-size:0.82rem;color:' + nc + ';margin:8px 0 4px">Vedha Hits (' + vedhaHitsP.length + ')</h4>';
                html += '<table class="data-table" style="font-size:0.75rem"><thead><tr><th>Target</th><th>Dir</th><th>Bindu</th><th>Tara</th><th>Severity</th><th>Temporal</th><th>Strength</th></tr></thead><tbody>';
                vedhaHitsP.forEach(function(vh){
                    var sc = vh.severity === 'CRITICAL' ? '#ff0000' : vh.severity === 'HIGH' ? '#ff4444' : '#ff8c00';
                    var ts = vh.temporal_state || {};
                    html += '<tr>' +
                        '<td style="font-weight:600">' + vh.to_entity + '</td>' +
                        '<td>' + (vh.vedha_direction||'') + '</td>' +
                        '<td style="color:var(--gold)">' + (vh.bindu_type||'—') + '</td>' +
                        '<td>' + (vh.tara||'—') + '</td>' +
                        '<td style="color:' + sc + ';font-weight:600">' + vh.severity + '</td>' +
                        '<td style="font-size:0.7rem">' + (ts.state || '—') + '</td>' +
                        '<td>' + (vh.strength_multiplier||1) + 'x</td>' +
                    '</tr>';
                });
                html += '</tbody></table>';
            } else {
                html += '<p style="font-size:0.78rem;color:var(--text-dim)">No vedha hits on sensitive points</p>';
            }

            // Latta
            if (lattaHitsP.length) {
                html += '<h4 style="font-size:0.82rem;color:#ff8c00;margin:8px 0 4px">Latta Hits</h4>';
                lattaHitsP.forEach(function(lh){
                    html += '<div style="padding:4px 8px;margin-bottom:4px;background:rgba(255,140,0,0.06);border-left:3px solid #ff8c00;border-radius:3px;font-size:0.78rem">' +
                        '<span style="font-weight:600">' + lh.kicked_nak + '</span>' +
                        (lh.bindu_type ? ' <span style="color:var(--gold)">(' + lh.bindu_type + ')</span>' : '') +
                        ' — <span style="color:var(--red)">' + lh.severity + '</span>' +
                        ' — ' + (lh.effect||'') + '</div>';
                });
            }

            // Book vedha targets
            var bTargets = pa.nak_vedha_targets;
            if (bTargets) {
                html += '<h4 style="font-size:0.82rem;color:var(--gold);margin:10px 0 4px">Book Vedha Targets (Shlokas 19-47)</h4>';
                ['vama', 'dakshina', 'sammukha'].forEach(function(dir){
                    var targets = bTargets[dir] || [];
                    if (!targets.length) return;
                    var dirLabel = dir === 'vama' ? 'Vama (Left/बाई)' : dir === 'dakshina' ? 'Dakshina (Right/दाहिनी)' : 'Sammukha (Front/सामने)';
                    var dirColor = dir === 'vama' ? '#66bb6a' : dir === 'dakshina' ? '#ef5350' : '#d4a843';
                    html += '<div style="margin-bottom:4px"><span style="font-size:0.75rem;font-weight:600;color:' + dirColor + '">' + dirLabel + ':</span> ';
                    html += '<span style="font-size:0.75rem;color:var(--text-muted)">' + targets.join(', ') + '</span></div>';
                });
                html += '<div style="font-size:0.7rem;color:var(--text-dim);margin-top:4px">' +
                    'Active direction per speed: <strong>' + (pa.vedha_mode||'') + '</strong>' +
                    (pa.vedha_mode === 'right' ? ' → only dakshina targets active (retrograde)' :
                     pa.vedha_mode === 'left' ? ' → only vama targets active (fast)' :
                     pa.vedha_mode === 'front' ? ' → only sammukha target active (medium speed)' :
                     ' → all directions active') + '</div>';
            }

            // Corner Pada Vedha (Shloka 52)
            var cpv = pa.corner_pada_vedha;
            if (cpv) {
                var cpvColor = cpv.nature === 'shubha_vedha' ? '#66bb6a' : '#ef5350';
                html += '<h4 style="font-size:0.82rem;color:#ba68c8;margin:10px 0 4px">Corner Pada Vedha (Shloka 52)</h4>';
                html += '<div style="padding:6px 10px;background:rgba(186,104,200,0.08);border-left:3px solid #ba68c8;border-radius:4px;font-size:0.78rem">';
                html += '<div><span style="font-weight:600;color:#ba68c8">' + cpv.corner + ' Corner</span>';
                html += ' — Planet at <strong>' + cpv.from_nak + ' Pada ' + cpv.from_pada + '</strong> (junction pada)</div>';
                html += '<div style="margin-top:3px">Vedhas svara <strong style="color:#ba68c8">' + cpv.svara + ' (' + cpv.svara_en + ')</strong>';
                html += ' at grid [' + cpv.svara_pos.join(',') + '] + <strong>Purna Tithi</strong> at center [' + cpv.center_pos.join(',') + ']</div>';
                html += '<div style="margin-top:3px;color:' + cpvColor + ';font-weight:600">' + cpv.effect + '</div>';
                html += '<div style="font-size:0.7rem;color:var(--text-dim);margin-top:2px">Strength: ' + (cpv.strength_multiplier||1) + 'x</div>';
                html += '</div>';
            }

            html += '</div>';
            resultDiv.innerHTML = html;
        });
    });
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

// ─── KP SYSTEM (Comprehensive Sub-Tab UI) ──────────────────
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
    const transitTime = document.getElementById('kp-transit-time').value;
    if (transitTime) body.transit_time = parseTimeInput(transitTime);
    const horaryNum = document.getElementById('kp-horary-num').value;
    if (horaryNum) body.kp_horary_number = parseInt(horaryNum);

    const data = await apiCall('/kp', body, resultEl);
    if (!data) return;

    const kp = data.kp_analysis || {};
    const cuspal = kp.cuspal_sublords || [];
    const fin = kp.financial_analysis || {};
    const rp = kp.ruling_planets || null;
    const sigHouses = kp.significators || {};
    const ptable = kp.planet_table || [];
    const promise = kp.promise_denial || {};
    const houseVerdicts = promise.house_verdicts || {};
    const groupVerdicts = promise.group_verdicts || {};
    const dba = kp.dba_analysis || null;
    const rahuAgents = kp.rahu_agents || {};
    const ketuAgents = kp.ketu_agents || {};
    const horary = kp.horary || null;
    const aspectsOnCusps = kp.aspects_on_cusps || [];
    const cuspalSubSub = kp.cuspal_sub_sub || [];
    const nadi = kp.nakshatra_nadi || [];
    const sigV2 = kp.planet_signification_v2 || [];
    const houseSigView = kp.house_significators_view || [];
    const allPlanets = data.planets || [];
    const allHouses = data.houses || [];
    const fortuna = kp.fortuna_point || {};
    const yogiData = kp.yogi_avayogi || {};
    const planetStatus = kp.planet_status || [];
    const aspectDefs = kp.aspect_definitions || [];
    const planetColors = {Sun:'#FFA500',Moon:'#C0C0C0',Mars:'#FF4444',Mercury:'#00CED1',Jupiter:'#FFD700',Venus:'#FF69B4',Saturn:'#4169E1',Rahu:'#8B008B',Ketu:'#808080',Ascendant:'#00FF88'};
    const verdictColor = function(v){ if(!v)return'var(--text-muted)'; return v==='PROMISE'?'var(--green)':v==='DENIAL'?'var(--red)':v.indexOf('PROMISE')>=0?'#66bb6a':'var(--text-muted)'; };
    const pColor = function(n){ return planetColors[n]||'#ccc'; };

    /* ── DMS helper ─────────────────────────────────────────── */
    function toDMS(deg) {
        if (typeof deg !== 'number') return '—';
        var d = Math.floor(deg); var m = Math.floor((deg - d) * 60); var s = Math.round(((deg - d) * 60 - m) * 60);
        if (s === 60) { m++; s = 0; } if (m === 60) { d++; m = 0; }
        return d + '°' + (m < 10 ? '0' : '') + m + "'" + (s < 10 ? '0' : '') + s + '"';
    }

    /* ═══ Sub-Tab Navigation Bar ═══════════════════════════════ */
    var kpTabs = [
        {id:'kp-overview', label:'Overview'},
        {id:'kp-charts',   label:'KP Chart'},
        {id:'kp-planets',  label:'Planets'},
        {id:'kp-cusps',    label:'Cusps'},
        {id:'kp-sig1',     label:'Planet Signification'},
        {id:'kp-sig2',     label:'Planet Sig V2'},
        {id:'kp-hsig',     label:'House Significators'},
        {id:'kp-nadi',     label:'Nakshatra Nadi'},
        {id:'kp-subsub',   label:'Cuspal Sub-Sub'},
        {id:'kp-4step',    label:'4-Step'},
        {id:'kp-aspect',   label:'Aspect on Cusp'},
        {id:'kp-rp',       label:'Ruling Planets'},
        {id:'kp-currp',    label:'Current RP'},
        {id:'kp-misc',     label:'Misc'},
        {id:'kp-dba',      label:'DBA Analysis'},
        {id:'kp-horary',   label:'KP Horary'},
        {id:'kp-moonnl',   label:'Moon NL/SL/SSL'},
        {id:'kp-prashna',  label:'Prashna Yes/No'},
        {id:'kp-match',    label:'Match Prediction'},
    ];

    var html = '<div class="kp-subtab-bar" style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:16px;border-bottom:1px solid #333;padding-bottom:8px">';
    kpTabs.forEach(function(t, i){
        html += '<button class="kp-stab'+(i===0?' active':'')+'" data-kptab="'+t.id+'" style="padding:6px 12px;border:1px solid #444;border-radius:4px 4px 0 0;background:'+(i===0?'var(--gold)':'#1a1a2e')+';color:'+(i===0?'#000':'var(--text-muted)')+';cursor:pointer;font-size:0.75rem;font-weight:600;border-bottom:none">'+t.label+'</button>';
    });
    html += '</div>';

    /* ═══ TAB: Overview ════════════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-overview">';
    html += '<div class="signal-card"><h3 style="color:var(--gold-light)">KP Financial Analysis</h3>';
    html += '<p style="color:var(--text);margin:8px 0">'+(fin.overall_verdict||'')+'</p>';
    html += '<div style="display:flex;gap:24px;flex-wrap:wrap;margin-top:10px">';
    html += '<div class="metric"><div class="label">KP Score</div><div class="value '+(fin.avg_score>0?'green':fin.avg_score<0?'red':'gold')+'">'+(fin.avg_score*100).toFixed(0)+'%</div></div>';
    var finHouses = fin.houses || {};
    [2,5,7,10,11].forEach(function(h){
        var fh = finHouses[h] || {};
        html += '<div class="metric"><div class="label">H'+h+' '+(fh.meaning||'').split('&')[0]+'</div><div class="value" style="font-size:0.85rem;color:'+verdictColor(fh.verdict||'')+'">'+(fh.verdict||'—')+'</div></div>';
    });
    html += '</div></div>';
    /* House Group Verdicts */
    html += '<div class="card"><h2 style="color:var(--gold-light)">House Group Analysis</h2>';
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-top:10px">';
    Object.keys(groupVerdicts).forEach(function(gk){
        var gv = groupVerdicts[gk];
        var bg = gv.verdict==='FAVORABLE'?'rgba(0,200,81,0.08)':gv.verdict==='UNFAVORABLE'?'rgba(255,61,0,0.08)':'rgba(255,255,255,0.03)';
        var border = gv.verdict==='FAVORABLE'?'#00c851':gv.verdict==='UNFAVORABLE'?'#ff3d00':'#555';
        html += '<div style="border:1px solid '+border+';border-radius:6px;padding:10px;background:'+bg+'">';
        html += '<div style="font-weight:700;font-size:0.85rem;color:var(--text)">'+gv.label+'</div>';
        html += '<div style="font-size:0.75rem;color:var(--text-muted)">Houses: '+gv.houses.join(', ')+'</div>';
        html += '<div style="font-weight:700;margin-top:4px;color:'+verdictColor(gv.verdict)+'">'+gv.verdict+'</div>';
        html += '<div style="font-size:0.7rem;color:var(--text-dim)">'+gv.promises+'P / '+gv.denials+'D</div>';
        html += '</div>';
    });
    html += '</div></div>';
    /* Rahu/Ketu Agents */
    html += '<div class="card"><h2 style="color:var(--gold-light)">Rahu/Ketu Agent Analysis</h2>';
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">';
    [rahuAgents, ketuAgents].forEach(function(ag){
        if (!ag.node) return;
        html += '<div style="border:1px solid #333;border-radius:6px;padding:12px">';
        html += '<div style="font-weight:700;color:'+pColor(ag.node)+'">'+ag.node+'</div>';
        html += '<div style="font-size:0.82rem;margin-top:6px"><span style="color:var(--text-muted)">Sign Lord:</span> <span style="color:'+pColor(ag.sign_lord)+'">'+ag.sign_lord+'</span></div>';
        html += '<div style="font-size:0.82rem"><span style="color:var(--text-muted)">Conjunct:</span> '+(ag.conjunct.length?ag.conjunct.join(', '):'None')+'</div>';
        html += '<div style="font-size:0.82rem"><span style="color:var(--text-muted)">Aspecting:</span> '+(ag.aspecting.length?ag.aspecting.join(', '):'None')+'</div>';
        html += '<div style="font-size:0.82rem;margin-top:4px;font-weight:600;color:var(--gold)">Acts as: '+(ag.acts_as||[]).join(', ')+'</div>';
        html += '</div>';
    });
    html += '</div></div>';
    html += '</div>'; /* end overview */

    /* ═══ TAB: KP Chart (North Indian Diamond) ═════════════════ */
    html += '<div class="kp-tab-pane" id="kp-charts" style="display:none">';
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">';
    /* KP Chart */
    html += '<div class="card"><h2 style="color:var(--gold-light)">KP Chart (Placidus)</h2>';
    html += '<div id="kp-diamond-chart" style="display:flex;justify-content:center"></div></div>';
    /* Rasi Chart */
    html += '<div class="card"><h2 style="color:var(--gold-light)">Rasi Chart</h2>';
    html += '<div id="kp-rasi-chart" style="display:flex;justify-content:center"></div></div>';
    html += '</div></div>';

    /* ═══ TAB: Planets ═════════════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-planets" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Planets Table</h2>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>Planet</th><th>Degree</th><th>DMS</th><th>Sign</th><th>Nakshatra</th><th>SL (Sign Lord)</th><th>NL (Star Lord)</th><th>SB (Sub Lord)</th><th>SS (Sub-Sub)</th><th>KP#</th><th>House</th><th>Status</th></tr></thead><tbody>';
    ptable.forEach(function(p){
        var retro = p.retro ? 'R' : '';
        var speed = allPlanets.find(function(x){return x.planet===p.planet;});
        var combust = ''; /* Sun proximity check */
        if (p.planet !== 'Sun' && p.planet !== 'Rahu' && p.planet !== 'Ketu' && speed) {
            var sunP = allPlanets.find(function(x){return x.planet==='Sun';});
            if (sunP) {
                var diff = Math.abs(p.longitude - sunP.longitude);
                if (diff > 180) diff = 360 - diff;
                if (diff < 10) combust = 'C';
            }
        }
        var status = [retro, combust].filter(Boolean).join('/') || '—';
        html += '<tr>';
        html += '<td style="font-weight:700;color:'+pColor(p.planet)+'">'+p.planet+'</td>';
        html += '<td>'+p.longitude.toFixed(4)+'</td>';
        html += '<td style="font-family:monospace;font-size:0.72rem">'+toDMS(p.longitude % 30)+'</td>';
        html += '<td>'+p.sign+'</td>';
        html += '<td style="font-size:0.72rem">'+p.nakshatra+' P'+p.pada+'</td>';
        html += '<td style="color:'+pColor(p.sign_lord)+'">'+p.sign_lord+'</td>';
        html += '<td style="color:'+pColor(p.star_lord)+'">'+p.star_lord+'</td>';
        html += '<td style="font-weight:700;color:'+pColor(p.sub_lord)+'">'+p.sub_lord+'</td>';
        html += '<td style="color:'+pColor(p.sub_sub_lord)+'">'+p.sub_sub_lord+'</td>';
        html += '<td style="color:var(--gold)">'+p.kp_number+'</td>';
        html += '<td>H'+p.house_occupied+'</td>';
        html += '<td style="color:'+(retro?'#FF4444':combust?'#FFA500':'var(--text-muted)')+'">'+status+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: Cusps ══════════════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-cusps" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Cusps Table</h2>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>House</th><th>Degree</th><th>DMS</th><th>Sign</th><th>SL (Sign Lord)</th><th>NL (Star Lord)</th><th>SB (Sub Lord)</th><th>SS (Sub-Sub)</th><th>KP#</th><th>Verdict</th></tr></thead><tbody>';
    cuspal.forEach(function(c){
        var hv = houseVerdicts[c.house] || {};
        var isFin = [2,5,7,10,11].indexOf(c.house) >= 0;
        html += '<tr style="'+(isFin?'background:rgba(212,168,67,0.04)':'')+'">';
        html += '<td style="font-weight:700;color:'+(isFin?'var(--gold)':'var(--text)')+'">H'+c.house+'</td>';
        html += '<td>'+c.cusp_longitude.toFixed(4)+'</td>';
        html += '<td style="font-family:monospace;font-size:0.72rem">'+toDMS(c.cusp_longitude % 30)+'</td>';
        html += '<td>'+c.sign+'</td>';
        html += '<td style="color:'+pColor(c.sign_lord)+'">'+c.sign_lord+'</td>';
        html += '<td style="color:'+pColor(c.star_lord)+'">'+c.star_lord+'</td>';
        html += '<td style="font-weight:700;color:'+pColor(c.sub_lord)+'">'+c.sub_lord+'</td>';
        html += '<td style="color:'+pColor(c.sub_sub_lord)+'">'+c.sub_sub_lord+'</td>';
        html += '<td>'+c.kp_number+'</td>';
        html += '<td style="font-weight:700;color:'+verdictColor(hv.verdict||'')+'">'+( hv.verdict||'—')+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: Planet Signification (Original) ═════════════════ */
    html += '<div class="kp-tab-pane" id="kp-sig1" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Planet Signification (4-Step KP Chain)</h2>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>Planet</th><th>Sign</th><th>Nak</th><th>Sign Lord</th><th>Star Lord</th><th>Sub Lord</th><th>Sub-Sub</th><th>KP#</th><th>H.Occ</th><th>H.Own</th><th>Signified Houses</th></tr></thead><tbody>';
    ptable.forEach(function(p){
        var retro = p.retro ? ' (R)' : '';
        html += '<tr>';
        html += '<td style="font-weight:700;color:'+pColor(p.planet)+'">'+p.planet+retro+'</td>';
        html += '<td>'+p.sign+'</td>';
        html += '<td style="font-size:0.72rem">'+p.nakshatra+' P'+p.pada+'</td>';
        html += '<td style="color:'+pColor(p.sign_lord)+'">'+p.sign_lord+'</td>';
        html += '<td style="color:'+pColor(p.star_lord)+'">'+p.star_lord+'</td>';
        html += '<td style="font-weight:700;color:'+pColor(p.sub_lord)+'">'+p.sub_lord+'</td>';
        html += '<td style="color:'+pColor(p.sub_sub_lord)+'">'+p.sub_sub_lord+'</td>';
        html += '<td style="color:var(--gold)">'+p.kp_number+'</td>';
        html += '<td>H'+p.house_occupied+'</td>';
        html += '<td>'+(p.houses_owned.length?p.houses_owned.map(function(h){return 'H'+h;}).join(','):'—')+'</td>';
        html += '<td style="font-size:0.72rem;font-weight:600">'+(p.signified_houses.map(function(s){return 'H'+s.house+'(L'+s.level+')';}).join(' '))+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: Planet Signification V2 ═════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-sig2" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Planet Signification View 2</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:10px">Star Lord Occupancy / Occupancy / Star Lord Ownership / Ownership</p>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>Planet</th><th>Star Lord Occupancy</th><th>Occupancy</th><th>Star Lord Ownership</th><th>Ownership</th><th>Signified Houses</th></tr></thead><tbody>';
    sigV2.forEach(function(p){
        html += '<tr>';
        html += '<td style="font-weight:700;color:'+pColor(p.planet)+'">'+p.planet+'</td>';
        html += '<td>'+p.star_lord+' → H'+(p.star_lord_occupancy||'—')+'</td>';
        html += '<td>H'+(p.occupancy||'—')+'</td>';
        html += '<td>'+p.star_lord+' → '+(p.star_lord_ownership.length?p.star_lord_ownership.map(function(h){return 'H'+h;}).join(','):'—')+'</td>';
        html += '<td>'+(p.ownership.length?p.ownership.map(function(h){return 'H'+h;}).join(','):'—')+'</td>';
        html += '<td style="font-weight:700;color:var(--gold)">'+(p.signified_houses.map(function(h){return h;}).join(', '))+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: House Significators ═════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-hsig" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">House Significators</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:10px">House → Planets that signify it (with step level)</p>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>House</th><th>Sign</th><th>Lord</th><th>Significators</th></tr></thead><tbody>';
    houseSigView.forEach(function(h){
        var isFin = [2,5,7,10,11].indexOf(h.house) >= 0;
        html += '<tr style="'+(isFin?'background:rgba(212,168,67,0.04)':'')+'">';
        html += '<td style="font-weight:700;color:'+(isFin?'var(--gold)':'var(--text)')+'">H'+h.house+'</td>';
        html += '<td>'+(h.sign||'')+'</td>';
        html += '<td style="color:'+pColor(h.lord||'')+'">'+( h.lord||'')+'</td>';
        html += '<td style="font-size:0.75rem">';
        (h.significators||[]).forEach(function(s, idx){
            if (idx > 0) html += ', ';
            var stepLabel = 'L'+s.level;
            var stepClr = s.level===1?'var(--green)':s.level===2?'#66bb6a':s.level===3?'#aaa':'#666';
            html += '<span style="color:'+pColor(s.planet)+';font-weight:600">'+s.planet+'</span><span style="color:'+stepClr+';font-size:0.68rem">('+stepLabel+')</span>';
        });
        html += '</td></tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: Nakshatra Nadi ═════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-nadi" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Nakshatra Nadi</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:10px">Planet — StarLord(Houses) — SubLord(Houses)</p>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.8rem">';
    html += '<thead><tr><th>Planet</th><th>Star Lord</th><th>Star Lord Houses</th><th>Sub Lord</th><th>Sub Lord Houses</th><th>Nadi String</th></tr></thead><tbody>';
    nadi.forEach(function(n){
        html += '<tr>';
        html += '<td style="font-weight:700;color:'+pColor(n.planet)+'">'+n.planet+'</td>';
        html += '<td style="color:'+pColor(n.star_lord)+'">'+n.star_lord+'</td>';
        html += '<td style="font-weight:600">'+n.star_lord_houses+'</td>';
        html += '<td style="color:'+pColor(n.sub_lord)+'">'+n.sub_lord+'</td>';
        html += '<td style="font-weight:600">'+n.sub_lord_houses+'</td>';
        html += '<td style="font-family:monospace;font-size:0.72rem;color:var(--gold)">'+n.nadi_string+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: Cuspal Sub-Sub ═════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-subsub" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Cuspal Sub-Sub with Signified Houses</h2>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>House</th><th>DMS</th><th>Star Lord</th><th>Star Houses</th><th>Sub Lord</th><th>Sub Houses</th><th>Sub-Sub</th><th>SS Houses</th><th>Status</th></tr></thead><tbody>';
    cuspalSubSub.forEach(function(c){
        var isFin = [2,5,7,10,11].indexOf(c.house) >= 0;
        var statusClr = c.position_status==='Promise'?'var(--green)':c.position_status==='Denial'?'var(--red)':'var(--text-muted)';
        html += '<tr style="'+(isFin?'background:rgba(212,168,67,0.04)':'')+'">';
        html += '<td style="font-weight:700;color:'+(isFin?'var(--gold)':'var(--text)')+'">H'+c.house+'</td>';
        html += '<td style="font-family:monospace;font-size:0.72rem">'+(c.cusp_dms||toDMS(c.cusp_deg%30))+'</td>';
        html += '<td style="color:'+pColor(c.star_lord)+'">'+c.star_lord+'</td>';
        html += '<td style="font-weight:600">'+(c.star_lord_houses||[]).join(',')+'</td>';
        html += '<td style="font-weight:700;color:'+pColor(c.sub_lord)+'">'+c.sub_lord+'</td>';
        html += '<td style="font-weight:600">'+(c.sub_lord_houses||[]).join(',')+'</td>';
        html += '<td style="color:'+pColor(c.sub_sub_lord)+'">'+c.sub_sub_lord+'</td>';
        html += '<td style="font-weight:600">'+(c.sub_sub_lord_houses||[]).join(',')+'</td>';
        html += '<td style="font-weight:700;color:'+statusClr+'">'+c.position_status+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: 4-Step Significator ═════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-4step" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">4-Step Significator Analysis</h2>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>House</th><th>Lord</th><th>Step 1<br><small>Star of Occ</small></th><th>Step 2<br><small>Occupants</small></th><th>Step 3<br><small>Star of Lord</small></th><th>Step 4<br><small>Lord</small></th><th>All Sigs</th><th>Effective</th></tr></thead><tbody>';
    for (var h = 1; h <= 12; h++) {
        var hs = sigHouses[h] || {};
        var isFin = [2,5,7,10,11].indexOf(h) >= 0;
        html += '<tr style="'+(isFin?'background:rgba(212,168,67,0.04)':'')+'">';
        html += '<td style="font-weight:700;color:'+(isFin?'var(--gold)':'var(--text)')+'">H'+h+' '+( hs.sign||'')+'</td>';
        html += '<td style="color:'+pColor(hs.lord||'')+'">'+( hs.lord||'')+'</td>';
        html += '<td style="color:var(--green)">'+(hs.step1_star_of_occ||[]).join(', ')||'—'+'</td>';
        html += '<td style="color:#66bb6a">'+(hs.step2_occupants||[]).join(', ')||'—'+'</td>';
        html += '<td style="color:#aaa">'+(hs.step3_star_of_lord||[]).join(', ')||'—'+'</td>';
        html += '<td style="color:#888">'+(hs.step4_lord||[]).join(', ')||'—'+'</td>';
        html += '<td style="font-weight:600;font-size:0.72rem">'+(hs.all_significators||[]).join(', ')+'</td>';
        html += '<td style="font-weight:700;color:var(--green);font-size:0.72rem">'+(hs.effective_significators||[]).join(', ')||'—'+'</td>';
        html += '</tr>';
    }
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: Aspect on KP Cusp ═════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-aspect" style="display:none">';
    /* Aspect definitions note */
    html += '<div class="card"><h2 style="color:var(--gold-light)">Aspect on KP Cusp</h2>';
    html += '<details style="margin-bottom:12px"><summary style="cursor:pointer;color:var(--gold);font-size:0.82rem;font-weight:600">Note: Aspect Definitions & Weights</summary>';
    html += '<div style="margin-top:8px;overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>Abbr-Aspect</th><th>Degree</th><th>Orb</th><th>Weight</th></tr></thead><tbody>';
    aspectDefs.forEach(function(a){
        html += '<tr><td style="font-weight:600">'+a.abbr+'-'+a.full.toUpperCase()+'</td><td>'+a.degree+'</td><td>'+a.orb+'</td><td>'+a.weight+'</td></tr>';
    });
    html += '</tbody></table></div>';
    html += '<p style="color:var(--text-dim);font-size:0.75rem;margin-top:6px">Weight denotes strength of the aspect. Cusp degree in KP System used for computation.</p>';
    html += '</details>';
    /* Aspect matrix */
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.72rem">';
    html += '<thead><tr><th>Cusp</th><th>Degree</th>';
    ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'].forEach(function(pn){
        html += '<th style="color:'+pColor(pn)+'">'+pn.substr(0,3)+'</th>';
    });
    html += '</tr></thead><tbody>';
    aspectsOnCusps.forEach(function(c){
        var isFin = [2,5,7,10,11].indexOf(c.house) >= 0;
        html += '<tr style="'+(isFin?'background:rgba(212,168,67,0.04)':'')+'">';
        html += '<td style="font-weight:700;color:'+(isFin?'var(--gold)':'var(--text)')+'">H'+c.house+'</td>';
        html += '<td style="font-family:monospace;font-size:0.68rem">'+toDMS(c.cusp_deg % 30)+'</td>';
        ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'].forEach(function(pn){
            /* Show strongest (highest weight) aspect for this planet-cusp pair */
            var aspects = (c.aspects||[]).filter(function(a){return a.planet===pn;});
            if (aspects.length) {
                aspects.sort(function(a,b){return (b.weight||0)-(a.weight||0);});
                var asp = aspects[0];
                var aClr = asp.aspect==='CN'?'#FFA500':asp.aspect==='OP'?'#FF69B4':asp.aspect==='TR'?'var(--green)':asp.aspect==='SX'?'#66bb6a':asp.aspect==='SQ'?'var(--red)':'#aaa';
                var appSep = asp.applying ? 'A' : 'S';
                html += '<td style="color:'+aClr+';font-weight:700;font-size:0.68rem">'+asp.aspect+'<br><span style="font-weight:400;font-size:0.6rem">'+asp.orb.toFixed(1)+'°'+appSep+' W'+asp.weight+'</span></td>';
            } else {
                html += '<td style="color:#333">—</td>';
            }
        });
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ═══ TAB: Ruling Planets ═════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-rp" style="display:none">';
    if (rp) {
        html += '<div class="card"><h2 style="color:var(--gold-light)">Ruling Planets (Event Timing)</h2>';
        html += '<div style="display:flex;gap:20px;flex-wrap:wrap;margin-bottom:12px">';
        html += '<div class="metric"><div class="label">Query Time</div><div class="value" style="font-size:0.85rem">'+(rp.query_datetime||'')+'</div></div>';
        html += '<div class="metric"><div class="label">Day Lord</div><div class="value" style="color:'+pColor(rp.day_lord)+'">'+rp.day_lord+'</div></div>';
        html += '<div class="metric"><div class="label">Signal</div><div class="value" style="color:'+(rp.financial_timing.signal==='BULLISH'?'var(--green)':rp.financial_timing.signal==='BEARISH'?'var(--red)':'var(--text)')+'">'+rp.financial_timing.signal+'</div></div>';
        html += '</div>';
        html += '<table class="data-table" style="font-size:0.82rem"><thead><tr><th>Ruling Planet</th><th>Strength</th><th>Sources</th></tr></thead><tbody>';
        (rp.ruling_planets.all||[]).forEach(function(r){
            var sources = (rp.rp_sources||[]).filter(function(s){return s.planet===r.planet;}).map(function(s){return s.source;}).join(', ');
            var isPrimary = r.strength >= 2;
            html += '<tr>';
            html += '<td style="font-weight:700;color:'+pColor(r.planet)+'">'+r.planet+(isPrimary?' ★':'')+'</td>';
            html += '<td style="color:'+(isPrimary?'var(--gold)':'var(--text-muted)')+'">'+r.strength+'x</td>';
            html += '<td style="font-size:0.75rem">'+sources+'</td>';
            html += '</tr>';
        });
        html += '</tbody></table>';
        html += '<p style="color:var(--text-muted);font-size:0.8rem;margin-top:8px">'+rp.financial_timing.action+'</p>';
        if (rp.financial_timing.active_sectors && rp.financial_timing.active_sectors.length) {
            html += '<div style="margin-top:8px"><strong style="color:var(--text);font-size:0.82rem">Active Sectors:</strong>';
            rp.financial_timing.active_sectors.forEach(function(s){ html += '<div style="font-size:0.78rem;color:var(--text-muted);margin-left:12px">• '+s+'</div>'; });
            html += '</div>';
        }
        html += '</div>';
    } else {
        html += '<div class="card"><p style="color:var(--text-muted)">Enter a Transit Date to calculate Ruling Planets.</p></div>';
    }
    html += '</div>';

    /* ═══ TAB: Current Ruling Planets (Real-time or specific) ═════════════ */
    html += '<div class="kp-tab-pane" id="kp-currp" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Ruling Planets</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:10px">Calculate RP for the current moment or a specific date/time &amp; place</p>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:12px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Date (YYYY-MM-DD)</label><input type="date" id="kp-rp-date" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem" value="'+today+'"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Time (HH:MM)</label><input type="text" id="kp-rp-time" placeholder="HH:MM or HH:MM AM/PM" maxlength="10" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:130px" value="'+new Date().toTimeString().slice(0,5)+'"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Place</label><input type="text" id="kp-rp-place" value="'+(body.place||'Mumbai, Maharashtra, India')+'" list="city-suggestions" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:200px"></div>';
    html += '<button id="kp-fetch-currp-now" class="btn-primary" style="font-size:0.82rem;padding:7px 14px">Fetch NOW</button>';
    html += '<button id="kp-fetch-currp-custom" class="btn-primary" style="font-size:0.82rem;padding:7px 14px;background:#2a5298">Fetch for Date/Time</button>';
    html += '</div>';
    html += '<div id="kp-currp-result"></div>';
    html += '</div></div>';

    /* ═══ TAB: Misc (Fortuna Point + Yogi/Avayogi) ════════════ */
    html += '<div class="kp-tab-pane" id="kp-misc" style="display:none">';
    /* Fortuna Point — KP + Western side by side */
    if (fortuna && fortuna.kp) {
        var fkp = fortuna.kp;
        var fwest = fortuna.western;
        html += '<div class="card"><h2 style="color:var(--gold-light)">Fortuna Point (Part of Fortune)</h2>';
        html += '<p style="color:var(--text-dim);font-size:0.78rem;margin-bottom:12px">'+(fortuna.is_day_chart?'Day Chart (Sun above horizon)':'Night Chart (Sun below horizon)')+(fortuna.same_result?' — Both formulas give same result':'')+'</p>';
        html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.8rem">';
        html += '<thead><tr><th>System</th><th>Formula</th><th>DMS</th><th>Sign</th><th>House</th><th>Nakshatra</th><th>Sign Lord</th><th>Star Lord</th><th>Sub Lord</th><th>Sub-Sub</th><th>KP#</th></tr></thead><tbody>';
        /* KP row */
        html += '<tr style="background:rgba(0,200,81,0.05)">';
        html += '<td style="font-weight:700;color:var(--green)">KP</td>';
        html += '<td style="font-size:0.72rem">'+fkp.formula+'</td>';
        html += '<td style="font-family:monospace;font-weight:700">'+fkp.dms+'</td>';
        html += '<td>'+fkp.sign+'</td>';
        html += '<td>H'+fkp.house+'</td>';
        html += '<td style="font-size:0.72rem">'+fkp.nakshatra+' P'+fkp.pada+'</td>';
        html += '<td style="color:'+pColor(fkp.sign_lord)+'">'+fkp.sign_lord+'</td>';
        html += '<td style="color:'+pColor(fkp.star_lord)+'">'+fkp.star_lord+'</td>';
        html += '<td style="font-weight:700;color:'+pColor(fkp.sub_lord)+'">'+fkp.sub_lord+'</td>';
        html += '<td style="color:'+pColor(fkp.sub_sub_lord)+'">'+fkp.sub_sub_lord+'</td>';
        html += '<td>'+fkp.kp_number+'</td></tr>';
        /* Western row */
        html += '<tr style="background:rgba(100,149,237,0.05)">';
        html += '<td style="font-weight:700;color:#6495ED">Western</td>';
        html += '<td style="font-size:0.72rem">'+fwest.formula+'</td>';
        html += '<td style="font-family:monospace;font-weight:700">'+fwest.dms+'</td>';
        html += '<td>'+fwest.sign+'</td>';
        html += '<td>H'+fwest.house+'</td>';
        html += '<td style="font-size:0.72rem">'+fwest.nakshatra+' P'+fwest.pada+'</td>';
        html += '<td style="color:'+pColor(fwest.sign_lord)+'">'+fwest.sign_lord+'</td>';
        html += '<td style="color:'+pColor(fwest.star_lord)+'">'+fwest.star_lord+'</td>';
        html += '<td style="font-weight:700;color:'+pColor(fwest.sub_lord)+'">'+fwest.sub_lord+'</td>';
        html += '<td style="color:'+pColor(fwest.sub_sub_lord)+'">'+fwest.sub_sub_lord+'</td>';
        html += '<td>'+fwest.kp_number+'</td></tr>';
        html += '</tbody></table></div>';
        if (!fortuna.same_result) {
            html += '<p style="color:var(--text-dim);font-size:0.75rem;margin-top:6px">Note: KP always uses Asc+Moon-Sun. Western reverses to Asc+Sun-Moon for night charts. For day charts both are identical.</p>';
        }
        html += '</div>';
    }
    /* Yogi / Avayogi */
    if (yogiData && yogiData.yogi_planet) {
        var yp = yogiData.yogi_point || {};
        var ap = yogiData.avayogi_point || {};
        var fi = yogiData.financial_impact || {};
        html += '<div class="card"><h2 style="color:var(--gold-light)">Yogi Point & Avayogi</h2>';
        html += '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px">';
        html += '<div style="border:1px solid var(--green);border-radius:6px;padding:12px;background:rgba(0,200,81,0.05)">';
        html += '<div style="font-size:0.75rem;color:var(--text-muted)">Yogi Planet</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:'+pColor(yogiData.yogi_planet)+'">'+yogiData.yogi_planet+'</div>';
        html += '<div style="font-size:0.7rem;color:var(--text-dim)">Gains in dasha/bhukti</div></div>';
        html += '<div style="border:1px solid var(--gold);border-radius:6px;padding:12px;background:rgba(212,168,67,0.05)">';
        html += '<div style="font-size:0.75rem;color:var(--text-muted)">Duplicate Yogi</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:'+pColor(yogiData.duplicate_yogi)+'">'+yogiData.duplicate_yogi+'</div>';
        html += '<div style="font-size:0.7rem;color:var(--text-dim)">Supports Yogi</div></div>';
        html += '<div style="border:1px solid var(--red);border-radius:6px;padding:12px;background:rgba(255,61,0,0.05)">';
        html += '<div style="font-size:0.75rem;color:var(--text-muted)">Avayogi</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:'+pColor(yogiData.avayogi)+'">'+yogiData.avayogi+'</div>';
        html += '<div style="font-size:0.7rem;color:var(--text-dim)">Losses in dasha/bhukti</div></div>';
        html += '</div>';
        /* Yogi point details */
        html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.8rem">';
        html += '<thead><tr><th>Point</th><th>DMS</th><th>Sign</th><th>Nakshatra</th><th>House</th><th>Sign Lord</th><th>Star Lord</th><th>Sub Lord</th></tr></thead><tbody>';
        html += '<tr><td style="font-weight:700;color:var(--green)">Yogi Point</td>';
        html += '<td style="font-family:monospace">'+(yp.dms||'')+'</td><td>'+(yp.sign||'')+'</td><td>'+(yp.nakshatra||'')+'</td>';
        html += '<td>H'+(yp.house||'')+'</td><td style="color:'+pColor(yp.sign_lord||'')+'">'+( yp.sign_lord||'')+'</td>';
        html += '<td style="color:'+pColor(yp.star_lord||'')+'">'+( yp.star_lord||'')+'</td>';
        html += '<td style="color:'+pColor(yp.sub_lord||'')+'">'+( yp.sub_lord||'')+'</td></tr>';
        html += '<tr><td style="font-weight:700;color:var(--red)">Avayogi Point</td>';
        html += '<td style="font-family:monospace">'+(ap.dms||'')+'</td><td>'+(ap.sign||'')+'</td><td>'+(ap.nakshatra||'')+'</td>';
        html += '<td>—</td><td>—</td><td>—</td><td>—</td></tr>';
        html += '</tbody></table></div>';
        html += '<div style="margin-top:8px;font-size:0.78rem;color:var(--text-dim)">';
        html += '<div>'+fi.yogi_periods+'</div>';
        html += '<div>'+fi.dup_yogi_periods+'</div>';
        html += '<div>'+fi.avayogi_periods+'</div>';
        html += '</div></div>';
    }
    /* Planet Status (combustion, dignity, speed) */
    if (planetStatus.length) {
        html += '<div class="card"><h2 style="color:var(--gold-light)">Planet Status</h2>';
        html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
        html += '<thead><tr><th>Planet</th><th>DMS</th><th>Sign</th><th>House</th><th>Speed</th><th>Status</th><th>Dignity</th><th>Combust</th></tr></thead><tbody>';
        planetStatus.forEach(function(ps){
            var statusClr = ps.is_retro?'#FF4444':ps.speed_status==='Fast'?'var(--green)':ps.speed_status==='Stationary'?'#FFA500':'var(--text-muted)';
            var dignClr = ps.dignity==='Exalted'?'var(--green)':ps.dignity==='Debilitated'?'var(--red)':ps.dignity==='Own Sign'?'var(--gold)':'var(--text-muted)';
            html += '<tr>';
            html += '<td style="font-weight:700;color:'+pColor(ps.planet)+'">'+ps.planet+'</td>';
            html += '<td style="font-family:monospace;font-size:0.72rem">'+ps.dms+'</td>';
            html += '<td>'+ps.sign+'</td>';
            html += '<td>H'+ps.house+'</td>';
            html += '<td style="font-size:0.72rem">'+ps.speed.toFixed(4)+'</td>';
            html += '<td style="color:'+statusClr+'">'+ps.speed_status+(ps.is_retro?' (R)':'')+'</td>';
            html += '<td style="color:'+dignClr+';font-weight:600">'+ps.dignity+'</td>';
            html += '<td style="color:'+(ps.is_combust?'var(--red)':'var(--text-dim)')+'">'+(ps.is_combust?'Yes ('+ps.combust_orb+'°)':'No')+'</td>';
            html += '</tr>';
        });
        html += '</tbody></table></div></div>';
    }
    html += '</div>';

    /* ═══ TAB: DBA Analysis ═══════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-dba" style="display:none">';
    if (dba) {
        html += '<div class="card"><h2 style="color:var(--gold-light)">DBA Significator Matching</h2>';
        html += '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px">';
        html += '<div class="metric"><div class="label">Mahadasha</div><div class="value" style="color:'+pColor(dba.mahadasha)+'">'+dba.mahadasha+'</div></div>';
        html += '<div class="metric"><div class="label">Antardasha</div><div class="value" style="color:'+pColor(dba.antardasha)+'">'+dba.antardasha+'</div></div>';
        if (dba.pratyantar) html += '<div class="metric"><div class="label">Pratyantar</div><div class="value" style="color:'+pColor(dba.pratyantar)+'">'+dba.pratyantar+'</div></div>';
        html += '</div>';
        /* DBA Lords signified houses */
        if (dba.dba_analysis && dba.dba_analysis.length) {
            html += '<table class="data-table" style="font-size:0.82rem;margin-bottom:12px"><thead><tr><th>DBA Lord</th><th>Signified Houses</th></tr></thead><tbody>';
            dba.dba_analysis.forEach(function(d){
                html += '<tr><td style="font-weight:700;color:'+pColor(d.lord)+'">'+d.lord+'</td>';
                html += '<td>'+(d.signified_houses||[]).map(function(h){return 'H'+h;}).join(', ')+'</td></tr>';
            });
            html += '</tbody></table>';
        }
        var activeGroups = dba.active_groups || {};
        if (Object.keys(activeGroups).length) {
            html += '<div style="font-size:0.85rem;color:var(--text);margin-bottom:6px"><strong>Active house groups in current DBA:</strong></div>';
            html += '<div style="display:flex;flex-wrap:wrap;gap:8px">';
            Object.keys(activeGroups).forEach(function(gk){
                var ag = activeGroups[gk];
                html += '<span style="background:rgba(212,168,67,0.15);border:1px solid #d4a843;padding:4px 10px;border-radius:4px;font-size:0.8rem;color:var(--gold)">'+ag.label+'</span>';
            });
            html += '</div>';
        } else {
            html += '<p style="color:var(--text-muted);font-size:0.85rem">No strong house group activation in current DBA period.</p>';
        }
        html += '</div>';
    } else {
        html += '<div class="card"><p style="color:var(--text-muted)">Dasha data not available. Make sure birth data is correct.</p></div>';
    }
    html += '</div>';

    /* ═══ TAB: KP Horary ═════════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-horary" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">KP Horary (Prashna)</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:12px">Think of a number between 1 and 249. That number sets the Ascendant for your Prashna chart.</p>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:14px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">KP Number (1–249)</label><input type="number" id="kp-horary-inline" min="1" max="249" value="'+(horary?horary.input_number:'')+'" placeholder="1–249" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.9rem;width:100px;font-weight:700"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Query Date</label><input type="date" id="kp-horary-date" value="'+today+'" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Query Time</label><input type="text" id="kp-horary-time" value="'+new Date().toTimeString().slice(0,5)+'" placeholder="HH:MM" maxlength="10" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:100px"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Place</label><input type="text" id="kp-horary-place" value="'+(body.place||'Ujjain, Madhya Pradesh, India')+'" list="city-suggestions" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:200px"></div>';
    html += '<button id="kp-horary-fetch" class="btn-primary" style="font-size:0.82rem;padding:7px 16px">Run Horary Analysis</button>';
    html += '</div>';
    if (horary) {
        html += '<div id="kp-horary-result">';
        html += '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px">';
        html += '<div class="metric"><div class="label">KP Number</div><div class="value gold">'+horary.input_number+'</div></div>';
        html += '<div class="metric"><div class="label">Sign</div><div class="value">'+horary.sign+'</div></div>';
        html += '<div class="metric"><div class="label">Nakshatra</div><div class="value">'+horary.nakshatra+' P'+horary.pada+'</div></div>';
        html += '<div class="metric"><div class="label">Sign Lord</div><div class="value" style="color:'+pColor(horary.sign_lord)+'">'+horary.sign_lord+'</div></div>';
        html += '<div class="metric"><div class="label">Star Lord</div><div class="value" style="color:'+pColor(horary.star_lord)+'">'+horary.star_lord+'</div></div>';
        html += '<div class="metric"><div class="label">Sub Lord</div><div class="value" style="color:'+pColor(horary.sub_lord)+'">'+horary.sub_lord+'</div></div>';
        html += '<div class="metric"><div class="label">Sub-Sub Lord</div><div class="value" style="color:'+pColor(horary.sub_sub_lord)+'">'+horary.sub_sub_lord+'</div></div>';
        html += '</div></div>';
    } else {
        html += '<div id="kp-horary-result"><p style="color:var(--text-muted);font-style:italic">Enter a KP number above and click "Run Horary Analysis"</p></div>';
    }
    html += '</div></div>';

    /* ═══ TAB: Moon NL/SL/SSL Daily Timeline ═══════════════════ */
    html += '<div class="kp-tab-pane" id="kp-moonnl" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">Moon NL / SL / SSL — Daily Timeline</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:12px">Shows when Moon\'s Nakshatra Lord, Sub Lord &amp; Sub-Sub Lord change throughout the day — minute-by-minute accuracy</p>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:14px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Date (YYYY-MM-DD)</label><input type="date" id="kp-moonnl-date" value="'+today+'" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Start Time</label><input type="text" id="kp-moonnl-time" value="00:00" placeholder="HH:MM" maxlength="10" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:100px"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Place</label><input type="text" id="kp-moonnl-place" value="'+(body.place||'Ujjain, Madhya Pradesh, India')+'" list="city-suggestions" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:200px"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Duration (hrs)</label><input type="number" id="kp-moonnl-hours" value="24" min="1" max="72" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:60px"></div>';
    html += '<button id="kp-fetch-moonnl" class="btn-primary" style="font-size:0.82rem;padding:7px 16px">Generate Timeline</button>';
    html += '</div>';
    html += '<div id="kp-moonnl-result"></div>';
    html += '</div></div>';

    /* ═══ TAB: Prashna Yes/No ══════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-prashna" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">KP Prashna — Yes / No</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:12px">Think of your question and a number between 1–249. The cuspal sub-lord of the relevant house decides the answer. Ruling Planets cross-validate timing.</p>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:14px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">KP Number (1–249)</label><input type="number" id="kp-prashna-num" min="1" max="249" placeholder="1–249" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.9rem;width:90px;font-weight:700"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Question Type</label>';
    html += '<select id="kp-prashna-qtype" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;min-width:180px">';
    var prashnaOptions = [
        {v:'marriage', l:'Marriage / Partnership'}, {v:'wealth', l:'Wealth / Finance'},
        {v:'job', l:'Will I Get the Job?'}, {v:'promotion', l:'Promotion'},
        {v:'transfer', l:'Transfer'}, {v:'health', l:'Health Recovery'},
        {v:'travel_short', l:'Short Journey'}, {v:'travel_foreign', l:'Foreign Travel'},
        {v:'foreign_settle', l:'Foreign Settlement'}, {v:'visa', l:'Visa / Immigration'},
        {v:'court_case', l:'Court Case / Legal'}, {v:'speculation', l:'Speculation / Stock Market'},
        {v:'buy_property', l:'Buy Property'}, {v:'sell_property', l:'Sell Property'},
        {v:'education', l:'Exams / Education'}, {v:'competitive_exam', l:'Competitive Exam'},
        {v:'children', l:'Children'}, {v:'love_affair', l:'Love Affair'},
        {v:'loan', l:'Get Loan'}, {v:'recovery_money', l:'Recover Money'},
        {v:'debt_freedom', l:'Debt Freedom'}, {v:'interview', l:'Interview Call'},
        {v:'contract', l:'Get Contract'}, {v:'lottery', l:'Lottery / Prize'},
        {v:'vehicle', l:'Get Vehicle'}, {v:'business_profit', l:'Business Profit'},
        {v:'partnership', l:'Business Partnership'}, {v:'election', l:'Win Election'},
        {v:'appeal', l:'Appeal Success'}, {v:'lost_item', l:'Recover Lost Item'},
        {v:'general_success', l:'General Success'}
    ];
    prashnaOptions.forEach(function(o){ html += '<option value="'+o.v+'">'+o.l+'</option>'; });
    html += '</select></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Query Date</label><input type="date" id="kp-prashna-date" value="'+today+'" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Query Time</label><input type="text" id="kp-prashna-time" value="'+new Date().toTimeString().slice(0,5)+'" placeholder="HH:MM" maxlength="10" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:100px"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Place</label><input type="text" id="kp-prashna-place" value="'+(body.place||'Ujjain, Madhya Pradesh, India')+'" list="city-suggestions" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:200px"></div>';
    html += '<button id="kp-prashna-fetch" class="btn-primary" style="font-size:0.82rem;padding:7px 16px;font-weight:700">GET ANSWER</button>';
    html += '</div>';
    html += '<div id="kp-prashna-result"><p style="color:var(--text-muted);font-style:italic">Enter KP number, select question type, and click "GET ANSWER"</p></div>';
    html += '</div>';

    /* ═══ EVENT PROMISE CHECKER (inside Prashna tab) ═════════ */
    html += '<div class="card" style="margin-top:16px;border:1px solid var(--gold)">';
    html += '<h3 style="color:var(--gold-light);margin-bottom:6px">Event Promise Checker — Will It Happen?</h3>';
    html += '<p style="color:var(--text-dim);font-size:0.78rem;margin-bottom:10px">Check if the natal chart PROMISES a specific event using KP 3-way sub-lord theory. Examines the primary cusp sub-lord, its star lord, and sub-lord significations.</p>';

    // Question type dropdown
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:10px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Event Type</label><select id="kp-promise-qtype" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.85rem;min-width:200px">';
    prashnaOptions.forEach(function(o){ html += '<option value="'+o.v+'">'+o.l+'</option>'; });
    html += '</select></div>';
    html += '<button id="kp-promise-fetch" class="btn-primary" style="font-size:0.82rem;padding:7px 16px;font-weight:700">CHECK PROMISE</button>';
    html += '</div>';
    html += '<div id="kp-promise-result"><p style="color:var(--text-muted);font-style:italic">Select an event type and click "CHECK PROMISE" to analyse the natal chart</p></div>';
    html += '</div>';

    /* ═══ DBA TIMING FINDER (inside Prashna tab) ═════════════ */
    html += '<div class="card" style="margin-top:16px;border:1px solid #333">';
    html += '<h3 style="color:var(--gold-light);margin-bottom:6px">DBA Timing Finder — When Will It Happen?</h3>';
    html += '<p style="color:var(--text-dim);font-size:0.78rem;margin-bottom:10px">Find the best future Dasha-Bhukti-Antara windows for any event. Uses natal chart significators to identify periods when DBA lords activate the relevant houses.</p>';

    // Mode toggle
    html += '<div style="display:flex;gap:8px;margin-bottom:10px">';
    html += '<label style="font-size:0.78rem;color:var(--text-dim);display:flex;align-items:center;gap:4px"><input type="radio" name="dba-mode" value="natal" checked> Natal (Birth Data)</label>';
    html += '<label style="font-size:0.78rem;color:var(--text-dim);display:flex;align-items:center;gap:4px"><input type="radio" name="dba-mode" value="prashna"> Prashna (Horary)</label>';
    html += '</div>';

    // Inputs row 1
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:10px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Question Type</label>';
    html += '<select id="kp-dba-qtype" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;min-width:180px">';
    prashnaOptions.forEach(function(o){ html += '<option value="'+o.v+'">'+o.l+'</option>'; });
    html += '</select></div>';
    html += '<div id="dba-kp-num-wrap" style="display:none;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">KP Number</label><input type="number" id="kp-dba-num" min="1" max="249" placeholder="1–249" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.9rem;width:90px;font-weight:700"></div>';
    html += '</div>';

    // Date range row
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:10px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Search From</label><input type="date" id="kp-dba-start" value="'+today+'" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem"></div>';
    // Default end = 2 years from now
    var twoYearsLater = new Date(); twoYearsLater.setFullYear(twoYearsLater.getFullYear()+2);
    var endDefault = twoYearsLater.toISOString().slice(0,10);
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Search Until</label><input type="date" id="kp-dba-end" value="'+endDefault+'" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--gold-light)">Validate Event Date</label><input type="date" id="kp-dba-validate" placeholder="Known event date" style="padding:6px 8px;border-radius:4px;border:1px solid var(--gold);background:#1a1a2e;color:#eee;font-size:0.82rem" title="Enter a known past event date to check if DBA was favorable"></div>';
    html += '<button id="kp-dba-fetch" class="btn-primary" style="font-size:0.82rem;padding:7px 16px;font-weight:700">FIND BEST TIMING</button>';
    html += '</div>';
    html += '<div id="kp-dba-result"><p style="color:var(--text-muted);font-style:italic">Select question type, set date range, and click "FIND BEST TIMING". Optionally enter a known event date to validate.</p></div>';
    html += '</div>';

    html += '</div>';

    /* ═══ TAB: Match Prediction ════════════════════════════════ */
    html += '<div class="kp-tab-pane" id="kp-match" style="display:none">';
    html += '<div class="card"><h2 style="color:var(--gold-light)">KP Match Prediction — Who Wins?</h2>';
    html += '<p style="color:var(--text-dim);font-size:0.8rem;margin-bottom:12px">Think of a number 1–249 while asking "Who will win?" H6 sub-lord decides victory, H12 = opponent\'s victory. Ruling Planets confirm timing.</p>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:14px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">KP Number (1–249)</label><input type="number" id="kp-match-num" min="1" max="249" placeholder="1–249" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.9rem;width:90px;font-weight:700"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Match Type</label>';
    html += '<select id="kp-match-type" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem">';
    var matchTypes = [
        {v:'cricket', l:'Cricket'}, {v:'football', l:'Football'},
        {v:'tennis', l:'Tennis'}, {v:'kabaddi', l:'Kabaddi'},
        {v:'hockey', l:'Hockey'}, {v:'boxing', l:'Boxing / Wrestling'},
        {v:'election', l:'Election'}, {v:'competition', l:'General Competition'},
        {v:'court_case', l:'Court Case'}, {v:'business', l:'Business Competition'},
        {v:'exam', l:'Competitive Exam'}
    ];
    matchTypes.forEach(function(o){ html += '<option value="'+o.v+'">'+o.l+'</option>'; });
    html += '</select></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Your Team / Side</label><input type="text" id="kp-match-teama" value="" placeholder="e.g. India, CSK" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:140px"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Opponent</label><input type="text" id="kp-match-teamb" value="" placeholder="e.g. Australia, MI" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:140px"></div>';
    html += '</div>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:14px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Query Date</label><input type="date" id="kp-match-date" value="'+today+'" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Query Time</label><input type="text" id="kp-match-time" value="'+new Date().toTimeString().slice(0,5)+'" placeholder="HH:MM" maxlength="10" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:100px"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Place</label><input type="text" id="kp-match-place" value="'+(body.place||'Ujjain, Madhya Pradesh, India')+'" list="city-suggestions" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:200px"></div>';
    html += '<button id="kp-match-fetch" class="btn-primary" style="font-size:0.82rem;padding:7px 16px;font-weight:700">PREDICT WINNER</button>';
    html += '</div>';
    html += '<div id="kp-match-result"><p style="color:var(--text-muted);font-style:italic">Enter KP number, team names, and click "PREDICT WINNER"</p></div>';
    html += '</div>';

    /* ═══ TOSS PREDICTION (inside Match tab) ═══════════════════ */
    html += '<div class="card" style="margin-top:16px;border:1px solid #333">';
    html += '<h3 style="color:var(--gold-light);margin-bottom:6px">Toss Prediction — Who Wins the Toss?</h3>';
    html += '<p style="color:var(--text-dim);font-size:0.78rem;margin-bottom:10px">Think of a <b>SEPARATE</b> KP number (1–249) while asking "Who will win the toss?" Use the moment you think of the number — NOT the actual toss time.</p>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:10px">';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">KP Number for Toss</label><input type="number" id="kp-toss-num" min="1" max="249" placeholder="1–249" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.9rem;width:90px;font-weight:700"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Your Team</label><input type="text" id="kp-toss-teama" value="" placeholder="e.g. CSK" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:120px"></div>';
    html += '<div style="display:flex;flex-direction:column;gap:2px"><label style="font-size:0.7rem;color:var(--text-dim)">Opponent</label><input type="text" id="kp-toss-teamb" value="" placeholder="e.g. MI" style="padding:6px 8px;border-radius:4px;border:1px solid #444;background:#1a1a2e;color:#eee;font-size:0.82rem;width:120px"></div>';
    html += '<button id="kp-toss-fetch" class="btn-primary" style="font-size:0.82rem;padding:7px 16px;font-weight:700">PREDICT TOSS</button>';
    html += '</div>';
    html += '<div id="kp-toss-result"><p style="color:var(--text-muted);font-style:italic">Enter a separate KP number for toss prediction</p></div>';
    html += '</div>';
    html += '</div>'; /* end kp-match tab pane */

    resultEl.innerHTML = html;

    /* ═══ Sub-tab switching logic ═══════════════════════════════ */
    resultEl.querySelectorAll('.kp-stab').forEach(function(btn){
        btn.addEventListener('click', function(){
            resultEl.querySelectorAll('.kp-stab').forEach(function(b){
                b.classList.remove('active');
                b.style.background = '#1a1a2e';
                b.style.color = 'var(--text-muted)';
            });
            this.classList.add('active');
            this.style.background = 'var(--gold)';
            this.style.color = '#000';
            resultEl.querySelectorAll('.kp-tab-pane').forEach(function(p){ p.style.display = 'none'; });
            var target = document.getElementById(this.dataset.kptab);
            if (target) target.style.display = 'block';
        });
    });

    /* ═══ Draw KP Diamond Charts ═══════════════════════════════ */
    /* ═══ Draw proper North Indian Diamond Charts ═══════════════ */
    (function drawKPCharts(){
        var chartEl = document.getElementById('kp-diamond-chart');
        var rasiEl = document.getElementById('kp-rasi-chart');
        if (!chartEl || !rasiEl) return;

        var signAbbr = {Aries:'Ari',Taurus:'Tau',Gemini:'Gem',Cancer:'Can',Leo:'Leo',Virgo:'Vir',Libra:'Lib',Scorpio:'Sco',Sagittarius:'Sag',Capricorn:'Cap',Aquarius:'Aqu',Pisces:'Pis'};
        var signList = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];

        function buildHouseData(planets, houses) {
            var hd = {};
            for (var i = 1; i <= 12; i++) hd[i] = { sign: '', planets: [] };
            if (houses && houses.length) {
                houses.forEach(function(h){ hd[h.house].sign = h.sign || ''; });
            }
            if (planets && planets.length) {
                var ascSign = (houses && houses.length) ? houses[0].sign : '';
                var ascIdx = signList.indexOf(ascSign);
                planets.forEach(function(p){
                    var pIdx = signList.indexOf(p.sign);
                    var hNum = ((pIdx - ascIdx + 12) % 12) + 1;
                    var abbr = p.planet.substr(0, 2);
                    if (p.planet === 'Mercury') abbr = 'Me';
                    if (p.planet === 'Mars') abbr = 'Ma';
                    if (p.planet === 'Moon') abbr = 'Mo';
                    var retro = (p.speed !== undefined && p.speed < 0) ? 'ᴿ' : '';
                    hd[hNum].planets.push(abbr + retro);
                });
            }
            return hd;
        }

        function drawNorthDiamond(container, houseData, title) {
            var w = 340, h = 340;
            var mx = w/2, my = h/2;
            /* North Indian diamond layout:
               Outer rectangle + two diagonals + inner diamond (midpoints connected) */
            var svg = '<svg viewBox="0 0 '+w+' '+h+'" xmlns="http://www.w3.org/2000/svg" style="max-width:340px;width:100%">';
            svg += '<rect width="'+w+'" height="'+h+'" fill="#0a0a1a" rx="6"/>';
            /* Outer border */
            svg += '<rect x="5" y="5" width="'+(w-10)+'" height="'+(h-10)+'" fill="none" stroke="#555" stroke-width="1.5" rx="2"/>';
            var L=5, R=w-5, T=5, B=h-5;
            /* Diagonals: corner to corner */
            svg += '<line x1="'+L+'" y1="'+T+'" x2="'+R+'" y2="'+B+'" stroke="#555" stroke-width="1"/>';
            svg += '<line x1="'+R+'" y1="'+T+'" x2="'+L+'" y2="'+B+'" stroke="#555" stroke-width="1"/>';
            /* Inner diamond: connect midpoints of sides */
            svg += '<polygon points="'+mx+','+T+' '+R+','+my+' '+mx+','+B+' '+L+','+my+'" fill="none" stroke="#555" stroke-width="1"/>';

            /* House text positions — North Indian (counter-clockwise from top):
               H1=top diamond, H2=upper-left, H3=left-upper, H4=left diamond,
               H5=left-lower, H6=lower-left, H7=bottom diamond, H8=lower-right,
               H9=right-lower, H10=right diamond, H11=right-upper, H12=upper-right */
            var hPos = [
                /* H1  */ {x:mx-20, y:T+25},
                /* H2  */ {x:L+10,  y:T+18},
                /* H3  */ {x:L+10,  y:my-25},
                /* H4  */ {x:L+10,  y:my+5},
                /* H5  */ {x:L+10,  y:B-45},
                /* H6  */ {x:mx-45, y:B-30},
                /* H7  */ {x:mx-20, y:B-48},
                /* H8  */ {x:R-70,  y:B-45},
                /* H9  */ {x:R-70,  y:my+5},
                /* H10 */ {x:R-70,  y:my-25},
                /* H11 */ {x:R-70,  y:T+18},
                /* H12 */ {x:mx+5,  y:T+18},
            ];

            for (var i = 1; i <= 12; i++) {
                var pos = hPos[i-1];
                var hInfo = houseData[i];
                var sAbbr = signAbbr[hInfo.sign] || '';
                /* House number + sign */
                svg += '<text x="'+pos.x+'" y="'+pos.y+'" fill="#d4a843" font-size="8" font-weight="700" font-family="monospace">'+i+'</text>';
                svg += '<text x="'+(pos.x+12)+'" y="'+pos.y+'" fill="#888" font-size="7" font-family="monospace">'+sAbbr+'</text>';
                /* Planets */
                var pText = hInfo.planets.join(' ');
                if (pText) {
                    svg += '<text x="'+pos.x+'" y="'+(pos.y+12)+'" fill="#e0e0e0" font-size="8" font-weight="600" font-family="sans-serif">'+pText+'</text>';
                }
            }
            /* Ascendant marker — small triangle at top of H1 */
            svg += '<polygon points="'+(mx-4)+','+(T+2)+' '+(mx+4)+','+(T+2)+' '+mx+','+(T+10)+'" fill="#d4a843"/>';
            svg += '<text x="'+(mx+8)+'" y="'+(T+10)+'" fill="#d4a843" font-size="7" font-weight="700">Asc</text>';
            svg += '</svg>';
            container.innerHTML = svg;
        }

        var hd = buildHouseData(allPlanets, allHouses);
        drawNorthDiamond(chartEl, hd, 'KP Chart');
        drawNorthDiamond(rasiEl, hd, 'Rasi Chart');
    })();

    /* ═══ Ruling Planets button handlers (NOW + custom date/time) ═══ */
    function fetchRP(useCustom) {
        var resultDiv = document.getElementById('kp-currp-result');
        resultDiv.innerHTML = '<p style="color:var(--text-muted)">Calculating Ruling Planets...</p>';
        var rpBody = {
            name: body.name,
            date: body.date,
            time: body.time,
            place: document.getElementById('kp-rp-place').value || body.place,
            ayanamsa: 'krishnamurti'
        };
        if (useCustom) {
            rpBody.rp_date = document.getElementById('kp-rp-date').value;
            rpBody.rp_time = parseTimeInput(document.getElementById('kp-rp-time').value);
        }
        fetch(API + '/kp/current-rp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(rpBody)
        }).then(function(resp){
            if (!resp.ok) throw new Error('API error ' + resp.status);
            return resp.json();
        }).then(function(crp){
            var chtml = '';
            var label = crp.is_realtime ? 'Real-time (NOW)' : 'For: ' + (crp.query_date||'') + ' ' + (crp.query_time||'');
            chtml += '<div style="background:rgba(212,168,67,0.08);border:1px solid var(--gold);border-radius:6px;padding:10px;margin-bottom:12px">';
            chtml += '<div style="font-size:0.82rem;font-weight:700;color:var(--gold)">'+(crp.datetime||label)+', '+(crp.place||'')+'</div>';
            chtml += '<div style="font-size:0.72rem;color:var(--text-dim)">'+(crp.coordinates||'')+' &nbsp;|&nbsp; '+label+'</div>';
            chtml += '</div>';
            chtml += '<table class="data-table" style="font-size:0.88rem">';
            chtml += '<thead><tr><th style="text-align:left">Source</th><th style="text-align:right">Planet</th></tr></thead><tbody>';
            (crp.rp_rows||[]).forEach(function(r){
                chtml += '<tr><td style="font-weight:600">'+r.source+'</td>';
                chtml += '<td style="text-align:right;font-weight:700;color:'+pColor(r.planet)+'">'+r.planet.substr(0,3).toUpperCase()+'</td></tr>';
            });
            chtml += '</tbody></table>';
            if (crp.ranked && crp.ranked.length) {
                chtml += '<div style="margin-top:10px;font-size:0.82rem;color:var(--text)"><strong>Ranked:</strong> ';
                crp.ranked.forEach(function(r, idx){
                    if (idx > 0) chtml += ', ';
                    chtml += '<span style="color:'+pColor(r.planet)+';font-weight:700">'+r.planet+'</span><span style="color:var(--text-dim)">('+r.count+'x)</span>';
                });
                chtml += '</div>';
            }
            resultDiv.innerHTML = chtml;
        }).catch(function(err){
            resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
        });
    }
    var rpNowBtn = document.getElementById('kp-fetch-currp-now');
    var rpCustomBtn = document.getElementById('kp-fetch-currp-custom');
    if (rpNowBtn) rpNowBtn.addEventListener('click', function(){ fetchRP(false); });
    if (rpCustomBtn) rpCustomBtn.addEventListener('click', function(){ fetchRP(true); });

    /* ═══ KP Horary inline fetch handler ═════════════════════ */
    var horaryBtn = document.getElementById('kp-horary-fetch');
    if (horaryBtn) {
        horaryBtn.addEventListener('click', async function(){
            var kpNum = parseInt(document.getElementById('kp-horary-inline').value);
            if (!kpNum || kpNum < 1 || kpNum > 249) {
                document.getElementById('kp-horary-result').innerHTML = '<p style="color:var(--red)">Please enter a valid KP number between 1 and 249</p>';
                return;
            }
            var resultDiv = document.getElementById('kp-horary-result');
            resultDiv.innerHTML = '<p style="color:var(--text-muted)">Running Horary Analysis for KP #'+kpNum+'...</p>';
            try {
                var hBody = {
                    name: body.name,
                    date: document.getElementById('kp-horary-date').value || body.date,
                    time: parseTimeInput(document.getElementById('kp-horary-time').value) || body.time,
                    place: document.getElementById('kp-horary-place').value || body.place,
                    ayanamsa: 'krishnamurti',
                    kp_horary_number: kpNum
                };
                var resp = await fetch(API + '/kp', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(hBody)
                });
                if (!resp.ok) throw new Error('API error ' + resp.status);
                var hData = await resp.json();
                var h = hData.kp_analysis && hData.kp_analysis.horary ? hData.kp_analysis.horary : null;
                if (!h) { resultDiv.innerHTML = '<p style="color:var(--red)">No horary data returned</p>'; return; }

                var hhtml = '';
                hhtml += '<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:14px">';
                hhtml += '<div class="metric"><div class="label">KP Number</div><div class="value gold">'+h.input_number+'</div></div>';
                hhtml += '<div class="metric"><div class="label">Sign</div><div class="value">'+h.sign+'</div></div>';
                hhtml += '<div class="metric"><div class="label">Nakshatra</div><div class="value">'+h.nakshatra+' P'+h.pada+'</div></div>';
                hhtml += '<div class="metric"><div class="label">Sign Lord</div><div class="value" style="color:'+pColor(h.sign_lord)+'">'+h.sign_lord+'</div></div>';
                hhtml += '<div class="metric"><div class="label">Star Lord (NL)</div><div class="value" style="color:'+pColor(h.star_lord)+'">'+h.star_lord+'</div></div>';
                hhtml += '<div class="metric"><div class="label">Sub Lord (SL)</div><div class="value" style="color:'+pColor(h.sub_lord)+'">'+h.sub_lord+'</div></div>';
                hhtml += '<div class="metric"><div class="label">Sub-Sub Lord (SSL)</div><div class="value" style="color:'+pColor(h.sub_sub_lord)+'">'+h.sub_sub_lord+'</div></div>';
                hhtml += '</div>';

                /* Show cuspal sub-lord verdicts from the full KP analysis */
                var kpa = hData.kp_analysis;
                if (kpa && kpa.cuspal_sublords && kpa.cuspal_sublords.length) {
                    hhtml += '<h3 style="color:var(--gold-light);margin-top:16px;font-size:0.9rem">Cuspal Sub-Lord Verdicts</h3>';
                    hhtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                    hhtml += '<thead><tr><th>Cusp</th><th>Sign</th><th>Star Lord</th><th>Sub Lord</th><th>Sub-Sub</th><th>Verdict</th></tr></thead><tbody>';
                    kpa.cuspal_sublords.forEach(function(c){
                        var vColor = c.verdict === 'PROMISE' ? 'var(--green)' : c.verdict === 'DENIAL' ? 'var(--red)' : 'var(--text-muted)';
                        hhtml += '<tr>';
                        hhtml += '<td style="font-weight:700">H'+c.house+'</td>';
                        hhtml += '<td>'+c.sign+'</td>';
                        hhtml += '<td style="color:'+pColor(c.star_lord)+'">'+c.star_lord+'</td>';
                        hhtml += '<td style="font-weight:700;color:'+pColor(c.sub_lord)+'">'+c.sub_lord+'</td>';
                        hhtml += '<td style="color:'+pColor(c.sub_sub_lord||'')+'">'+( c.sub_sub_lord||'-')+'</td>';
                        hhtml += '<td style="font-weight:700;color:'+vColor+'">'+( c.verdict||'-')+'</td>';
                        hhtml += '</tr>';
                    });
                    hhtml += '</tbody></table></div>';
                }

                /* Show significators summary */
                if (kpa && kpa.significators && kpa.significators.length) {
                    hhtml += '<h3 style="color:var(--gold-light);margin-top:16px;font-size:0.9rem">Planet Significators (4-Step)</h3>';
                    hhtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                    hhtml += '<thead><tr><th>Planet</th><th>Signified Houses</th><th>Strong Houses</th></tr></thead><tbody>';
                    kpa.significators.forEach(function(s){
                        var houses = (s.signified_houses||[]).join(', ');
                        var strong = (s.strong_houses||s.signified_houses||[]).join(', ');
                        hhtml += '<tr><td style="font-weight:700;color:'+pColor(s.planet)+'">'+s.planet+'</td>';
                        hhtml += '<td>'+houses+'</td><td>'+strong+'</td></tr>';
                    });
                    hhtml += '</tbody></table></div>';
                }

                /* Show ruling planets if available */
                if (kpa && kpa.ruling_planets && kpa.ruling_planets.ranked) {
                    hhtml += '<h3 style="color:var(--gold-light);margin-top:16px;font-size:0.9rem">Ruling Planets</h3>';
                    hhtml += '<div style="font-size:0.82rem;color:var(--text)">';
                    kpa.ruling_planets.ranked.forEach(function(r, idx){
                        if (idx > 0) hhtml += ', ';
                        hhtml += '<span style="color:'+pColor(r.planet)+';font-weight:700">'+r.planet+'</span><span style="color:var(--text-dim)">('+r.count+'x)</span>';
                    });
                    hhtml += '</div>';
                }

                /* Financial house groups */
                if (kpa && kpa.financial) {
                    hhtml += '<h3 style="color:var(--gold-light);margin-top:16px;font-size:0.9rem">Financial House Groups</h3>';
                    hhtml += '<div style="display:flex;gap:12px;flex-wrap:wrap">';
                    Object.keys(kpa.financial).forEach(function(group){
                        var fg = kpa.financial[group];
                        if (!fg) return;
                        var verdict = fg.verdict || fg.signal || '-';
                        var vClr = verdict === 'BULLISH' || verdict === 'PROMISE' ? 'var(--green)' : verdict === 'BEARISH' || verdict === 'DENIAL' ? 'var(--red)' : 'var(--gold)';
                        hhtml += '<div class="metric"><div class="label">'+group+'</div><div class="value" style="color:'+vClr+';font-size:0.85rem">'+verdict+'</div></div>';
                    });
                    hhtml += '</div>';
                }

                resultDiv.innerHTML = hhtml;
            } catch(err) {
                resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
            }
        });
    }

    /* ═══ Moon NL/SL/SSL Timeline handler ═════════════════════ */
    var moonNLBtn = document.getElementById('kp-fetch-moonnl');
    if (moonNLBtn) {
        moonNLBtn.addEventListener('click', async function(){
            var resultDiv = document.getElementById('kp-moonnl-result');
            resultDiv.innerHTML = '<p style="color:var(--text-muted)">Calculating Moon NL/SL/SSL timeline... (this may take a moment)</p>';
            try {
                var nlBody = {
                    name: body.name,
                    date: body.date,
                    time: body.time,
                    place: document.getElementById('kp-moonnl-place').value || body.place,
                    ayanamsa: 'krishnamurti',
                    query_date: document.getElementById('kp-moonnl-date').value,
                    query_time: parseTimeInput(document.getElementById('kp-moonnl-time').value),
                    duration_hours: parseInt(document.getElementById('kp-moonnl-hours').value) || 24
                };
                var resp = await fetch(API + '/kp/daily-moon-nl', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(nlBody)
                });
                if (!resp.ok) throw new Error('API error ' + resp.status);
                var nlData = await resp.json();
                var trs = nlData.transitions || [];

                var nhtml = '';
                nhtml += '<div style="background:rgba(212,168,67,0.08);border:1px solid var(--gold);border-radius:6px;padding:10px;margin-bottom:12px">';
                nhtml += '<div style="font-size:0.82rem;font-weight:700;color:var(--gold)">Moon NL/SL/SSL Timeline — '+nlData.query_date+' starting '+nlData.query_time+'</div>';
                nhtml += '<div style="font-size:0.72rem;color:var(--text-dim)">'+(nlData.place||'')+' | '+nlData.duration_hours+'h | '+nlData.total_transitions+' transitions | '+(nlData.coordinates||'')+'</div>';
                nhtml += '</div>';

                nhtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem;width:100%">';
                nhtml += '<thead><tr>';
                nhtml += '<th style="text-align:left">From</th>';
                nhtml += '<th style="text-align:left">To</th>';
                nhtml += '<th style="text-align:right">Min</th>';
                nhtml += '<th style="text-align:left">Sign</th>';
                nhtml += '<th style="text-align:left">Nakshatra</th>';
                nhtml += '<th style="text-align:center">P</th>';
                nhtml += '<th style="text-align:left">NL</th>';
                nhtml += '<th style="text-align:left">SL</th>';
                nhtml += '<th style="text-align:left">SSL</th>';
                nhtml += '<th style="text-align:center">KP#</th>';
                nhtml += '<th style="text-align:left">Moon DMS</th>';
                nhtml += '</tr></thead><tbody>';

                var prevNL = '';
                trs.forEach(function(t, idx){
                    var nlChanged = t.nl !== prevNL;
                    var rowBg = nlChanged ? 'rgba(212,168,67,0.08)' : (idx % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)');
                    var borderTop = nlChanged && idx > 0 ? 'border-top:2px solid var(--gold);' : '';
                    nhtml += '<tr style="background:'+rowBg+';'+borderTop+'">';
                    nhtml += '<td style="font-family:monospace;font-weight:600">'+t.start_time+'</td>';
                    nhtml += '<td style="font-family:monospace">'+t.end_time+'</td>';
                    nhtml += '<td style="text-align:right;color:var(--text-dim)">'+t.duration_min+'</td>';
                    nhtml += '<td>'+t.sign+'</td>';
                    nhtml += '<td style="font-size:0.72rem">'+t.nakshatra+'</td>';
                    nhtml += '<td style="text-align:center">'+t.pada+'</td>';
                    nhtml += '<td style="font-weight:700;color:'+pColor(t.nl)+'">'+t.nl+'</td>';
                    nhtml += '<td style="font-weight:700;color:'+pColor(t.sl)+'">'+t.sl+'</td>';
                    nhtml += '<td style="font-weight:700;color:'+pColor(t.ssl)+'">'+t.ssl+'</td>';
                    nhtml += '<td style="text-align:center;color:var(--text-dim)">'+t.kp_number+'</td>';
                    nhtml += '<td style="font-family:monospace;font-size:0.72rem">'+t.start_dms+' → '+t.end_dms+'</td>';
                    nhtml += '</tr>';
                    prevNL = t.nl;
                });
                nhtml += '</tbody></table></div>';
                resultDiv.innerHTML = nhtml;
            } catch(err) {
                resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
            }
        });
    }

    /* ═══ Prashna Yes/No handler ═════════════════════════════════ */
    var prashnaBtn = document.getElementById('kp-prashna-fetch');
    if (prashnaBtn) {
        prashnaBtn.addEventListener('click', async function(){
            var kpNum = parseInt(document.getElementById('kp-prashna-num').value);
            if (!kpNum || kpNum < 1 || kpNum > 249) {
                document.getElementById('kp-prashna-result').innerHTML = '<p style="color:var(--red)">Please enter a valid KP number between 1 and 249</p>';
                return;
            }
            var qType = document.getElementById('kp-prashna-qtype').value;
            var resultDiv = document.getElementById('kp-prashna-result');
            resultDiv.innerHTML = '<p style="color:var(--text-muted)">Analyzing Prashna for KP #'+kpNum+' ('+qType+')...</p>';
            try {
                var pBody = {
                    name: body.name,
                    date: body.date,
                    time: body.time,
                    place: document.getElementById('kp-prashna-place').value || body.place,
                    ayanamsa: 'krishnamurti',
                    kp_number: kpNum,
                    question_type: qType,
                    query_date: document.getElementById('kp-prashna-date').value,
                    query_time: parseTimeInput(document.getElementById('kp-prashna-time').value)
                };
                var resp = await fetch(API + '/kp/prashna-yesno', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(pBody)
                });
                if (!resp.ok) throw new Error('API error ' + resp.status);
                var pData = await resp.json();
                var pr = pData.prashna;
                if (!pr) { resultDiv.innerHTML = '<p style="color:var(--red)">No prashna data returned</p>'; return; }

                var phtml = '';

                /* ── Big verdict banner ── */
                var vBg = pr.verdict_type === 'positive' ? 'rgba(0,200,100,0.15)' : pr.verdict_type === 'negative' ? 'rgba(255,60,60,0.15)' : 'rgba(212,168,67,0.15)';
                var vBorder = pr.verdict_type === 'positive' ? '#00c864' : pr.verdict_type === 'negative' ? '#ff3c3c' : 'var(--gold)';
                var vColor = pr.verdict_type === 'positive' ? '#00e874' : pr.verdict_type === 'negative' ? '#ff4444' : 'var(--gold)';
                phtml += '<div style="background:'+vBg+';border:2px solid '+vBorder+';border-radius:10px;padding:20px;text-align:center;margin-bottom:18px">';
                phtml += '<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:4px">'+pr.question_label+'</div>';
                phtml += '<div style="font-size:2.4rem;font-weight:900;color:'+vColor+';letter-spacing:2px">'+pr.verdict+'</div>';
                phtml += '<div style="font-size:0.85rem;color:var(--text-dim);margin-top:4px">Confidence: '+pr.confidence_score+'%</div>';
                phtml += '</div>';

                /* ── KP Horary details ── */
                if (pr.horary_kp) {
                    var hk = pr.horary_kp;
                    phtml += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px">';
                    phtml += '<div class="metric"><div class="label">KP #</div><div class="value gold">'+pr.kp_number+'</div></div>';
                    phtml += '<div class="metric"><div class="label">Sign</div><div class="value">'+hk.sign+'</div></div>';
                    phtml += '<div class="metric"><div class="label">Nakshatra</div><div class="value">'+hk.nakshatra+' P'+hk.pada+'</div></div>';
                    phtml += '<div class="metric"><div class="label">Sign Lord</div><div class="value" style="color:'+pColor(hk.sign_lord)+'">'+hk.sign_lord+'</div></div>';
                    phtml += '<div class="metric"><div class="label">Star Lord</div><div class="value" style="color:'+pColor(hk.star_lord)+'">'+hk.star_lord+'</div></div>';
                    phtml += '<div class="metric"><div class="label">Sub Lord</div><div class="value" style="color:'+pColor(hk.sub_lord)+'">'+hk.sub_lord+'</div></div>';
                    phtml += '<div class="metric"><div class="label">Sub-Sub</div><div class="value" style="color:'+pColor(hk.sub_sub_lord)+'">'+hk.sub_sub_lord+'</div></div>';
                    phtml += '</div>';
                }

                /* ── Primary house analysis ── */
                phtml += '<h3 style="color:var(--gold-light);margin-top:14px;font-size:0.9rem">Primary House Analysis (H'+pr.primary_house+')</h3>';
                phtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.82rem"><tbody>';
                phtml += '<tr><td style="color:var(--text-dim);width:200px">Primary House</td><td style="font-weight:700">House '+pr.primary_house+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Cusp Sub Lord</td><td style="font-weight:700;color:'+pColor(pr.cusp_sub_lord)+'">'+pr.cusp_sub_lord+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Cusp Star Lord</td><td style="color:'+pColor(pr.cusp_star_lord)+'">'+pr.cusp_star_lord+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Sub Lord Signifies Houses</td><td>'+(pr.sub_lord_signifies||[]).join(', ')+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Conductive Houses</td><td style="color:var(--green)">'+(pr.conductive_houses||[]).join(', ')+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Detrimental Houses</td><td style="color:var(--red)">'+(pr.detrimental_houses||[]).join(', ')+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Conductive Match</td><td style="font-weight:700;color:var(--green)">'+(pr.conductive_match && pr.conductive_match.length ? pr.conductive_match.join(', ') : 'None')+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Detrimental Match</td><td style="font-weight:700;color:var(--red)">'+(pr.detrimental_match && pr.detrimental_match.length ? pr.detrimental_match.join(', ') : 'None')+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Sub Lord Retrograde?</td><td style="color:'+(pr.is_sub_lord_retro ? 'var(--red)' : 'var(--green)')+'">'+( pr.is_sub_lord_retro ? 'YES (Retro)' : 'No (Direct)')+'</td></tr>';
                phtml += '<tr><td style="color:var(--text-dim)">Star Lord Retrograde?</td><td style="color:'+(pr.is_star_lord_retro ? 'var(--red)' : 'var(--green)')+'">'+( pr.is_star_lord_retro ? 'YES (Retro)' : 'No (Direct)')+'</td></tr>';
                phtml += '</tbody></table></div>';

                /* ── Group cusp analysis ── */
                if (pr.group_cusp_analysis && pr.group_cusp_analysis.length) {
                    phtml += '<h3 style="color:var(--gold-light);margin-top:14px;font-size:0.9rem">Conductive House Cusps</h3>';
                    phtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                    phtml += '<thead><tr><th>House</th><th>Sub Lord</th><th>Signifies</th><th>Verdict</th></tr></thead><tbody>';
                    pr.group_cusp_analysis.forEach(function(gc){
                        var gcColor = gc.verdict === 'PROMISE' ? 'var(--green)' : gc.verdict === 'DENIAL' ? 'var(--red)' : gc.verdict === 'MIXED' ? 'var(--gold)' : 'var(--text-dim)';
                        phtml += '<tr><td style="font-weight:700">H'+gc.house+'</td>';
                        phtml += '<td style="color:'+pColor(gc.sub_lord)+'">'+gc.sub_lord+'</td>';
                        phtml += '<td>'+(gc.signifies||[]).join(', ')+'</td>';
                        phtml += '<td style="font-weight:700;color:'+gcColor+'">'+gc.verdict+'</td></tr>';
                    });
                    phtml += '</tbody></table></div>';
                }

                /* ── Ruling Planets ── */
                if (pr.ruling_planets) {
                    var rp = pr.ruling_planets;
                    phtml += '<h3 style="color:var(--gold-light);margin-top:14px;font-size:0.9rem">Ruling Planets at Query Moment</h3>';
                    phtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                    phtml += '<thead><tr><th>Source</th><th>Planet</th></tr></thead><tbody>';
                    (rp.rp_rows||[]).forEach(function(r){
                        phtml += '<tr><td style="color:var(--text-dim)">'+r.source+'</td>';
                        phtml += '<td style="font-weight:700;color:'+pColor(r.planet)+'">'+r.planet+'</td></tr>';
                    });
                    phtml += '</tbody></table></div>';

                    if (rp.ranked && rp.ranked.length) {
                        phtml += '<div style="margin-top:8px;font-size:0.82rem"><strong style="color:var(--gold)">Ranked RPs: </strong>';
                        rp.ranked.forEach(function(r, idx){
                            if (idx > 0) phtml += ', ';
                            phtml += '<span style="color:'+pColor(r.planet)+';font-weight:700">'+r.planet+'</span><span style="color:var(--text-dim)">('+r.count+'x)</span>';
                        });
                        phtml += '</div>';
                    }
                }

                /* ── Fruitful Significators ── */
                if (pr.fruitful_significators && pr.fruitful_significators.length) {
                    phtml += '<div style="margin-top:10px;padding:10px;background:rgba(0,200,100,0.08);border:1px solid var(--green);border-radius:6px">';
                    phtml += '<div style="font-size:0.82rem;font-weight:700;color:var(--green)">Fruitful Significators (RP-matched): ';
                    pr.fruitful_significators.forEach(function(f, idx){
                        if (idx > 0) phtml += ', ';
                        phtml += '<span style="color:'+pColor(f)+'">'+f+'</span>';
                    });
                    phtml += '</div></div>';
                }

                /* ── Reasoning ── */
                if (pr.reasons && pr.reasons.length) {
                    phtml += '<h3 style="color:var(--gold-light);margin-top:14px;font-size:0.9rem">Reasoning</h3>';
                    phtml += '<div style="font-size:0.82rem;color:var(--text)">';
                    pr.reasons.forEach(function(r, idx){
                        var icon = r.indexOf('WARNING') >= 0 ? '&#9888;' : r.indexOf('STRONG') >= 0 ? '&#10003;' : r.indexOf('WEAK') >= 0 ? '&#10007;' : '&#8226;';
                        var rColor = r.indexOf('WARNING') >= 0 ? 'var(--red)' : r.indexOf('STRONG') >= 0 ? 'var(--green)' : r.indexOf('WEAK') >= 0 ? 'var(--red)' : 'var(--text)';
                        phtml += '<div style="margin-bottom:6px;color:'+rColor+'">'+icon+' '+r+'</div>';
                    });
                    phtml += '</div>';
                }

                resultDiv.innerHTML = phtml;
            } catch(err) {
                resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
            }
        });
    }

    /* ═══ Event Promise Checker handler ═══════════════════════════ */
    var promiseBtn = document.getElementById('kp-promise-fetch');
    if (promiseBtn) {
        promiseBtn.addEventListener('click', async function(){
            var qType = document.getElementById('kp-promise-qtype').value;
            var resultDiv = document.getElementById('kp-promise-result');
            resultDiv.innerHTML = '<p style="color:var(--text-muted)">Checking chart promise...</p>';

            try {
                var promBody = {
                    name: body.name,
                    date: body.date,
                    time: body.time,
                    place: body.place,
                    ayanamsa: 'krishnamurti',
                    question_type: qType
                };

                var resp = await fetch(API + '/kp/event-promise', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(promBody)
                });
                if (!resp.ok) {
                    var errBody = await resp.json().catch(function(){ return {}; });
                    throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
                }
                var pData = await resp.json();
                var pr = pData.promise;
                if (!pr) { resultDiv.innerHTML = '<p style="color:var(--red)">No promise data returned</p>'; return; }

                var phtml = '';

                /* ── Verdict Banner ── */
                var vColor = pr.verdict_color === 'green' ? '#00ff88' : pr.verdict_color === 'gold' ? 'var(--gold-light)' : pr.verdict_color === 'orange' ? '#ff9900' : '#ff4444';
                var vBg = pr.verdict_color === 'green' ? 'rgba(0,255,100,0.08)' : pr.verdict_color === 'gold' ? 'rgba(212,168,67,0.08)' : pr.verdict_color === 'orange' ? 'rgba(255,150,0,0.08)' : 'rgba(255,50,50,0.08)';
                var vBorder = pr.verdict_color === 'green' ? 'var(--green)' : pr.verdict_color === 'gold' ? 'var(--gold)' : pr.verdict_color === 'orange' ? '#ff9900' : 'var(--red)';
                phtml += '<div style="background:'+vBg+';border:2px solid '+vBorder+';border-radius:8px;padding:16px;margin-bottom:16px;text-align:center">';
                phtml += '<div style="font-size:0.82rem;color:var(--text-dim)">'+pr.label+'</div>';
                phtml += '<div style="font-size:1.5rem;font-weight:800;color:'+vColor+';margin:6px 0">'+pr.verdict+'</div>';
                phtml += '<div style="font-size:0.85rem;color:var(--text)">Promise Score: <b>'+pr.promise_score+'</b> | Levels Conductive: <b>'+pr.levels_conductive+'/3</b> | Levels Detrimental: <b>'+pr.levels_detrimental+'/3</b></div>';
                phtml += '<div style="font-size:0.78rem;color:var(--text-dim);margin-top:4px">Primary House: '+pr.primary_house+' | Conductive: '+pr.conductive.join(', ')+' | Detrimental: '+pr.detrimental.join(', ')+'</div>';
                phtml += '</div>';

                /* ── 3-Way Sub-Lord Analysis ── */
                phtml += '<div style="background:rgba(100,100,200,0.06);border:1px solid #444;border-radius:8px;padding:14px;margin-bottom:14px">';
                phtml += '<div style="font-size:0.9rem;font-weight:700;color:var(--gold-light);margin-bottom:10px">3-Way Sub-Lord Analysis — House '+pr.primary_house+' Cusp</div>';

                // Cusp info
                phtml += '<div style="font-size:0.82rem;margin-bottom:8px;color:var(--text-dim)">';
                phtml += 'Cusp Sign Lord: <span style="color:'+pColor(pr.cusp_sign_lord)+'">'+pr.cusp_sign_lord+'</span> | ';
                phtml += 'Star Lord: <span style="color:'+pColor(pr.cusp_star_lord)+'">'+pr.cusp_star_lord+'</span> | ';
                phtml += 'Sub Lord: <span style="color:'+pColor(pr.cusp_sub_lord)+'"><b>'+pr.cusp_sub_lord+'</b></span>';
                phtml += '</div>';

                // Level 1: Sub-lord
                var l1Color = pr.sub_lord_conductive.length > 0 ? (pr.sub_lord_detrimental.length > 0 ? '#ff9900' : 'var(--green)') : (pr.sub_lord_detrimental.length > 0 ? 'var(--red)' : 'var(--text-dim)');
                phtml += '<div style="border-left:3px solid '+l1Color+';padding:8px 12px;margin-bottom:8px;background:rgba(0,0,0,0.15);border-radius:0 6px 6px 0">';
                phtml += '<div style="font-size:0.82rem;font-weight:700;color:'+l1Color+'">LEVEL 1 — Sub-Lord: '+pr.cusp_sub_lord+'</div>';
                phtml += '<div style="font-size:0.78rem;margin-top:2px">Signifies houses: <b>'+pr.sub_lord_signifies.join(', ')+'</b></div>';
                if (pr.sub_lord_conductive.length) phtml += '<div style="font-size:0.78rem;color:var(--green)">Conductive hit: '+pr.sub_lord_conductive.join(', ')+' — PROMISE</div>';
                if (pr.sub_lord_detrimental.length) phtml += '<div style="font-size:0.78rem;color:var(--red)">Detrimental hit: '+pr.sub_lord_detrimental.join(', ')+' — DENIAL</div>';
                if (!pr.sub_lord_conductive.length && !pr.sub_lord_detrimental.length) phtml += '<div style="font-size:0.78rem;color:var(--text-dim)">No conductive or detrimental — neutral</div>';
                phtml += '</div>';

                // Level 2: Star lord
                var l2Color = pr.star_lord_conductive.length > 0 ? (pr.star_lord_detrimental.length > 0 ? '#ff9900' : 'var(--green)') : (pr.star_lord_detrimental.length > 0 ? 'var(--red)' : 'var(--text-dim)');
                phtml += '<div style="border-left:3px solid '+l2Color+';padding:8px 12px;margin-bottom:8px;background:rgba(0,0,0,0.15);border-radius:0 6px 6px 0">';
                phtml += '<div style="font-size:0.82rem;font-weight:700;color:'+l2Color+'">LEVEL 2 — Star Lord of '+pr.cusp_sub_lord+': '+pr.sl_natal_star_lord+'</div>';
                phtml += '<div style="font-size:0.78rem;margin-top:2px">Signifies houses: <b>'+pr.star_lord_signifies.join(', ')+'</b></div>';
                if (pr.star_lord_conductive.length) phtml += '<div style="font-size:0.78rem;color:var(--green)">Conductive hit: '+pr.star_lord_conductive.join(', ')+' — source supports</div>';
                if (pr.star_lord_detrimental.length) phtml += '<div style="font-size:0.78rem;color:var(--red)">Detrimental hit: '+pr.star_lord_detrimental.join(', ')+' — source opposes</div>';
                if (!pr.star_lord_conductive.length && !pr.star_lord_detrimental.length) phtml += '<div style="font-size:0.78rem;color:var(--text-dim)">Neutral source</div>';
                phtml += '</div>';

                // Level 3: Sub-sub lord
                var l3Color = pr.sub_sub_conductive.length > 0 ? (pr.sub_sub_detrimental.length > 0 ? '#ff9900' : 'var(--green)') : (pr.sub_sub_detrimental.length > 0 ? 'var(--red)' : 'var(--text-dim)');
                phtml += '<div style="border-left:3px solid '+l3Color+';padding:8px 12px;margin-bottom:8px;background:rgba(0,0,0,0.15);border-radius:0 6px 6px 0">';
                phtml += '<div style="font-size:0.82rem;font-weight:700;color:'+l3Color+'">LEVEL 3 — Sub-Lord of '+pr.cusp_sub_lord+': '+pr.sl_natal_sub_lord+'</div>';
                phtml += '<div style="font-size:0.78rem;margin-top:2px">Signifies houses: <b>'+pr.sub_sub_signifies.join(', ')+'</b></div>';
                if (pr.sub_sub_conductive.length) phtml += '<div style="font-size:0.78rem;color:var(--green)">Conductive hit: '+pr.sub_sub_conductive.join(', ')+' — delivery confirmed</div>';
                if (pr.sub_sub_detrimental.length) phtml += '<div style="font-size:0.78rem;color:var(--red)">Detrimental hit: '+pr.sub_sub_detrimental.join(', ')+' — delivery blocked</div>';
                if (!pr.sub_sub_conductive.length && !pr.sub_sub_detrimental.length) phtml += '<div style="font-size:0.78rem;color:var(--text-dim)">Neutral delivery</div>';
                phtml += '</div>';

                // Retrograde status
                if (pr.retro_tier > 0) {
                    var rColor = pr.retro_tier >= 2 ? 'var(--red)' : '#ff9900';
                    phtml += '<div style="border-left:3px solid '+rColor+';padding:8px 12px;margin-bottom:8px;background:rgba(255,0,0,0.05);border-radius:0 6px 6px 0">';
                    phtml += '<div style="font-size:0.82rem;font-weight:700;color:'+rColor+'">RETROGRADE — Tier '+pr.retro_tier+'</div>';
                    phtml += '<div style="font-size:0.78rem;margin-top:2px">'+pr.retro_detail+'</div>';
                    phtml += '</div>';
                }

                phtml += '</div>';

                /* ── All Conductive Cusp Analysis ── */
                if (pr.cusp_analysis && pr.cusp_analysis.length) {
                    phtml += '<details style="margin-bottom:14px"><summary style="cursor:pointer;color:var(--gold-light);font-size:0.85rem;font-weight:700">';
                    phtml += 'All Conductive House Cusp Analysis ('+pr.supporting_cusps+' support, '+pr.denying_cusps+' deny)';
                    phtml += '</summary>';
                    phtml += '<div style="overflow-x:auto;margin-top:6px"><table class="data-table" style="font-size:0.78rem">';
                    phtml += '<thead><tr><th>House</th><th>Sub-Lord</th><th>Signifies</th><th>Cond</th><th>Detr</th><th>Star Lord</th><th>Star Cond</th><th>Sub-Lord</th><th>Sub Cond</th><th>Status</th></tr></thead><tbody>';
                    pr.cusp_analysis.forEach(function(ca){
                        var stColor = ca.status === 'SUPPORTS' ? 'var(--green)' : ca.status === 'DENIES' ? 'var(--red)' : ca.status === 'MIXED' ? '#ff9900' : 'var(--text-dim)';
                        phtml += '<tr>';
                        phtml += '<td style="font-weight:700">'+ca.house+'</td>';
                        phtml += '<td style="color:'+pColor(ca.cusp_sub_lord)+'">'+ca.cusp_sub_lord+'</td>';
                        phtml += '<td>'+ca.signifies.join(',')+'</td>';
                        phtml += '<td style="color:var(--green)">'+(ca.conductive_hit.length ? ca.conductive_hit.join(',') : '-')+'</td>';
                        phtml += '<td style="color:var(--red)">'+(ca.detrimental_hit.length ? ca.detrimental_hit.join(',') : '-')+'</td>';
                        phtml += '<td style="color:'+pColor(ca.star_lord)+'">'+ca.star_lord+'</td>';
                        phtml += '<td style="color:var(--green)">'+(ca.star_conductive.length ? ca.star_conductive.join(',') : '-')+'</td>';
                        phtml += '<td style="color:'+pColor(ca.sub_lord)+'">'+ca.sub_lord+'</td>';
                        phtml += '<td style="color:var(--green)">'+(ca.sub_conductive.length ? ca.sub_conductive.join(',') : '-')+'</td>';
                        phtml += '<td style="color:'+stColor+';font-weight:700">'+ca.status+'</td>';
                        phtml += '</tr>';
                    });
                    phtml += '</tbody></table></div></details>';
                }

                /* ── Detailed Reasoning ── */
                if (pr.reasons && pr.reasons.length) {
                    phtml += '<details style="margin-bottom:10px"><summary style="cursor:pointer;color:var(--text-dim);font-size:0.82rem;font-weight:700">Detailed Reasoning</summary>';
                    phtml += '<div style="font-size:0.78rem;margin-top:6px">';
                    pr.reasons.forEach(function(r){
                        var rc = r.indexOf('PROMISE') >= 0 || r.indexOf('conductive') >= 0 || r.indexOf('supports') >= 0 || r.indexOf('confirmed') >= 0 || r.indexOf('self-promising') >= 0 ? 'var(--green)' : r.indexOf('DENIAL') >= 0 || r.indexOf('detrimental') >= 0 || r.indexOf('opposes') >= 0 || r.indexOf('blocked') >= 0 || r.indexOf('RETRO') >= 0 || r.indexOf('failure') >= 0 ? 'var(--red)' : r.indexOf('weakens') >= 0 || r.indexOf('mixed') >= 0 || r.indexOf('delayed') >= 0 ? '#ff9900' : 'var(--text)';
                        phtml += '<div style="color:'+rc+';margin-bottom:4px">'+r+'</div>';
                    });
                    phtml += '</div></details>';
                }

                resultDiv.innerHTML = phtml;
            } catch(err) {
                resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
            }
        });
    }

    /* ═══ DBA Timing Finder handler ════════════════════════════════ */
    // Mode toggle: show/hide KP number field
    var dbaRadios = document.querySelectorAll('input[name="dba-mode"]');
    dbaRadios.forEach(function(r){
        r.addEventListener('change', function(){
            var wrap = document.getElementById('dba-kp-num-wrap');
            if (wrap) wrap.style.display = this.value === 'prashna' ? 'flex' : 'none';
        });
    });

    var dbaBtn = document.getElementById('kp-dba-fetch');
    if (dbaBtn) {
        dbaBtn.addEventListener('click', async function(){
            var mode = document.querySelector('input[name="dba-mode"]:checked').value;
            var qType = document.getElementById('kp-dba-qtype').value;
            var resultDiv = document.getElementById('kp-dba-result');

            // Validate prashna mode needs KP number
            var kpNum = null;
            if (mode === 'prashna') {
                kpNum = parseInt(document.getElementById('kp-dba-num').value);
                if (!kpNum || kpNum < 1 || kpNum > 249) {
                    resultDiv.innerHTML = '<p style="color:var(--red)">Prashna mode requires a valid KP number (1–249)</p>';
                    return;
                }
            }

            resultDiv.innerHTML = '<p style="color:var(--text-muted)">Searching for best DBA timing windows...</p>';
            try {
                var dbaBody = {
                    name: body.name,
                    date: body.date,
                    time: body.time,
                    place: body.place,
                    ayanamsa: 'krishnamurti',
                    question_type: qType,
                    mode: mode,
                    search_start_date: document.getElementById('kp-dba-start').value,
                    search_end_date: document.getElementById('kp-dba-end').value
                };
                if (kpNum) dbaBody.kp_number = kpNum;
                var valDate = document.getElementById('kp-dba-validate').value;
                if (valDate) dbaBody.validate_date = valDate;

                var resp = await fetch(API + '/kp/dba-timing', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(dbaBody)
                });
                if (!resp.ok) {
                    var errBody = await resp.json().catch(function(){ return {}; });
                    throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
                }
                var dData = await resp.json();
                var t = dData.timing;
                if (!t) { resultDiv.innerHTML = '<p style="color:var(--red)">No timing data returned</p>'; return; }

                var dhtml = '';

                /* ── Summary banner ── */
                dhtml += '<div style="background:rgba(212,168,67,0.1);border:1px solid var(--gold);border-radius:8px;padding:14px;margin-bottom:16px;text-align:center">';
                dhtml += '<div style="font-size:0.85rem;color:var(--text-dim)">'+t.label+'</div>';
                dhtml += '<div style="font-size:1.4rem;font-weight:800;color:var(--gold-light);margin:4px 0">'+t.total_windows+' Timing Windows Found</div>';
                dhtml += '<div style="font-size:0.78rem;color:var(--text-dim)">'+t.search_start+' to '+t.search_end+' | Conductive houses: '+t.conductive.join(', ')+' | Detrimental: '+t.detrimental.join(', ')+'</div>';
                dhtml += '</div>';

                /* ── Validation Result ── */
                if (t.validation && !t.validation.error) {
                    var v = t.validation;
                    var vqColor = v.quality === 'EXCELLENT' ? '#00ff88' : v.quality === 'VERY GOOD' ? '#00cc66' : v.quality === 'GOOD' ? 'var(--gold-light)' : v.quality === 'FAIR' ? '#ff9900' : v.quality === 'WEAK' ? '#ff6666' : '#ff3333';
                    var vBorder = v.quality === 'EXCELLENT' || v.quality === 'VERY GOOD' ? 'var(--green)' : v.quality === 'GOOD' || v.quality === 'FAIR' ? 'var(--gold)' : 'var(--red)';
                    dhtml += '<div style="background:rgba(100,200,150,0.08);border:2px solid '+vBorder+';border-radius:8px;padding:14px;margin-bottom:16px">';
                    dhtml += '<div style="font-size:0.9rem;font-weight:800;color:var(--gold-light);margin-bottom:8px">Event Validation: '+v.validate_date+'</div>';
                    dhtml += '<div style="display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-bottom:8px">';
                    dhtml += '<div style="font-size:1.1rem;font-weight:800;color:'+vqColor+'">'+v.quality+'</div>';
                    dhtml += '<div style="font-size:0.85rem">Score: <b>'+v.score+'</b></div>';
                    dhtml += '<div style="font-size:0.85rem">Lords in conductive: <b>'+v.lords_conductive+'/3</b></div>';
                    if (v.rank_in_search) dhtml += '<div style="font-size:0.85rem">Rank: <b>#'+v.rank_in_search+'</b> of '+v.total_windows+'</div>';
                    dhtml += '</div>';
                    dhtml += '<div style="font-size:0.85rem;margin-bottom:6px">';
                    dhtml += 'DBA: <span style="color:'+pColor(v.dasha_lord)+'">'+v.dasha_lord+'</span> → ';
                    dhtml += '<span style="color:'+pColor(v.bhukti_lord)+'">'+v.bhukti_lord+'</span> → ';
                    dhtml += '<span style="color:'+pColor(v.antara_lord)+'">'+v.antara_lord+'</span>';
                    dhtml += '</div>';
                    dhtml += '<div style="font-size:0.78rem;color:var(--text-dim);margin-bottom:4px">';
                    dhtml += 'Dasha houses: '+v.dasha_houses.join(',')+' | Bhukti houses: '+v.bhukti_houses.join(',')+' | Antara houses: '+v.antara_houses.join(',');
                    dhtml += '</div>';
                    if (v.conductive_hit.length) dhtml += '<div style="font-size:0.78rem;color:var(--green)">Conductive houses hit: '+v.conductive_hit.join(', ')+'</div>';
                    if (v.detrimental_hit.length) dhtml += '<div style="font-size:0.78rem;color:var(--red)">Detrimental houses hit: '+v.detrimental_hit.join(', ')+'</div>';
                    dhtml += '<details style="margin-top:6px"><summary style="cursor:pointer;color:var(--text-dim);font-size:0.78rem">Analysis Details</summary>';
                    dhtml += '<div style="font-size:0.78rem;margin-top:4px">';
                    v.reasons.forEach(function(r){
                        var rc = r.indexOf('NOT') >= 0 || r.indexOf('retro') >= 0 || r.indexOf('detrimental') >= 0 ? 'var(--red)' : r.indexOf('conductive') >= 0 || r.indexOf('Primary') >= 0 ? 'var(--green)' : 'var(--text)';
                        dhtml += '<div style="color:'+rc+';margin-bottom:3px">'+r+'</div>';
                    });
                    dhtml += '</div></details>';
                    dhtml += '</div>';
                } else if (t.validation && t.validation.error) {
                    dhtml += '<div style="background:rgba(255,50,50,0.08);border:1px solid var(--red);border-radius:6px;padding:10px;margin-bottom:14px">';
                    dhtml += '<div style="font-size:0.82rem;color:var(--red)">Validation Error for '+t.validation.validate_date+': '+t.validation.error+'</div>';
                    dhtml += '</div>';
                }

                /* ── Current DBA reference ── */
                if (t.current_dba && t.current_dba.mahadasha) {
                    var cd = t.current_dba;
                    dhtml += '<div style="background:rgba(100,100,200,0.08);border:1px solid #555;border-radius:6px;padding:10px;margin-bottom:14px">';
                    dhtml += '<div style="font-size:0.82rem;font-weight:700;color:var(--text)">Current Running DBA</div>';
                    dhtml += '<div style="font-size:0.85rem;margin-top:4px">';
                    dhtml += '<span style="color:'+pColor(cd.mahadasha)+'">'+cd.mahadasha+'</span> → ';
                    dhtml += '<span style="color:'+pColor(cd.antardasha)+'">'+cd.antardasha+'</span> → ';
                    dhtml += '<span style="color:'+pColor(cd.pratyantar)+'">'+cd.pratyantar+'</span>';
                    dhtml += '</div></div>';
                }

                /* ── Planet signification summary ── */
                if (t.planet_significations) {
                    dhtml += '<details style="margin-bottom:14px"><summary style="cursor:pointer;color:var(--gold-light);font-size:0.85rem;font-weight:700">Planet House Significations</summary>';
                    dhtml += '<div style="overflow-x:auto;margin-top:6px"><table class="data-table" style="font-size:0.78rem">';
                    dhtml += '<thead><tr><th>Planet</th><th>Signifies Houses</th><th>Conductive</th><th>Detrimental</th></tr></thead><tbody>';
                    var condSet = new Set(t.conductive);
                    var detrSet = new Set(t.detrimental);
                    Object.keys(t.planet_significations).forEach(function(pl){
                        var hs = t.planet_significations[pl];
                        var cond = hs.filter(function(h){ return condSet.has(h); });
                        var detr = hs.filter(function(h){ return detrSet.has(h); });
                        dhtml += '<tr><td style="font-weight:700;color:'+pColor(pl)+'">'+pl+'</td>';
                        dhtml += '<td>'+hs.join(', ')+'</td>';
                        dhtml += '<td style="color:var(--green)">'+(cond.length?cond.join(', '):'-')+'</td>';
                        dhtml += '<td style="color:var(--red)">'+(detr.length?detr.join(', '):'-')+'</td></tr>';
                    });
                    dhtml += '</tbody></table></div></details>';
                }

                /* ── Top Windows Table ── */
                var topW = t.top_windows || [];
                if (topW.length) {
                    dhtml += '<h3 style="color:var(--gold-light);font-size:0.9rem;margin-bottom:8px">Top '+topW.length+' Best Timing Windows</h3>';
                    dhtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                    dhtml += '<thead><tr><th>#</th><th>Quality</th><th>Period</th><th>Dasha</th><th>Bhukti</th><th>Antara</th><th>Score</th><th>Conductive Hit</th></tr></thead><tbody>';
                    topW.forEach(function(w, idx){
                        var qBg = w.quality === 'EXCELLENT' ? 'rgba(0,200,100,0.15)' : w.quality === 'VERY GOOD' ? 'rgba(0,200,100,0.08)' : w.quality === 'GOOD' ? 'rgba(212,168,67,0.1)' : w.quality === 'FAIR' ? 'rgba(200,200,200,0.05)' : 'rgba(255,60,60,0.05)';
                        var qColor = w.quality === 'EXCELLENT' ? '#00e874' : w.quality === 'VERY GOOD' ? '#00c864' : w.quality === 'GOOD' ? 'var(--gold)' : w.quality === 'FAIR' ? 'var(--text-dim)' : 'var(--red)';
                        dhtml += '<tr style="background:'+qBg+'">';
                        dhtml += '<td style="font-weight:700">'+(idx+1)+'</td>';
                        dhtml += '<td style="font-weight:700;color:'+qColor+'">'+w.quality+'</td>';
                        dhtml += '<td style="font-size:0.75rem;white-space:nowrap">'+w.start_date+'<br>to '+w.end_date+'</td>';
                        dhtml += '<td style="color:'+pColor(w.dasha_lord)+';font-weight:700">'+w.dasha_lord+(w.dasha_retro?' (R)':'')+'</td>';
                        dhtml += '<td style="color:'+pColor(w.bhukti_lord)+';font-weight:700">'+w.bhukti_lord+(w.bhukti_retro?' (R)':'')+'</td>';
                        dhtml += '<td style="color:'+pColor(w.antara_lord)+';font-weight:700">'+w.antara_lord+(w.antara_retro?' (R)':'')+'</td>';
                        dhtml += '<td style="font-weight:700">'+w.score+'</td>';
                        dhtml += '<td style="color:var(--green)">'+(w.conductive_hit||[]).join(', ')+'</td>';
                        dhtml += '</tr>';
                    });
                    dhtml += '</tbody></table></div>';

                    /* ── Expandable details for each window ── */
                    dhtml += '<div style="margin-top:12px">';
                    topW.forEach(function(w, idx){
                        if (idx >= 10) return; // Show details for top 10 only
                        var qColor = w.quality === 'EXCELLENT' ? '#00e874' : w.quality === 'VERY GOOD' ? '#00c864' : w.quality === 'GOOD' ? 'var(--gold)' : 'var(--text-dim)';
                        dhtml += '<details style="margin-bottom:6px;border:1px solid #333;border-radius:4px;padding:8px">';
                        dhtml += '<summary style="cursor:pointer;font-size:0.82rem;color:'+qColor+';font-weight:700">#'+(idx+1)+' '+w.quality+' — '+w.dasha_lord+'/'+w.bhukti_lord+'/'+w.antara_lord+' ('+w.start_date+' to '+w.end_date+')</summary>';
                        dhtml += '<div style="margin-top:6px;font-size:0.78rem">';
                        dhtml += '<div style="margin-bottom:4px"><strong>Dasha houses:</strong> '+w.dasha_houses.join(', ')+' | <strong>Bhukti houses:</strong> '+w.bhukti_houses.join(', ')+' | <strong>Antara houses:</strong> '+w.antara_houses.join(', ')+'</div>';
                        if (w.rp_match && w.rp_match.length) {
                            dhtml += '<div style="margin-bottom:4px;color:var(--green)"><strong>RP Match:</strong> '+w.rp_match.join(', ')+' '+(w.rp_confirmed?'CONFIRMED':'')+'</div>';
                        }
                        dhtml += '<div>';
                        (w.reasons||[]).forEach(function(r){
                            var rColor = r.indexOf('conductive') >= 0 ? 'var(--green)' : r.indexOf('detrimental') >= 0 ? 'var(--red)' : r.indexOf('STRONGEST') >= 0 ? '#00e874' : r.indexOf('retro') >= 0 ? 'var(--red)' : 'var(--text)';
                            dhtml += '<div style="margin-bottom:3px;color:'+rColor+'">&#8226; '+r+'</div>';
                        });
                        dhtml += '</div></div></details>';
                    });
                    dhtml += '</div>';
                } else {
                    dhtml += '<p style="color:var(--text-muted)">No favorable DBA windows found in the selected date range.</p>';
                }

                resultDiv.innerHTML = dhtml;
            } catch(err) {
                resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
            }
        });
    }

    /* ═══ Match Prediction handler ═══════════════════════════════ */
    var matchBtn = document.getElementById('kp-match-fetch');
    if (matchBtn) {
        matchBtn.addEventListener('click', async function(){
            var kpNum = parseInt(document.getElementById('kp-match-num').value);
            if (!kpNum || kpNum < 1 || kpNum > 249) {
                document.getElementById('kp-match-result').innerHTML = '<p style="color:var(--red)">Please enter a valid KP number between 1 and 249</p>';
                return;
            }
            var teamA = document.getElementById('kp-match-teama').value || 'Team A';
            var teamB = document.getElementById('kp-match-teamb').value || 'Team B';
            var resultDiv = document.getElementById('kp-match-result');
            resultDiv.innerHTML = '<p style="color:var(--text-muted)">Predicting '+teamA+' vs '+teamB+' for KP #'+kpNum+'...</p>';
            try {
                var mBody = {
                    name: body.name,
                    date: body.date,
                    time: body.time,
                    place: document.getElementById('kp-match-place').value || body.place,
                    ayanamsa: 'krishnamurti',
                    kp_number: kpNum,
                    match_type: document.getElementById('kp-match-type').value,
                    team_a: teamA,
                    team_b: teamB,
                    query_date: document.getElementById('kp-match-date').value,
                    query_time: parseTimeInput(document.getElementById('kp-match-time').value)
                };
                var resp = await fetch(API + '/kp/match-prediction', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(mBody)
                });
                if (!resp.ok) throw new Error('API error ' + resp.status);
                var mData = await resp.json();
                var mp = mData.prediction;
                if (!mp) { resultDiv.innerHTML = '<p style="color:var(--red)">No prediction data returned</p>'; return; }

                var mhtml = '';

                /* ── Big winner banner ── */
                var wBg, wBorder, wColor, wIcon;
                if (mp.verdict_type === 'team_a') {
                    wBg = 'rgba(0,200,100,0.18)'; wBorder = '#00c864'; wColor = '#00e874'; wIcon = '&#127942;';
                } else if (mp.verdict_type === 'team_b') {
                    wBg = 'rgba(255,80,80,0.18)'; wBorder = '#ff5050'; wColor = '#ff6666'; wIcon = '&#127942;';
                } else if (mp.verdict_type === 'team_a_close') {
                    wBg = 'rgba(0,200,100,0.10)'; wBorder = '#44aa66'; wColor = '#66cc88'; wIcon = '&#8680;';
                } else if (mp.verdict_type === 'team_b_close') {
                    wBg = 'rgba(255,80,80,0.10)'; wBorder = '#cc6666'; wColor = '#ee8888'; wIcon = '&#8680;';
                } else {
                    wBg = 'rgba(212,168,67,0.15)'; wBorder = 'var(--gold)'; wColor = 'var(--gold)'; wIcon = '&#9878;';
                }

                mhtml += '<div style="background:'+wBg+';border:2px solid '+wBorder+';border-radius:12px;padding:24px;text-align:center;margin-bottom:18px">';
                mhtml += '<div style="font-size:0.85rem;color:var(--text-dim);margin-bottom:2px">'+mp.match_type+'</div>';
                mhtml += '<div style="font-size:1.1rem;color:var(--text);margin-bottom:8px;font-weight:600">'+mp.team_a+' <span style="color:var(--text-dim);font-weight:400">vs</span> '+mp.team_b+'</div>';
                mhtml += '<div style="font-size:2.2rem;font-weight:900;color:'+wColor+';letter-spacing:1px">'+wIcon+' '+mp.verdict+'</div>';
                mhtml += '<div style="font-size:0.85rem;color:var(--text-dim);margin-top:6px">Confidence: '+mp.confidence+'%</div>';
                mhtml += '</div>';

                /* ── Tournament Elimination Warning ── */
                if (mp.is_eliminated) {
                    mhtml += '<div style="background:rgba(255,40,40,0.15);border:2px solid #ff4444;border-radius:10px;padding:16px;text-align:center;margin-bottom:14px">';
                    mhtml += '<div style="font-size:1.4rem;font-weight:900;color:#ff4444">&#9888; TEAM ELIMINATION ALERT</div>';
                    mhtml += '<div style="font-size:0.88rem;color:#ff8888;margin-top:6px">6th cusp SL ('+mp.cusp_6_sub_lord+') signifies houses '+(mp.elimination_houses||[]).join(', ')+' at Level 1/2</div>';
                    mhtml += '<div style="font-size:0.82rem;color:var(--text-dim);margin-top:4px">Houses 5, 4, 12 = team elimination in tournament context</div>';
                    mhtml += '</div>';
                }

                /* ── Score bar ── */
                var totalScore = mp.team_a_score + mp.team_b_score;
                var pctA = totalScore > 0 ? Math.round(mp.team_a_score / totalScore * 100) : 50;
                var pctB = 100 - pctA;
                mhtml += '<div style="margin-bottom:16px">';
                mhtml += '<div style="display:flex;justify-content:space-between;font-size:0.82rem;font-weight:700;margin-bottom:4px"><span style="color:#00e874">'+mp.team_a+' ('+mp.team_a_score+')</span><span style="color:#ff6666">'+mp.team_b+' ('+mp.team_b_score+')</span></div>';
                mhtml += '<div style="height:14px;border-radius:7px;overflow:hidden;display:flex;background:#222">';
                mhtml += '<div style="width:'+pctA+'%;background:linear-gradient(90deg,#00c864,#44ee88);transition:width 0.5s"></div>';
                mhtml += '<div style="width:'+pctB+'%;background:linear-gradient(90deg,#ee4444,#ff6666);transition:width 0.5s"></div>';
                mhtml += '</div></div>';

                /* ── KP Horary details ── */
                if (mp.horary_kp) {
                    var hk = mp.horary_kp;
                    mhtml += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px">';
                    mhtml += '<div class="metric"><div class="label">KP #</div><div class="value gold">'+mp.kp_number+'</div></div>';
                    mhtml += '<div class="metric"><div class="label">Sign</div><div class="value">'+hk.sign+'</div></div>';
                    mhtml += '<div class="metric"><div class="label">Nakshatra</div><div class="value">'+hk.nakshatra+' P'+hk.pada+'</div></div>';
                    mhtml += '<div class="metric"><div class="label">Sign Lord</div><div class="value" style="color:'+pColor(hk.sign_lord)+'">'+hk.sign_lord+'</div></div>';
                    mhtml += '<div class="metric"><div class="label">Star Lord</div><div class="value" style="color:'+pColor(hk.star_lord)+'">'+hk.star_lord+'</div></div>';
                    mhtml += '<div class="metric"><div class="label">Sub Lord</div><div class="value" style="color:'+pColor(hk.sub_lord)+'">'+hk.sub_lord+'</div></div>';
                    mhtml += '</div>';
                }

                /* ── Key Cusp Analysis ── */
                mhtml += '<h3 style="color:var(--gold-light);margin-top:14px;font-size:0.9rem">Key Cusp Sub-Lord Analysis</h3>';
                mhtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                mhtml += '<thead><tr><th>Cusp</th><th>Role</th><th>Sub Lord</th><th>Star Lord</th><th>Signifies Houses</th></tr></thead><tbody>';
                (mp.cusp_details||[]).forEach(function(cd){
                    var roleBg = cd.house === 6 || cd.house === 11 ? 'rgba(0,200,100,0.08)' : cd.house === 12 || cd.house === 5 ? 'rgba(255,80,80,0.08)' : '';
                    mhtml += '<tr style="background:'+roleBg+'">';
                    mhtml += '<td style="font-weight:700">H'+cd.house+'</td>';
                    mhtml += '<td style="font-size:0.72rem;color:var(--text-dim)">'+cd.role+'</td>';
                    mhtml += '<td style="font-weight:700;color:'+pColor(cd.sub_lord)+'">'+cd.sub_lord+'</td>';
                    mhtml += '<td style="color:'+pColor(cd.star_lord)+'">'+cd.star_lord+'</td>';
                    mhtml += '<td>'+(cd.signifies||[]).join(', ')+'</td>';
                    mhtml += '</tr>';
                });
                mhtml += '</tbody></table></div>';

                /* ── Retro status — 3-tier ── */
                if (mp.retro_tier_6 > 0 || mp.retro_tier_12 > 0) {
                    mhtml += '<div style="margin-top:10px;padding:8px 12px;background:rgba(255,60,60,0.1);border:1px solid var(--red);border-radius:6px;font-size:0.82rem;color:var(--red)">';
                    if (mp.retro_tier_6 === 1) mhtml += '&#9888; 6th SL ('+mp.cusp_6_sub_lord+') Tier-1: Retro in star of Direct — '+mp.team_a+' result delayed<br>';
                    else if (mp.retro_tier_6 === 2) mhtml += '&#9888; 6th SL ('+mp.cusp_6_sub_lord+') Tier-2: Retro in star of Retro — '+mp.team_a+' victory DENIED (total failure)<br>';
                    else if (mp.retro_tier_6 === 3) mhtml += '&#9888; 6th SL ('+mp.cusp_6_sub_lord+') Tier-3: Direct in star of Retro — CANNOT give result for '+mp.team_a+'<br>';
                    if (mp.retro_tier_12 === 1) mhtml += '&#9888; 12th SL ('+mp.cusp_12_sub_lord+') Tier-1: Retro in star of Direct — '+mp.team_b+' result delayed<br>';
                    else if (mp.retro_tier_12 === 2) mhtml += '&#9888; 12th SL ('+mp.cusp_12_sub_lord+') Tier-2: Retro in star of Retro — '+mp.team_b+' victory DENIED<br>';
                    else if (mp.retro_tier_12 === 3) mhtml += '&#9888; 12th SL ('+mp.cusp_12_sub_lord+') Tier-3: Direct in star of Retro — CANNOT give result for '+mp.team_b;
                    mhtml += '</div>';
                }

                /* ── 4-Step Significator Detail ── */
                mhtml += '<h3 style="color:var(--gold-light);margin-top:16px;font-size:0.9rem">4-Step Significator Analysis</h3>';
                mhtml += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px">';

                /* 6th SL detail */
                mhtml += '<div style="flex:1;min-width:280px;padding:12px;background:rgba(0,200,100,0.06);border:1px solid rgba(0,200,100,0.3);border-radius:8px">';
                mhtml += '<div style="font-size:0.82rem;font-weight:700;color:#00e874;margin-bottom:8px">6th Cusp SL: <span style="color:'+pColor(mp.cusp_6_sub_lord)+'">'+mp.cusp_6_sub_lord+'</span> ('+mp.team_a+')</div>';
                if (mp.cusp_6_L12 && mp.cusp_6_L12.length) {
                    mhtml += '<div style="font-size:0.78rem;margin-bottom:4px"><span style="color:var(--gold);font-weight:700">L1/L2 (Strong):</span> <span style="color:#00e874;font-weight:600">H'+mp.cusp_6_L12.join(', H')+'</span></div>';
                }
                if (mp.cusp_6_L34 && mp.cusp_6_L34.length) {
                    mhtml += '<div style="font-size:0.78rem;margin-bottom:4px"><span style="color:var(--text-dim)">L3/L4 (Weak):</span> H'+mp.cusp_6_L34.join(', H')+'</div>';
                }
                if (mp.sl6_4step) {
                    mhtml += '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:6px;border-top:1px solid rgba(255,255,255,0.08);padding-top:6px">';
                    Object.keys(mp.sl6_4step).forEach(function(h){
                        var lvls = mp.sl6_4step[h];
                        var hNum = parseInt(h);
                        var isWin = [6,10,11,1,2,3].indexOf(hNum) >= 0;
                        var isLose = [12,5,4,7,8,9].indexOf(hNum) >= 0;
                        var hColor = isWin ? '#00e874' : isLose ? '#ff6666' : 'var(--text)';
                        mhtml += '<div>H'+h+': <span style="color:'+hColor+'">'+(Array.isArray(lvls)?lvls.join(', '):lvls)+'</span></div>';
                    });
                    mhtml += '</div>';
                }
                mhtml += '</div>';

                /* 12th SL detail */
                mhtml += '<div style="flex:1;min-width:280px;padding:12px;background:rgba(255,80,80,0.06);border:1px solid rgba(255,80,80,0.3);border-radius:8px">';
                mhtml += '<div style="font-size:0.82rem;font-weight:700;color:#ff6666;margin-bottom:8px">12th Cusp SL: <span style="color:'+pColor(mp.cusp_12_sub_lord)+'">'+mp.cusp_12_sub_lord+'</span> ('+mp.team_b+')</div>';
                if (mp.cusp_12_L12 && mp.cusp_12_L12.length) {
                    mhtml += '<div style="font-size:0.78rem;margin-bottom:4px"><span style="color:var(--gold);font-weight:700">L1/L2 (Strong):</span> <span style="color:#ff6666;font-weight:600">H'+mp.cusp_12_L12.join(', H')+'</span></div>';
                }
                if (mp.cusp_12_L34 && mp.cusp_12_L34.length) {
                    mhtml += '<div style="font-size:0.78rem;margin-bottom:4px"><span style="color:var(--text-dim)">L3/L4 (Weak):</span> H'+mp.cusp_12_L34.join(', H')+'</div>';
                }
                if (mp.sl12_4step) {
                    mhtml += '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:6px;border-top:1px solid rgba(255,255,255,0.08);padding-top:6px">';
                    Object.keys(mp.sl12_4step).forEach(function(h){
                        var lvls = mp.sl12_4step[h];
                        var hNum = parseInt(h);
                        var isWin = [12,5,4,7,8,9].indexOf(hNum) >= 0;
                        var isLose = [6,10,11,1,2,3].indexOf(hNum) >= 0;
                        var hColor = isWin ? '#ff6666' : isLose ? '#00e874' : 'var(--text)';
                        mhtml += '<div>H'+h+': <span style="color:'+hColor+'">'+(Array.isArray(lvls)?lvls.join(', '):lvls)+'</span></div>';
                    });
                    mhtml += '</div>';
                }
                mhtml += '</div>';
                mhtml += '</div>';

                /* ── Moon Nakshatra for Bilateral Series ── */
                if (mp.moon_nakshatra) {
                    var mn = mp.moon_nakshatra;
                    mhtml += '<div style="margin-bottom:14px;padding:12px;background:rgba(212,168,67,0.08);border:1px solid rgba(212,168,67,0.3);border-radius:8px">';
                    mhtml += '<div style="font-size:0.85rem;font-weight:700;color:var(--gold-light);margin-bottom:6px">&#127769; Moon Nakshatra — Bilateral Series Indicator</div>';
                    mhtml += '<div style="display:flex;gap:16px;flex-wrap:wrap;font-size:0.82rem">';
                    mhtml += '<div><span style="color:var(--text-dim)">Moon in:</span> <span style="font-weight:600">'+mn.nakshatra+'</span> ('+mn.moon_sign+')</div>';
                    mhtml += '<div><span style="color:var(--text-dim)">Nak Lord:</span> <span style="font-weight:700;color:'+pColor(mn.nak_lord)+'">'+mn.nak_lord+'</span></div>';
                    mhtml += '</div>';
                    if (mn.nak_lord_signifies_L12 && mn.nak_lord_signifies_L12.length) {
                        mhtml += '<div style="font-size:0.78rem;margin-top:6px"><span style="color:var(--gold)">Nak Lord Strong Houses (L1/L2):</span> H'+mn.nak_lord_signifies_L12.join(', H')+'</div>';
                    }
                    if (mn.nak_lord_signifies_all && mn.nak_lord_signifies_all.length) {
                        mhtml += '<div style="font-size:0.78rem;margin-top:2px"><span style="color:var(--text-dim)">All Significations:</span> H'+mn.nak_lord_signifies_all.join(', H')+'</div>';
                    }
                    mhtml += '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:6px;font-style:italic">In a bilateral series, same horary chart applies to all matches. Moon\'s transiting nakshatra lord on match day determines result.</div>';
                    mhtml += '</div>';
                }

                /* ── Ruling Planets ── */
                if (mp.ruling_planets) {
                    var rp = mp.ruling_planets;
                    mhtml += '<h3 style="color:var(--gold-light);margin-top:14px;font-size:0.9rem">Ruling Planets at Query Moment</h3>';
                    mhtml += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                    mhtml += '<thead><tr><th>Source</th><th>Planet</th></tr></thead><tbody>';
                    (rp.rp_rows||[]).forEach(function(r){
                        mhtml += '<tr><td style="color:var(--text-dim)">'+r.source+'</td>';
                        mhtml += '<td style="font-weight:700;color:'+pColor(r.planet)+'">'+r.planet+'</td></tr>';
                    });
                    mhtml += '</tbody></table></div>';
                    if (rp.ranked && rp.ranked.length) {
                        mhtml += '<div style="margin-top:6px;font-size:0.82rem"><strong style="color:var(--gold)">Ranked: </strong>';
                        rp.ranked.forEach(function(r, idx){
                            if (idx > 0) mhtml += ', ';
                            mhtml += '<span style="color:'+pColor(r.planet)+';font-weight:700">'+r.planet+'</span><span style="color:var(--text-dim)">('+r.count+'x)</span>';
                        });
                        mhtml += '</div>';
                    }
                }

                /* ── Fruitful Significators ── */
                if ((mp.fruitful_team_a && mp.fruitful_team_a.length) || (mp.fruitful_team_b && mp.fruitful_team_b.length)) {
                    mhtml += '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px">';
                    if (mp.fruitful_team_a && mp.fruitful_team_a.length) {
                        mhtml += '<div style="flex:1;min-width:200px;padding:10px;background:rgba(0,200,100,0.08);border:1px solid var(--green);border-radius:6px">';
                        mhtml += '<div style="font-size:0.78rem;color:var(--green);font-weight:700">'+mp.team_a+' Fruitful Sigs (RP-matched):</div>';
                        mhtml += '<div style="font-size:0.85rem;margin-top:4px">';
                        mp.fruitful_team_a.forEach(function(f, idx){ if(idx>0)mhtml+=', '; mhtml+='<span style="color:'+pColor(f)+';font-weight:700">'+f+'</span>'; });
                        mhtml += '</div></div>';
                    }
                    if (mp.fruitful_team_b && mp.fruitful_team_b.length) {
                        mhtml += '<div style="flex:1;min-width:200px;padding:10px;background:rgba(255,80,80,0.08);border:1px solid var(--red);border-radius:6px">';
                        mhtml += '<div style="font-size:0.78rem;color:var(--red);font-weight:700">'+mp.team_b+' Fruitful Sigs (RP-matched):</div>';
                        mhtml += '<div style="font-size:0.85rem;margin-top:4px">';
                        mp.fruitful_team_b.forEach(function(f, idx){ if(idx>0)mhtml+=', '; mhtml+='<span style="color:'+pColor(f)+';font-weight:700">'+f+'</span>'; });
                        mhtml += '</div></div>';
                    }
                    mhtml += '</div>';
                }

                /* ── Reasoning ── */
                if (mp.reasons && mp.reasons.length) {
                    mhtml += '<h3 style="color:var(--gold-light);margin-top:14px;font-size:0.9rem">Detailed Reasoning</h3>';
                    mhtml += '<div style="font-size:0.82rem;color:var(--text)">';
                    mp.reasons.forEach(function(r){
                        var icon = r.indexOf('WARNING') >= 0 ? '&#9888;' : r.indexOf('STRONG') >= 0 || r.indexOf('victory') >= 0 ? '&#10003;' : r.indexOf('LOSE') >= 0 || r.indexOf('denied') >= 0 ? '&#10007;' : '&#8226;';
                        var rColor = r.indexOf('WARNING') >= 0 || r.indexOf('LOSE') >= 0 ? 'var(--red)' : r.indexOf('STRONG') >= 0 || r.indexOf('victory') >= 0 || r.indexOf('desire fulfilled') >= 0 ? 'var(--green)' : 'var(--text)';
                        mhtml += '<div style="margin-bottom:6px;color:'+rColor+'">'+icon+' '+r+'</div>';
                    });
                    mhtml += '</div>';
                }

                resultDiv.innerHTML = mhtml;
            } catch(err) {
                resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
            }
        });
    }

    /* ═══ Toss Prediction handler ═══════════════════════════════ */
    var tossBtn = document.getElementById('kp-toss-fetch');
    if (tossBtn) {
        tossBtn.addEventListener('click', async function(){
            var kpNum = parseInt(document.getElementById('kp-toss-num').value);
            if (!kpNum || kpNum < 1 || kpNum > 249) {
                document.getElementById('kp-toss-result').innerHTML = '<p style="color:var(--red)">Please enter a valid KP number between 1 and 249</p>';
                return;
            }
            var teamA = document.getElementById('kp-toss-teama').value || document.getElementById('kp-match-teama').value || 'Team A';
            var teamB = document.getElementById('kp-toss-teamb').value || document.getElementById('kp-match-teamb').value || 'Team B';
            var resultDiv = document.getElementById('kp-toss-result');
            resultDiv.innerHTML = '<p style="color:var(--text-muted)">Predicting toss for '+teamA+' vs '+teamB+' (KP #'+kpNum+')...</p>';
            try {
                var tBody = {
                    name: body.name,
                    date: body.date,
                    time: body.time,
                    place: document.getElementById('kp-match-place').value || body.place,
                    ayanamsa: 'krishnamurti',
                    kp_number: kpNum,
                    team_a: teamA,
                    team_b: teamB,
                    query_date: document.getElementById('kp-match-date').value,
                    query_time: parseTimeInput(document.getElementById('kp-match-time').value)
                };
                var resp = await fetch(API + '/kp/toss-prediction', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(tBody)
                });
                if (!resp.ok) throw new Error('API error ' + resp.status);
                var tData = await resp.json();
                var tp = tData.prediction;
                if (!tp) { resultDiv.innerHTML = '<p style="color:var(--red)">No toss prediction data returned</p>'; return; }

                var thtml = '';

                /* Toss winner banner */
                var tBg, tBorder, tColor;
                if (tp.verdict_type === 'team_a') {
                    tBg = 'rgba(0,200,100,0.15)'; tBorder = '#00c864'; tColor = '#00e874';
                } else if (tp.verdict_type === 'team_b') {
                    tBg = 'rgba(255,80,80,0.15)'; tBorder = '#ff5050'; tColor = '#ff6666';
                } else {
                    tBg = 'rgba(212,168,67,0.12)'; tBorder = 'var(--gold)'; tColor = 'var(--gold)';
                }

                thtml += '<div style="background:'+tBg+';border:2px solid '+tBorder+';border-radius:10px;padding:18px;text-align:center;margin-bottom:12px">';
                thtml += '<div style="font-size:0.82rem;color:var(--text-dim);margin-bottom:2px">TOSS PREDICTION</div>';
                thtml += '<div style="font-size:0.95rem;color:var(--text);margin-bottom:6px">'+tp.team_a+' <span style="color:var(--text-dim)">vs</span> '+tp.team_b+'</div>';
                thtml += '<div style="font-size:1.6rem;font-weight:900;color:'+tColor+'">&#127944; '+tp.verdict+'</div>';
                thtml += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Confidence: '+tp.confidence+'%</div>';
                thtml += '</div>';

                /* Score bar */
                var tTotal = tp.team_a_score + tp.team_b_score;
                var tPctA = tTotal > 0 ? Math.round(tp.team_a_score / tTotal * 100) : 50;
                thtml += '<div style="margin-bottom:10px">';
                thtml += '<div style="display:flex;justify-content:space-between;font-size:0.78rem;font-weight:700;margin-bottom:3px"><span style="color:#00e874">'+tp.team_a+' ('+tp.team_a_score+')</span><span style="color:#ff6666">'+tp.team_b+' ('+tp.team_b_score+')</span></div>';
                thtml += '<div style="height:10px;border-radius:5px;overflow:hidden;display:flex;background:#222">';
                thtml += '<div style="width:'+tPctA+'%;background:linear-gradient(90deg,#00c864,#44ee88)"></div>';
                thtml += '<div style="width:'+(100-tPctA)+'%;background:linear-gradient(90deg,#ee4444,#ff6666)"></div>';
                thtml += '</div></div>';

                /* KP details */
                if (tp.horary_kp) {
                    var hk = tp.horary_kp;
                    thtml += '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;font-size:0.78rem">';
                    thtml += '<div class="metric"><div class="label">KP #</div><div class="value gold">'+tp.kp_number+'</div></div>';
                    thtml += '<div class="metric"><div class="label">Sign</div><div class="value">'+(hk.sign||'')+'</div></div>';
                    thtml += '<div class="metric"><div class="label">Star</div><div class="value">'+(hk.nakshatra||'')+'</div></div>';
                    thtml += '<div class="metric"><div class="label">Sub Lord</div><div class="value" style="color:'+pColor(hk.sub_lord)+'">'+hk.sub_lord+'</div></div>';
                    thtml += '</div>';
                }

                /* 6th SL analysis */
                thtml += '<div style="font-size:0.8rem;margin-bottom:6px"><span style="color:var(--gold)">6th Cusp SL:</span> <span style="font-weight:700;color:'+pColor(tp.cusp_6_sub_lord)+'">'+tp.cusp_6_sub_lord+'</span> signifies H'+(tp.cusp_6_signifies||[]).join(', H')+'</div>';
                thtml += '<div style="font-size:0.8rem;margin-bottom:10px"><span style="color:var(--gold)">12th Cusp SL:</span> <span style="font-weight:700;color:'+pColor(tp.cusp_12_sub_lord)+'">'+tp.cusp_12_sub_lord+'</span> signifies H'+(tp.cusp_12_signifies||[]).join(', H')+'</div>';

                /* Retro tier */
                if (tp.retro_tier_6 > 0) {
                    thtml += '<div style="padding:6px 10px;background:rgba(255,60,60,0.1);border:1px solid var(--red);border-radius:5px;font-size:0.78rem;color:var(--red);margin-bottom:8px">';
                    thtml += '&#9888; Retro Tier-'+tp.retro_tier_6+' on 6th SL — ';
                    if (tp.retro_tier_6 === 1) thtml += 'delayed result';
                    else if (tp.retro_tier_6 === 2) thtml += 'total failure promised';
                    else thtml += 'cannot give result';
                    thtml += '</div>';
                }

                /* Reasoning */
                if (tp.reasons && tp.reasons.length) {
                    thtml += '<div style="font-size:0.76rem;color:var(--text-dim);border-top:1px solid #333;padding-top:8px">';
                    tp.reasons.forEach(function(r){
                        var icon = r.indexOf('RETRO') >= 0 ? '&#9888;' : r.indexOf('favours') >= 0 ? '&#10003;' : '&#8226;';
                        thtml += '<div style="margin-bottom:3px">'+icon+' '+r+'</div>';
                    });
                    thtml += '</div>';
                }

                resultDiv.innerHTML = thtml;
            } catch(err) {
                resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
            }
        });
    }
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

// ═══════════════════════════════════════════════════════════════
//  SHODASVARGA — 16 Divisional Charts (D1–D60) Diamond Style
// ═══════════════════════════════════════════════════════════════

(function(){

var svData = null; // store API response

/* ── Rashi abbreviations & symbols ─────────────────────────── */
var RASHI_SHORT = {
    'Aries':'Ari','Taurus':'Tau','Gemini':'Gem','Cancer':'Can',
    'Leo':'Leo','Virgo':'Vir','Libra':'Lib','Scorpio':'Sco',
    'Sagittarius':'Sag','Capricorn':'Cap','Aquarius':'Aqu','Pisces':'Pis'
};
var RASHI_SYMBOL = {
    'Aries':'♈','Taurus':'♉','Gemini':'♊','Cancer':'♋',
    'Leo':'♌','Virgo':'♍','Libra':'♎','Scorpio':'♏',
    'Sagittarius':'♐','Capricorn':'♑','Aquarius':'♒','Pisces':'♓'
};
var RASHI_ORDER = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
                   'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];
var PLANET_SHORT = {
    'Sun':'Su','Moon':'Mo','Mars':'Ma','Mercury':'Me','Jupiter':'Ju',
    'Venus':'Ve','Saturn':'Sa','Rahu':'Ra','Ketu':'Ke','Ascendant':'As'
};
var PLANET_COLOR = {
    'Sun':'#FFA500','Moon':'#C0C0C0','Mars':'#FF4444','Mercury':'#00CED1',
    'Jupiter':'#FFD700','Venus':'#FF69B4','Saturn':'#4169E1','Rahu':'#8B008B','Ketu':'#808080'
};
var DIGNITY_COLOR = {
    'Exalted (Uchcha)':'#00e676', 'Own Sign (Swakshetra)':'#66bb6a',
    'Normal':'#aaa', 'Debilitated (Neecha)':'#ff5252'
};
var DASHA_COLOR = {
    'Sun':'#FFA500','Moon':'#C0C0C0','Mars':'#FF4444','Mercury':'#00CED1',
    'Jupiter':'#FFD700','Venus':'#FF69B4','Saturn':'#4169E1','Rahu':'#8B008B','Ketu':'#808080'
};

/* ── South Indian Diamond Chart (SVG) ──────────────────────── */
/*  Fixed-house layout: each rashi always in the same position.
    Pisces  | Aries  | Taurus | Gemini
    Aquarius|                  | Cancer
    Capricorn|                 | Leo
    Sagittarius|Scorpio|Libra | Virgo
    The inner diamond is formed by connecting midpoints.        */

function southIndianHouseCoords(houseIdx) {
    /* Returns {row, col} in a 4x4 grid for South Indian style */
    var map = [
        /* Ari=0 */ {r:0,c:1}, /* Tau=1 */ {r:0,c:2}, /* Gem=2 */ {r:0,c:3},
        /* Can=3 */ {r:1,c:3}, /* Leo=4 */ {r:2,c:3}, /* Vir=5 */ {r:3,c:3},
        /* Lib=6 */ {r:3,c:2}, /* Sco=7 */ {r:3,c:1}, /* Sag=8 */ {r:3,c:0},
        /* Cap=9 */ {r:2,c:0}, /* Aqu=10*/ {r:1,c:0}, /* Pis=11*/ {r:0,c:0}
    ];
    return map[houseIdx % 12];
}

function drawSouthIndianSVG(chartData, size) {
    var s = size || 320;
    var cell = s / 4;
    var planets = chartData.planets || [];
    var ascSign = chartData.ascendant || '';
    var ascIdx = RASHI_ORDER.indexOf(ascSign);

    // Build sign→planets map
    var signPlanets = {};
    RASHI_ORDER.forEach(function(r){ signPlanets[r] = []; });
    planets.forEach(function(p){
        var sign = p.sign || '';
        if (signPlanets[sign]) signPlanets[sign].push(p);
    });

    var svg = '<svg viewBox="0 0 '+s+' '+s+'" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:'+s+'px">';
    // Background
    svg += '<rect width="'+s+'" height="'+s+'" fill="#0d1117" rx="4"/>';

    // Draw 4x4 grid
    for (var i = 0; i < 12; i++) {
        var pos = southIndianHouseCoords(i);
        var x = pos.c * cell, y = pos.r * cell;
        var rashi = RASHI_ORDER[i];
        var isAsc = (i === ascIdx);

        // Cell border
        svg += '<rect x="'+x+'" y="'+y+'" width="'+cell+'" height="'+cell+'" fill="'+(isAsc?'rgba(212,168,67,0.12)':'rgba(255,255,255,0.03)')+'" stroke="#555" stroke-width="0.8"/>';

        // Rashi number + symbol (top-left)
        svg += '<text x="'+(x+4)+'" y="'+(y+13)+'" fill="'+(isAsc?'#d4a843':'#888')+'" font-size="10" font-weight="'+(isAsc?'700':'400')+'">'+(i+1)+' '+RASHI_SYMBOL[rashi]+'</text>';

        // Diagonal line (diamond effect)
        svg += '<line x1="'+x+'" y1="'+y+'" x2="'+(x+cell)+'" y2="'+(y+cell)+'" stroke="#333" stroke-width="0.4"/>';
        svg += '<line x1="'+(x+cell)+'" y1="'+y+'" x2="'+x+'" y2="'+(y+cell)+'" stroke="#333" stroke-width="0.4"/>';

        // Planets in this sign
        var pp = signPlanets[rashi] || [];
        var startY = y + 26;
        pp.forEach(function(p, idx){
            var pName = PLANET_SHORT[p.planet] || p.planet.substring(0,2);
            var pColor = PLANET_COLOR[p.planet] || '#ccc';
            var retro = p.retro ? '(R)' : '';
            var dignityMark = '';
            var str = p.strength || '';
            if (str.indexOf('Exalted') >= 0) dignityMark = '↑';
            else if (str.indexOf('Own') >= 0) dignityMark = '★';
            else if (str.indexOf('Debilitated') >= 0) dignityMark = '↓';
            var px = x + 6 + (idx % 2) * (cell/2 - 4);
            var py = startY + Math.floor(idx / 2) * 13;
            svg += '<text x="'+px+'" y="'+py+'" fill="'+pColor+'" font-size="10" font-weight="600">'+pName+retro+dignityMark+'</text>';
        });

        // "Asc" marker
        if (isAsc) {
            svg += '<text x="'+(x+cell-18)+'" y="'+(y+cell-4)+'" fill="#d4a843" font-size="8" font-weight="700">ASC</text>';
        }
    }

    // Center area (empty in South Indian — the 2x2 center)
    svg += '<rect x="'+cell+'" y="'+cell+'" width="'+(cell*2)+'" height="'+(cell*2)+'" fill="#0a0e1a" stroke="#555" stroke-width="1"/>';
    // Chart name in center
    var chartName = chartData.chart || '';
    var divMatch = chartName.match(/D\d+/);
    var divLabel = divMatch ? divMatch[0] : '';
    svg += '<text x="'+(s/2)+'" y="'+(s/2-6)+'" fill="#d4a843" font-size="14" font-weight="700" text-anchor="middle">'+divLabel+'</text>';
    var shortDesc = chartData.description || '';
    if (shortDesc.length > 30) shortDesc = shortDesc.substring(0, 28) + '..';
    svg += '<text x="'+(s/2)+'" y="'+(s/2+10)+'" fill="#888" font-size="8" text-anchor="middle">'+shortDesc+'</text>';

    svg += '</svg>';
    return svg;
}


/* ── North Indian Diamond Chart (SVG) — Clean H1-H12 layout ── */
/* Lagna always at top center. Houses arranged as diamond.
   House 1 = top, House 4 = left, House 7 = bottom, House 10 = right
   Labels: H1-H12, no roman numerals or zodiac symbols. */

function drawNorthIndianSVG(chartData, size) {
    var s = size || 420;
    var pad = Math.round(s * 0.04);  // inner padding
    var inner = s - pad * 2;
    var mid = s / 2;
    var planets = chartData.planets || [];
    var ascSign = chartData.ascendant || '';
    var ascIdx = RASHI_ORDER.indexOf(ascSign);
    if (ascIdx < 0) ascIdx = 0;

    // Build house→planets map (house 1 = ascendant sign)
    var housePlanets = {};
    for (var h = 1; h <= 12; h++) housePlanets[h] = [];
    planets.forEach(function(p){
        var pSign = p.sign || '';
        var pIdx = RASHI_ORDER.indexOf(pSign);
        if (pIdx < 0) return;
        var house = ((pIdx - ascIdx + 12) % 12) + 1;
        housePlanets[house].push(p);
    });

    // Scaled font sizes based on chart size
    var fs = Math.max(8, Math.round(s / 35));    // planet font
    var fsLbl = Math.max(7, Math.round(s / 42));  // house label font
    var fsCenter = Math.max(11, Math.round(s / 25)); // center label font
    var lineH = Math.max(10, Math.round(s / 28)); // line height for planets

    // Key points
    var TL = [pad,pad], TR = [s-pad,pad], BR = [s-pad,s-pad], BL = [pad,s-pad];
    var T = [mid,pad], R = [s-pad,mid], B = [mid,s-pad], L = [pad,mid];
    var C = [mid,mid];

    // House polygons (12 houses)
    var q1 = [(TL[0]+T[0])/2, (TL[1]+T[1])/2];  // midpoint top-left edge
    var q2 = [(T[0]+TR[0])/2, (T[1]+TR[1])/2];   // midpoint top-right edge
    var q3 = [(TR[0]+R[0])/2, (TR[1]+R[1])/2];
    var q4 = [(R[0]+BR[0])/2, (R[1]+BR[1])/2];
    var q5 = [(BR[0]+B[0])/2, (BR[1]+B[1])/2];
    var q6 = [(B[0]+BL[0])/2, (B[1]+BL[1])/2];
    var q7 = [(BL[0]+L[0])/2, (BL[1]+L[1])/2];
    var q8 = [(L[0]+TL[0])/2, (L[1]+TL[1])/2];

    var HP = {
        1:  [T, q2, C, q1],
        2:  [TL, T, q1],
        3:  [TL, q1, L],
        4:  [L, q8, C, q1],
        5:  [BL, L, q7],
        6:  [BL, q7, B],
        7:  [B, q6, C, q7],
        8:  [BR, B, q5],
        9:  [BR, q5, R],
        10: [R, q4, C, q5],
        11: [TR, R, q3],
        12: [TR, q3, T]
    };

    // Diamond midpoints for kendra houses
    var DM_TL = [mid-(inner/4), mid-(inner/4)];  // inner diamond top-left
    var DM_TR = [mid+(inner/4), mid-(inner/4)];  // inner diamond top-right
    var DM_BL = [mid-(inner/4), mid+(inner/4)];  // inner diamond bottom-left
    var DM_BR = [mid+(inner/4), mid+(inner/4)];  // inner diamond bottom-right

    // House polygons — ANTI-CLOCKWISE from H1 (North Indian standard)
    // H1=top, H2=top-left, H3=left-upper, H4=left diamond,
    // H5=left-lower, H6=bottom-left, H7=bottom, H8=bottom-right,
    // H9=right-lower, H10=right diamond, H11=right-upper, H12=top-right
    HP[1]  = [T, DM_TR, C, DM_TL];            // top diamond (Lagna)
    HP[12] = [TR, DM_TR, T];                   // top-right triangle
    HP[11] = [TR, R, DM_TR];                   // right-upper triangle
    HP[10] = [R, DM_TR, C, DM_BR];            // right diamond
    HP[9]  = [BR, DM_BR, R];                   // right-lower triangle
    HP[8]  = [BR, B, DM_BR];                   // bottom-right triangle
    HP[7]  = [B, DM_BR, C, DM_BL];            // bottom diamond
    HP[6]  = [BL, DM_BL, B];                   // bottom-left triangle
    HP[5]  = [BL, L, DM_BL];                   // left-lower triangle
    HP[4]  = [L, DM_TL, C, DM_BL];            // left diamond
    HP[3]  = [TL, DM_TL, L];                   // left-upper triangle
    HP[2]  = [TL, T, DM_TL];                   // top-left triangle

    // House label & planet centers — computed from triangle/quad centroids
    var HC = {
        1:  [mid, mid*0.52],           // top diamond center
        2:  [s*0.27, s*0.12],          // top-left triangle
        3:  [s*0.12, s*0.27],          // left-upper triangle
        4:  [s*0.27, mid],             // left diamond center
        5:  [s*0.12, s*0.73],          // left-lower triangle
        6:  [s*0.27, s*0.87],          // bottom-left triangle
        7:  [mid, s*0.62],             // bottom diamond center
        8:  [s*0.73, s*0.87],          // bottom-right triangle
        9:  [s*0.88, s*0.73],          // right-lower triangle
        10: [s*0.73, mid],             // right diamond center
        11: [s*0.88, s*0.27],          // right-upper triangle
        12: [s*0.73, s*0.12]           // top-right triangle
    };

    var svg = '<svg viewBox="0 0 '+s+' '+s+'" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:'+s+'px">';

    // Dark background
    svg += '<rect width="'+s+'" height="'+s+'" fill="#0d1117" rx="6"/>';

    // Outer box
    svg += '<rect x="'+pad+'" y="'+pad+'" width="'+inner+'" height="'+inner+'" fill="none" stroke="#d4a84366" stroke-width="1.5" rx="2"/>';

    // Inner diamond
    svg += '<polygon points="'+T.join(',')+' '+R.join(',')+' '+B.join(',')+' '+L.join(',')+'" fill="none" stroke="#d4a84366" stroke-width="1.5"/>';

    // Diagonal lines (corner to corner through center)
    svg += '<line x1="'+TL[0]+'" y1="'+TL[1]+'" x2="'+BR[0]+'" y2="'+BR[1]+'" stroke="#d4a84333" stroke-width="0.8"/>';
    svg += '<line x1="'+TR[0]+'" y1="'+TR[1]+'" x2="'+BL[0]+'" y2="'+BL[1]+'" stroke="#d4a84333" stroke-width="0.8"/>';

    // Draw each house
    for (var h = 1; h <= 12; h++) {
        var pts = HP[h];
        var polyStr = pts.map(function(p){ return p[0]+','+p[1]; }).join(' ');
        var isLagna = (h === 1);

        // Subtle fill for lagna
        if (isLagna) {
            svg += '<polygon points="'+polyStr+'" fill="rgba(212,168,67,0.08)" stroke="none"/>';
        }

        var hc = HC[h];

        // House label: zodiac sign number (Aries=1, Taurus=2 ... Pisces=12)
        var rashiIdx = (ascIdx + h - 1) % 12;  // 0-based index in RASHI_ORDER
        var signNum = rashiIdx + 1;             // 1-based zodiac number
        svg += '<text x="'+hc[0]+'" y="'+(hc[1]-Math.round(lineH*0.3))+'" fill="'+(isLagna?'#d4a843':'#555')+'" font-size="'+fsLbl+'" font-weight="'+(isLagna?'700':'500')+'" text-anchor="middle" font-family="monospace">'+signNum+'</text>';

        // Planets
        var pp = housePlanets[h] || [];
        pp.forEach(function(p, idx){
            var pName = PLANET_SHORT[p.planet] || p.planet.substring(0,2);
            var pColor = PLANET_COLOR[p.planet] || '#ccc';
            var retro = (p.retro || (p.speed != null && p.speed < 0)) ? 'ᴿ' : '';
            var dignityMark = '';
            var str = p.strength || '';
            if (str.indexOf('Exalted') >= 0) dignityMark = '↑';
            else if (str.indexOf('Own') >= 0) dignityMark = '★';
            else if (str.indexOf('Debilitated') >= 0) dignityMark = '↓';
            var cols = pp.length > 4 ? 3 : 2;
            var offX = (idx % cols - (cols-1)/2) * Math.round(fs * 2.2);
            var offY = Math.round(lineH * 0.5) + Math.floor(idx / cols) * lineH;
            svg += '<text x="'+(hc[0]+offX)+'" y="'+(hc[1]+offY)+'" fill="'+pColor+'" font-size="'+fs+'" font-weight="700" text-anchor="middle">'+pName+retro+dignityMark+'</text>';
        });
    }

    // Chart name in center
    var chartName = chartData.chart || '';
    var divMatch = chartName.match(/D\d+/);
    var divLabel = divMatch ? divMatch[0] : '';
    svg += '<text x="'+mid+'" y="'+(mid-Math.round(fsCenter*0.3))+'" fill="#d4a843" font-size="'+fsCenter+'" font-weight="700" text-anchor="middle" font-family="sans-serif">'+divLabel+'</text>';
    // Short description under label
    var shortDesc = chartData.description || '';
    if (shortDesc.length > 24) shortDesc = shortDesc.substring(0, 22) + '..';
    svg += '<text x="'+mid+'" y="'+(mid+Math.round(fsCenter*0.8))+'" fill="#666" font-size="'+Math.round(fsCenter*0.55)+'" text-anchor="middle">'+shortDesc+'</text>';

    svg += '</svg>';
    return svg;
}


/* ── Render chart based on style toggle ────────────────────── */
function renderDiamondChart(chartData, style) {
    if (style === 'north') return drawNorthIndianSVG(chartData, 420);
    return drawSouthIndianSVG(chartData, 420);
}


/* ── Dasha Tree HTML ──────────────────────────────────────── */
function renderDashaTree(dashaData, currentDasha) {
    if (!dashaData || !dashaData.dashas) return '';
    var dashas = dashaData.dashas;
    var html = '<div class="card" style="margin-top:16px">';
    html += '<h2 style="color:var(--gold-light)">Vimshottari Dasha</h2>';

    // Current dasha summary
    if (currentDasha) {
        html += '<div class="signal-card" style="margin-bottom:16px">';
        html += '<div style="display:flex;gap:20px;flex-wrap:wrap;align-items:center">';
        html += '<div><span style="color:var(--text-muted);font-size:0.8rem">Mahadasha</span><div style="font-size:1.2rem;font-weight:700;color:'+(DASHA_COLOR[currentDasha.mahadasha]||'#fff')+'">'+(currentDasha.mahadasha||'')+'</div></div>';
        html += '<div><span style="color:var(--text-muted);font-size:0.8rem">Antardasha</span><div style="font-size:1.1rem;font-weight:600;color:'+(DASHA_COLOR[currentDasha.antardasha]||'#ccc')+'">'+(currentDasha.antardasha||'')+'</div></div>';
        html += '<div><span style="color:var(--text-muted);font-size:0.8rem">Pratyantar</span><div style="font-size:1rem;color:#aaa">'+(currentDasha.pratyantar||'')+'</div></div>';
        html += '</div></div>';
    }

    // Mahadasha timeline (collapsible)
    html += '<div style="max-height:400px;overflow-y:auto">';
    html += '<table class="data-table" style="font-size:0.82rem">';
    html += '<thead><tr><th></th><th>Lord</th><th>Start</th><th>End</th><th>Years</th><th>Score</th><th>Sectors</th></tr></thead><tbody>';
    dashas.forEach(function(d, idx){
        var fin = d.financial || {};
        var isCurrent = currentDasha && currentDasha.mahadasha === d.mahadasha_lord;
        html += '<tr style="border-left:3px solid '+(fin.color||'#888')+';"'+(isCurrent?' class="sv-current-dasha"':'')+'>';
        html += '<td><button class="sv-dasha-toggle" data-idx="'+idx+'" style="background:none;border:1px solid #555;color:#aaa;cursor:pointer;font-size:0.7rem;padding:1px 5px;border-radius:3px">+</button></td>';
        html += '<td style="font-weight:700;color:'+(fin.color||'#fff')+'">'+d.mahadasha_lord+'</td>';
        html += '<td>'+apiToDdmm(d.start_date)+'</td><td>'+apiToDdmm(d.end_date)+'</td>';
        html += '<td>'+(d.duration_years ? d.duration_years.toFixed(1) : '')+'</td>';
        html += '<td style="color:'+(fin.score > 0.5 ? 'var(--green)' : fin.score < 0 ? 'var(--red)' : 'var(--text)')+'">'+(fin.score !== undefined ? fin.score.toFixed(2) : '')+'</td>';
        html += '<td style="font-size:0.72rem;max-width:180px;white-space:normal">'+(fin.sectors ? fin.sectors.join(', ') : '')+'</td>';
        html += '</tr>';
        // Antardasha rows (hidden by default)
        (d.antardashas || []).forEach(function(ad){
            html += '<tr class="sv-antar-row sv-antar-'+idx+'" style="display:none;background:rgba(255,255,255,0.02)">';
            html += '<td></td>';
            html += '<td style="padding-left:16px;color:'+(DASHA_COLOR[ad.antardasha_lord]||'#ccc')+'">'+d.mahadasha_lord+'/'+ad.antardasha_lord+'</td>';
            html += '<td>'+apiToDdmm(ad.start_date)+'</td><td>'+apiToDdmm(ad.end_date)+'</td>';
            html += '<td style="font-size:0.75rem">'+(ad.duration_days ? Math.round(ad.duration_days)+'d' : '')+'</td>';
            html += '<td style="color:'+(ad.combined_score > 0.5 ? 'var(--green)' : ad.combined_score < 0 ? 'var(--red)' : 'var(--text)')+'">'+(ad.combined_score !== undefined ? ad.combined_score.toFixed(2) : '')+'</td>';
            html += '<td style="font-size:0.72rem">'+(ad.sectors ? ad.sectors.join(', ') : '')+'</td>';
            html += '</tr>';
        });
    });
    html += '</tbody></table></div></div>';
    return html;
}


/* ── Dignity Summary Table ────────────────────────────────── */
function renderDignityTable(dignity) {
    if (!dignity || !dignity.length) return '';
    var html = '<div class="card" style="margin-top:16px">';
    html += '<h2 style="color:var(--gold-light)">Dignity Summary Across All Vargas</h2>';
    html += '<table class="data-table" style="font-size:0.82rem">';
    html += '<thead><tr><th>Planet</th><th>Total Score</th><th>Exalted</th><th>Own Sign</th><th>Debilitated</th></tr></thead><tbody>';
    dignity.forEach(function(d){
        var scoreColor = d.total > 5 ? 'var(--green)' : d.total < 0 ? 'var(--red)' : 'var(--text)';
        html += '<tr>';
        html += '<td style="font-weight:600;color:'+(PLANET_COLOR[d.planet]||'#ccc')+'">'+d.planet+'</td>';
        html += '<td style="font-weight:700;color:'+scoreColor+'">'+d.total+'</td>';
        html += '<td style="color:#00e676">'+d.exalted+'</td>';
        html += '<td style="color:#66bb6a">'+d.own+'</td>';
        html += '<td style="color:#ff5252">'+d.debilitated+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    return html;
}


/* ── Vargottama Display ───────────────────────────────────── */
function renderVargottama(vargottama) {
    if (!vargottama || !vargottama.length) return '<div class="card" style="margin-top:16px"><h2 style="color:var(--gold-light)">Vargottama</h2><p style="color:var(--text-muted)">No Vargottama planets found in this chart.</p></div>';
    var html = '<div class="card" style="margin-top:16px">';
    html += '<h2 style="color:var(--gold-light)">Vargottama Planets</h2>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:10px;margin-top:8px">';
    vargottama.forEach(function(v){
        html += '<div style="background:rgba(212,168,67,0.15);border:1px solid #d4a843;padding:8px 14px;border-radius:6px">';
        html += '<span style="font-weight:700;color:'+(PLANET_COLOR[v.planet]||'#d4a843')+'">'+v.planet+'</span>';
        html += ' <span style="color:#aaa;font-size:0.8rem">in '+v.sign+'</span>';
        html += '<div style="font-size:0.7rem;color:#888;margin-top:2px">Same sign in: '+v.matching_charts.join(', ')+'</div>';
        html += '</div>';
    });
    html += '</div></div>';
    return html;
}


/* ── Planet Table for Selected Chart ──────────────────────── */
function renderPlanetTable(chartData) {
    var planets = chartData.planets || [];
    if (!planets.length) return '';
    var html = '<table class="data-table" style="font-size:0.82rem;margin-top:12px">';
    html += '<thead><tr><th>Planet</th><th>Sign</th><th>Dignity</th></tr></thead><tbody>';
    planets.forEach(function(p){
        var str = p.strength || 'Normal';
        var sColor = DIGNITY_COLOR[str] || '#aaa';
        var retro = p.retro ? ' (R)' : '';
        html += '<tr>';
        html += '<td style="font-weight:600;color:'+(PLANET_COLOR[p.planet]||'#ccc')+'">'+p.planet+retro+'</td>';
        html += '<td>'+(RASHI_SYMBOL[p.sign]||'')+' '+(p.sign||'')+'</td>';
        html += '<td style="color:'+sColor+'">'+str+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
}


/* ── Main Render Function ─────────────────────────────────── */
function renderShodasvarga(data) {
    svData = data;
    var resultEl = document.getElementById('shodasvarga-result');
    var charts = data.charts || {};
    var chartList = data.chart_list || [];
    var currentChart = chartList.length ? chartList[0].id.toLowerCase() : 'd1';

    // Build dropdown options
    var dropdownHtml = '<select id="sv-chart-select" style="background:#1a2332;color:#e2e8f0;border:1px solid #555;padding:6px 12px;border-radius:4px;font-size:0.9rem;min-width:260px">';
    chartList.forEach(function(c){
        dropdownHtml += '<option value="'+c.id.toLowerCase()+'">'+c.id+' — '+c.name+' ('+c.desc+')</option>';
    });
    dropdownHtml += '</select>';

    // Style toggle
    var toggleHtml = '<div style="display:flex;gap:6px;align-items:center">';
    toggleHtml += '<button class="sv-style-btn" data-style="south" style="padding:4px 12px;border:1px solid #555;background:transparent;color:#aaa;border-radius:4px;cursor:pointer;font-size:0.8rem">South Indian</button>';
    toggleHtml += '<button class="sv-style-btn active" data-style="north" style="padding:4px 12px;border:1px solid #555;background:rgba(212,168,67,0.15);color:#d4a843;border-radius:4px;cursor:pointer;font-size:0.8rem">North Indian</button>';
    toggleHtml += '</div>';

    var html = '';

    // Top controls
    html += '<div class="card" style="display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between">';
    html += '<div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><span style="color:var(--gold);font-weight:600">Chart:</span>' + dropdownHtml + '</div>';
    html += toggleHtml;
    html += '</div>';

    // Chart area + planet table side by side
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px" id="sv-chart-area">';
    html += '<div class="card" id="sv-diamond-wrap" style="display:flex;justify-content:center;align-items:center;min-height:440px"></div>';
    html += '<div class="card" id="sv-planet-table-wrap"><h3 style="color:var(--gold-light);margin-bottom:8px">Planet Positions</h3><div id="sv-planet-table"></div></div>';
    html += '</div>';

    // All 16 mini charts overview
    html += '<div class="card" style="margin-top:16px">';
    html += '<h2 style="color:var(--gold-light);margin-bottom:12px">All 16 Shodasvarga Charts</h2>';
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px" id="sv-all-mini-charts">';
    chartList.forEach(function(c){
        var cd = charts[c.id.toLowerCase()];
        if (cd) {
            html += '<div class="sv-mini-chart-card" data-chart="'+c.id.toLowerCase()+'" style="cursor:pointer;border:1px solid #333;border-radius:8px;padding:6px;transition:border-color 0.2s">';
            html += '<div style="font-size:0.75rem;color:#d4a843;text-align:center;font-weight:600;padding:3px 0">'+c.id+' '+c.name+'</div>';
            html += drawNorthIndianSVG(cd, 210);
            html += '</div>';
        }
    });
    html += '</div></div>';

    // Vargottama
    html += renderVargottama(data.vargottama);

    // Dignity Summary
    html += renderDignityTable(data.dignity_summary);

    // Dasha Tree
    html += renderDashaTree(data.dasha_data, data.current_dasha);

    resultEl.innerHTML = html;

    // Set initial chart
    updateSelectedChart(currentChart, 'north');

    // Event: chart dropdown
    document.getElementById('sv-chart-select').addEventListener('change', function(){
        var style = document.querySelector('.sv-style-btn.active');
        updateSelectedChart(this.value, style ? style.dataset.style : 'north');
    });

    // Event: style toggle
    document.querySelectorAll('.sv-style-btn').forEach(function(btn){
        btn.addEventListener('click', function(){
            document.querySelectorAll('.sv-style-btn').forEach(function(b){
                b.classList.remove('active');
                b.style.background = 'transparent';
                b.style.color = '#aaa';
            });
            this.classList.add('active');
            this.style.background = 'rgba(212,168,67,0.15)';
            this.style.color = '#d4a843';
            var sel = document.getElementById('sv-chart-select');
            updateSelectedChart(sel.value, this.dataset.style);
        });
    });

    // Event: mini chart click
    document.querySelectorAll('.sv-mini-chart-card').forEach(function(card){
        card.addEventListener('click', function(){
            var chartId = this.dataset.chart;
            document.getElementById('sv-chart-select').value = chartId;
            var style = document.querySelector('.sv-style-btn.active');
            updateSelectedChart(chartId, style ? style.dataset.style : 'north');
            // Scroll to top of chart area
            document.getElementById('sv-chart-area').scrollIntoView({behavior:'smooth'});
        });
    });

    // Event: dasha toggle
    document.querySelectorAll('.sv-dasha-toggle').forEach(function(btn){
        btn.addEventListener('click', function(){
            var idx = this.dataset.idx;
            var rows = document.querySelectorAll('.sv-antar-'+idx);
            var showing = this.textContent === '-';
            rows.forEach(function(r){ r.style.display = showing ? 'none' : 'table-row'; });
            this.textContent = showing ? '+' : '-';
        });
    });
}

function updateSelectedChart(chartId, style) {
    if (!svData) return;
    var cd = svData.charts[chartId];
    if (!cd) return;
    var diamondWrap = document.getElementById('sv-diamond-wrap');
    var ptWrap = document.getElementById('sv-planet-table');
    if (diamondWrap) diamondWrap.innerHTML = renderDiamondChart(cd, style);
    if (ptWrap) ptWrap.innerHTML = renderPlanetTable(cd);
    // Highlight mini chart
    document.querySelectorAll('.sv-mini-chart-card').forEach(function(c){
        c.style.borderColor = c.dataset.chart === chartId ? '#d4a843' : '#333';
    });
}


/* ── Form Submit ──────────────────────────────────────────── */
document.getElementById('shodasvarga-form').addEventListener('submit', async function(e){
    e.preventDefault();
    var resultEl = document.getElementById('shodasvarga-result');
    var data = await apiCall('/shodasvarga', {
        name: document.getElementById('sv-name').value,
        date: ddmmToApi(document.getElementById('sv-date').value),
        time: document.getElementById('sv-time').value,
        place: document.getElementById('sv-place').value,
        ayanamsa: document.getElementById('sv-ayanamsa').value,
    }, resultEl);
    if (!data) return;
    renderShodasvarga(data);
});

/* ═══════════════════════════════════════════════════════════
   GOCHAR (TRANSIT) PANCHANG TAB
   ═══════════════════════════════════════════════════════════ */

// Set default dates for gochar (current month)
(function(){
    var today = new Date();
    var startEl = document.getElementById('gochar-start');
    var endEl = document.getElementById('gochar-end');
    if (startEl) startEl.value = today.toISOString().slice(0,10);
    if (endEl) {
        var nextMonth = new Date(today);
        nextMonth.setMonth(nextMonth.getMonth() + 1);
        endEl.value = nextMonth.toISOString().slice(0,10);
    }
})();

var gocharBtn = document.getElementById('gochar-fetch');
if (gocharBtn) {
    gocharBtn.addEventListener('click', async function(){
        var resultDiv = document.getElementById('gochar-result');
        var startDate = document.getElementById('gochar-start').value;
        var endDate = document.getElementById('gochar-end').value;
        var ayanamsa = document.getElementById('gochar-ayanamsa').value;

        if (!startDate || !endDate) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Please select both start and end dates</p>';
            return;
        }

        resultDiv.innerHTML = '<p style="color:var(--text-muted)">Calculating planet transits (including Lagna if location available)...</p>';

        // Get lat/lon from master birth data for Lagna
        var latEl = document.getElementById('lat');
        var lonEl = document.getElementById('lon');
        var lat = latEl ? parseFloat(latEl.value) : null;
        var lon = lonEl ? parseFloat(lonEl.value) : null;

        var payload = {
            start_date: startDate,
            end_date: endDate,
            ayanamsa: ayanamsa,
            timezone_offset_minutes: 330
        };
        if (lat && lon && !isNaN(lat) && !isNaN(lon)) {
            payload.latitude = lat;
            payload.longitude = lon;
        }

        try {
            var resp = await fetch(API + '/gochar/transits', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            if (!resp.ok) {
                var errBody = await resp.json().catch(function(){ return {}; });
                throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
            }
            var data = await resp.json();
            renderGochar(data);
        } catch(err) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
        }
    });
}

function renderGochar(data) {
    var resultDiv = document.getElementById('gochar-result');
    var html = '';
    var planetColors = {Sun:'#FFA500',Moon:'#C0C0C0',Mars:'#FF4444',Mercury:'#00CED1',Jupiter:'#FFD700',Venus:'#FF69B4',Saturn:'#4169E1',Rahu:'#8B008B',Ketu:'#808080',Lagna:'#00FF88'};
    var pColor = function(n){ return planetColors[n]||'#ccc'; };

    /* ── Summary Banner ── */
    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:1px solid var(--gold)">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:var(--gold-light)">Gochar Panchang</div>';
    html += '<div style="font-size:0.85rem;color:var(--text-dim);margin-top:4px">' + data.start_date + ' to ' + data.end_date + ' | ' + data.ayanamsa + ' ayanamsa</div>';
    html += '<div style="font-size:1.1rem;font-weight:700;color:var(--text);margin-top:6px">' + data.total_events + ' Transit Events</div>';
    html += '</div>';

    /* ── Current Planet Positions ── */
    html += '<div class="card" style="margin-bottom:16px">';
    html += '<h3 style="color:var(--gold-light);margin-bottom:10px">Planet Positions at ' + data.start_date + '</h3>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.82rem">';
    html += '<thead><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>Longitude</th><th>Nakshatra</th><th>Lord</th><th>Pada</th><th>Speed</th><th>Status</th></tr></thead><tbody>';
    data.planet_positions.forEach(function(p){
        var statusColor = p.retrograde ? 'var(--red)' : 'var(--green)';
        var statusText = p.retrograde ? 'R' : 'D';
        html += '<tr>';
        html += '<td style="color:' + p.color + ';font-weight:700">' + p.planet + '</td>';
        html += '<td>' + p.sign + '</td>';
        html += '<td>' + p.degree_in_sign.toFixed(2) + '°</td>';
        html += '<td>' + p.longitude.toFixed(2) + '°</td>';
        html += '<td>' + p.nakshatra + '</td>';
        html += '<td style="color:' + (pColor(p.nakshatra_lord) || '#ccc') + '">' + p.nakshatra_lord + '</td>';
        html += '<td>' + p.pada + '</td>';
        html += '<td>' + p.speed.toFixed(4) + '°/d</td>';
        html += '<td style="color:' + statusColor + ';font-weight:700">' + statusText + '</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    html += '</div>';

    /* ── Per-Planet Summary ── */
    html += '<details style="margin-bottom:16px" class="card"><summary style="cursor:pointer;color:var(--gold-light);font-weight:700;font-size:0.9rem">Per-Planet Event Summary</summary>';
    html += '<div style="overflow-x:auto;margin-top:8px"><table class="data-table" style="font-size:0.82rem">';
    html += '<thead><tr><th>Planet</th><th>Sign Changes</th><th>Nakshatra Changes</th><th>Pada Changes</th><th>Retro Events</th><th>Total</th></tr></thead><tbody>';
    var planetOrder = ['Lagna','Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'];
    planetOrder.forEach(function(pn){
        var s = data.planet_summaries[pn];
        if (!s) return;
        html += '<tr>';
        html += '<td style="color:' + (pColor(pn) || '#ccc') + ';font-weight:700">' + pn + '</td>';
        html += '<td>' + s.sign_changes + '</td>';
        html += '<td>' + s.nakshatra_changes + '</td>';
        html += '<td>' + s.pada_changes + '</td>';
        html += '<td>' + s.retro_events + '</td>';
        html += '<td style="font-weight:700">' + s.total_events + '</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></details>';

    /* ── Filter buttons ── */
    html += '<div class="card" style="margin-bottom:16px">';
    html += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px">';
    html += '<button class="gochar-filter active" data-filter="all" style="padding:4px 10px;border-radius:4px;border:1px solid var(--gold);background:var(--gold);color:#000;font-size:0.78rem;font-weight:700;cursor:pointer">All Events</button>';
    html += '<button class="gochar-filter" data-filter="sign_change" style="padding:4px 10px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.78rem;cursor:pointer">Sign Changes</button>';
    html += '<button class="gochar-filter" data-filter="nakshatra_change" style="padding:4px 10px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.78rem;cursor:pointer">Nakshatra</button>';
    html += '<button class="gochar-filter" data-filter="pada_change" style="padding:4px 10px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.78rem;cursor:pointer">Pada</button>';
    html += '<button class="gochar-filter" data-filter="retro" style="padding:4px 10px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.78rem;cursor:pointer">Retrograde</button>';

    // Planet filters
    html += '<span style="color:var(--text-dim);font-size:0.72rem;margin-left:8px;align-self:center">Planet:</span>';
    planetOrder.forEach(function(pn){
        html += '<button class="gochar-planet-filter" data-planet="' + pn + '" style="padding:4px 8px;border-radius:4px;border:1px solid #555;background:transparent;color:' + (pColor(pn) || '#ccc') + ';font-size:0.72rem;cursor:pointer">' + pn + '</button>';
    });
    html += '</div>';
    html += '<div id="gochar-visible-count" style="font-size:0.75rem;color:var(--text-dim);margin-top:6px">' + data.events.length + ' events shown</div>';

    /* ── Main Events Table ── */
    html += '<div style="overflow-x:auto"><table class="data-table" id="gochar-events-table" style="font-size:0.78rem">';
    html += '<thead><tr><th>Date</th><th>Time</th><th>Planet</th><th>Event</th><th>Details</th></tr></thead><tbody>';

    data.events.forEach(function(e, idx){
        var evClass = e.event_type;
        var importClass = e.importance === 'high' ? 'font-weight:700;' : '';

        // Event type icon and color
        var icon = '';
        var evColor = e.color || '#ccc';
        if (e.event_type === 'sign_change') icon = '♈';
        else if (e.event_type === 'nakshatra_change') icon = '✦';
        else if (e.event_type === 'pada_change') icon = '·';
        else if (e.event_type === 'retro_start') icon = '℞';
        else if (e.event_type === 'retro_end') icon = '▶';

        // Build detail column
        var detail = '';
        if (e.event_type === 'sign_change') {
            detail = e.from_sign + ' → <b>' + e.to_sign + '</b>';
        } else if (e.event_type === 'nakshatra_change') {
            detail = e.from_nakshatra + ' → <b>' + e.to_nakshatra + '</b> (' + e.to_nak_lord + ')';
        } else if (e.event_type === 'pada_change') {
            detail = e.nakshatra + ' Pada ' + e.from_pada + ' → <b>Pada ' + e.to_pada + '</b>';
        } else if (e.event_type === 'retro_start' || e.event_type === 'retro_end') {
            detail = e.degree + '° ' + e.sign;
        }

        html += '<tr class="gochar-row" data-type="' + evClass + '" data-planet="' + e.planet + '" style="' + importClass + '">';
        html += '<td>' + e.date + '</td>';
        html += '<td>' + e.time + '</td>';
        html += '<td style="color:' + evColor + ';font-weight:700">' + icon + ' ' + e.planet + '</td>';
        html += '<td>' + e.description + '</td>';
        html += '<td>' + detail + '</td>';
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    html += '</div>';

    resultDiv.innerHTML = html;

    /* ── Combined filter logic ── */
    function applyGocharFilters() {
        // Get active event type
        var activeTypeBtn = document.querySelector('.gochar-filter.active');
        var typeFilter = activeTypeBtn ? activeTypeBtn.dataset.filter : 'all';

        // Get active planets
        var activePlanets = [];
        document.querySelectorAll('.gochar-planet-filter.active').forEach(function(b){ activePlanets.push(b.dataset.planet); });

        document.querySelectorAll('.gochar-row').forEach(function(row){
            var showType = true;
            var showPlanet = true;

            // Type filter
            if (typeFilter !== 'all') {
                if (typeFilter === 'retro') {
                    showType = (row.dataset.type === 'retro_start' || row.dataset.type === 'retro_end');
                } else {
                    showType = row.dataset.type === typeFilter;
                }
            }

            // Planet filter
            if (activePlanets.length > 0) {
                showPlanet = activePlanets.indexOf(row.dataset.planet) >= 0;
            }

            row.style.display = (showType && showPlanet) ? '' : 'none';
        });

        // Update count
        var visible = document.querySelectorAll('.gochar-row:not([style*="display: none"])').length;
        var countEl = document.getElementById('gochar-visible-count');
        if (countEl) countEl.textContent = visible + ' events shown';
    }

    /* ── Filter click handlers ── */
    document.querySelectorAll('.gochar-filter').forEach(function(btn){
        btn.addEventListener('click', function(){
            document.querySelectorAll('.gochar-filter').forEach(function(b){ b.classList.remove('active'); b.style.background = 'transparent'; b.style.color = 'var(--text)'; });
            this.classList.add('active'); this.style.background = 'var(--gold)'; this.style.color = '#000';
            applyGocharFilters();
        });
    });

    document.querySelectorAll('.gochar-planet-filter').forEach(function(btn){
        btn.addEventListener('click', function(){
            var planet = this.dataset.planet;
            var isActive = this.classList.toggle('active');
            if (isActive) {
                this.style.background = pColor(planet) || '#555';
                this.style.color = '#000';
            } else {
                this.style.background = 'transparent';
                this.style.color = pColor(planet) || '#ccc';
            }
            applyGocharFilters();
        });
    });
}

})(); // end IIFE

/* ═══════════════════════════════════════════════════════════════
   GOLD PRICE PREDICTOR TAB
   ═══════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════
   LAAL KITAB TAB
   ═══════════════════════════════════════════════════════════════ */

document.getElementById('lk-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultEl = document.getElementById('lk-result');
    const data = await apiCall('/laal-kitab', {
        name: document.getElementById('lk-name').value,
        date: ddmmToApi(document.getElementById('lk-date').value),
        time: document.getElementById('lk-time').value,
        place: document.getElementById('lk-place').value,
        ayanamsa: document.getElementById('lk-ayanamsa').value,
    }, resultEl);
    if (!data) return;
    renderLaalKitab(data);
});

function renderLaalKitab(data) {
    var resultDiv = document.getElementById('lk-result');
    var html = '';
    var lkRed = '#e53935';
    var pColors = {Sun:'#FFA500',Moon:'#C0C0C0',Mars:'#FF4444',Mercury:'#00CED1',Jupiter:'#FFD700',Venus:'#FF69B4',Saturn:'#4169E1',Rahu:'#8B008B',Ketu:'#808080'};
    var pC = function(n){ return pColors[n]||'#ccc'; };

    /* ── Summary Banner ── */
    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid '+lkRed+';background:linear-gradient(135deg,rgba(229,57,53,0.08),transparent)">';
    html += '<div style="font-size:1.5rem;font-weight:800;color:'+lkRed+'">Laal Kitab — Teva Analysis</div>';
    html += '<div style="font-size:0.9rem;color:var(--text);margin-top:4px"><b>' + (data.name || '') + '</b></div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:2px">' + (data.input ? data.input.date + ' | ' + data.input.time + ' | ' + data.input.place : '') + '</div>';
    html += '<div style="font-size:1rem;color:var(--text);margin-top:8px">Ascendant: <b style="color:'+lkRed+'">' + data.ascendant_sign + '</b> (House 1)</div>';
    /* Flatten yogas dict → array */
    var yogasRaw = data.yogas || {};
    var yogas = [];
    if (Array.isArray(yogasRaw)) {
        yogas = yogasRaw;
    } else {
        Object.keys(yogasRaw).forEach(function(cat){
            var items = yogasRaw[cat];
            if (Array.isArray(items)) {
                items.forEach(function(y){
                    y.yoga = y.yoga || (cat.charAt(0).toUpperCase() + cat.slice(1));
                    y.nature = y.nature || (cat === 'tabet' || cat === 'panauti' || cat === 'grahan' ? 'malefic' : 'benefic');
                    yogas.push(y);
                });
            }
        });
    }
    if (yogas.length > 0) {
        html += '<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-top:10px">';
        yogas.forEach(function(y){
            var yClr = y.nature === 'benefic' ? 'var(--green)' : y.nature === 'malefic' ? 'var(--red)' : '#FFA500';
            html += '<span style="font-size:0.7rem;padding:2px 8px;border-radius:12px;border:1px solid '+yClr+';color:'+yClr+';font-weight:600">'+y.yoga+'</span>';
        });
        html += '</div>';
    }
    html += '</div>';

    /* ── Sub-tab navigation ── */
    html += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px">';
    var lkTabs = [
        {id:'lk-predictions',label:'Predictions',icon:'📖'},
        {id:'lk-house-map',label:'House Map',icon:'🏠'},
        {id:'lk-yogas',label:'Yogas',icon:'🔮'},
        {id:'lk-financial',label:'Financial',icon:'💰'},
        {id:'lk-luck',label:'Luck Activation',icon:'🍀'},
        {id:'lk-conjunctions',label:'Conjunctions',icon:'🤝'},
        {id:'lk-debts',label:'Debts (Rin)',icon:'⚖️'},
        {id:'lk-states',label:'Planet States',icon:'👁️'},
        {id:'lk-remedies',label:'Remedies',icon:'🙏'},
        {id:'lk-nakshatras',label:'Nakshatras',icon:'⭐'},
    ];
    lkTabs.forEach(function(t, i){
        var active = i === 0;
        html += '<button class="lk-sub-tab" data-lk-tab="'+t.id+'" style="padding:6px 14px;border:1px solid '+(active?lkRed:'var(--border)')+';background:'+(active?lkRed:'transparent')+';color:'+(active?'#fff':'var(--text)')+';border-radius:6px;cursor:pointer;font-size:0.82rem;font-weight:600">'+t.icon+' '+t.label+'</button>';
    });
    html += '</div>';

    /* ══════════════════════════════════════════
       PREDICTIONS TAB (Enhanced)
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-predictions">';
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+lkRed+';margin-bottom:10px">Planet-in-House Predictions (Teva)</h3>';
    (data.predictions || []).forEach(function(p){
        var dignityClr = p.dignity === 'Exalted' ? 'var(--green)' : p.dignity === 'Debilitated' ? 'var(--red)' : p.dignity === 'Pakka Ghar' ? '#FFD700' : 'var(--text-dim)';
        var dignityBadge = '<span style="background:'+dignityClr+';color:#000;padding:1px 6px;border-radius:3px;font-size:0.65rem;font-weight:700">'+p.dignity+'</span>';
        html += '<div style="border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:12px;background:rgba(229,57,53,0.03)">';
        /* Header */
        html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">';
        html += '<span style="color:'+pC(p.planet)+';font-weight:800;font-size:1.15rem">'+p.planet+'</span>';
        html += '<span style="color:var(--text-dim);font-size:0.85rem">in House '+p.house+' ('+p.sign+')</span>';
        html += dignityBadge;
        if (p.conjunctions && p.conjunctions.length > 0) {
            html += '<span style="font-size:0.75rem;color:var(--text-dim)">with '+p.conjunctions.join(', ')+'</span>';
        }
        html += '</div>';
        /* Core predictions */
        html += '<div style="font-size:0.85rem;color:var(--text);margin-bottom:6px">'+p.effect+'</div>';
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">';
        html += '<div style="font-size:0.8rem;padding:8px;border-radius:6px;background:rgba(76,175,80,0.08);border:1px solid rgba(76,175,80,0.2)"><b style="color:var(--green)">Good Results</b><br>'+p.good_results+'</div>';
        html += '<div style="font-size:0.8rem;padding:8px;border-radius:6px;background:rgba(244,67,54,0.08);border:1px solid rgba(244,67,54,0.2)"><b style="color:var(--red)">Bad Results</b><br>'+p.bad_results+'</div>';
        html += '</div>';
        /* New enhanced fields */
        if (p.financial) {
            html += '<div style="font-size:0.8rem;padding:8px;border-radius:6px;background:rgba(255,215,0,0.08);border:1px solid rgba(255,215,0,0.2);margin-bottom:6px"><b style="color:#FFD700">💰 Financial:</b> '+p.financial+'</div>';
        }
        if (p.health) {
            html += '<div style="font-size:0.8rem;padding:8px;border-radius:6px;background:rgba(100,181,246,0.08);border:1px solid rgba(100,181,246,0.2);margin-bottom:6px"><b style="color:#64b5f6">🏥 Health:</b> '+p.health+'</div>';
        }
        if (p.family) {
            html += '<div style="font-size:0.8rem;padding:8px;border-radius:6px;background:rgba(206,147,216,0.08);border:1px solid rgba(206,147,216,0.2);margin-bottom:6px"><b style="color:#ce93d8">👨‍👩‍👧 Family:</b> '+p.family+'</div>';
        }
        /* Age triggers */
        if (p.age_triggers && p.age_triggers.length > 0) {
            html += '<div style="font-size:0.78rem;margin-bottom:6px"><b style="color:'+lkRed+'">⏰ Age Triggers:</b> ';
            p.age_triggers.forEach(function(at, idx){
                html += '<span style="display:inline-block;margin:2px;padding:1px 7px;border-radius:10px;background:rgba(229,57,53,0.1);border:1px solid rgba(229,57,53,0.25);font-size:0.72rem">'+at+'</span>';
            });
            html += '</div>';
        }
        /* Conditional modifiers */
        if (p.conditions && p.conditions.length > 0) {
            html += '<div style="font-size:0.78rem;padding:6px 8px;border-radius:6px;background:rgba(255,255,255,0.03);border:1px solid var(--border);margin-bottom:6px">';
            html += '<b style="color:#FFA500">⚡ Conditional Effects:</b><ul style="margin:4px 0 0 16px;padding:0">';
            p.conditions.forEach(function(c){
                html += '<li style="margin-bottom:2px">'+c+'</li>';
            });
            html += '</ul></div>';
        }
        /* Remedy */
        html += '<div style="font-size:0.82rem;color:#64b5f6;padding:6px 8px;border-radius:6px;background:rgba(100,181,246,0.05)"><b>🙏 Upay:</b> '+p.remedy+'</div>';
        html += '</div>';
    });
    html += '</div></div>';

    /* ══════════════════════════════════════════
       HOUSE MAP TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-house-map" style="display:none">';
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+lkRed+';margin-bottom:10px">House-wise Planet Placement (Teva)</h3>';
    html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:8px">Ascendant '+data.ascendant_sign+' = House 1. Houses counted from ascendant sign.</p>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.82rem">';
    html += '<thead><tr><th>House</th><th>Sign</th><th>Planets</th><th>Status</th></tr></thead><tbody>';
    var hs = data.house_summary || {};
    for (var h = 1; h <= 12; h++) {
        var hd = hs[h] || hs[String(h)] || {};
        var planets = hd.planets || [];
        var isEmpty = planets.length === 0;
        var pList = planets.map(function(pn){ return '<span style="color:'+pC(pn)+';font-weight:700">'+pn+'</span>'; }).join(', ');
        html += '<tr>';
        html += '<td style="font-weight:700;color:'+lkRed+'">H'+h+(h===1?' (Asc)':'')+'</td>';
        html += '<td>'+(hd.sign||'')+'</td>';
        html += '<td>'+(isEmpty ? '<span style="color:var(--text-dim)">Empty</span>' : pList)+'</td>';
        html += '<td>'+(isEmpty ? '—' : planets.length+' planet'+(planets.length>1?'s':''))+'</td>';
        html += '</tr>';
    }
    html += '</tbody></table></div>';
    /* Planet → House chips */
    html += '<div style="margin-top:12px;padding:10px;background:rgba(229,57,53,0.05);border-radius:6px;border:1px solid rgba(229,57,53,0.2)">';
    html += '<div style="font-size:0.8rem;font-weight:700;color:'+lkRed+';margin-bottom:6px">Planet → LK House Mapping</div>';
    var phMap = data.planet_houses || {};
    Object.keys(phMap).forEach(function(pn){
        html += '<span style="display:inline-block;margin:2px 4px;padding:2px 8px;border-radius:4px;font-size:0.75rem;background:rgba(229,57,53,0.1);border:1px solid rgba(229,57,53,0.3)">';
        html += '<span style="color:'+pC(pn)+';font-weight:700">'+pn+'</span> → H'+phMap[pn];
        html += '</span>';
    });
    html += '</div></div></div>';

    /* ══════════════════════════════════════════
       YOGAS TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-yogas" style="display:none">';
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+lkRed+';margin-bottom:10px">LK Yogas — Dharmi, Kamini, Tabet, Panauti & More</h3>';
    html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:10px">Laal Kitab identifies special planetary combinations (Yogas) that amplify or diminish results.</p>';
    if (yogas.length === 0) {
        html += '<div style="text-align:center;padding:20px;color:var(--text-dim)">No special yogas detected in this chart.</div>';
    } else {
        yogas.forEach(function(y){
            var yClr = y.nature === 'benefic' ? 'var(--green)' : y.nature === 'malefic' ? 'var(--red)' : '#FFA500';
            var yBg = y.nature === 'benefic' ? 'rgba(76,175,80,0.06)' : y.nature === 'malefic' ? 'rgba(244,67,54,0.06)' : 'rgba(255,165,0,0.06)';
            var yBdr = y.nature === 'benefic' ? 'rgba(76,175,80,0.3)' : y.nature === 'malefic' ? 'rgba(244,67,54,0.3)' : 'rgba(255,165,0,0.3)';
            html += '<div style="border:1px solid '+yBdr+';border-left:4px solid '+yClr+';border-radius:8px;padding:12px;margin-bottom:10px;background:'+yBg+'">';
            html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">';
            html += '<span style="font-weight:800;font-size:1.05rem;color:'+yClr+'">'+y.yoga+'</span>';
            html += '<span style="font-size:0.68rem;padding:1px 6px;border-radius:3px;background:'+yClr+';color:#fff;font-weight:700;text-transform:uppercase">'+y.nature+'</span>';
            html += '</div>';
            /* Planets involved */
            if (y.planets) {
                html += '<div style="font-size:0.8rem;margin-bottom:4px"><b>Planets:</b> ';
                (Array.isArray(y.planets) ? y.planets : [y.planets]).forEach(function(pn){
                    html += '<span style="color:'+pC(pn)+';font-weight:700;margin-right:6px">'+pn+'</span>';
                });
                html += '</div>';
            }
            if (y.planet) {
                html += '<div style="font-size:0.8rem;margin-bottom:4px"><b>Planet:</b> <span style="color:'+pC(y.planet)+';font-weight:700">'+y.planet+'</span> in H'+(y.house||'?')+'</div>';
            }
            html += '<div style="font-size:0.82rem;color:var(--text);margin-bottom:4px">'+(y.description||y.effect||'')+'</div>';
            if (y.financial) {
                html += '<div style="font-size:0.8rem;color:#FFD700;margin-bottom:4px"><b>💰 Financial Impact:</b> '+y.financial+'</div>';
            }
            if (y.remedy) {
                html += '<div style="font-size:0.8rem;color:#64b5f6"><b>🙏 Remedy:</b> '+y.remedy+'</div>';
            }
            html += '</div>';
        });
    }
    html += '</div></div>';

    /* ══════════════════════════════════════════
       FINANCIAL ANALYSIS TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-financial" style="display:none">';
    var fin = data.financial_analysis || {};
    html += '<div class="card" style="margin-bottom:12px;border:1px solid rgba(255,215,0,0.3)"><h3 style="color:#FFD700;margin-bottom:10px">💰 Financial Analysis — Laal Kitab</h3>';

    /* Wealth Houses */
    var wh = fin.wealth_houses || {};
    html += '<div style="margin-bottom:14px"><h4 style="color:'+lkRed+';font-size:0.9rem;margin-bottom:6px">Wealth Houses (H2, H6, H11)</h4>';
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px">';
    var whKeys = [
        {key:'h2_family_wealth', lbl:'H2 — Family Wealth', clr:'var(--green)'},
        {key:'h6_debts', lbl:'H6 — Debts/Enemies', clr:'var(--red)'},
        {key:'h11_gains', lbl:'H11 — Gains/Income', clr:'var(--green)'},
    ];
    whKeys.forEach(function(wk){
        var hData = wh[wk.key] || {};
        html += '<div style="padding:8px;border-radius:6px;border:1px solid var(--border);background:rgba(255,215,0,0.03)">';
        html += '<div style="font-weight:700;font-size:0.8rem;color:'+wk.clr+';margin-bottom:4px">'+wk.lbl+'</div>';
        if (hData.planets && hData.planets.length > 0) {
            hData.planets.forEach(function(pn){ html += '<span style="color:'+pC(pn)+';font-weight:700;margin-right:4px;font-size:0.82rem">'+pn+'</span>'; });
        } else {
            html += '<span style="color:var(--text-dim);font-size:0.78rem">Empty</span>';
        }
        if (hData.analysis) html += '<div style="font-size:0.75rem;color:var(--text-dim);margin-top:4px">'+hData.analysis+'</div>';
        html += '</div>';
    });
    html += '</div></div>';

    /* Wealth & Blocking planets */
    var wp = fin.wealth_planets || [];
    var bp = fin.blocking_planets || [];
    if (wp.length > 0 || bp.length > 0) {
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">';
        html += '<div style="padding:10px;border-radius:6px;background:rgba(76,175,80,0.06);border:1px solid rgba(76,175,80,0.2)">';
        html += '<div style="font-weight:700;font-size:0.85rem;color:var(--green);margin-bottom:6px">Wealth-Giving Planets</div>';
        wp.forEach(function(w){
            var secs = Array.isArray(w.sectors) ? w.sectors.join(', ') : (w.sectors||'');
            html += '<div style="font-size:0.8rem;margin-bottom:3px"><span style="color:'+pC(w.planet)+';font-weight:700">'+w.planet+'</span> (H'+w.house+') — <span style="color:var(--text-dim)">'+w.reason+'</span>';
            if (secs) html += '<div style="font-size:0.72rem;color:var(--text-dim);margin-left:8px">Sectors: '+secs+'</div>';
            html += '</div>';
        });
        if (wp.length === 0) html += '<span style="color:var(--text-dim);font-size:0.78rem">None identified</span>';
        html += '</div>';
        html += '<div style="padding:10px;border-radius:6px;background:rgba(244,67,54,0.06);border:1px solid rgba(244,67,54,0.2)">';
        html += '<div style="font-weight:700;font-size:0.85rem;color:var(--red);margin-bottom:6px">Wealth-Blocking Planets</div>';
        bp.forEach(function(b){
            var bsecs = Array.isArray(b.blocked_sectors) ? b.blocked_sectors.join(', ') : (b.blocked_sectors||'');
            html += '<div style="font-size:0.8rem;margin-bottom:3px"><span style="color:'+pC(b.planet)+';font-weight:700">'+b.planet+'</span> (H'+b.house+') — <span style="color:var(--text-dim)">'+b.reason+'</span>';
            if (bsecs) html += '<div style="font-size:0.72rem;color:var(--text-dim);margin-left:8px">Blocked: '+bsecs+'</div>';
            html += '</div>';
        });
        if (bp.length === 0) html += '<span style="color:var(--text-dim);font-size:0.78rem">None identified</span>';
        html += '</div></div>';
    }

    /* Property & Business */
    var prop = fin.property_indicators || {};
    var biz = fin.business_indicators || {};
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">';
    html += '<div style="padding:10px;border-radius:6px;border:1px solid var(--border)">';
    html += '<div style="font-weight:700;font-size:0.85rem;color:#FFA500;margin-bottom:4px">🏠 Property (H4)</div>';
    html += '<div style="font-size:0.8rem;color:var(--text)">'+(prop.analysis||'No specific indicators')+'</div>';
    html += '</div>';
    html += '<div style="padding:10px;border-radius:6px;border:1px solid var(--border)">';
    html += '<div style="font-weight:700;font-size:0.85rem;color:#00CED1;margin-bottom:4px">💼 Business (H7/H10)</div>';
    html += '<div style="font-size:0.8rem;color:var(--text)">'+(biz.analysis||'No specific indicators')+'</div>';
    html += '</div></div>';

    /* Debt Risk */
    var dr = fin.debt_risk || {};
    if (dr.analysis) {
        html += '<div style="padding:10px;border-radius:6px;border:1px solid rgba(244,67,54,0.2);background:rgba(244,67,54,0.04);margin-bottom:14px">';
        html += '<div style="font-weight:700;font-size:0.85rem;color:var(--red);margin-bottom:4px">⚠️ Debt Risk (H6/H8/H12)</div>';
        html += '<div style="font-size:0.8rem;color:var(--text)">'+dr.analysis+'</div>';
        html += '</div>';
    }

    /* Investment Advice */
    var inv = fin.investment_advice || {};
    var investIn = Array.isArray(inv.invest_in) ? inv.invest_in : (Array.isArray(inv) ? inv : []);
    if (investIn.length > 0) {
        html += '<div style="padding:10px;border-radius:6px;border:1px solid rgba(255,215,0,0.3);background:rgba(255,215,0,0.05);margin-bottom:14px">';
        html += '<div style="font-weight:700;font-size:0.9rem;color:#FFD700;margin-bottom:8px">📊 Recommended Investment Sectors</div>';
        html += '<div style="display:flex;flex-wrap:wrap;gap:6px">';
        investIn.forEach(function(sec){
            html += '<span style="font-size:0.78rem;padding:3px 10px;border-radius:12px;background:rgba(255,215,0,0.12);border:1px solid rgba(255,215,0,0.3);color:#FFD700;font-weight:600">'+sec+'</span>';
        });
        html += '</div>';
        /* Show planet-wise sector breakdown from wealth_planets */
        if (wp.length > 0) {
            html += '<div style="margin-top:10px;font-size:0.78rem;color:var(--text-dim)">';
            wp.forEach(function(w){
                var secs = Array.isArray(w.sectors) ? w.sectors.join(', ') : '';
                if (secs) html += '<div style="margin-bottom:2px"><span style="color:'+pC(w.planet)+';font-weight:700">'+w.planet+'</span> → '+secs+'</div>';
            });
            html += '</div>';
        }
        html += '</div>';
    }

    /* Best periods */
    var bestP = fin.best_period_for_wealth || [];
    if (bestP.length > 0) {
        html += '<div style="padding:10px;border-radius:6px;border:1px solid rgba(76,175,80,0.3);background:rgba(76,175,80,0.05)">';
        html += '<div style="font-weight:700;font-size:0.85rem;color:var(--green);margin-bottom:6px">⏰ Best Periods for Wealth</div>';
        bestP.forEach(function(bp){
            html += '<div style="font-size:0.8rem;margin-bottom:3px"><span style="color:'+pC(bp.planet)+';font-weight:700">'+bp.planet+'</span> (H'+(bp.house||'?')+'): '+(bp.trigger||bp.period||'')+'</div>';
        });
        html += '</div>';
    }
    html += '</div></div>';

    /* ══════════════════════════════════════════
       LUCK ACTIVATION TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-luck" style="display:none">';
    var luck = data.luck_activation || {};
    var guide = luck.guide || {};
    html += '<div class="card" style="margin-bottom:12px;border:1px solid rgba(76,175,80,0.3)"><h3 style="color:var(--green);margin-bottom:10px">🍀 Luck Activation — '+data.ascendant_sign+' Ascendant</h3>';

    /* Lucky items grid */
    html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-bottom:14px">';
    var luckyItems = [
        {label:'Lucky Colors', val: guide.lucky_colors, icon:'🎨'},
        {label:'Lucky Numbers', val: guide.lucky_numbers, icon:'🔢'},
        {label:'Lucky Days', val: guide.lucky_days, icon:'📅'},
        {label:'Lucky Metals', val: guide.lucky_metals, icon:'⚙️'},
        {label:'Lucky Stones', val: guide.lucky_stones, icon:'💎'},
    ];
    luckyItems.forEach(function(li){
        var val = Array.isArray(li.val) ? li.val.join(', ') : (li.val||'—');
        html += '<div style="padding:8px;border-radius:6px;text-align:center;border:1px solid var(--border);background:rgba(76,175,80,0.03)">';
        html += '<div style="font-size:1.2rem">'+li.icon+'</div>';
        html += '<div style="font-size:0.72rem;color:var(--text-dim);font-weight:700;margin-top:2px">'+li.label+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text);font-weight:600;margin-top:2px">'+val+'</div>';
        html += '</div>';
    });
    html += '</div>';

    /* Lucky & Dangerous Planets */
    var lps = luck.lucky_planets_status || [];
    var dps = luck.dangerous_planets_status || [];
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">';
    html += '<div style="padding:10px;border-radius:6px;background:rgba(76,175,80,0.06);border:1px solid rgba(76,175,80,0.2)">';
    html += '<div style="font-weight:700;font-size:0.85rem;color:var(--green);margin-bottom:6px">Lucky Planets</div>';
    if (lps.length > 0) {
        lps.forEach(function(lp){
            html += '<div style="font-size:0.8rem;margin-bottom:3px"><span style="color:'+pC(lp.planet)+';font-weight:700">'+lp.planet+'</span>';
            html += ' <span style="font-size:0.7rem;color:var(--text-dim)">H'+(lp.house||'?')+'</span>';
            html += ' — <span style="color:var(--text-dim)">'+lp.status+'</span></div>';
        });
    } else {
        (guide.lucky_planets||[]).forEach(function(pn){
            html += '<span style="color:'+pC(pn)+';font-weight:700;margin-right:6px">'+pn+'</span>';
        });
    }
    html += '</div>';
    html += '<div style="padding:10px;border-radius:6px;background:rgba(244,67,54,0.06);border:1px solid rgba(244,67,54,0.2)">';
    html += '<div style="font-weight:700;font-size:0.85rem;color:var(--red);margin-bottom:6px">Dangerous Planets</div>';
    if (dps.length > 0) {
        dps.forEach(function(dp){
            html += '<div style="font-size:0.8rem;margin-bottom:3px"><span style="color:'+pC(dp.planet)+';font-weight:700">'+dp.planet+'</span>';
            html += ' <span style="font-size:0.7rem;color:var(--text-dim)">H'+(dp.house||'?')+'</span>';
            html += ' — <span style="color:var(--text-dim)">'+dp.status+'</span></div>';
        });
    } else {
        (guide.dangerous_planets||[]).forEach(function(pn){
            html += '<span style="color:'+pC(pn)+';font-weight:700;margin-right:6px">'+pn+'</span>';
        });
    }
    html += '</div></div>';

    /* Activation Remedies, Career, Wealth, Relationship, Health */
    var sections = [
        {key:'activation_remedies', title:'🔑 Activation Remedies', clr:'#64b5f6'},
        {key:'career_directions', title:'💼 Career Directions', clr:'#FFD700'},
        {key:'wealth_activation', title:'💰 Wealth Activation', clr:'var(--green)'},
        {key:'relationship_tips', title:'❤️ Relationship Tips', clr:'#FF69B4'},
        {key:'health_watch', title:'🏥 Health Watch', clr:'#FFA500'},
    ];
    sections.forEach(function(sec){
        var val = guide[sec.key];
        if (val) {
            var content = Array.isArray(val) ? val.join(' | ') : val;
            html += '<div style="padding:10px;border-radius:6px;border:1px solid var(--border);margin-bottom:8px">';
            html += '<div style="font-weight:700;font-size:0.85rem;color:'+sec.clr+';margin-bottom:4px">'+sec.title+'</div>';
            html += '<div style="font-size:0.82rem;color:var(--text)">'+content+'</div>';
            html += '</div>';
        }
    });

    /* Personalized activation */
    var pa = luck.personalized_activation;
    if (pa) {
        html += '<div style="padding:10px;border-radius:6px;border:2px solid rgba(76,175,80,0.4);background:rgba(76,175,80,0.05);margin-bottom:8px">';
        html += '<div style="font-weight:700;font-size:0.9rem;color:var(--green);margin-bottom:6px">🌟 Personalized Activation</div>';
        if (Array.isArray(pa)) {
            pa.forEach(function(step, idx){
                html += '<div style="font-size:0.82rem;margin-bottom:4px;padding-left:8px;border-left:2px solid var(--green)">';
                html += '<b style="color:'+lkRed+'">'+(idx+1)+'.</b> '+step;
                html += '</div>';
            });
        } else {
            html += '<div style="font-size:0.82rem;color:var(--text)">'+pa+'</div>';
        }
        html += '</div>';
    }
    html += '</div></div>';

    /* ══════════════════════════════════════════
       CONJUNCTION EFFECTS TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-conjunctions" style="display:none">';
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+lkRed+';margin-bottom:10px">🤝 Planetary Conjunctions</h3>';
    html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:10px">When two or more planets share a house in Laal Kitab, they modify each other\'s results.</p>';
    var conj = data.conjunction_effects || [];
    if (conj.length === 0) {
        html += '<div style="text-align:center;padding:20px;color:var(--text-dim)">No planetary conjunctions in this chart.</div>';
    } else {
        conj.forEach(function(c){
            html += '<div style="border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:10px;background:rgba(229,57,53,0.03)">';
            html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">';
            html += '<span style="color:'+pC(c.planet_1||c.planet1)+';font-weight:800">'+(c.planet_1||c.planet1)+'</span>';
            html += '<span style="color:var(--text-dim)">+</span>';
            html += '<span style="color:'+pC(c.planet_2||c.planet2)+';font-weight:800">'+(c.planet_2||c.planet2)+'</span>';
            html += '<span style="color:var(--text-dim);font-size:0.8rem">in House '+(c.house||'?')+'</span>';
            html += '</div>';
            html += '<div style="font-size:0.82rem;color:var(--text);margin-bottom:4px">'+c.effect+'</div>';
            if (c.financial) {
                html += '<div style="font-size:0.8rem;color:#FFD700;margin-bottom:4px"><b>💰 Financial:</b> '+c.financial+'</div>';
            }
            if (c.remedy) {
                html += '<div style="font-size:0.8rem;color:#64b5f6"><b>🙏 Remedy:</b> '+c.remedy+'</div>';
            }
            html += '</div>';
        });
    }
    html += '</div></div>';

    /* ══════════════════════════════════════════
       DEBTS (RIN) TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-debts" style="display:none">';
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+lkRed+';margin-bottom:10px">⚖️ Planetary Debts (Rins)</h3>';
    html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:10px">Laal Kitab identifies 5 types of karmic debts (Rin). Active debts indicate areas requiring urgent remedial measures.</p>';
    var debts = data.debts || [];
    if (debts.length === 0) {
        html += '<div style="text-align:center;padding:20px;color:var(--green);font-weight:700;font-size:1.1rem">No active debts found — Good karma!</div>';
    } else {
        debts.forEach(function(d){
            html += '<div style="border:1px solid var(--border);border-left:4px solid var(--red);border-radius:8px;padding:12px;margin-bottom:10px">';
            html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">';
            html += '<span style="font-weight:800;font-size:1rem;color:'+lkRed+'">'+(d.label||d.debt)+'</span>';
            html += '<span style="font-size:0.7rem;padding:1px 6px;border-radius:3px;background:var(--red);color:#fff;font-weight:700">Active</span>';
            html += '</div>';
            html += '<div style="font-size:0.82rem;color:var(--text);margin-bottom:4px"><b>Description:</b> '+(d.description||'')+'</div>';
            if (d.symptoms) {
                html += '<div style="font-size:0.82rem;color:#FFA500;margin-bottom:4px"><b>Symptoms:</b> '+d.symptoms+'</div>';
            }
            if (d.triggers && d.triggers.length > 0) {
                html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:4px"><b>Triggers:</b> '+d.triggers.join(', ')+'</div>';
            }
            if (d.remedy) {
                html += '<div style="font-size:0.82rem;color:#64b5f6;margin-top:4px"><b>🙏 Remedy:</b> '+d.remedy+'</div>';
            }
            html += '</div>';
        });
    }
    html += '</div></div>';

    /* ══════════════════════════════════════════
       PLANET STATES TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-states" style="display:none">';
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+lkRed+';margin-bottom:10px">👁️ Planet States — Soya / Andha / Jaagta</h3>';
    html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:10px">Jaagta (Awake) = full results, Soya (Sleeping) = delayed/dormant, Andha (Blind) = reversed/wrong results.</p>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.82rem">';
    html += '<thead><tr><th>Planet</th><th>House</th><th>State</th><th>Strength</th><th>Friends</th><th>Enemies</th><th>Details</th></tr></thead><tbody>';
    var states = data.planet_states || [];
    states.forEach(function(s){
        var stLower = (s.state||'').toLowerCase();
        var stClr = stLower.indexOf('awake')>=0||stLower.indexOf('jaagta')>=0 ? 'var(--green)' : stLower.indexOf('sleeping')>=0||stLower.indexOf('soya')>=0 ? '#FFA500' : stLower.indexOf('blind')>=0||stLower.indexOf('andha')>=0 ? 'var(--red)' : 'var(--text-dim)';
        var stIcon = stLower.indexOf('awake')>=0||stLower.indexOf('jaagta')>=0 ? '👁️' : stLower.indexOf('sleeping')>=0||stLower.indexOf('soya')>=0 ? '😴' : stLower.indexOf('blind')>=0||stLower.indexOf('andha')>=0 ? '🔒' : '—';
        html += '<tr>';
        html += '<td style="color:'+pC(s.planet)+';font-weight:700">'+s.planet+'</td>';
        html += '<td>H'+(s.house||'—')+'</td>';
        html += '<td style="color:'+stClr+';font-weight:700">'+stIcon+' '+s.state+'</td>';
        html += '<td style="font-weight:600">'+(s.strength||'—')+'</td>';
        html += '<td style="font-size:0.75rem;color:var(--green)">'+(s.friends_supporting&&s.friends_supporting.length?s.friends_supporting.map(function(f){return '<span style="color:'+pC(f)+'">'+f+'</span>';}).join(', '):'—')+'</td>';
        html += '<td style="font-size:0.75rem;color:var(--red)">'+(s.enemies_affecting&&s.enemies_affecting.length?s.enemies_affecting.map(function(f){return '<span style="color:'+pC(f)+'">'+f+'</span>';}).join(', '):'—')+'</td>';
        html += '<td style="font-size:0.75rem">'+(s.description||'')+'</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div></div></div>';

    /* ══════════════════════════════════════════
       REMEDIES TAB
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-remedies" style="display:none">';
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+lkRed+';margin-bottom:10px">🙏 Remedies (Upay)</h3>';
    var remedies = data.remedies || [];
    if (remedies.length === 0) {
        html += '<div style="text-align:center;padding:20px;color:var(--green);font-weight:700;font-size:1.1rem">No urgent remedies needed!</div>';
    } else {
        remedies.sort(function(a,b){ return a.urgency === 'High' ? -1 : b.urgency === 'High' ? 1 : 0; });
        remedies.forEach(function(r){
            var urgClr = r.urgency === 'High' ? 'var(--red)' : '#FFA500';
            html += '<div style="border:1px solid var(--border);border-radius:8px;padding:12px;margin-bottom:10px;background:rgba(100,181,246,0.03)">';
            html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">';
            html += '<span style="color:'+pC(r.planet)+';font-weight:800;font-size:1rem">'+r.planet+'</span>';
            html += '<span style="color:var(--text-dim);font-size:0.8rem">in House '+r.house+'</span>';
            html += '<span style="font-size:0.7rem;padding:1px 6px;border-radius:3px;background:'+urgClr+';color:#fff;font-weight:700">'+r.urgency+'</span>';
            html += '</div>';
            if (r.issue) {
                html += '<div style="font-size:0.82rem;color:var(--red);margin-bottom:4px"><b>Issue:</b> '+r.issue+'</div>';
            }
            html += '<div style="font-size:0.85rem;color:#64b5f6;font-weight:600"><b>🙏 Upay:</b> '+r.remedy+'</div>';
            html += '</div>';
        });
    }
    html += '</div></div>';

    /* ══════════════════════════════════════════
       NAKSHATRAS TAB (separate API call)
       ══════════════════════════════════════════ */
    html += '<div class="lk-tab-pane" id="lk-nakshatras" style="display:none">';
    html += '<div class="card" style="margin-bottom:12px;border:1px solid rgba(255,215,0,0.3)">';
    html += '<h3 style="color:#FFD700;margin-bottom:8px">⭐ Nakshatra-Planet Deep Predictions</h3>';
    html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:12px">Advanced analysis: each planet\'s nakshatra placement reveals personality, events, career, relationships, health, finances, and spiritual path. Multi-planet nakshatra effects included.</p>';
    html += '<button id="lk-fetch-nakshatras" style="padding:8px 20px;background:#FFD700;color:#000;font-weight:700;border:none;border-radius:6px;cursor:pointer;font-size:0.9rem">⭐ Fetch Nakshatra Analysis</button>';
    html += '</div>';
    html += '<div id="lk-nakshatra-result"></div>';
    html += '</div>';

    resultDiv.innerHTML = html;

    /* ── Nakshatra fetch button ── */
    var nakBtn = document.getElementById('lk-fetch-nakshatras');
    if (nakBtn) {
        nakBtn.addEventListener('click', async function(){
            var nakResultDiv = document.getElementById('lk-nakshatra-result');
            nakResultDiv.innerHTML = '<p style="color:#FFD700;text-align:center;padding:20px">⭐ Calculating Nakshatra Predictions...</p>';
            var nakData = await apiCall('/nakshatra-predictions', {
                name: document.getElementById('lk-name').value,
                date: ddmmToApi(document.getElementById('lk-date').value),
                time: document.getElementById('lk-time').value,
                place: document.getElementById('lk-place').value,
                ayanamsa: document.getElementById('lk-ayanamsa').value,
            }, nakResultDiv);
            if (!nakData) return;
            renderNakshatraPredictions(nakData, nakResultDiv);
        });
    }

    /* ── Sub-tab click handler ── */
    document.querySelectorAll('.lk-sub-tab').forEach(function(btn){
        btn.addEventListener('click', function(){
            document.querySelectorAll('.lk-sub-tab').forEach(function(b){
                b.style.background = 'transparent';
                b.style.color = 'var(--text)';
                b.style.borderColor = 'var(--border)';
            });
            this.style.background = lkRed;
            this.style.color = '#fff';
            this.style.borderColor = lkRed;
            var target = this.getAttribute('data-lk-tab');
            document.querySelectorAll('.lk-tab-pane').forEach(function(pane){
                pane.style.display = pane.id === target ? 'block' : 'none';
            });
        });
    });
}

/* ══════════════════════════════════════════════════════════════════
   NAKSHATRA PREDICTIONS RENDERER
   ══════════════════════════════════════════════════════════════════ */

function renderNakshatraPredictions(data, container) {
    var html = '';
    var pColors = {Sun:'#FFA500',Moon:'#C0C0C0',Mars:'#FF4444',Mercury:'#00CED1',Jupiter:'#FFD700',Venus:'#FF69B4',Saturn:'#4169E1',Rahu:'#8B008B',Ketu:'#808080'};
    var pC = function(n){ return pColors[n]||'#ccc'; };
    var gold = '#FFD700';

    /* ── Ascendant Nakshatra Banner ── */
    var asc = data.ascendant_nakshatra || {};
    html += '<div class="card" style="margin-bottom:14px;border:2px solid '+gold+';background:linear-gradient(135deg,rgba(255,215,0,0.06),transparent)">';
    html += '<div style="text-align:center;margin-bottom:10px">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:'+gold+'">Ascendant Nakshatra: '+asc.nakshatra+'</div>';
    html += '<div style="font-size:0.85rem;color:var(--text-dim)">Lord: <b>'+asc.lord+'</b> | Pada: <b>'+asc.pada+'</b> | Navamsha: <b>'+(asc.pada_navamsha||'')+'</b></div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">'+asc.deity+' | '+asc.symbol+'</div>';
    html += '</div>';
    html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">';
    html += '<div style="padding:8px;border-radius:6px;background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.2)">';
    html += '<div style="font-size:0.75rem;font-weight:700;color:'+gold+';margin-bottom:3px">Temperament</div>';
    html += '<div style="font-size:0.8rem;color:var(--text)">'+(asc.temperament||'—')+'</div></div>';
    html += '<div style="padding:8px;border-radius:6px;background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.2)">';
    html += '<div style="font-size:0.75rem;font-weight:700;color:'+gold+';margin-bottom:3px">General Traits</div>';
    html += '<div style="font-size:0.8rem;color:var(--text)">'+(asc.general_traits||'—')+'</div></div>';
    html += '<div style="padding:8px;border-radius:6px;background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.2)">';
    html += '<div style="font-size:0.75rem;font-weight:700;color:'+gold+';margin-bottom:3px">Career Traits</div>';
    html += '<div style="font-size:0.8rem;color:var(--text)">'+(asc.career_traits||'—')+'</div></div>';
    html += '<div style="padding:8px;border-radius:6px;background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.2)">';
    html += '<div style="font-size:0.75rem;font-weight:700;color:'+gold+';margin-bottom:3px">Spiritual Traits</div>';
    html += '<div style="font-size:0.8rem;color:var(--text)">'+(asc.spiritual_traits||'—')+'</div></div>';
    html += '</div></div>';

    /* ── Multi-Planet Nakshatra Effects (if any) ── */
    var multi = data.multi_planet_nakshatras || [];
    if (multi.length > 0) {
        html += '<div class="card" style="margin-bottom:14px;border:1px solid rgba(255,69,0,0.4);background:rgba(255,69,0,0.04)">';
        html += '<h3 style="color:#FF4500;margin-bottom:10px">🔥 Multi-Planet Nakshatra Effects</h3>';
        html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:10px">When 2+ planets share the same nakshatra, their combined energy creates intensified life themes.</p>';
        multi.forEach(function(m){
            html += '<div style="border:1px solid rgba(255,69,0,0.3);border-radius:8px;padding:12px;margin-bottom:10px">';
            html += '<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">';
            html += '<span style="font-weight:800;font-size:1.05rem;color:#FF4500">'+m.nakshatra+'</span>';
            html += '<span style="font-size:0.7rem;padding:2px 8px;border-radius:10px;background:rgba(255,69,0,0.15);color:#FF4500;font-weight:700">'+m.intensity+'</span>';
            m.planets.forEach(function(pn){
                html += '<span style="color:'+pC(pn)+';font-weight:700;font-size:0.9rem">'+pn+'</span>';
            });
            html += '</div>';
            html += '<div style="font-size:0.78rem;color:var(--text-dim);margin-bottom:4px"><b>Deity:</b> '+m.deity+' | <b>Shakti:</b> '+m.shakti+'</div>';
            html += '<div style="font-size:0.82rem;color:var(--text)">'+m.combined_effect+'</div>';
            html += '</div>';
        });
        html += '</div>';
    }

    /* ── Planet-in-Nakshatra Cards ── */
    var planets = data.planet_nakshatras || [];
    html += '<div class="card" style="margin-bottom:12px"><h3 style="color:'+gold+';margin-bottom:10px">⭐ Planet-Nakshatra Blend Predictions</h3>';
    html += '<p style="font-size:0.78rem;color:var(--text-dim);margin-bottom:12px">Each planet blends its energy with the nakshatra it occupies, revealing deep personality and life-event patterns.</p>';

    planets.forEach(function(p){
        html += '<div style="border:1px solid var(--border);border-radius:10px;padding:16px;margin-bottom:14px;background:rgba(255,215,0,0.02)">';

        /* Header */
        html += '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap">';
        html += '<span style="color:'+pC(p.planet)+';font-weight:800;font-size:1.2rem">'+p.planet+'</span>';
        html += '<span style="font-size:0.9rem;color:var(--text)">in <b style="color:'+gold+'">'+p.nakshatra+'</b></span>';
        html += '<span style="font-size:0.75rem;padding:2px 8px;border-radius:10px;background:rgba(255,215,0,0.12);color:'+gold+';border:1px solid rgba(255,215,0,0.3)">Pada '+p.pada+' ('+p.pada_navamsha+')</span>';
        html += '<span style="font-size:0.7rem;color:var(--text-dim)">Lord: '+p.nakshatra_lord+'</span>';
        html += '</div>';

        /* Nakshatra attributes chips */
        html += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px">';
        var attrs = [
            {lbl:'Deity', val:p.deity},
            {lbl:'Symbol', val:p.symbol},
            {lbl:'Shakti', val:p.shakti},
            {lbl:'Guna', val:p.guna},
            {lbl:'Gana', val:p.gana},
            {lbl:'Element', val:p.element},
            {lbl:'Dosha', val:p.dosha},
            {lbl:'Motivation', val:p.motivation},
        ];
        attrs.forEach(function(a){
            if (a.val) html += '<span style="font-size:0.68rem;padding:2px 6px;border-radius:4px;background:rgba(255,255,255,0.05);border:1px solid var(--border);color:var(--text-dim)"><b>'+a.lbl+':</b> '+a.val+'</span>';
        });
        html += '</div>';

        /* Pada quality */
        if (p.pada_quality) {
            html += '<div style="font-size:0.8rem;margin-bottom:8px;padding:6px 8px;border-radius:6px;background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.15)"><b style="color:'+gold+'">Pada '+p.pada+' Quality:</b> '+p.pada_quality+'</div>';
        }

        /* Planet-specific predictions */
        if (p.personality) {
            html += '<div style="font-size:0.85rem;color:var(--text);margin-bottom:8px;padding:8px;border-radius:6px;background:rgba(100,181,246,0.06);border:1px solid rgba(100,181,246,0.2)"><b style="color:#64b5f6">🧠 Personality:</b> '+p.personality+'</div>';
        }
        if (p.nature) {
            html += '<div style="font-size:0.83rem;color:var(--text);margin-bottom:8px;padding:8px;border-radius:6px;background:rgba(206,147,216,0.06);border:1px solid rgba(206,147,216,0.2)"><b style="color:#ce93d8">🌀 Nature:</b> '+p.nature+'</div>';
        }
        if (p.events) {
            html += '<div style="font-size:0.83rem;color:var(--text);margin-bottom:8px;padding:8px;border-radius:6px;background:rgba(255,165,0,0.06);border:1px solid rgba(255,165,0,0.2)"><b style="color:#FFA500">⚡ Key Events:</b> '+p.events+'</div>';
        }

        /* Grid of predictions */
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">';
        var predFields = [
            {key:'career', lbl:'💼 Career', clr:'#00CED1'},
            {key:'relationship', lbl:'❤️ Relationship', clr:'#FF69B4'},
            {key:'health', lbl:'🏥 Health', clr:'#66bb6a'},
            {key:'financial', lbl:'💰 Financial', clr:'#FFD700'},
            {key:'spiritual', lbl:'🙏 Spiritual', clr:'#9C27B0'},
        ];
        predFields.forEach(function(f){
            if (p[f.key]) {
                html += '<div style="padding:8px;border-radius:6px;border:1px solid var(--border);background:rgba(255,255,255,0.02)">';
                html += '<div style="font-size:0.72rem;font-weight:700;color:'+f.clr+';margin-bottom:3px">'+f.lbl+'</div>';
                html += '<div style="font-size:0.78rem;color:var(--text)">'+p[f.key]+'</div>';
                html += '</div>';
            }
        });
        html += '</div>';

        /* Age Events */
        if (p.age_events && p.age_events.length > 0) {
            html += '<div style="padding:8px;border-radius:6px;border:1px solid rgba(255,165,0,0.2);background:rgba(255,165,0,0.04);margin-bottom:8px">';
            html += '<div style="font-size:0.75rem;font-weight:700;color:#FFA500;margin-bottom:4px">⏰ Age-wise Events</div>';
            p.age_events.forEach(function(ae){
                html += '<div style="font-size:0.78rem;color:var(--text);margin-bottom:2px;padding-left:8px;border-left:2px solid #FFA500">'+ae+'</div>';
            });
            html += '</div>';
        }

        /* Remedies */
        if (p.remedies) {
            html += '<div style="font-size:0.82rem;color:#64b5f6;padding:8px;border-radius:6px;background:rgba(100,181,246,0.05);border:1px solid rgba(100,181,246,0.15)"><b>🙏 Remedies:</b> '+p.remedies+'</div>';
        }

        html += '</div>';
    });
    html += '</div>';

    container.innerHTML = html;
}

var SIGNS_LK = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'];

/* Apply DD-MM-YYYY auto-format to gold date inputs */
document.querySelectorAll('.gold-date').forEach(setupDateInput);

var goldBtn = document.getElementById('gold-fetch');
if (goldBtn) {
    goldBtn.addEventListener('click', async function(){
        var resultDiv = document.getElementById('gold-result');
        var startRaw = document.getElementById('gold-start').value;
        var endRaw = document.getElementById('gold-end').value;
        var ayanamsa = document.getElementById('gold-ayanamsa').value;

        if (!startRaw || !endRaw) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Please enter both start and end dates (DD-MM-YYYY)</p>';
            return;
        }

        /* Convert DD-MM-YYYY to YYYY-MM-DD for API */
        var startDate = ddmmToApi(startRaw);
        var endDate = ddmmToApi(endRaw);

        resultDiv.innerHTML = '<p style="color:#FFD700">Calculating gold predictions using Vedic rules...</p>';

        try {
            var resp = await fetch(API + '/gold/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate,
                    ayanamsa: ayanamsa,
                    timezone_offset_minutes: 330
                })
            });
            if (!resp.ok) {
                var errBody = await resp.json().catch(function(){ return {}; });
                throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
            }
            var data = await resp.json();
            renderGold(data);
        } catch(err) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
        }
    });
}

function renderGold(data) {
    var resultDiv = document.getElementById('gold-result');
    var html = '';
    var pColors = {Sun:'#FFA500',Moon:'#C0C0C0',Mars:'#FF4444',Mercury:'#00CED1',Jupiter:'#FFD700',Venus:'#FF69B4',Saturn:'#4169E1',Rahu:'#8B008B',Ketu:'#808080'};
    var pC = function(n){ return pColors[n]||'#ccc'; };

    /* ── Summary Banner ── */
    var sigColor = data.overall_signal.indexOf('BULLISH') >= 0 ? '#FFD700' : data.overall_signal.indexOf('BEARISH') >= 0 ? '#ff5252' : '#bdbdbd';
    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid #FFD700;background:linear-gradient(135deg,rgba(255,215,0,0.08),transparent)">';
    html += '<div style="font-size:1.5rem;font-weight:800;color:#FFD700">Gold Price Prediction</div>';
    html += '<div style="font-size:0.85rem;color:var(--text-dim);margin-top:4px">' + data.start_date + ' to ' + data.end_date + ' | ' + data.ayanamsa + ' ayanamsa | ' + data.total_days + ' days</div>';
    html += '<div style="font-size:2rem;font-weight:900;color:' + sigColor + ';margin-top:10px">' + data.overall_signal + '</div>';
    html += '<div style="font-size:1rem;color:var(--text);margin-top:4px">Average Score: <b>' + data.average_score + '</b></div>';
    html += '<div style="display:flex;justify-content:center;gap:20px;margin-top:12px;font-size:0.85rem">';
    html += '<div><span style="color:#66bb6a;font-weight:700">' + data.bullish_days + '</span> Bullish days</div>';
    html += '<div><span style="color:#bdbdbd;font-weight:700">' + data.neutral_days + '</span> Neutral days</div>';
    html += '<div><span style="color:#ff5252;font-weight:700">' + data.bearish_days + '</span> Bearish days</div>';
    html += '</div></div>';

    /* ── Planet Positions ── */
    html += '<div class="card" style="margin-bottom:16px">';
    html += '<h3 style="color:#FFD700;margin-bottom:10px">Planet Positions & Gold Roles at ' + data.start_date + '</h3>';
    html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.82rem">';
    html += '<thead><tr><th>Planet</th><th>Sign</th><th>Nakshatra</th><th>Status</th><th>Bala</th><th>Gold Role</th><th>Nak Flag</th></tr></thead><tbody>';
    (data.planet_positions || []).forEach(function(p){
        var statusClr = p.retrograde ? 'var(--red)' : 'var(--green)';
        var statusTxt = p.retrograde ? 'Retro' : 'Direct';
        var roleClr = (p.gold_role === 'primary_ruler') ? '#FFD700' : (p.gold_role === 'secondary_ruler') ? '#ffeb3b' : 'var(--text-dim)';
        var nakFlag = '';
        if (p.is_gold_nak) nakFlag = '<span style="background:#FFD700;color:#000;padding:1px 5px;border-radius:3px;font-size:0.65rem;font-weight:700">GOLD</span>';
        else if (p.is_metal_nak) nakFlag = '<span style="background:#90A4AE;color:#000;padding:1px 5px;border-radius:3px;font-size:0.65rem;font-weight:700">METAL</span>';
        html += '<tr>';
        html += '<td style="color:' + pC(p.planet) + ';font-weight:700">' + p.planet + '</td>';
        html += '<td>' + p.sign + '</td>';
        html += '<td>' + p.nakshatra + (p.nakshatra_shloka ? ' <span style="color:var(--text-dim);font-size:0.65rem">(Sh.' + p.nakshatra_shloka + ')</span>' : '') + '</td>';
        html += '<td style="color:' + statusClr + ';font-weight:700">' + statusTxt + '</td>';
        html += '<td>' + (p.kshetra_bala || 0).toFixed(2) + '</td>';
        html += '<td style="color:' + roleClr + ';font-weight:' + (p.gold_role ? '700' : '400') + '">' + (p.gold_role || '—').replace(/_/g,' ') + '</td>';
        html += '<td>' + nakFlag + '</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div>';
    /* Commodities for gold nakshatra planets */
    var goldNakPlanets = (data.planet_positions || []).filter(function(p){ return p.is_gold_nak; });
    if (goldNakPlanets.length > 0) {
        html += '<div style="margin-top:8px;padding:8px;background:rgba(255,215,0,0.08);border-radius:6px;border:1px solid rgba(255,215,0,0.3)">';
        html += '<div style="font-size:0.8rem;font-weight:700;color:#FFD700;margin-bottom:4px">Planets in Gold Nakshatras:</div>';
        goldNakPlanets.forEach(function(p){
            var comms = (p.nakshatra_commodities || []).join(', ');
            html += '<div style="font-size:0.75rem;color:var(--text)"><span style="color:' + pC(p.planet) + ';font-weight:700">' + p.planet + '</span> in ' + p.nakshatra + (comms ? ' — Commodities: ' + comms : '') + '</div>';
        });
        html += '</div>';
    }
    html += '</div>';

    /* ── SBC Vedha Snapshot ── */
    if (data.vedha_snapshot && data.vedha_snapshot.at_start_date) {
        var vs = data.vedha_snapshot.at_start_date;
        if ((vs.vedha_hits && vs.vedha_hits.length > 0) || (vs.ubhayato && vs.ubhayato.length > 0)) {
            html += '<div class="card" style="margin-bottom:16px;border:1px solid rgba(255,215,0,0.3)">';
            html += '<h3 style="color:#FFD700;margin-bottom:8px">SBC Vedha on Gold Nakshatras <span style="font-size:0.75rem;color:var(--text-dim)">at ' + data.start_date + '</span></h3>';
            html += '<div style="display:flex;gap:16px;margin-bottom:8px;font-size:0.82rem">';
            html += '<div>Papa vedha: <span style="color:#ff5252;font-weight:700">' + (vs.papa_count||0) + '</span></div>';
            html += '<div>Shubha vedha: <span style="color:#66bb6a;font-weight:700">' + (vs.shubha_count||0) + '</span></div>';
            html += '<div>Vedha Score: <span style="color:#FFD700;font-weight:700">' + (vs.score >= 0 ? '+' : '') + vs.score + '</span></div>';
            html += '</div>';
            if (vs.vedha_hits && vs.vedha_hits.length > 0) {
                html += '<div style="overflow-x:auto"><table class="data-table" style="font-size:0.78rem">';
                html += '<thead><tr><th>Vedha Planet</th><th>Nature</th><th>Target</th><th>Type</th><th>Score</th><th>Bala</th><th>Shloka</th></tr></thead><tbody>';
                vs.vedha_hits.forEach(function(vh){
                    var natClr = vh.vedha_nature === 'papa' ? '#ff5252' : '#66bb6a';
                    var dirClr = vh.direction.indexOf('bullish') >= 0 ? '#66bb6a' : '#ff5252';
                    html += '<tr>';
                    html += '<td style="color:' + pC(vh.vedha_planet) + ';font-weight:700">' + vh.vedha_planet + '</td>';
                    html += '<td style="color:' + natClr + ';font-weight:700;text-transform:uppercase">' + vh.vedha_nature + '</td>';
                    html += '<td>' + vh.target + '</td>';
                    html += '<td style="color:var(--text-dim);font-size:0.7rem">' + (vh.target_type||'').replace(/_/g,' ') + '</td>';
                    html += '<td style="color:' + dirClr + ';font-weight:700">' + (vh.score >= 0 ? '+' : '') + vh.score + '</td>';
                    html += '<td>' + (vh.graha_bala||0).toFixed(2) + '</td>';
                    html += '<td style="color:var(--text-dim);font-size:0.7rem">' + (vh.shloka||'') + '</td>';
                    html += '</tr>';
                });
                html += '</tbody></table></div>';
            }
            if (vs.ubhayato && vs.ubhayato.length > 0) {
                vs.ubhayato.forEach(function(ub){
                    html += '<div style="margin-top:8px;padding:8px;background:rgba(255,0,0,0.1);border-radius:6px;border:1px solid rgba(255,0,0,0.4)">';
                    html += '<div style="font-weight:800;color:#ff5252;font-size:0.85rem">UBHAYATO VEDHA on ' + ub.target + '</div>';
                    html += '<div style="font-size:0.78rem;color:var(--text)">Planets: ' + ub.planets.join(', ') + ' | Score: +' + ub.score + ' | Shloka ' + ub.shloka + '</div>';
                    html += '<div style="font-size:0.72rem;color:var(--text-dim)">' + ub.detail + '</div>';
                    html += '</div>';
                });
            }
            html += '</div>';
        }
    }

    /* ── Daily Signal Calendar ── */
    html += '<div class="card" style="margin-bottom:16px">';
    html += '<h3 style="color:#FFD700;margin-bottom:10px">Daily Gold Signals</h3>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:12px">';
    (data.daily_signals || []).forEach(function(d, idx){
        var bg = d.signal_color || '#333';
        var txtC = (d.score >= 1.0 || d.score <= -1.0) ? '#000' : '#fff';
        var scoreSign = d.score >= 0 ? '+' : '';
        html += '<div class="gold-day-cell" data-idx="' + idx + '" style="width:42px;height:52px;background:' + bg + ';border-radius:4px;text-align:center;padding:2px;cursor:pointer;font-size:0.65rem;color:' + txtC + ';position:relative;display:flex;flex-direction:column;justify-content:center;border:1px solid rgba(255,255,255,0.1)" title="' + d.date + ' | ' + d.signal + ' | Score: ' + d.score + '">';
        html += '<div style="font-weight:700;font-size:0.6rem">' + d.date.substring(5) + '</div>';
        html += '<div style="font-weight:800;font-size:0.75rem">' + scoreSign + d.score + '</div>';
        html += '<div style="font-size:0.55rem">' + d.weekday + '</div>';
        html += '</div>';
    });
    html += '</div>';

    /* Daily detail panel (shows on click) */
    html += '<div id="gold-day-detail" style="display:none;padding:12px;background:var(--bg-card-alt);border-radius:8px;border:1px solid #FFD700"></div>';
    html += '</div>';

    /* ── Transit Events Timeline ── */
    if (data.events && data.events.length > 0) {
        html += '<div class="card" style="margin-bottom:16px">';
        html += '<h3 style="color:#FFD700;margin-bottom:10px">Gold Transit Events (' + data.events.length + ')</h3>';

        /* Event type filter buttons */
        html += '<div style="margin-bottom:6px;font-size:0.72rem;color:var(--text-dim);font-weight:700">Event Type:</div>';
        html += '<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px">';
        html += '<button class="gold-ev-filter active" data-filter="all" style="padding:3px 9px;border-radius:4px;border:1px solid #FFD700;background:#FFD700;color:#000;font-size:0.75rem;font-weight:700;cursor:pointer">All</button>';
        html += '<button class="gold-ev-filter" data-filter="critical" style="padding:3px 9px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.75rem;cursor:pointer">Critical</button>';
        html += '<button class="gold-ev-filter" data-filter="high" style="padding:3px 9px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.75rem;cursor:pointer">High</button>';
        html += '<button class="gold-ev-filter" data-filter="sign_change" style="padding:3px 9px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.75rem;cursor:pointer">Sign Changes</button>';
        html += '<button class="gold-ev-filter" data-filter="retro" style="padding:3px 9px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.75rem;cursor:pointer">Retro</button>';
        html += '<button class="gold-ev-filter" data-filter="gold_nakshatra" style="padding:3px 9px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.75rem;cursor:pointer">Gold Nak</button>';
        html += '<button class="gold-ev-filter" data-filter="metal_nakshatra" style="padding:3px 9px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.75rem;cursor:pointer">Metal Nak</button>';
        html += '<button class="gold-ev-filter" data-filter="vedha_gold_nak" style="padding:3px 9px;border-radius:4px;border:1px solid #666;background:transparent;color:var(--text);font-size:0.75rem;cursor:pointer">Vedha</button>';
        html += '</div>';

        /* Planet filter buttons */
        var goldPlanetOrder = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'];
        html += '<div style="margin-bottom:4px;font-size:0.72rem;color:var(--text-dim);font-weight:700">Planet:</div>';
        html += '<div style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px">';
        html += '<button class="gold-pl-filter active" data-planet="all" style="padding:3px 9px;border-radius:4px;border:1px solid #FFD700;background:#FFD700;color:#000;font-size:0.75rem;font-weight:700;cursor:pointer">All</button>';
        goldPlanetOrder.forEach(function(pn){
            html += '<button class="gold-pl-filter" data-planet="' + pn + '" style="padding:3px 9px;border-radius:4px;border:1px solid ' + pC(pn) + ';background:transparent;color:' + pC(pn) + ';font-size:0.75rem;font-weight:600;cursor:pointer">' + pn + '</button>';
        });
        html += '</div>';
        html += '<div id="gold-ev-visible-count" style="font-size:0.72rem;color:var(--text-dim);margin-bottom:6px">Showing ' + data.events.length + ' of ' + data.events.length + ' events</div>';

        html += '<div style="overflow-x:auto"><table class="data-table" id="gold-events-table" style="font-size:0.78rem">';
        html += '<thead><tr><th>Date</th><th>Planet</th><th>Event</th><th>Impact</th><th>Gold Effect</th><th>Shloka</th></tr></thead><tbody>';
        data.events.forEach(function(e){
            var effClr = (e.gold_effect || 0) > 0 ? '#66bb6a' : (e.gold_effect || 0) < 0 ? '#ff5252' : '#bdbdbd';
            var effSign = (e.gold_effect || 0) >= 0 ? '+' : '';
            var impClr = e.importance === 'critical' ? '#FFD700' : e.importance === 'high' ? '#ff9800' : '#bdbdbd';
            var evType = e.event_type || '';
            html += '<tr class="gold-ev-row" data-type="' + evType + '" data-importance="' + (e.importance||'medium') + '" data-planet="' + (e.planet||'') + '">';
            html += '<td>' + e.date + '</td>';
            html += '<td style="color:' + (e.color||'#ccc') + ';font-weight:700">' + e.planet + '</td>';
            html += '<td><span style="color:' + impClr + ';font-weight:700;font-size:0.65rem;text-transform:uppercase">' + (e.importance||'') + '</span> ' + evType.replace(/_/g,' ') + '</td>';
            html += '<td style="font-size:0.75rem">' + (e.impact||'') + '</td>';
            html += '<td style="color:' + effClr + ';font-weight:700">' + effSign + (e.gold_effect||0) + '</td>';
            html += '<td style="color:var(--text-dim);font-size:0.7rem">' + (e.shloka||'') + '</td>';
            html += '</tr>';
        });
        html += '</tbody></table></div></div>';
    }

    /* ── Rules Reference ── */
    if (data.rules_used && data.rules_used.length > 0) {
        html += '<details class="card" style="margin-bottom:16px"><summary style="cursor:pointer;color:#FFD700;font-weight:700;font-size:0.9rem">Vedic Rules Applied (' + data.rules_used.length + ')</summary>';
        html += '<div style="margin-top:10px">';
        data.rules_used.forEach(function(r){
            html += '<div style="margin-bottom:10px;padding:8px;background:var(--bg-card-alt);border-radius:6px;border-left:3px solid #FFD700">';
            html += '<div style="font-weight:700;color:var(--text)">' + r.id + '. ' + r.name + ' <span style="color:var(--text-dim);font-size:0.75rem">(Shloka ' + r.shloka + ')</span></div>';
            html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">' + r.description + '</div>';
            html += '</div>';
        });
        html += '</div></details>';
    }

    resultDiv.innerHTML = html;

    /* ── Day cell click handler ── */
    document.querySelectorAll('.gold-day-cell').forEach(function(cell){
        cell.addEventListener('click', function(){
            var idx = parseInt(this.dataset.idx);
            var d = data.daily_signals[idx];
            if (!d) return;
            var detailDiv = document.getElementById('gold-day-detail');
            var dh = '<div style="font-size:1.1rem;font-weight:800;color:#FFD700">' + d.date + ' (' + d.weekday + ') — ' + d.signal + '</div>';
            dh += '<div style="font-size:0.9rem;margin-top:4px">Score: <b style="color:' + d.signal_color + '">' + d.score + '</b> | Day Lord: <b style="color:' + pC(d.day_lord) + '">' + d.day_lord + '</b> | Moon: <b>' + d.moon_nakshatra + '</b> (' + d.moon_sign + ') | Sun: <b>' + d.sun_sign + '</b> | Jupiter: <b>' + d.jupiter_sign + '</b></div>';
            if (d.retro_planets && d.retro_planets.length > 0) {
                dh += '<div style="margin-top:4px;font-size:0.82rem"><span style="color:var(--red)">Retrograde:</span> ' + d.retro_planets.join(', ') + '</div>';
            }
            /* Vedha summary for this day */
            if (d.vedha_summary) {
                var vsum = d.vedha_summary;
                dh += '<div style="margin-top:6px;display:flex;gap:12px;font-size:0.8rem;padding:4px 8px;background:rgba(255,215,0,0.05);border-radius:4px">';
                dh += '<div>SBC Vedha Score: <b style="color:#FFD700">' + (vsum.vedha_score >= 0 ? '+' : '') + vsum.vedha_score + '</b></div>';
                dh += '<div>Papa: <b style="color:#ff5252">' + vsum.papa_count + '</b></div>';
                dh += '<div>Shubha: <b style="color:#66bb6a">' + vsum.shubha_count + '</b></div>';
                if (vsum.ubhayato > 0) dh += '<div style="color:#ff5252;font-weight:700">UBHAYATO: ' + vsum.ubhayato + '</div>';
                dh += '</div>';
            }
            /* Planet nakshatras snapshot */
            if (d.planet_nakshatras) {
                dh += '<div style="margin-top:6px;font-size:0.78rem"><b>Planet Nakshatras:</b> ';
                var pnParts = [];
                Object.keys(d.planet_nakshatras).forEach(function(pn){
                    var pnd = d.planet_nakshatras[pn];
                    var flag = pnd.is_gold_nak ? ' <span style="background:#FFD700;color:#000;padding:0 3px;border-radius:2px;font-size:0.6rem;font-weight:700">GOLD</span>' : (pnd.is_metal_nak ? ' <span style="background:#90A4AE;color:#000;padding:0 3px;border-radius:2px;font-size:0.6rem">METAL</span>' : '');
                    pnParts.push('<span style="color:' + pC(pn) + '">' + pn + '</span>: ' + pnd.nakshatra + flag);
                });
                dh += pnParts.join(' | ');
                dh += '</div>';
            }
            if (d.reasons && d.reasons.length > 0) {
                dh += '<div style="margin-top:8px;font-size:0.82rem;color:var(--text-dim)"><b>Reasons:</b></div>';
                d.reasons.forEach(function(r){
                    dh += '<div style="font-size:0.78rem;padding:2px 0;color:var(--text)">• ' + r + '</div>';
                });
            }
            if (d.active_rules && d.active_rules.length > 0) {
                dh += '<div style="margin-top:8px;font-size:0.82rem;color:var(--text-dim)"><b>Active Rules:</b></div>';
                d.active_rules.forEach(function(ar){
                    var arClr = ar.effect.indexOf('bullish') >= 0 ? '#66bb6a' : ar.effect.indexOf('bearish') >= 0 ? '#ff5252' : '#bdbdbd';
                    dh += '<div style="font-size:0.75rem;padding:2px 8px;margin:2px 0;background:rgba(255,215,0,0.05);border-radius:4px">';
                    dh += '<span style="font-weight:700">' + ar.rule + '</span> <span style="color:var(--text-dim);font-size:0.68rem">(Shloka ' + (ar.shloka||'') + ')</span> ';
                    dh += '<span style="color:' + arClr + ';font-weight:700">' + ar.effect.toUpperCase() + '</span> ';
                    dh += '<span style="color:var(--text-dim)">' + (ar.score >= 0 ? '+' : '') + ar.score + '</span>';
                    if (ar.detail) dh += '<div style="font-size:0.68rem;color:var(--text-dim);margin-top:2px">' + ar.detail + '</div>';
                    dh += '</div>';
                });
            }
            detailDiv.innerHTML = dh;
            detailDiv.style.display = 'block';
        });
    });

    /* ── Combined event + planet filter ── */
    function applyGoldEventFilters() {
        var activeType = 'all';
        var activePlanet = 'all';
        var typeBtn = document.querySelector('.gold-ev-filter.active');
        var plBtn = document.querySelector('.gold-pl-filter.active');
        if (typeBtn) activeType = typeBtn.dataset.filter;
        if (plBtn) activePlanet = plBtn.dataset.planet;

        var visible = 0;
        var total = 0;
        document.querySelectorAll('.gold-ev-row').forEach(function(row){
            total++;
            var showType = false;
            var showPlanet = (activePlanet === 'all') || (row.dataset.planet === activePlanet);

            if (activeType === 'all') {
                showType = true;
            } else if (activeType === 'critical' || activeType === 'high') {
                showType = (row.dataset.importance === activeType);
            } else if (activeType === 'retro') {
                showType = (row.dataset.type === 'retro_start' || row.dataset.type === 'retro_end');
            } else {
                showType = (row.dataset.type === activeType);
            }

            if (showType && showPlanet) {
                row.style.display = '';
                visible++;
            } else {
                row.style.display = 'none';
            }
        });

        var countDiv = document.getElementById('gold-ev-visible-count');
        if (countDiv) countDiv.textContent = 'Showing ' + visible + ' of ' + total + ' events';
    }

    document.querySelectorAll('.gold-ev-filter').forEach(function(btn){
        btn.addEventListener('click', function(){
            document.querySelectorAll('.gold-ev-filter').forEach(function(b){ b.classList.remove('active'); b.style.background = 'transparent'; b.style.color = 'var(--text)'; });
            this.classList.add('active'); this.style.background = '#FFD700'; this.style.color = '#000';
            applyGoldEventFilters();
        });
    });

    document.querySelectorAll('.gold-pl-filter').forEach(function(btn){
        btn.addEventListener('click', function(){
            document.querySelectorAll('.gold-pl-filter').forEach(function(b){
                b.classList.remove('active');
                b.style.background = 'transparent';
                var origColor = b.dataset.planet === 'all' ? 'var(--text)' : pC(b.dataset.planet);
                b.style.color = origColor;
            });
            this.classList.add('active');
            this.style.background = this.dataset.planet === 'all' ? '#FFD700' : pC(this.dataset.planet);
            this.style.color = '#000';
            applyGoldEventFilters();
        });
    });
}

/* ═══════════════════════════════════════════════════════════════
   DEITY ANALYSIS TAB — D3/D7/D9/D10/D12/D60 + Dasha-Deity Timeline
   ═══════════════════════════════════════════════════════════════ */

var deityDataCache = null;

var deityBtn = document.getElementById('deity-fetch');
if (deityBtn) {
    deityBtn.addEventListener('click', async function(){
        var resultDiv = document.getElementById('deity-result');
        var name  = document.getElementById('master-name').value;
        var date  = document.getElementById('master-date').value;
        var time  = document.getElementById('master-time').value;
        var place = document.getElementById('master-place').value;

        if (!date || !time) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Please enter birth date and time in the Master Birth Data panel above.</p>';
            return;
        }

        resultDiv.innerHTML = '<div class="loading" style="color:#9C27B0">Analyzing divisional deities across D3/D7/D9/D10/D12/D60...</div>';

        try {
            var resp = await fetch(API + '/deities', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: name,
                    date: ddmmToApi(date),
                    time: time,
                    place: place,
                    ayanamsa: 'lahiri'
                })
            });
            if (!resp.ok) {
                var errBody = await resp.json().catch(function(){ return {}; });
                throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
            }
            var data = await resp.json();
            deityDataCache = data;

            // Show sub-tabs
            var subTabsEl = document.getElementById('deity-sub-tabs');
            if (subTabsEl) subTabsEl.style.display = 'flex';

            renderDeityOverview(data);
        } catch(err) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
        }
    });
}

// Sub-tab switching
document.querySelectorAll('[data-deity-tab]').forEach(function(btn){
    btn.addEventListener('click', function(){
        document.querySelectorAll('[data-deity-tab]').forEach(function(b){
            b.classList.remove('active');
            b.style.background = 'transparent';
            b.style.color = 'var(--text)';
            b.style.borderColor = 'var(--border)';
        });
        this.classList.add('active');
        this.style.background = '#9C27B0';
        this.style.color = '#fff';
        this.style.borderColor = '#9C27B0';
        if (!deityDataCache) return;
        var tab = this.dataset.deityTab;
        if (tab === 'deity-overview') renderDeityOverview(deityDataCache);
        else if (tab === 'deity-d3')  renderDeityD3(deityDataCache);
        else if (tab === 'deity-d7')  renderDeityD7(deityDataCache);
        else if (tab === 'deity-d9')  renderDeityD9(deityDataCache);
        else if (tab === 'deity-d10') renderDeityD10(deityDataCache);
        else if (tab === 'deity-d12') renderDeityD12(deityDataCache);
        else if (tab === 'deity-d60') renderDeityD60(deityDataCache);
        else if (tab === 'deity-dasha') renderDashaDeityTimeline(deityDataCache);
    });
});

var dPurple = '#9C27B0';
var dPColors = {Sun:'#FFA500',Moon:'#C0C0C0',Mars:'#FF4444',Mercury:'#00CED1',Jupiter:'#FFD700',Venus:'#FF69B4',Saturn:'#4169E1',Rahu:'#8B008B',Ketu:'#808080',Ascendant:'#FF6F00'};
function dPC(n){ return dPColors[n]||'#ccc'; }
function natureBadge(nature) {
    if (!nature) return '';
    var c = nature === 'benefic' ? '#4CAF50' : nature === 'malefic' ? '#f44336' : '#FF9800';
    return '<span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.7rem;font-weight:700;background:'+c+'22;color:'+c+';border:1px solid '+c+'44">'+nature.toUpperCase()+'</span>';
}

/* ── OVERVIEW ─────────────────────────────────────────────────── */
function renderDeityOverview(data) {
    var resultDiv = document.getElementById('deity-result');
    var da = data.deity_analysis || {};
    var planets = da.planet_deities || [];
    var cur = data.current_dasha || {};
    var html = '';

    // Banner
    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid '+dPurple+';background:linear-gradient(135deg,rgba(156,39,176,0.08),transparent)">';
    html += '<div style="font-size:1.5rem;font-weight:800;color:'+dPurple+'">Divisional Deity Analysis</div>';
    html += '<div style="font-size:0.9rem;color:var(--text);margin-top:4px"><b>' + (data.name || '') + '</b></div>';
    if (data.input) {
        html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:2px">' + data.input.date + ' | ' + data.input.time + ' | ' + data.input.place + '</div>';
    }
    html += '</div>';

    // Current Dasha Deity Summary
    if (cur && cur.mahadasha) {
        var timeline = data.dasha_deity_timeline || [];
        var curMaha = timeline.find(function(t){ return t.mahadasha_lord === cur.mahadasha; });
        html += '<div class="card" style="margin-bottom:16px;border-left:4px solid '+dPurple+'">';
        html += '<div style="font-size:1.1rem;font-weight:700;color:'+dPurple+';margin-bottom:8px">Current Dasha Deity Rulers</div>';
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px">';

        html += '<div style="background:var(--card-bg);padding:10px;border-radius:8px;border:1px solid var(--border)">';
        html += '<div style="font-size:0.75rem;color:var(--text-dim)">Mahadasha</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:'+dPC(cur.mahadasha)+'">'+cur.mahadasha+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text-dim)">'+cur.mahadasha_start+' → '+cur.mahadasha_end+'</div>';
        html += '</div>';

        if (cur.antardasha) {
            html += '<div style="background:var(--card-bg);padding:10px;border-radius:8px;border:1px solid var(--border)">';
            html += '<div style="font-size:0.75rem;color:var(--text-dim)">Antardasha</div>';
            html += '<div style="font-size:1.1rem;font-weight:700;color:'+dPC(cur.antardasha)+'">'+cur.antardasha+'</div>';
            html += '<div style="font-size:0.8rem;color:var(--text-dim)">'+cur.antardasha_start+' → '+cur.antardasha_end+'</div>';
            html += '</div>';
        }
        if (curMaha) {
            html += '<div style="background:var(--card-bg);padding:10px;border-radius:8px;border:1px solid var(--border)">';
            html += '<div style="font-size:0.75rem;color:var(--text-dim)">D10 Career Deity</div>';
            html += '<div style="font-size:1.1rem;font-weight:700;color:#FF9800">'+curMaha.d10_deity+'</div>';
            html += '<div style="font-size:0.75rem;color:var(--text-dim)">'+curMaha.d10_domain+'</div>';
            html += '</div>';

            html += '<div style="background:var(--card-bg);padding:10px;border-radius:8px;border:1px solid var(--border)">';
            html += '<div style="font-size:0.75rem;color:var(--text-dim)">D60 Karma Deity</div>';
            html += '<div style="font-size:1.1rem;font-weight:700;color:#E91E63">'+curMaha.d60_deity+'</div>';
            html += '<div style="font-size:0.75rem;color:var(--text-dim)">'+curMaha.d60_karma.substring(0,80)+'...</div>';
            html += '</div>';

            html += '<div style="background:var(--card-bg);padding:10px;border-radius:8px;border:1px solid var(--border)">';
            html += '<div style="font-size:0.75rem;color:var(--text-dim)">D9 Fortune Deity</div>';
            html += '<div style="font-size:1.1rem;font-weight:700;color:#00BCD4">'+curMaha.d9_deity+'</div>';
            html += '<div style="font-size:0.75rem;color:var(--text-dim)">'+curMaha.d9_fortune.substring(0,80)+'...</div>';
            html += '</div>';
        }
        html += '</div>';

        // Current dasha combined interpretation
        if (curMaha && curMaha.interpretation) {
            var ci = curMaha.interpretation;
            html += '<div style="margin-top:12px;padding:14px;background:linear-gradient(135deg,rgba(156,39,176,0.06),rgba(255,152,0,0.04));border-radius:10px;border:1px solid '+dPurple+'44">';
            html += '<div style="font-size:1rem;font-weight:700;color:'+dPurple+';margin-bottom:10px">Your Current Dasha-Deity Reading</div>';

            html += '<div style="margin-bottom:10px">';
            html += '<div style="font-size:0.82rem;font-weight:700;color:#FF9800;margin-bottom:4px">Career Path ('+cur.mahadasha+' × D10 '+curMaha.d10_deity+')</div>';
            html += '<div style="font-size:0.85rem;color:var(--text);line-height:1.5">'+ci.career_interpretation+'</div>';
            html += '</div>';

            html += '<div style="margin-bottom:10px">';
            html += '<div style="font-size:0.82rem;font-weight:700;color:#F44336;margin-bottom:4px">Karmic Pattern ('+cur.mahadasha+' × D60 '+curMaha.d60_deity+')</div>';
            html += '<div style="font-size:0.85rem;color:var(--text);line-height:1.5">'+ci.karma_interpretation+'</div>';
            html += '</div>';

            html += '<div style="margin-bottom:10px">';
            html += '<div style="font-size:0.82rem;font-weight:700;color:#00BCD4;margin-bottom:4px">Fortune Flow ('+cur.mahadasha+' × D9 '+curMaha.d9_deity+')</div>';
            html += '<div style="font-size:0.85rem;color:var(--text);line-height:1.5">'+ci.fortune_interpretation+'</div>';
            html += '</div>';

            if (ci.practical_advice) {
                html += '<div style="padding:10px;background:'+dPurple+'11;border-radius:8px;border-left:4px solid '+dPurple+'">';
                html += '<div style="font-size:0.82rem;font-weight:700;color:'+dPurple+';margin-bottom:4px">Practical Advice</div>';
                html += '<div style="font-size:0.85rem;color:var(--text);line-height:1.5">'+ci.practical_advice+'</div>';
                html += '</div>';
            }

            html += '</div>';
        }

        html += '</div>';
    }

    // Planet Deity Summary Table
    html += '<div class="card" style="margin-bottom:16px">';
    html += '<div style="font-size:1.1rem;font-weight:700;color:'+dPurple+';margin-bottom:10px">Planet-Deity Matrix</div>';
    html += '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:0.8rem">';
    html += '<thead><tr style="background:'+dPurple+'22">';
    html += '<th style="padding:8px;text-align:left;border-bottom:2px solid '+dPurple+'">Planet</th>';
    html += '<th style="padding:8px;text-align:left;border-bottom:2px solid '+dPurple+'">D3</th>';
    html += '<th style="padding:8px;text-align:left;border-bottom:2px solid '+dPurple+'">D7</th>';
    html += '<th style="padding:8px;text-align:left;border-bottom:2px solid '+dPurple+'">D9</th>';
    html += '<th style="padding:8px;text-align:left;border-bottom:2px solid '+dPurple+'">D10</th>';
    html += '<th style="padding:8px;text-align:left;border-bottom:2px solid '+dPurple+'">D12</th>';
    html += '<th style="padding:8px;text-align:left;border-bottom:2px solid '+dPurple+'">D60</th>';
    html += '</tr></thead><tbody>';

    planets.forEach(function(p){
        html += '<tr style="border-bottom:1px solid var(--border)">';
        html += '<td style="padding:6px 8px;font-weight:700;color:'+dPC(p.planet)+'">'+p.planet+'</td>';
        html += '<td style="padding:6px 8px">'+(p.d3.deity||'-')+'</td>';
        html += '<td style="padding:6px 8px">'+(p.d7.deity||'-')+'</td>';
        html += '<td style="padding:6px 8px">'+(p.d9.deity||'-')+'</td>';
        html += '<td style="padding:6px 8px">'+(p.d10.deity||'-')+'</td>';
        html += '<td style="padding:6px 8px">'+(p.d12.deity||'-')+'</td>';
        html += '<td style="padding:6px 8px">'+(p.d60.deity||'-')+'</td>';
        html += '</tr>';
    });

    html += '</tbody></table></div></div>';

    resultDiv.innerHTML = html;
}

/* ── D3 DREKKANA ──────────────────────────────────────────────── */
function renderDeityD3(data) {
    var resultDiv = document.getElementById('deity-result');
    var planets = (data.deity_analysis || {}).planet_deities || [];
    var html = '';

    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid #FF5722">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:#FF5722">D3 Drekkana — 36 Deities of Courage & Siblings</div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Each sign divided into 3 parts (10° each) — reveals innate courage, co-born & life pattern</div>';
    html += '</div>';

    planets.forEach(function(p){
        var d = p.d3;
        if (!d.deity) return;
        html += '<div class="card" style="margin-bottom:10px;border-left:4px solid '+dPC(p.planet)+'">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">';
        html += '<div><span style="font-size:1rem;font-weight:700;color:'+dPC(p.planet)+'">'+p.planet+'</span>';
        html += ' <span style="font-size:0.8rem;color:var(--text-dim)">('+p.d1_sign+' '+p.longitude.toFixed(2)+'°)</span></div>';
        html += natureBadge(d.nature);
        html += '</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:#FF5722;margin-bottom:4px">'+d.deity+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:4px"><b>Domain:</b> '+d.domain+'</div>';
        html += '<div style="font-size:0.85rem;color:var(--text)">'+d.result+'</div>';
        html += '</div>';
    });

    resultDiv.innerHTML = html;
}

/* ── D7 SAPTAMSHA ─────────────────────────────────────────────── */
function renderDeityD7(data) {
    var resultDiv = document.getElementById('deity-result');
    var planets = (data.deity_analysis || {}).planet_deities || [];
    var html = '';

    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid #E91E63">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:#E91E63">D7 Saptamsha — 7 Matrikas (Divine Mothers)</div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Each sign divided into 7 parts (4°17\' each) — reveals children, creative power & progeny</div>';
    html += '</div>';

    planets.forEach(function(p){
        var d = p.d7;
        if (!d.deity) return;
        html += '<div class="card" style="margin-bottom:10px;border-left:4px solid '+dPC(p.planet)+'">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">';
        html += '<div><span style="font-size:1rem;font-weight:700;color:'+dPC(p.planet)+'">'+p.planet+'</span>';
        html += ' <span style="font-size:0.8rem;color:var(--text-dim)">('+p.d1_sign+')</span></div>';
        html += natureBadge(d.nature);
        html += '</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:#E91E63;margin-bottom:4px">'+d.deity+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:4px"><b>Domain:</b> '+d.domain+'</div>';
        html += '<div style="font-size:0.85rem;color:var(--text)">'+d.result+'</div>';
        html += '</div>';
    });

    resultDiv.innerHTML = html;
}

/* ── D9 NAVAMSHA ──────────────────────────────────────────────── */
function renderDeityD9(data) {
    var resultDiv = document.getElementById('deity-result');
    var planets = (data.deity_analysis || {}).planet_deities || [];
    var html = '';

    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid #00BCD4">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:#00BCD4">D9 Navamsha — 12 Fortune Deities</div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">9-fold division (3°20\' each) — dharma path, fortune, spouse & spiritual destiny</div>';
    html += '</div>';

    planets.forEach(function(p){
        var d = p.d9;
        if (!d.deity) return;
        html += '<div class="card" style="margin-bottom:10px;border-left:4px solid '+dPC(p.planet)+'">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">';
        html += '<div><span style="font-size:1rem;font-weight:700;color:'+dPC(p.planet)+'">'+p.planet+'</span>';
        html += ' <span style="font-size:0.8rem;color:var(--text-dim)">('+p.d1_sign+' → D9: '+d.sign+')</span></div>';
        html += natureBadge(d.nature);
        html += '</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:#00BCD4;margin-bottom:4px">'+d.deity+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text);margin-bottom:3px"><b style="color:#00BCD4">Fortune:</b> '+d.fortune+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text);margin-bottom:3px"><b style="color:#00BCD4">Dharma:</b> '+d.dharma+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text)"><b style="color:#00BCD4">Marriage:</b> '+d.marriage+'</div>';
        html += '</div>';
    });

    resultDiv.innerHTML = html;
}

/* ── D10 DASHAMSHA ────────────────────────────────────────────── */
function renderDeityD10(data) {
    var resultDiv = document.getElementById('deity-result');
    var planets = (data.deity_analysis || {}).planet_deities || [];
    var html = '';

    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid #FF9800">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:#FF9800">D10 Dashamsha — 10 Career Deities</div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Each sign divided into 10 parts (3° each) — career path, professional destiny & public standing</div>';
    html += '</div>';

    planets.forEach(function(p){
        var d = p.d10;
        if (!d.deity) return;
        html += '<div class="card" style="margin-bottom:10px;border-left:4px solid '+dPC(p.planet)+'">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">';
        html += '<div><span style="font-size:1rem;font-weight:700;color:'+dPC(p.planet)+'">'+p.planet+'</span>';
        html += ' <span style="font-size:0.8rem;color:var(--text-dim)">('+p.d1_sign+')</span></div>';
        html += natureBadge(d.nature);
        html += '</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:#FF9800;margin-bottom:4px">'+d.deity+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:4px"><b>Domain:</b> '+d.domain+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text);margin-bottom:3px"><b style="color:#FF9800">Career:</b> '+d.career+'</div>';
        html += '<div style="font-size:0.85rem;color:var(--text)"><b style="color:#FF9800">Result:</b> '+d.result+'</div>';
        html += '</div>';
    });

    resultDiv.innerHTML = html;
}

/* ── D12 DWADASHAMSHA ─────────────────────────────────────────── */
function renderDeityD12(data) {
    var resultDiv = document.getElementById('deity-result');
    var planets = (data.deity_analysis || {}).planet_deities || [];
    var html = '';

    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid #8BC34A">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:#8BC34A">D12 Dwadashamsha — 12 Adityas (Solar Deities)</div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Each sign divided into 12 parts (2°30\' each) — parents, lineage & ancestral karma</div>';
    html += '</div>';

    planets.forEach(function(p){
        var d = p.d12;
        if (!d.deity) return;
        html += '<div class="card" style="margin-bottom:10px;border-left:4px solid '+dPC(p.planet)+'">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">';
        html += '<div><span style="font-size:1rem;font-weight:700;color:'+dPC(p.planet)+'">'+p.planet+'</span>';
        html += ' <span style="font-size:0.8rem;color:var(--text-dim)">('+p.d1_sign+')</span></div>';
        html += natureBadge(d.nature);
        html += '</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:#8BC34A;margin-bottom:4px">'+d.deity+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:4px"><b>Domain:</b> '+d.domain+'</div>';
        html += '<div style="font-size:0.85rem;color:var(--text)">'+d.result+'</div>';
        html += '</div>';
    });

    resultDiv.innerHTML = html;
}

/* ── D60 SHASHTIAMSHA ─────────────────────────────────────────── */
function renderDeityD60(data) {
    var resultDiv = document.getElementById('deity-result');
    var planets = (data.deity_analysis || {}).planet_deities || [];
    var html = '';

    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid #F44336">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:#F44336">D60 Shashtiamsha — 60 Karmic Deities</div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Each sign divided into 60 parts (0°30\' each) — deep past-life karma, fortune & final destiny</div>';
    html += '</div>';

    planets.forEach(function(p){
        var d = p.d60;
        if (!d.deity) return;
        html += '<div class="card" style="margin-bottom:10px;border-left:4px solid '+dPC(p.planet)+'">';
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">';
        html += '<div><span style="font-size:1rem;font-weight:700;color:'+dPC(p.planet)+'">'+p.planet+'</span>';
        html += ' <span style="font-size:0.8rem;color:var(--text-dim)">('+p.d1_sign+' '+p.longitude.toFixed(2)+'°)</span></div>';
        html += natureBadge(d.nature);
        html += '</div>';
        html += '<div style="font-size:1.1rem;font-weight:700;color:#F44336;margin-bottom:4px">'+d.deity+'</div>';
        html += '<div style="font-size:0.8rem;color:var(--text);margin-bottom:3px"><b style="color:#F44336">Karma:</b> '+d.karma+'</div>';
        html += '<div style="font-size:0.85rem;color:var(--text)"><b style="color:#F44336">Fortune:</b> '+d.fortune+'</div>';
        html += '</div>';
    });

    resultDiv.innerHTML = html;
}

/* ── DASHA-DEITY TIMELINE ─────────────────────────────────────── */
function renderDashaDeityTimeline(data) {
    var resultDiv = document.getElementById('deity-result');
    var timeline = data.dasha_deity_timeline || [];
    var cur = data.current_dasha || {};
    var html = '';

    html += '<div class="card" style="text-align:center;margin-bottom:16px;border:2px solid '+dPurple+'">';
    html += '<div style="font-size:1.3rem;font-weight:800;color:'+dPurple+'">Dasha-Deity Timeline</div>';
    html += '<div style="font-size:0.8rem;color:var(--text-dim);margin-top:4px">Each Mahadasha mapped to D9 Fortune, D10 Career & D60 Karma deities with antardasha breakdown</div>';
    html += '</div>';

    timeline.forEach(function(maha){
        var isCurrent = (cur.mahadasha === maha.mahadasha_lord);
        var borderColor = isCurrent ? '#FFD700' : dPC(maha.mahadasha_lord);
        var bgExtra = isCurrent ? ';background:linear-gradient(135deg,rgba(255,215,0,0.06),transparent)' : '';

        html += '<div class="card" style="margin-bottom:14px;border-left:5px solid '+borderColor+bgExtra+'">';

        // Header
        html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">';
        html += '<div>';
        html += '<span style="font-size:1.15rem;font-weight:800;color:'+dPC(maha.mahadasha_lord)+'">'+maha.mahadasha_lord+' Mahadasha</span>';
        if (isCurrent) html += ' <span style="background:#FFD700;color:#000;padding:2px 8px;border-radius:10px;font-size:0.7rem;font-weight:700">ACTIVE</span>';
        html += '</div>';
        html += '<div style="font-size:0.8rem;color:var(--text-dim)">'+maha.start_date+' → '+maha.end_date+' ('+maha.duration_years.toFixed(1)+' yrs)</div>';
        html += '</div>';

        // Deity cards row
        html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin-bottom:10px">';

        // D9
        html += '<div style="background:var(--bg);padding:10px;border-radius:8px;border:1px solid #00BCD422">';
        html += '<div style="font-size:0.7rem;color:#00BCD4;font-weight:700">D9 FORTUNE</div>';
        html += '<div style="font-size:1rem;font-weight:700;color:#00BCD4">'+maha.d9_deity+'</div>';
        html += '<div style="font-size:0.75rem;color:var(--text);margin-top:4px">'+maha.d9_fortune+'</div>';
        if (maha.d9_dharma) html += '<div style="font-size:0.75rem;color:var(--text-dim);margin-top:2px"><i>Dharma: '+maha.d9_dharma+'</i></div>';
        html += '</div>';

        // D10
        html += '<div style="background:var(--bg);padding:10px;border-radius:8px;border:1px solid #FF980022">';
        html += '<div style="font-size:0.7rem;color:#FF9800;font-weight:700">D10 CAREER</div>';
        html += '<div style="font-size:1rem;font-weight:700;color:#FF9800">'+maha.d10_deity+'</div>';
        html += '<div style="font-size:0.75rem;color:var(--text-dim)">'+maha.d10_domain+'</div>';
        html += '<div style="font-size:0.75rem;color:var(--text);margin-top:4px">'+maha.d10_career+'</div>';
        html += '</div>';

        // D60
        html += '<div style="background:var(--bg);padding:10px;border-radius:8px;border:1px solid #F4433622">';
        html += '<div style="font-size:0.7rem;color:#F44336;font-weight:700">D60 KARMA</div>';
        html += '<div style="font-size:1rem;font-weight:700;color:#F44336">'+maha.d60_deity+'</div>';
        html += '<div style="font-size:0.75rem;color:var(--text);margin-top:4px">'+maha.d60_karma+'</div>';
        html += '<div style="font-size:0.75rem;color:var(--text-dim);margin-top:2px"><i>Fortune: '+maha.d60_fortune+'</i></div>';
        html += '</div>';

        html += '</div>';

        // ── COMBINED INTERPRETATION SECTION ──
        var interp = maha.interpretation || {};
        if (interp.career_interpretation) {
            html += '<div style="margin:10px 0;padding:12px;background:linear-gradient(135deg,rgba(156,39,176,0.04),rgba(255,152,0,0.04));border-radius:8px;border:1px solid '+dPurple+'33">';
            html += '<div style="font-size:0.85rem;font-weight:700;color:'+dPurple+';margin-bottom:8px">Combined Interpretation — '+maha.mahadasha_lord+' Dasha × Deities</div>';

            html += '<div style="margin-bottom:8px">';
            html += '<div style="font-size:0.75rem;font-weight:700;color:#FF9800;margin-bottom:3px">Career Reading ('+maha.mahadasha_lord+' + D10 '+maha.d10_deity+')</div>';
            html += '<div style="font-size:0.8rem;color:var(--text)">'+interp.career_interpretation+'</div>';
            html += '</div>';

            html += '<div style="margin-bottom:8px">';
            html += '<div style="font-size:0.75rem;font-weight:700;color:#F44336;margin-bottom:3px">Karmic Reading ('+maha.mahadasha_lord+' + D60 '+maha.d60_deity+')</div>';
            html += '<div style="font-size:0.8rem;color:var(--text)">'+interp.karma_interpretation+'</div>';
            html += '</div>';

            html += '<div style="margin-bottom:8px">';
            html += '<div style="font-size:0.75rem;font-weight:700;color:#00BCD4;margin-bottom:3px">Fortune Reading ('+maha.mahadasha_lord+' + D9 '+maha.d9_deity+')</div>';
            html += '<div style="font-size:0.8rem;color:var(--text)">'+interp.fortune_interpretation+'</div>';
            html += '</div>';

            if (interp.practical_advice) {
                html += '<div style="padding:8px;background:'+dPurple+'11;border-radius:6px;border-left:3px solid '+dPurple+'">';
                html += '<div style="font-size:0.75rem;font-weight:700;color:'+dPurple+';margin-bottom:3px">Practical Advice</div>';
                html += '<div style="font-size:0.8rem;color:var(--text)">'+interp.practical_advice+'</div>';
                html += '</div>';
            }

            html += '</div>';
        }

        // Antardasha collapsible
        if (maha.antardashas && maha.antardashas.length > 0) {
            var toggleId = 'antar-toggle-' + maha.mahadasha_lord;
            html += '<details style="margin-top:6px">';
            html += '<summary style="cursor:pointer;color:'+dPurple+';font-size:0.85rem;font-weight:600">View Antardasha Deity Breakdown ('+maha.antardashas.length+' periods)</summary>';
            html += '<div style="margin-top:8px">';

            maha.antardashas.forEach(function(a){
                var isActive = cur.antardasha === a.antardasha_lord && isCurrent;
                var aBorder = isActive ? '#FFD700' : dPC(a.antardasha_lord);
                var aBg = isActive ? ';background:linear-gradient(135deg,rgba(255,215,0,0.06),transparent)' : '';

                html += '<div style="margin-bottom:8px;padding:10px;border-left:3px solid '+aBorder+';border-radius:6px;background:var(--bg)'+aBg+'">';

                html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">';
                html += '<div><span style="font-weight:700;color:'+dPC(a.antardasha_lord)+'">'+maha.mahadasha_lord+' / '+a.antardasha_lord+'</span>';
                if (isActive) html += ' <span style="background:#FFD700;color:#000;padding:1px 6px;border-radius:8px;font-size:0.65rem;font-weight:700">NOW</span>';
                html += '</div>';
                html += '<span style="font-size:0.72rem;color:var(--text-dim)">'+a.start_date+' → '+a.end_date+'</span>';
                html += '</div>';

                html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:6px">';
                html += '<div style="font-size:0.75rem"><span style="color:#FF9800;font-weight:600">D10: '+a.d10_deity+'</span> — '+a.d10_career.substring(0,80)+'</div>';
                html += '<div style="font-size:0.75rem"><span style="color:#F44336;font-weight:600">D60: '+a.d60_deity+'</span> — '+a.d60_karma.substring(0,80)+'</div>';
                html += '</div>';

                if (a.interpretation) {
                    html += '<div style="font-size:0.78rem;color:var(--text);padding:6px;background:'+dPurple+'08;border-radius:4px">';
                    html += '<b style="color:'+dPurple+'">Reading:</b> '+a.interpretation;
                    html += '</div>';
                }

                html += '</div>';
            });

            html += '</div></details>';
        }

        html += '</div>';
    });

    resultDiv.innerHTML = html;
}


// ═══════════════════════════════════════════════════════════════
// ASTROLOGICAL EVENTS — Fetch + Render all 9 event types
// ═══════════════════════════════════════════════════════════════

var astroEvtBtn = document.getElementById('astro-evt-fetch');
if (astroEvtBtn) {
    astroEvtBtn.addEventListener('click', async function(){
        var resultDiv = document.getElementById('astro-evt-result');
        var startDate = document.getElementById('astro-evt-start').value;
        var endDate = document.getElementById('astro-evt-end').value;
        var ayanamsa = document.getElementById('astro-evt-ayanamsa').value;

        if (!startDate || !endDate) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Please select both start and end dates</p>';
            return;
        }

        resultDiv.innerHTML = '<p style="color:#FF6F00;font-weight:600">Calculating all 9 astrological event types... This may take a moment.</p>';

        var payload = {
            start_date: startDate,
            end_date: endDate,
            ayanamsa: ayanamsa,
            timezone_offset_minutes: 330
        };

        try {
            var resp = await fetch(API + '/astro-events', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            if (!resp.ok) {
                var errBody = await resp.json().catch(function(){ return {}; });
                throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
            }
            var data = await resp.json();
            renderAstroEvents(data, resultDiv);
        } catch(err) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
        }
    });
}

// ── Color palette for event sections ─────────────────────────
var EVT_COLORS = {
    combustion: '#F44336',
    retrograde: '#9C27B0',
    transits: '#2196F3',
    positions: '#009688',
    mutual_aspects: '#FF9800',
    lunar_aspects: '#3F51B5',
    mutual_parallel: '#795548',
    ecliptic_crossings: '#607D8B',
    graha_yuddha: '#E91E63'
};

var EVT_ICONS = {
    combustion: '🔥',
    retrograde: '↺',
    transits: '→',
    positions: '📍',
    mutual_aspects: '⚔',
    lunar_aspects: '🌙',
    mutual_parallel: '∥',
    ecliptic_crossings: '✕',
    graha_yuddha: '⚔'
};

var EVT_TITLES = {
    combustion: 'Planets Combustion',
    retrograde: 'Planets Retrograde',
    transits: 'Planets Transit (Sign Ingress)',
    positions: 'Planetary Positions',
    mutual_aspects: 'Planets Mutual Aspects',
    lunar_aspects: 'Lunar Aspects',
    mutual_parallel: 'Planets Mutual Parallel',
    ecliptic_crossings: 'Ecliptic Crossings',
    graha_yuddha: 'Graha Yuddha (Planetary War)'
};

function renderAstroEvents(data, resultDiv) {
    var html = '';
    html += '<div style="background:var(--card-bg);border-radius:10px;padding:14px;margin-bottom:12px;border-left:4px solid #FF6F00">';
    html += '<h3 style="color:#FF6F00;margin:0 0 6px 0">Astrological Events Summary</h3>';
    html += '<div style="display:flex;flex-wrap:wrap;gap:8px;font-size:0.85rem;color:var(--text-dim)">';
    html += '<span><b>Period:</b> ' + data.start_date + ' to ' + data.end_date + '</span>';
    html += '<span><b>Days:</b> ' + data.total_days + '</span>';
    html += '<span><b>Ayanamsa:</b> ' + data.ayanamsa + '</span>';
    html += '</div></div>';

    // Render each of the 9 sections
    var sections = ['combustion','retrograde','transits','positions','mutual_aspects','lunar_aspects','mutual_parallel','ecliptic_crossings','graha_yuddha'];
    sections.forEach(function(key) {
        var events = data[key];
        var color = EVT_COLORS[key];
        var icon = EVT_ICONS[key];
        var title = EVT_TITLES[key];
        var count = Array.isArray(events) ? events.length : 0;

        html += '<div style="background:var(--card-bg);border-radius:10px;padding:14px;margin-bottom:14px;border-left:4px solid '+color+'">';
        html += '<h3 style="color:'+color+';margin:0 0 10px 0;cursor:pointer" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===\'none\'?\'block\':\'none\'">';
        html += icon + ' ' + title + ' <span style="font-size:0.8rem;background:'+color+'22;color:'+color+';padding:2px 8px;border-radius:10px;margin-left:6px">' + count + ' events</span>';
        html += ' <span style="font-size:0.7rem;color:var(--text-dim)">click to toggle</span></h3>';
        html += '<div>';

        if (count === 0) {
            html += '<p style="color:var(--text-dim);font-style:italic;margin:4px 0">No events found in this period</p>';
        } else {
            switch(key) {
                case 'combustion': html += renderEvtCombustion(events, color); break;
                case 'retrograde': html += renderEvtRetrograde(events, color); break;
                case 'transits': html += renderEvtTransits(events, color); break;
                case 'positions': html += renderEvtPositions(events, color); break;
                case 'mutual_aspects': html += renderEvtMutualAspects(events, color); break;
                case 'lunar_aspects': html += renderEvtLunarAspects(events, color); break;
                case 'mutual_parallel': html += renderEvtMutualParallel(events, color); break;
                case 'ecliptic_crossings': html += renderEvtEclipticCrossings(events, color); break;
                case 'graha_yuddha': html += renderEvtGrahaYuddha(events, color); break;
            }
        }

        html += '</div></div>';
    });

    resultDiv.innerHTML = html;
}

// ── Helper: table wrapper ────────────────────────────────────
function evtTable(headers, rows, color) {
    var h = '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:0.82rem">';
    h += '<thead><tr>';
    headers.forEach(function(hdr) {
        h += '<th style="background:'+color+'15;color:'+color+';padding:6px 8px;text-align:left;border-bottom:2px solid '+color+'33;white-space:nowrap">'+hdr+'</th>';
    });
    h += '</tr></thead><tbody>';
    rows.forEach(function(row, i) {
        var bg = i % 2 === 0 ? 'transparent' : 'var(--card-bg)';
        h += '<tr style="background:'+bg+'">';
        row.forEach(function(cell) {
            h += '<td style="padding:5px 8px;border-bottom:1px solid var(--border,#333)">'+(cell||'')+'</td>';
        });
        h += '</tr>';
    });
    h += '</tbody></table></div>';
    return h;
}

// ── 1. Combustion ────────────────────────────────────────────
function renderEvtCombustion(events, color) {
    var rows = events.map(function(e) {
        return [
            '<b style="color:'+color+'">'+e.planet+'</b>',
            e.date || '',
            e.event || e.status || '',
            e.distance_from_sun != null ? e.distance_from_sun.toFixed(2)+'°' : '',
            e.combustion_orb ? e.combustion_orb+'°' : '',
            e.planet_sign || '',
            e.planet_longitude != null ? e.planet_longitude.toFixed(2)+'°' : ''
        ];
    });
    return evtTable(['Planet','Date','Event','Dist from Sun','Orb','Sign','Longitude'], rows, color);
}

// ── 2. Retrograde ────────────────────────────────────────────
function renderEvtRetrograde(events, color) {
    var rows = events.map(function(e) {
        return [
            '<b style="color:'+color+'">'+(e.planet||'')+'</b>',
            e.date || '',
            '<span style="color:'+(e.event==='retrograde_start'?'#F44336':'#4CAF50')+';font-weight:600">'+(e.event==='retrograde_start'?'Retrograde ↺':'Direct →')+'</span>',
            e.sign || '',
            e.longitude != null ? e.longitude.toFixed(2)+'°' : ''
        ];
    });
    return evtTable(['Planet','Date','Event','Sign','Longitude'], rows, color);
}

// ── 3. Transits (Sign Ingress) ───────────────────────────────
function renderEvtTransits(events, color) {
    var rows = events.map(function(e) {
        return [
            '<b style="color:'+color+'">'+(e.planet||'')+'</b>',
            e.date || '',
            e.from_sign ? e.from_sign+' → <b>'+e.to_sign+'</b>' : (e.to_sign || e.sign || ''),
            e.longitude != null ? e.longitude.toFixed(2)+'°' : ''
        ];
    });
    return evtTable(['Planet','Date','Transit','Longitude'], rows, color);
}

// ── 4. Positions ─────────────────────────────────────────────
function renderEvtPositions(events, color) {
    // Group by date
    var byDate = {};
    events.forEach(function(e) {
        var d = e.date || 'unknown';
        if (!byDate[d]) byDate[d] = [];
        byDate[d].push(e);
    });

    var h = '';
    var dates = Object.keys(byDate);
    dates.forEach(function(date, di) {
        var planets = byDate[date];
        h += '<details'+(di===0?' open':'')+' style="margin-bottom:8px">';
        h += '<summary style="font-weight:600;color:'+color+';cursor:pointer;font-size:0.85rem;padding:4px 0">'+date+' ('+planets.length+' planets)</summary>';
        var rows = planets.map(function(p) {
            return [
                '<b>'+p.planet+'</b>',
                p.sign || '',
                p.longitude != null ? p.longitude.toFixed(2)+'°' : '',
                p.nakshatra || '',
                p.retrograde ? '<span style="color:#F44336;font-weight:700">R</span>' : ''
            ];
        });
        h += evtTable(['Planet','Sign','Longitude','Nakshatra','Retro'], rows, color);
        h += '</details>';
    });
    return h;
}

// ── 5. Mutual Aspects ────────────────────────────────────────
function renderEvtMutualAspects(events, color) {
    var rows = events.map(function(e) {
        return [
            e.date || '',
            '<b style="color:'+color+'">'+(e.planet1||'')+'</b>',
            e.aspect_type || e.aspect || '',
            '<b style="color:'+color+'">'+(e.planet2||'')+'</b>',
            e.angle != null ? e.angle.toFixed(1)+'°' : '',
            e.sign1 || '',
            e.sign2 || ''
        ];
    });
    return evtTable(['Date','Planet 1','Aspect','Planet 2','Angle','Sign 1','Sign 2'], rows, color);
}

// ── 6. Lunar Aspects ─────────────────────────────────────────
function renderEvtLunarAspects(events, color) {
    var rows = events.map(function(e) {
        return [
            e.date || '',
            '<b style="color:'+color+'">Moon</b>',
            e.aspect_type || e.aspect || '',
            '<b>'+(e.planet||'')+'</b>',
            e.angle != null ? e.angle.toFixed(1)+'°' : '',
            e.moon_sign || '',
            e.planet_sign || ''
        ];
    });
    return evtTable(['Date','Moon','Aspect','Planet','Angle','Moon Sign','Planet Sign'], rows, color);
}

// ── 7. Mutual Parallel ──────────────────────────────────────
function renderEvtMutualParallel(events, color) {
    var rows = events.map(function(e) {
        return [
            e.date || '',
            '<b style="color:'+color+'">'+(e.planet1||'')+'</b>',
            '<b style="color:'+color+'">'+(e.planet2||'')+'</b>',
            e.type || e.parallel_type || '',
            e.declination1 != null ? e.declination1.toFixed(2)+'°' : '',
            e.declination2 != null ? e.declination2.toFixed(2)+'°' : ''
        ];
    });
    return evtTable(['Date','Planet 1','Planet 2','Type','Decl. 1','Decl. 2'], rows, color);
}

// ── 8. Ecliptic Crossings ────────────────────────────────────
function renderEvtEclipticCrossings(events, color) {
    var rows = events.map(function(e) {
        return [
            e.date || '',
            '<b style="color:'+color+'">'+(e.planet||'')+'</b>',
            e.direction || '',
            e.sign || '',
            e.longitude != null ? e.longitude.toFixed(2)+'°' : ''
        ];
    });
    return evtTable(['Date','Planet','Direction','Sign','Longitude'], rows, color);
}

// ── 9. Graha Yuddha ─────────────────────────────────────────
function renderEvtGrahaYuddha(events, color) {
    var rows = events.map(function(e) {
        return [
            e.date || '',
            '<b style="color:'+color+'">'+(e.planet1||'')+'</b>',
            'vs',
            '<b style="color:'+color+'">'+(e.planet2||'')+'</b>',
            e.separation != null ? e.separation.toFixed(2)+'°' : '',
            e.winner ? '<span style="color:#4CAF50;font-weight:700">'+e.winner+'</span>' : '',
            e.sign || ''
        ];
    });
    return evtTable(['Date','Planet 1','','Planet 2','Separation','Winner','Sign'], rows, color);
}


// ═══════════════════════════════════════════════════════════════
// NUMEROLOGY — Fetch + Render
// ═══════════════════════════════════════════════════════════════

var numBtn = document.getElementById('num-fetch');
if (numBtn) {
    numBtn.addEventListener('click', async function(){
        var resultDiv = document.getElementById('num-result');
        var nameEl = document.getElementById('num-name');
        var dobEl = document.getElementById('num-dob');
        var mobileEl = document.getElementById('num-mobile');
        var carEl = document.getElementById('num-car');
        var passEl = document.getElementById('num-password');

        // Auto-fill from master birth data if empty
        var name = nameEl.value.trim();
        var dob = dobEl.value.trim();
        if (!name) {
            var masterName = document.querySelector('.birth-name');
            if (masterName && masterName !== nameEl) name = masterName.value.trim();
            if (name) nameEl.value = name;
        }
        if (!dob) {
            var masterDob = document.querySelector('#master-birth-panel .birth-date');
            if (masterDob && masterDob !== dobEl) dob = masterDob.value.trim();
            if (dob) dobEl.value = dob;
        }

        if (!name || !dob) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Please enter Name and DOB</p>';
            return;
        }

        resultDiv.innerHTML = '<p style="color:#E65100;font-weight:600">Calculating numerology...</p>';

        var payload = { name: name, dob: dob, system: "both" };
        if (mobileEl.value.trim()) payload.mobile = mobileEl.value.trim();
        if (carEl.value.trim()) payload.car_number = carEl.value.trim();
        if (passEl.value.trim()) payload.password = passEl.value.trim();

        try {
            var resp = await fetch(API + '/numerology', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            if (!resp.ok) {
                var errBody = await resp.json().catch(function(){ return {}; });
                throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
            }
            var data = await resp.json();
            renderNumerology(data, resultDiv);
        } catch(err) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
        }
    });
}

var NC = '#E65100'; // Numerology color

function renderNumerology(data, resultDiv) {
    var html = '';

    // ── 1. Core Numbers Summary ──────────────────────────
    html += numSection('Core Numbers', '🔢', renderCoreNumbers(data));

    // ── 2. Date Addition Analysis ────────────────────────
    html += numSection('Date Addition Analysis', '📅', renderDateAddition(data));

    // ── 3. Name Analysis (Pythagorean + Chaldean) ────────
    html += numSection('Name Analysis', '✍', renderNameAnalysis(data));

    // ── 4. Loshu Grid ────────────────────────────────────
    html += numSection('Loshu Grid (Lo Shu Magic Square)', '⊞', renderLoshuGrid(data));

    // ── 5. Raj Yogas (Golden / Silver / All) ─────────────
    html += numSection('Raj Yogas — Golden, Silver & Numerological Yogas', '👑', renderRajYogas(data));

    // ── 6. Personality & Characteristics ─────────────────
    html += numSection('Personality & Characteristics', '👤', renderCharacteristics(data));

    // ── 7. Yearly Predictions (15-Year Forecast) ─────────
    html += numSection('Yearly Predictions — Loshu Grid Forecast', '📊', renderYearlyPredictions(data));

    // ── 8. Name Correction ───────────────────────────────
    html += numSection('Name Correction', '✏', renderNameCorrection(data));

    // ── 9. Mobile Number Analysis ────────────────────────
    if (data.mobile_analysis) {
        html += numSection('Mobile Number Analysis', '📱', renderNumberAnalysis(data.mobile_analysis));
    }

    // ── 10. Car Number Analysis ──────────────────────────
    if (data.car_analysis) {
        html += numSection('Car/Vehicle Number Analysis', '🚗', renderNumberAnalysis(data.car_analysis));
    }

    // ── 11. Password Analysis ────────────────────────────
    html += numSection('Password Numerology', '🔐', renderPasswordAnalysis(data));

    // ── 12. Personal Year Cycle ──────────────────────────
    html += numSection('Personal Year Cycle', '🔄', renderPersonalCycle(data));

    resultDiv.innerHTML = html;
}

function numSection(title, icon, content) {
    return '<div style="background:var(--card-bg);border-radius:10px;padding:14px;margin-bottom:14px;border-left:4px solid '+NC+'">'
         + '<h3 style="color:'+NC+';margin:0 0 10px 0">'+icon+' '+title+'</h3>'
         + content + '</div>';
}

function numCard(label, value, sub, color) {
    color = color || NC;
    var h = '<div style="display:inline-block;background:'+color+'11;border:1px solid '+color+'33;border-radius:8px;padding:10px 16px;margin:4px;text-align:center;min-width:120px">';
    h += '<div style="font-size:0.75rem;color:var(--text-dim)">'+label+'</div>';
    h += '<div style="font-size:1.8rem;font-weight:800;color:'+color+'">'+value+'</div>';
    if (sub) h += '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:2px">'+sub+'</div>';
    h += '</div>';
    return h;
}

// ── Core Numbers ─────────────────────────────────────────────
function renderCoreNumbers(data) {
    var c = data.core_numbers;
    var h = '<div style="display:flex;flex-wrap:wrap;gap:0">';
    h += numCard('Life Path', c.life_path.number, c.life_path.is_master ? 'MASTER NUMBER' : 'Primary Number', '#D32F2F');
    h += numCard('Birthday', c.birthday.number, 'Day: '+c.birthday.raw_day, '#1565C0');
    h += numCard('Maturity', c.maturity.number, 'After age 35+', '#6A1B9A');

    // Name numbers from pythagorean
    var na = data.name_analysis;
    var pyth = na.pythagorean || na.chaldean;
    if (pyth) {
        h += numCard('Destiny', pyth.destiny_number, 'Expression', '#2E7D32');
        h += numCard('Soul Urge', pyth.soul_urge_number, 'Heart\'s Desire', '#C62828');
        h += numCard('Personality', pyth.personality_number, 'Outer Self', '#00695C');
    }
    h += '</div>';

    // Calculation details
    h += '<div style="margin-top:10px;font-size:0.8rem;color:var(--text-dim)">';
    h += '<div><b>Life Path:</b> ' + c.life_path.calculation + '</div>';
    h += '<div><b>Maturity:</b> ' + c.maturity.calculation + ' — ' + c.maturity.meaning + '</div>';
    if (c.life_path.karmic_debt) {
        h += '<div style="color:#F44336;margin-top:6px;padding:8px;background:#F4433611;border-radius:6px"><b>⚠ Karmic Debt:</b> ' + c.life_path.karmic_debt + '</div>';
    }
    h += '</div>';
    return h;
}

// ── Date Addition Analysis ───────────────────────────────────
function renderDateAddition(data) {
    var da = data.core_numbers.date_addition;
    var h = '<div style="display:flex;flex-wrap:wrap;gap:0">';
    h += numCard('Day Number', da.day_number, da.day_calculation, '#1565C0');
    h += numCard('Total DOB', da.total_dob_reduced, 'Sum: ' + da.total_dob_sum, '#D32F2F');
    h += '</div>';

    h += '<div style="margin-top:8px;font-size:0.8rem;color:var(--text-dim)">';
    h += '<div><b>Day Calculation:</b> ' + da.day_calculation + '</div>';
    h += '<div><b>Total Calculation:</b> ' + da.total_calculation + '</div>';
    h += '</div>';

    // Day number traits
    if (da.day_traits && da.day_traits.personality) {
        h += '<div style="margin-top:10px;padding:10px;background:#1565C011;border-radius:8px;border-left:3px solid #1565C0">';
        h += '<div style="font-weight:700;color:#1565C0;margin-bottom:4px">Day Number ' + da.day_number + ' Personality:</div>';
        h += '<div style="font-size:0.82rem">' + da.day_traits.personality + '</div>';
        h += '</div>';
    }
    // Total traits (if different)
    if (da.total_traits && da.total_traits.personality && da.total_dob_reduced !== da.day_number) {
        h += '<div style="margin-top:8px;padding:10px;background:#D32F2F11;border-radius:8px;border-left:3px solid #D32F2F">';
        h += '<div style="font-weight:700;color:#D32F2F;margin-bottom:4px">Total Number ' + da.total_dob_reduced + ' Personality:</div>';
        h += '<div style="font-size:0.82rem">' + da.total_traits.personality + '</div>';
        h += '</div>';
    }
    return h;
}

// ── Name Analysis ────────────────────────────────────────────
function renderNameAnalysis(data) {
    var na = data.name_analysis;
    var h = '';
    var systems = ['pythagorean', 'chaldean'];
    systems.forEach(function(sys) {
        var nd = na[sys];
        if (!nd) return;
        var label = sys.charAt(0).toUpperCase() + sys.slice(1);
        var color = sys === 'pythagorean' ? '#1565C0' : '#6A1B9A';
        h += '<div style="margin-bottom:12px;padding:10px;background:'+color+'08;border-radius:8px;border:1px solid '+color+'22">';
        h += '<div style="font-weight:700;color:'+color+';margin-bottom:6px">'+label+' System</div>';
        h += '<div style="display:flex;flex-wrap:wrap;gap:0">';
        h += numCard('Destiny', nd.destiny_number, 'Total: '+nd.destiny_total, color);
        h += numCard('Soul Urge', nd.soul_urge_number, 'Vowels: '+nd.soul_urge_total, '#C62828');
        h += numCard('Personality', nd.personality_number, 'Consonants: '+nd.personality_total, '#00695C');
        h += '</div>';

        // Letter values table
        if (nd.letter_values && nd.letter_values.length > 0) {
            h += '<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:2px">';
            nd.letter_values.forEach(function(lv) {
                var isVowel = 'AEIOU'.indexOf(lv.letter) >= 0;
                h += '<span style="display:inline-block;width:28px;text-align:center;padding:3px 0;font-size:0.75rem;border-radius:4px;background:'+(isVowel?'#C6282822':'#00695C22')+'">';
                h += '<div style="font-weight:700">'+lv.letter+'</div>';
                h += '<div style="color:var(--text-dim)">'+lv.value+'</div>';
                h += '</span>';
            });
            h += '</div>';
        }

        if (nd.karmic_debt) {
            h += '<div style="color:#F44336;margin-top:6px;font-size:0.8rem"><b>⚠ Karmic Debt:</b> ' + nd.karmic_debt + '</div>';
        }
        h += '</div>';
    });
    return h;
}

// ── Loshu Grid ───────────────────────────────────────────────
function renderLoshuGrid(data) {
    var lg = data.loshu_grid;
    var h = '';

    // Draw the 3x3 grid
    h += '<div style="display:flex;flex-wrap:wrap;gap:20px;align-items:flex-start">';
    h += '<div>';
    h += '<table style="border-collapse:collapse;margin-bottom:10px">';
    for (var r = 0; r < 3; r++) {
        h += '<tr>';
        for (var c = 0; c < 3; c++) {
            var cell = lg.grid[r][c];
            var num = cell.number;
            var cnt = cell.count;
            var bg = cnt === 0 ? '#33333344' : (cnt === 1 ? NC+'22' : (cnt >= 3 ? '#F4433644' : NC+'44'));
            var fw = cnt > 0 ? '800' : '400';
            var textColor = cnt === 0 ? 'var(--text-dim)' : NC;
            h += '<td style="width:70px;height:70px;text-align:center;border:2px solid '+NC+'44;background:'+bg+';vertical-align:middle">';
            h += '<div style="font-size:1.4rem;font-weight:'+fw+';color:'+textColor+'">'+num+'</div>';
            if (cnt > 0) {
                h += '<div style="font-size:0.7rem;color:'+NC+'">×'+cnt+'</div>';
            } else {
                h += '<div style="font-size:0.65rem;color:var(--text-dim)">missing</div>';
            }
            h += '</td>';
        }
        h += '</tr>';
    }
    h += '</table>';
    h += '</div>';

    // Summary beside grid
    h += '<div style="flex:1;min-width:200px">';
    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>DOB Digits:</b> ' + (lg.dob_raw_digits||[]).join(', ') + '</div>';
    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b style="color:#1565C0">Driver (Moolank):</b> <span style="font-weight:800;font-size:1rem;color:#1565C0">'+lg.driver_number+'</span></div>';
    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b style="color:#D32F2F">Conductor (Bhagyank):</b> <span style="font-weight:800;font-size:1rem;color:#D32F2F">'+lg.conductor_number+'</span></div>';
    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>All Grid Digits:</b> ' + (lg.all_digits||[]).join(', ') + '</div>';
    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b style="color:#4CAF50">Present:</b> ' + lg.present_numbers.join(', ') + '</div>';
    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b style="color:#F44336">Missing:</b> ' + (lg.missing_numbers.length ? lg.missing_numbers.join(', ') : 'None!') + '</div>';

    // Repeated numbers
    if (lg.repeated_meanings && Object.keys(lg.repeated_meanings).length > 0) {
        h += '<div style="margin-top:6px;font-size:0.8rem"><b>Repeated Numbers:</b></div>';
        Object.keys(lg.repeated_meanings).forEach(function(num) {
            var rm = lg.repeated_meanings[num];
            h += '<div style="font-size:0.78rem;padding:3px 6px;margin:2px 0;background:#FF980022;border-radius:4px"><b>'+num+' (×'+rm.count+'):</b> '+rm.meaning+'</div>';
        });
    }
    h += '</div></div>';

    // Arrows
    if (lg.arrows && lg.arrows.length > 0) {
        h += '<div style="margin-top:12px"><b style="color:'+NC+'">Arrows Found:</b></div>';
        h += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">';
        lg.arrows.forEach(function(arr) {
            var arrColor = arr.type === 'strength' ? '#4CAF50' : '#F44336';
            h += '<div style="padding:8px 12px;background:'+arrColor+'11;border:1px solid '+arrColor+'33;border-radius:8px;font-size:0.8rem;flex:1;min-width:250px">';
            h += '<div style="font-weight:700;color:'+arrColor+'">'+arr.key.replace(/_/g,' ').toUpperCase()+' ['+arr.numbers.join('-')+']</div>';
            h += '<div>'+arr.desc+'</div>';
            h += '</div>';
        });
        h += '</div>';
    }

    // Planes
    h += '<details style="margin-top:12px"><summary style="font-weight:700;color:'+NC+';cursor:pointer">Planes Analysis (click to expand)</summary>';
    h += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px">';
    lg.planes.forEach(function(pl) {
        var sColor = pl.strength === 'strong' ? '#4CAF50' : (pl.strength === 'moderate' ? '#FF9800' : (pl.strength === 'weak' ? '#F44336' : '#666'));
        h += '<div style="padding:8px;background:'+sColor+'11;border:1px solid '+sColor+'22;border-radius:8px;font-size:0.78rem;flex:1;min-width:200px">';
        h += '<div style="font-weight:700;color:'+sColor+'">'+pl.name+' <span style="background:'+sColor+'22;padding:1px 6px;border-radius:4px;font-size:0.7rem">'+pl.strength.toUpperCase()+'</span></div>';
        h += '<div style="color:var(--text-dim);font-size:0.72rem">Numbers: '+pl.numbers.join(', ')+' | Present: '+pl.present_count+'/3</div>';
        h += '<div style="margin-top:3px">'+pl.desc+'</div>';
        h += '</div>';
    });
    h += '</div></details>';

    // Missing number remedies
    if (lg.missing_remedies && lg.missing_remedies.length > 0) {
        h += '<details style="margin-top:10px"><summary style="font-weight:700;color:#F44336;cursor:pointer">Remedies for Missing Numbers</summary>';
        h += '<div style="margin-top:6px">';
        lg.missing_remedies.forEach(function(rem) {
            h += '<div style="padding:8px;margin-bottom:4px;background:#F4433611;border-radius:6px;font-size:0.8rem;border-left:3px solid #F44336">';
            h += '<b style="color:#F44336">Number '+rem.number+'</b> (Lucky Color: '+rem.color+'): '+rem.remedy;
            h += '</div>';
        });
        h += '</div></details>';
    }

    return h;
}

// ── Personality & Characteristics ────────────────────────────
function renderCharacteristics(data) {
    var ch = data.characteristics;
    var h = '';
    var sections = [
        {key:'life_path', label:'Life Path '+data.core_numbers.life_path.number, color:'#D32F2F'},
        {key:'destiny', label:'Destiny Number', color:'#2E7D32'},
        {key:'birthday', label:'Birthday Number '+data.core_numbers.birthday.number, color:'#1565C0'},
    ];
    sections.forEach(function(sec) {
        var c = ch[sec.key];
        if (!c || !c.personality) return;
        h += '<details'+(sec.key==='life_path'?' open':'')+' style="margin-bottom:10px">';
        h += '<summary style="font-weight:700;color:'+sec.color+';cursor:pointer;font-size:0.9rem">'+sec.label+' — '+c.ruler+' ('+c.element+')</summary>';
        h += '<div style="padding:10px;background:'+sec.color+'08;border-radius:8px;margin-top:4px">';

        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Personality:</b> '+c.personality+'</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Behavior:</b> '+c.behavior+'</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Traits:</b> '+c.traits+'</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b style="color:#4CAF50">Strengths:</b> '+c.strengths+'</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b style="color:#F44336">Weaknesses:</b> '+c.weaknesses+'</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Career:</b> '+c.career+'</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Health:</b> '+c.health+'</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Vedic Deity:</b> '+c.vedic_deity+'</div>';

        // Lucky items
        h += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;font-size:0.78rem">';
        if (c.lucky_colors) h += '<span style="padding:3px 8px;background:#FF980022;border-radius:4px"><b>Colors:</b> '+c.lucky_colors.join(', ')+'</span>';
        if (c.lucky_days) h += '<span style="padding:3px 8px;background:#2196F322;border-radius:4px"><b>Days:</b> '+c.lucky_days.join(', ')+'</span>';
        if (c.lucky_gems) h += '<span style="padding:3px 8px;background:#9C27B022;border-radius:4px"><b>Gems:</b> '+c.lucky_gems.join(', ')+'</span>';
        if (c.compatible) h += '<span style="padding:3px 8px;background:#4CAF5022;border-radius:4px"><b>Compatible:</b> '+c.compatible.join(', ')+'</span>';
        if (c.incompatible) h += '<span style="padding:3px 8px;background:#F4433622;border-radius:4px"><b>Incompatible:</b> '+c.incompatible.join(', ')+'</span>';
        if (c.best_dates) h += '<span style="padding:3px 8px;background:#FF980022;border-radius:4px"><b>Best Dates:</b> '+c.best_dates.join(', ')+'</span>';
        h += '</div>';

        h += '</div></details>';
    });
    return h;
}

// ── Name Correction ──────────────────────────────────────────
function renderNameCorrection(data) {
    var nc = data.name_correction;
    var h = '';
    ['pythagorean', 'chaldean'].forEach(function(sys) {
        var corr = nc[sys];
        if (!corr) return;
        var label = sys.charAt(0).toUpperCase() + sys.slice(1);
        var vColor = corr.is_compatible ? '#4CAF50' : '#F44336';
        h += '<div style="margin-bottom:10px;padding:10px;border:1px solid '+vColor+'33;border-radius:8px;background:'+vColor+'08">';
        h += '<div style="font-weight:700;color:'+vColor+';margin-bottom:4px">'+label+': '+corr.verdict+'</div>';
        h += '<div style="font-size:0.8rem;color:var(--text-dim)">Current Name Number: <b>'+corr.current_destiny_number+'</b> | Life Path: <b>'+corr.life_path_number+'</b> | Compatible Numbers: <b>'+corr.compatible_name_numbers.join(', ')+'</b></div>';

        if (corr.spelling_suggestions && corr.spelling_suggestions.length > 0) {
            h += '<div style="margin-top:8px;font-size:0.82rem"><b>Spelling Suggestions:</b></div>';
            h += '<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">';
            corr.spelling_suggestions.forEach(function(ss) {
                h += '<span style="padding:4px 10px;background:#4CAF5022;border:1px solid #4CAF5033;border-radius:6px;font-size:0.8rem">';
                h += '<b>'+ss.modified_name+'</b> → <span style="color:#4CAF50">'+ss.new_number+'</span>';
                h += '</span>';
            });
            h += '</div>';
        }
        h += '</div>';
    });
    return h;
}

// ── Number Analysis (Mobile / Car) ───────────────────────────
function renderNumberAnalysis(analysis) {
    var vColor = analysis.compatible_with_life_path ? '#4CAF50' : '#F44336';
    var h = '<div style="display:flex;flex-wrap:wrap;gap:0;margin-bottom:8px">';
    h += numCard(analysis.label, analysis.final_number, 'Sum: ' + analysis.digit_sum, vColor);
    h += numCard('Compound', analysis.compound_number, analysis.is_master ? 'MASTER' : '', '#6A1B9A');
    h += '</div>';

    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Original:</b> ' + analysis.original + ' | <b>Calculation:</b> ' + analysis.calculation + '</div>';
    h += '<div style="font-size:0.82rem;margin-bottom:6px;color:'+vColor+';font-weight:600">' + analysis.verdict + '</div>';
    h += '<div style="font-size:0.8rem;padding:6px;background:#6A1B9A11;border-radius:6px;margin-bottom:6px"><b>Compound '+analysis.compound_number+':</b> ' + analysis.compound_meaning + '</div>';
    h += '<div style="font-size:0.8rem;color:var(--text-dim)"><b>Ideal numbers for your Life Path:</b> ' + analysis.ideal_numbers_for_you.join(', ') + '</div>';

    if (analysis.tips) {
        h += '<div style="margin-top:8px">';
        analysis.tips.forEach(function(tip) {
            h += '<div style="font-size:0.8rem;padding:3px 0;color:var(--text-dim)">• '+tip+'</div>';
        });
        h += '</div>';
    }
    return h;
}

// ── Password Analysis ────────────────────────────────────────
function renderPasswordAnalysis(data) {
    var h = '';

    // Current password analysis
    if (data.password_current) {
        var pc = data.password_current;
        var vColor = pc.compatible_with_life_path ? '#4CAF50' : '#F44336';
        h += '<div style="margin-bottom:10px;padding:10px;border:1px solid '+vColor+'33;border-radius:8px;background:'+vColor+'08">';
        h += '<div style="font-weight:700;color:'+vColor+'">Current Password Analysis</div>';
        h += '<div style="font-size:0.82rem">Number: <b>'+pc.final_number+'</b> | Compound: <b>'+pc.compound_number+'</b></div>';
        h += '<div style="font-size:0.82rem;color:'+vColor+'">'+pc.verdict+'</div>';
        h += '</div>';
    }

    // Suggestions
    var ps = data.password_suggestions;
    if (ps) {
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Ideal Password Lengths:</b> ' + ps.ideal_lengths.join(', ') + ' characters</div>';
        h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Lucky Digits:</b> ' + ps.lucky_digits.join(', ') + '</div>';

        if (ps.tips) {
            ps.tips.forEach(function(tip) {
                h += '<div style="font-size:0.8rem;padding:3px 0;color:var(--text-dim)">• '+tip+'</div>';
            });
        }

        if (ps.example_patterns) {
            h += '<div style="margin-top:8px;font-size:0.82rem"><b>Pattern Examples:</b></div>';
            h += '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">';
            ps.example_patterns.forEach(function(p) {
                h += '<code style="padding:4px 10px;background:var(--card-bg);border:1px solid var(--border);border-radius:4px;font-size:0.8rem">'+p+'</code>';
            });
            h += '</div>';
        }
        h += '<div style="font-size:0.72rem;color:var(--text-dim);margin-top:6px;font-style:italic">'+ps.note+'</div>';
    }
    return h;
}

// ── Personal Year Cycle ──────────────────────────────────────
function renderPersonalCycle(data) {
    var pc = data.personal_cycles;
    if (!pc) return '';
    var h = '<div style="display:flex;flex-wrap:wrap;gap:0;margin-bottom:8px">';
    h += numCard('Personal Year', pc.personal_year_number, pc.current_year.toString(), '#6A1B9A');
    h += '</div>';
    h += '<div style="font-size:0.82rem;margin-bottom:6px"><b>Calculation:</b> ' + pc.calculation + '</div>';
    h += '<div style="font-size:0.82rem;margin-bottom:4px"><b>Cycle:</b> ' + pc.cycle_position + '</div>';
    h += '<div style="padding:10px;background:#6A1B9A11;border-radius:8px;font-size:0.85rem;border-left:3px solid #6A1B9A">';
    h += '<b style="color:#6A1B9A">Year Energy:</b> ' + pc.meaning;
    h += '</div>';
    return h;
}

// ── Raj Yogas ────────────────────────────────────────────────
function renderRajYogas(data) {
    var ry = data.raj_yogas;
    if (!ry) return '<p style="color:var(--text-dim)">No yoga data available</p>';

    var h = '';

    // Status badge
    var statusColors = {
        double_raj_yoga: '#FFD700', golden_raj_yoga: '#FFD700', silver_raj_yoga: '#C0C0C0',
        multi_yoga: '#4CAF50', yoga_present: '#2196F3', ordinary: '#666'
    };
    var statusLabels = {
        double_raj_yoga: 'DOUBLE RAJ YOGA (Golden + Silver)', golden_raj_yoga: 'GOLDEN RAJ YOGA',
        silver_raj_yoga: 'SILVER RAJ YOGA', multi_yoga: 'MULTIPLE YOGAS',
        yoga_present: 'YOGA PRESENT', ordinary: 'No Major Yoga'
    };
    var sc = statusColors[ry.status] || '#666';
    var sl = statusLabels[ry.status] || ry.status;
    h += '<div style="text-align:center;margin-bottom:14px;padding:12px;background:'+sc+'22;border:2px solid '+sc+';border-radius:10px">';
    h += '<div style="font-size:1.3rem;font-weight:800;color:'+sc+'">'+sl+'</div>';
    h += '<div style="font-size:0.82rem;color:var(--text-dim)">'+ry.grid_yoga_count+' yoga(s) found in your Loshu Grid</div>';
    h += '</div>';

    // Grid yogas
    if (ry.grid_yogas && ry.grid_yogas.length > 0) {
        ry.grid_yogas.forEach(function(yoga) {
            var yc = yoga.type === 'golden' ? '#FFD700' : (yoga.type === 'silver' ? '#C0C0C0' : NC);
            var badge = yoga.type === 'golden' ? '🥇 GOLDEN' : (yoga.type === 'silver' ? '🥈 SILVER' : '✦');
            h += '<div style="margin-bottom:10px;padding:12px;border:1px solid '+yc+'55;border-radius:10px;background:'+yc+'11;border-left:4px solid '+yc+'">';
            h += '<div style="font-weight:800;font-size:1rem;color:'+yc+'">'+badge+' '+yoga.name+'</div>';
            h += '<div style="font-size:0.75rem;color:var(--text-dim);margin-bottom:6px">Numbers: '+yoga.numbers.join('-')+' | Strength: <b>'+yoga.strength.toUpperCase()+'</b> ('+yoga.total_occurrences+' hits) | Rarity: '+yoga.rarity+'</div>';
            h += '<div style="font-size:0.82rem;margin-bottom:6px">'+yoga.desc+'</div>';

            h += '<div style="display:flex;flex-wrap:wrap;gap:6px;font-size:0.78rem">';
            h += '<div style="flex:1;min-width:150px;padding:6px;background:'+yc+'0A;border-radius:6px"><b style="color:#2E7D32">Career:</b> '+yoga.career+'</div>';
            h += '<div style="flex:1;min-width:150px;padding:6px;background:'+yc+'0A;border-radius:6px"><b style="color:#D32F2F">Wealth:</b> '+yoga.wealth+'</div>';
            h += '<div style="flex:1;min-width:150px;padding:6px;background:'+yc+'0A;border-radius:6px"><b style="color:#1565C0">Health:</b> '+yoga.health+'</div>';
            h += '<div style="flex:1;min-width:150px;padding:6px;background:'+yc+'0A;border-radius:6px"><b style="color:#6A1B9A">Relationships:</b> '+yoga.relationships+'</div>';
            h += '</div></div>';
        });
    } else {
        h += '<p style="color:var(--text-dim);font-style:italic">No Loshu Grid yogas detected. Missing numbers prevent yoga formation. Check Name Correction and Remedies below.</p>';
    }

    // Driver-Conductor yoga
    if (ry.driver_conductor_yoga) {
        var dc = ry.driver_conductor_yoga;
        h += '<div style="margin-top:12px;padding:12px;background:#9C27B011;border:1px solid #9C27B033;border-radius:10px;border-left:4px solid #9C27B0">';
        h += '<div style="font-weight:800;color:#9C27B0;font-size:0.95rem">Driver-Conductor Yoga: '+dc.name+'</div>';
        h += '<div style="font-size:0.78rem;color:var(--text-dim)">Driver: '+dc.driver+' × Conductor: '+dc.conductor+'</div>';
        h += '<div style="font-size:0.82rem;margin-top:4px">'+dc.desc+'</div>';
        h += '</div>';
    }

    return h;
}

// ── Yearly Predictions ───────────────────────────────────────
function renderYearlyPredictions(data) {
    var yp = data.yearly_predictions;
    if (!yp || !yp.yearly_predictions) return '<p style="color:var(--text-dim)">No yearly data</p>';

    var h = '';
    var currentYear = new Date().getFullYear();

    // Quick year rating bar
    h += '<div style="margin-bottom:14px;overflow-x:auto">';
    h += '<div style="display:flex;gap:3px;min-width:600px">';
    yp.yearly_predictions.forEach(function(yr) {
        var barColor = yr.classification === 'golden_year' ? '#FFD700' :
                       yr.classification === 'excellent' ? '#4CAF50' :
                       yr.classification === 'good' ? '#2196F3' :
                       yr.classification === 'average' ? '#FF9800' : '#F44336';
        var isCurrent = yr.year === currentYear;
        var border = isCurrent ? '3px solid #fff' : '1px solid '+barColor+'33';
        h += '<div style="flex:1;text-align:center;padding:6px 2px;background:'+barColor+'33;border:'+border+';border-radius:6px;min-width:50px;cursor:pointer" title="'+yr.year+': '+yr.class_label+' ('+yr.rating+'/10)">';
        h += '<div style="font-size:0.65rem;color:var(--text-dim)">'+yr.year+'</div>';
        h += '<div style="font-size:1rem;font-weight:800;color:'+barColor+'">'+yr.rating+'</div>';
        if (yr.has_golden) h += '<div style="font-size:0.6rem">🥇</div>';
        else if (yr.has_silver) h += '<div style="font-size:0.6rem">🥈</div>';
        h += '</div>';
    });
    h += '</div></div>';

    // Legend
    h += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;font-size:0.72rem">';
    h += '<span style="padding:2px 8px;background:#FFD70033;border-radius:4px;color:#FFD700;font-weight:700">Golden Year (9-10)</span>';
    h += '<span style="padding:2px 8px;background:#4CAF5033;border-radius:4px;color:#4CAF50;font-weight:700">Excellent (7-8)</span>';
    h += '<span style="padding:2px 8px;background:#2196F333;border-radius:4px;color:#2196F3;font-weight:700">Good (5-6)</span>';
    h += '<span style="padding:2px 8px;background:#FF980033;border-radius:4px;color:#FF9800;font-weight:700">Average (4)</span>';
    h += '<span style="padding:2px 8px;background:#F4433633;border-radius:4px;color:#F44336;font-weight:700">Challenging (1-3)</span>';
    h += '</div>';

    // Detailed yearly cards
    yp.yearly_predictions.forEach(function(yr) {
        var isCurrent = yr.year === currentYear;
        var barColor = yr.classification === 'golden_year' ? '#FFD700' :
                       yr.classification === 'excellent' ? '#4CAF50' :
                       yr.classification === 'good' ? '#2196F3' :
                       yr.classification === 'average' ? '#FF9800' : '#F44336';

        h += '<details'+(isCurrent?' open':'')+' style="margin-bottom:8px">';
        h += '<summary style="cursor:pointer;padding:8px 12px;background:'+barColor+'15;border:1px solid '+barColor+'33;border-radius:8px;border-left:4px solid '+barColor+'">';
        h += '<span style="font-weight:800;font-size:0.95rem;color:'+barColor+'">'+yr.year+'</span>';
        h += ' <span style="font-size:0.82rem;font-weight:600">'+yr.class_label+'</span>';
        h += ' <span style="font-size:0.75rem;color:var(--text-dim)">| PY: '+yr.personal_year+' | Rating: '+yr.rating+'/10</span>';
        if (yr.has_golden) h += ' <span style="font-size:0.75rem">🥇 Golden Yoga</span>';
        if (yr.has_silver) h += ' <span style="font-size:0.75rem">🥈 Silver Yoga</span>';
        if (yr.yoga_count > 0) h += ' <span style="font-size:0.72rem;color:var(--text-dim)">('+yr.yoga_count+' yogas)</span>';
        if (isCurrent) h += ' <span style="background:'+barColor+';color:#000;padding:1px 6px;border-radius:4px;font-size:0.65rem;font-weight:700">CURRENT</span>';
        h += '</summary>';

        h += '<div style="padding:10px;background:var(--card-bg);border:1px solid var(--border);border-radius:0 0 8px 8px;margin-top:-2px">';
        h += '<div style="font-weight:700;color:'+barColor+';margin-bottom:6px;font-size:0.9rem">Theme: '+yr.theme+'</div>';

        h += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;font-size:0.8rem">';
        h += '<div style="padding:8px;background:#2E7D3211;border-radius:6px;border-left:3px solid #2E7D32"><b style="color:#2E7D32">Career:</b> '+yr.career+'</div>';
        h += '<div style="padding:8px;background:#D32F2F11;border-radius:6px;border-left:3px solid #D32F2F"><b style="color:#D32F2F">Money:</b> '+yr.money+'</div>';
        h += '<div style="padding:8px;background:#1565C011;border-radius:6px;border-left:3px solid #1565C0"><b style="color:#1565C0">Health:</b> '+yr.health+'</div>';
        h += '<div style="padding:8px;background:#6A1B9A11;border-radius:6px;border-left:3px solid #6A1B9A"><b style="color:#6A1B9A">Relationships:</b> '+yr.relationships+'</div>';
        h += '</div>';

        h += '<div style="margin-top:8px;padding:6px 10px;background:'+barColor+'11;border-radius:6px;font-size:0.82rem"><b style="color:'+barColor+'">Advice:</b> '+yr.advice+'</div>';

        // Year grid info
        h += '<div style="margin-top:6px;font-size:0.72rem;color:var(--text-dim)">';
        h += 'Year Digits: '+yr.year_digits.join(',')+' | Present: '+yr.present_numbers.join(',')+' | Missing: '+(yr.missing_numbers.length?yr.missing_numbers.join(','):'None');
        if (yr.year_yogas.length) h += ' | Yogas: '+yr.year_yogas.map(function(y){return y.replace(/_/g,' ')}).join(', ');
        h += '</div>';

        h += '</div></details>';
    });

    return h;
}


// ═══════════════════════════════════════════════════════════════
// TAROT CARD READING — Fetch + Render
// ═══════════════════════════════════════════════════════════════

var tarotBtn = document.getElementById('tarot-draw');
if (tarotBtn) {
    tarotBtn.addEventListener('click', async function(){
        var resultDiv = document.getElementById('tarot-result');
        var numCards = parseInt(document.getElementById('tarot-count').value) || 3;
        var question = document.getElementById('tarot-question').value.trim();

        resultDiv.innerHTML = '<p style="color:#7B1FA2;font-weight:600;font-size:1.1rem;text-align:center">Shuffling the deck and drawing your cards...</p>';

        var payload = { num_cards: numCards };
        if (question) payload.question = question;

        try {
            var resp = await fetch(API + '/tarot', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            if (!resp.ok) {
                var errBody = await resp.json().catch(function(){ return {}; });
                throw new Error('API error ' + resp.status + ': ' + (errBody.detail || JSON.stringify(errBody)));
            }
            var data = await resp.json();
            renderTarot(data, resultDiv);
        } catch(err) {
            resultDiv.innerHTML = '<p style="color:var(--red)">Error: ' + err.message + '</p>';
        }
    });
}

var TC = '#7B1FA2'; // Tarot color

function renderTarot(data, resultDiv) {
    var html = '';

    // Header
    html += '<div style="text-align:center;margin-bottom:16px;padding:14px;background:'+TC+'11;border-radius:12px;border:1px solid '+TC+'33">';
    html += '<div style="font-size:1.2rem;font-weight:800;color:'+TC+'">'+data.spread_type+'</div>';
    if (data.question) {
        html += '<div style="font-size:0.9rem;color:var(--text-dim);margin-top:4px;font-style:italic">"'+data.question+'"</div>';
    }
    html += '<div style="font-size:0.75rem;color:var(--text-dim);margin-top:4px">Deck: '+data.deck_size+' cards (22 Major + 56 Minor Arcana)</div>';
    html += '</div>';

    // Cards display
    html += '<div style="display:flex;flex-wrap:wrap;gap:14px;justify-content:center;margin-bottom:18px">';
    data.cards.forEach(function(card, i) {
        html += renderTarotCard(card, i);
    });
    html += '</div>';

    // Combination analysis
    if (data.combination_analysis && data.num_cards >= 2) {
        html += renderCombinationAnalysis(data.combination_analysis);
    }

    // Draw again button
    html += '<div style="text-align:center;margin-top:16px">';
    html += '<button onclick="document.getElementById(\'tarot-draw\').click()" style="background:'+TC+';color:#fff;padding:10px 28px;border:none;border-radius:8px;font-size:1rem;font-weight:700;cursor:pointer">Draw Again</button>';
    html += '</div>';

    resultDiv.innerHTML = html;
}

function renderTarotCard(card, index) {
    var isRev = card.is_reversed;
    var isMajor = card.arcana === 'major';
    var borderColor = isMajor ? '#FFD700' : (SUIT_COLORS[card.suit] || TC);
    var bgGrad = isRev
        ? 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)'
        : 'linear-gradient(180deg, #1a1a2e 0%, '+borderColor+'15 100%)';
    var rotation = isRev ? 'transform:rotate(180deg);' : '';

    var h = '<div style="width:220px;background:'+bgGrad+';border:2px solid '+borderColor+';border-radius:12px;overflow:hidden;box-shadow:0 4px 15px rgba(0,0,0,0.3)">';

    // Position label
    h += '<div style="padding:6px 10px;background:'+borderColor+'33;text-align:center;font-size:0.72rem;font-weight:700;color:'+borderColor+';text-transform:uppercase">'+card.position+'</div>';

    // Card face
    h += '<div style="padding:14px;text-align:center">';

    // Card number/suit symbol
    var symbol = isMajor ? _majorSymbol(card.number) : _suitSymbol(card.suit);
    h += '<div style="font-size:2.5rem;'+rotation+'">'+symbol+'</div>';

    // Roman numeral for major
    if (isMajor) {
        h += '<div style="font-size:0.7rem;color:'+borderColor+';margin:2px 0">'+_toRoman(card.number)+'</div>';
    }

    // Card name
    h += '<div style="font-size:1rem;font-weight:800;color:#fff;margin:6px 0">'+card.name+'</div>';

    // Orientation badge
    var orientColor = isRev ? '#F44336' : '#4CAF50';
    var orientLabel = isRev ? 'REVERSED' : 'UPRIGHT';
    h += '<div style="display:inline-block;padding:2px 10px;background:'+orientColor+'33;color:'+orientColor+';border-radius:10px;font-size:0.7rem;font-weight:700">'+orientLabel+'</div>';

    // Arcana type
    h += '<div style="font-size:0.7rem;color:var(--text-dim);margin-top:4px">';
    if (isMajor) h += 'Major Arcana | '+card.element+' | '+card.planet;
    else h += card.suit+' | '+card.element+' | '+card.domain;
    h += '</div>';

    h += '</div>';

    // Active meaning
    h += '<div style="padding:10px 12px;background:rgba(0,0,0,0.3);border-top:1px solid '+borderColor+'33">';
    h += '<div style="font-size:0.8rem;color:#eee;line-height:1.4">'+card.active_meaning+'</div>';

    // Keywords
    if (card.active_keywords && card.active_keywords.length) {
        h += '<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:3px">';
        card.active_keywords.forEach(function(kw) {
            h += '<span style="font-size:0.65rem;padding:1px 6px;background:'+borderColor+'22;color:'+borderColor+';border-radius:4px">'+kw+'</span>';
        });
        h += '</div>';
    }
    h += '</div>';

    // Detailed meanings (expandable)
    if (isMajor) {
        h += '<details style="padding:0 12px 10px 12px">';
        h += '<summary style="font-size:0.72rem;color:'+borderColor+';cursor:pointer;padding:6px 0">Detailed Meanings</summary>';
        h += '<div style="font-size:0.75rem;line-height:1.4">';
        var meanKey = isRev ? 'rev' : 'up';
        if (card['love_'+meanKey]) h += '<div style="margin:3px 0"><b style="color:#E91E63">Love:</b> '+card['love_'+meanKey]+'</div>';
        if (card['career_'+meanKey]) h += '<div style="margin:3px 0"><b style="color:#2E7D32">Career:</b> '+card['career_'+meanKey]+'</div>';
        if (card['money_'+meanKey]) h += '<div style="margin:3px 0"><b style="color:#FF6F00">Money:</b> '+card['money_'+meanKey]+'</div>';
        if (card['health_'+meanKey]) h += '<div style="margin:3px 0"><b style="color:#1565C0">Health:</b> '+card['health_'+meanKey]+'</div>';
        h += '</div></details>';
    }

    h += '</div>';
    return h;
}

var SUIT_COLORS = { Wands: '#FF6F00', Cups: '#1565C0', Swords: '#607D8B', Pentacles: '#2E7D32' };

function _suitSymbol(suit) {
    var m = { Wands: '🪄', Cups: '🏆', Swords: '⚔', Pentacles: '⭐' };
    return m[suit] || '✦';
}

function _majorSymbol(num) {
    var symbols = ['🃏','✨','🌙','👑','🏛','📜','❤','🏇','🦁','🏔','🎡',
                   '⚖','🔄','💀','⚗','😈','🗼','⭐','🌊','☀','📯','🌍'];
    return symbols[num] || '✦';
}

function _toRoman(n) {
    if (n === 0) return '0';
    var roman = ['','I','II','III','IV','V','VI','VII','VIII','IX','X',
                 'XI','XII','XIII','XIV','XV','XVI','XVII','XVIII','XIX','XX','XXI'];
    return roman[n] || n.toString();
}

function renderCombinationAnalysis(combo) {
    var h = '<div style="background:var(--card-bg);border-radius:12px;padding:14px;border-left:4px solid '+TC+';margin-bottom:14px">';
    h += '<h3 style="color:'+TC+';margin:0 0 10px 0">Combination Analysis</h3>';

    // Stats
    h += '<div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;font-size:0.8rem">';
    h += '<span style="padding:4px 10px;background:#FFD70022;border-radius:6px"><b>Major:</b> '+combo.major_count+'</span>';
    h += '<span style="padding:4px 10px;background:#2196F322;border-radius:6px"><b>Minor:</b> '+combo.minor_count+'</span>';
    h += '<span style="padding:4px 10px;background:#F4433622;border-radius:6px"><b>Reversed:</b> '+combo.reversals+' ('+combo.reversal_percentage+'%)</span>';
    if (combo.dominant_suit) h += '<span style="padding:4px 10px;background:'+(SUIT_COLORS[combo.dominant_suit]||TC)+'22;border-radius:6px"><b>Dominant:</b> '+combo.dominant_suit+'</span>';
    if (combo.dominant_element) h += '<span style="padding:4px 10px;background:#FF980022;border-radius:6px"><b>Element:</b> '+combo.dominant_element+'</span>';
    h += '</div>';

    // Energy analysis
    if (combo.energy_analysis && combo.energy_analysis.length) {
        combo.energy_analysis.forEach(function(msg) {
            if (!msg) return;
            h += '<div style="padding:8px 12px;margin-bottom:6px;background:'+TC+'11;border-radius:8px;font-size:0.82rem;border-left:3px solid '+TC+'">'+msg+'</div>';
        });
    }

    // Special combos
    if (combo.special_combos && combo.special_combos.length) {
        h += '<div style="margin-top:8px">';
        combo.special_combos.forEach(function(sc) {
            h += '<div style="padding:8px 12px;margin-bottom:4px;background:#FFD70011;border-radius:8px;font-size:0.82rem;border-left:3px solid #FFD700"><b style="color:#FFD700">Special:</b> '+sc+'</div>';
        });
        h += '</div>';
    }

    // Overall summary
    h += '<div style="margin-top:10px;padding:10px;background:'+TC+'22;border-radius:8px;font-size:0.85rem;font-weight:600;color:'+TC+'">'+combo.summary+'</div>';

    h += '</div>';
    return h;
}
