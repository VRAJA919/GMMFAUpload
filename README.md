# GeoManager Login + User Upload (Playwright, Python)

Hybrid automation for Trimble **GeoManager** (`eugm.road.com`): password sign-in, **optional email OTP (MFA)**, shell navigation, and **user definition CSV upload** in the embedded **User Administration** iframe. Browser automation uses **Playwright for Python** with explicit waits—the same operations exposed by the **Playwright MCP** server (`user-playwright`) for agent-driven runs in Cursor. **`pytest` uses the Playwright Python API** so runs are repeatable in **CI without an MCP client** (same model as [GMloginMFA](../GMloginMFA/README.md)).

## Project overview

- **Page Object Model**: `pages/` — `BasePage`, `GmLoginPage`, `GmMFAPage`, `GmShellPage`, `GmUserUploadPage`.
- **Flows (business layer)**: `flows/` — `LoginFlow` (password + optional MFA + shell transition), `UserUploadFlow` (menu → iframe → file → Done → sign out).
- **Tests**: `pytest` + `pytest-playwright`; Allure-friendly hooks and **failure screenshots** in `conftest.py`.
- **Config**: `.env` + `config/settings.py` for URLs, credentials, CSV path, timeouts.
- **Upload file**: default `define_user (1).csv` at project root (override with `GM_UPLOAD_CSV`).

## Setup (first time only)

