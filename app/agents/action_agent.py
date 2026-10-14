"""Action agent — chases, request creation, handoff cards and safe fallbacks."""
from __future__ import annotations

from app.core.consent import AuditLog
from app.core.journey_engine import journey_state
from app.schemas.ask import AskRequest, AskResponse
from app.schemas.common import Citation, Owner
from app.schemas.handoff import HandoffCard
from app.services.notify import HandoffStore, RequestStore

# event/action -> (request type, owning team)
_ACTION_TARGETS = {
    "laptop": ("laptop_issue", "IT Service Desk"),
    "medical": ("medical_booking", "Visa & Immigration"),
    "access": ("access_request", "IT Service Desk"),
    "visa": ("visa_query", "Visa & Immigration"),
    "insurance": ("insurance_query", "HR Benefits"),
    "تأمين": ("insurance_query", "HR Benefits"),
    "payroll": ("payroll_query", "Payroll"),
    "salary": ("payroll_query", "Payroll"),
    "رواتب": ("payroll_query", "الرواتب"),
    "transfer": ("transfer_approval", "HR Mobility"),
    "نقل": ("transfer_approval", "HR Mobility"),
    "leave": ("leave_query", "Line Manager"),
}
_TYPE_POLICY = {
    "medical_booking": ("ONB-03", "Visa and Relocation"),
    "laptop_issue": ("ONB-07", "IT Provisioning"),
    "access_request": ("IT-01", "Access and Account Requests"),
    "visa_query": ("ONB-03", "Visa and Relocation"),
}


def _detect_target(message: str) -> str:
    m = message.lower()
    for key in _ACTION_TARGETS:
        if key in m:
            return key
    return "general"


async def handle_action(req: AskRequest, store, mode: str) -> AskResponse:
    target = _detect_target(req.message)
    if mode == "chase":
        return chase(req, store, target)
    return start_request(req, store, target)


def chase(req: AskRequest, store, target: str) -> AskResponse:
    ar = req.lang == "ar"
    state = journey_state(store, req.employee_id)
    if target == "general":
        # "please chase it" — no explicit target: chase the worst blocker, if any
        blocker = max(state.blockers, key=lambda b: b.days_overdue, default=None)
    else:
        blocker = next((b for b in state.blockers if target in b.event or b.event in target), None)
    handoffs, audits = HandoffStore(), AuditLog()

    if blocker is not None:
        existing = handoffs.open_for(req.employee_id, blocker.event)
        if existing:
            if ar:
                answer = f"هناك متابعة مفتوحة بالفعل مع {existing.suggested_owner.name} (رقم {existing.handoff_id})."
            else:
                answer = f"There's already an open chase with {existing.suggested_owner.name} ({existing.handoff_id})."
            return AskResponse(answer=answer, confidence=0.9, escalated=True,
                               handoff_id=existing.handoff_id, actions=[f"chase_{blocker.event}"],
                               kind="action")
        card = handoffs.create(HandoffCard(
            employee_id=req.employee_id,
            event_key=blocker.event,
            stage=f"{state.journey.value}/day-{state.day}",
            blocker=f"{blocker.label} (due day {blocker.due_day}, {blocker.days_overdue} day(s) overdue)",
            tried=["Companion auto-reminder (sweep)", "Employee self-check in journey timeline"],
            suggested_owner=Owner(name=blocker.owner.name, role=blocker.owner.role),
            summary=(f"{req.employee_id} is blocked on '{blocker.label}' — journey day {state.day}, "
                     f"{blocker.days_overdue} day(s) past the day-{blocker.due_day} target. Chase raised by Rafiq."),
            created_day=state.day,
        ))
        audits.append(req.employee_id, "chase_raised",
                      {"event": blocker.event, "owner": blocker.owner.name, "handoff_id": card.handoff_id})
        if ar:
            answer = (f"تابعتُ {blocker.owner.name} نيابة عنك ورفعتُ بطاقة إحالة ({card.handoff_id}) "
                      f"توضح العائق وما جُرِّب. سترى كل ذلك في سجل النشاط.")
        else:
            answer = (f"I've chased {blocker.owner.name} for you and raised a handoff card "
                      f"({card.handoff_id}) with the blocker and what's been tried. "
                      f"You'll see it in your audit log.")
        return AskResponse(answer=answer, confidence=0.9, escalated=True, handoff_id=card.handoff_id,
                           actions=[f"chase_{blocker.event}"], kind="action")

    # no blocker — chase the open request instead
    reqs = store.requests_for(req.employee_id)
    open_reqs = reqs[reqs["status"].astype(str).str.lower() == "open"] if not reqs.empty else reqs
    if not open_reqs.empty:
        r = open_reqs.iloc[0]
        RequestStore().chase(str(r["request_id"]), req.employee_id)
        audits.append(req.employee_id, "chase_raised", {"request_id": str(r["request_id"])})
        owner = str(r.get("owner", "the owner"))
        if ar:
            answer = f"تابعتُ الطلب {r['request_id']} مع {owner}. ستجد المتابعة في سجل النشاط."
        else:
            answer = f"I've chased request {r['request_id']} with {owner}. It's logged in your audit log."
        return AskResponse(answer=answer, confidence=0.85, actions=["chase_request"], kind="action")

    return AskResponse(
        answer=("I couldn't find anything stuck on your journey right now. "
                "If something feels wrong, I can route you to a person." if not ar else
                "لا يوجد شيء متعثر في رحلتك حاليًا. إذا كنت تشعر بخلل ما، يمكنني تحويلك إلى شخص."),
        confidence=0.8, kind="action")


