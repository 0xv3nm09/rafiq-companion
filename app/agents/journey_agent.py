"""Journey agent — deterministic status replies from the SLA engine."""
from __future__ import annotations

from app.core.guardrails import trust_gate
from app.core.journey_engine import journey_state, timeline
from app.schemas.ask import AskRequest, AskResponse
from app.schemas.common import Citation

# event -> the policy that governs it (cited on blocker replies)
EVENT_POLICY = {
    "laptop_issued": ("ONB-07", "IT Provisioning"),
    "it_account_created": ("ONB-07", "IT Provisioning"),
    "badge_building_access": ("ONB-01", "Pre-boarding and Day One"),
    "visa_entry_permit": ("ONB-03", "Visa and Relocation"),
    "medical_fitness_test": ("ONB-03", "Visa and Relocation"),
    "emirates_id_application": ("ONB-03", "Visa and Relocation"),
    "residence_visa_stamped": ("ONB-03", "Visa and Relocation"),
    "bank_wps_setup": ("PAY-02", "Wage Protection System Setup"),
    "health_insurance_enrolled": ("ONB-09", "Health Insurance"),
    "induction_training_booked": ("ONB-07", "IT Provisioning"),
    "probation_review_30": ("ONB-12", "Probation and Reviews"),
    "transfer_request_approved": ("MOB-01", "Internal Transfer Policy"),
    "receiving_team_signoff": ("MOB-01", "Internal Transfer Policy"),
    "release_from_current_team": ("MOB-01", "Internal Transfer Policy"),
    "access_reprovisioned": ("IT-01", "Access and Account Requests"),
    "new_location_ready": ("MOB-06", "Relocation on Transfer"),
    "first_1on1_new_team": ("MOB-01", "Internal Transfer Policy"),
}

_AR = dict(stage="مرحلتك", day="اليوم", blockers="عناصر متعثرة", overdue="متأخر",
           chase="أتابع", for_you="نيابة عنك", all_good="كل شيء على المسار الصحيح",
           next="الخطوة التالية")

# Arabic labels for journey events (UI + replies)
EVENT_LABELS_AR = {
    "offer_accepted": "قبول العرض", "documents_submitted": "تقديم المستندات",
    "badge_building_access": "بطاقة الدخول للمبنى", "it_account_created": "إنشاء حساب تقنية المعلومات",
    "laptop_issued": "تسليم الحاسوب المحمول", "first_manager_1on1": "أول لقاء مع المدير",
    "induction_training_booked": "حجز التدريب التمهيدي", "bank_wps_setup": "إعداد البنك ونظام حماية الأجور",
    "health_insurance_enrolled": "التسجيل في التأمين الصحي", "visa_entry_permit": "تصريح الدخول",
    "medical_fitness_test": "اختبار اللياقة الطبية", "emirates_id_application": "طلب الهوية الإماراتية",
    "residence_visa_stamped": "إقلام تأشيرة الإقامة", "probation_review_30": "تقييم الثلاثين يومًا",
    "transfer_request_approved": "اعتماد طلب النقل", "receiving_team_signoff": "موافقة الفريق المستقبل",
    "release_from_current_team": "إطلاق الفريق الحالي", "access_reprovisioned": "إعادة تجهيز الصلاحيات",
    "new_location_ready": "جهوزية الموقع الجديد", "first_1on1_new_team": "أول لقاء مع الفريق الجديد",
}


@trust_gate
async def journey_reply(req: AskRequest, store) -> AskResponse:
    state = journey_state(store, req.employee_id)
    ar = req.lang == "ar"

    lines: list[str] = []
    if ar:
        lines.append(f"أنت في مرحلة «{state.stage}» — اليوم {state.day} من رحلتك.")
    else:
        lines.append(f"You are in the '{state.stage}' stage — day {state.day} of your journey.")

    citations: list[Citation] = []
    actions: list[str] = []
    if state.blockers:
        for b in state.blockers:
            hint = EVENT_POLICY.get(b.event)
            if hint and hint[0] not in [c.policy_id for c in citations]:
                citations.append(Citation(policy_id=hint[0], title=hint[1], lang=req.lang.value))
            owner = b.owner.name
            label = EVENT_LABELS_AR.get(b.event, b.label) if ar else b.label
            if ar:
                lines.append(f"«{label}» متأخر {b.days_overdue} يوم — كان مستحقًا يوم {b.due_day}. "
                             f"المالك: {owner}. أستطيع المتابعة {(_AR['for_you'])}.")
            else:
                lines.append(f"'{b.label}' is {b.days_overdue} day(s) overdue (due day {b.due_day}). "
                             f"Owner: {owner}. I can chase them for you.")
            actions.append(f"offer_chase:{b.event}")
    else:
        lines.append(_AR["all_good"] if ar else "Everything is on track — no blockers.")
        nxt = timeline(store, req.employee_id)
        upcoming = [s for s in nxt if s.status == "upcoming"][:2]
        for s in upcoming:
            label = EVENT_LABELS_AR.get(s.event, s.label) if ar else s.label
            lines.append((f"الخطوة التالية: {label} — مستهدفة يوم {s.target_day} ({s.owner})."
                          if ar else
                          f"Next up: {s.label} — targeted day {s.target_day} ({s.owner})."))

    return AskResponse(answer="\n".join(lines), confidence=0.95, citations=citations,
                       actions=actions, kind="journey")
