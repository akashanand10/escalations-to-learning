# BP Engineering Escalations Analysis (March 2026)

Query used:

```jql
created >= "2026-03-01"
and project = BP
and type = "Engineering Escalation"
and created <= "2026-03-31"
ORDER BY key DESC, created DESC
```

Total tickets found: 21

Note: Update history below is based on ticket creation metadata and comment timelines from Jira.

Issue: https://paylocity.atlassian.net/browse/BP-8024 — Drafts > Cannot delete draft

Customer/Account: Workleap (Prod)

Product Area: Bills (Drafts)

Priority: Medium | Status: Selected for Development (migrated) | Owner: Abhishek Kumar

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-27
- Asif Rawloo assigned Abhishek Kumar to investigate the bill draft deletion issue and linked a Datadog trace; cc'd Sarthak Vashisht for context

Next action: Abhishek Kumar to investigate root cause of draft deletion failure and deploy fix; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-8019 — Payments > Card payment declined due to exceeding limit

Customer/Account: Wayside Publishing (Prod)

Product Area: Payments

Priority: Medium | Status: Backlog | Owner: Von Miguel Medeza

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-27
- no comments yet

Next action: Triage root cause — determine if limit is a card-level cap or a platform payment ceiling; Owner: Von Miguel Medeza

---

Issue: https://paylocity.atlassian.net/browse/BP-8007 — Bills > Bills approval UI intermittently shows incorrect PO match

Customer/Account: Sonatype (Prod)

Product Area: Bills (Approval)

Priority: Medium | Status: Selected for Development (migrated) | Owner: Manishwar Segu

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-26
- Asif Rawloo noted Manishwar was already aware of the issue (with context linked) and asked for help triaging

Next action: Manishwar Segu to identify and fix the intermittent PO match display condition in the Bills Approval UI; Owner: Manishwar Segu

---

Issue: https://paylocity.atlassian.net/browse/BP-8006 — Inbox > Still receiving inbox emails from vendor after offboarding

Customer/Account: myOrthos (Prod)

Product Area: Inbox

Priority: Medium | Status: In Review | Owner: Asif Rawloo

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-26
- no comments yet

Next action: Asif Rawloo to identify why vendor email ingestion persists post-offboarding and implement suppression fix; Owner: Asif Rawloo

---

Issue: https://paylocity.atlassian.net/browse/BP-7983 — Inbox > Scanning > Multiple invoices not being scanned properly

Customer/Account: Wild Alaskan (Prod)

Product Area: Inbox (Scanning)

Priority: Medium | Status: In Review | Owner: Asif Rawloo

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-25
- Asif Rawloo identified root cause: 24-page PDF causes OCR timeout in Veryfi, treating the file as an attachment; single-page PDFs succeed normally
- Smita Shankar noted Veryfi limits are not officially documented; suggested at minimum filling header-level fields for large invoices even when full scan fails
- Asif Rawloo raised the timeout issue with Veryfi and is awaiting their response

Next action: Await Veryfi response on OCR timeout; implement fallback to extract header-level fields for large PDFs that hit the time limit; Owner: Asif Rawloo

---

Issue: https://paylocity.atlassian.net/browse/BP-7982 — Bills > No duplicate invoice number warning when editing a pending bill

Customer/Account: GHC (Prod)

Product Area: Bills (Create/Edit)

Priority: Medium | Status: In Progress | Owner: Vishwajeet Singh

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-25
- Asif Rawloo assigned Vishwajeet Singh to investigate the missing duplicate-check during bill edits

Next action: Vishwajeet Singh to implement duplicate invoice number validation on the bill edit path; Owner: Vishwajeet Singh

---

Issue: https://paylocity.atlassian.net/browse/BP-7970 — Payments > POA-marked bill still triggers payment reminder email

Customer/Account: Productboard Inc. (Prod)

Product Area: Payments (POA/Notifications)

Priority: Medium | Status: Done | Owner: Karan Suthar

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-24
- Asif Rawloo asked Karan Suthar to pick up the ticket
- Karan Suthar identified root cause: a missing condition in the reminder-send logic — a previously unmarked vendor-payment caused the system to treat the bill as unpaid and send reminders even after POA marking
- Karan Suthar confirmed the fix was deployed

