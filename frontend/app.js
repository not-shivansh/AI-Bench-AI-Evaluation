/* ═══════════════════════════════════════════════════════════
   AIBench Dashboard – Application Logic
   ═══════════════════════════════════════════════════════════ */

const API_BASE = "/api";

// ── DOM References ────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const els = {
    // Navigation
    tabs: $$(".nav-tab"),
    sections: $$(".section"),
    statusDot: $("#status-dot"),
    statusText: $("#status-text"),

    // Playground
    promptInput: $("#prompt-input"),
    charCount: $("#char-count"),
    btnGenerate: $("#btn-generate"),
    responseArea: $("#response-area"),
    scoresPanel: $("#scores-panel"),
    scoreValue: $("#score-value"),
    ringProgress: $("#ring-progress"),
    scSemantic: $("#sc-semantic"),
    scKeyword: $("#sc-keyword"),
    scLatency: $("#sc-latency"),
    barSemantic: $("#bar-semantic"),
    barKeyword: $("#bar-keyword"),
    barLatency: $("#bar-latency"),

    // Dashboard
    mvTotal: $("#mv-total"),
    mvScore: $("#mv-score"),
    mvLatency: $("#mv-latency"),
    mvUptime: $("#mv-uptime"),

    // History
    historyBody: $("#history-body"),
    historyEmpty: $("#history-empty"),
    historyTable: $("#history-table"),
    btnRefresh: $("#btn-refresh"),

    // Overlays
    loadingOverlay: $("#loading-overlay"),
    toastContainer: $("#toast-container"),
};

// ── Inject SVG gradient for score ring ────────────────────
(function injectSVGDefs() {
    const svg = document.querySelector(".score-ring svg");
    if (!svg) return;
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
        <linearGradient id="score-gradient" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#34d399"/>
            <stop offset="100%" stop-color="#22d3ee"/>
        </linearGradient>
    `;
    svg.prepend(defs);
})();

// ── Navigation ────────────────────────────────────────────
els.tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
        const target = tab.dataset.section;
        switchSection(target);
    });
});

function switchSection(name) {
    els.tabs.forEach((t) => t.classList.toggle("active", t.dataset.section === name));
    els.sections.forEach((s) => {
        s.classList.remove("section-active");
        if (s.id === `section-${name}`) {
            s.classList.add("section-active");
        }
    });

    // Fetch data when switching to dashboard or history
    if (name === "dashboard") fetchMetrics();
    if (name === "history") fetchHistory();
}

// ── Health Check ──────────────────────────────────────────
async function checkHealth() {
    try {
        const res = await fetch("/health");
        const data = await res.json();
        if (data.status === "ok") {
            els.statusDot.className = "status-dot online";
            els.statusText.textContent = "API Online";
        } else {
            throw new Error("Unhealthy");
        }
    } catch {
        els.statusDot.className = "status-dot offline";
        els.statusText.textContent = "API Offline";
    }
}

// ── Character Count ───────────────────────────────────────
els.promptInput.addEventListener("input", () => {
    const len = els.promptInput.value.length;
    els.charCount.textContent = `${len} character${len !== 1 ? "s" : ""}`;
});

// ── Generate ──────────────────────────────────────────────
els.btnGenerate.addEventListener("click", handleGenerate);

els.promptInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) handleGenerate();
});

async function handleGenerate() {
    const prompt = els.promptInput.value.trim();
    if (!prompt) {
        showToast("Please enter a prompt first.", "error");
        return;
    }

    els.btnGenerate.disabled = true;
    els.loadingOverlay.style.display = "flex";

    try {
        const res = await fetch(`${API_BASE}/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: prompt }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();
        displayResponse(data);
        displayScores(data);
        showToast("Response generated successfully!", "success");
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
    } finally {
        els.btnGenerate.disabled = false;
        els.loadingOverlay.style.display = "none";
    }
}

function displayResponse(data) {
    els.responseArea.textContent = data.response;
    els.responseArea.classList.remove("empty-state");
}

