# AI-Powered JD-Based Resume Generator (CareerForge AI)

A production-grade, full-stack AI platform that synthesizes role-specific, ATS-optimized resumes based on a target **Job Description (JD)**, candidate **Reference Resume**, and candidate **Complete Career Profile**.

Unlike generic resume polishers, this application bridges technology gaps using genuine transferable engineering experience from the candidate's career history rather than treating an uploaded resume as the sole source of truth.

---

## 🌟 Key Product Pillars

1. **Three-Source Information Architecture**:
   - **Job Description**: Analyzes mandatory skills, preferred skills, ATS keywords, and core duties.
   - **Reference Resume**: Extracts current baseline information (contact, summary, layout).
   - **Complete Career Profile**: Comprehensive database maintaining all past projects, technologies, and achievements that might not fit on a single resume.
2. **Provider-Agnostic LLM Architecture (`backend/services/llm/`)**:
   - Clean abstraction layer decoupling business logic from model vendors.
   - Google Gemini provider (`gemini-1.5-flash` / `gemini-1.5-pro`) with structured JSON schema validation (Pydantic), exponential backoff retries, and rate-limit handling.
3. **Dynamic Experience-Level Prompt Engineering (`backend/prompts/`)**:
   - Adapts resume generation strategy dynamically according to the candidate's professional level:
     - **Fresher / No Internship**: Focuses on CS fundamentals, academic capstones, and open source work without fabricating phantom senior roles.
     - **Internship / Apprentice**: Focuses on real-world team deliverables, tools used, and production code hygiene.
     - **1–2 Years**: Emphasizes feature ownership, REST APIs, automated tests, and database transactions.
     - **3–5+ Years**: Highlights architecture, system design, scalability, and technical leadership.
4. **Human-in-the-Loop Workflow (Extremely Important)**:
   - Returns structured text before generating a PDF.
   - **Visual Change Highlights**:
     - 🟢 **Green**: Newly added content backed by profile evidence.
     - 🟡 **Yellow**: Modified / rephrased content highlighting transferable skills.
     - 🔴 **Red**: Removed / replaced content.
   - **YES / NO Approval System**:
     - **NO**: Prompts user for specific feedback instructions, sends to AI, creates version $N+1$, recalculates JD score, updates diffs, and loops.
     - **YES**: Finalizes approved snapshot, prompts for 1-Page or 2-Page layout, applies optional final polish, and compiles the ATS PDF.
     - **CANCEL**: Aborts workflow without finalizing a PDF, preserves drafts, and returns safely to the dashboard.
5. **Deterministic JD Match Report**:
   - Computes evidence-backed coverage %, keyword coverage %, mandatory skill coverage %, and flags unbacked evidence gaps to protect against hallucinations.
6. **ReportLab ATS PDF Engine (`backend/apps/pdf_engine/`)**:
   - Generates pixel-perfect ATS-compliant PDFs budgeted strictly for **1-Page** or **2-Page** layouts.
   - Standardized naming convention: `candidate_name_company_name_target_role_version_number.pdf`.

---

## 🏗️ Tech Stack

- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, Lucide Icons, Canvas-Confetti.
- **Backend**: Django 5, Django REST Framework, SimpleJWT, Psycopg 3, ReportLab, PyPDF, Python-docx, Pydantic.
- **Database**: PostgreSQL (with automated development fallback to SQLite and Docker Compose).
- **AI / LLM**: Google Gemini API via official `google-generativeai`.

---

## 📁 Repository Structure

```
AI-POWERED-JD-BASED-RESUME-GENERATOR/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/             # Settings, URLs, WSGI/ASGI
│   ├── apps/
│   │   ├── authentication/ # User accounts & JWT auth
│   │   ├── profiles/       # Complete Career Profile CRUD
│   │   ├── documents/      # PDF & DOCX text parsing for JD & resumes
│   │   ├── generations/    # Generation session, versions & revision loop
│   │   ├── history/        # Finalized resume archive & match reports
│   │   └── pdf_engine/     # ReportLab ATS PDF compiler
│   ├── services/
│   │   ├── llm/            # BaseLLMProvider, GeminiProvider, LLM Factory
│   │   ├── matching/       # Evidence-backed score calculator
│   │   └── diff/           # Structured visual diff generator
│   ├── prompts/            # Dynamic prompt templates isolated from business logic
│   └── tests/              # Comprehensive test suite (isolation, diffs, approvals)
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── dashboard/  # SaaS metrics & recent resumes
│   │   │   ├── generate/   # Multi-step resume generation wizard
│   │   │   ├── review/[id]/# Human-in-the-Loop review & revision screen
│   │   │   ├── profile/    # Complete Career Profile manager
│   │   │   ├── history/    # Permanent history with view & download
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── components/     # ScoreMeter, StructuredResumeView, ApprovalModal, Navbar
│   │   └── lib/            # AuthContext, API client, TypeScript definitions
├── docker-compose.yml       # PostgreSQL database container
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker for PostgreSQL

---

### Backend Setup

1. **Activate Virtual Environment**:
   ```powershell
   cd backend
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```powershell
   cp .env.example .env
   ```
   Add your Google Gemini API key:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   USE_SQLITE=True
   ```
   *(Note: `USE_SQLITE=True` is enabled by default for zero-setup local execution. Set `USE_SQLITE=False` and run `docker compose up -d` to use PostgreSQL).*

4. **Apply Database Migrations**:
   ```powershell
   python manage.py migrate
   ```

5. **Run Backend Test Suite**:
   ```powershell
   python manage.py test tests
   ```

6. **Start Backend Server**:
   ```powershell
   python manage.py runserver 127.0.0.1:8000
   ```

---

### Frontend Setup

1. **Navigate and Install Dependencies**:
   ```powershell
   cd frontend
   npm install
   ```

2. **Run TypeScript Build Verification**:
   ```powershell
   npm run build
   ```

3. **Start Next.js Development Server**:
   ```powershell
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Verified Acceptance Tests

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_normalize_filename` | Sanitizes name, company, target role, and version into standardized lowercase slug | ✅ PASS |
| `test_pdf_generation_budget` | Generates valid 1-Page and 2-Page ATS PDF without trailing blank pages | ✅ PASS |
| `test_score_calculator` | Deterministically calculates evidence-backed JD coverage, keyword coverage, and gaps | ✅ PASS |
| `test_structured_diff` | Categorizes additions (Green), modifications (Yellow), and deletions (Red) | ✅ PASS |
| `test_complete_human_in_the_loop_workflow` | End-to-end flow: generate v1 -> NO revision -> approve v2 -> download final PDF | ✅ PASS |
| `test_user_data_isolation` | Verifies that User B cannot view, revise, or download User A's resumes | ✅ PASS |
| `test_cancel_workflow` | Verifies CANCEL stops workflow without finalizing a PDF | ✅ PASS |
| `Next.js Production Build` | Turbopack compilation and TypeScript validation of all App Router routes | ✅ PASS |

---

## 📄 License
MIT License. Built for high-impact, truthful career development.
