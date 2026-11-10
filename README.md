# Radar Console: Test Automation Lab

A small, complete test-automation project: a toy "radar console" web app with **REST API tests**, **browser UI tests in both Selenium and Playwright**, and the same suites running in **three places**: locally, in **Docker**, and in CI on both **GitHub Actions** and **Jenkins**.

**Stack:** Python 3 · pytest · requests · Selenium 4 · Playwright · Docker · GitHub Actions · Jenkins (declarative pipeline)

---

## What it shows

| Area | Where | Highlights |
|---|---|---|
| API testing | `tests/test_api.py` | Schema and value-range checks, `parametrize`, negative cases (400 / 401 / 404) |
| UI testing, Selenium | `tests/test_ui.py`, `tests/pages/login_page.py` | Page Object Model, explicit waits (no `time.sleep`), headless Chrome, screenshot on failure |
| UI testing, Playwright | `tests/test_ui_playwright.py`, `tests/pages/login_page_pw.py` | User-facing locators, auto-waiting `expect()`, **network mocking** with `page.route`, trace + screenshot on failure |
| Flakiness, measured | `scripts/demo_sleep_vs_wait.py` | `time.sleep(1)` passed 6/10 runs; an explicit wait passed 10/10 |
| Containers | `Dockerfile` | Test-runner image on Microsoft's Playwright base; runs API + Playwright suites anywhere |
| CI: GitHub Actions | `.github/workflows/tests.yml` | API, Playwright and Selenium steps; container job; JUnit XML, screenshots and traces uploaded as artifacts |
| CI: Jenkins | `Jenkinsfile`, `jenkins/` | Jenkins in Docker, staged pipeline, JUnit trend, archived artifacts, failure notification hook |

The app under test (`app/radar_app.py`) is standard-library Python. Its login page waits a **random 300–1800 ms** before showing the result, like a real UI behind a network, so tests that guess at timing fail and tests that wait on conditions pass.

## Run it

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium

.venv/bin/pytest                    # everything (18 tests)
.venv/bin/pytest -m api             # REST API only
.venv/bin/pytest -m playwright      # Playwright UI
.venv/bin/pytest -m ui              # Selenium UI (uses your local Chrome)
HEADED=1 .venv/bin/pytest -m ui     # watch the browser
```

**In Docker** (API + Playwright suites):

```bash
docker build -t sdet-lab-tests .
docker run --rm sdet-lab-tests
```

**In Jenkins** (runs locally in Docker, bound to 127.0.0.1):

```bash
bash scripts/start_jenkins.sh       # then open http://127.0.0.1:8080/job/sdet-lab/ and click Build Now
bash scripts/stop_jenkins.sh
```

Jenkins builds what is committed to Git. The lab Jenkins skips the setup wizard and has no login, which is only acceptable because it listens on localhost.

**GitHub Actions** runs on every push and pull request to `main`. Reports are attached to each run as artifacts.

## Project layout

```
app/radar_app.py              app under test: login page + /api/health, /api/tracks, /api/login
tests/
  conftest.py                 fixtures: app server on a free port, API session, Chrome driver, screenshot on failure
  pages/login_page.py         Selenium page object (explicit waits live here)
  pages/login_page_pw.py      Playwright page object
  test_api.py                 REST API tests
  test_ui.py                  Selenium UI tests
  test_ui_playwright.py       Playwright UI tests, incl. mocked backend responses
scripts/                      local runner, Jenkins start/stop, sleep-vs-wait demo
jenkins/                      Jenkins image (LTS + Python + Chromium) and job bootstrap
Dockerfile                    test-runner image
Jenkinsfile                   pipeline: setup, API, Selenium, Playwright, publish
.github/workflows/tests.yml   GitHub Actions workflow
```

## Design notes

### Wait for conditions, never for time

```python
# Flaky: the page needs 0.3-1.8 s, so this fails whenever it needs more than 1 s.
page.login("operator", "radar123")
time.sleep(1)

# Selenium: poll a condition, return as soon as it's true, give up after 5 s.
WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "welcome")))

# Playwright: assertions retry on their own.
expect(page.locator("#welcome")).to_have_text("Welcome, operator. 3 active tracks.")
```

Measured with `scripts/demo_sleep_vs_wait.py` (10 logins each): `time.sleep(1)` passed **6/10**; `WebDriverWait` passed **10/10**. Implicit and explicit waits are never mixed, because their timeouts stack unpredictably.

### Page objects

Each page is one class that holds its locators and exposes user-level actions; tests contain intent and assertions only. A markup change means editing one class, not every test. The Selenium and Playwright page objects cover the same page, so the two tools can be compared directly.

### Selenium vs Playwright, side by side

| | Selenium (`test_ui.py`) | Playwright (`test_ui_playwright.py`) |
|---|---|---|
| Waiting | Explicit `WebDriverWait` + `expected_conditions` | Auto-wait on actions; `expect()` retries |
| Locators | IDs (`By.ID`) | Label and role (`get_by_label`, `get_by_role`) |
| Network control | None built in | `page.route()` to stub or fail API calls |
| Failure evidence | Screenshot (custom hook in `conftest.py`) | Screenshot + replayable trace (`--tracing=retain-on-failure`) |
| Browser setup | Chrome + matching driver | `playwright install chromium` |

### Testing the UI against a mocked backend

`page.route()` answers the browser's API calls from the test, so failure paths that are hard to produce on a real server can be checked directly:

- `/api/login` returns **503** → the page must show the server's message rather than hang or crash.
- `/api/tracks` returns **5 tracks** → the welcome line must say 5, which proves the count is read from the API and not hard-coded.

### Headless in CI

Chrome runs with `--headless=new`, a fixed window size (layouts change at small widths) and the container flags `--no-sandbox` / `--disable-dev-shm-usage`. Because nobody watches a CI run, every UI failure saves evidence: a screenshot for Selenium, a screenshot and trace for Playwright. CI keeps both as artifacts.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Cannot connect to the Docker daemon` | Start Docker (on macOS with Colima: `colima start`) |
| Port 8080 in use | `docker ps` or `lsof -i :8080` to find what's running |
| Jenkins doesn't see a change | Commit it; Jenkins checks out `main` |
| Selenium driver error | Update Chrome; Selenium Manager fetches the matching driver. Set `SELENIUM_MANAGER=1` to ignore any `chromium` on `PATH` |
| Playwright says the browser is missing | `.venv/bin/playwright install chromium` |

The `operator / radar123` account exists only inside the toy app.
