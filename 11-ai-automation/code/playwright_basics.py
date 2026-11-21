"""
playwright_basics.py - drive a real web browser from Python with Playwright.

Playwright opens a browser (Chromium, Firefox or WebKit), and your code clicks,
types and reads the page exactly like a person - but scripted. No AI involved:
this is classic, predictable automation. Browser *agents* (browser_use_agent.py)
put an LLM on top of exactly this kind of control.

Setup (on your own computer)
-----------------------------
    pip install playwright
    playwright install chromium        # downloads the browser itself (~150 MB)
    python playwright_basics.py

Key ideas
---------
* page.goto(url)              open a page
* page.locator(selector)      find element(s); prefer get_by_role / get_by_label / get_by_text
                              (they match what users see and break less when the HTML changes)
* .fill(), .click()           act on an element; Playwright auto-waits until it is ready
* .inner_text(), .count()     read from the page
* headless=True               run without a visible window (servers, CI)
"""
import sys

try:
    from playwright.sync_api import sync_playwright   # "sync" = simple, step-by-step style
except ImportError:
    print("Playwright not installed: pip install playwright && playwright install chromium")
    sys.exit(0)

# A tiny local web page, so the demo needs no internet and never changes.
DEMO_HTML = """
<html><body>
  <h1>Demo shop</h1>
  <label for="q">Search</label> <input id="q" name="q">
  <button onclick="document.getElementById('out').innerText =
      'Results for: ' + document.getElementById('q').value">Search</button>
  <p id="out"></p>
  <ul><li class="product">Blue mug - 299</li><li class="product">Red mug - 349</li></ul>
</body></html>
"""


def main() -> None:
    with sync_playwright() as p:                       # starts the Playwright engine
        try:
            browser = p.chromium.launch(headless=True) # open Chromium with no window
        except Exception as e:                         # browser binaries not downloaded yet
            print("Could not start Chromium - run `playwright install chromium`.", type(e).__name__)
            return
        page = browser.new_page()                      # a fresh tab
        page.set_content(DEMO_HTML)                    # load our HTML (use page.goto(url) for real sites)

        print("Title text:", page.get_by_role("heading").inner_text())
        page.get_by_label("Search").fill("mug")        # type into the input labelled "Search"
        page.get_by_role("button", name="Search").click()
        print(page.locator("#out").inner_text())       # read the result paragraph

        products = page.locator(".product")            # all matching elements
        for i in range(products.count()):
            print(" -", products.nth(i).inner_text())

        page.screenshot(path="demo_shop.png")          # save what the browser shows
        print("Saved screenshot demo_shop.png")
        browser.close()


if __name__ == "__main__":
    main()
