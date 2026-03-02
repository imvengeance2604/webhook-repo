/* =========================================================
   GitHub Activity Monitor – frontend polling logic
   Polls /events every 15 seconds and renders the feed.
   ========================================================= */

const POLL_INTERVAL = 15; // seconds

let countdownValue = POLL_INTERVAL;
let countdownTimer = null;
let pollTimer = null;

// ── DOM refs ────────────────────────────────────────────────────────────────
const feed         = document.getElementById("event-feed");
const emptyState   = document.getElementById("empty-state");
const statusDot    = document.getElementById("status-dot");
const statusText   = document.getElementById("status-text");
const lastUpdated  = document.getElementById("last-updated");
const countdownEl  = document.getElementById("countdown");
const statsBar     = document.getElementById("stats-bar");
const pushCount    = document.getElementById("push-count");
const prCount      = document.getElementById("pr-count");
const mergeCount   = document.getElementById("merge-count");
const totalCount   = document.getElementById("total-count");

// ── Utilities ────────────────────────────────────────────────────────────────

/**
 * Format an ISO-8601 UTC timestamp into the required display string.
 * e.g. "1st April 2021 - 9:30 PM UTC"
 */
function formatTimestamp(isoString) {
  const dt = new Date(isoString);
  if (isNaN(dt)) return isoString;

  const day   = dt.getUTCDate();
  const month = dt.toLocaleString("en-GB", { month: "long", timeZone: "UTC" });
  const year  = dt.getUTCFullYear();

  const hours   = dt.getUTCHours();
  const minutes = dt.getUTCMinutes().toString().padStart(2, "0");
  const ampm    = hours >= 12 ? "PM" : "AM";
  const h12     = hours % 12 || 12;

  const suffix = ["th","st","nd","rd"][
    (day % 10 < 4 && Math.floor(day / 10) !== 1) ? day % 10 : 0
  ];

  return `${day}${suffix} ${month} ${year} - ${h12}:${minutes} ${ampm} UTC`;
}

/**
 * Build the human-readable sentence for each action type.
 */
function buildMessage(event) {
  const author = `<strong>"${escHtml(event.author)}"</strong>`;
  const from   = `<span class="branch-tag">${escHtml(event.from_branch)}</span>`;
  const to     = `<span class="branch-tag">${escHtml(event.to_branch)}</span>`;
  const ts     = formatTimestamp(event.timestamp);

  switch (event.action) {
    case "PUSH":
      return `${author} pushed to ${to} on ${ts}`;

    case "PULL_REQUEST":
      return `${author} submitted a pull request from ${from} to ${to} on ${ts}`;

    case "MERGE":
      return `${author} merged branch ${from} to ${to} on ${ts}`;

    default:
      return `${author} performed <strong>${escHtml(event.action)}</strong> on ${ts}`;
  }
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function badgeClass(action) {
  return { PUSH: "push", PULL_REQUEST: "pr", MERGE: "merge" }[action] || "push";
}

function badgeLabel(action) {
  return { PUSH: "PUSH", PULL_REQUEST: "PULL REQUEST", MERGE: "MERGE" }[action] || action;
}

// ── Render ───────────────────────────────────────────────────────────────────

function renderEvents(events) {
  // Clear existing cards (keep empty-state node intact)
  const cards = feed.querySelectorAll(".event-card");
  cards.forEach(c => c.remove());

  if (!events || events.length === 0) {
    emptyState.style.display = "";
    statsBar.style.display   = "none";
    return;
  }

  emptyState.style.display = "none";
  statsBar.style.display   = "flex";

  // Update stats
  const counts = { PUSH: 0, PULL_REQUEST: 0, MERGE: 0 };
  events.forEach(e => { if (counts[e.action] !== undefined) counts[e.action]++; });

  pushCount.textContent  = counts.PUSH;
  prCount.textContent    = counts.PULL_REQUEST;
  mergeCount.textContent = counts.MERGE;
  totalCount.textContent = events.length;

  // Render cards (newest first – server already sorts desc)
  events.forEach(event => {
    const bc   = badgeClass(event.action);
    const card = document.createElement("article");
    card.className = `event-card ${bc}-card`;
    card.innerHTML = `
      <span class="event-badge ${bc}-badge">${badgeLabel(event.action)}</span>
      <div class="event-body">
        <p class="event-message">${buildMessage(event)}</p>
        <p class="event-time">Request ID: ${escHtml(event.request_id)}</p>
      </div>
    `;
    feed.appendChild(card);
  });
}

// ── Status helpers ────────────────────────────────────────────────────────────

function setStatus(state) {
  statusDot.className = `status-dot ${state}`;
  statusText.textContent = state === "live" ? "Live" : state === "error" ? "Error" : "Connecting…";
}

// ── Polling ───────────────────────────────────────────────────────────────────

async function fetchEvents() {
  try {
    const res = await fetch("/events");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderEvents(data);
    setStatus("live");
    lastUpdated.textContent = new Date().toLocaleTimeString();
  } catch (err) {
    console.error("Poll error:", err);
    setStatus("error");
  }
}

function startCountdown() {
  clearInterval(countdownTimer);
  countdownValue = POLL_INTERVAL;
  countdownEl.textContent = countdownValue;

  countdownTimer = setInterval(() => {
    countdownValue--;
    countdownEl.textContent = countdownValue;
    if (countdownValue <= 0) {
      clearInterval(countdownTimer);
    }
  }, 1000);
}

function poll() {
  fetchEvents();
  startCountdown();
}

// ── Boot ─────────────────────────────────────────────────────────────────────
poll();
pollTimer = setInterval(poll, POLL_INTERVAL * 1000);
