/* Rafiq UI logic — vanilla JS, no build step. */
"use strict";

const state = { employeeId: "E0421", lang: "en", journey: null, tab: "timeline" };
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

const I18N = {
  en: {
    day: "Day", stage: "Stage", blockers: "Open blockers", risk: "Friction risk",
    done: "done", upcoming: "upcoming", overdue: "overdue", na: "n/a",
    targetDay: "target day", owner: "owner", completed: "completed day",
    chase: "Chase it for me", chaseOwner: (o) => `Chase ${o}`, talkPerson: "Talk to a person",
    viewHandoff: "View handoff", journeyTitle: "Your journey timeline",
    dataTitle: "What we hold about you", auditTitle: "Everything Rafiq did for you",
    noticesTitle: "Proactive notices", none: "Nothing yet.",
    role: "Role", dept: "Department", journey: "Journey", reqs: "Service requests",
    pulseEntries: "Pulse entries (held)", pulseUsed: "Pulse used in signals",
    yes: "Yes", no: "No", notUsedFor: "Not used for", notUsedVal: "performance or discipline — ever",
    consentSaved: "Preference saved and logged.", sweeping: "Sweep running…",
    swept: (n, e) => `Sweep: ${n} new notice(s), ${e} escalation(s)`,
    sent: "Sent", lowConf: "Low confidence — routed to a human", handoff: "Handoff",
    action: "Action taken", grounded: "Grounded + cited", profile: "Profile",
    stageNow: (s, d) => `${s} · day ${d}`, noBlockers: "None — on track",
  },
  ar: {
    day: "اليوم", stage: "المرحلة", blockers: "عوائق مفتوحة", risk: "درجة التعثر",
    done: "منجز", upcoming: "قادم", overdue: "متأخر", na: "غير منطبق",
    targetDay: "اليوم المستهدف", owner: "المالك", completed: "أُنجز يوم",
    chase: "تابعها نيابة عني", chaseOwner: (o) => `تابع ${o}`, talkPerson: "تحدث إلى شخص",
    viewHandoff: "عرض الإحالة", journeyTitle: "الجدول الزمني لرحلتك",
    dataTitle: "ما نحتفظ به عنك", auditTitle: "كل ما قام به رفيق نيابة عنك",
    noticesTitle: "التنبيهات الاستباقية", none: "لا شيء بعد.",
    role: "الدور", dept: "القسم", journey: "الرحلة", reqs: "طلبات الخدمة",
    pulseEntries: "مدخلات النبض (محفوظة)", pulseUsed: "النبض يُستخدم في الإشارات",
    yes: "نعم", no: "لا", notUsedFor: "لا يُستخدم لـ", notUsedVal: "التقييم أو الانضباط — أبدًا",
    consentSaved: "تم الحفظ والتسجيل.", sweeping: "جارٍ الفحص…",
    swept: (n, e) => `الفحص: ${n} تنبيه جديد، ${e} تصعيد`,
    sent: "أُرسل", lowConf: "ثقة منخفضة — حُوِّل إلى شخص", handoff: "إحالة",
    action: "إجراء منفَّذ", grounded: "مُسنَد ومُوثَّق", profile: "الملف",
    stageNow: (s, d) => `${s} · اليوم ${d}`, noBlockers: "لا شيء — على المسار",
  },
};
const T = () => I18N[state.lang];

/* ---------------- api ---------------- */
async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}
const post = (path, body) => api(path, { method: "POST", body: JSON.stringify(body) });

/* ---------------- boot ---------------- */
async function boot() {
  await loadEmployees();
  await refreshAll();
  welcome();
}

async function loadEmployees() {
  const list = await api("/employees");
  const sel = $("#employee-select");
  sel.innerHTML = list.map((e) => `<option value="${e.employee_id}">${e.label}</option>`).join("");
  sel.value = state.employeeId;
  sel.addEventListener("change", async () => {
    state.employeeId = sel.value;
    $("#thread").innerHTML = "";
    await refreshAll();
    welcome();
  });
}

async function refreshAll() {
  state.journey = await api(`/journey/${state.employeeId}`);
  renderStage();
  renderPanel();
  refreshConsent();
  refreshNoticeBadge();
}

