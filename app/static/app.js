/* Rafiq UI logic — hash-routed screens, vanilla JS, no build step. */
"use strict";

const state = {
  employeeId: "E0421", lang: "en", journey: null,
  employees: [], screen: "home",
};
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

const I18N = {
  en: {
    day: "Day", stage: "Stage", blockers: "Open blockers",
    done: "done", upcoming: "upcoming", overdue: "overdue", na: "n/a",
    targetDay: "target day", owner: "owner", completed: "completed day",
    chase: "Chase it for me", chaseOwner: (o) => `Chase ${o}`,
    viewHandoff: "View handoff", journeyTitle: "Your journey timeline",
    dataTitle: "What we hold about you", auditTitle: "Everything Rafiq did for you",
    noticesTitle: "Proactive notices", none: "Nothing yet.",
    role: "Role", dept: "Department", journey: "Journey", reqs: "Service requests",
    pulseEntries: "Pulse entries (held)", pulseUsed: "Pulse used in signals",
    yes: "Yes", no: "No", notUsedFor: "Not used for", notUsedVal: "performance or discipline — ever",
    consent: "Pulse consent", consentSaved: "Preference saved and logged.",
    sweeping: "Sweep running…", swept: (n, e) => `Sweep: ${n} new notice(s), ${e} escalation(s)`,
    lowConf: "Low confidence — routed to a human", handoff: "Handoff",
    action: "Action taken", grounded: "Grounded + cited", profile: "Profile",
    stageNow: (s, d) => `${s} · day ${d}`, noBlockers: "None — on track",
    risk: "Friction risk", journeyStage: "Journey stage",
  },
  ar: {
    day: "اليوم", stage: "المرحلة", blockers: "عوائق مفتوحة",
    done: "منجز", upcoming: "قادم", overdue: "متأخر", na: "غير منطبق",
    targetDay: "اليوم المستهدف", owner: "المالك", completed: "أُنجز يوم",
    chase: "تابعها نيابة عني", chaseOwner: (o) => `تابع ${o}`,
    viewHandoff: "عرض الإحالة", journeyTitle: "الجدول الزمني لرحلتك",
    dataTitle: "ما نحتفظ به عنك", auditTitle: "كل ما قام به رفيق نيابة عنك",
    noticesTitle: "التنبيهات الاستباقية", none: "لا شيء بعد.",
    role: "الدور", dept: "القسم", journey: "الرحلة", reqs: "طلبات الخدمة",
    pulseEntries: "مدخلات النبض (محفوظة)", pulseUsed: "النبض يُستخدم في الإشارات",
    yes: "نعم", no: "لا", notUsedFor: "لا يُستخدم لـ", notUsedVal: "التقييم أو الانضباط — أبدًا",
    consent: "موافقة نبضات الرأي", consentSaved: "تم الحفظ والتسجيل.",
    sweeping: "جارٍ الفحص…", swept: (n, e) => `الفحص: ${n} تنبيه جديد، ${e} تصعيد`,
    lowConf: "ثقة منخفضة — حُوِّل إلى شخص", handoff: "إحالة",
    action: "إجراء منفَّذ", grounded: "مُسنَد ومُوثَّق", profile: "الملف",
    stageNow: (s, d) => `${s} · اليوم ${d}`, noBlockers: "لا شيء — على المسار",
    risk: "درجة التعثر", journeyStage: "مرحلة الرحلة",
  },
};
const T = () => I18N[state.lang];

const EVENT_LABELS_AR = {
  offer_accepted: "قبول العرض", documents_submitted: "تقديم المستندات",
  photo_shared: "تقديم الأوراق والصورة",
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
const EVENT_HINTS_AR = {
  medical_fitness_test: "يمكن إنجازها مبكرًا — غالبًا في زيارة نافذة التأشيرة",
  emirates_id_application: "البصمة عادةً في الزيارة نفسها التي يجري فيها الفحص الطبي",
};
const eventLabel = (s) => (state.lang === "ar" && EVENT_LABELS_AR[s.event]) || s.label;
const eventNote = (s) => (state.lang === "ar" ? EVENT_HINTS_AR[s.event] : s.note) || "";
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const langPick = (en, ar) => (state.lang === "ar" ? ar : en);

/* ---------------- api ---------------- */
async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!r.ok) throw new Error(`${r.status}`);
  return r.json();
}
const post = (path, body) => api(path, { method: "POST", body: JSON.stringify(body) });