function displayScores(data) {
    els.scoresPanel.style.display = "block";

    // Final score ring
    const score = data.score;
    const circumference = 2 * Math.PI * 52; // r=52
    const offset = circumference - score * circumference;
    els.ringProgress.style.strokeDashoffset = offset;
    els.scoreValue.textContent = score.toFixed(2);

    // Breakdown
    animateValue(els.scSemantic, data.semantic_score.toFixed(2));
    els.barSemantic.style.width = `${data.semantic_score * 100}%`;

    animateValue(els.scKeyword, data.keyword_score.toFixed(2));
    els.barKeyword.style.width = `${data.keyword_score * 100}%`;

    // Latency – normalize to a bar (max ~5s = 5000ms)
    const latencyNorm = Math.min(data.latency_ms / 5000, 1);
    els.scLatency.textContent = `${data.latency_ms.toFixed(0)} ms`;
    els.barLatency.style.width = `${latencyNorm * 100}%`;
}

function animateValue(el, target) {
    el.textContent = target;
}

// ── Metrics ───────────────────────────────────────────────
async function fetchMetrics() {
    try {
        const res = await fetch(`${API_BASE}/metrics`);
        const data = await res.json();

        animateCounter(els.mvTotal, data.total_requests, 0, false);
        animateCounter(els.mvScore, data.average_score, 2, false);
        els.mvLatency.textContent = `${data.average_latency.toFixed(0)} ms`;
    } catch {
        showToast("Failed to load metrics.", "error");
    }
}

function animateCounter(el, target, decimals = 0) {
    const duration = 600;
    const start = parseFloat(el.textContent) || 0;
    const startTime = performance.now();

    function step(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = start + (target - start) * eased;
        el.textContent = decimals ? current.toFixed(decimals) : Math.round(current);
        if (progress < 1) requestAnimationFrame(step);
    }

    requestAnimationFrame(step);
}

// ── History ───────────────────────────────────────────────
els.btnRefresh.addEventListener("click", fetchHistory);

async function fetchHistory() {
    try {
        const res = await fetch(`${API_BASE}/history`);
        const data = await res.json();
        renderHistory(data);
    } catch {
        showToast("Failed to load history.", "error");
    }
}

function renderHistory(items) {
    if (!items.length) {
        els.historyTable.style.display = "none";
        els.historyEmpty.style.display = "flex";
        return;
    }

    els.historyTable.style.display = "table";
    els.historyEmpty.style.display = "none";

    els.historyBody.innerHTML = items
        .map(
            (item) => `
        <tr>
            <td style="font-family:var(--font-mono);color:var(--text-muted);">#${item.id}</td>
            <td class="prompt-cell" title="${escapeHtml(item.input)}">${escapeHtml(item.input)}</td>
            <td><span class="score-chip ${scoreClass(item.score)}">${item.score.toFixed(2)}</span></td>
            <td><span class="score-chip ${scoreClass(item.semantic_score)}">${item.semantic_score.toFixed(2)}</span></td>
            <td><span class="score-chip ${scoreClass(item.keyword_score)}">${item.keyword_score.toFixed(2)}</span></td>
            <td style="font-family:var(--font-mono);">${item.latency_ms.toFixed(0)} ms</td>
            <td><span class="status-badge status-${item.status}">${item.status}</span></td>
            <td class="time-cell">${formatTime(item.timestamp)}</td>
        </tr>
    `
        )
        .join("");
}

function scoreClass(score) {
    if (score >= 0.7) return "score-good";
    if (score >= 0.4) return "score-mid";
    return "score-low";
}

function formatTime(ts) {
    const d = new Date(ts);
    return d.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

// ── Toast ─────────────────────────────────────────────────
function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    els.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(20px)";
        toast.style.transition = "all 0.3s ease";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ── Init ──────────────────────────────────────────────────
checkHealth();
setInterval(checkHealth, 30000); // ping every 30s
