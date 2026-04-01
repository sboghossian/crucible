/**
 * Crucible Debate Viewer — vanilla JS SPA
 * Hash-based routing: #/ (list), #/debate/:id (viewer), #/live/:id (live)
 */

// ─── Constants ────────────────────────────────────────────────────────────────

const PERSONA_META = {
  pragmatist:   { label: "The Pragmatist",   color: "#f97316", initials: "PR" },
  visionary:    { label: "The Visionary",    color: "#a78bfa", initials: "VI" },
  skeptic:      { label: "The Skeptic",      color: "#f87171", initials: "SK" },
  user_advocate:{ label: "The User Advocate",color: "#4ade80", initials: "UA" },
};

const ROUND_META = {
  1: { label: "Round 1", desc: "Opening Statements" },
  2: { label: "Round 2", desc: "Cross-Examination" },
  3: { label: "Round 3", desc: "Closing Arguments" },
};

// ─── Router ───────────────────────────────────────────────────────────────────

function getRoute() {
  const hash = location.hash.slice(1) || "/";
  if (hash === "/") return { view: "list" };
  const debateMatch = hash.match(/^\/debate\/([^/]+)$/);
  if (debateMatch) return { view: "debate", id: debateMatch[1] };
  const liveMatch = hash.match(/^\/live\/([^/]+)$/);
  if (liveMatch) return { view: "live", id: liveMatch[1] };
  return { view: "list" };
}

function navigate(path) {
  location.hash = path;
}

window.addEventListener("hashchange", () => render(getRoute()));

// ─── API ──────────────────────────────────────────────────────────────────────

async function apiFetch(path, opts = {}) {
  const res = await fetch(path, opts);
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json();
}

// ─── Templates ────────────────────────────────────────────────────────────────

function cloneTemplate(id) {
  return document.getElementById(id).content.cloneNode(true);
}

function qs(root, sel) {
  return root.querySelector(sel);
}

// ─── Views ────────────────────────────────────────────────────────────────────