/* ---------------- stage card ---------------- */
const EVENT_LABELS_AR = {
  offer_accepted: "قبول العرض", documents_submitted: "تقديم المستندات",
  badge_building_access: "بطاقة الدخول للمبنى", it_account_created: "إنشاء حساب تقنية المعلومات",
  laptop_issued: "تسليم الحاسوب المحمول", first_manager_1on1: "أول لقاء مع المدير",
  induction_training_booked: "حجز التدريب التمهيدي", bank_wps_setup: "إعداد البنك ونظام حماية الأجور",
  health_insurance_enrolled: "التسجيل في التأمين الصحي", visa_entry_permit: "تصريح الدخول",
  medical_fitness_test: "اختبار اللياقة الطبية", emirates_id_application: "طلب الهوية الإماراتية",
  residence_visa_stamped: "إقلام تأشيرة الإقامة", probation_review_30: "تقييم الثلاثين يومًا",
  transfer_request_approved: "اعتماد طلب النقل", receiving_team_signoff: "موافقة الفريق المستقبل",
  release_from_current_team: "إطلاق الفريق الحالي", access_reprovisioned: "إعادة تجهيز الصلاحيات",
  new_location_ready: "جهوزية الموقع الجديد", first_1on1_new_team: "أول لقاء مع الفريق الجديد",
};
const eventLabel = (s) => (state.lang === "ar" && EVENT_LABELS_AR[s.event]) || s.label;

function renderStage() {
  const s = state.journey.state, t = T();
  $("#stage-value").textContent = t.stageNow(s.stage, s.day);
  $("#stage-meta").textContent = s.blockers.length
    ? `${t.blockers}: ${s.blockers.map((b) => eventLabel(b)).join(", ")}`
    : t.noBlockers;
}

/* ---------------- chat ---------------- */
function welcome() {
  const s = state.journey.state;
  if (!s.blockers.length) return;
  const b = s.blockers[0];
  pushRafiqHTML(`<div class="answer-text" dir="auto">${langPick(
    `Day ${s.day} check-in: “${esc(b.label)}” is ${b.days_overdue} day(s) overdue (target day ${b.due_day}).
     The owner is ${esc(b.owner.name)}. Want me to chase them for you?`,
    `يوم ${s.day}: «${esc(b.label)}» متأخر ${b.days_overdue} يوم (المستهدف يوم ${b.due_day}) والمالك ${esc(b.owner.name)}. أتابعه نيابة عنك؟`
  )}</div><div class="answer-actions"><button class="cta" data-chase="${esc(b.event)}" data-owner="${esc(b.owner.name)}">${T().chase}</button></div>`);
}

