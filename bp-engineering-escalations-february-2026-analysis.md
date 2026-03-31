# BP Engineering Escalations Analysis (February 2026)

Query used:

```jql
created >= "2026-02-01"
and project = BP
and type = "Engineering Escalation"
and created <= "2026-02-28"
ORDER BY key DESC
```

Total tickets found: 24

Note: Update history below is based on ticket creation metadata and comment timelines from Jira.

---

Issue: https://paylocity.atlassian.net/browse/BP-7829 — Bills > Retrieve Changes Done to Bill Prior Rejection

Customer/Account: Headspace (Prod)

Product Area: Bills (Approval/POA)

Priority: Medium | Status: In Progress | Owner: Gayathri Nair

Issue Summary: PO auto-detachment on bill rejection is expected behavior. Secondary issue discovered — the approver name field is blank in the "Denied Bills" tab for Slack-based rejections, suggesting the actor name is not being captured for that rejection channel.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-26
- Gayathri Nair investigated and found the PO was automatically detached by the system on bill rejection (expected behavior); confirmed bill was rejected via Slack by user Annie Crook based on audit events
- Customer (via Pattie Espinosa-Alex) reported the approver name field is blank in the "Denied Bills" tab for this bill; Gayathri Nair clarified the rejection was recorded but the Denied tab appears to not show the actor name for Slack-based rejections

Next action: Clarify whether blank approver name in the Denied Bills tab for Slack-rejected bills is expected behavior, and communicate findings to customer; Owner: Gayathri Nair

---

Issue: https://paylocity.atlassian.net/browse/BP-7828 — Payments > Initiating Payment in List Page Returns Error "Cannot read properties of undefined (reading 'id')"

Customer/Account: 37th Parallel Properties (Prod)

Product Area: Payments

Priority: Medium | Status: Done | Owner: Sarthak Vashisht

Issue Summary: Null reference error in payment list page when a payment's subsidiary object is missing. The `groupedBySubsidiary[payment.subsidiary.id]` call threw because `.id` was null. Null check fix deployed.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-26
- Gayathri Nair identified a null reference in the subsidiary grouping logic (`groupedBySubsidiary[payment.subsidiary.id]` — `.id` null when subsidiary is missing); escalated to Sagar Parthasarathy / Utkarsh Saraogi
- Sagar Parthasarathy confirmed it was the same as a prior known issue; Sarthak Vashisht raised and merged a fix for the null check exception
- Sarthak Vashisht: marked done after fix deployed

Next action: Resolved — null check exception in payment list's subsidiary grouping fixed; Owner: Sarthak Vashisht

---

Issue: https://paylocity.atlassian.net/browse/BP-7789 — Reports > All Bills Export Payment Completion Date Blank

Customer/Account: Domino Data Lab (Prod)

Product Area: Reports / Exports

Priority: Medium | Status: Done | Owner: Gayathri Nair

Issue Summary: In partial payment scenarios with multiple vendor-payments, the "Payment Completion Date" column in the All Bills Export was blank. Root cause: the date was sourced from the last vendor-payment sorted by initiation date — if that payment had no initiation date set, the field came out blank. Fix deployed 2026-02-26.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-23
- Gayathri Nair: RCA — in partial payment scenarios with multiple vendor-payments, the payment completion date is populated from the last vendor-payment ordered by initiation date; if that last payment had no initiation date set, it caused the completion date to be blank in the export
- Fix deployed 2026-02-26

Next action: Resolved — payment completion date now correctly populated in All Bills Export for partial payment scenarios; Owner: Gayathri Nair

---

Issue: https://paylocity.atlassian.net/browse/BP-7780 — Inbox > Update Forwarding Email for UK Subsidiary

Customer/Account: Bounteous (Prod)

Product Area: Inbox

Priority: Medium | Status: Done | Owner: Yash Soni

Issue Summary: Customer requested inbox forwarding email update after a subsidiary name change. The email follows a fixed system-generated pattern and cannot be customized. Forwarding email had already been updated via PDCM on Feb 17.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-20
- Customer requested updating the inbox forwarding email for their UK subsidiary after a subsidiary name change
- Abhishek Kumar clarified the email must follow the pattern `<company>+<subsidiary>+invoices@airbase-mail.com` and cannot be customised; there is no way to redirect from a custom email alias
- Yash Soni confirmed the subsidiary's forwarding email was already updated on Feb 17 via PDCM from `bounteous-uk-ltd+bounteous+invoices@airbase-mail.com` to `ap.uk+bounteous+invoices@airbase-mail.com` in reference to a prior ticket

Next action: Resolved — forwarding email update confirmed; customer informed to use the system-generated address format; Owner: Yash Soni

