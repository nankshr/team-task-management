# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Team Task Manager** - A general-purpose task management system for teams with 5-10+ employees. The system consists of:
- **FastAPI Backend** - REST API with JWT authentication, PostgreSQL database
- **Next.js Frontend** - Web dashboard for task assignment and monitoring
- **Telegram Bot** (planned) - Employee interface for task management and attendance

**Goal:** Replace manual task tracking (phone/WhatsApp) with automated system for task assignment, attendance tracking, and routine management.

## Development Commands

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Configuration

```bash
cd backend
cp .env.example .env
# Edit .env with actual values for DB credentials, SECRET_KEY, and TELEGRAM_BOT_TOKEN
```

### Database Operations

```bash
# Create database (ensure PostgreSQL is running)
createdb team_tasks

# Initialize database and create owner user
cd backend
python scripts/init_db.py

# Seed development data (8 employees, 5 labels, 6 routines, 4 tasks)
python scripts/seed_data.py

# Create migration after model changes
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Running the Application

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation: http://localhost:8000/docs

### Testing

```bash
cd backend
pytest
```

### Code Formatting

```bash
cd backend
black app/
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Running the Frontend

```bash
cd frontend
npm run dev
```

Frontend application: http://localhost:3000

### Building the Frontend

```bash
cd frontend
npm run build
npm run start
```

## Architecture

### Database Schema Design

The system uses **11 tables** with UUID primary keys and the following key relationships:

**Core Entities:**
- `users` - Authentication for owners/admins (JWT-based, bcrypt password hashing)
- `employees` - Shop workers linked to Telegram via `telegram_user_id`
- `employee_labels` - Categories like "janitor", "security", "sales", "cashier"

**Task Management:**
- `tasks` - Individual work assignments with self-referential relationship for subtasks
  - Task numbering: `T2024-001` (year + sequential)
  - Subtask numbering: `T2024-001-S1` (parent + S + sequential)
  - Supports both `routine` and `one_time` task types
  - Statuses: pending → assigned → in_progress → completed (or blocked/overdue)
  - Priorities: low, medium, high, urgent
- `task_comments` - Employee/user comments with types: general, issue_report, clarification
- `routines` - Recurring task templates (daily/weekly/monthly) that auto-generate tasks

**Attendance:**
- `attendance` - Daily tracking with statuses: present, absent, half_day, on_leave
  - Auto-absent marking for employees who don't mark attendance by deadline
- `notifications` - Telegram message tracking for audit trail

**Many-to-Many Relationships:**
- `employee_label_assignments` - Employees ↔ Labels
- `task_labels` - Tasks ↔ Labels (filter tasks by employee category)
- `routine_labels` - Routines ↔ Labels (auto-assign to employee categories)

### Task Workflow

1. **Routine Tasks:** Scheduler generates tasks from `routines` table at configured times
2. **Manual Tasks:** Owner creates via dashboard → Task sent to employee via Telegram
3. **Subtasks:** When employee reports issue/blocker → Subtask created for owner to resolve
4. **Status Updates:** Employee marks completion → Owner receives notification → Task status updated

### Authentication Flow

- JWT tokens with access (30min) and refresh (7 days) tokens
- `get_current_user` dependency protects routes
- Default admin created by `init_db.py`: username `admin`, password `admin123` (change in production!)

### Telegram Integration

- Employees identified by `telegram_user_id` (BigInteger, linked via `/start` command)
- Tasks store `telegram_message_id` for message updates
- Notifications logged in `notifications` table for debugging
- Owner receives reports at scheduled times (morning, midday, end-of-day)

## Code Organization

```
backend/app/
├── api/           # Route handlers (auth.py implemented, others planned)
├── models/        # SQLAlchemy ORM models (8 files)
├── schemas/       # Pydantic validation schemas (5 files)
├── core/          # Configuration, database, security utilities
├── services/      # Business logic (empty, to be implemented)
└── main.py        # FastAPI app with CORS, router registration
```

### Adding New API Endpoints

1. Create route file in `app/api/` (e.g., `employees.py`)
2. Import and register in `app/main.py`:
   ```python
   from app.api import employees
   app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
   ```
3. Use `get_current_user` dependency for protected routes

### Database Model Conventions

- All models inherit from `Base` (defined in `app/core/database.py`)
- UUID primary keys: `id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)`
- All models include `created_at` and `updated_at` timestamps
- Use SQLAlchemy enums for type safety (imported as `SQLEnum`)
- Foreign keys use `UUID(as_uuid=True)` type
- Index frequently queried fields (e.g., `employee_id`, `date`, `status`)