Next action: Monitor for any further spurious reminders on POA-marked bills; verify fix covers all vendor-payment states; Owner: Karan Suthar

---

Issue: https://paylocity.atlassian.net/browse/BP-7959 — Inbox > Upload > Invoices uploaded via email not appearing in inbox

Customer/Account: Not specified (Prod)

Product Area: Inbox (Upload) / Infrastructure

Priority: High | Status: Done | Owner: Asif Rawloo

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-23
- Von Miguel Medeza posted platform RCA: R15 memory quota exceeded ~06:10 UTC triggered a backup in the create_purchase_order task queue; medium queue celery workers processed fewer tasks than expected for several hours; workers self-recovered ~18:30 UTC

Next action: Platform team to add alerting for memory quota exhaustion and task queue depth; monitor inbox email ingestion for recurrence; Owner: Asif Rawloo

---

Issue: https://paylocity.atlassian.net/browse/BP-7933 — Bills > Unable to save changes to a pending bill

Customer/Account: GHC (Prod)

Product Area: Bills (Edit)

Priority: High | Status: Done | Owner: Sagar Parthasarathy

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-17
- Asif Rawloo assigned Gayathri Nair; Smita Shankar followed up on review status
- Sagar Parthasarathy identified root cause: subsidiary V2 API returning null for gl_currency on subsidiary 3617; deployed a code fallback to use bill.gl_currency, unblocking the customer
- Gayathri Nair noted the missing currency is a broader data concern requiring accounting team input
- Accounting team (Archana Sharma) confirmed the customer had already re-authorized their NetSuite integration and entries were syncing correctly
- Sagar Parthasarathy confirmed resolution; code fallback remains in place to prevent future stalls

Next action: Accounting team to investigate why subsidiary currency can be null in NetSuite subsidiary V2; monitor for recurrence; Owner: Sagar Parthasarathy

---

Issue: https://paylocity.atlassian.net/browse/BP-7932 — Bills > Replace file upload blocked by Cloudflare

Customer/Account: CS Disco (Prod)

Product Area: Bills (Create/Edit) / Infrastructure

Priority: Medium | Status: Done | Owner: Sagar Parthasarathy

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-17
- Sagar Parthasarathy diagnosed Cloudflare WAF rules blocking specific PDF uploads (similar to prior incidents); proposed workaround of re-saving PDF as new file before upload
- Vijayboopathy Elangovan updated the Cloudflare config to allow uploads; issue resolved

Next action: Monitor for further Cloudflare-blocked PDF uploads; consider a proactive Cloudflare review for other file upload endpoints; Owner: Sagar Parthasarathy

---

Issue: https://paylocity.atlassian.net/browse/BP-7930 — Bills > Bill approval error blocking payment

Customer/Account: Little Island (Prod)

Product Area: Bills (Approval)

Priority: High | Status: Done | Owner: Asif Rawloo

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-17
- Asif Rawloo identified the known R&A framework bug: when an already-approved user is re-added individually to an approval group, their manual approval remains stuck as pending
- Asif Rawloo manually fixed the bill data to unblock payments; customer confirmed unblocked
- Asif Rawloo closed the ticket; underlying framework bug remains open for future fix

Next action: Track the R&A approval framework bug for a permanent fix to prevent re-added approvers from getting stuck; Owner: Asif Rawloo

---

Issue: https://paylocity.atlassian.net/browse/BP-7924 — Payments > Initiating payment from list page returns "Cannot convert undefined or null to object"

Customer/Account: Sustainable Beverage Technologies Inc. (Prod)

Product Area: Payments

