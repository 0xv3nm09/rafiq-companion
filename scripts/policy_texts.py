"""Bilingual policy texts for the synthetic pack — the ground truth Rafiq cites.

Format: {policy_id: {"title": ..., "title_ar": ..., "sections": [(en_title, en_text), ...],
        "sections_ar": [(ar_title, ar_text), ...]}}
"""

POLICIES: dict[str, dict] = {
    "ONB-01": {
        "title": "Pre-boarding and Day One",
        "title_ar": "ما قبل الانضمام واليوم الأول",
        "sections": [
            ("Before Day One", "New joiners receive a pre-boarding pack at offer acceptance covering documents to bring, first-week agenda, and their buddy assignment. HR Onboarding confirms building access and badge readiness before day one. Any document gap should be raised with HR Onboarding before the start date."),
            ("Day One", "On day one the line manager welcomes the joiner and walks them through the org chart, desk and facilities. A badge with building access is issued by Facilities on day one. If a badge is not ready, the joiner should ask the companion to chase Facilities."),
        ],
    },
    "ONB-03": {
        "title": "Visa and Relocation",
        "title_ar": "التأشيرة والانتقال",
        "sections": [
            ("Entry Permit", "For relocating hires the entry permit is sponsored by the employer and normally takes up to 10 working days from document submission. The Visa and Immigration team owns this step and updates the journey once issued. Roughly half of relocating employees call the visa stage the hardest part of the move, so each step is tracked with a named owner."),
            ("Medical Fitness and Emirates ID", "After entry, the medical fitness test is booked by the Visa and Immigration team with a target of day 15, and the Emirates ID application follows with a target of day 20. The employee attends in person; the employer arranges appointments. Status of both steps is visible in the journey timeline."),
            ("Residence Visa Stamping", "Residence visa stamping is the final immigration step with a target of day 25, after which the passport is returned. Delays beyond target are escalated to the named owner. Family or dependent sponsorship can start once the residence visa is stamped."),
        ],
    },
    "ONB-07": {
        "title": "IT Provisioning",
        "title_ar": "التجهيزات التقنية",
        "sections": [
            ("Laptop and Equipment SLA", "A laptop is issued by day 3 of onboarding by the IT Service Desk. If a laptop has not been issued by its target day, the employee can ask the companion to chase IT, which raises a priority ticket with the IT Service Desk as owner. Equipment overdue by more than two days is escalated automatically."),
            ("Accounts and Access", "IT accounts (email, VPN, core systems) are created by day 2, before the laptop is issued. Access to additional systems is requested through the service desk and granted by the system owner. First-week induction training is booked by Learning and Development with a target of day 7."),
        ],
    },
    "ONB-09": {
        "title": "Health Insurance",
        "title_ar": "التأمين الصحي",
        "sections": [
            ("Enrolment", "Health insurance is enrolled by HR Benefits with a target of day 14 and takes effect from the first day of the following month at the latest. The employee selects a plan category during pre-boarding. Enrolment status is visible in the journey timeline."),
            ("Dependents", "Spouse and children can be added to health insurance after the employee's enrolment is complete; documents required are marriage and birth certificates. Dependent cover is at shared cost per the benefits schedule. Claims questions are answered from this policy; disputes go to HR Benefits."),
        ],
    },
    "ONB-12": {
        "title": "Probation and Reviews",
        "title_ar": "فترة التجربة والتقييمات",
        "sections": [
            ("Probation Period", "New joiners complete a six-month probation. Structured check-ins with the line manager happen at days 30, 60 and 90, each with written feedback. A probation review without a scheduled 30-day check-in is flagged to the line manager."),
            ("Reviews", "The 30/60/90 reviews set expectations and record progress against role benchmarks. Outcomes are advisory to the confirmation decision, which rests with the line manager and HR. Questions about review content should be raised with the line manager first."),
        ],
    },
    "MOB-01": {
        "title": "Internal Transfer Policy",
        "title_ar": "سياسة النقل الداخلي",
        "sections": [
            ("Approval Chain", "An internal transfer needs three approvals in order: receiving team sign-off (target day 15), release from the current manager (target day 20), and HR Mobility sign-off. The transfer request itself is approved by HR Mobility at day 10. Each step is tracked against its service-level target and stalls are flagged."),
            ("Release and Handover", "The current manager owns the handover plan; the notice period follows the contract grade. A move to a new team is treated as a second onboarding: the new joiner checklist, access re-provisioning and a first 1:1 with the new manager (target day 30) all apply. Approval steps overdue beyond two days are escalated with a summary to the named owner."),
        ],
    },
    "MOB-04": {
        "title": "Role Change Terms",
        "title_ar": "شروط تغيير الدور",
        "sections": [
            ("Grade and Compensation", "A role change may adjust grade and salary; the new terms are confirmed in the transfer letter issued by HR Mobility. Salary is aligned to the destination grade band. Questions about the calculation are answered from this policy; contested cases go to HR Mobility."),
            ("Leave Accrual", "Annual leave accrual carries over across an internal move; the balance is not reset. Probation does not restart for a lateral move but may restart for a promotion into a different job family. The employee can view their leave balance in the HR self-service portal."),
        ],
    },
    "MOB-06": {
        "title": "Relocation on Transfer",
        "title_ar": "الانتقال عند النقل",
        "sections": [
            ("Allowance Recalculation", "Moving to a new emirate or country triggers recalculation of housing and location allowances per the destination band. Payroll applies the change from the effective date of the move. The employee sees the recalculation in the transfer letter."),
            ("Housing and Logistics", "Facilities confirms the new location is ready with a target of day 25, including desk, access and parking. Visa transfer for cross-border moves is handled by Visa and Immigration using the ONB-03 process. Shipping of personal effects is per the relocation allowance schedule."),
        ],
    },
    "HR-01": {
        "title": "Annual Leave",
        "title_ar": "الإجازة السنوية",
        "sections": [
            ("Entitlement", "Employees accrue 30 calendar days of annual leave per year, prorated for partial years. Accrual continues across internal transfers. Balances are visible in the self-service portal."),
            ("Booking and Approval", "Leave is requested in the portal and approved by the line manager within five working days. Requests more than 15 working days require four weeks' notice. Unapproved requests past five working days can be chased through the companion."),
        ],
    },
    "HR-02": {
        "title": "Sick and Special Leave",
        "title_ar": "الإجازة المرضية والإجازات الخاصة",
        "sections": [
            ("Sick Leave", "Sick leave is 90 calendar days per year: full pay for the first 45, half pay for the next 30, unpaid thereafter, with a medical certificate from day one. Certificates are uploaded to the portal. Extended illness cases are handled by HR Benefits."),
            ("Hajj and Compassionate Leave", "Hajj leave is up to 30 days once per service for eligible employees. Compassionate leave is five days for the loss of an immediate family member. Both are requested through the line manager; the companion can explain eligibility from this policy."),
        ],
    },
    "HR-04": {
        "title": "Allowances",
        "title_ar": "البدلات",
        "sections": [
            ("Housing and Transport", "Housing allowance is 30% of basic salary and transport allowance is 10%, per the grade band. Allowances are reviewed at grade changes. The WPS salary setup reflects the full breakdown."),
            ("Education", "Education allowance supports up to three children per the grade-dependent schedule, paid termly against receipts. Claims are submitted to Payroll. Eligibility questions are answered from this policy."),
        ],
    },
    "HR-08": {
        "title": "End-of-Service Gratuity",
        "title_ar": "مكافأة نهاية الخدمة",
        "sections": [
            ("Calculation", "Gratuity is 21 days of basic salary per year for the first five years and 30 days per year thereafter, capped at two years' total salary. Unpaid leave days are excluded from service. This explainer is informational; the binding calculation is issued by Payroll."),
            ("Payment", "Gratuity is paid within 14 days of the last working day. Deductions for outstanding loans follow the contractual schedule. Disputes go to Payroll, then to HR."),
        ],
    },
    "HR-11": {
        "title": "Remote and Hybrid Work",
        "title_ar": "العمل عن بعد والهجين",
        "sections": [
            ("Eligibility", "Roles are tagged on-site, hybrid or remote by the function. Hybrid roles default to two remote days per week. Frontline and operational roles remain on-site."),
            ("Approval", "Permanent remote arrangements require line manager and function-head approval with a six-month review. Ad-hoc remote days are requested in the portal. Equipment for home offices follows IT-01."),
        ],
    },
    "IT-01": {
        "title": "Access and Account Requests",
        "title_ar": "طلبات الوصول والحسابات",
        "sections": [
            ("Requesting Access", "System access is requested through the service desk and approved by the system owner within two working days. New joiners' core access follows the ONB-07 provisioning plan. Access for movers is re-provisioned with a target of day 22 in the mobility journey."),
            ("Lost or Broken Equipment", "Lost or damaged equipment is reported to the IT Service Desk the same day; replacements are issued within three working days after a short review. The employee acknowledges the incident in writing. Insurance questions go to HR Benefits."),
        ],
    },
    "EMR-01": {
        "title": "Staff Travel and Flight Benefits",
        "title_ar": "سفر الموظفين ومزايا الرحلات",
        "sections": [
            ("Eligibility", "Confirmed employees receive annual concessional travel tickets for themselves and eligible family per the benefits schedule. Eligibility starts after probation confirmation. Standby upgrade rules apply per the travel portal."),
            ("Concessional Fares", "Concessional fares are booked through the staff travel portal with applicable taxes only. Ticket counts and zones follow the grade band. The portal shows live availability; this policy explains entitlement."),
        ],
    },
    "PAY-02": {
        "title": "Wage Protection System Setup",
        "title_ar": "إعداد نظام حماية الأجور",
        "sections": [
            ("WPS Setup", "Salaries are paid through the Wage Protection System to a UAE bank account in the employee's name. Bank and WPS setup has a target of day 10 with Payroll as owner. The employee provides IBAN details during pre-boarding."),
            ("First Salary", "The first salary reflects the partial month and includes the housing and transport allowances. Payslips are available in the portal from payday plus one day. Deduction questions are answered from this policy; discrepancies go to Payroll."),
        ],
    },
    "GPSSA-01": {
        "title": "Pension Registration for Emirati Hires",
        "title_ar": "تسجيل المعاش للموظفين الإماراتيين",
        "sections": [
            ("30-Day Registration", "Emirati hires in the private sector must be registered with GPSSA for pension within 30 days of the start date. HR Onboarding raises the registration; the employee verifies their record in Nafis. This deadline-driven step appears as a first-class task on the joiner's own timeline."),
            ("Nafis Benefits", "Nafis benefits for eligible Emirati employees include a salary top-up, child allowance and reduced employee pension contributions. Enrolment is guided by HR Benefits. Aggregated, non-individual localization progress is reported to the entity."),
        ],
    },
}
