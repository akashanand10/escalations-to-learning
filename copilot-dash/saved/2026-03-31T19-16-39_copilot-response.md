# Copilot Response

_Saved: 4/1/2026, 12:46:39 AM_

---

## 1
            Step 1: Feb vs March Trend Comparison

Here's the comparison between February and March 2026:

---

## Feb → March Escalation Comparison

### 📊 Overall Volume
**Feb: 24 tickets → March: 21 tickets (↓ 12.5%)**

---

### ✅ Improved Areas

| Area | Feb | March | Notes |
|---|---|---|---|
| **Bills – Approval/POA** | 7 | 4 | ↓ 43% — the Feb Send Back/resubmit regression (4 tickets, single root cause) was reverted and resolved |
| **Bills – Archiving/Ledger** | 3 | 0 | Fully resolved — the LE edit validation hotfix (Feb 17) cleared the wave |
| **Reports/Exports** | 1 | 0 | Payment completion date export bug fixed |
| **Inbox – Permissions** | 2 | 0 | Upload Invoices visibility bug fixed in Feb; didn't recur |

---

### ❌ Got Worse

| Area | Feb | March | Notes |
|---|---|---|---|
| **Bills – Create/Edit** | 2 | 4 | Doubled — 2 of 4 are Cloudflare WAF blocking PDF uploads (new infra pattern) |
| **Bills – Drafts** | 1 | 2 | Draft currency fix didn't prevent new draft visibility and deletion issues |
| **Inbox** | 1 | 3 | New issue types: OCR timeout on large PDFs, email suppression after offboarding, R15 memory quota outage |

---

### 🆕 New Categories in March

- **Vendor Credits** — silent upload failure with no user-facing error (BP-7878)
- **Cloudflare/Infrastructure** — WAF blocking specific PDFs became a recurring theme (2 tickets); R15 memory quota outage hit inbox ingestion
- **Payments – Notifications** — POA-marked bills still triggering payment reminder emails
- **Bills – Tags/Line Items** — DB timeout from uncapped 700k NetSuite tag fetch

---

### Key Takeaways

1. **The big Feb regressions are gone.** The archiving bug wave and Send Back resubmit failures don't appear in March — hotfixes held.
2. **Cloudflare WAF is emerging as a recurring infra risk** — it hit twice in March across different endpoints. Worth a proactive review.
3. **Permissions bugs keep surfacing in new places** — inbox permissions (Feb), draft visibility (March). There may be a systemic gap in how permission scoping is applied to new features.
4. **Payments volume is stable** (~6–7 tickets/month) with no single dominant root cause — spread across cards, FX, approvals, notifications.
5. **Inbox issues shifted character** — permissions cleaned up but operational issues (OCR limits, email suppression, platform memory) are the new concern.



## 2
            Step 2: Identify Escalation Hotspots

Here are the top 5 escalation hotspots across both months (45 total tickets):

---

## 🔥 Top 5 Recurring Escalation Hotspots

---

### #1 — Bills: Approval & POA · 10 tickets
**Feb:** BP-7829, BP-7776, BP-7775, BP-7742, BP-7733, BP-7746, BP-7662  
**Mar:** BP-7930, BP-8007, BP-7852

**Recurring patterns:**
- Closed posting period / amortization preventing bill resubmission after send-back (4 Feb tickets, single root cause wave)
- Slack approval path missing `handle_paid_outside_airbase` logic → bills not auto-marked POA (Mar BP-7852)
- R&A framework bug: re-added approved user stuck as pending (Mar BP-7930)
- Approval UI showing incorrect PO match data (Mar BP-8007)

**Preventive actions:**
1. **Gate resubmission earlier.** Validate posting period lock and amortization status *before* send-back is permitted — surface the blocker to the approver at send-back time, not to the submitter on resubmit.
2. **Audit all approval paths for POA parity.** Slack, email, and direct UI approvals should all funnel through the same `handle_paid_outside_airbase` logic. Add a coverage test that simulates each approval channel and asserts POA flag is set.
3. **Add an R&A state machine test.** The "re-added user stuck as pending" bug suggests state transitions aren't fully covered — add an integration test for the re-add → approve → payment flow.
4. **Alert on approval queue depth.** Escalations from this area are usually user-blocking. A queue depth or SLA breach alert would surface these before they become escalations.

---

### #2 — Payments (all types) · 11 tickets
**Feb:** BP-7828, BP-7777, BP-7722, BP-7725, BP-7670, BP-7845, BP-7767  
**Mar:** BP-8019, BP-7924, BP-7917, BP-7970, BP-7856, BP-7872

**Recurring patterns:**
- Null reference crashes (`payment.subsidiary.id`, "Cannot convert undefined or null to object") — 2 separate tickets
- FX/Corpay transient failures blocking payment initiation (2 tickets)
- International payment validation gaps: virtual card selected for non-USD bills (Mar BP-7856)
- Payment state display corruption from partial-payments migration (Mar BP-7917)
- POA bills still triggering payment reminder emails (Mar BP-7970)

**Preventive actions:**
1. **Defensive null guards on payment objects.** Two separate null-reference crashes in two months in the payment flow — add a lint/type rule requiring null-checked access on `subsidiary`, `payer`, and `payment_method` fields. Add unit tests for null/missing subsidiary on payment grouping.
2. **Corpay circuit breaker.** FX failures are transient but user-blocking. Wrap Corpay calls in a retry with exponential backoff and expose a degraded-mode UX ("FX rates temporarily unavailable, retry in X min") instead of a silent freeze.
3. **International payment method validation.** Assert at proposal-build time that virtual cards are never selected for non-USD bills — this is a constraint that should be a pre-condition, not a failure mode.
4. **POA reminder exclusion test.** Add a unit test that asserts bills with `paid_outside_airbase = true` are excluded from the payment reminder email job.
5. **Post-migration reconciliation job.** After the partial-payments migration, a standing data-consistency job (or one-time audit) would catch stuck "Payment Initiated" states before customers report them.

