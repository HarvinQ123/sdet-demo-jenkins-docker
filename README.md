# Radar Console: Test Automation Lab

A complete, runnable test-automation project in Python: **REST API tests**, **browser UI tests in both Selenium and Playwright**, a **Docker** test-runner image, and **CI pipelines for GitHub Actions and Jenkins**, all aimed at one small web app.

**Stack:** Python 3 · pytest · requests · Selenium 4 · Playwright · Docker · GitHub Actions · Jenkins

---

## 1. The scenario

A team is building a **radar operator console**. Operators sign in on a web page and see how many radar **tracks** (detected objects such as drones, vehicles and people) are active. The page gets its data from a small REST API.

This repository plays the role of the team's **SDET (Software Development Engineer in Test)**. It contains:

| Part | What it is | Where |
|---|---|---|
| The app under test | A tiny console: a login page plus a JSON API. Standard-library Python only, so it starts inside the tests. | `app/radar_app.py` |
| API tests | Check the API contract: status codes, JSON schema, value ranges, bad input, wrong password, unknown routes | `tests/test_api.py` |
| Selenium UI tests | Drive the login page in headless Chrome, using a page object and explicit waits | `tests/test_ui.py`, `tests/pages/login_page.py` |
| Playwright UI tests | The same checks in Playwright, plus **mocked API responses** (server outage, different track data) | `tests/test_ui_playwright.py`, `tests/pages/login_page_pw.py` |
| A flakiness demo | Measures `time.sleep()` against a real wait on the same page | `scripts/demo_sleep_vs_wait.py` |
| Docker image | Runs the API + Playwright suites in a container, identical on any machine | `Dockerfile` |
| CI pipelines | Run everything automatically and keep the reports | `.github/workflows/tests.yml`, `Jenkinsfile`, `jenkins/` |

The API the tests exercise:

| Request | Response |
|---|---|
| `GET /login` | HTML login page |
| `GET /api/health` | `{"status": "ok"}` |
| `GET /api/tracks` | List of 3 tracks: `id`, `range_m`, `azimuth_deg`, `velocity_mps`, `classification` |
| `POST /api/login` with `{"username": ..., "password": ...}` | `200` + token, `401` wrong password, `400` missing fields or bad JSON |

**The built-in trap:** after you click *Sign in*, the page waits a **random 300–1800 ms** before showing the result, the way a real UI lags behind the network. A test that sleeps for a fixed time passes on some runs and fails on others. A test that waits for a condition passes every time. The suites here show how to handle that correctly.

The demo account `operator / radar123` exists only inside this toy app.

---

## 2. Prerequisites

| Tool | Needed for | Check it's installed |
|---|---|---|
| **Git** | Getting the code; Jenkins also builds from Git | `git --version` |
| **Python 3.10 or newer** | Everything (tested on 3.10, 3.12 and 3.13) | `python3 --version` |
| **Google Chrome** | Selenium tests and the sleep-vs-wait demo only | Open Chrome → About |
| **Docker** | The Docker image and the local Jenkins only | `docker --version` and `docker info` |

You do **not** need to install Playwright's browser or ChromeDriver by hand. The setup steps below install Playwright's Chromium, and Selenium Manager (built into Selenium 4) downloads the ChromeDriver that matches your Chrome.

### Install on macOS (with Homebrew)

```bash
# Homebrew, the macOS package manager (skip if `brew --version` already works)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install git python@3.12        # Git and a current Python
brew install --cask google-chrome   # only for the Selenium tests

# Docker: either Docker Desktop ...
brew install --cask docker
# ... or the lightweight command-line option, Colima + the Docker CLI:
brew install colima docker
colima start                        # starts the Docker engine in a small Linux VM
```