---

Issue: https://paylocity.atlassian.net/browse/BP-7777 — UI > Payment Tabs Overlapping with Export Window

Customer/Account: Team Cymru (Prod)

Product Area: Payments

Priority: Medium | Status: Done | Owner: Sagar Parthasarathy

Issue Summary: Minor CSS issue caused payment tabs to overlap the export window on the payments page. Style fix deployed.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-19
- Sagar Parthasarathy identified a minor CSS style issue causing payment tabs to overlap the export window; fixed via style update

Next action: Resolved — style fix deployed; Owner: Sagar Parthasarathy

---

Issue: https://paylocity.atlassian.net/browse/BP-7776 — Bills > Resubmitting Sent Back Bill Returns Error "Submit Validation Failed"

Customer/Account: Action Behavior Centers (Prod)

Product Area: Bills (Approval/POA)

Priority: High | Status: Done | Owner: Abhishek Kumar

Issue Summary: Resubmitting a sent-back bill failed because the posting period was closed, making the ledger entry non-editable. Change reverted to restore previous resubmit behavior; workaround (reopen posting period and unlock AP) communicated to customer.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-19
- Abhishek Kumar: root cause — posting period is closed, so the ledger entry is not editable, which blocks bill resubmission
- Alternate solution communicated to customer: reopen the posting period and unlock AP in the GL
- Abhishek Kumar: underlying change reverted ~Feb 20, restoring previous resubmit behavior

Next action: Resolved — change reverted; posting period workaround communicated; longer-term fix (disable Send Back for non-editable bills with tooltip) tracked separately; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7775 — Bills > Resubmitting Sent Back Bill Returns Error "Submit Validation Failed"

Customer/Account: Domino Data Lab (Prod)

Product Area: Bills (Approval/POA)

Priority: High | Status: Done | Owner: Abhishek Kumar

Issue Summary: Amortization enabled on the bill prevented ledger entry edits, blocking bill resubmission after send-back. Change reverted ~Feb 20 to restore the resubmit path.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-19
- Abhishek Kumar: amortization is enabled on the bill, which prevents ledger entry edits and blocks resubmission
- Change reverted ~Feb 20; issue resolved

Next action: Resolved — change reverted restoring resubmit path; longer-term UI improvement to disable Send Back for non-editable bills is tracked for next sprint; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7757 — Bills > Drafts > Draft Currency Reverts to Vendor Preferred instead of Saved Currency

Customer/Account: ACAMS (Prod)

Product Area: Bills (Drafts)

Priority: Medium | Status: Done | Owner: Sarthak Vashisht

Issue Summary: When reopening a draft bill, the vendor auto-fill logic was overriding the saved draft currency with the vendor's preferred currency. Fix skips vendor-triggered currency update when the invoice already has a saved draft. Deployed 2026-02-23.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-17
- Gayathri Nair: the draft API saves the correct currency, but on reload the vendor auto-fill logic overrides it with the vendor's preferred currency; assigned to Sarthak Vashisht
- Sarthak Vashisht: raised PR — skips currency update on vendor load when invoice already has a draft bill; fix deployed 2026-02-23

Next action: Resolved — vendor auto-fill no longer overrides saved draft currency; Owner: Sarthak Vashisht

---

Issue: https://paylocity.atlassian.net/browse/BP-7746 — Approval > Dynamic Approval Restarting Despite All Toggles are Off

Customer/Account: RPA (Prod)

Product Area: Bills (Approval/POA)

Priority: Medium | Status: Done | Owner: Smita Shankar

Issue Summary: Confirmed expected behavior — approval restart is determined by the delegate's active time window at bill-edit time, not by the toggle state at resubmit time. No code change required.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-16
- Smita Shankar: both reported scenarios (approval restart and spend owner change) are expected behavior — approval restart depends on the delegate's active time window at the time the bill was edited, regardless of toggle state at time of resubmit
- Explanation relayed to customer

Next action: Resolved — behavior confirmed as expected; explanation communicated to customer; Owner: Smita Shankar

---

Issue: https://paylocity.atlassian.net/browse/BP-7745 — Bills > Archiving Bill Returns Error "Ledger entry 21520834 is not editable."

Customer/Account: ESO Solutions Inc (Prod)

Product Area: Bills (Archiving/Ledger)

Priority: High | Status: Done | Owner: Gayathri Nair

Issue Summary: Archiving failed for bills with Airbase amortization/prepayment entries or closed/locked posting period due to the LE edit validation incorrectly blocking the archival path. Hotfix deployed 2026-02-17.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-16
- Gayathri Nair: hotfix deployed to prod 2026-02-17; customer asked to retry