1. Install [Python 3.10+](https://www.python.org/downloads/) and ensure `python` works in your terminal.
2. Open **Command Prompt** or **PowerShell**, go to this project folder (use quotes if the path has spaces):

```bat
cd /d "C:\path\to\GMMFAUpload"
```

3. Create the virtual environment and install Python packages:

```bat
python -m venv .venv
```

4. **Activate** the virtual environment:

| Terminal | Command |
|----------|---------|
| **Command Prompt (cmd.exe)** | `.venv\Scripts\activate.bat` |
| **PowerShell** | `.\.venv\Scripts\Activate.ps1` |

If PowerShell blocks scripts, run once as Administrator:  
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

5. With the venv active, install dependencies and browsers you need:

```bat
pip install -r requirements.txt
playwright install chromium
playwright install firefox
```

6. Copy `.env.example` to `.env` and set `GM_USERNAME`, `GM_PASSWORD`. If MFA appears after password, set **`GM_OTP_EMAIL`** (e.g. `you@mailinator.com`) and **`MAILINATOR_DOMAIN=public`**, or set **`GM_OTP_CODE`** for a one-shot code.

## Run tests (every time)

Run commands **from the `GMMFAUpload` folder** (where `pytest.ini` and `tests/` live).

### Option A — Activate the venv, then run `pytest`

**Command Prompt:**

```bat
cd /d "C:\path\to\GMMFAUpload"
.venv\Scripts\activate.bat
pytest tests\test_gm_upload.py -v --alluredir=allure-results
```

**PowerShell:**

```powershell
Set-Location "C:\path\to\GMMFAUpload"
.\.venv\Scripts\Activate.ps1
pytest tests\test_gm_upload.py -v --alluredir=allure-results
```

Example path: `C:\GM Automation\Cursor pratice\demo2\GMMFAUpload`.

### Option B — No activation (call `pytest` inside `.venv`)

```bat
cd /d "C:\path\to\GMMFAUpload"
.venv\Scripts\pytest.exe tests\test_gm_upload.py -v --alluredir=allure-results
```

### Chromium + Firefox (headed)

```bat
.venv\Scripts\pytest.exe tests\test_gm_upload.py -v -m e2e --browser chromium --browser firefox --headed
```

### Useful variants

```bat
pytest tests -v --alluredir=allure-results
pytest -m e2e -v --alluredir=allure-results
pytest tests\test_gm_upload.py -v --alluredir=allure-results --video=on
```

### Allure report (optional)

After a run with `--alluredir=allure-results`:

```bat
allure serve allure-results
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `GM_LOGIN_URL` | Secured login page URL |
| `GM_USERNAME` / `GM_PASSWORD` | Sign-in |
| `GM_OTP_EMAIL` / `OTP_EMAIL` | Mailinator inbox (full or local-part) for dynamic MFA fetch |
| `GM_OTP_CODE` | Optional static 6-digit OTP when MFA appears |
| `MAILINATOR_DOMAIN` | Use `public` for `@mailinator.com` (default in `settings.py`) |
| `GM_UPLOAD_CSV` | Path to user definition CSV (default: `define_user (1).csv` at repo root) |
| `GM_PRODUCT_TILE_SELECTOR` | CSS for post-login product tile if UI changes |
| `PLAYWRIGHT_TIMEOUT_MS` | Default locator timeout |

## Framework layout

- `config/settings.py` — env-backed settings  
- `pages/` — POM (login, MFA, shell, iframe upload)  
- `flows/` — composed user journeys  
- `tests/` — pytest entry points  
- `utils/exceptions.py` — small domain errors  

## MCP (Cursor) — same usage model as GMloginMFA

For **interactive agent execution**, enable the **user-playwright** MCP server in Cursor and use tools such as `playwright_navigate`, `playwright_fill`, `playwright_click`, `playwright_upload_file`, etc. Mirror the same **roles, labels, and iframe** usage as in the page classes:

| Area | MCP / manual parity |
|------|---------------------|
| Login | `get_by_role("textbox", name="Username")`, `Password`, `get_by_role("button", name="SIGN IN")` — see `GmLoginPage` |
| MFA (if shown) | OTP field selectors in `GmMFAPage` |
| Shell | `Loading GeoManager™`, Administration → User → User Administration — `GmShellPage` |
| Upload iframe | First `iframe` content frame; `input[type=file]`, `Upload File`, completion text / **Done** — `GmUserUploadPage` |

Automated **`pytest` runs do not call MCP**; they call Playwright Python directly so **GitHub Actions, Jenkins, and local CLI** stay self-contained.

## Check in this project to GitHub

1. Create an empty repository on GitHub (no README if you already have one locally).
2. In **Command Prompt** or **PowerShell**, from the parent folder of `GMMFAUpload`:

```bat
cd /d "C:\path\to\GMMFAUpload"
git init
git add .
git commit -m "Add GMMFAUpload Playwright hybrid framework"
git branch -M main
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

3. Ensure **`.env` is not committed** (it is listed in `.gitignore`). Use **GitHub Actions secrets** and **Jenkins credentials** for real passwords.
4. Commit **`define_user (1).csv`** only if your policy allows sample data in the repo; otherwise remove from tracking and set `GM_UPLOAD_CSV` to a CI artifact path.

## CI/CD — GitHub Actions

Workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

**Run full E2E in CI:** add **repository secrets** (repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**). Names are **case-sensitive**.

### 1. Login (one pair)

| Option | Secrets |
|--------|---------|
| **A** | `GM_USERNAME`, `GM_PASSWORD` |
| **B** (same names as GMloginMFA) | `VALID_USERNAME`, `VALID_PASSWORD` |

If **neither** pair is set, **e2e** skips (no login).

### 2. MFA / OTP (required for EU PROD tests to **pass**)

The **E2E job runs** when **login** secrets (section 1) are set. After password, PROD usually shows **email MFA** — without OTP secrets below, `pytest` may **fail** at login (not skipped).

| Secret | When to use |
|--------|-------------|
| **`GM_OTP_EMAIL`** | **Recommended** — full Mailinator address (e.g. `you@mailinator.com`). CI sets `MAILINATOR_DOMAIN=public`. |
| **`OTP_EMAIL`** | Same as GMloginMFA — local-part or full address; workflow maps it to `GM_OTP_EMAIL`. |
| **`GM_OTP_CODE`** | Fixed 6-digit code (short-lived; prefer email secrets). |
| **`IMAP_HOST`** + **`IMAP_USER`** | Also set **`IMAP_PASSWORD`** if you fetch OTP via IMAP instead of Mailinator. |

If only login secrets are configured, the workflow Summary may show a **note** reminding you to add MFA secrets.

**Manual run:** Actions → **CI** → **Run workflow**.

| Job | When |
|-----|------|
| **validate** | Push / PR / manual: pip install, Playwright Chromium, `pytest --collect-only` |
| **e2e** | After validate, when **login** secrets exist: `pytest tests/ -v --alluredir=allure-results` |

On failure, **allure-results** are uploaded as an artifact.

## CI/CD — Jenkins

Pipeline: [`Jenkinsfile`](Jenkinsfile) at repo root.

1. Create **Username with password** credentials with ID **`gm-mfa-upload-creds`** (or edit `credentialsId` in the Jenkinsfile).
2. Multibranch or Pipeline job pointing at this repository.
3. Use parameter **RUN_E2E** (default on) to run tests after install.
4. The pipeline uses **Linux** (`sh` + `.venv/bin/activate`) or **Windows** (`bat` + `.venv\Scripts\activate.bat`) based on the agent.

## Troubleshooting

| Symptom | What to check |
|--------|----------------|
| **E2E skipped on GitHub** | Add **`GM_USERNAME` + `GM_PASSWORD`** *or* **`VALID_USERNAME` + `VALID_PASSWORD`** under **Repository secrets** (not Environment secrets, unless you add `environment:` to the job). |
| **E2E fails or skips at MFA** | Add **`GM_OTP_EMAIL`** or **`OTP_EMAIL`** (Mailinator), or **`GM_OTP_CODE`**, or IMAP secrets. CI skips E2E with a notice if login exists but none of these are set. |
| **Missing CSV in CI** | The workflow checks for **`define_user (1).csv`** at the repo root; commit it or set **`GM_UPLOAD_CSV`** to a path that exists in the checkout. |
| **Done / upload timeout** | Firefox vs Chromium differences; `GmUserUploadPage` includes iframe + JS fallback for **Done**. Run with `--headed` to observe. |
| **MFA error** | Set `GM_OTP_CODE` or extend flow with Mailinator like GMloginMFA. |

## Related project

- **[GMloginMFA](../GMloginMFA/README.md)** — login + Mailinator MFA focus; same MCP + pytest split.
