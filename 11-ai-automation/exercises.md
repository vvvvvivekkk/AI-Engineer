# Module 11 — Exercises

Graded easy (⭐) → hard (⭐⭐⭐). Solutions: [`solutions/solutions.md`](solutions/solutions.md) and the `.py` / `.json` files in `solutions/`.

---

### 1. ⭐ Place it on the spectrum
For each, choose: plain workflow, workflow + AI step, workflow + AI router, workflow that calls an agent, or autonomous agent. One sentence of reasoning each.
a) Copy every new Stripe payment into a Google Sheet.
b) Turn each new customer review into a one-line summary and a sentiment score.
c) Send each incoming email to sales, support or spam.
d) For each new bug report, search the codebase and draft a possible fix for a developer to review.

### 2. ⭐ Read the workflow
Open `workflows/02-rss-digest-to-sheets.json`. Answer: (a) Which node is the trigger and when does it fire? (b) Why is the Limit node placed *before* the LLM node? (c) What must row 1 of the Google Sheet contain, and why? (d) Which credentials must you create?

### 3. ⭐ Decode cron
Write cron lines for: (a) every weekday at 07:30, (b) every 15 minutes, (c) 00:05 on the 1st of every month. Explain each field. Bonus: why is "the last day of every month" awkward in standard cron, and how could you work around it?

### 4. ⭐⭐ Webhook replay protection
Extend the receiver in notebook 02 so the sender also sends `X-Timestamp` (Unix seconds) and the signature covers `timestamp + "." + body`. Reject requests older than 300 seconds with `401`. Test a fresh request and a stale one with `TestClient`.

### 5. ⭐⭐ Retry with a give-up path
Write `fetch_with_retry(url, attempts, backoff)` that uses `httpx` and, after the last failure, returns `None` and logs a warning to stderr instead of raising. Test with an `httpx.MockTransport` that always returns 503, and with one that fails once then succeeds.

### 6. ⭐⭐ Add a node to workflow 01
Using Python (load → modify → save as a new file), add a **billing** branch to workflow 01: replace the IF with a second IF chain or a **Switch** node so `billing` tickets go to a new email node addressed to `billing@example.com`. Run `code/validate_workflows.py`-style checks on your new file.

### 7. ⭐⭐ Validator upgrade
Add two checks to the validator: (a) warn if any HTTP Request node has no `timeout` option; (b) warn if a node's `credentials` contains anything other than `id` and `name` keys (a sign someone pasted a secret). Run it on all three workflows.

### 8. ⭐⭐ Simulate workflow 03
Extend the simulator from notebook 03 to run workflow 03: stand-ins for the search request (use the FAQ list and keyword overlap) and for `respondToWebhook`. Show one question that is answered and one that hits the "no answer" branch.

### 9. ⭐⭐ ROI for your idea
Add a row to `excel/automation-ideas-roi.xlsx` for an automation from your own work or college. Fill in realistic numbers. What is the payback period? Which single input changes the result most? (Try halving and doubling each.)

### 10. ⭐⭐⭐ Robust Playwright script
On your own machine, extend `code/playwright_basics.py`: add a second product search that finds nothing, and make the script print `"no results"` instead of crashing. Use `page.get_by_text(...)` and `locator.count()`. Take a screenshot only when something unexpected happens.

### 11. ⭐⭐⭐ Browser agent guard rails
In notebook 04's fake browser, add: (a) a **domain allow-list** (only paths starting with `/orders` or `/` may be visited), (b) a **loop detector** that stops if the same URL is visited 3 times, and (c) an audit log of every action. Show a scripted LLM that triggers each guard.

### 12. ⭐⭐⭐ Design review: automation or agent?
Your college wants to "use AI to handle student fee queries" (≈ 3,000 emails per month; fee data lives in a database with an internal API; refunds need an accountant's approval). Write a one-page design: trigger, nodes/steps, where the LLM is used, where a human approves, what is logged, failure handling, and a rough ROI. Justify why your design is (or isn't) an agent.
