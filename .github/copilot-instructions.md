# AI ROBO HUB – QR Code Generator: Copilot Instructions

## Project Overview
**AI ROBO HUB** is a SaaS platform for enterprise QR code generation. Two-tier architecture:
- **Streamlit Frontend** (`app.py`): User-facing UI for single/bulk QR generation
- **FastAPI Auth Server** (`auth_server/`): Authentication & user management service (partially implemented, login/register active)

## Core Architecture

### Frontend Layer (Streamlit)
- **Entry point**: [app.py](../app.py) – Routes to single/bulk/CRM generators via sidebar navigation
- **Module pattern**: Each generator (single_qr.py, bulk_qr.py) exports an `app()` function rendered on demand
- **Health check**: App pings `http://localhost:8000/ping` at startup; fails gracefully if auth server offline
- **UI components**: Extracted to [ui_header.py](../ui_header.py), [ui_footer.py](../ui_footer.py), [ui_layout.py](../ui_layout.py) for consistency
- **Session state**: Uses `st.session_state` to persist QR results, validation errors, and bulk processing status across reruns

### QR Generators (Streamlit Modules)

**Single QR** ([single_qr.py](../single_qr.py)):
- Input: Website URL, Code/Text (max 50 chars), or WhatsApp number
- Output: PNG (resizable: 300–1770px) + PDF print-ready format
- Flow: Select type → validate input → generate → display + download
- Key convention: File names encode source (e.g., `qr_website.png`, `qr_id_{code}.png`)