Priority: High | Status: Done | Owner: Manishwar Segu

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-16
- Manishwar Segu deployed a fix and asked Jose Darwin Doniego to request customer confirmation (POST API path prevents impersonation testing)
- Manishwar Segu confirmed no further reports since the Mar 17 fix; marked Done; root cause and fix documented in PR (https://github.com/Airbase/airbase-frontend/pull/2686)

Next action: Verify no regression on this payment initiation path; Owner: Manishwar Segu

---

Issue: https://paylocity.atlassian.net/browse/BP-7922 — Bills > Cannot add approver to existing recurring bill

Customer/Account: Healthmap Solutions Inc (Prod)

Product Area: Bills (Recurring/Approval)

Priority: Medium | Status: Done | Owner: Abhishek Kumar

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-16
- Von Miguel Medeza requested prioritization
- Abhishek Kumar manually added the approver as an immediate unblock
- Von Miguel Medeza asked for confirmation of whether this is a bug and if a permanent fix is planned
- Abhishek Kumar confirmed it appears to be a bug; FE investigation needed to determine why the "add approver" option is absent on existing recurring bills; committed to creating a follow-up ticket

Next action: Abhishek Kumar to open and prioritize FE bug ticket for missing "add approver" UI on existing recurring bills; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7917 — Invoice from Dec 2024 still showing as "Payment Initiated"

Customer/Account: Not specified (Prod)

Product Area: Payments

Priority: Medium | Status: Done | Owner: Karan Suthar

Updates:

- ticket created by Eugene Velita on 2026-03-12
- Eugene Velita reported a Dec 2024 Amazon bill for RoboNation Inc. stuck in "Payment Initiated" state; no associated deal found
- Karan Suthar identified root cause: data corruption from the partial-payments migration caused tracking info to show incorrect payment status; the payment was actually processed correctly; manually fixed the display data
- Karan Suthar created backlog ticket BP-7955 to address remaining bills with similar data issues from the migration; asked Yash Soni to prioritize and assign

Next action: Drive completion of BP-7955 to clean up all partial-payments migration data issues; Owner: Karan Suthar

---

Issue: https://paylocity.atlassian.net/browse/BP-7879 — Bills > Unable to add tags in line items

Customer/Account: Cocofloss (Prod)

Product Area: Bills (Tags/Line Items)

Priority: High | Status: Done | Owner: Abhishek Kumar

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-11
- Manishwar Segu identified the ledger/tag API returning 503; UI has no error handling so users see an infinite loader
- Manishwar Segu asked Yash Soni to assign a BE engineer to investigate; Yash Soni assigned Abhishek Kumar
- Abhishek Kumar found GET /ledger/tag consistently returning 500 due to DB query timeout; the customer has 700k NetSuite customer records
- Shubham Verma explained: a recent change removed the old 70k-tag fetch cap, causing all 700k customer tags to be fetched and overwhelming the query
- Abhishek Kumar relayed the fix via the accounting team; tagging now works for the customer

Next action: Reintroduce a safe fetch limit or optimize the tag query for large-scale NetSuite datasets; monitor /ledger/tag API latency; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7878 — Vendor Credit > Document upload fails

Customer/Account: Healthmap Solutions Inc (Prod)

Product Area: Vendor Credits

Priority: Medium | Status: Done | Owner: Gayathri Nair

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-11
- Von Miguel Medeza raised a clarification about inbox behavior when upload fails: file should not appear in inbox if not attached to memo
- Gayathri Nair identified root cause: vendor credit already has a linked document (ID 5581001); system blocks linking a second one, but when PDF conversion fails no error is surfaced to the user — unlike bills, which show a "failed to load preview" message
- Von Miguel Medeza requested the same fix be applied to a second affected vendor credit (ID 41538)
- Gayathri Nair completed the fix and added a FE task to surface error messaging for failed PDF conversion in vendor credits

Next action: Monitor FE task to ensure error display for failed vendor credit PDF uploads is deployed; Owner: Gayathri Nair

---

Issue: https://paylocity.atlassian.net/browse/BP-7872 — Payments > Accessing payment approval draft returns "Oops Something went wrong"

Customer/Account: Understood (Prod)

Product Area: Payments (Approvals)

Priority: High | Status: Done | Owner: Sagar Parthasarathy

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-10
- Von Miguel Medeza escalated urgency — customer needs to initiate payments for affected bills
- Manishwar Segu confirmed the issue was resolved and the fix is live

Next action: Verify the customer can successfully access and action payment approval drafts; Owner: Sagar Parthasarathy

---

Issue: https://paylocity.atlassian.net/browse/BP-7871 — Bills > Unable to replace PDF image on pending bills

Customer/Account: GHC (Prod)

Product Area: Bills (Create/Edit) / Infrastructure

Priority: High | Status: Done | Owner: Sagar Parthasarathy

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-10
- Sagar Parthasarathy reported 403 errors specifically for certain PDF files (e.g. Faktura_2599.pdf) during bill replace; other PDFs work fine
- Gayathri Nair and Sagar confirmed the issue is file-specific (Datadog shows 200 but browser shows 403)
- Gayathri Nair identified Cloudflare WAF as root cause; escalated to platform team
- Utkarsh Saraogi confirmed a Cloudflare request-blocking pattern and pointed to a prior similar fix
- Sagar Parthasarathy added frontend error handling so unsupported PDFs now show an error message instead of an infinite loader; fix validated in prod
- Vijayboopathy Elangovan updated the Cloudflare config to allow the affected uploads

Next action: Verify the Cloudflare fix covers all previously-failing PDF files; monitor for further WAF-blocked uploads on the replace-invoice path; Owner: Sagar Parthasarathy

---

Issue: https://paylocity.atlassian.net/browse/BP-7859 — Bills > Drafts > Users with "Create Bills" permission can see all drafts including others'

Customer/Account: US HealthConnect (Prod)

Product Area: Bills (Drafts/Visibility)

Priority: Medium | Status: Done | Owner: Abhishek Kumar

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-05
- Abhishek Kumar committed to picking up the fix in the sprint starting March 13, targeting completion by March 20
- Von Miguel Medeza and Ayush Gupta followed up multiple times requesting timeline and status
- Abhishek Kumar merged the PR; fix deployed — users with Create Bills permission no longer see drafts created by other users

Next action: Verify draft visibility is correctly scoped across all roles and permission levels; Owner: Abhishek Kumar

---

Issue: https://paylocity.atlassian.net/browse/BP-7856 — Payment proposal #39071 failed for international vendors

Customer/Account: Not specified (Prod)

Product Area: Payments (International)

Priority: Medium | Status: Done | Owner: Gayathri Nair

Updates:

- ticket created by Eugene Velita on 2026-03-04
- Eugene Velita escalated on behalf of client Parloa (Company ID 3129) — a multi-vendor payment proposal of $103,900.33 failed
- Roopak A N found payments failing at validation (not at bank transfer level); moved to Bank Payments board for further diagnosis
- Gayathri Nair identified root cause: the failed payments are for international bills using virtual card as payment method, which is not supported for non-USD bills; no UI warning exists to prevent this configuration
- Karan Suthar noted a secondary data issue: preferred_payment_method set to "virtual" for vendors with non-US bank countries — this is unexpected and should be blocked at the vendor data level

Next action: Create product ticket for UX/validation to prevent selecting virtual card for non-USD international bills; fix vendor payment method data for affected vendors; Owner: Gayathri Nair

---

Issue: https://paylocity.atlassian.net/browse/BP-7852 — Bills > Bill not automatically marked as POA upon approval via Slack

Customer/Account: Trailblazer (Prod)

Product Area: Bills (POA)

Priority: Medium | Status: Done | Owner: Abhishek Kumar

Updates:

- ticket created by Connector for Salesforce & Jira on 2026-03-03
- Yash Soni identified the bill was approved via Slack action (not the Airbase platform)
- Abhishek Kumar confirmed the Slack approval path uses BillFacade.approve but does not call handle_paid_outside_airbase_on_bill_approval_v2, which handles POA marking — the logic is missing from the Slack path
- Abhishek Kumar merged and deployed the fix for POA marking on Slack approval; noted further discrepancies between Slack/email and platform approval flows; created a follow-up ticket to address those in the next sprint

Next action: Track follow-up ticket for full parity between Slack/email and Airbase platform approval flows; monitor POA auto-marking reliability; Owner: Abhishek Kumar