Next action: Resolved — hotfix deployed allowing archiving of bills with Airbase amortization/prepayment entries or closed/locked posting period; Owner: Gayathri Nair

---

Issue: https://paylocity.atlassian.net/browse/BP-7744 — Bills > Archiving Bill Returns Error "Ledger entry 20510904 is not editable."

Customer/Account: BlueConic (Prod)

Product Area: Bills (Archiving/Ledger)

Priority: High | Status: Done | Owner: Gayathri Nair

Issue Summary: Same archiving issue as BP-7745 — LE edit validation blocked archival for bills with amortization or locked posting period. Same hotfix deployed 2026-02-17.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-16
- Gayathri Nair: same hotfix as BP-7745 deployed to prod 2026-02-17

Next action: Resolved — same hotfix resolves archiving failure for bills with amortization or locked posting period; Owner: Gayathri Nair

---

Issue: https://paylocity.atlassian.net/browse/BP-7742 — Bills > Resubmitting Sent Back Bill Returns Error "Submit Validation Failed"

Customer/Account: ESO Solutions Inc (Prod)

Product Area: Bills (Approval/POA)

Priority: High | Status: Done | Owner: Abhishek Kumar

Issue Summary: Amortization on the bill blocked ledger entry edits, preventing resubmission after send-back. Change reverted ~Feb 20. UX improvement (disable Send Back button + tooltip for non-editable bills) added to sprint backlog.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-16
- Gayathri Nair: identified same root cause (amortization + locked posting period blocks ledger edits); proposed two workarounds — unlock posting period in GL and resync, or edit posting period via PDC
- Smita Shankar and Gayathri Nair discussed longer-term fix: the Send Back action should be disabled for non-editable bills
- Abhishek Kumar: amortization on this bill confirmed as blocking LE edit; change reverted ~Feb 20

Next action: Resolved — change reverted; Send Back / resubmit UX improvement (disable button + tooltip) added to sprint backlog; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7733 — Bills > Unable to Resubmit Sent Back Bill

Customer/Account: Emergetech (Prod)

Product Area: Bills (Approval/POA)

Priority: High | Status: Done | Owner: Abhishek Kumar

Issue Summary: Posting period was locked and Airbase was not syncing the updated unlock status from GL, blocking bill resubmission. Multiple sub-issues: edit URL param inconsistency and permission gaps. Customer used workaround (archive + recreate). Sprint tickets created to disable Send Back/Edit for non-editable bills.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-13
- Sagar Parthasarathy: posting period locked; investigated why it remained locked even after customer unlocked in GL — Airbase was not syncing the updated status
- Multiple sub-issues: (1) posting period lock blocking resubmit, (2) edit URL param inconsistency, (3) permission inconsistency for users without clicking Edit button
- Gayathri Nair and Sagar Parthasarathy: `is_editable` field needed in bill listing API to disable Edit CTA from the list page; assigned as follow-up
- Customer ultimately archived the bill and created a new one as a workaround
- Smita Shankar (post-resolution): requested next sprint tickets to disable Send Back and Edit buttons for locked/amortized bills with tooltip messaging; FE and BE tickets created by Sagar Parthasarathy

Next action: Customer unblocked via workaround; sprint tickets created to disable Send Back/Edit for non-editable bills with proper tooltip; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7725 — Payments > Cards were Overcharged and Stuck in Unpaid Status

Customer/Account: Nitti Sanitation (Prod)

Product Area: Payments (Cards)

Priority: High | Status: Done | Owner: Von Miguel Medeza

Issue Summary: Virtual cards were overcharged and stuck in unpaid status. Issue addressed with payment processor.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-12
- Abhishek Kumar pointed to a related Slack thread with context on the overcharge and stuck status

Next action: Resolved — card overcharge and unpaid status issue addressed; Owner: Von Miguel Medeza

---

Issue: https://paylocity.atlassian.net/browse/BP-7724 — Bills > Archiving Bill Returns Error "Ledger entry 21721905 is not editable"

Customer/Account: Neogov (Prod)

Product Area: Bills (Archiving/Ledger)

Priority: High | Status: Done | Owner: Gayathri Nair

Issue Summary: LE edit validation was incorrectly applied to the archival path, blocking archiving for bills with Airbase prepayment/amortization entries or closed/locked posting period. NetSuite amortization was not affected. Fix deployed ~Feb 17.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-12
- Abhishek Kumar: the LE edit validation was incorrectly applied to the archival path; raised a fix
- Gayathri Nair: fix deployed ~Feb 17; RCA documented — the error affected bills with Airbase prepayment/amortization (prepayment entries already generated) or closed/locked posting period; NetSuite amortization not affected

