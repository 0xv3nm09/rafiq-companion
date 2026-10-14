/* Rafiq UI logic — hash-routed screens, vanilla JS, no build step. */
"use strict";

const state = {
  employeeId: "E0421", lang: "en", journey: null,
  employees: [], viewRole: "employee", personaId: null, persona: null,
  managers: [], hrbps: [], owners: [],
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

const SCREENS = {
  employee: ["home", "chat", "journey", "me", "audit", "notices", "stalls"],
  manager: ["team", "stalls"],
  hrbp: ["queue", "handoffs", "stalls"],
  owner: ["handoffs"],
};

/* ---------------- boot + router ---------------- */
async function boot() {
  [state.employees, state.managers, state.hrbps, state.owners] = await Promise.all([
    api("/employees"), api("/people/managers"), api("/people/hrbps"), api("/people/owners"),
  ]);
  buildViewAs();
  buildNav();
  await refreshJourney();
  route();
}

function buildNav() {
  const labels = {
    home: ["Home", "الرئيسية"], chat: ["Chat", "المحادثة"], journey: ["Journey", "الرحلة"],
    me: ["My data", "بياناتي"], audit: ["Audit log", "سجل النشاط"],
    notices: ["Notices", "التنبيهات"], team: ["Team", "الفريق"],
    queue: ["Early-warning queue", "قائمة الإنذار المبكر"], handoffs: ["Handoffs", "الإحالات"],
    stalls: ["Where journeys stall", "أكثر مواضع التعثر"],
  };
  $("#nav").innerHTML = SCREENS[state.viewRole].map((s) => {
    const badge = s === "notices" ? '<span class="badge" id="notice-badge" hidden></span>' : "";
    return `<a class="nav-pill" href="#/${s}" data-screen="${s}">${langPick(labels[s][0], labels[s][1])}${badge}</a>`;
  }).join("");
}

async function refreshJourney() {
  if (state.viewRole !== "employee") return;
  state.journey = await api(`/journey/${state.employeeId}`);
  const emp = state.employees.find((e) => e.employee_id === state.employeeId);
  $("#viewas-current").textContent = emp ? emp.employee_id : state.employeeId;
  refreshNoticeBadge();
}

function route() {
  const name = (location.hash.replace(/^#\//, "") || "home").split("?")[0];
  const known = SCREENS[state.viewRole];
  state.screen = known.includes(name) ? name : known[0];
  $$(".screen").forEach((s) => s.classList.remove("is-active"));
  $(`#screen-${state.screen}`).classList.add("is-active");
  $$("#nav .nav-pill").forEach((p) => p.classList.toggle("is-active", p.dataset.screen === state.screen));
  renderScreen();
  if (state.screen === "chat" && !$("#thread").children.length) welcome();
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);

async function renderScreen() {
  if (state.viewRole === "manager") return renderTeam();
  if (state.viewRole === "hrbp") {
    if (state.screen === "queue") return renderQueue();
    return renderHandoffs();
  }
  if (state.viewRole === "owner") return renderHandoffs();
  if (state.screen === "home") await renderHome();
  if (state.screen === "journey") renderJourney();
  if (state.screen === "me") await renderMe();
  if (state.screen === "audit") await renderAudit();
  if (state.screen === "notices") await renderNotices();
  if (state.screen === "stalls") await renderStalls();
  if (state.screen === "chat") applyLangInput();
}

/* ---------------- view as (employees, managers, HR & owners) ---------------- */
function buildViewAs() {
  const menu = $("#viewas-menu");
  const empItems = state.employees.map((e) => `
    <button class="viewas-item ${state.viewRole === "employee" && e.employee_id === state.employeeId ? "is-current" : ""}"
            data-role="employee" data-emp="${esc(e.employee_id)}" data-text="${esc(e.label.toLowerCase())}"><span>${esc(e.label)}</span></button>`).join("");
  const mgrItems = state.managers.map((m) => `
    <button class="viewas-item ${state.viewRole === "manager" && m.id === state.personaId ? "is-current" : ""}"
            data-role="manager" data-emp="${esc(m.id)}" data-text="${esc(m.name.toLowerCase())} ${esc(m.department.toLowerCase())}">
      <span>${esc(m.name)} · ${esc(m.department)} — team of ${m.team_size}</span></button>`).join("");
  const hrItems = state.hrbps.map((h) => `
    <button class="viewas-item ${state.viewRole === "hrbp" && h.id === state.personaId ? "is-current" : ""}"
            data-role="hrbp" data-emp="${esc(h.id)}" data-text="${esc(h.name.toLowerCase())}">
      <span>${esc(h.name)} · HRBP — caseload ${h.caseload}</span></button>`).join("")
    + state.owners.map((o) => `
    <button class="viewas-item ${state.viewRole === "owner" && o.name === state.personaId ? "is-current" : ""}"
            data-role="owner" data-emp="${esc(o.name)}" data-text="${esc(o.name.toLowerCase())}">
      <span>${esc(o.name)} · service owner</span></button>`).join("");
  menu.innerHTML = `
    <input class="viewas-search" id="viewas-search" type="search"
           placeholder-en="Search people…" placeholder-ar="ابحث عن شخص…">
    <div id="viewas-list">
    <div class="viewas-section t-en">Employees</div><div class="viewas-section t-ar">الموظفون</div>
    ${empItems}
    <div class="viewas-section t-en">Line managers</div><div class="viewas-section t-ar">المديرون المباشرون</div>
    ${mgrItems}
    <div class="viewas-section t-en">HR & service owners</div><div class="viewas-section t-ar">الموارد البشرية ومالكو الخدمة</div>
    ${hrItems}
    </div>`;
  $("#viewas-search").addEventListener("input", (e) => {
    const q = e.target.value.trim().toLowerCase();
    $$(".viewas-item", menu).forEach((b) => {
      b.style.display = !q || b.dataset.text.includes(q) ? "" : "none";
    });
  });
  $$(".viewas-item", menu).forEach((b) => b.addEventListener("click", async () => {
    state.viewRole = b.dataset.role;
    state.personaId = b.dataset.emp;
    $("#viewas-menu").hidden = true;
    $("#thread").innerHTML = "";
    await refreshJourney();
    if (state.viewRole !== "employee") {
      state.persona = state.managers.find((m) => m.id === state.personaId)
        || state.hrbps.find((h) => h.id === state.personaId)
        || state.owners.find((o) => o.name === state.personaId);
      $("#viewas-current").textContent = state.persona ? (state.persona.name || state.personaId) : state.personaId;
    }
    buildNav();
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

/* ---------------- persona dashboards (manager / HRBP / service owner) ---------------- */
const riskPill = (r) => `<span class="pill ${r >= 0.5 ? "low" : r >= 0.25 ? "med" : "high"}">${Math.round(r * 100)}%</span>`;

async function renderTeam() {
  const d = await api(`/team/${state.personaId}`);
  window.__teamData = d;
  $("#team-card").innerHTML = `
    <h3>${langPick("Team", "الفريق")} — ${esc(d.manager.name)} · ${esc(d.manager.department)} (${d.team_size})</h3>
    <div class="chips-row">
      ${["all", "blocked", "ontrack"].map((f) =>
        `<button class="chip filter" data-filter="${f}">${langPick(
          { all: "All", blocked: "Blocked", ontrack: "On track" }[f],
          { all: "الكل", blocked: "متعثرون", ontrack: "على المسار" }[f])}</button>`).join("")}
    </div>
    <div class="note">${langPick("Read-only help, not surveillance: blockers shown are journey facts.",
      "مساعدة للقراءة فقط وليست مراقبة: العوائق المعروضة حقائق رحلة.")}</div>
    <div class="note warn">${esc(d.privacy)}</div>
    <div class="person-list" id="team-list"></div>`;
  const draw = (f) => {
    const rows = d.reports
      .filter((r) => f === "all" || (f === "blocked" ? r.blockers.length : !r.blockers.length))
      .map((r) => `
        <div class="person-row">
          <div class="person-main">
            <span class="person-name" dir="auto">${esc(r.name)}</span>
            <span class="person-sub">${esc(r.role)} · ${esc(r.journey)} · ${t_day(r.day)}</span>
            ${r.blockers.length ? r.blockers.map((b) => `
              <div class="person-blocker"><b dir="auto">${esc(b.label)}</b>
                <span class="tl-status overdue">+${b.days_overdue} ${T().overdue}</span>
                <span class="person-owner">${T().owner}: ${esc(b.owner)}</span></div>`).join("")
              : `<div class="person-blocker ok">${langPick("On track", "على المسار الصحيح")}</div>`}
          </div>
          ${riskPill(r.risk)}
        </div>`).join("");
    $("#team-list").innerHTML = rows || `<div class="note">${T().none}</div>`;
  };
  $$("#team-card .chip.filter").forEach((c) => c.addEventListener("click", () => {
    $$("#team-card .chip.filter").forEach((x) => x.classList.remove("is-active"));
    c.classList.add("is-active");
    draw(c.dataset.filter);
  }));
  $("#team-card .chip.filter").classList.add("is-active");
  draw("all");
}
const t_day = (n) => langPick(`day ${n}`, `اليوم ${n}`);

async function renderQueue() {
  const d = await api(`/queue/${state.personaId}`);
  window.__queueData = d;
  const strip = Object.entries(d.stalls_by_owner).map(([o, n]) =>
    `<span class="chip static">${esc(o)} × ${n}</span>`).join("");
  $("#queue-card").innerHTML = `
    <h3>${langPick("Early-warning queue", "قائمة الإنذار المبكر")} — ${esc(d.hrbp.name)}</h3>
    <div class="kv-strip"><b>${d.blocked_total}/${d.caseload}</b> ${langPick("people blocked", "أشخاص متعثرون")}</div>
    <div class="chips-row">${strip}</div>
    <div class="chips-row">
      ${["all", "onboarding", "mobility"].map((f) =>
        `<button class="chip filter" data-filter="${f}">${langPick(
          { all: "All", onboarding: "Onboarding", mobility: "Mobility" }[f],
          { all: "الكل", onboarding: "انضمام", mobility: "تنقل" }[f])}</button>`).join("")}
    </div>
    <div class="note">${langPick("Only real stalls land here — the employee always saw theirs first.",
      "التعثرات الحقيقية فقط تصل هنا — الموظف رأى تعثره أولًا دائمًا.")}</div>
    <div class="person-list" id="queue-list"></div>`;
  const draw = (f) => {
    const rows = d.flagged
      .filter((x) => f === "all" || x.journey === f)
      .map((x) => `
        <div class="person-row">
          <div class="person-main">
            <span class="person-name" dir="auto">${esc(x.name)}</span>
            <span class="person-sub">${esc(x.journey)} · ${t_day(x.day)} · ${T().risk} ${Math.round(x.risk * 100)}%</span>
            ${x.blockers.map((b) => `
              <div class="person-blocker"><b dir="auto">${esc(b.label)}</b>
                <span class="tl-status overdue">+${b.days_overdue} ${T().overdue}</span>
                <span class="person-owner">${T().owner}: ${esc(b.owner)}</span></div>`).join("")}
            <div class="person-blocker ok">${x.employee_notified
              ? langPick("✓ Employee notified first (companion)", "✓ تم تنبيه الموظف أولًا (الرفيق)")
              : langPick("Not yet notified", "لم يتم التنبيه بعد")}</div>
          </div>
          <div class="person-side">${x.open_handoff_id
            ? `<button class="cta secondary" data-open-handoff="${esc(x.open_handoff_id)}">${T().viewHandoff}</button>`
            : ""}</div>
        </div>`).join("");
    $("#queue-list").innerHTML = rows || `<div class="note">${T().none}</div>`;
    $$("[data-open-handoff]", $("#queue-list")).forEach((b) =>
      b.addEventListener("click", () => expandHandoff(b.dataset.openHandoff)));
  };
  $$("#queue-card .chip.filter").forEach((c) => c.addEventListener("click", () => {
    $$("#queue-card .chip.filter").forEach((x) => x.classList.remove("is-active"));
    c.classList.add("is-active");
    draw(c.dataset.filter);
  }));
  $("#queue-card .chip.filter").classList.add("is-active");
  draw("all");
}

async function renderStalls() {
  const d = await api("/stalls");
  const max = Math.max(1, ...d.by_stage.map((x) => x.count));
  const bars = d.by_stage.map((x) => `
    <div class="bar-row">
      <span class="bar-label" dir="auto">${esc(x.label || x.event.replace(/_/g, " "))}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.round(x.count / max * 100)}%"></div></div>
      <span class="bar-count">${x.count}</span>
    </div>`).join("");
  const owners = d.by_owner.map((x) => `<span class="chip static">${esc(x.owner)} × ${x.count}</span>`).join("");
  const reqs = d.overdue_requests_by_type.map((x) =>
    `<span class="chip static">${esc(x.type)} × ${x.count}</span>`).join("");
  $("#stalls-card").innerHTML = `
    <h3>${langPick("Where journeys stall most", "أكثر مواضع التعثر في الرحلات")}</h3>
    <div class="kv-strip"><b>${d.blocked_total}/${d.journeys_scanned}</b>
      ${langPick("journeys currently blocked", "رحلة متعثرة حاليًا")}</div>
    <div class="bars">${bars}</div>
    <h3 class="sub">${langPick("Stalls by named owner", "التعثرات حسب المالك")}</h3>
    <div class="chips-row">${owners}</div>
    <h3 class="sub">${langPick("Overdue requests by type", "الطلبات المتأخرة حسب النوع")}</h3>
    <div class="chips-row">${reqs || `<span class="chip static">${T().none}</span>`}</div>
    <div class="note">${langPick("Aggregate only — never an individual. This is where the organization should fix the process, not the person.",
      "بيانات مجمعة فقط — لا فرد أبدًا. هنا يجب أن تصلح المنظمة العملية لا الشخص.")}</div>`;
}

async function renderHandoffs() {
  const all = await api("/handoffs");
  const mine = state.viewRole === "owner"
    ? all.filter((c) => c.suggested_owner.name === state.personaId)
    : all;
  const t = T();
  $("#handoffs-card").innerHTML = `
    <h3>${langPick("Handoff inbox", "صندوق الإحالات")}${state.persona ? ` — ${esc(state.persona.name || state.personaId)}` : ""}</h3>
    <div class="note">${langPick("Complete requests: employee + stage, the blocker, what's been tried, the named owner.",
      "طلبات مكتملة: الموظف والمرحلة والعائق وما جُرِّب والمالك المحدد بالاسم.")}</div>
    ${mine.length ? mine.map((c) => `
      <div class="handoff-card">
        <div class="handoff-head">
          <b>${esc(c.handoff_id)}</b>
          <span class="pill ${c.status === "open" ? "med" : "high"}">${esc(c.status)}</span>
        </div>
        <div class="handoff-grid">
          <div><span class="kv-key">${langPick("Employee", "الموظف")}</span><b dir="auto"> ${esc(c.employee_id)}</b></div>
          <div><span class="kv-key">${t.stage}</span> ${esc(c.stage)}</div>
          <div><span class="kv-key">${langPick("Owner", "المالك")}</span><b dir="auto"> ${esc(c.suggested_owner.name)}</b></div>
          <div><span class="kv-key">${t.blockers}</span><span dir="auto"> ${esc(c.blocker)}</span></div>
          <div><span class="kv-key">${langPick("Tried", "ما جُرِّب")}</span><span dir="auto"> ${esc((c.tried || []).join(" · "))}</span></div>
          <div class="handoff-summary" dir="auto">${esc(c.summary)}</div>
        </div>
        ${c.status === "open" ? `
          <div class="handoff-actions">
            <button class="cta secondary" data-status="acknowledged" data-id="${esc(c.handoff_id)}">${langPick("Acknowledge", "إشعار بالاستلام")}</button>
            <button class="cta" data-status="resolved" data-id="${esc(c.handoff_id)}">${langPick("Resolve", "تم الحل")}</button>
          </div>` : ""}
      </div>`).join("") : `<div class="note">${t.none}</div>`}`;
  $$("[data-status]", $("#handoffs-card")).forEach((b) => b.addEventListener("click", async () => {
    await post(`/handoff/${b.dataset.id}/status`, { status: b.dataset.status });
    toast(langPick("Handoff updated — the employee's audit log shows it.",
                   "تم تحديث الإحالة — يظهر ذلك في سجل نشاط الموظف."));
    renderHandoffs();
  }));
}

async function expandHandoff(id) {
  location.hash = "#/handoffs";
  if (state.viewRole === "employee") return;
  renderHandoffs();
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
      ${kv(langPick("Line manager", "المدير المباشر"), d.line_manager ? esc(d.line_manager.name) : "—")}
      ${kv(langPick("HR Business Partner", "شريك الموارد البشرية"), d.hrbp ? esc(d.hrbp.name) : "—")}
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
    if (badge) { badge.hidden = !rows.length; badge.textContent = rows.length; }
    const bell = $("#bell-btn");
    bell.hidden = state.viewRole !== "employee";
    const bb = $("#bell-badge");
    bb.hidden = !rows.length;
    bb.textContent = rows.length;
  }).catch(() => {});
}

/* notification bell tray (employee-side, super friendly) */
$("#bell-btn").addEventListener("click", async () => {
  const tray = $("#bell-tray");
  if (!tray.hidden) { tray.hidden = true; return; }
  const rows = await api(`/me/notices?employee_id=${state.employeeId}`);
  tray.innerHTML = `<div class="tray-head">${langPick("Notifications", "التنبيهات")}</div>`
    + (rows.length ? rows.slice(0, 6).map((n) => `
      <div class="tray-row ${esc(n.kind)}">
        <div class="notice-title" dir="auto">${esc(n.title)}</div>
        <div class="notice-detail" dir="auto">${esc(n.detail)}</div>
      </div>`).join("")
      + `<a class="ghost-link" href="#/notices">${langPick("See all →", "عرض الكل ←")}</a>`
      : `<div class="tray-empty">${langPick("Nothing needs you right now.", "لا شيء يتطلب انتباهك الآن.")}</div>`);
  tray.hidden = false;
  if (rows.length) {
    await post("/me/notices/read", { employee_id: state.employeeId });
    refreshNoticeBadge();
  }
});
document.addEventListener("click", (e) => {
  if (!e.target.closest("#bell-btn") && !e.target.closest("#bell-tray")) $("#bell-tray").hidden = true;
});

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
