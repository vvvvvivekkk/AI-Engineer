# Module 11 — Solutions

Runnable code: [`solutions_code.py`](solutions_code.py) (exercises 4, 5, 6, 7, 8, 11 — `python solutions_code.py`, offline). Exercise 6 writes [`01b-ticket-triage-with-billing.json`](01b-ticket-triage-with-billing.json), which you can import into n8n.

---

### 1. Spectrum
a) **Plain workflow.** No language understanding is needed: a payment event maps directly to a row.
b) **Workflow + AI step.** Summary and sentiment are fuzzy (LLM), but the steps are fixed.
c) **Workflow + AI router.** One LLM decision picks a branch; the rest is fixed.
d) **Workflow that calls an agent.** Searching code and drafting a fix has unknown steps (agent), but the trigger, hand-off to a developer and approval are fixed (workflow).

### 2. Reading workflow 02
(a) **Every morning 8am** (Schedule Trigger), daily at 08:00 in the instance/workflow time zone. (b) The LLM node runs once per item and each call costs money and time; limiting first means at most 5 calls instead of one per article in the feed. (c) The headers `date, title, summary, link`, because the Sheets node uses **auto-map**: it matches item field names to column headers. (d) An HTTP Header Auth credential for the LLM API, and a Google Sheets OAuth2 credential.

### 3. Cron
Fields: minute, hour, day-of-month, month, day-of-week.
(a) `30 7 * * 1-5` — minute 30, hour 7, any day of month, any month, Monday–Friday.
(b) `*/15 * * * *` — every 15th minute (0, 15, 30, 45) of every hour.
(c) `5 0 1 * *` — minute 5, hour 0, on day 1 of every month.
Bonus: months have 28–31 days and standard cron has no "last day" symbol. Workaround: run daily at 23:00 and let the script check "is tomorrow the 1st?" (`(today + 1 day).day == 1`) before doing the work. Some schedulers (e.g. Quartz-style cron in other tools) support `L`, but plain Unix cron does not.

### 4. Replay protection
Sign `timestamp + "." + body`, so an attacker cannot change the timestamp without breaking the signature. After checking the signature, reject if `abs(now - timestamp) > 300`. Result: fresh → `200`, stale → `401 stale request`. This is the same idea Stripe and Slack use for their webhooks.

### 5. Retry with give-up
Catch `httpx.HTTPError` (it covers connection errors, timeouts, and `raise_for_status()` errors), sleep `backoff * 2**i`, and after the loop print a warning to `stderr` and `return None`. The caller then decides what to do (skip today's digest, alert someone). Output: always-503 → `None` plus a warning; fail-once → `"hello"`.

### 6. Billing branch
The solution replaces the IF node with a **Switch** node (type `n8n-nodes-base.switch`) in *rules* mode: rule 1 `category == urgent` → output 0 → Slack; rule 2 `category == billing` → output 1 → new "Email billing team" node; fallback output → output 2 → "Email support team". Connections must be updated: `Parse category → Route by category`, and the Switch node's `main` list has three outputs. The validator confirms no dangling links. *Note:* Switch node parameter formats differ between node versions; if n8n shows a warning after import, open the node and re-select the rules in the UI — the structure (three outputs) stays the same. Alternative without Switch: chain two IF nodes (urgent? → else billing? → else general).

### 7. Validator upgrade
See `extra_checks()`. Our three workflows produce no warnings (every HTTP node has `options.timeout`; credentials contain only `id` and `name`). The deliberately bad example triggers both warnings.

### 8. Simulating workflow 03
Stand-ins: the search node returns FAQ lines sharing a word with the question; the IF node picks output 0 when `context` is non-empty; the LLM stand-in answers from the first passage; `respondToWebhook` builds the reply. "how many days for refunds" → answer with source; "do you sell bicycles" → polite no-answer, and **no LLM call was made** on that branch.

### 9. ROI for your idea
Answers vary. Typical finding: **runs per month** and **minutes saved per run** dominate; LLM cost per run rarely matters for AI-step workflows (fractions of a cent to a few cents) but matters a lot for agents and computer use (many calls, screenshots). Payback under ~6 months is usually an easy yes; check maintenance hours honestly — they are often forgotten.

### 10. Robust Playwright (run locally)
```python
page.get_by_label("Search").fill("teapot")
page.get_by_role("button", name="Search").click()
hits = page.get_by_text("teapot", exact=False)
if hits.count() == 0:
    print("no results")
else:
    for i in range(hits.count()):
        print(hits.nth(i).inner_text())
```
Wrap the whole flow in `try/except Exception` and call `page.screenshot(path="error.png")` in the `except` block, so a failure leaves evidence without crashing silently. Use `count()` (which never raises) to test for presence before reading.

### 11. Browser guard rails
`guarded_browser()` shows all three: (a) an allow-list blocks `https://evil.example/promo`; (b) a visit counter stops when any URL is visited a third time; (c) every step is appended to an audit list. In a real browser agent these checks live in the **executor** (your code that performs the agent's chosen action), never only in the prompt — prompts can be ignored or hijacked.

### 12. Design review (model answer, abridged)
- **Trigger:** new email in the fees mailbox (Gmail/IMAP trigger) — about 100 per day.
- **Step 1, AI step:** LLM extracts `{student_id, intent: balance | due_date | refund | other, urgency}` as JSON; validate with a schema.
- **Step 2, API:** call the internal fee API with the student id (no agent needed — the API exists).
- **Step 3, AI step:** LLM drafts a reply using only the API data (RAG-style: "answer only from these fields").
- **Branch:** `balance`/`due_date` with high confidence → send automatically. `refund` → create a task for an accountant with the draft attached; send only after approval (human-in-the-loop). `other` or low confidence → human queue.
- **Logging:** every email id, extracted fields, API response, draft, decision and approver, in a sheet or database.
- **Failures:** API timeout → retry with backoff, then human queue; LLM invalid JSON → retry once, then human queue; error workflow alerts the team.
- **ROI:** 3,000 emails × 4 min saved ≈ 200 hours/month. Even at modest hourly costs this pays back a few weeks of build time within months; LLM cost is ~2 calls per email.
- **Agent?** No. Steps are known; the only fuzzy parts are understanding and drafting text, which are AI *steps*. A free agent would add cost and risk (refunds!) with no benefit.