function langPick(en, ar) { return state.lang === "ar" ? ar : en; }
function esc(s) { return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

function pushUser(text) {
  const div = document.createElement("div");
  div.className = "bubble user";
  div.setAttribute("dir", "auto");
  div.textContent = text;
  $("#thread").appendChild(div);
  scrollThread();
}

function pushRafiqHTML(html) {
  const div = document.createElement("div");
  div.className = "answer-card";
  div.innerHTML = html;
  $("#thread").appendChild(div);
  $$("[data-chase]", div).forEach((b) => b.addEventListener("click", () => {
    pushUser(`${T().chase}`);
    send(`chase ${b.dataset.chase.replace(/_/g, " ")}`, { echo: false });
  }));
  $$("[data-cite]", div).forEach((chip) => chip.addEventListener("click", () => toggleSource(chip, div)));
  scrollThread();
  return div;
}

function pushTyping() {
  const div = document.createElement("div");
  div.className = "typing";
  div.textContent = "…";
  div.id = "typing";
  $("#thread").appendChild(div);
  scrollThread();
}
const unTyping = () => $("#typing")?.remove();
const scrollThread = () => { const el = $("#thread"); el.scrollTop = el.scrollHeight; };

async function send(msg, { echo = true } = {}) {
  if (!msg.trim()) return;
  if (echo) pushUser(msg);
  pushTyping();
  try {
    const resp = await post("/ask", { employee_id: state.employeeId, message: msg, lang: state.lang });
    unTyping();
    renderAnswer(resp);
    refreshNoticeBadge();
  } catch (e) {
    unTyping();
    pushRafiqHTML(`<div class="answer-text">${langPick("Something went wrong — please try again.",
      "حدث خطأ — أعد المحاولة من فضلك.")}</div>`);
  }
}

function confPill(resp) {
  const t = T();
  if (resp.kind === "handoff") return `<span class="pill handoff">${t.handoff}</span>`;
  if (resp.kind === "action") return `<span class="pill action">${t.action}</span>`;
  if (resp.kind === "journey") return `<span class="pill high">${t.grounded}</span>`;
  const c = resp.confidence;
  const cls = c >= 0.65 ? "high" : c >= 0.5 ? "med" : "low";
  return `<span class="pill ${cls}">${Math.round(c * 100)}%</span>`;
}

function renderAnswer(resp) {
  const t = T();
  const cites = (resp.citations || [])
    .map((c) => `<button class="cite-chip" data-cite="${esc(c.policy_id)}" data-open="0">§ ${esc(c.policy_id)}${c.section ? " · " + esc(c.section) : ""}</button>`)
    .join("");
  const handoff = resp.handoff_id
    ? `<button class="cta secondary" data-handoff="${esc(resp.handoff_id)}">${t.viewHandoff} ${esc(resp.handoff_id)}</button>` : "";
  const card = pushRafiqHTML(`
    <div class="answer-meta">${confPill(resp)} ${cites}</div>
    <div class="answer-text" dir="auto">${esc(resp.answer)}</div>
    ${handoff}
    <div class="src-box" hidden></div>`);
  $$("[data-handoff]", card).forEach((b) => b.addEventListener("click", () => showHandoff(b.dataset.handoff)));
}

async function toggleSource(chip, card) {
  const box = $(".src-box", card);
  if (box.hidden === false) { box.hidden = true; return; }
  if (box.dataset.loaded !== "1") {
    const pid = chip.dataset.cite;
    const sections = await api(`/policy/${pid}?lang=${state.lang}`).catch(() => []);
    box.innerHTML = sections.map((s) => `<h4>${esc(s.title)} — ${esc(s.section)}</h4><div>${esc(s.text)}</div>`).join("")
      || `<div>${T().none}</div>`;
    box.dataset.loaded = "1";
  }
  box.hidden = false;
}

async function showHandoff(id) {
  const c = await api(`/handoff/${id}`);
  pushRafiqHTML(`<div class="answer-text" dir="auto"><b>${T().handoff} ${esc(c.handoff_id)}</b>
${langPick("Owner:", "المالك:")} ${esc(c.suggested_owner.name)}
${langPick("Blocker:", "العائق:")} ${esc(c.blocker)}
${langPick("Tried:", "ما جُرِّب:")} ${esc((c.tried || []).join(" · "))}
${esc(c.summary)}</div>`);
}

/* ---------------- panels ---------------- */
function renderPanel() {
  if (state.tab === "timeline") return renderTimeline();
  if (state.tab === "data") return renderData();
  if (state.tab === "audit") return renderAudit();
  return renderNotices();
}

function renderTimeline() {
  const t = T();
  const steps = state.journey.timeline.map((s) => `
    <div class="tl-step">
      <div class="dot ${s.status}">${s.status === "done" ? "✓" : s.status === "overdue" ? "!" : s.status === "na" ? "–" : ""}</div>
      <div class="tl-main">
        <div class="tl-title" dir="auto">${esc(eventLabel(s))} <span class="tl-status ${s.status}">${t[s.status]}</span></div>
        <div class="tl-meta">${t.targetDay}: ${s.target_day} · ${t.owner}: ${esc(s.owner)}
          ${s.status === "done" ? `· ${t.completed}: ${s.completed_day}` : ""}
          ${s.status === "overdue" ? `· <b>+${s.days_overdue} ${t.overdue}</b>` : ""}</div>
        ${s.status === "overdue" ? `<div class="tl-chase"><button class="cta" data-chase="${esc(s.event)}" data-owner="${esc(s.owner)}">${t.chaseOwner(esc(s.owner))}</button></div>` : ""}
      </div>
    </div>`).join("");
  $("#panel").innerHTML = `<h3>${t.journeyTitle}</h3><div class="tl">${steps}</div>`;
  bindChaseButtons();
}

async function renderData() {
  const t = T();
  const d = await api(`/me/data?employee_id=${state.employeeId}`);
  const kv = (k, v) => `<div class="kv-row"><span class="kv-key">${k}</span><span class="kv-val">${v}</span></div>`;
  $("#panel").innerHTML = `<h3>${t.dataTitle}</h3>
    <div class="kv">
      ${kv(t.profile, esc(d.employee?.name || ""))}
      ${kv(t.role, esc(d.employee?.role || ""))}
      ${kv(t.dept, esc(d.employee?.department || ""))}
      ${kv(t.journey, esc(d.employee?.journey || ""))}
      ${kv(t.stage, esc(d.journey.stage))}
      ${kv(t.day, d.journey.day)}
      ${kv(t.reqs, d.service_requests)}
      ${kv(t.pulseEntries, d.pulse_entries)}
      ${kv(t.pulseUsed, d.pulse_used_for_signals ? t.yes : t.no)}
      ${kv(t.notUsedFor, t.notUsedVal)}
    </div>
    <div class="note ${d.pulse_used_for_signals ? "" : "warn"}">${esc(d.pulse_note)}</div>`;
}

async function renderAudit() {
  const t = T();
  const rows = await api(`/me/audit?employee_id=${state.employeeId}`);
  $("#panel").innerHTML = `<h3>${t.auditTitle}</h3>` + (rows.length ? rows.map((r) => `
    <div class="audit-row">
      <span class="audit-action">${esc(r.action.replaceAll("_", " "))}</span>
      <span class="audit-detail">${esc(JSON.stringify(r.detail || {}))}</span>
      <span class="audit-ts">${esc((r.ts || "").replace("T", " ").slice(0, 19))} UTC</span>
    </div>`).join("") : `<div class="note">${t.none}</div>`);
}

async function renderNotices() {
  const t = T();
  const rows = await api(`/me/notices?employee_id=${state.employeeId}`);
  $("#panel").innerHTML = `<h3>${t.noticesTitle}</h3>` + (rows.length ? rows.map((n) => `
    <div class="notice-row ${esc(n.kind)}">
      <div class="notice-title">${esc(n.title)}</div>
      <div class="notice-detail">${esc(n.detail)}</div>
    </div>`).join("") : `<div class="note">${t.none}</div>`);
  refreshNoticeBadge();
}

function bindChaseButtons() {
  $$("[data-chase]", $("#panel")).forEach((b) => b.addEventListener("click", () => {
    pushUser(T().chase);
    send(`chase ${b.dataset.chase.replace(/_/g, " ")}`, { echo: false });
  }));
}

/* ---------------- tabs, consent, sweep, language ---------------- */
$$("#rail-tabs .tab").forEach((tab) => tab.addEventListener("click", () => {
  $$("#rail-tabs .tab").forEach((x) => x.classList.remove("is-active"));
  tab.classList.add("is-active");
  state.tab = tab.dataset.tab;
  renderPanel();
}));

async function refreshConsent() {
  const d = await api(`/me/data?employee_id=${state.employeeId}`).catch(() => null);
  $("#consent-toggle").checked = !!(d && d.consent && d.consent.pulse);
}
$("#consent-toggle").addEventListener("change", async (e) => {
  const r = await post("/consent", { employee_id: state.employeeId, consent_pulse: e.target.checked });
  toast(r.message);
});

$("#sweep-btn").addEventListener("click", async () => {
  toast(T().sweeping);
  const r = await post("/sweep", {});
  toast(T().swept(r.notices_new, r.escalations));
  refreshAll();
  if (state.tab === "notices") renderNotices();
});

function refreshNoticeBadge() {
  api(`/me/notices?employee_id=${state.employeeId}`).then((rows) => {
    const badge = $("#notice-badge");
    badge.hidden = !rows.length;
    badge.textContent = rows.length;
  }).catch(() => {});
}

function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.hidden = true; }, 3200);
}

function applyLang() {
  document.documentElement.lang = state.lang;
  document.documentElement.dir = state.lang === "ar" ? "rtl" : "ltr";
  $$(".lang-opt").forEach((o) => o.classList.toggle("is-active", o.dataset.lang === state.lang));
  $("#lang-toggle").setAttribute("aria-checked", state.lang === "ar");
  const input = $("#msg-input");
  input.placeholder = input.getAttribute(`placeholder-${state.lang}`);
  renderStage();
  renderPanel();
}

$("#lang-toggle").addEventListener("click", () => {
  state.lang = state.lang === "en" ? "ar" : "en";
  applyLang();
});
$("#lang-toggle").addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("#lang-toggle").click(); }
});

/* ---------------- composer ---------------- */
$("#composer").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = $("#msg-input");
  send(input.value);
  input.value = "";
});
$$("#chips .chip").forEach((c) => c.addEventListener("click", () => send(c.dataset.msg)));

boot();
