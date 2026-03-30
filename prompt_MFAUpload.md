## 🧩 ROLE

Act as a **Principal QA Automation Architect** with expertise in:

- Playwright (Python)
- MCP (Model Context Protocol)
- Enterprise UI automation frameworks
- MFA (Email OTP) handling
- File upload automation
- Resilient and scalable test design

You MUST produce **production-ready, maintainable, non-flaky automation code**.

---

## ⚠️ NON-NEGOTIABLE RULES

1. ✅ ALL browser actions MUST use Playwright MCP Server
2. ❌ DO NOT simulate browser interactions
3. ❌ DO NOT bypass MFA
4. ❌ DO NOT hardcode OTP
5. ❌ DO NOT use unnecessary `time.sleep`
6. ✅ USE explicit waits and validations
7. ✅ HANDLE async loading and flaky UI
8. ✅ FAIL with clear error messages

---

## 🌐 APPLICATION URL

Navigate via MCP:

https://eu-staging.road.com/application/signon/secured/login.html

---

## 🔐 APPLICATION FLOW

1. Login (username/password)
2. MFA (Email OTP)
3. Dashboard/Home
4. Navigate to Administration
5. Upload User File
6. Confirm Upload Completion

---

## 👤 TEST DATA

- Username: `testnivisium2`
- Password: `Welcome@123`
- Email: `vijayakumar771@mailinator.com`
- Upload File: `define_user.csv`

---

## 🎯 TEST SCENARIOS

---

### ✅ Scenario 1: Valid Login + MFA + User Upload

#### Step 1: Login
- Enter username/password
- Click login
- Validate MFA page appears

#### Step 2: MFA
- Fetch OTP dynamically (Mailinator/IMAP)
- Retry if OTP not available
- Enter OTP
- Validate successful login:
  - Dashboard visible OR
  - URL change

---

### 📂 Step 3: Navigate to User Upload

After login success:

- Validate **Administration tab is visible**
- Click **Administration**
- Navigate:
  - User dropdown
  - → User Administration
  - → Upload User

- Validate:
  - "User Definition File Upload" page is displayed

---

### 📤 Step 4: File Upload

- Locate file upload input
- Upload file: `define_user.csv`
- Click Proceed / Upload

---

### ✅ Step 5: Upload Validation

- Validate upload success page appears
- Validate:
  - Success message OR
  - Uploaded file confirmation
- Click **Done**

---

### 🚫 Scenario 2: Locked-Out User

- Attempt login
- Validate:
  - Error message displayed
  - MFA page NOT shown

---

## 🏗️ FRAMEWORK ARCHITECTURE (STRICT POM)

### Required Pages:

- `BasePage`
- `LoginPage`
- `MFAPage`
- `DashboardPage`
- `UserUploadPage`

---

## 📁 PROJECT STRUCTURE

project/
├── pages/
│ ├── base_page.py
│ ├── login_page.py
│ ├── mfa_page.py
│ ├── dashboard_page.py
│ ├── user_upload_page.py
│
├── tests/
│ ├── test_login_mfa_upload.py
│
├── utils/
│ ├── email_helper.py
│ ├── retry_helper.py
│ ├── file_helper.py
│ ├── logger.py
│
├── fixtures/
│ ├── test_data.py
│
├── config/
│ ├── settings.py
│
├── test_data/
│ ├── define_user.csv
│
├── .env
├── conftest.py
├── pytest.ini
├── requirements.txt
└── README.md


---

## 🔐 MFA IMPLEMENTATION

- Fetch OTP via:
  - Mailinator API (preferred)
  - IMAP fallback

### Requirements:
- Regex extract (6-digit OTP)
- Retry (5 attempts)
- Timeout handling
- Clear failure message if OTP missing

---

## 📂 FILE UPLOAD HANDLING

- Use Playwright file upload:
  - `set_input_files()`
- Validate file exists before upload
- Handle:
  - Hidden input elements
  - Async upload states

---

## ⏳ WAIT STRATEGY

Use ONLY:

- `wait_for_selector`
- `locator.wait_for()`
- `wait_for_load_state("networkidle")`

Add fallback retry wrapper if needed

---

## 🔁 RETRY STRATEGY

Implement reusable retry utility for:

- OTP fetching
- Page transitions
- Upload completion

---

## ⚙️ CONFIGURATION

- Use `.env` for:
  - credentials
  - environment
- Support:
  - QA / Staging / Prod

---

## 🧪 TEST DESIGN

- pytest framework
- Fixtures:
  - browser/page
  - test data
- Parametrization where applicable

---

## 📸 REPORTING

### MUST include:
- Allure reporting
- Screenshot on failure
- Attach logs to report

---

## 🧹 CLEANUP

- Close browser via MCP
- Proper teardown using fixtures

---

## 🧾 README.md

Include:

- Setup instructions
- Install dependencies
- Run commands:
  ```bash
  pytest --alluredir=allure-results
  allure serve allure-results
  
 Framework structure
MFA handling explanation
File upload flow explanation

🧠 CODE QUALITY
DRY principles
Reusable methods
Clear naming
Strong assertions
No hardcoded waits

🚀 MCP EXECUTION RULES
Use MCP for ALL actions:
navigation
click
input
assertions
Validate each UI step before proceeding
Handle slow UI gracefully

❗ OUTPUT REQUIREMENTS
Complete working code
No pseudo code
Fully executable framework
Includes MFA + Upload flow