---

### #3 — Inbox · 6 tickets
**Feb:** BP-7780, BP-7674, BP-7672  
**Mar:** BP-8006, BP-7983, BP-7959

**Recurring patterns:**
- Permission scoping: "Upload Invoices" users seeing all invoices across subsidiaries (Feb, 2 tickets — same root cause)
- Vendor email not suppressed after offboarding (Mar BP-8006)
- OCR timeout on large PDFs (Mar BP-7983)
- R15 memory quota outage causing email processing delay (Mar BP-7959)

**Preventive actions:**
1. **Permissions regression test suite for inbox.** The Feb upload-visibility bug affected 2 tickets and a March draft-visibility bug hit a different area. There's a gap in permission-scope test coverage — add explicit tests asserting subsidiary and ownership scoping for every inbox role.
2. **Vendor offboarding checklist.** Add a step to the offboarding flow (or a post-offboard async job) that disables inbox routing for that vendor's email domain/address. Add an integration test that confirms offboarded vendor emails are rejected.
3. **OCR page-count pre-check.** Before submitting to Veryfi, check PDF page count. Over a threshold (e.g. 20 pages), skip OCR and queue for manual review or chunked processing — don't let large files silently timeout.
4. **R15 memory quota alerting.** Add a Datadog/PagerDuty alert when R15 worker memory approaches quota so on-call can respond before the queue backup causes customer-visible delays.

---

### #4 — Bills: Create/Edit · 6 tickets
**Feb:** BP-7690, BP-7782  
**Mar:** BP-7933, BP-7932, BP-7871, BP-7982

**Recurring patterns:**
- Cloudflare WAF blocking specific PDFs on upload/replace (2 Mar tickets, different endpoints — same infra cause)
- Null `gl_currency` from Subsidiary V2 API (Mar BP-7933)
- Tax type display field bug: `name` vs `display_name` (Feb BP-7782)
- Duplicate invoice number validation missing from edit path (Mar BP-7982)

**Preventive actions:**
1. **Proactive Cloudflare WAF audit.** WAF hit two different bill endpoints in one month — it's a pattern, not a one-off. Run a sweep of all file-upload endpoints against the WAF ruleset with representative PDF samples. Work with the infra team to create a test suite for WAF rules before deployment.
2. **API contract validation for Subsidiary V2.** The `gl_currency` null return was a silent regression from an API update. Add contract tests (e.g. Pact) between the bills service and Subsidiary V2 so nullable fields are caught before reaching production.
3. **Parity test: create vs edit paths.** Two separate bugs (duplicate validation, LE edit validation) existed on one path but not the other. Add a test matrix explicitly asserting business rules are applied consistently across create, edit, and resubmit paths.
4. **Display field enumeration.** `name` vs `display_name` is a recurring class of bug in UI code. Audit all bill form fields for consistent use of display-friendly field names; add a linter or type wrapper that enforces `display_name` for user-facing labels.

---

### #5 — Bills: Drafts · 3 tickets (both months)
**Feb:** BP-7757  
**Mar:** BP-8024, BP-7859

**Recurring patterns:**
- Vendor auto-fill overwriting saved draft currency (Feb BP-7757)
- Draft bills visible to all "Create Bills" users, not scoped to owner (Mar BP-7859)
- Draft deletion broken with no identified root cause (Mar BP-8024)

**Preventive actions:**
1. **Draft mutation contract.** Define which fields a vendor auto-fill is *allowed* to overwrite on load (e.g. vendor name, address) vs which must be preserved (e.g. user-set currency). Enforce this in a unit test: "loading a vendor on a draft with an existing currency must not change the currency."
2. **Draft visibility scoping test.** Add an explicit test asserting that a user with "Create Bills" can only list their own drafts — not drafts owned by others. This is analogous to the Feb inbox permissions bug and suggests a shared gap in row-level ownership enforcement.
3. **Draft deletion smoke test.** Add a basic end-to-end test covering draft creation → deletion. The BP-8024 root cause being "not yet identified" suggests there's no test that would have caught a deletion regression.
4. **Unified ownership middleware.** Both the inbox and drafts visibility bugs are ownership-scoping failures. Consider a shared middleware/decorator for "owned resources" that enforces user-id filtering at the query level, rather than relying on each feature area to implement it independently.

---

## Summary Table

| # | Area | Total Tickets | Both Months? | Primary Risk |
|---|------|:---:|:---:|---|
| 1 | Bills – Approval/POA | 10 | ✅ | State machine gaps, approval path parity |
| 2 | Payments | 11 | ✅ | Null refs, Corpay reliability, migration debt |
| 3 | Inbox | 6 | ✅ | Permission scoping, infra headroom |
| 4 | Bills – Create/Edit | 6 | ✅ | Cloudflare WAF, API contract drift |
| 5 | Bills – Drafts | 3 | ✅ | Ownership scoping, mutation contracts |

**Cross-cutting theme:** Permission/ownership scoping failures appear in Inbox (#3), Drafts (#5), and Approval (#1). A shared ownership-enforcement layer would address bugs across all three areas simultaneously.