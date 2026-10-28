/* Ember Studio dashboard: shared components (Dashboard 2.0, Phase D). Exposes window.ui.
   Data comes from the page shell's window.dash (datasets) and window.dashHealth (sync jobs). Unknown values are
   never shown as 0: every helper takes null as "no value" and renders a state instead. */
window.ui = (() => {
  const fmt = d3.format(',');
  const num = v => (v == null || v === '' || Number.isNaN(Number(v))) ? null : Number(v);
  const usd = v => v == null || !isFinite(v) ? '—' : d3.format(Math.abs(v) >= 1000 ? '$,.0f' : '$,.2f')(v);
  const pct = v => v == null || !isFinite(v) ? '—' : d3.format('.1%')(v);
  const big = v => v == null ? '—' : Math.abs(v) >= 10000 ? d3.format('.3~s')(v) : fmt(Math.round(v * 100) / 100);
  const day = s => d3.utcFormat('%b %-d')(new Date(s + 'T00:00:00Z'));
  const iso = t => d3.utcFormat('%Y-%m-%d')(t);
  const addDays = (s, n) => iso(new Date(new Date(s + 'T00:00:00Z').getTime() + n * 864e5));

  function el(tag, attrs = {}, ...kids) {
    const e = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([k, v]) => {
      if (v == null || v === false) return;
      if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? '' : v);
    });
    kids.flat().forEach(k => k != null && e.append(k instanceof Node ? k : document.createTextNode(String(k))));
    return e;
  }

  const rows = id => { const d = dash.data(id); return d.status === 'ok' ? d.data : []; };
  const status = id => dash.data(id).status;
  const todayET = () => new Intl.DateTimeFormat('sv-SE', {timeZone: 'America/New_York'}).format(new Date());

  /* Periods: the selected window ending today (Eastern) and the equal window right before it. */
  function periods(n, end = todayET()) {
    const from = addDays(end, -(n - 1));
    return {cur: [from, end], prev: [addDays(from, -n), addDays(from, -1)], n};
  }
  const inRange = (d, [a, b]) => d >= a && d <= b;
  function sumIn(data, key, range, dateKey = 'date', filter = () => true) {
    const hit = data.filter(r => inRange(String(r[dateKey]).slice(0, 10), range) && filter(r));
    return hit.length ? d3.sum(hit, r => num(r[key]) || 0) : null;
  }
  function series(data, key, range, dateKey = 'date', filter = () => true) {
    const by = d3.rollup(data.filter(r => inRange(String(r[dateKey]).slice(0, 10), range) && filter(r)),
      v => d3.sum(v, r => num(r[key]) || 0), r => String(r[dateKey]).slice(0, 10));
    const out = []; for (let d = range[0]; d <= range[1]; d = addDays(d, 1)) out.push(by.get(d) ?? 0);
    return out;
  }

  /* Freshness of a sync job, from the shell's health list. */
  function freshness(job, lateMin) {
    const h = (window.dashHealth || []).filter(x => job.endsWith('*') ? x.job.startsWith(job.slice(0, -1)) : x.job === job);
    if (!h.length) return {cls: '', text: 'never synced'};
    const last = d3.min(h, x => x.last_success ? new Date(x.last_success) : null);
    if (h.some(x => x.ok === false)) return {cls: 'bad', text: 'last sync failed'};
    if (!last) return {cls: 'warn', text: 'never synced'};
    const age = (Date.now() - last) / 60000;
    const t = age < 90 ? `${Math.round(age)} min ago` : age < 2880 ? `${Math.round(age / 60)} h ago` : `${Math.round(age / 1440)} d ago`;
    return {cls: age > (lateMin || 45) ? 'warn' : 'ok', text: t};
  }

  function spark(values, color) {
    const W = 120, H = 28;
    const svg = d3.create('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('preserveAspectRatio', 'none').attr('class', 'kpi-spark')
      .attr('width', '100%').attr('aria-hidden', 'true');
    if (!values || values.length < 2 || !d3.max(values)) return svg.node();
    const x = d3.scaleLinear([0, values.length - 1], [1, W - 1]), y = d3.scaleLinear([0, d3.max(values)], [H - 2, 2]);
    svg.append('path').attr('d', d3.area((v, i) => x(i), H - 1, v => y(v))(values)).attr('fill', color).attr('opacity', .12);
    svg.append('path').attr('d', d3.line((v, i) => x(i), v => y(v))(values)).attr('fill', 'none').attr('stroke', color).attr('stroke-width', 1.6);
    return svg.node();
  }

  /* KPI card. o: {label, value, prev, format, invert (lower is better), spark, color, source, job, lateMin, tip, state, sub} */
  function kpi(o) {
    const f = o.format || big;
    const card = el('div', {class: 'es-tile kpi', title: o.tip || null});
    const top = el('div', {class: 'kpi-top'}, el('span', {class: 'es-label', text: o.label}));
    card.append(top);
    if (o.state) {
      card.append(el('div', {class: 'kpi-val', text: '—'}), el('div', {class: 'kpi-state', text: o.state}));
    } else {
      card.append(el('div', {class: 'kpi-val', text: o.value == null ? '—' : f(o.value)}));
      let delta = null;
      if (o.value != null && o.prev != null) {
        const ch = o.prev === 0 ? (o.value === 0 ? 0 : null) : (o.value - o.prev) / Math.abs(o.prev);
        const dir = ch == null ? (o.value > 0 ? 'up' : 'flat') : Math.abs(ch) < 0.005 ? 'flat' : ch > 0 ? 'up' : 'down';
        delta = el('span', {class: `kpi-delta ${dir}${o.invert ? ' inv' : ''}`,
          // a tiny previous period (e.g. before launch) makes percentages meaningless: cap the display at 10x
          text: ch == null ? 'new' : ch > 9 ? '▲ >10×' : `${ch > 0 ? '▲' : ch < 0 ? '▼' : '■'} ${d3.format('.0%')(Math.abs(ch))}`});
        top.append(delta);
      }
      card.append(el('div', {class: 'kpi-prev', text: o.sub || (o.prev == null ? 'no previous period data' : `previous period ${f(o.prev)}`)}));
      if (o.spark) card.append(spark(o.spark, o.color || 'var(--color-accent)'));
    }
    const fr = o.job ? freshness(o.job, o.lateMin) : null;
    card.append(el('div', {class: 'kpi-foot'}, el('span', {text: o.source || ''}),
      fr ? el('span', {}, el('span', {class: `dot ${fr.cls}`}), fr.text) : el('span')));
    return card;
  }

  function tooltip(box) {
    let tip = box.querySelector('.es-tip');
    if (!tip) { tip = el('div', {class: 'es-tip'}); tip.hidden = true; box.append(tip); }
    return tip;
  }

  /* Bars over days. o: {x (key), y (fn), color (str|fn), yfmt, lines (fn -> [str]), empty, ref} */
  function bars(box, data, o) {
    box.replaceChildren();
    const yv = o.y;
    if (!data.length || !d3.max(data, yv)) { box.append(el('p', {class: 'es-empty', text: o.empty || 'No data yet.'})); return; }
    const W = Math.max(280, box.clientWidth), H = o.height || 180, m = {t: 12, r: 12, b: 26, l: 46};
    const x = d3.scaleBand(data.map(r => r[o.x]), [m.l, W - m.r]).padding(0.25);
    const y = d3.scaleLinear([0, Math.max(d3.max(data, yv), o.ref || 0, 1)], [H - m.b, m.t]).nice(4);
    const svg = d3.select(box).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`);
    svg.append('g').selectAll('line').data(y.ticks(4)).join('line').attr('x1', m.l).attr('x2', W - m.r)
      .attr('y1', v => y(v)).attr('y2', v => y(v)).attr('stroke', 'var(--cds-chart-grid)');
    svg.append('g').selectAll('text').data(y.ticks(4)).join('text').attr('x', m.l - 6).attr('y', v => y(v) + 4)
      .attr('text-anchor', 'end').text(o.yfmt || fmt);
    const step = Math.ceil(data.length / Math.max(1, Math.floor((W - m.l - m.r) / 56)));
    svg.append('g').selectAll('text').data(data.filter((r, i) => i % step === 0)).join('text')
      .attr('x', r => x(r[o.x]) + x.bandwidth() / 2).attr('y', H - 8).attr('text-anchor', 'middle').text(r => day(r[o.x]));
    svg.append('g').selectAll('rect').data(data).join('rect').attr('x', r => x(r[o.x]) + Math.max(0, (x.bandwidth() - 26) / 2))
      .attr('width', Math.min(26, x.bandwidth())).attr('y', r => y(yv(r))).attr('height', r => y(0) - y(yv(r))).attr('rx', 3)
      .attr('fill', o.color || 'var(--color-accent)');
    if (o.ref) svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(o.ref)).attr('y2', y(o.ref))
      .attr('stroke', 'var(--cds-chart-reference)').attr('stroke-dasharray', '4 4');
    const tip = tooltip(box);
    svg.selectAll('rect').on('mousemove', (ev, r) => {
      tip.hidden = false;
      tip.replaceChildren(el('div', {class: 'd', text: day(r[o.x])}), ...(o.lines ? o.lines(r) : [fmt(yv(r))]).map(t => el('div', {text: t})));
      const [px, py] = d3.pointer(ev, box);
      tip.style.left = Math.min(px + 12, box.clientWidth - tip.offsetWidth) + 'px'; tip.style.top = Math.max(0, py - 56) + 'px';
    }).on('mouseleave', () => { tip.hidden = true; });
  }

  /* Sortable table with optional CSV export. cols: [{k, label, n (numeric), f (format fn), cls (fn -> class)}] */
  function table(tbl, data, cols, o = {}) {
    const state = tbl._sort || (tbl._sort = {k: o.sortKey, desc: o.desc ?? true});
    const head = tbl.querySelector('thead') || tbl.appendChild(el('thead'));
    const body = tbl.querySelector('tbody') || tbl.appendChild(el('tbody'));
    const redraw = () => table(tbl, data, cols, o);
    head.replaceChildren(el('tr', {}, cols.map(c => el('th', {class: c.n ? 'n' : null, 'data-k': c.k,
      onclick: () => { state.desc = state.k === c.k ? !state.desc : !!c.n; state.k = c.k; redraw(); }},
      c.label + (state.k === c.k ? (state.desc ? ' ↓' : ' ↑') : '')))));
    let rs = [...data];
    if (state.k) {
      const c = cols.find(c => c.k === state.k) || {};
      const v = r => c.n ? (num(r[state.k]) ?? -Infinity) : String(r[state.k] ?? '');
      rs.sort((a, b) => (v(a) < v(b) ? -1 : v(a) > v(b) ? 1 : 0) * (state.desc ? -1 : 1));
    }
    if (o.total) rs.push({...o.total, _total: true});
    body.replaceChildren(...(rs.length ? rs.map(r => el('tr', {class: r._total ? 'total' : null, onclick: o.onRow && !r._total ? () => o.onRow(r) : null,
      style: o.onRow && !r._total ? 'cursor:pointer' : null},
      cols.map(c => el('td', {class: [c.n ? 'n' : '', c.cls ? c.cls(r) : ''].join(' ').trim() || null,
        text: c.f ? c.f(r[c.k], r) : (r[c.k] ?? '')})))) : [el('tr', {}, el('td', {class: 'es-empty', colspan: cols.length, text: o.empty || 'Nothing yet.'}))]));
    return rs;
  }

  function csv(filename, data, cols) {
    const q = v => { const s = String(v ?? ''); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
    const text = [cols.map(c => q(c.label)).join(','), ...data.map(r => cols.map(c => q(r[c.k])).join(','))].join('\n');
    const a = el('a', {href: URL.createObjectURL(new Blob([text], {type: 'text/csv'})), download: filename});
    document.body.append(a); a.click(); a.remove();
  }

  function drawer(title, ...content) {
    document.querySelectorAll('.drawer, .drawer-back').forEach(n => n.remove());
    const close = () => { back.remove(); d.remove(); document.removeEventListener('keydown', esc); };
    const esc = e => { if (e.key === 'Escape') close(); };
    const back = el('div', {class: 'drawer-back', onclick: close});
    const d = el('aside', {class: 'drawer', role: 'dialog', 'aria-label': title},
      el('button', {class: 'es-btn close', type: 'button', onclick: close, text: 'Close'}), el('h3', {text: title}), ...content);
    document.body.append(back, d); document.addEventListener('keydown', esc);
    d.querySelector('.close').focus();
  }
  const dl = pairs => el('dl', {}, pairs.filter(([, v]) => v != null && v !== '').flatMap(([k, v]) => [el('dt', {text: k}), el('dd', {}, v)]));

  function segmented(container, options, value, onChange) {
    container.replaceChildren(...options.map(([v, label]) => el('button', {type: 'button', 'aria-pressed': String(v === value),
      onclick: () => onChange(v), text: label})));
  }

  /* Rule-based alerts: each says what happened, why it matters, the evidence and what to do. */
  function alerts(range) {
    const {usd, num, day, rows, sumIn, todayET} = window.ui;
    const store = rows('store_daily').map(r => ({...r, date: r.day}));
    const c = {spend: sumIn(rows('ads_daily'), 'spend', range), orders: sumIn(store, 'orders', range)};
    const P = {cur: range};
    const out = [];
    (window.dashHealth || []).forEach(h => {
      const age = h.last_success ? (Date.now() - new Date(h.last_success)) / 60000 : null;
      const late = h.job.startsWith('ads:') ? 7 * 60 : 45;
      if (h.ok === false) out.push({sev: 'bad', title: `${h.label} sync failed`, why: 'Its numbers on the dashboard are not current.',
        ev: h.error || 'see Operations', act: 'Check Operations → Sync health.', href: '/ops'});
      else if (age == null || age > late) out.push({sev: 'warn', title: `${h.label} data is stale`, why: 'Figures may be out of date.',
        ev: `last success ${age == null ? 'never' : Math.round(age / 60) + ' h ago'}`, act: h.job.startsWith('ads:') ? 'Keep the Claude app open for the 3-hourly ads refresh.' : 'Check the dashboard task on the PC.', href: '/ops'});
    });
    const ads = rows('ads_daily'), accts = rows('ads_accounts');
    accts.forEach(a => {
      const recent = sumIn(ads.filter(r => r.platform === a.platform), 'spend', [window.ui.addDays(todayET(), -2), todayET()]);
      if (num(a.active_campaigns) > 0 && !recent) out.push({sev: 'info', title: `${a.platform === 'meta' ? 'Meta' : a.platform === 'tiktok' ? 'TikTok' : 'Microsoft'}: campaign live but not delivering`,
        why: 'A live campaign with no spend for 3 days is usually in review, learning or blocked.', ev: a.note || '', act: 'Check delivery status in that ad account.', href: '/ads'});
    });
    if ((c.spend || 0) >= 40 && !c.orders) out.push({sev: 'warn', title: 'Ad spend without orders', why: 'Spend is at least twice the $20 planning cost per order with no sales.',
      ev: `${usd(c.spend)} spent, 0 orders in the period`, act: 'Check tracking and the ads’ landing pages before spending more.', href: '/ads'});
    const flagged = rows('store_daily').filter(r => Number(r.bot_flag) && window.ui.inRange(r.day, P.cur));
    if (flagged.length) out.push({sev: 'info', title: `${flagged.length} day${flagged.length > 1 ? 's' : ''} of likely bot traffic`,
      why: 'Left out of visits and conversion so they do not distort the rates.', ev: flagged.map(r => `${day(r.day)}: ${r.bot_reason}`).join('; '), act: 'Nothing to do; see Store for detail.', href: '/store'});
    const rec = rows('store_reconciliation')[0];
    if (rec && !rec.ok) out.push({sev: 'bad', title: 'Store numbers do not match Shopify', why: 'Store figures may be wrong.',
      ev: (rec.checks || []).filter(x => !x.ok).map(x => x.check).join(', '), act: 'See Store → Data check.', href: '/store'});
    const drafts = rows('schedule').filter(r => /TikTok drafts/.test(r.tiktok || ''));
    if (drafts.length) out.push({sev: 'warn', title: `${drafts.length} video${drafts.length > 1 ? 's' : ''} waiting in your TikTok drafts`,
      why: 'They only go live once you post them from the TikTok app (with the AI-generated label).', ev: drafts.map(r => `${day(r.date)} ${r.time} ${r.series}`).join('; '),
      act: 'Open TikTok → Inbox or Drafts and post them.', href: '/content'});
    const attr = rows('store_attribution')[0];
    (attr && attr.tag_issues || []).forEach(t => out.push({sev: 'warn', title: `Tracking tags arrived unfilled (${t.source})`,
      why: 'Visits from this link can’t be tied to a campaign. Ad previews often do this; live clicks should not.',
      ev: `${t.macros.join(', ')} on ${t.sessions} visit${t.sessions === 1 ? '' : 's'} (campaign "${t.campaign}")`,
      act: 'If it keeps happening after launch, fix the URL parameters in that ad (needs your OK).', href: '/ads'}));
    rows('ads_entities').filter(e => e.level === 'campaign' && /^active/i.test(e.status || '') && /^none/i.test(e.url_tags || '')
      && !/Like Page/i.test(e.url_tags || '')).forEach(e => out.push({sev: 'warn', title: `${e.name}: links carry no tracking tags`,
      why: 'Store visits and orders from this campaign will look like ordinary search or direct traffic.', ev: e.url_tags,
      act: 'Add a final URL suffix with utm_source/utm_medium/utm_campaign (a change to a live campaign: needs your OK).', href: '/ads'}));
    return out;
  }

  return {alerts, fmt, num, usd, pct, big, day, iso, addDays, el, rows, status, todayET, periods, inRange, sumIn, series, freshness,
    spark, kpi, tooltip, bars, table, csv, drawer, dl, segmented};
})();