Next action: Resolved — fix deployed; archiving of amortized and locked-period bills now works correctly; Owner: Gayathri Nair

---

Issue: https://paylocity.atlassian.net/browse/BP-7722 — Payments > Payment Approvals > Payment Run Stuck in Pending

Customer/Account: US HealthConnect (Prod)

Product Area: Payments (Approvals)

Priority: Medium | Status: Done | Owner: Sagar Parthasarathy

Issue Summary: Inactive payer bank account caused payment run to get stuck in pending. Secondary issue: bill detail page was blocked from opening when payer bank error was present. Fix deployed to allow viewing bill details while blocking only payment initiation.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-12
- Von Miguel Medeza: root cause 1 — missing GL Funding Account (payer bank account inactive) caused payment run to be stuck
- Abhishek Kumar confirmed payer bank account was inactive
- Root cause 2 — bill detail page was also blocked from opening when payer bank error was present (existing behavior)
- Sarthak Das and Sagar Parthasarathy: product decision to remove block on opening bill detail page; payment initiation blocked but viewing should remain possible; fix deployed ~Feb 17

Next action: Resolved — payer bank configuration corrected; bill detail page no longer blocked by payer bank error; Owner: Sagar Parthasarathy

---

Issue: https://paylocity.atlassian.net/browse/BP-7690 — Bills > Editing Bills Returns "Oops! Something went wrong."

Customer/Account: GHC (Prod)

Product Area: Bills (Create/Edit)

Priority: Medium | Status: Done | Owner: Abhishek Kumar

Issue Summary: Intermittent "Something went wrong" error when editing bills. No API failures found in logs; issue self-resolved. Flagged as a recurring bug to monitor.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-11
- Abhishek Kumar: no API failures observed in the past week; issue appeared intermittent and may be ISP-related
- Von Miguel Medeza: confirmed issue self-resolved for the customer; flagged as a recurring bug to monitor

Next action: Monitor for recurrence; no root cause identified — likely intermittent; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7674 — Inbox > Invoices > UMI Fund - issue with invoices showing in Bill Inbox in Airbase

Customer/Account: RPA / UMI Fund (Prod)

Product Area: Inbox (Visibility/Permissions)

Priority: Medium | Status: Done | Owner: Jose Darwin Doniego

Issue Summary: Three sub-issues: (1) cross-subsidiary invoices appearing in inbox — expected behavior; (2) users with only "Upload Invoices" permission seeing all invoices instead of own uploads — permissions bug fixed ~Feb 17; (3) disputed upload attribution — audit logs confirmed user did upload from the platform.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-09
- Three sub-issues: (1) invoices appearing from outside subsidiary — confirmed expected (email sent to subsidiary-specific email address); (2) users seeing invoices they didn't upload despite having only Upload Invoices permission — confirmed as a permissions bug; (3) two invoices attributed to Kanchan Kapoor who disputes uploading them — audit and logs confirm the user uploaded them from the platform
- Abhishek Kumar: deployed fix for issue 2 based on Smita Shankar's permission matrix — users with only Upload Invoices permission now see only their own uploads; deployed ~Feb 17
- March follow-up: customer pushed back on attribution; Abhishek Kumar confirmed audit trail (uploaded from AB platform, separately, Jan 13 in user timezone)

Next action: Audit evidence shared with CS team for customer communication; permission fix confirmed live; Owner: Jose Darwin Doniego

---

Issue: https://paylocity.atlassian.net/browse/BP-7781 — Bill entry > Tax Type is not shown once Tax Code has been applied

Customer/Account: Mind Gym (Prod)

Product Area: Bills (Create/Edit)

Priority: Medium | Status: Done | Owner: Sagar Parthasarathy

Issue Summary: After applying a tax code, the tax type was not displayed. Root cause: frontend was using the `name` field (e.g. "S-SG") instead of `display_name` (e.g. "GST_SG:S-SG (7.000%)") on the tax rate object. Fix deployed ~Feb 27.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-06
- Multiple teams investigated; Siddharth Deshpande identified root cause: frontend using `name` field instead of `display_name` on the tax rate object; `display_name` (e.g. `GST_SG:S-SG (7.000%)`) includes tax type and rate while `name` (e.g. `S-SG`) does not
- Ashwin Kailas confirmed `display_name` should be used consistently across dropdown and line item table
- Sagar Parthasarathy: raised PR; fix deployed ~Feb 27

Next action: Resolved — frontend now displays `display_name` for tax codes, ensuring tax type is visible after selection; Owner: Sagar Parthasarathy