async function renderDebateList(root) {
  const frag = cloneTemplate("tpl-debate-list");
  root.innerHTML = "";
  root.appendChild(frag);

  const grid = root.querySelector("#debate-grid");

  let debates;
  try {
    const data = await apiFetch("/api/debates");
    debates = data.debates;
  } catch (err) {
    grid.innerHTML = `<div class="error">Failed to load debates: ${err.message}</div>`;
    return;
  }

  if (debates.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">⚗</div>
        <p>No debates recorded yet.</p>
        <button class="btn btn-primary" onclick="document.getElementById('btn-new-debate').click()">
          Start your first debate
        </button>
      </div>`;
    return;
  }

  grid.innerHTML = "";
  for (const debate of debates) {
    grid.appendChild(buildDebateCard(debate));
  }
}

function buildDebateCard(debate) {
  const frag = cloneTemplate("tpl-debate-card");
  const card = frag.querySelector(".debate-card");
  card.dataset.id = debate.id;
  card.addEventListener("click", () => navigate(`/debate/${debate.id}`));

  qs(card, ".debate-date").textContent = formatDate(debate.created_at);
  qs(card, ".debate-topic").textContent = debate.topic;

  const winnerMeta = PERSONA_META[debate.winner];
  if (winnerMeta) {
    const badge = qs(card, ".winner-badge");
    badge.textContent = winnerMeta.label;
    badge.style.setProperty("--winner-color", winnerMeta.color);
    badge.classList.add("winner-badge--visible");
  }

  const scoreBars = qs(card, ".score-bars");
  for (const [persona, score] of Object.entries(debate.scores || {}).sort((a, b) => b[1] - a[1])) {
    const meta = PERSONA_META[persona];
    if (!meta) continue;
    const row = document.createElement("div");
    row.className = "score-row";
    row.innerHTML = `
      <span class="score-persona" style="color:${meta.color}">${meta.initials}</span>
      <div class="score-bar-track">
        <div class="score-bar-fill" style="width:${(score / 10) * 100}%;background:${meta.color}"></div>
      </div>
      <span class="score-val">${score.toFixed(1)}</span>`;
    scoreBars.appendChild(row);
  }

  return frag;
}

async function renderDebateViewer(root, id) {
  const frag = cloneTemplate("tpl-debate-viewer");
  root.innerHTML = "";
  root.appendChild(frag);

  // Wire back button
  root.querySelector(".back-btn").addEventListener("click", () => navigate("/"));

  let debate;
  try {
    debate = await apiFetch(`/api/debates/${id}`);
  } catch (err) {
    root.querySelector(".viewer-rounds").innerHTML =
      `<div class="error">Failed to load debate: ${err.message}</div>`;
    return;
  }

  root.querySelector(".viewer-topic").textContent = debate.topic;
  root.querySelector(".viewer-date").textContent = formatDate(debate.created_at);

  // Winner banner
  const winnerMeta = PERSONA_META[debate.winner];
  if (winnerMeta) {
    const banner = root.querySelector("#winner-banner");
    banner.hidden = false;
    banner.style.setProperty("--winner-color", winnerMeta.color);
    banner.querySelector(".winner-name").textContent = winnerMeta.label;
    banner.querySelector(".winner-score").textContent = debate.winner_score.toFixed(1);
    banner.classList.add("winner-banner--animate");
  }

  // Score chart
  if (debate.scores && Object.keys(debate.scores).length > 0) {
    const scoresSection = root.querySelector("#viewer-scores");
    scoresSection.hidden = false;
    const chart = root.querySelector("#score-chart");
    const sorted = Object.entries(debate.scores).sort((a, b) => b[1] - a[1]);
    for (const [persona, score] of sorted) {
      const meta = PERSONA_META[persona];
      if (!meta) continue;
      const isWinner = persona === debate.winner;
      const row = document.createElement("div");
      row.className = "chart-row" + (isWinner ? " chart-row--winner" : "");
      row.innerHTML = `
        <div class="chart-persona">
          <div class="avatar" style="--color:${meta.color}">${meta.initials}</div>
          <span class="chart-name" style="color:${meta.color}">${meta.label}</span>
          ${isWinner ? '<span class="crown">👑</span>' : ""}
        </div>
        <div class="chart-bar-track">
          <div class="chart-bar-fill" style="--pct:${(score / 10) * 100}%;--color:${meta.color}"></div>
        </div>
        <span class="chart-score">${score.toFixed(1)}</span>`;
      chart.appendChild(row);
    }
  }

  // Rounds
  const roundsEl = root.querySelector("#viewer-rounds");
  roundsEl.innerHTML = "";

  for (const roundData of debate.rounds || []) {
    roundsEl.appendChild(buildRound(roundData));
  }
}

function buildRound(roundData) {
  const frag = cloneTemplate("tpl-round");
  const section = frag.querySelector(".round-section");
  const meta = ROUND_META[roundData.round] || { label: `Round ${roundData.round}`, desc: "" };
  qs(section, ".round-label").textContent = meta.label;
  qs(section, ".round-desc").textContent = meta.desc;

  const stmtsEl = qs(section, ".round-statements");
  for (const stmt of roundData.statements || []) {
    stmtsEl.appendChild(buildStatement(stmt, roundData.round));
  }
  return frag;
}

function buildStatement(stmt, round) {
  const frag = cloneTemplate("tpl-statement");
  const el = frag.querySelector(".statement");
  const meta = PERSONA_META[stmt.persona] || { label: stmt.persona, color: "#888", initials: "??" };

  el.style.setProperty("--persona-color", meta.color);
  if (round === 2) el.classList.add("statement--cross");

  const avatar = qs(el, ".persona-avatar");
  avatar.textContent = meta.initials;
  avatar.style.background = meta.color + "22";
  avatar.style.borderColor = meta.color;

  qs(el, ".persona-name").textContent = meta.label;
  qs(el, ".persona-name").style.color = meta.color;
  qs(el, ".persona-role").textContent = ROUND_META[round]?.desc || "";

  if (stmt.targets && stmt.targets.length > 0) {
    const targetsEl = qs(el, ".statement-targets");
    targetsEl.innerHTML = stmt.targets.map(t => {
      const tm = PERSONA_META[t];
      return tm
        ? `<span class="target-tag" style="color:${tm.color};border-color:${tm.color}">→ ${tm.label}</span>`
        : "";
    }).join("");
  }

  qs(el, ".statement-body").textContent = stmt.content;
  return frag;
}

// ─── Live View ────────────────────────────────────────────────────────────────

function renderLiveViewer(root, debateId) {
  const frag = cloneTemplate("tpl-live-viewer");
  root.innerHTML = "";
  root.appendChild(frag);

  root.querySelector(".back-btn").addEventListener("click", () => {
    if (ws) ws.close();
    navigate("/");
  });

  const statusText = root.querySelector("#live-status-text");
  const roundsEl  = root.querySelector("#viewer-rounds");

  // State
  const rounds = {};
  let ws = null;

  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(`${proto}://${location.host}/ws/debate/${debateId}`);

  ws.onopen = () => { statusText.textContent = "Connected — waiting for debate to start…"; };
  ws.onerror = () => { statusText.textContent = "Connection error."; };
  ws.onclose = () => {
    statusText.textContent = "Debate finished.";
    root.querySelector(".live-spinner").style.display = "none";
  };

  ws.onmessage = (evt) => {
    let event;
    try { event = JSON.parse(evt.data); } catch { return; }
    handleLiveEvent(event, root, rounds, roundsEl, statusText, debateId);
  };
}

function handleLiveEvent(event, root, rounds, roundsEl, statusText, debateId) {
  const kind = event.kind;

  if (kind === "debate_started") {
    root.querySelector(".viewer-topic").textContent = event.topic;
    statusText.textContent = "Debate in progress…";
    return;
  }

  if (kind === "persona_thinking") {
    const meta = PERSONA_META[event.persona_name];
    statusText.textContent = `${meta?.label || event.persona_name} is thinking… (${event.round_label})`;
    return;
  }

  if (kind === "argument_submitted" || kind === "cross_examination") {
    const round = event.round || 2;
    if (!rounds[round]) {
      rounds[round] = { round, statements: [] };
      const roundEl = buildRound(rounds[round]);
      roundEl.firstElementChild.dataset.round = round;
      roundsEl.appendChild(roundEl);
    }
    const stmt = {
      persona: event.persona_name,
      content: event.content,
      targets: event.targets || [],
    };
    rounds[round].statements.push(stmt);

    // Find the section for this round and append statement
    const section = roundsEl.querySelector(`[data-round="${round}"] .round-statements`)
      || roundsEl.lastElementChild?.querySelector(".round-statements");
    if (section) {
      const stmtEl = buildStatement(stmt, round);
      stmtEl.firstElementChild.classList.add("statement--enter");
      section.appendChild(stmtEl);
    }
    return;
  }

  if (kind === "scoring_started") {
    statusText.textContent = "Scoring in progress…";
    return;
  }

  if (kind === "scoring_complete") {
    statusText.textContent = "Scoring complete.";
    return;
  }

  if (kind === "winner_declared") {
    const meta = PERSONA_META[event.winner];
    statusText.textContent = `Winner: ${meta?.label || event.winner} (${event.winner_score.toFixed(1)}/10)`;

    const banner = root.querySelector("#winner-banner");
    if (banner) {
      banner.hidden = false;
      banner.style.setProperty("--winner-color", meta?.color || "#fff");
      banner.querySelector(".winner-name").textContent = meta?.label || event.winner;
      banner.querySelector(".winner-score").textContent = event.winner_score.toFixed(1);
      banner.classList.add("winner-banner--animate");
    }

    // After a short delay, redirect to the saved debate
    setTimeout(() => navigate(`/debate/${debateId}`), 3000);
    return;
  }

  if (kind === "error") {
    statusText.textContent = `Error: ${event.message}`;
  }
}

// ─── Modal ────────────────────────────────────────────────────────────────────

function openModal(title, bodyFn) {
  document.getElementById("modal-title").textContent = title;
  const body = document.getElementById("modal-body");
  body.innerHTML = "";
  bodyFn(body);
  document.getElementById("modal-backdrop").hidden = false;
}

function closeModal() {
  document.getElementById("modal-backdrop").hidden = true;
}

function openNewDebateModal() {
  openModal("New Debate", (body) => {
    const frag = cloneTemplate("tpl-new-debate-form");
    body.appendChild(frag);

    body.querySelector("#form-cancel").addEventListener("click", closeModal);

    body.querySelector("#new-debate-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const form = e.target;
      const submitBtn = form.querySelector("#form-submit");
      submitBtn.disabled = true;
      submitBtn.textContent = "Starting…";

      const topic = form.topic.value.trim();
      const context = form.context.value.trim();
      const optionsRaw = form.options.value.trim();
      const options = optionsRaw ? optionsRaw.split(",").map(s => s.trim()).filter(Boolean) : [];

      try {
        const { debate_id } = await apiFetch("/api/debates", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic, context, options }),
        });
        closeModal();
        navigate(`/live/${debate_id}`);
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = "Start Debate";
        const errEl = document.createElement("p");
        errEl.className = "form-error";
        errEl.textContent = err.message;
        form.prepend(errEl);
      }
    });
  });
}

// ─── Root render ──────────────────────────────────────────────────────────────

async function render(route) {
  const root = document.getElementById("view-root");
  root.innerHTML = `<div class="loading">Loading…</div>`;

  if (route.view === "list") {
    await renderDebateList(root);
  } else if (route.view === "debate") {
    await renderDebateViewer(root, route.id);
  } else if (route.view === "live") {
    renderLiveViewer(root, route.id);
  }
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function formatDate(iso) {
  if (!iso) return "";
  try {
    return new Intl.DateTimeFormat(undefined, {
      year: "numeric", month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit",
    }).format(new Date(iso));
  } catch {
    return iso;
  }
}

// ─── Boot ─────────────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  // Global nav delegation
  document.addEventListener("click", (e) => {
    const link = e.target.closest("[data-nav]");
    if (link) { e.preventDefault(); navigate(link.dataset.nav); }
  });

  document.getElementById("btn-new-debate").addEventListener("click", openNewDebateModal);
  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("modal-backdrop").addEventListener("click", (e) => {
    if (e.target === document.getElementById("modal-backdrop")) closeModal();
  });

  render(getRoute());
});
