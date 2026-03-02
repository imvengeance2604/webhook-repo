/* =========================================================
   GitHub Activity Monitor – Frontend Polling Logic
   
   This module handles real-time event monitoring:
   - Polls the /events endpoint every 15 seconds
   - Renders event cards with formatted timestamps
   - Updates live status indicator and statistics
   - Prevents duplicate events via DOM clearing between polls
   
   Date Format: "2nd March 2026 - 2:35 PM UTC"
   ========================================================= */

const POLL_INTERVAL = 15; // Refresh interval in seconds

// Track countdown timer state
let countdownValue = POLL_INTERVAL;
let countdownTimer = null;
let pollTimer = null;

// ── DOM References ────────────────────────────────────────────────────────────
// Main feed container
const feed         = document.getElementById("event-feed");
const emptyState   = document.getElementById("empty-state");

// Status indicator (top-right corner)
const statusDot    = document.getElementById("status-dot");
const statusText   = document.getElementById("status-text");
const lastUpdated  = document.getElementById("last-updated");
const countdownEl  = document.getElementById("countdown");

// Statistics bar (counts by action type)
const statsBar     = document.getElementById("stats-bar");
const pushCount    = document.getElementById("push-count");
const prCount      = document.getElementById("pr-count");
const mergeCount   = document.getElementById("merge-count");
const totalCount   = document.getElementById("total-count");

// ── Utilities ────────────────────────────────────────────────────────────────

/**
 * Format an ISO-8601 UTC timestamp into human-readable display format.
 * 
 * Converts: "2026-03-02T14:35:00Z"
 * To: "2nd March 2026 - 2:35 PM UTC"
 * 
 * Features:
 * - Proper ordinal suffixes (1st, 2nd, 3rd, etc.)
 * - 12-hour time format with AM/PM
 * - Full month names
 * - UTC timezone notation
 * 
 * @param {string} isoString - ISO-8601 timestamp string
 * @returns {string} Formatted timestamp for display
 */
function formatTimestamp(isoString) {
  // Parse ISO string to UTC date
  const dt = new Date(isoString);
  if (isNaN(dt)) return isoString; // Fallback for invalid dates
  
  // Extract date components in UTC (not local time)
  const day   = dt.getUTCDate();
  const month = dt.toLocaleString("en-GB", { month: "long", timeZone: "UTC" });
  const year  = dt.getUTCFullYear();

  // Extract time components
  const hours   = dt.getUTCHours();
  const minutes = dt.getUTCMinutes().toString().padStart(2, "0");
  const ampm    = hours >= 12 ? "PM" : "AM";
  const h12     = hours % 12 || 12; // Convert 0 to 12 for midnight

  // Calculate ordinal suffix (st, nd, rd, th)
  // Rule: 1,2,3 get -st,-nd,-rd unless they're in the teens
  const suffix = ["th","st","nd","rd"][
    (day % 10 < 4 && Math.floor(day / 10) !== 1) ? day % 10 : 0
  ];

  return `${day}${suffix} ${month} ${year} - ${h12}:${minutes} ${ampm} UTC`;
}
/**
 * Build the human-readable message for each event action type.
 * 
 * Formats event details into clear, descriptive sentences:
 * - PUSH: "username pushed to branch-name on timestamp"
 * - PULL_REQUEST: "username submitted a pull request from branch-name to branch-name on timestamp"
 * - MERGE: "username merged branch branch-name to branch-name on timestamp"
 * 
 * @param {Object} event - Event object from API
 * @returns {string} HTML-formatted message string
 */
function buildMessage(event) {
  const author = `<strong>"${escHtml(event.author)}"</strong>`;
  const from   = `<span class="branch-tag">${escHtml(event.from_branch)}</span>`;
  const to     = `<span class="branch-tag">${escHtml(event.to_branch)}</span>`;
  const ts     = formatTimestamp(event.timestamp);

  // Build message based on action type
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

/**
 * Escape HTML special characters to prevent XSS attacks.
 * 
 * @param {string} str - String to escape
 * @returns {string} HTML-safe string
 */
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Get CSS class name for badge styling based on action type.
 * 
 * @param {string} action - Action type (PUSH, PULL_REQUEST, MERGE)
 * @returns {string} CSS class name
 */
function badgeClass(action) {
  return { PUSH: "push", PULL_REQUEST: "pr", MERGE: "merge" }[action] || "push";
}

/**
 * Get display label for badge based on action type.
 * 
 * @param {string} action - Action type
 * @returns {string} Human-readable action label
 */
function badgeLabel(action) {
  return { PUSH: "PUSH", PULL_REQUEST: "PULL REQUEST", MERGE: "MERGE" }[action] || action;
}

// ── Render ───────────────────────────────────────────────────────────────────

/**
 * Render event cards to the DOM and update statistics.
 * 
 * This function:
 * 1. Clears all existing event cards (prevents duplicates)
 * 2. Shows/hides empty state message
 * 3. Updates statistics (counts by action type)
 * 4. Renders new event cards with formatted messages
 * 
 * @param {Array} events - Array of event objects from API
 */
function renderEvents(events) {
  // Remove all existing cards (new DOM prevents duplicates from old polls)
  const cards = feed.querySelectorAll(".event-card");
  cards.forEach(c => c.remove());

  // Handle empty state
  if (!events || events.length === 0) {
    emptyState.style.display = "";
    statsBar.style.display   = "none";
    return;
  }

  // Show stats bar
  emptyState.style.display = "none";
  statsBar.style.display   = "flex";

  // Calculate and display event counts
  const counts = { PUSH: 0, PULL_REQUEST: 0, MERGE: 0 };
  events.forEach(e => { if (counts[e.action] !== undefined) counts[e.action]++; });

  pushCount.textContent  = counts.PUSH;
  prCount.textContent    = counts.PULL_REQUEST;
  mergeCount.textContent = counts.MERGE;
  totalCount.textContent = events.length;

  // Render event cards (newest first – server already sorts by timestamp desc)
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

// ── Status Helpers ────────────────────────────────────────────────────────────

/**
 * Update the connection status indicator.
 * 
 * @param {string} state - Status state ('live', 'error', or 'connecting')
 */
function setStatus(state) {
  statusDot.className = `status-dot ${state}`;
  statusText.textContent = state === "live" ? "Live" : state === "error" ? "Error" : "Connecting…";
}

// ── Polling ───────────────────────────────────────────────────────────────────

/**
 * Fetch events from the server API and render them.
 * 
 * Handles:
 * - HTTP requests to GET /events
 * - JSON parsing
 * - Event rendering
 * - Status indicator updates
 * - Error handling with user feedback
 */
async function fetchEvents() {
  try {
    // Request latest events from backend
    const res = await fetch("/events");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    
    // Render events and update status
    renderEvents(data);
    setStatus("live");
    lastUpdated.textContent = new Date().toLocaleTimeString();
  } catch (err) {
    console.error("Poll error:", err);
    setStatus("error");
  }
}

/**
 * Start a countdown timer showing seconds until next poll.
 * Updates the countdown display every second.
 */
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

/**
 * Execute one poll cycle: fetch events and start countdown.
 */
function poll() {
  fetchEvents();
  startCountdown();
}

// ── Initialize ───────────────────────────────────────────────────────────────
// Perform initial poll and set up interval for subsequent polls
poll();
pollTimer = setInterval(poll, POLL_INTERVAL * 1000);