---

Issue: https://paylocity.atlassian.net/browse/BP-7767 — Currency Option Missing (USD)

Customer/Account: Virtus (Prod)

Product Area: Payments

Priority: Medium | Status: Done | Owner: Karan Suthar

Issue Summary: Expected behavior — the bill was GBP-denominated, so only GBP payment was available. USD payment is only supported for USD-denominated invoices. No code change required.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-06
- Customer unable to pay vendor The Economist Group in USD; vendor's preferred currency is GBP
- Karan Suthar: confirmed expected behavior — the bill is GBP-denominated and only GBP payment is available; USD payment is only available for USD-denominated invoices

Next action: Resolved — expected behavior confirmed and communicated to customer; Owner: Karan Suthar

---

Issue: https://paylocity.atlassian.net/browse/BP-7672 — Inbox > User Visibility into All Invoices

Customer/Account: Trail Blazers (Prod)

Product Area: Inbox (Visibility/Permissions)

Priority: Highest | Status: Done | Owner: Abhishek Kumar

Issue Summary: Users with "Upload Invoices" permission could see all invoices across subsidiaries instead of only their own uploads. Permission matrix corrected: Upload Invoices = own uploads only; Manage Inbox = all invoices in allowed subsidiaries. Fix deployed Feb 7 with edge-case cleanup Feb 17.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-05
- User with Spend Access to 6 subsidiaries was able to see all invoices across those subsidiaries despite having only "Upload Invoices" permission; should only see their own uploads
- Abhishek Kumar and Smita Shankar aligned on permission matrix: Upload Invoices = own uploads only; Manage Inbox = all invoices in allowed subsidiaries
- Abhishek Kumar: raised PR and deployed fix Feb 7; additional cleanup deployed Feb 17 to cover remaining permission edge cases

Next action: Resolved — inbox visibility correctly scoped per permission level; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7670 — Payments > Cannot Initiate Payment and Returns the Error "Couldn't Update Exchange Rate"

Customer/Account: Aurora Solar (Prod)

Product Area: Payments (FX/International)

Priority: High | Status: Done | Owner: Harshit Gupta

Issue Summary: Corpay returned "client access disabled" when attempting to update the FX exchange rate, blocking payment initiation. Transient Corpay-side issue; resolved on retry.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-05
- Harshit Gupta: Corpay returned "client access disabled" when attempting to update the exchange rate; Corpay requested a retry
- Payments processed individually after retry; issue resolved

Next action: Resolved — Corpay transient access issue self-resolved; payments initiated individually; Owner: Harshit Gupta

---

Issue: https://paylocity.atlassian.net/browse/BP-7845 — Vendor payment freezes for Vendor: Ross Brooke

Customer/Account: Bolt Financials (Prod)

Product Area: Payments (FX/International)

Priority: Medium | Status: In Progress | Owner: Roopak A N

Issue Summary: Clicking "Pay in GBP" caused the page to freeze because the `spot_rate` API was failing, preventing the FX rates modal from opening. UI freeze fix deployed. Root issue: Corpay account closed due to inactivity — re-onboarding in progress.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-03
- Clicking "Pay in GBP" causes the page to freeze; SaiKrishna identified root cause: `spot_rate` API failing, preventing FX rates modal from opening; VM team does not own the affected code
- Manishwar Segu: fixed the UI freeze (loader was indefinitely blocking on `spot_rate` API failure); deployed fix
- Roopak A N: Corpay confirmed Bolt Financial Limited's account was closed in Sept 2025 due to inactivity; needs to submit new onboarding documents to Corpay to re-enable
- Awaiting confirmation from onboarding team as of late March

Next action: Await completion of Bolt Financials' Corpay re-onboarding; UI freeze fix already deployed; Owner: Roopak A N

---

Issue: https://paylocity.atlassian.net/browse/BP-7662 — Bills > Approved Bill Not Moving to Payment Queue (Bill #12092025_JL)

Customer/Account: RPA (Prod)

Product Area: Bills (Approval/POA)

Priority: Medium | Status: Done | Owner: Abhishek Kumar

Issue Summary: Approved bill was not appearing in the payment queue. Investigation confirmed the bill was correctly approved and no system issue was found — data consistency was already restored by the existing PDC `ApproveBillIfNoPending` task.

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-02-02
- Abhishek Kumar: logs confirm bill status was correctly updated to Approved on Jan 8 when the last approver approved; no race condition detected; PDC `ApproveBillIfNoPending` task had already run; no further action possible

Next action: Resolved — bill confirmed approved; no system issue found; data consistency was restored by existing PDC task; Owner: Abhishek Kumar
