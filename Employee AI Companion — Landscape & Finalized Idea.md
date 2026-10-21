# Emirates AI Companion — Landscape & Finalized Idea

Oct 13, 2026 · @M Omaid

**Bottom line:** the market splits into onboarding/support bots (Leena AI, Moveworks) and internal-mobility marketplaces (Gloat, Fuel50) — almost nobody unifies both journeys in one employee-owned companion, and the proactive "spot friction before it escalates" layer is the weakest part of every product. Winning means excelling at both journeys as co-equals — not bolting mobility onto an onboarding bot — on a proactive, consent-first, UAE-sovereign build. The employee-voice data backs this: onboarding pain in the UAE concentrates in visa/relocation, while career-progression clarity is the single biggest retention lever, and no product serves both.

## The landscape: two separate markets

The software that touches this problem splits into two categories that rarely overlap, which matters because the Emirates brief asks for one companion spanning *both* onboarding and internal mobility.

**Category 1 — Employee support & onboarding assistants.** Conversational AI that answers HR/IT/policy questions and automates routine requests, deployed inside Slack or Teams. The leaders are [Leena AI](https://www.leena.ai/leenaAI-vs-Moveworks) (pre-built "AI colleagues" for HR, IT, finance and procurement across 1,000+ enterprise systems), [Moveworks](https://www.moveworks.com/us/en/platform/moveworks-ai) (an agentic reasoning engine with inline citations, now part of ServiceNow), and Aisera (now part of Automation Anywhere). Onboarding-specific players like Enboarder (journey builder), Rippling (unified HR+IT provisioning) and SAP's Joule onboarding agents sit alongside them. These tools are strong at answering and automating, but they treat onboarding as a checklist and largely stop at day 90.

**Category 2 — Internal talent marketplaces.** Skills-based platforms that match employees to internal roles, gigs, projects and mentors. [Gloat](https://us.fitgap.com/products/gloat) created the category and runs mobility at enterprise scale (Spotify, Goldman Sachs, Schneider); [Fuel50](https://www.cbinsights.com/compare/fuel50-vs-workey) and Eightfold compete on skills-taxonomy depth. These own the *move* — but they are career-planning engines, not day-to-day companions, and they do nothing for onboarding, policy questions or request chasing.

The practical takeaway: a new joiner uses one world, an internal mover uses the other, and no mainstream product carries a person smoothly across both with a single memory of where they are. That seam is exactly what the challenge targets.

## Competitor comparison

The players most worth studying, what each is genuinely best at, and the weakness that leaves room for us.

| Player | Category | Best at | Weakness for this challenge |
| --- | --- | --- | --- |
| [Leena AI](https://www.leena.ai/leenaAI-vs-Moveworks) | Support/onboarding | Pre-built HR/IT/finance agents live in weeks; grounds answers in a "knowledge studio"; workflows authored in plain English | Reactive — waits to be asked; onboarding is FAQ + ticketing, not a journey it owns; no mobility |
| [Moveworks](https://www.moveworks.com/us/en/platform/moveworks-ai) | Support/onboarding | Strong reasoning engine, inline source citations, deep enterprise search across apps | IT-rooted; HR/mobility coverage is a build; now tied to ServiceNow's stack |
| Rippling | Onboarding + provisioning | Unified HR + IT, auto-provisions accounts/devices on hire | US/SMB-leaning; provisioning engine, not an employee-facing companion; no Arabic/GCC focus |
| Enboarder | Onboarding journeys | Personalized, nudge-driven onboarding journeys that feel human at scale | Journey nudges, not Q&A or request resolution; stops around onboarding |
| SAP Joule / SuccessFactors | Onboarding (suite) | Onboarding agents native to the SAP HR/payroll stack | Only shines inside an SAP footprint; heavy; agent coverage still emerging |
| [Gloat](https://us.fitgap.com/products/gloat) | Mobility marketplace | Category creator; matches people to roles/gigs/projects at scale; rich workforce analytics | Career engine, not a daily companion; nothing for onboarding, policy or request chasing; needs clean data |
| [Fuel50](https://www.cbinsights.com/compare/fuel50-vs-workey) | Mobility marketplace | Granular skills taxonomy; career-pathing and reskilling | Same gap as Gloat — mobility only, not a support or onboarding layer |

The pattern is consistent: everyone is excellent at *one* slice, reactive rather than anticipatory, and none is built around UAE data law, Arabic-first support, or an employee-owned trust model.

## Market size & opportunity

The money and the mandate are both moving toward exactly this problem. The GCC HR-tech market is forecast to grow at roughly [9.45% CAGR through 2034](https://www.peoplematters.in/news/hr-technology/gcc-hr-tech-market-expected-to-grow-at-945percent-cagr-through-2034-imarc-49711), with the UAE and Saudi Arabia the biggest contributors. The narrower HR-management-systems segment is projected to roughly triple, from [USD 1.04B in 2025 to USD 2.89B by 2032](https://www.marknteladvisors.com/research-library/gcc-human-resource-management-system-market-study.html) (15.6% CAGR). A named growth driver is workforce localization — Emiratization and Saudization require nationality-based tracking and reporting, which an employee companion can surface natively. And the workforce is receptive: [60% of UAE employees see AI as an opportunity](https://gulfnews.com/gn-focus/uae-employees-are-unfazed-by-ai-but-demand-better-benefits-from-employer-1.1731657648429), not a threat. The timing, the budget and the employee appetite all line up.

## Voice of the employee: what UAE/GCC workers want

Across multiple surveys the message is consistent — pay matters, but career growth and clarity now rival it, and employees are more willing to walk than ever. This is the demand signal our companion is built to meet.

| What they want | Evidence | Source |
| --- | --- | --- |
| Career growth & development | 83% would leave for better training elsewhere; 57% want higher roles, yet \~1 in 3 have never been promoted at their current employer | [Bayt / YouGov](https://www.thenational.ae/uae/most-uae-professionals-would-quit-jobs-for-better-career-development-survey-1.194197) |
| Transparency on pathways & pay | Lack of clarity on progression and pay hurts motivation; 26% felt *less* positive after their last review, only 21% more optimistic | [Robert Walters ME 2026](https://www.khaleejtimes.com/business/uae-employees-want-more-from-performance-reviews-than-just-salary-says-new-report) |
| The freedom to move | 98% of UAE employees are open to a new role in 2026; 66% are actively considering a move | [GCC Salary Guide](https://me.peoplemattersglobal.com/news/recruitment/nearly-all-uae-employees-are-ready-to-change-jobs-in-2026-and-pay-is-only-part-of-the-story-48326) |
| Benefits as a baseline | Benefits have shifted from nice-to-have to must-have; \~8 in 10 GCC employees weigh a change partly on inadequate benefits | [Gulf News survey](https://gulfnews.com/gn-focus/uae-employees-are-unfazed-by-ai-but-demand-better-benefits-from-employer-1.1731657648429) |
| To be seen early | Over half of UAE 18–24s would leave for growth; \~30% feel overlooked for lack of experience | [Gulf News survey](https://gulfnews.com/gn-focus/uae-employees-are-unfazed-by-ai-but-demand-better-benefits-from-employer-1.1731657648429) |

The through-line: the thing employees most want help with — knowing where they stand and where they can go — is precisely the mobility journey the incumbents ignore.

## Employee sentiment: the Glassdoor read

Emirates Group itself is well-rated — [3.9/5 with \~72% recommending](https://static.glassdoor.com.ar/Reviews/The-Emirates-Group-Reviews-E23433_P7.htm) across 5,000+ reviews, above its industry average. Reading the reviews (paraphrased, not quoted) the pattern is telling for this challenge:

- **Onboarding is often a *strength*.** Reviewers repeatedly describe the joining process as easy and engaging — so a companion can't win on "nicer onboarding FAQ" alone. The edge has to be proactivity and the mobility side.
- **Progression clarity is the recurring complaint.** The most common frustrations cluster around a lack of clarity on future development, seniority feeling unrewarded versus new joiners, and HR being seen as supporting employees only superficially.
- **Management rigidity and "people-first" gaps** show up often — strict, process-heavy, slow to explain the *why*. A companion that gives every employee a clear, cited "here's what's happening and what's next" directly counters that.

This is the strategic read: at Emirates, the onboarding box is largely ticked, so the differentiated value is catching stalls early and owning the mobility/progression journey that reviews say is weakest.

## The major issues, mapped to the two journeys

Both journeys have distinct, documented failure points. Our companion has to answer both columns — which is exactly why covering only one category loses.

| Journey | Major issue | Evidence |
| --- | --- | --- |
| Onboarding | Bad onboarding actively drives early exits | [24% of UAE juniors say onboarding made them more likely to leave; only 51% rate it good/excellent](https://www.khaleejtimes.com/uae/junior-employees-quitting-poor-onboarding-report-finds) |
| Onboarding | Visa & relocation is the hardest part | [\~50% of relocating talent call the visa/immigration process the most difficult part of the move](https://www.jobbatical.com/blog/what-international-employees-are-struggling-with) |
| Onboarding | Expats learn a role, a market and a culture at once | [Robert Walters: UAE's diverse workforce makes onboarding uniquely demanding](https://www.khaleejtimes.com/uae/junior-employees-quitting-poor-onboarding-report-finds) |
| Onboarding | "Where do I go for this?" — fragmented ownership across visa, payroll, IT, insurance | [UAE day-one playbooks stress clarifying who handles each request](https://www.talentera.com/en/blog/welcome-new-employee-in-the-uae-day-one-experience/) |
| Mobility | No transparent path; progression feels opaque | [Robert Walters 2026: lack of transparency on progression erodes motivation](https://www.khaleejtimes.com/business/uae-employees-want-more-from-performance-reviews-than-just-salary-says-new-report) |
| Mobility | Development gaps push people out | [83% would leave for better training; 1 in 3 never promoted internally](https://www.thenational.ae/uae/most-uae-professionals-would-quit-jobs-for-better-career-development-survey-1.194197) |
| Mobility | A move = a second onboarding, with the same friction | New team, location, approvals and systems repeat the onboarding pain with no dedicated support |
| Both | Problems surface only after a complaint or escalation | The brief's core premise — signals exist but are scattered and arrive late |

## Regional AI players — and how we're better

The GCC has its own AI-in-HR players, and one is a government system. They matter because judges will know them; showing we've mapped them and still differentiate is a credibility win.

| Regional player | What it is | Strong at | Why we're different |
| --- | --- | --- | --- |
| [Bayzat](https://yespress.io/bayzat) (Dubai) | GCC-native HR/payroll/benefits/insurance suite with a "Bayzat AI" chat assistant | GCC localization, benefits & insurance, 4,000+ companies | Reactive service-desk assistant bolted onto a suite — no journey-state memory, no proactive stall detection, no mobility journey |
| [Darwinbox](https://www.gccbusinessnews.com/hr-tech-unicorn-darwinbox-boosts-its-mena-presence-with-new-difc-office/) (MENA/DIFC) | Enterprise full-lifecycle HRIS with AI/ML, Arabic app, Voicebot | Enterprise breadth, Arabic, big regional clients | A system of record; onboarding and mobility are modules, not one employee-owned, anticipatory companion |
| [OrangeHRM + Citra AI](https://www.orangehrmlive.com/resources/blog/top-ten-hr-software-in-the-uae-and-middle-east-2026) | HR suite with a region-trained AI assistant | Compliance logic, data sovereignty | Assistant augments HR admin; not journey-first, not proactive |
| PeopleStrong "Jinie" | AI chatbot for policy and request handling | Instant policy access | Reactive Q&A and ticketing only |
| [FAHR AI HR Assistant](https://gulfnews.com/uae/government/uae-launches-ai-powered-hr-assistant-to-transform-government-services-1.500264344) (UAE federal gov, on "Bayanati") | Government AI HR assistant: 50,000 federal employees, 108 services, Arabic/English, voice, AI agents | Government-grade, sovereign, multilingual, proven scale | Reactive self-service across services — not journey-aware, not proactive, no both-journeys companion or employee-owned trust model |

**How we beat all of them — five lines:**

1. **Proactive, not reactive.** Every regional tool answers when asked. We detect a stall (overdue event, breached SLA, pulse dip) and act *before* the employee complains — the brief's actual prize.
2. **Journey-state memory.** They're service desks and systems of record. We hold one living model of "where you are" across onboarding and mobility, so "day 5, laptop not issued" is known, not asked.
3. **Both journeys, one companion.** None of them carries a person through a role/team/location move as a first-class journey. We do.
4. **Employee-owned by design.** They're bought for HR. Ours leads with the employee's own data view, opt-in consent and audit log — the 25% Responsible-AI criterion made visible.
5. **Complement, don't compete.** FAHR/Bayanati and Bayzat prove the appetite and can be the systems we sit on top of — a reuse story for Emirates and other government entities, not a turf war.

## The white space we should own

Five gaps run across the whole market. Our idea should be built on top of them — each maps to a judging criterion.

1. **One companion, both journeys.** Onboarding bots and mobility marketplaces are separate products. A single companion that holds one memory of "where you are" — whether that's day 5 of onboarding or week 2 of a transfer — is genuinely differentiated and is precisely the brief.
2. **Proactive, not reactive.** Every leader waits to be asked. The brief's real prize is spotting friction *before* the complaint — a laptop not issued by day 5, a transfer approval stalled past its SLA. A deterministic journey-state engine that compares events against target times makes this reliable, which is what the 30% hidden-scenario score rewards.
3. **Employee-owned trust model.** Most tools are bought for HR and point analytics *at* employees. The brief is explicit: this works for the employee, not as a manager-monitoring tool. A visible "what we hold about you" panel, opt-in pulse consent, and an action audit log turn the 25% Responsible-AI criterion into something a judge can click in the live demo — an advantage most teams will underbuild.
4. **Complete, correctly-routed handoffs.** Service owners want requests that arrive complete. A structured handoff card (employee + stage, the blocker, what's been tried, the named owner) beats a raw ticket and directly serves the routing requirement.
5. **UAE-native by design.** No global player is built around UAE data residency, Arabic-first interaction, or reuse across government entities. Grounding the build in UAE law and sovereign Arabic models is both a differentiator and the deployability/reuse score (10%).

## What the research says

The technical literature converges on a few points that should shape the build and that we can cite in the solution note.

**RAG is the right spine for policy answers, but grounding discipline is the hard part.** Retrieval-augmented generation over a bounded, authoritative corpus (HR policies, SOPs, IT FAQs) is the established pattern — work such as the ACL/DaSH study on [optimizing a retrieval-augmented QA chatbot](https://aclanthology.org/2024.dash-1.2.pdf) formalizes it. The recurring failure mode is confident hallucination when retrieval is weak; the documented fix is to raise the match threshold and instruct the model to answer *only* from retrieved text and say so when nothing relevant is found. This is identical to the brief's "cite the source; if unsure, say so and hand off" guardrail — so it should be a visible, tested behavior, not an afterthought.

**Escalation on sensitive cases is a research norm, not just a policy.** Guidance on production HR agents is consistent that any question involving an individual's specific circumstances — accommodations, medical, disciplinary, visa — must route to a human immediately rather than be answered. That lines up with the brief's "named human owner" rule and should be wired into the routing logic.

**The friction signals we need are already known and map onto the data pack.** Predictive-onboarding research identifies the first 90 days as the highest-attrition window and names the early signals: onboarding task completion rate and pace, a missed first manager 1:1 within \~5 business days, early-pulse scores, and time-to-productivity against role benchmarks. Those map almost one-to-one onto `journey_events.csv`, `service_requests.csv` and `pulse_feedback.csv` — meaning our "friction radar" can be evidence-based rather than invented. A deterministic SLA-breach rule (event overdue vs. `journey_maps.md` target) is more defensible for a demo than a black-box risk model, and easier for a judge to trust.

## Emirates & GCC context

This is where a generic solution loses and a UAE-aware one wins. Four things about the environment:

**The scale makes the problem real.** The Emirates Group reached [130,919 employees in 2025–26](https://www.khaleejtimes.com/business/aviation/jobs-in-uae-emirates-group-hires-9700-employees-from-35-million-applications), up 8%, spanning [160+ nationalities across six continents](https://unleash.ai/employee-experience-and-engagement/interview/emirates-hr-tech-enabled-post-pandemic-bounce-back). It onboarded nearly 9,700 people in the UAE alone last year and reviewed 3.5 million applications. At that volume, even a small per-journey friction rate is thousands of stuck employees — a companion that resolves routine needs and catches stalls early has an obvious business case.

**Emirates is already an AI-in-HR pioneer, so the bar is high.** Under EVP HR Oliver Grohmann the Group won the [2026 HR Pacesetter Award from the Josh Bersin Company](https://ae.linkedin.com/in/sumithp) for building GenAI capability across its workforce, and already runs people analytics, ML and predictive retention tooling with its people strategy anchored in Dubai's D33 economic agenda. The companion must feel native to an organization that already does tech-enabled onboarding — the edge is the employee-owned, proactive, bilingual framing, not "a chatbot."

**UAE data law is the backbone of the Responsible-AI story.** The [UAE PDPL (Federal Decree-Law No. 45 of 2021)](https://uppersetup.com/en/article/uae-personal-data-protection-law-pdpl-the-complete-business) is GDPR-like: explicit, voluntary consent, data-subject access rights, DPIAs, and [restrictions on cross-border transfer](https://captaincompliance.com/education/uaes-ai-governance-laws-pdpl-difc-rules-and-human-centric-principles/) (Articles 22–23). In June 2026 the UAE consolidated oversight under a new [Federal Authority for AI and Data](https://www.morganlewis.com/pubs/uae-establishes-federal-authority-for-artificial-intelligence-and-data), and the National AI Ethics Guidelines emphasize transparency, fairness and accountability. Translation for the build: opt-in consent, employee-visible data, human-in-the-loop, and keeping inference in-region are not nice-to-haves — they are the law, and they are exactly the 25% criterion.

**Sovereign Arabic AI makes bilingual + data residency a strength, not a cost.** The UAE has its own frontier Arabic models — TII's [Falcon Arabic / Falcon-H1 Arabic](https://www.businesswire.com/news/home/20260105343577/en), which leads the Open Arabic LLM Leaderboard and runs open-source and on-premise, and G42/Core42's [JAIS](https://enterpriseam.com/uae/issues/uae-launches-new-ai-model-to-rival-big-tech/) Arabic–English bilingual model. Naming an on-premise/in-region sovereign model as the deployment path answers Arabic-first support, PDPL residency, and government-entity reuse in one move.

## The finalized idea

**Working name:** *Rafiq* (Arabic for "companion") — an employee-owned AI companion that carries a person across both the onboarding and the internal-mobility journey, resolves routine needs, and quietly catches friction before it escalates.

**One-line pitch:** Unlike support bots that only answer and marketplaces that only match, Rafiq knows exactly where you are in your journey, cites the policy behind every answer, and flags a stall to the right named owner before it becomes a complaint — all on a consent-first, UAE-sovereign footing.

**Both journeys are first-class, by design.** Onboarding support wins the day-5-laptop and stalled-visa cases; the mobility track treats a role/team/location move as a second onboarding — tracking transfer and relocation approvals against their SLAs, answering the policy questions a move raises, and giving the employee a clear "where am I, what's next" view. That mobility track is where the employee-voice data says the real unmet need sits, so it carries equal weight rather than being an onboarding add-on.

**The architecture has four parts** (keep the first deterministic for trust):

1. **Journey-state engine** — joins journey events against `journey_maps.md` target times to know the current stage and what's overdue. Deterministic, so "day 5, laptop not issued" is reliable, not guessed.
2. **Grounded answer layer** — RAG over the policy pack with an inline source citation on every answer; low-confidence → says so and hands off.
3. **Action & routing layer** — starts/updates requests and produces a structured handoff card to the correct owner.
4. **Friction radar** — combines overdue events + requests past SLA + opt-in pulse sentiment into a risk flag the *employee sees first*; HRBP is pinged only on real stalls, with a summary.

**Trust layer across all four:** a "what we hold about you" panel, opt-in consent toggles, an action audit log, and a named human owner stamped on every escalation.

### How it maps to the judging criteria

| Criterion | Weight | How Rafiq wins it |
| --- | --- | --- |
| Scenario performance | 30% | Deterministic journey engine + grounded, cited answers resolve/route hidden cases (e.g. stalled visa) reliably |
| Employee experience | 25% | One companion for both journeys, bilingual, shows "what happens next"; demos as helpful and trustworthy |
| Responsible AI & privacy | 25% | Opt-in consent, employee-visible data panel, audit log, human-owned escalations — all clickable, all PDPL-aligned |
| Deployability & reuse | 10% | UAE-sovereign model path (Falcon/JAIS), in-region inference, policy-agnostic design reusable by other gov entities |
| Team & pilot readiness | 10% | Scoped to two journeys on synthetic data; deterministic core is pilot-safe next quarter |

**Build-for-the-demo priorities:** nail the two scenarios (day-5 laptop; stalled transfer/visa), make the Responsible-AI panel genuinely clickable, and show one "where journeys stall most" view. Arabic/English with RTL and a manager view for new joiners are the bonus points to add if time allows.

## The Emiratization angle (a distinctive wedge)

No global competitor is built around workforce localization, yet it is the single most UAE-specific, compliance-critical thread in the whole employee journey — and a named driver of regional HR-tech spend. Leaning into it is both a differentiator and a direct answer to the deployability/government-reuse criterion.

The mandate is real and time-boxed: private-sector firms with 50+ staff must raise their Emirati share by [2% a year toward 10% of skilled roles by end-2026](https://hyring.com/free-hr-toolkit/hr-glossary/emiratization), administered via MOHRE's Nafis platform (now extended to 2040), with [penalties of AED 96,000 per Emirati shortfall](https://en.aletihad.ae/news/uae/4539486/javasxript:). Compliance has hard, dated steps that live inside onboarding: registering Emirati hires with [GPSSA for pension within \~30 days](https://en.aletihad.ae/news/uae/4546233/javasxript:), routing salaries through the Wage Protection System, and enrolling eligible staff in Nafis benefits (salary top-up, child allowance, reduced employer pension contributions).

**Why this matters for the companion:** an Emirati joining the private sector for the first time has a different, higher-stakes onboarding — and most of its steps are exactly the deadline-driven, "who do I talk to" items the companion is built to track and cite. Surfacing GPSSA/WPS/Nafis status as first-class onboarding tasks (for the *employee*, not as a monitoring dashboard) is a feature no incumbent offers. Handled carefully and in aggregate, the same journey data also helps the entity see its localization progress — useful for Emirates and for any other UAE government entity reusing the solution.

## Use-case catalogue

The companion's surface area, grouped. Pick a handful for the demo; the breadth shows a judge this is a platform, not a one-trick bot. UAE-specific cases are flagged 🇦🇪.

### Onboarding journey

- Day-5-laptop-style checks: detect any kit/access not issued by its target day and offer to chase IT
- Pre-boarding pack before day 1: what to bring, what to expect, first-week agenda
- Visa-stage tracker 🇦🇪: entry permit → medical → Emirates ID → residence-visa stamping, with who owns each step
- Medical-fitness test booking + status 🇦🇪
- Emirates ID application/collection reminders 🇦🇪
- Labour contract / MOHRE offer explainer in plain language 🇦🇪
- Bank account + WPS salary setup guidance 🇦🇪
- Health-insurance enrolment incl. dependents
- First-day logistics: building access, badge, parking, desk, org chart
- IT provisioning status: email, VPN, systems, software licences
- Mandatory induction/training scheduling + completion nudges
- Buddy/mentor assignment and introduction
- Benefits explainer: leave, allowances, profit-share eligibility, staff-travel/flight benefits
- Probation milestones (30/60/90) and what "good" looks like
- Relocation logistics: temporary housing, shipping, driving-licence conversion 🇦🇪
- Dependent/family visa sponsorship guidance 🇦🇪
- Expat market & culture orientation (role + country + culture at once)
- First-payroll timing, deductions and gratuity explainer

### Internal-mobility journey

- Transfer-approval tracker: manager release → receiving-team approval → HR sign-off, against SLA
- Stalled-transfer / stalled-visa-on-move detection 🇦🇪
- "What changes" explainer: grade, comp, leave, reporting line on a move
- New-team onboarding checklist — the "second onboarding"
- Access re-provisioning for the new role (systems, permissions)
- Cross-emirate/country relocation: visa transfer, housing/location allowance recalculation 🇦🇪
- Notice-period and handover guidance
- "Where am I, what's next, who owns it" live status view for the move
- Target-role skill gaps and the training to close them (stretch)
- Internal opportunity visibility: roles, gigs, projects you qualify for (stretch)

### Proactive friction & early warning

- SLA-breach detection on any event vs `journey_maps.md` target
- Missed first manager 1:1 within \~5 days flag
- Training not booked by its due point
- Equipment/access not provisioned by day X
- Opt-in pulse dip → gentle check-in, optional escalation
- Repeated unanswered questions on one topic → flag a policy gap
- Probation ending without a review scheduled
- Document-expiry reminders: visa, Emirates ID, passport, contract 🇦🇪
- Approver sitting on a request → nudge the named owner

### Policy & knowledge (every answer cited)

- Leave: annual, sick, parental, Hajj, compassionate 🇦🇪
- Allowances: housing, transport, education, relocation
- Remote/hybrid and attendance policy
- Expense and travel policy
- Code of conduct / dress code
- End-of-service gratuity calculation explainer 🇦🇪
- Staff-travel / flight-benefit rules (Emirates-specific)
- Low-confidence or sensitive question → "I'm not sure" + human handoff

### Requests & routing

- Start/track IT tickets (laptop, access, software)
- Facilities requests (desk, parking, access)
- HR letters: salary certificate, NOC, employment/bank letter 🇦🇪
- Payroll queries routed to the payroll owner
- Structured handoff card to the named owner on escalation
- Multi-owner assembly: one relocation request fanned out to HR + IT + facilities

### Responsible-AI & trust

- "What we hold about you" data view the employee can open anytime
- Opt-in/opt-out consent toggles for pulse and sentiment
- Action audit log: everything the companion did on your behalf
- Named human owner stamped on every escalation
- Employee can correct or dispute data held about them
- Private pulse content never exposed to managers without consent
- Clear "this is not used for performance or discipline" boundary

### UAE-specific & Emiratization 🇦🇪

- GPSSA pension registration within \~30 days for Emirati hires — as the employee's own task, with reminders
- WPS salary-setup verification
- Nafis benefit enrolment guidance: salary top-up, child allowance, pension support
- Tailored first-time private-sector onboarding track for Emirati joiners
- Mainland vs free-zone jurisdiction clarity (who handles visa/payroll/insurance)
- Arabic-first interaction with full RTL
- Aggregate localization-progress view for the entity (never individual monitoring)

### Manager & HRBP views (nice-to-have)

- Manager view of their new joiners' progress and blockers
- HRBP early-warning queue — only real stalls, each with a summary
- Service-owner handoff inbox: complete, correctly-routed requests

### Analytics & "where journeys stall"

- Heatmap of where journeys stall most, by stage, owner or location
- SLA-breach trends by request type
- Onboarding completion funnel with drop-off points
- Cohort views to surface systemic issues (aggregate, privacy-safe)

### Stretch / future

- Multilingual beyond Arabic/English for a 160-nationality workforce
- Voice interface and delivery via Teams/WhatsApp
- Right-moment proactive nudges tied to journey stage
- Connector-ready to HRIS/ITSM (Bayanati, SuccessFactors, ServiceNow)
- Policy-agnostic template packaged for reuse by other government entities

## AI approaches in HR — taxonomy & where we sit

Vendors blur these words, so here's the honest map of every AI type used in HR/onboarding and where our companion lands. The 2026 consensus is that [these capabilities increasingly chain together](https://www.lyzr.ai/blog/ai-in-hr/) rather than compete — and that [agentic, multi-agent systems are the enterprise standard](https://www.hono.ai/blog/agentic-ai-in-hrms), governed by human gates.

| AI type | What it is | Good at | Limits | Our use |
| --- | --- | --- | --- | --- |
| Rule-based / menu bots | Scripted flows and buttons | Cheap, predictable | Brittle; breaks on free text | Avoid — too rigid for a journey |
| Conversational AI | Understands & replies in natural language | 24/7 Q&A, self-service | [Hallucinates without grounding](https://findem.ai/blog/types-of-ai-in-hr) | The chat surface |
| Generative AI | Creates text/plans from patterns | Drafts, summaries, personalized plans | Invents "facts"; no company truth | Draft plans/messages — only when grounded |
| Retrieval (RAG) | Pulls approved docs, answers from them | Accurate, cited policy answers | Only as good as the corpus | Our policy-answer layer |
| Predictive AI / ML | Forecasts from history (attrition, risk) | Early-warning scores | Opaque; data-hungry; bias risk | Light signal in the friction radar |
| Agentic / multi-agent | Plans, reasons, executes multi-step, proactively | Runs a journey end-to-end, takes action | Needs guardrails + human gates | Our core — orchestration |
| Voice AI | Speech in and out | Accessibility, deskless, hands-free | Accuracy, privacy, cost | Optional channel (Arabic/English) |

**Where we sit:** we combine RAG (grounded, cited answers) + agentic orchestration (plans and *acts*, proactively) + a light predictive/deterministic layer for friction, behind a conversational (and optionally voice) surface — all wrapped in guardrails. We deliberately reject rule-based brittleness and ungrounded generative hallucination. In one line: most incumbents are conversational-plus-a-bit-of-generative; we are agentic-on-grounded-retrieval, which is where the field is heading.

## Recommended agentic architecture

This is how the companion should work under the hood. An orchestrator routes each request to a small set of specialist agents; a friction radar feeds it proactively; everything the employee sees passes through a trust gate; and named humans own every escalation. The diagram below shows it.

&#91;embedded content: recommended architecture · orchestrator + 3 agents, grounded and gated\]

The left column is the live flow: the employee asks, the orchestrator plans and routes to the journey, policy and action agents, and the trust gate checks consent, citations and confidence before the answer returns (the dashed loop). The right column is support: the friction radar pushes stalls in proactively, the agents draw on grounded stores and system connectors, and anything needing a person goes to a named owner.

### Zoned view

The same system drawn as deployment zones — employee + channels, the companion app, and data + people — with a dot wherever personal data crosses a boundary. Connectors are synthetic in the build and live read-only in a pilot.

&#91;embedded content: zoned architecture · data crosses a boundary at each dot\]

## Proactive engine — how it actually works

Proactivity is the hardest thing to fake and the easiest to get credit for, so keep it concrete and mostly deterministic — that's also what makes it trustworthy in a live demo.

- **Event-driven core:** every journey event (offer accepted, kit issued, transfer approved) is checked against its target time in `journey_maps.md`. Past target = a flag. No ML needed — it's a rule, and a rule is explainable to a judge.
- **Scheduled sweeps:** a periodic job re-checks open requests and upcoming milestones (probation end, visa/document expiry) so nothing waits for the employee to ask.
- **Opt-in sentiment as a tie-breaker:** a consented pulse dip raises a soft flag; it never acts alone and never reaches a manager without consent.
- **Employee-first, then a human gate:** the employee sees their own blocker first and can act; only a real, persistent stall escalates to a named owner with a summary.
- **Light ML later:** once data exists, a risk score can rank the flags — but start deterministic, for trust and demo-safety.

## Voice AI — verdict

**Build text-first, add voice as an optional channel, and demo it — don't make it the core.**

Why it earns a place here: [73% of organizations are piloting voice AI for at least one HR function](https://hyring.com/free-hr-toolkit/hr-glossary/voice-ai-in-hr), its strongest value is accessibility and reach for deskless/frontline staff (cabin crew, airport agents, engineers away from a desk) and Arabic-dialect speakers, and there's regional precedent — [Menaitech's Menabot does self-service HR by voice in English and Arabic dialects](https://menaitech.com/en/news/menabot-offers-self-service-hr-via-voice-chat/), and FAHR's government assistant already offers voice.

Why not the core: voice adds speech-recognition error, privacy exposure and cost, and most onboarding/mobility tasks are better as tappable, cited, auditable text. So text-and-chat is the trustworthy default; a voice mode (Arabic/English) layered on the same agent stack is a high-impact accessibility win and a strong demo flourish — not a separate build.

## Sources

- [Leena AI vs Moveworks](https://www.leena.ai/leenaAI-vs-Moveworks) — positioning and coverage of the two leading support agents
- [Moveworks AI platform](https://www.moveworks.com/us/en/platform/moveworks-ai) — reasoning engine, inline citations
- [Gloat overview](https://us.fitgap.com/products/gloat) and [Fuel50 vs Gloat](https://www.cbinsights.com/compare/fuel50-vs-workey) — internal mobility marketplaces
- [Policy Q&A agent blueprint](https://resources.rework.com/libraries/ai-agents/ai-policy-qa-agent) — RAG stack, context, routing
- [Optimizing a retrieval-augmented QA chatbot (ACL/DaSH 2024)](https://aclanthology.org/2024.dash-1.2.pdf) — academic RAG grounding
- [Predictive onboarding analytics](https://4spotconsulting.com/unlocking-personalized-onboarding-with-predictive-analytics/) and [HR analytics retention strategies](https://4spotconsulting.com/predictive-hr-analytics-safeguarding-talent-for-strategic-advantage/) — early-churn signals
- [Emirates Group 2025–26 workforce](https://www.khaleejtimes.com/business/aviation/jobs-in-uae-emirates-group-hires-9700-employees-from-35-million-applications) and [HR / diversity profile](https://unleash.ai/employee-experience-and-engagement/interview/emirates-hr-tech-enabled-post-pandemic-bounce-back)
- [Emirates EVP HR / Josh Bersin HR Pacesetter 2026](https://ae.linkedin.com/in/sumithp)
- [UAE PDPL business guide](https://uppersetup.com/en/article/uae-personal-data-protection-law-pdpl-the-complete-business) and [UAE AI governance (PDPL, DIFC, ethics)](https://captaincompliance.com/education/uaes-ai-governance-laws-pdpl-difc-rules-and-human-centric-principles/)
- [UAE Federal Authority for AI and Data, June 2026](https://www.morganlewis.com/pubs/uae-establishes-federal-authority-for-artificial-intelligence-and-data)
- [Falcon-H1 Arabic (TII)](https://www.businesswire.com/news/home/20260105343577/en) and [JAIS bilingual model (G42/Core42)](https://enterpriseam.com/uae/issues/uae-launches-new-ai-model-to-rival-big-tech/)

* [GCC HR-tech market CAGR (IMARC via People Matters)](https://www.peoplematters.in/news/hr-technology/gcc-hr-tech-market-expected-to-grow-at-945percent-cagr-through-2034-imarc-49711) and [GCC HRMS market size](https://www.marknteladvisors.com/research-library/gcc-human-resource-management-system-market-study.html)
* [Emirates Group Glassdoor reviews](https://static.glassdoor.com.ar/Reviews/The-Emirates-Group-Reviews-E23433_P7.htm) — rating, recommend rate, review themes
* [Bayt/YouGov: UAE professionals would quit for career development](https://www.thenational.ae/uae/most-uae-professionals-would-quit-jobs-for-better-career-development-survey-1.194197)
* [Robert Walters ME 2026: employees want more from reviews](https://www.khaleejtimes.com/business/uae-employees-want-more-from-performance-reviews-than-just-salary-says-new-report)
* [GCC Salary Guide: 98% open to changing jobs in 2026](https://me.peoplemattersglobal.com/news/recruitment/nearly-all-uae-employees-are-ready-to-change-jobs-in-2026-and-pay-is-only-part-of-the-story-48326)
* [Gulf News: UAE employees on AI and benefits](https://gulfnews.com/gn-focus/uae-employees-are-unfazed-by-ai-but-demand-better-benefits-from-employer-1.1731657648429)
* [Robert Walters UAE: 1 in 4 juniors consider quitting over poor onboarding](https://www.khaleejtimes.com/uae/junior-employees-quitting-poor-onboarding-report-finds)
* [Jobbatical: relocation challenges — visa the hardest part](https://www.jobbatical.com/blog/what-international-employees-are-struggling-with) and [Talentera: UAE day-one onboarding playbook](https://www.talentera.com/en/blog/welcome-new-employee-in-the-uae-day-one-experience/)

- [Bayzat (GCC HR suite + Bayzat AI)](https://yespress.io/bayzat) and [Darwinbox MENA/DIFC](https://www.gccbusinessnews.com/hr-tech-unicorn-darwinbox-boosts-its-mena-presence-with-new-difc-office/)
- [Top HR software UAE & Middle East 2026 (OrangeHRM/Citra, PeopleStrong Jinie)](https://www.orangehrmlive.com/resources/blog/top-ten-hr-software-in-the-uae-and-middle-east-2026)
- [UAE FAHR AI HR Assistant (Bayanati, 50k federal employees)](https://gulfnews.com/uae/government/uae-launches-ai-powered-hr-assistant-to-transform-government-services-1.500264344)
- [Emiratization overview (targets, Nafis, penalties)](https://hyring.com/free-hr-toolkit/hr-glossary/emiratization) and [GPSSA 30-day registration via Nafis](https://en.aletihad.ae/news/uae/4546233/javasxript:)

* [AI in HR: four capability types (Lyzr)](https://www.lyzr.ai/blog/ai-in-hr/) and [types of AI in HR (Findem)](https://findem.ai/blog/types-of-ai-in-hr)
* [Agentic AI as the 2026 HRMS standard, human gates (HONO)](https://www.hono.ai/blog/agentic-ai-in-hrms)
* [Voice AI in HR — adoption & use cases](https://hyring.com/free-hr-toolkit/hr-glossary/voice-ai-in-hr) and [Menaitech Menabot: Arabic/English voice HR](https://menaitech.com/en/news/menabot-offers-self-service-hr-via-voice-chat/)