def start_request(req: AskRequest, store, target: str) -> AskResponse:
    ar = req.lang == "ar"
    rtype, owner = _ACTION_TARGETS.get(target, ("general_request", "HR Service Desk"))
    rid = RequestStore().create(req.employee_id, rtype, owner, store.journey_day(req.employee_id))
    AuditLog().append(req.employee_id, "request_created", {"request_id": rid, "type": rtype, "owner": owner})
    citations = []
    hint = _TYPE_POLICY.get(rtype)
    if hint:
        citations.append(Citation(policy_id=hint[0], title=hint[1], lang=req.lang.value))
    if ar:
        answer = (f"أنشأتُ الطلب {rid} ({rtype}) وحوّلته إلى {owner} مع سياق رحلتك. "
                  f"الحالة ستظهر في الجدول الزمني.")
    else:
        answer = (f"Created request {rid} ({rtype}) and routed it to {owner} with your journey "
                  f"context attached. You can track it on your timeline.")
    return AskResponse(answer=answer, confidence=0.9, citations=citations,
                       actions=[f"start_request:{rtype}"], kind="action")


def low_confidence_response(req: AskRequest) -> AskResponse:
    """No source, no claim — say so and hand off (the brief's exact rule)."""
    ar = req.lang == "ar"
    card = HandoffStore().create(HandoffCard(
        employee_id=req.employee_id, stage="handoff", blocker="Low-confidence question",
        tried=["Grounded retrieval below threshold"],
        suggested_owner=Owner(name="HR Service Desk", role="HR Service Desk"),
        summary=f"{req.employee_id} asked: “{req.message[:200]}” — retrieval not confident; needs a person.",
        created_day=0,
    ))
    AuditLog().append(req.employee_id, "low_confidence_handoff", {"handoff_id": card.handoff_id})
    return AskResponse(
        answer=("I'm not sure about that one — I don't have a policy source I can cite, so I've "
                f"routed your question to the HR Service Desk ({card.handoff_id})."
                if not ar else
                "لست متأكدًا من ذلك — لا أملك مصدر سياسة يمكنني الاستشهاد به، لذا حوّلتُ سؤالك "
                f"إلى مكتب خدمات الموارد البشرية ({card.handoff_id})."),
        confidence=0.2, citations=[], escalated=True, handoff_id=card.handoff_id, kind="handoff")


def sensitive_response(req: AskRequest, topic: str) -> AskResponse:
    """Sensitive topic → a named human immediately; nothing auto-answered."""
    ar = req.lang == "ar"
    card = HandoffStore().create(HandoffCard(
        employee_id=req.employee_id, stage="sensitive", blocker=f"Sensitive topic: {topic}",
        tried=[],
        suggested_owner=Owner(name="HR Business Partner", role="HR Business Partner"),
        summary=f"{req.employee_id} raised a {topic}-related matter. Routed to a human, not auto-processed.",
        created_day=0,
    ))
    AuditLog().append(req.employee_id, "sensitive_handoff", {"topic": topic, "handoff_id": card.handoff_id})
    return AskResponse(
        answer=("That touches a personal matter, so I won't answer it myself — I've connected you "
                f"with your HR Business Partner ({card.handoff_id}). Nothing here is auto-processed."
                if not ar else
                "هذا يخص أمرًا شخصيًا، لذا لن أجيب عنه بنفسي — ربطتُك بشريك الموارد البشرية "
                f"({card.handoff_id}). لا يعالَج شيء هنا آليًا."),
        confidence=1.0, citations=[], escalated=True, handoff_id=card.handoff_id, kind="handoff")