### Install on Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip   # python3-venv is required for step 3
# Chrome (Selenium tests only):
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y ./google-chrome-stable_current_amd64.deb
# Docker: follow https://docs.docker.com/engine/install/ubuntu/
```

### Windows

Use **WSL 2** (Ubuntu) and follow the Ubuntu steps, with Docker Desktop's WSL integration turned on. The `scripts/*.sh` files are Bash scripts, so they need WSL or Git Bash.

---

## 3. Get the code and set up a virtual environment

**Do this before any `pip` / `pip3` install.** A virtual environment (venv) is a private copy of Python just for this project. Packages install into the project's `.venv/` folder instead of your system Python, so they can't break other projects, and deleting `.venv/` undoes everything.

```bash
git clone https://github.com/HarvinQ123/sdet-demo-jenkins-docker.git
cd sdet-demo-jenkins-docker
```

| Step | Command | What it does |
|---|---|---|
| Create the venv (once) | `python3 -m venv .venv` | Makes `.venv/`, a self-contained Python with its own `pip` |
| Activate it, macOS / Linux / WSL | `source .venv/bin/activate` | Points `python`, `pip` and `pytest` in **this terminal** at `.venv`. Your prompt shows `(.venv)`. |
| Activate it, Windows PowerShell | `.venv\Scripts\Activate.ps1` | Same, for PowerShell |
| Check it worked | `which python` (Windows: `where python`) | Should print a path ending in `.venv/bin/python` |
| Upgrade pip | `python -m pip install --upgrade pip` | Current pip inside the venv; avoids old-installer errors |
| Install the Python packages | `python -m pip install -r requirements.txt` | pytest, requests, Selenium, Playwright, pytest-playwright (exact versions are pinned in the file) |
| Install Playwright's browser | `python -m playwright install chromium` | Downloads the Chromium build that Playwright drives (about 150 MB, once per machine) |
| Leave the venv when done | `deactivate` | Returns the terminal to your system Python |

Activation lasts only for the current terminal window. **Every time you open a new terminal**, `cd` into the project and run `source .venv/bin/activate` again before running tests.

Inside an active venv, `pip` and `pip3` are the same program. `python -m pip` is used above because it always means "the pip that belongs to this Python".

Without activating, you can call the venv's tools by path instead: `.venv/bin/pytest`, `.venv/bin/python`.

---

## 4. Running things: commands and what they do

All commands assume you're in the project folder **with the venv active** (step 3).

### Run the tests

| Command | What runs | Why you'd use it |
|---|---|---|
| `pytest` | All 18 tests: 10 API, 3 Selenium, 5 Playwright | Full check before pushing a change |
| `pytest -m api` | Only tests marked `api` (the REST API tests) | Fastest feedback (under a second). No browser needed. |
| `pytest -m playwright` | The 5 Playwright UI tests, headless | UI checks, including the mocked-backend tests |
| `pytest -m ui` | The 3 Selenium UI tests, headless Chrome | UI checks with Selenium; needs Google Chrome |
| `pytest -m "api or playwright"` | Combines markers | Everything that runs without Google Chrome (this is what the Docker image runs) |
| `pytest -k invalid_login` | Every test whose name contains `invalid_login` (one per UI tool) | Re-run just the test you're working on |
| `pytest -x` | Stops at the first failure | Saves time when many tests fail for one reason |
| `pytest --junitxml=reports/results.xml` | Any of the above, plus a JUnit XML report | The report format CI servers read to show pass/fail trends |

**How it works:** the tests start the app themselves. A pytest fixture in `tests/conftest.py` launches `radar_app.py` on a free port before the first test and shuts it down after the last, so there's no server to start by hand. `-m` picks tests by the markers defined in `pytest.ini`, and `-v` (verbose, one line per test) is on by default there.

### Watch the browser, and debug failures

| Command | What it does | Why |
|---|---|---|
| `HEADED=1 pytest -m ui` | Runs the Selenium tests in a visible Chrome window | See what the test is clicking. Headless is the default because CI machines have no screen. |
| `pytest -m playwright --headed --slowmo 500` | Visible browser, with a 500 ms pause before each Playwright action | Slows things down enough to follow by eye |
| `python -m playwright show-trace reports/playwright/<test-folder>/trace.zip` | Opens Playwright's trace viewer for a failed test | Replay the failure step by step: DOM snapshots, network calls, console output |

When a UI test fails, evidence is saved automatically:
- Selenium: a screenshot in `reports/screenshots/`, written by a hook in `conftest.py`.
- Playwright: a screenshot and a trace in `reports/playwright/`, set up through `--screenshot` / `--tracing` in `pytest.ini`.

### See the flakiness problem for yourself

```bash
python scripts/demo_sleep_vs_wait.py
```

This logs in 10 times with `time.sleep(1)` and 10 times with an explicit `WebDriverWait`, then prints the pass count and total time for each. The sleep version usually passes only **6–7 of 10** (it varies run to run, which is the point), while the wait version passes **10/10** every time. That's the reason no test in this repo uses `time.sleep`. Needs Google Chrome.

### Poke at the app by hand

```bash
python app/radar_app.py --port 5050          # starts the app; leave it running (Ctrl+C stops it)
```

Then, in a **second** terminal:

```bash
curl http://127.0.0.1:5050/api/health        # -> {"status": "ok"}         is the server up?
curl http://127.0.0.1:5050/api/tracks        # -> list of 3 tracks         the data the UI displays
curl -i -X POST http://127.0.0.1:5050/api/login \
     -H "Content-Type: application/json" \
     -d '{"username": "operator", "password": "wrong"}'
                                             # -> HTTP 401 + error JSON    -i prints the status line
```

You can also open http://127.0.0.1:5050/login in a browser and sign in yourself. These are the same requests and pages the tests check automatically.

### One-command local run

```bash
bash scripts/run_tests_local.sh              # all tests
bash scripts/run_tests_local.sh -m api       # any pytest options are passed through
```

The script creates `.venv` if it's missing, installs the requirements and Playwright's Chromium, then runs pytest with a JUnit report in `reports/results.xml`. It doesn't need the venv activated, because it uses `.venv/bin/...` paths directly.

---

## 5. Run the tests in Docker

Docker makes the test environment identical everywhere: same OS, same Python, same browser. That's how "passes on my machine" becomes "passes in CI". Docker must be running (`docker info` answers; with Colima, run `colima start`).

```bash
docker build -t sdet-lab-tests .
```
Builds an image from `Dockerfile`, starting from Microsoft's official Playwright image (Ubuntu, Python and Chromium are already installed). It then installs `requirements.txt` and copies in the app and tests. Unchanged layers are cached, so rebuilds take seconds.

```bash
docker run --rm sdet-lab-tests
```
Starts a container from the image, runs `pytest -m "api or playwright"` (15 tests), prints the results, and `--rm` deletes the container afterwards. The Selenium tests aren't included because they need Google Chrome, which this image doesn't have. They run in the Jenkins image instead.

To keep the JUnit report from a container run:

```bash
docker run --name sdet-run sdet-lab-tests        # same run, but the container is kept
docker cp sdet-run:/work/reports ./reports       # copy its reports/ folder out
docker rm sdet-run                               # then remove the container
```

---

## 6. Run the pipeline in Jenkins (local, in Docker)

```bash
bash scripts/start_jenkins.sh
```
This script:
1. Starts Docker through Colima if it isn't running.
2. Builds a Jenkins image (Jenkins LTS + Python + Chromium + pipeline plugins).
3. Starts it at **http://127.0.0.1:8080**, with this project mounted read-only and a job called `sdet-lab` already created.

Open http://127.0.0.1:8080/job/sdet-lab/ and click **Build Now**. The `Jenkinsfile` runs these stages: *Setup Python* → *API tests* → *UI tests (Selenium)* → *UI tests (Playwright)*. It then publishes the JUnit results (with a trend graph) and archives `reports/`, including failure screenshots.

```bash
bash scripts/stop_jenkins.sh            # removes the Jenkins container; build history is kept
bash scripts/stop_jenkins.sh --purge    # also deletes the build history
colima stop                             # stops the Docker VM (Colima users)
```

Notes:
- Jenkins checks out the **committed** code on the `main` branch, so commit a change before clicking *Build Now*.
- This Jenkins skips the setup wizard and has no login. That's only acceptable because it listens on 127.0.0.1 and can't be reached from another machine. Don't reuse these settings on a real server.

---

## 7. GitHub Actions

`.github/workflows/tests.yml` runs automatically on every push and pull request to `main`. You can also start it from the **Actions** tab (*Run workflow*). It has two jobs that run in parallel:

| Job | Steps |
|---|---|
| `tests` | Set up Python 3.12 → install requirements and Playwright Chromium → API tests → Playwright tests → Selenium tests (using the runner's Chrome) → upload `reports/` |
| `docker` | Build the test image → run the suite inside it → copy out and upload its reports |

Each run's JUnit XML, screenshots and traces can be downloaded under **Artifacts** on its page in the Actions tab. With the GitHub CLI, `gh run list` shows recent runs, and `gh run watch` follows one live.

---

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
scripts/
  run_tests_local.sh          one-command local run
  demo_sleep_vs_wait.py       sleep-vs-wait flakiness demo
  start_jenkins.sh            build + start local Jenkins in Docker
  stop_jenkins.sh             stop it
jenkins/                      Jenkins image (Dockerfile) and job bootstrap script
Dockerfile                    test-runner image
Jenkinsfile                   Jenkins pipeline
.github/workflows/tests.yml   GitHub Actions workflow
pytest.ini                    markers, report and failure-artifact settings
requirements.txt              pinned Python packages
```

---

## Design notes

**Wait for conditions, never for time.** Selenium code polls a condition with `WebDriverWait(driver, 5).until(EC.visibility_of_element_located(...))` and returns the moment it's true. Playwright's actions and `expect()` assertions retry on their own. Implicit and explicit waits are never mixed, because their timeouts stack unpredictably.

**Page objects.** Each page is one class that holds its locators and user-level actions; tests contain intent and assertions only. A markup change means editing one class, not every test.

**Selenium and Playwright, side by side.**

| | Selenium (`test_ui.py`) | Playwright (`test_ui_playwright.py`) |
|---|---|---|
| Waiting | Explicit `WebDriverWait` + `expected_conditions` | Auto-wait on actions; `expect()` retries |
| Locators | IDs (`By.ID`) | Label and role (`get_by_label`, `get_by_role`) |
| Network control | None built in | `page.route()` to stub or fail API calls |
| Failure evidence | Screenshot (custom hook) | Screenshot + replayable trace |

**Mocking the backend.** `page.route()` answers the browser's API calls from inside the test, so failure paths that are hard to produce on a real server can be checked directly:
- `/api/login` returns **503**: the page must show the server's message rather than hang.
- `/api/tracks` returns **5 tracks**: the page must say 5, which proves the count comes from the API and isn't hard-coded.

**Headless in CI.** Chrome runs with `--headless=new`, a fixed window size (layouts change at small widths) and the container flags `--no-sandbox` / `--disable-dev-shm-usage`.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `error: externally-managed-environment` when running pip | You're installing into system Python. Create and activate the venv (step 3) first. |
| `pytest: command not found` | The venv isn't active in this terminal: `source .venv/bin/activate` |
| `No module named venv` / `ensurepip is not available` (Ubuntu) | `sudo apt install python3-venv` |
| Playwright: *Executable doesn't exist* | `python -m playwright install chromium` |
| Selenium: driver or Chrome errors | Install or update Google Chrome; Selenium Manager fetches a matching driver. Set `SELENIUM_MANAGER=1` to ignore any `chromium` on your `PATH`. |
| `Cannot connect to the Docker daemon` | Start Docker Desktop, or run `colima start` |
| Port 8080 already in use | `docker ps` or `lsof -i :8080` to see what's using it |
| Jenkins doesn't pick up a change | Commit it; Jenkins builds the committed `main` branch |