/* ---------------- boot + router ---------------- */
async function boot() {
  state.employees = await api("/employees");
  buildViewAs();
  await refreshJourney();
  route();
}

async function refreshJourney() {
  state.journey = await api(`/journey/${state.employeeId}`);
  const emp = state.employees.find((e) => e.employee_id === state.employeeId);
  $("#viewas-current").textContent = emp ? emp.employee_id : state.employeeId;
  refreshNoticeBadge();
}

function route() {
  const name = (location.hash.replace(/^#\//, "") || "home").split("?")[0];
  const known = ["home", "chat", "journey", "me", "audit", "notices"];
  state.screen = known.includes(name) ? name : "home";
  $$(".screen").forEach((s) => s.classList.remove("is-active"));
  $(`#screen-${state.screen}`).classList.add("is-active");
  $$("#nav .nav-pill").forEach((p) => p.classList.toggle("is-active", p.dataset.screen === state.screen));
  renderScreen();
  if (state.screen === "chat" && !$("#thread").children.length) welcome();
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);

async function renderScreen() {
  if (state.screen === "home") await renderHome();
  if (state.screen === "journey") renderJourney();
  if (state.screen === "me") await renderMe();
  if (state.screen === "audit") await renderAudit();
  if (state.screen === "notices") await renderNotices();
  if (state.screen === "chat") applyLangInput();
}

/* ---------------- view as ---------------- */
function buildViewAs() {
  const menu = $("#viewas-menu");
  menu.innerHTML = state.employees.map((e) => `
    <button class="viewas-item ${e.employee_id === state.employeeId ? "is-current" : ""}"
            data-emp="${esc(e.employee_id)}">
      <span>${esc(e.label)}</span>
    </button>`).join("");
  $$(".viewas-item", menu).forEach((b) => b.addEventListener("click", async () => {
    state.employeeId = b.dataset.emp;
    $("#viewas-menu").hidden = true;
    $("#thread").innerHTML = "";
    await refreshJourney();
    route();
    if (state.screen === "chat") welcome();
  }));
}
$("#viewas-btn").addEventListener("click", () => {
  $("#viewas-menu").hidden = !$("#viewas-menu").hidden;
});
document.addEventListener("click", (e) => {
  if (!$("#viewas").contains(e.target)) $("#viewas-menu").hidden = true;
});

/* ---------------- home ---------------- */
async function renderHome() {
  const s = state.journey.state, t = T();
  const emp = state.employees.find((e) => e.employee_id === state.employeeId);
  $("#home-greet").textContent =
    `${emp ? emp.label.split("· ").slice(1).join("· ") : s.employee_id} — ${t.stageNow(s.stage, s.day)}`;
  $("#home-greet-ar").textContent =
    `${emp ? emp.label.split("· ").slice(1).join("· ") : s.employee_id} — ${t.stageNow(s.stage, s.day)}`;
  $("#home-stage").innerHTML = `
    <div class="stage-label">${t.journeyStage}</div>
    <div class="stage-value">${t.stageNow(s.stage, s.day)}</div>
    <div class="stage-meta">${s.blockers.length ? `${t.blockers}: ${s.blockers.map((b) => esc(eventLabel(b))).join(", ")}` : t.noBlockers}</div>
    <a class="ghost-link" href="#/journey">${langPick("Open timeline →", "افتح الجدول الزمني ←")}</a>`;

  const first = s.blockers[0];
  $("#home-blocker").innerHTML = first ? `
    <h3>${langPick("Needs your attention", "يحتاج انتباهك")}</h3>
    <div class="blocker-line"><b dir="auto">${esc(eventLabel(first))}</b>
      <span class="tl-status overdue">${t.overdue}</span></div>
    <p>${langPick(`Due day ${first.due_day} — ${first.days_overdue} day(s) overdue. Owner: ${esc(first.owner.name)}.`,
                  `كان مستحقًا يوم ${first.due_day} — متأخر ${first.days_overdue} يوم. المالك: ${esc(first.owner.name)}.`)}</p>
    <button class="cta" data-chase="${esc(first.event)}">${t.chase}</button>
    <a class="ghost-link" href="#/notices">${langPick("All notices →", "كل التنبيهات ←")}</a>`
    : `<h3>${langPick("All clear", "كل شيء على المسار")}</h3>
       <p>${langPick("No blockers on your journey today. Notices will appear here if that changes.",
                     "لا عوائق في رحلتك اليوم. ستظهر التنبيهات هنا إذا تغيّر ذلك.")}
       </p><a class="ghost-link" href="#/notices">${langPick("All notices →", "كل التنبيهات ←")}</a>`;
  bindChaseButtons($("#home-blocker"));
}

function bindChaseButtons(scope) {
  $$("[data-chase]", scope || document).forEach((b) => b.addEventListener("click", () => {
    location.hash = "#/chat";
    pushUser(T().chase);
    send(`chase ${b.dataset.chase.replace(/_/g, " ")}`, { echo: false });
  }));
}

/* ---------------- journey ---------------- */
function renderJourney() {
  const t = T();
  const steps = state.journey.timeline.map((s) => `
    <div class="tl-step">
      <div class="dot ${s.status}">${s.status === "done" ? "✓" : s.status === "overdue" ? "!" : s.status === "na" ? "–" : ""}</div>
      <div class="tl-main">
        <div class="tl-title" dir="auto">${esc(eventLabel(s))} <span class="tl-status ${s.status}">${t[s.status]}</span></div>
        <div class="tl-meta">${t.targetDay}: ${s.target_day} · ${t.owner}: ${esc(s.owner)}
          ${s.status === "done" ? `· ${t.completed}: ${s.completed_day}` : ""}
          ${s.status === "overdue" ? `· <b>+${s.days_overdue} ${t.overdue}</b>` : ""}</div>
        ${s.note && s.status === "upcoming" ? `<div class="tl-note">${esc(eventNote(s))}</div>` : ""}
        ${s.status === "overdue" ? `<div class="tl-chase"><button class="cta" data-chase="${esc(s.event)}">${t.chaseOwner(esc(s.owner))}</button></div>` : ""}
      </div>
    </div>`).join("");
  $("#journey-card").innerHTML = `<h3>${t.journeyTitle}</h3><div class="tl">${steps}</div>`;
  bindChaseButtons($("#journey-card"));
}

/* ---------------- my data ---------------- */
async function renderMe() {
  const t = T();
  const d = await api(`/me/data?employee_id=${state.employeeId}`);
  const consented = d.consent && d.consent.pulse;
  const kv = (k, v) => `<div class="kv-row"><span class="kv-key">${k}</span><span class="kv-val" dir="auto">${v}</span></div>`;
  $("#me-card").innerHTML = `<h3>${t.dataTitle}</h3>
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
    <div class="consent-row">
      <span>${t.consent}</span>
      <label class="switch"><input type="checkbox" id="consent-toggle" ${consented ? "checked" : ""}><span class="slider"></span></label>
    </div>
    <div class="note ${consented ? "" : "warn"}">${esc(d.pulse_note)}</div>`;
  $("#consent-toggle").addEventListener("change", async (e) => {
    const r = await post("/consent", { employee_id: state.employeeId, consent_pulse: e.target.checked });
    toast(r.message);
    renderMe();
  });
}

/* ---------------- audit + notices ---------------- */
async function renderAudit() {
  const t = T();
  const rows = await api(`/me/audit?employee_id=${state.employeeId}`);
  $("#audit-card").innerHTML = `<h3>${t.auditTitle}</h3>` + (rows.length ? rows.map((r) => `
    <div class="audit-row">
      <span class="audit-action">${esc(r.action.replaceAll("_", " "))}</span>
      <span class="audit-detail" dir="auto">${esc(JSON.stringify(r.detail || {}))}</span>
      <span class="audit-ts">${esc((r.ts || "").replace("T", " ").slice(0, 19))} UTC</span>
    </div>`).join("") : `<div class="note">${t.none}</div>`);
}

async function renderNotices() {
  const t = T();
  const rows = await api(`/me/notices?employee_id=${state.employeeId}`);
  $("#notices-card").innerHTML = `<h3>${t.noticesTitle}</h3>` + (rows.length ? rows.map((n) => `
    <div class="notice-row ${esc(n.kind)}">
      <div class="notice-title" dir="auto">${esc(n.title)}</div>
      <div class="notice-detail" dir="auto">${esc(n.detail)}</div>
    </div>`).join("") : `<div class="note">${t.none}</div>`);
  refreshNoticeBadge();
}

function refreshNoticeBadge() {
  api(`/me/notices?employee_id=${state.employeeId}`).then((rows) => {
    const badge = $("#notice-badge");
    badge.hidden = !rows.length;
    badge.textContent = rows.length;
  }).catch(() => {});
}

/* ---------------- chat ---------------- */
function welcome() {
  const s = state.journey.state;
  if (!s.blockers.length) return;
  const b = s.blockers[0];
  pushRafiqHTML(`<div class="answer-text" dir="auto">${langPick(
    `Day ${s.day} check-in: “${esc(eventLabel(b))}” is ${b.days_overdue} day(s) overdue (target day ${b.due_day}).
     The owner is ${esc(b.owner.name)}. Want me to chase them for you?`,
    `يوم ${s.day}: «${esc(eventLabel(b))}» متأخر ${b.days_overdue} يوم (المستهدف يوم ${b.due_day}) والمالك ${esc(b.owner.name)}. أتابعه نيابة عنك؟`
  )}</div><div class="answer-actions"><button class="cta" data-chase="${esc(b.event)}">${T().chase}</button></div>`);
}

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
    pushUser(T().chase);
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
    .map((c) => `<button class="cite-chip" data-cite="${esc(c.policy_id)}">§ ${esc(c.policy_id)}${c.section ? " · " + esc(c.section) : ""}</button>`)
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
    box.innerHTML = sections.map((s) => `<h4 dir="auto">${esc(s.title)} — ${esc(s.section)}</h4><div dir="auto">${esc(s.text)}</div>`).join("")
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

$("#composer").addEventListener("submit", (e) => {
  e.preventDefault();
  const input = $("#msg-input");
  send(input.value);
  input.value = "";
});
$$("#chips .chip").forEach((c) => c.addEventListener("click", () => send(c.dataset.msg)));

/* ---------------- sweep + language ---------------- */
$("#sweep-btn").addEventListener("click", async () => {
  toast(T().sweeping);
  const r = await post("/sweep", {});
  toast(T().swept(r.notices_new, r.escalations));
  await refreshJourney();
  renderScreen();
});

function applyLangInput() {
  const input = $("#msg-input");
  input.placeholder = input.getAttribute(`placeholder-${state.lang}`);
}

function applyLang() {
  document.documentElement.lang = state.lang;
  document.documentElement.dir = state.lang === "ar" ? "rtl" : "ltr";
  $$(".lang-opt").forEach((o) => o.classList.toggle("is-active", o.dataset.lang === state.lang));
  $("#lang-toggle").setAttribute("aria-checked", state.lang === "ar");
  applyLangInput();
  renderScreen();
}

$("#lang-toggle").addEventListener("click", () => {
  state.lang = state.lang === "en" ? "ar" : "en";
  applyLang();
});
$("#lang-toggle").addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("#lang-toggle").click(); }
});

function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.hidden = true; }, 3200);
}

boot();
