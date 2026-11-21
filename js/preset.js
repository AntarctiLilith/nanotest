/* preset.js — shared logic for dedicated preset pages (game-shows.html, ezugi.html) */
(function () {
    const BINTU_API = 'https://bintu.nanostream.cloud/stream/';
    const statusCache = {};
    let hideOffline = true; // "Hide offline" toggle — on by default

    function extractStreamId(url) {
        if (!url) return null;
        let m = url.match(/group\.id=([0-9a-fA-F-]{36})/);
        if (m) return m[1];
        m = url.match(/\/playout\/([0-9a-fA-F-]{36})/);
        if (m) return m[1];
        return null;
    }

    function streamState(stream) {
        const id = extractStreamId(stream.url);
        if (!id) return 'nostream';
        if (statusCache[id]) return statusCache[id];
        return 'checking';
    }

    function statusLabel(state) {
        if (state === 'live') return 'LIVE';
        if (state === 'checking') return '…';
        if (state === 'nostream') return 'NO LINK';
        if (state === 'error') return 'ERROR';
        return 'OFFLINE';
    }

    function statusClass(state) {
        return (state === 'live' || state === 'nostream' || state === 'checking' || state === 'error')
            ? state : 'offline';
    }

    function checkStreamStatus(stream) {
        const id = extractStreamId(stream.url);
        if (!id) { stream.status = 'nostream'; return; }
        if (statusCache[id]) { stream.status = statusCache[id]; return; }
        stream.status = 'checking';
        fetch(BINTU_API + id)
            .then(r => r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status)))
            .then(d => { statusCache[id] = d.state || 'unknown'; stream.status = statusCache[id]; refreshStatuses(); })
            .catch(() => { stream.status = 'error'; refreshStatuses(); });
    }

    function checkAll() {
        (window.__PRESET_STREAMS__ || []).forEach(checkStreamStatus);
    }

    function refreshStatuses() {
        document.querySelectorAll('.preset-card').forEach(card => {
            const stream = window.__PRESET_STREAMS__.find(s => s.name === card.dataset.name);
            if (!stream) return;
            const el = card.querySelector('.status');
            const st = streamState(stream);
            el.className = 'status ' + statusClass(st);
            el.innerHTML = (st === 'live' ? '<span class="dot"></span>' : '') + statusLabel(st);
        });
        applyVisibility();
    }

    // A card is hidden when "Hide offline" is on and the stream is not live.
    // "checking" cards stay visible until their status resolves.
    function applyVisibility() {
        const count = document.getElementById('preset-count');
        const total = (window.__PRESET_STREAMS__ || []).length;
        let visible = 0;
        document.querySelectorAll('.preset-card').forEach(card => {
            const stream = window.__PRESET_STREAMS__.find(s => s.name === card.dataset.name);
            const st = stream ? streamState(stream) : 'nostream';
            const isLive = st === 'live';
            const pending = st === 'checking';
            const hide = hideOffline && !isLive && !pending;
            card.classList.toggle('hidden', hide);
            if (!hide) visible++;
        });
        if (count) count.textContent = (hideOffline && visible < total) ? visible + ' of ' + total : total;
    }

    document.addEventListener('DOMContentLoaded', () => {
        const streams = window.__PRESET_STREAMS__ || [];
        const grid = document.getElementById('preset-grid');
        const count = document.getElementById('preset-count');
        if (count) count.textContent = streams.length;

        streams.forEach(s => {
            const card = document.createElement('div');
            card.className = 'preset-card';
            card.dataset.name = s.name;

            const head = document.createElement('div');
            head.className = 'preset-card-head';
            const name = document.createElement('span');
            name.className = 'preset-name';
            name.textContent = s.name;
            const badge = document.createElement('span');
            badge.className = 'status checking';
            badge.textContent = '…';
            head.appendChild(name);
            head.appendChild(badge);
            card.appendChild(head);

            const frameWrap = document.createElement('div');
            frameWrap.className = 'preset-frame-wrap';
            const embedSrc = s.embed || s.url;
            if (embedSrc) {
                const iframe = document.createElement('iframe');
                iframe.src = embedSrc;
                iframe.className = 'preset-frame';
                iframe.allow = 'autoplay; fullscreen; encrypted-media';
                iframe.allowFullscreen = true;
                iframe.referrerPolicy = 'no-referrer';
                frameWrap.appendChild(iframe);
            } else {
                const noLink = document.createElement('div');
                noLink.className = 'preset-nolink';
                noLink.textContent = 'No stream link';
                frameWrap.appendChild(noLink);
            }
            card.appendChild(frameWrap);

            const foot = document.createElement('div');
            foot.className = 'preset-card-foot';
            const meta = [s.category, s.location, s.country].filter(Boolean).join(' · ');
            if (meta) { const m = document.createElement('span'); m.className = 'preset-meta'; m.textContent = meta; foot.appendChild(m); }
            const openHref = s.playout || s.url;
            if (openHref) {
                const a = document.createElement('a');
                a.className = 'preset-open';
                a.href = openHref; a.target = '_blank'; a.rel = 'noopener';
                a.textContent = 'Open ↗';
                foot.appendChild(a);
            }
            card.appendChild(foot);

            grid.appendChild(card);
        });

        checkAll();
        const btn = document.getElementById('refresh-status');
        if (btn) btn.addEventListener('click', () => {
            for (const k in statusCache) delete statusCache[k];
            checkAll();
        });

        // Auto-refresh: re-check live status every 90s (skips hidden tabs).
        setInterval(() => {
            if (document.hidden) return;
            for (const k in statusCache) delete statusCache[k];
            checkAll();
        }, 90000);

        const hideBtn = document.getElementById('hide-offline');
        if (hideBtn) {
            const sync = () => hideBtn.classList.toggle('active', hideOffline);
            sync();
            hideBtn.addEventListener('click', () => {
                hideOffline = !hideOffline;
                sync();
                applyVisibility();
            });
        }
        applyVisibility();
    });
})();