**Bulk QR** ([bulk_qr.py](../bulk_qr.py)):
- Input: Excel file with `value` (data to encode) and `status` (tracking column)
- Output: ZIP archive of PNGs + updated Excel with completion status
- Template: Auto-creates [bulk_qr_template.xlsx](../bulk_qr_template.xlsx) if missing
- Error handling: Row-level validation; failed records tracked with reason in separate dataframe
- Safe filename generation: Uses [safe_filename()](../bulk_qr.py#L28) to sanitize QR codes for filesystem (max 40 chars after truncation)

### Authentication Layer (FastAPI)

**Database** ([auth_server/database.py](../auth_server/database.py)):
- SQLite at `./users.db` (local, single-threaded mode enabled)
- ORM: SQLAlchemy with declarative Base

**User Model** ([auth_server/models.py](../auth_server/models.py)):
```python
User: id, name, mobile, location, business_info, email (unique), password, verified, reset_code
```

**Endpoints** ([auth_server/main.py](../auth_server/main.py)):
- `GET /login` → Render login form
- `POST /login` → Validate credentials, redirect to Streamlit (`http://localhost:8501`)
- `GET /register` → Render registration form
- `POST /register` → Validate password strength, check email uniqueness, create user
- `GET /ping` → Health check (`{"status":"ok"}`)

**Security** ([auth_server/security.py](../auth_server/security.py)):
- Password rules: 8–64 chars, uppercase, lowercase, digit, special char
- Hashing: bcrypt via `passlib.context.CryptContext`
- Verification: `verify_password(plain, hashed)` compares plain input against bcrypt hash

**Email Service** ([auth_server/email_service.py](../auth_server/email_service.py)):
- Gmail SMTP (chrao7676@gmail.com with app password)
- Single function: `send_verification_email(to_email, code)`
- Status: Defined but not integrated into register/reset flows yet

## Developer Workflows

### Running Locally
```bash
# Terminal 1 – Start auth server
cd auth_server
uvicorn main:app --reload --port 8000

# Terminal 2 – Start Streamlit frontend
streamlit run app.py
```
- **Note**: Streamlit default is `http://localhost:8501`, FastAPI is `http://localhost:8000`
- Auth server must be running before Streamlit app loads (enforced by startup ping)

### Project Structure
```
qr-code-generator-app/
├── app.py                 # Main Streamlit entry, router
├── single_qr.py          # Single QR generator module
├── bulk_qr.py            # Bulk QR generator module
├── crm_qr.py             # CRM integration (stub)
├── ui_*.py               # Shared UI components
├── auth_server/
│   ├── main.py           # FastAPI app + endpoints
│   ├── models.py         # SQLAlchemy User model
│   ├── database.py       # Engine & session factory
│   ├── security.py       # Password hashing/validation
│   ├── email_service.py  # SMTP email sender
│   └── templates/        # Jinja2 HTML (login, register, reset forms)
├── requirements.txt      # Dependencies
├── users.db              # SQLite database
└── bulk_qr_output/       # Generated QR ZIP + Excel output
```

## Key Conventions & Patterns

### Streamlit State Management
- **Session key naming**: Suffix with result type: `qr_result`, `bulk_result`, `bulk_errors`, `bulk_success`
- **Cleanup pattern**: Reset buttons delete state keys then call `st.rerun()` to refresh UI
- Example: `if clr: del st.session_state[key]; st.rerun()`

### QR Generation
- **QR Library**: `qrcode.QRCode(version=1, box_size=10, border=4)` with `.make(fit=True)`
- **Image formats**: PNG for digital, PDF (via reportlab) for print-ready
- **Size handling**: `QR_SIZES` dict maps emoji-labeled descriptions to pixel dimensions (300, 420, 885, 1770)
- **PDF layout**: Centered on A4 page at (w/2–100, h/2–100) with 200×200px image

### Input Validation Patterns
- **URLs**: Must start with `http://` or `https://` (regex: `^(http|https)://`)
- **WhatsApp numbers**: Digits only, 10–15 chars (regex: `^\d{10,15}$`)
- **Text/Codes**: Max 50 characters
- **Excel columns**: Must have exactly `value` and `status` (enforced: `{"value","status"}.issubset(df.columns)`)

### Error Handling
- **Global exception handler** in FastAPI: Returns full traceback on 500 errors for debugging
- **Streamlit validation**: Early returns with `st.error()` instead of exceptions
- **Database cleanup**: All FastAPI endpoints use try/finally to close DB sessions: `db = SessionLocal(); try: ... finally: db.close()`

### Auth Redirects
- **Post-login redirect**: Hard-coded to `http://localhost:8501` (Streamlit default)
- **Post-register redirect**: Redirects to `/login` page
- **Status code**: All redirects use `status_code=302` (temporary)

## Integration Points

### Streamlit ↔ FastAPI
- One-way health check on startup: `requests.get("http://localhost:8000/ping")`
- No session tokens passed yet (auth flow incomplete)
- Future: Embed JWT/session cookie in Streamlit after login

### Excel I/O
- **Read**: `pd.read_excel(uploaded_file)` with column validation
- **Write**: `df.to_excel(path, index=False)` for status tracking
- **Files served**: ZIP archive created with `zipfile.ZipFile()`

### External Dependencies
- **QR Generation**: `qrcode[pil]` library
- **Excel**: `pandas` + `openpyxl`
- **PDF**: `reportlab` (canvas-based layout)
- **Email**: `smtplib` + `email.mime`

## Common Tasks for AI Agents

### Adding a New QR Type
1. Add option to `QR_TYPES` list in [single_qr.py](../single_qr.py) or [bulk_qr.py](../bulk_qr.py)
2. Add validation logic in the `if gen` / processing block (follow URL/WhatsApp/text patterns)
3. Update filename generation to reflect type
4. Test with both single and bulk flows

### Extending Auth Flows
- Uncomment reset password endpoints in [auth_server/main.py](../auth_server/main.py#L77-L107)
- Call `email_service.send_verification_email()` to trigger SMTP
- Note: Gmail credentials hardcoded in [email_service.py](../auth_server/email_service.py#L3-L4) – move to `.env` before production

### Debugging Auth Issues
- Check `users.db` exists and `users` table created (happens on startup via `Base.metadata.create_all()`)
- Verify password passes `validate_password()` (must have: length 8–64, uppercase, lowercase, digit, special char)
- Test login directly: `POST /login` with form data `email=test@example.com&password=...`

### Bulk Processing Improvements
- Progress tracking: Currently UI updates every row; consider batching for large files
- Error recovery: Partial ZIP created even if some rows fail (by design)
- Filename collisions: `safe_filename()` may truncate; consider UUID fallback for identical values

## Known Limitations & TODOs

- **Auth incomplete**: Reset password, email verification endpoints commented out
- **No session persistence**: Login redirects to Streamlit but no token/cookie passed; all users share same auth server instance
- **Email service**: Hardcoded Gmail app password (SECURITY RISK – move to environment variables)
- **CRM module stub**: [crm_qr.py](../crm_qr.py) displays placeholder, not implemented
- **No HTTPS**: Local dev only; hardcoded URLs use `http://localhost`
- **Bulk output cleanup**: No automatic deletion of `bulk_qr_output/` directory; can accumulate