### Configuration

Settings loaded via Pydantic Settings from `.env`:
- Database: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Security: `SECRET_KEY`, `ALGORITHM`, token expiration settings
- Telegram: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_OWNER_CHAT_ID`
- App: `DEBUG`, `TZ` (timezone), `CORS_ORIGINS`

Access settings: `from app.core.config import settings`

## Key Implementation Details

### Task Assignment Logic
- Filter employees by labels before assignment
- Tasks can be assigned to multiple employees via label matching
- Subtasks automatically link to parent via `parent_task_id`

### Attendance System
- Morning reminder sent at configured time (default 8:00 AM)
- Auto-marking employees as absent if no response by deadline
- Generate daily/weekly/monthly attendance reports for owner

### Routine Task Generation
- Scheduler (APScheduler) checks `routines` table
- Active routines generate tasks based on `recurrence_type` and `recurrence_day`
- Tasks auto-assigned to employees matching routine labels
- `recurrence_day`: For weekly (1=Monday, 7=Sunday), for monthly (1-31)

### Notification Strategy
- All Telegram messages logged to `notifications` table
- Track delivery status, message IDs for updates/edits
- Owner notifications sent to `TELEGRAM_OWNER_CHAT_ID`

## Development Status

**Completed (Phase 1 - Backend & Frontend Foundation):**

**Backend (100%):**
- ✅ Complete project structure with FastAPI
- ✅ All SQLAlchemy models (11 tables) and Pydantic schemas
- ✅ Core infrastructure (config, database, security)
- ✅ Full Authentication system (JWT with Bearer tokens + HTTP-only cookies)
- ✅ Database initialization and seed scripts
- ✅ All REST API endpoints implemented:
  - Authentication (login, logout, refresh, current user)
  - Employees (CRUD + get tasks by employee)
  - Labels (CRUD for employee categories)
  - Tasks (CRUD + filtering, subtasks, comments)
  - Routines (CRUD + recurring task templates)
  - Attendance (mark, list, reports)
  - Dashboard (statistics and recent tasks)

**Frontend (In Progress - ~40%):**
- ✅ Next.js 14 with App Router + TypeScript
- ✅ Tailwind CSS v3 with shadcn/ui components
- ✅ Complete authentication flow (login, protected routes, token management)
- ✅ Bearer token + cookie-based auth (cross-port compatible)
- ✅ Dashboard layout (sidebar + header)
- ✅ Dashboard home page with stats and recent tasks
- ✅ Complete API client with all endpoints
- ✅ **Employees management page** with full CRUD operations
- ⏳ Tasks management page (pending)
- ⏳ Attendance tracking page (pending)
- ⏳ Routines management page (pending)

### Frontend Architecture

**Tech Stack:**
- **Framework:** Next.js 14 with App Router and TypeScript
- **Styling:** Tailwind CSS with shadcn/ui components
- **State Management:** TanStack Query (React Query) for server state
- **HTTP Client:** Axios with cookie-based authentication
- **Forms:** React Hook Form + Zod validation

**Project Structure:**
```
frontend/
├── app/                       # Next.js app router
│   ├── login/                # Authentication page
│   │   └── page.tsx          # Login page component
│   ├── dashboard/            # Protected dashboard routes
│   │   ├── layout.tsx        # Dashboard layout with sidebar & header
│   │   ├── page.tsx          # Dashboard home page
│   │   ├── employees/        # Employee management (to be implemented)
│   │   ├── tasks/            # Task management (to be implemented)
│   │   ├── routines/         # Routine management (to be implemented)
│   │   └── attendance/       # Attendance tracking (to be implemented)
│   ├── layout.tsx            # Root layout with providers
│   ├── page.tsx              # Root page (redirects to /login)
│   └── globals.css           # Global Tailwind styles
├── components/
│   ├── ui/                   # shadcn/ui base components
│   │   ├── button.tsx        # Button component
│   │   ├── card.tsx          # Card component
│   │   ├── input.tsx         # Input component
│   │   └── label.tsx         # Label component
│   ├── layout/               # Layout components
│   │   ├── sidebar.tsx       # Navigation sidebar
│   │   └── header.tsx        # Dashboard header
│   ├── employees/            # Employee-specific components (to be created)
│   ├── tasks/                # Task-specific components (to be created)
│   └── routines/             # Routine-specific components (to be created)
├── lib/
│   ├── api/                  # API client and service functions
│   │   ├── client.ts         # Axios instance with interceptors
│   │   ├── index.ts          # API exports
│   │   ├── auth.ts           # Authentication API
│   │   ├── employees.ts      # Employee API
│   │   ├── tasks.ts          # Task API
│   │   ├── routines.ts       # Routine API
│   │   ├── attendance.ts     # Attendance API
│   │   └── dashboard.ts      # Dashboard stats API
│   ├── auth/                 # Authentication utilities
│   │   ├── auth-context.tsx  # Auth context provider
│   │   ├── protected-route.tsx # Route protection wrapper
│   │   └── index.ts          # Auth exports
│   ├── providers.tsx         # React Query provider
│   └── utils.ts              # Utility functions (cn helper)
├── types/
│   └── index.ts              # TypeScript type definitions
├── public/                   # Static assets
├── .env.local                # Environment variables (local)
├── .env.example              # Environment template
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── postcss.config.mjs        # PostCSS configuration
└── next.config.ts            # Next.js configuration
```

**Authentication:**
- JWT Bearer tokens stored in-memory + HTTP-only cookies (dual support)
- Automatic token refresh on 401/403 responses
- Protected routes with `ProtectedRoute` wrapper
- Auth context provides `useAuth` hook with login/logout
- Cross-port compatible (frontend: 3000, backend: 8000)

**API Integration:**
All API calls use the centralized `apiClient` from `lib/api/client.ts` with:
- Automatic Authorization header injection
- Token refresh interceptor (prevents infinite loops)
- Cookie and Bearer token support
- Proper error handling

**UI Components Created:**
- Button, Card, Input, Label (basic components)
- Dialog (modal dialogs with Radix UI)
- Select (dropdown with Radix UI)
- Sidebar (navigation menu)
- Header (dashboard top bar with user info)

## Session Progress (Latest - 2025-11-09)

### Major Achievements:

1. **Fixed Authentication System:**
   - Resolved infinite refresh token loops
   - Implemented dual auth: Bearer tokens + HTTP-only cookies
   - Fixed cross-port cookie issues (3000 vs 8000)
   - Updated backend `get_current_user` to read from both Authorization header and cookies
   - Frontend token management with in-memory storage

2. **Rebranded Application:**
   - Changed from "Jewelry Shop Task Manager" to "Team Task Manager"
   - Updated all references in backend and frontend
   - Changed database name from `jewelry_tasks` to `team_tasks`

3. **Built Employee Management Page:**
   - Full CRUD operations (Create, Read, Update, Delete)
   - Employee cards with user info
   - Role assignment (Admin, Supervisor, Employee)
   - Label/category display
   - Modal dialogs for create/edit
   - Integrated with TanStack Query for data fetching

4. **UI Component Library:**
   - Created Dialog component (Radix UI)
   - Created Select component (Radix UI)
   - Installed @radix-ui/react-dialog and @radix-ui/react-select

### Files Modified/Created Today:

**Backend:**
- `app/main.py` - Updated API description
- `app/core/config.py` - Changed APP_NAME and DB_NAME
- `app/api/auth.py` - Dual auth support (Bearer + cookies)
- `.env.example` - Updated database name

**Frontend:**
- `package.json` - Updated name, added Radix UI packages
- `app/login/page.tsx` - Updated title to "Team Task Manager"
- `app/dashboard/employees/page.tsx` - **NEW** Employee management page
- `components/ui/dialog.tsx` - **NEW** Dialog component
- `components/ui/select.tsx` - **NEW** Select component
- `lib/api/client.ts` - Bearer token management
- `lib/auth/auth-context.tsx` - Token storage integration

## Next Steps (For Tomorrow):

1. **Tasks Management Page:** Create, assign, filter, and sort tasks with status updates
2. **Attendance Tracking Page:** Mark attendance, view today's status, attendance reports
3. **Routines Management Page:** CRUD for recurring task templates
4. **Telegram Bot:** Basic bot setup and handlers (Phase 2)

**Known Issues:**
- Telegram bot not implemented yet
- Task/Attendance/Routine management pages still need to be built
- No automated tests yet
- Default admin password must be changed in production

## Important Notes

- **Timezone:** All timestamps use UTC internally, configured timezone in `settings.TZ`
- **Task Numbering:** Generated sequentially, ensure thread-safe implementation
- **Secret Key:** Generate with `python backend/generate_secret_key.py` (script exists in repo)
- **Windows Compatibility:** Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- **PostgreSQL Required:** Application uses PostgreSQL-specific types (UUID, BigInteger)
