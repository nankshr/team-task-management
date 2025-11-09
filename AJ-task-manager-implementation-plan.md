# Jewelry Shop Task Management System - Implementation Plan

## Executive Summary

**Project:** Task management system for retail/wholesale jewelry shop with 5-10 employees
**Timeline:** 6-8 weeks (MVP Demo-Ready)
**Owner:** You (Developer) building for client (Jewelry Shop Owner)
**Goal:** Replace manual task tracking (phone/WhatsApp) with automated system using Telegram bot + web dashboard

---

## Problem Statement & Solution

### Current Pain Points
- Tasks communicated via scattered channels (phone, WhatsApp, in-person)
- No visibility into task completion status
- Manual follow-up is time-consuming
- Daily, weekly, monthly routines being missed
- No accountability tracking

### Solution Overview
A two-part system:
1. **Owner Web Dashboard** - Create, assign, and monitor tasks
2. **Employee Telegram Bot** - Receive tasks, mark attendance, report completion, raise issues

### Key Features (MVP)
- Daily attendance via Telegram with auto-reporting to owner
- Recurring task routines (daily/weekly/monthly)
- Manual task assignment with label-based filtering
- Task completion tracking with timestamps
- Subtask creation for blockers
- Overdue task tracking and reminders
- Daily status reports to owner (morning, midday, end-of-day)
- Text-only communication (no photo uploads in MVP)

---

## End Product Vision

### Owner Experience
The shop owner logs into a clean web dashboard each morning. They see:
- **Attendance Overview:** 7/8 employees present, 1 absent (auto-marked)
- **Today's Tasks:** All scheduled routines displayed with status (pending/in-progress/completed/overdue)
- **Quick Actions:** "Assign New Task", "View Reports", "Manage Routines"

The owner filters employees by role (janitor, security, sales, cashier) and assigns a one-time task: "Pick up jewelry from Vendor X by 3 PM". The system sends a Telegram message to the selected employee immediately.

Throughout the day, the owner receives automated reports:
- **9:00 AM:** Attendance summary
- **3:00 PM:** Midday progress update
- **9:00 PM:** End-of-day completion report

If an employee reports an issue (e.g., "Shelf bracket broken"), a subtask appears in the owner's dashboard marked "Urgent - Employee Blocked". The owner resolves it, marks subtask complete, and the employee is auto-notified to continue the original task.

### Employee Experience
At 8:00 AM, each employee receives:
```
🌅 Good morning! Mark your attendance:
[✅ Present] [❌ Absent] [🕐 Half Day]
```

After marking attendance, they receive their daily tasks:
```
📋 Task #T2024-001
Clean display shelves
⏰ Due: Today 6:00 PM
🎯 Priority: High

[✓ Complete] [⚠️ Issue] [💬 Comment]
```

When the employee completes the task, they tap **[✓ Complete]**. The system logs completion time and notifies the owner.

If there's an issue, they tap **[⚠️ Issue]**, type their message, and a subtask is created for the owner. They receive updates when blockers are resolved.

Missed tasks trigger reminders at midday and end-of-day, keeping everyone accountable.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────┐
│   Owner Browser     │
│   (Next.js App)     │
└──────────┬──────────┘
           │
           │ HTTPS/REST
           ▼
┌─────────────────────┐      ┌──────────────────┐
│   FastAPI Backend   │◄────►│   PostgreSQL     │
│   (Python 3.11+)    │      │   Database       │
└──────────┬──────────┘      └──────────────────┘
           │
           │ Webhook/API
           ▼
┌─────────────────────┐
│   Telegram Bot      │◄─────► Employee Phones
│   (python-telegram- │       (Telegram App)
│    bot library)     │
└─────────────────────┘
```

### Technology Stack (Confirmed)

**Backend**
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0
- **Task Queue:** APScheduler (for cron jobs and reminders)
- **Telegram:** python-telegram-bot library (v20+)
- **Authentication:** JWT tokens
- **Validation:** Pydantic v2

**Frontend**
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui (accessible, functional, not flashy)
- **State:** React Query (TanStack Query) for API calls
- **Forms:** React Hook Form + Zod validation

**Database**
- **Primary:** PostgreSQL 15+ (self-hosted)
- **Schema:** Relational with proper foreign keys
- **Migrations:** Alembic

**Infrastructure**
- **Hosting:** Your VPS with Coolify
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Caddy/Traefik (managed by Coolify)
- **Environment:** Production-ready with proper secrets management

---

## Database Schema

### Core Tables

**users**
```sql
id: UUID PRIMARY KEY
username: VARCHAR(50) UNIQUE NOT NULL
email: VARCHAR(255) UNIQUE
password_hash: VARCHAR(255) NOT NULL
role: ENUM('owner', 'admin', 'employee')
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**employees**
```sql
id: UUID PRIMARY KEY
user_id: UUID FK -> users.id (nullable, for future app login)
name: VARCHAR(100) NOT NULL
phone: VARCHAR(20)
telegram_user_id: BIGINT UNIQUE
telegram_username: VARCHAR(50)
is_active: BOOLEAN DEFAULT true
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**employee_labels**
```sql
id: UUID PRIMARY KEY
name: VARCHAR(50) NOT NULL (e.g., 'janitor', 'security', 'sales', 'cashier')
color: VARCHAR(7) (hex color for UI)
created_at: TIMESTAMP
```

**employee_label_assignments**
```sql
employee_id: UUID FK -> employees.id
label_id: UUID FK -> employee_labels.id
PRIMARY KEY (employee_id, label_id)
```

**attendance**
```sql
id: UUID PRIMARY KEY
employee_id: UUID FK -> employees.id
date: DATE NOT NULL
status: ENUM('present', 'absent', 'half_day', 'leave')
marked_at: TIMESTAMP
auto_marked: BOOLEAN DEFAULT false
UNIQUE(employee_id, date)
```

**tasks**
```sql
id: UUID PRIMARY KEY
task_number: VARCHAR(20) UNIQUE NOT NULL (e.g., 'T2024-001')
title: VARCHAR(200) NOT NULL
description: TEXT
task_type: ENUM('routine', 'one_time')
priority: ENUM('low', 'medium', 'high', 'urgent')
status: ENUM('pending', 'assigned', 'in_progress', 'blocked', 'completed', 'overdue')
due_date: DATE NOT NULL
due_time: TIME
assigned_to: UUID FK -> employees.id
assigned_by: UUID FK -> users.id
created_by: UUID FK -> users.id
parent_task_id: UUID FK -> tasks.id (for subtasks)
is_subtask: BOOLEAN DEFAULT false
telegram_message_id: BIGINT (for tracking bot messages)
completed_at: TIMESTAMP
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**task_labels**
```sql
task_id: UUID FK -> tasks.id
label_id: UUID FK -> employee_labels.id
PRIMARY KEY (task_id, label_id)
```

**routines**
```sql
id: UUID PRIMARY KEY
title: VARCHAR(200) NOT NULL
description: TEXT
recurrence_type: ENUM('daily', 'weekly', 'monthly')
recurrence_time: TIME NOT NULL
recurrence_day: INTEGER (for weekly: 1-7, monthly: 1-31)
is_active: BOOLEAN DEFAULT true
created_by: UUID FK -> users.id
created_at: TIMESTAMP
updated_at: TIMESTAMP
```

**routine_labels**
```sql
routine_id: UUID FK -> routines.id
label_id: UUID FK -> employee_labels.id
PRIMARY KEY (routine_id, label_id)
```

**task_comments**
```sql
id: UUID PRIMARY KEY
task_id: UUID FK -> tasks.id
comment_by_employee_id: UUID FK -> employees.id (nullable)
comment_by_user_id: UUID FK -> users.id (nullable)
comment_text: TEXT NOT NULL
comment_type: ENUM('general', 'issue_report', 'clarification')
created_at: TIMESTAMP
```

**notifications**
```sql
id: UUID PRIMARY KEY
notification_type: ENUM('task_assigned', 'task_completed', 'attendance_reminder', 'task_overdue', 'daily_report')
recipient_employee_id: UUID FK -> employees.id (nullable)
recipient_user_id: UUID FK -> users.id (nullable)
message: TEXT NOT NULL
sent_at: TIMESTAMP
read_at: TIMESTAMP
```

---

## API Endpoint Design

### Authentication Endpoints
```
POST   /api/auth/login          - Owner/Admin login
POST   /api/auth/logout         - Logout
GET    /api/auth/me             - Get current user info
POST   /api/auth/refresh        - Refresh JWT token
```

### Employee Management
```
GET    /api/employees           - List all employees (with filters)
POST   /api/employees           - Create new employee
GET    /api/employees/{id}      - Get employee details
PUT    /api/employees/{id}      - Update employee
DELETE /api/employees/{id}      - Deactivate employee
GET    /api/employees/{id}/tasks - Get employee's tasks
```

### Label Management
```
GET    /api/labels              - List all labels
POST   /api/labels              - Create new label
PUT    /api/labels/{id}         - Update label
DELETE /api/labels/{id}         - Delete label
```

### Attendance Management
```
GET    /api/attendance/today    - Today's attendance summary
GET    /api/attendance          - Attendance history (with date filters)
POST   /api/attendance/mark     - Manual attendance marking (by owner)
GET    /api/attendance/report   - Generate attendance report
```

### Task Management
```
GET    /api/tasks               - List tasks (with filters: status, employee, date, priority)
POST   /api/tasks               - Create new task
GET    /api/tasks/{id}          - Get task details
PUT    /api/tasks/{id}          - Update task
DELETE /api/tasks/{id}          - Delete task
POST   /api/tasks/{id}/assign   - Assign task to employee
POST   /api/tasks/{id}/complete - Mark task complete
POST   /api/tasks/{id}/subtask  - Create subtask
GET    /api/tasks/{id}/comments - Get task comments
POST   /api/tasks/{id}/comments - Add comment to task
GET    /api/tasks/overdue       - Get all overdue tasks
```

### Routine Management
```
GET    /api/routines            - List all routines
POST   /api/routines            - Create new routine
GET    /api/routines/{id}       - Get routine details
PUT    /api/routines/{id}       - Update routine
DELETE /api/routines/{id}       - Deactivate routine
POST   /api/routines/{id}/generate - Manually trigger routine task generation
```

### Reports & Analytics
```
GET    /api/reports/daily       - Daily summary report
GET    /api/reports/completion-rate - Task completion analytics
GET    /api/reports/employee-performance - Employee performance metrics
GET    /api/reports/overdue-trends - Overdue task trends
```

### Telegram Webhook (Internal)
```
POST   /api/telegram/webhook    - Telegram bot webhook endpoint
```

### Dashboard Statistics (New - For Frontend)
```
GET    /api/dashboard/stats     - Get dashboard overview statistics
                                  Returns: {
                                    attendance: {today_present, today_absent, total_employees},
                                    tasks: {pending, in_progress, completed, overdue},
                                    recent_tasks: [...]
                                  }
```

---

### Implementation Status

**✅ Implemented:**
- Authentication endpoints (login, logout, refresh, me) - `backend/app/api/auth.py`
- Database models for all entities - `backend/app/models/`
- Pydantic schemas for validation - `backend/app/schemas/`

**⏳ To Be Implemented (Required for Frontend):**
- Employee Management endpoints (CRUD, list, tasks by employee)
- Label Management endpoints (CRUD, list)
- Task Management endpoints (CRUD, assign, complete, comments, subtasks)
- Routine Management endpoints (CRUD, activate/deactivate)
- Attendance endpoints (today summary, history, reports)
- Dashboard statistics endpoint
- Reports & Analytics endpoints (can be deferred to Phase 4)

---

## Telegram Bot Flow & Message Design

### Bot Command Structure

**Commands Available to Employees:**
- `/start` - Initialize bot, register Telegram ID
- `/help` - Show available commands
- `/tasks` - List all assigned tasks
- `/attendance` - Mark attendance manually
- `/status` - Check today's attendance and task summary

### Message Templates

#### 1. Attendance Request (Sent at 8:00 AM daily)
```
🌅 Good morning, [Employee Name]!

Please mark your attendance for [Date]:

[Inline Keyboard Buttons]
┌─────────────────────────────┐
│  ✅ Present  │  ❌ Absent    │
├──────────────┼───────────────┤
│  🕐 Half Day │  🏖️ Leave     │
└─────────────────────────────┘
```

**Response Handling:**
- Button press → Update database, send confirmation
- Confirmation message: "✅ Attendance marked as Present for [Date]"

#### 2. Task Assignment (Reply Markup Design)
```
📋 Task #T2024-001

🎯 Clean display shelves
⏰ Due: Nov 04, 2024 6:00 PM
🔴 Priority: High

━━━━━━━━━━━━━━━━━━━━━━━━

[Inline Keyboard Buttons]
┌──────────────────────────────┐
│       ✅ Mark Complete       │
├──────────────────────────────┤
│       ⚠️ Report Issue         │
├──────────────────────────────┤
│       💬 Add Comment          │
└──────────────────────────────┘
```

**Button Actions:**

**✅ Mark Complete**
- Checks if subtasks exist and are open → Block with message "⛔ Cannot complete. Blocked by: [Subtask #]"
- If no blockers → Mark complete, log timestamp, notify owner
- Response: "✅ Task #T2024-001 marked as completed at 4:32 PM"

**⚠️ Report Issue**
- Bot prompts: "Please describe the issue:"
- Employee types text response
- System creates subtask for owner, links to parent task
- Response: "⚠️ Issue reported. Subtask #T2024-001-S1 created for Owner. You'll be notified when resolved."

**💬 Add Comment**
- Bot prompts: "Enter your comment:"
- Employee types text response
- System saves comment, notifies owner
- Response: "💬 Comment added to Task #T2024-001"

#### 3. Subtask Blocker Resolved Notification
```
✅ Blocker Resolved!

Task #T2024-001: Clean display shelves
Subtask #T2024-001-S1 has been completed by Owner.

You can now complete this task.

[View Task Details] ← Button to show task again
```

#### 4. Overdue Task Reminder (Sent at 3:00 PM and 9:00 PM)
```
⏰ Reminder: Overdue Tasks

You have 2 tasks pending:

1️⃣ Task #T2024-001
   Clean display shelves
   🔴 Due: Today 6:00 PM (Overdue by 3 hrs)

2️⃣ Task #T2024-003
   Rearrange stock
   🟡 Due: Today 5:00 PM (Overdue by 4 hrs)

Please complete or report issues.
```

#### 5. Daily Task Batch (Sent at 8:30 AM after attendance)
```
📋 Your Tasks for Today

You have 5 tasks assigned:

━━━━━━━━━━━━━━━━━━━━━━━━

[Individual task messages follow, each with reply markup buttons]
```

**Note:** Each task is sent as a separate message with its own unique inline keyboard, ensuring proper message_id tracking for reply handling.

### Bot State Machine

```
Employee Interaction States:
1. IDLE → Waiting for interaction
2. AWAITING_ISSUE_DESCRIPTION → After pressing "Report Issue"
3. AWAITING_COMMENT → After pressing "Add Comment"
4. AWAITING_ATTENDANCE → Daily attendance prompt active
```

---

## Task Assignment & Notification Logic

### Daily Routine Task Generation

**Cron Job (Runs at 7:30 AM daily):**
1. Query all active routines with `recurrence_type = 'daily'`
2. For each routine:
   - Check attendance for employees with matching labels
   - Filter to only "present" employees
   - Create task instances for today
   - Assign based on manual assignment rules (MVP: owner assigns later)
   - Store in database with status "pending"

**Post-Attendance Task Delivery (After employee marks attendance):**
1. Query all tasks for today assigned to this employee
2. Send each task as separate Telegram message with inline keyboard
3. Store `telegram_message_id` in database for reply tracking

### Weekly Routine Task Generation

**Cron Job (Runs at 7:30 AM daily):**
1. Check if today matches any weekly routine's `recurrence_day` (1=Monday, 7=Sunday)
2. Generate tasks same as daily logic

### Monthly Routine Task Generation

**Cron Job (Runs at 7:30 AM daily):**
1. Check if today's date matches any monthly routine's `recurrence_day`
2. Generate tasks same as daily logic

### One-Time Task Assignment (Manual by Owner)

**Owner Action in Dashboard:**
1. Owner selects employee(s) manually or filters by label
2. Owner clicks "Assign Task"
3. System creates task in database
4. System checks employee's attendance for today
   - If present → Send Telegram notification immediately
   - If absent → Queue for delivery when they mark attendance
5. Store `telegram_message_id` for tracking

---

## Overdue Task Tracking & Reminders

### Overdue Detection (Cron Job - Runs every 30 minutes)

```python
def detect_overdue_tasks():
    current_time = datetime.now()
    
    # Query tasks that are past due and not completed
    overdue_tasks = db.query(Task).filter(
        Task.status.in_(['pending', 'assigned', 'in_progress']),
        Task.due_date < current_time.date(),
        or_(
            Task.due_time.is_(None),
            Task.due_time < current_time.time()
        )
    ).all()
    
    for task in overdue_tasks:
        task.status = 'overdue'
        db.commit()
```

### Reminder Schedule

**Midday Reminder (3:00 PM):**
- Send reminder for all overdue tasks
- Send reminder for tasks due within 3 hours

**End-of-Day Reminder (9:00 PM):**
- Send reminder for all incomplete tasks
- Mark tasks as "carried forward to next day" in database

**Next Day Handling:**
- Overdue tasks remain visible the next day
- Employee can still complete or report issues
- Completion updates status to "completed (late)" with timestamp

---

## Owner Daily Reports

### Report Schedule

**1. Morning Attendance Report (9:00 AM or when all attendance marked)**

```
📊 Attendance Report - [Date]

✅ Present: 7
❌ Absent: 1
🕐 Half Day: 0
🏖️ Leave: 0

━━━━━━━━━━━━━━━━━━━━━━━━

Absent Employees:
• Raj Kumar (Janitor)

Present Employees:
• Priya (Sales)
• Arun (Security)
• Meena (Sales)
• Kumar (Cashier)
• Lakshmi (Sales)
• Senthil (Janitor)
• Divya (Admin)

[View Dashboard] ← Link to web app
```

**2. Midday Progress Report (3:00 PM)**

```
📊 Midday Progress - [Date] 3:00 PM

Tasks Status:
✅ Completed: 12
⏳ In Progress: 5
⏰ Overdue: 2
📋 Pending: 8

━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Overdue Tasks:
1. #T2024-001 - Clean shelves (Raj Kumar) - Due 12:00 PM
2. #T2024-005 - Update gold rate board (Priya) - Due 10:00 AM

🔄 In Progress:
1. #T2024-008 - Stock count (Meena)
2. #T2024-010 - Security check (Arun)
...

[View Dashboard]
```

**3. End-of-Day Report (9:00 PM)**

```
📊 End of Day Report - [Date]

Today's Summary:
✅ Completed: 23 (85%)
⏰ Overdue: 3 (11%)
❌ Incomplete: 1 (4%)

━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Overdue Tasks (carried forward):
1. #T2024-001 - Clean shelves (Raj Kumar)
   • Reason: Shelf bracket broken (Issue reported)
   • Subtask #T2024-001-S1 created for you

2. #T2024-015 - Rearrange jewelry display (Meena)
   • No response from employee

3. #T2024-020 - Check CCTV recordings (Arun)
   • Employee comment: "File corrupted"

━━━━━━━━━━━━━━━━━━━━━━━━

Top Performers:
🥇 Priya - 6/6 tasks completed
🥈 Lakshmi - 5/5 tasks completed
🥉 Kumar - 4/4 tasks completed

[View Detailed Report] [Send Reminder to Employees]
```

### Report Delivery Methods

**Owner receives reports via:**
1. Telegram message to owner's personal chat
2. Visible in dashboard "Reports" section
3. Email notification (optional, post-MVP)

---

## Frontend Dashboard Design (Functional, Not Fancy)

### Layout Structure

**Sidebar Navigation:**
- Dashboard (Overview)
- Tasks
- Routines
- Employees
- Reports
- Settings

### Key Pages

#### 1. Dashboard (Home)
```
┌─────────────────────────────────────────────────────┐
│  Jewelry Shop Task Manager                          │
│  Welcome back, [Owner Name]                         │
└─────────────────────────────────────────────────────┘

┌─────────────┬─────────────┬─────────────┬──────────┐
│ ✅ Completed │ ⏳ Pending   │ ⏰ Overdue   │ 👥 Present│
│     23       │     8        │     3        │    7/8   │
└─────────────┴─────────────┴─────────────┴──────────┘

Today's Attendance
[Attendance summary with employee names and status]

Recent Tasks
[Table showing latest 10 tasks with status, employee, due time]

Quick Actions
[Assign New Task] [View All Tasks] [Generate Report]
```

#### 2. Tasks Page
```
┌─────────────────────────────────────────────────────┐
│  Tasks                                    [+ New Task]│
└─────────────────────────────────────────────────────┘

Filters: 
[All Status ▼] [All Employees ▼] [Today ▼] [All Priority ▼]

┌────────────────────────────────────────────────────┐
│ Task #      │ Title          │ Assigned To │ Due    │ Status    │
├────────────────────────────────────────────────────┤
│ T2024-001   │ Clean shelves  │ Raj Kumar   │ 6 PM   │ ⏰ Overdue │
│ T2024-002   │ Update board   │ Priya       │ 10 AM  │ ✅ Done    │
│ T2024-003   │ Stock count    │ Meena       │ 5 PM   │ ⏳ Pending │
└────────────────────────────────────────────────────┘
[Click row to view details/subtasks/comments]
```

#### 3. Task Detail Modal
```
┌───────────────────────────────────────────┐
│  Task #T2024-001                    [✕]   │
├───────────────────────────────────────────┤
│  Clean display shelves                    │
│  🔴 High Priority                         │
│  ⏰ Due: Nov 04, 2024 6:00 PM            │
│  👤 Assigned to: Raj Kumar               │
│  📊 Status: Overdue                      │
│                                           │
│  Description:                             │
│  Clean all display shelves and rearrange │
│  jewelry items for better visibility      │
│                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                           │
│  🔗 Subtasks (1):                        │
│  ⚠️ #T2024-001-S1 - Fix shelf bracket    │
│     (Assigned to: You)                    │
│     Status: Pending                       │
│                                           │
│  💬 Comments (2):                         │
│  [Raj Kumar] 2:30 PM: "Bracket broken"   │
│  [You] 2:45 PM: "Will fix tomorrow"      │
│                                           │
│  [Add Comment] [Mark Complete] [Edit]    │
└───────────────────────────────────────────┘
```

#### 4. Routines Page
```
┌─────────────────────────────────────────────────────┐
│  Routines                            [+ New Routine] │
└─────────────────────────────────────────────────────┘

Daily Routines (12)
┌────────────────────────────────────────────────────┐
│ Turn on lights            │ 6:00 PM  │ 🟢 Active   │ [Edit] │
│ Clean shelves             │ 6:30 PM  │ 🟢 Active   │ [Edit] │
│ Update gold rate board    │ 10:00 AM │ 🟢 Active   │ [Edit] │
└────────────────────────────────────────────────────┘

Weekly Routines (5)
┌────────────────────────────────────────────────────┐
│ Stock inventory count     │ Sat 5 PM │ 🟢 Active   │ [Edit] │
│ Deep cleaning             │ Sun 7 PM │ 🟢 Active   │ [Edit] │
└────────────────────────────────────────────────────┘

Monthly Routines (3)
┌────────────────────────────────────────────────────┐
│ GST documentation         │ 28th     │ 🟢 Active   │ [Edit] │
│ Security audit            │ 15th     │ 🟢 Active   │ [Edit] │
└────────────────────────────────────────────────────┘
```

#### 5. Employees Page
```
┌─────────────────────────────────────────────────────┐
│  Employees                         [+ Add Employee]  │
└─────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ Name        │ Labels            │ Status  │ Tasks  │
├────────────────────────────────────────────────────┤
│ Raj Kumar   │ 🧹 Janitor        │ ✅ Active │ 5 open │
│ Priya       │ 💼 Sales          │ ✅ Active │ 3 open │
│ Arun        │ 🔒 Security       │ ✅ Active │ 2 open │
│ Meena       │ 💼 Sales          │ ✅ Active │ 4 open │
│ Kumar       │ 💰 Cashier        │ ✅ Active │ 1 open │
└────────────────────────────────────────────────────┘
```

### UI Design Principles (Functional, Not Fancy)

**Color Palette:**
- Primary: Simple blue (#3B82F6)
- Success: Green (#10B981)
- Warning: Amber (#F59E0B)
- Danger: Red (#EF4444)
- Neutral: Gray shades

**Typography:**
- Font: Inter or System UI
- Sizes: Clear hierarchy (32px headers, 16px body, 14px captions)

**Components:**
- Clean tables with hover states
- Simple buttons (solid, no gradients)
- Clear form inputs with validation
- Modal dialogs for details
- Toast notifications for success/error

**No Fancy Stuff:**
- ❌ No animations (except simple fades)
- ❌ No gradients
- ❌ No parallax effects
- ❌ No complex charts (simple bar/line charts only)
- ✅ Fast loading
- ✅ Responsive (mobile-friendly but desktop-first)
- ✅ Keyboard navigation
- ✅ Clear visual hierarchy

---

## Implementation Task Breakdown

### Phase 1: Foundation (Week 1-2)

**Week 1: Backend Setup & Core Models**

**Day 1-2: Project Setup**
- [ ] Initialize Git repository with proper .gitignore
- [ ] Set up Python virtual environment
- [ ] Install FastAPI, SQLAlchemy, Alembic, python-telegram-bot
- [ ] Create project structure:
  ```
  backend/
  ├── app/
  │   ├── api/
  │   │   ├── auth.py
  │   │   ├── employees.py
  │   │   ├── tasks.py
  │   │   ├── routines.py
  │   │   └── reports.py
  │   ├── models/
  │   │   ├── user.py
  │   │   ├── employee.py
  │   │   ├── task.py
  │   │   ├── routine.py
  │   │   └── attendance.py
  │   ├── schemas/
  │   ├── core/
  │   │   ├── config.py
  │   │   ├── security.py
  │   │   └── database.py
  │   ├── services/
  │   │   ├── telegram_bot.py
  │   │   ├── task_service.py
  │   │   └── notification_service.py
  │   └── main.py
  ├── alembic/
  ├── tests/
  └── requirements.txt
  ```
- [ ] Set up environment variables (.env file)
- [ ] Configure PostgreSQL connection

**Day 3-4: Database Models & Migrations**
- [ ] Define SQLAlchemy models for all tables (users, employees, tasks, routines, attendance, etc.)
- [ ] Create Alembic migrations
- [ ] Test database schema creation
- [ ] Add indexes for performance (employee_id, task_id, date fields)
- [ ] Create seed data script for testing

**Day 5-7: Authentication & User Management**
- [ ] Implement JWT token generation and validation
- [ ] Create auth endpoints (login, logout, refresh)
- [ ] Implement password hashing (bcrypt)
- [ ] Create middleware for protected routes
- [ ] Test authentication flow
- [ ] Create first owner user via script

**Week 2: Telegram Bot Foundation & Employee Management**

**Day 1-3: Telegram Bot Setup**
- [ ] Set up Telegram bot via BotFather
- [ ] Implement python-telegram-bot handlers
- [ ] Create webhook endpoint in FastAPI
- [ ] Implement `/start` command (register employee Telegram ID)
- [ ] Implement `/help` command
- [ ] Test bot connectivity
- [ ] Create bot command handler structure
- [ ] Implement inline keyboard creation utility

**Day 4-5: Employee Management API**
- [ ] Implement employee CRUD endpoints
- [ ] Implement label management endpoints
- [ ] Create employee-label assignment logic
- [ ] Test API endpoints with Postman/Thunder Client
- [ ] Add validation and error handling

**Day 6-7: Attendance System**
- [ ] Implement attendance marking via Telegram
- [ ] Create morning attendance reminder (8:00 AM)
- [ ] Implement auto-absent marking (after 8 hours)
- [ ] Create attendance API endpoints
- [ ] Test attendance flow end-to-end
- [ ] Generate attendance report logic

---

### Phase 2: Core Task Management (Week 3-4)

**Week 3: Task Creation & Assignment**

**Day 1-3: Task System Backend**
- [ ] Implement task CRUD endpoints
- [ ] Create task assignment logic
- [ ] Implement task status transitions
- [ ] Create subtask creation logic
- [ ] Link subtasks to parent tasks
- [ ] Add task comment system
- [ ] Test all task operations

**Day 4-5: Telegram Task Notifications**
- [ ] Implement task assignment message with inline keyboard
- [ ] Create button handlers (Complete, Issue, Comment)
- [ ] Implement message_id tracking in database
- [ ] Test task notification delivery
- [ ] Handle reply-to-message linking for comments/issues

**Day 6-7: Task Completion & Subtask Workflow**
- [ ] Implement task completion logic
- [ ] Add blocker checking (prevent completion if subtasks open)
- [ ] Create subtask-to-owner notification
- [ ] Implement blocker-resolved notification to employee
- [ ] Test full task lifecycle (assign → issue → subtask → resolve → complete)

**Week 4: Recurring Routines & Scheduling**

**Day 1-3: Routine Management**
- [ ] Implement routine CRUD endpoints
- [ ] Create routine-label assignment
- [ ] Build recurrence pattern logic (daily/weekly/monthly)
- [ ] Test routine creation and editing

**Day 4-5: Task Generation from Routines**
- [ ] Implement APScheduler for cron jobs
- [ ] Create daily routine task generation (7:30 AM)
- [ ] Create weekly routine task generation
- [ ] Create monthly routine task generation
- [ ] Test task auto-generation
- [ ] Handle edge cases (last day of month, etc.)

**Day 6-7: Overdue Detection & Reminders**
- [ ] Implement overdue detection cron job (every 30 min)
- [ ] Create reminder messages (midday & end-of-day)
- [ ] Implement task carryforward logic
- [ ] Test reminder delivery
- [ ] Add reminder throttling (avoid spam)

---

### Phase 3: Frontend Dashboard (Week 5)

**Day 1-2: Next.js Setup & Layout**
- [ ] Initialize Next.js 14 project with TypeScript in `frontend/` folder
- [ ] Set up Tailwind CSS with custom configuration
- [ ] Install shadcn/ui components (button, card, form, input, table, dialog, etc.)
- [ ] Create project folder structure:
  - `src/app/` - Next.js app router pages (auth, dashboard layouts)
  - `src/components/` - Reusable components (ui, layout, feature-specific)
  - `src/lib/` - API client, auth context, utilities
  - `src/types/` - TypeScript interfaces for API models
- [ ] Create layout structure (sidebar navigation, header with user menu)
- [ ] Implement app routing with layout groups (auth, dashboard)
- [ ] Set up TanStack Query (React Query) for API state management
- [ ] Create Axios API client with interceptors for cookie-based auth

**Day 3-4: Authentication & Dashboard Page**
- [ ] Create login page with React Hook Form + Zod validation
- [ ] Implement JWT token storage using **HTTP-only cookies**
- [ ] Create authentication context provider (useAuth hook)
- [ ] Implement protected route middleware for dashboard pages
- [ ] Add automatic token refresh logic
- [ ] Build dashboard overview page with grid layout
- [ ] Create attendance summary widget (present/absent counts, today's date)
- [ ] Create task status cards (completed, pending, in-progress, overdue counts)
- [ ] Display recent tasks table with status badges and priority indicators
- [ ] Add logout functionality with token cleanup

**Day 5: Tasks Page**
- [ ] Create tasks list page with filters
- [ ] Implement task creation modal
- [ ] Build task detail modal (with subtasks & comments)
- [ ] Add manual task assignment UI
- [ ] Show employee selector with label filtering

**Day 6: Routines & Employees Pages**
- [ ] Create routines list page
- [ ] Implement routine creation/edit modal
- [ ] Build employees list page
- [ ] Create employee creation/edit modal
- [ ] Add label management UI

**Day 7: Reports Page**
- [ ] Create daily reports view
- [ ] Display attendance reports
- [ ] Show completion rate analytics
- [ ] Add overdue task summary
- [ ] Implement date range filtering

---

### Phase 4: Reports, Testing & Polish (Week 6)

**Day 1-2: Owner Notification System**
- [ ] Implement owner Telegram notifications
- [ ] Create morning attendance report
- [ ] Create midday progress report
- [ ] Create end-of-day report
- [ ] Add "send to owner" logic for all report types
- [ ] Test report delivery timing

**Day 3-4: Integration Testing**
- [ ] Test complete user flows:
  - [ ] Employee onboarding (register via /start)
  - [ ] Attendance marking → task delivery
  - [ ] Task assignment → notification → completion
  - [ ] Issue reporting → subtask creation → resolution
  - [ ] Routine task generation → assignment → completion
  - [ ] Overdue detection → reminders
  - [ ] Daily reports to owner
- [ ] Fix bugs found during testing
- [ ] Handle edge cases

**Day 5: UI Polish & Responsiveness**
- [ ] Test dashboard on different screen sizes
- [ ] Ensure mobile-friendly (responsive tables)
- [ ] Add loading states (skeletons, spinners)
- [ ] Add error handling and user feedback (toast notifications)
- [ ] Improve form validation messages
- [ ] Add keyboard shortcuts (optional)

**Day 6-7: Documentation & Demo Preparation**
- [ ] Write API documentation (Swagger/OpenAPI)
- [ ] Create user guide for owner (PDF or in-app help)
- [ ] Document bot commands for employees
- [ ] Create seed data for demo (5 employees, 20 tasks, 10 routines)
- [ ] Prepare demo script (what to show client)
- [ ] Test entire system one more time

---

### Phase 5: Deployment (Week 7-8)

**Week 7: Containerization & VPS Setup**

**Day 1-2: Docker Configuration**
- [ ] Write Dockerfile for FastAPI backend
- [ ] Write Dockerfile for Next.js frontend
- [ ] Create docker-compose.yml (backend, frontend, PostgreSQL)
- [ ] Test local Docker deployment
- [ ] Set up environment variable management
- [ ] Configure volume mounts for PostgreSQL data

**Day 3-4: VPS Preparation**
- [ ] Install Coolify on your VPS (if not already done)
- [ ] Configure domain/subdomain (e.g., tasks.jewelryshop.com)
- [ ] Set up SSL certificates (Coolify handles this automatically)
- [ ] Create PostgreSQL database in Coolify
- [ ] Configure environment variables in Coolify

**Day 5-7: Deployment & Testing**
- [ ] Push Docker images to registry (Docker Hub or Coolify's registry)
- [ ] Deploy backend via Coolify
- [ ] Deploy frontend via Coolify
- [ ] Configure reverse proxy (Caddy/Traefik via Coolify)
- [ ] Set up Telegram webhook to point to your backend URL
- [ ] Test production deployment
- [ ] Run database migrations on production
- [ ] Load seed data for demo

**Week 8: Monitoring, Backup & Demo**

**Day 1-2: Monitoring & Logging**
- [ ] Set up basic logging (Python logging to files)
- [ ] Configure log rotation
- [ ] Add health check endpoint (`/health`)
- [ ] Set up uptime monitoring (UptimeRobot or similar)
- [ ] Configure error notifications (email or Telegram)

**Day 3-4: Backup Strategy**
- [ ] Set up automated PostgreSQL backups (daily)
- [ ] Test backup restoration
- [ ] Document backup procedures
- [ ] Configure off-site backup storage (optional)

**Day 5: Final Testing & Bug Fixes**
- [ ] Test all features on production
- [ ] Fix any deployment-specific bugs
- [ ] Verify Telegram bot works in production
- [ ] Test with real phone numbers
- [ ] Ensure notifications are delivered

**Day 6-7: Demo Preparation & Client Handoff**
- [ ] Create demo environment with sample data
- [ ] Prepare demo presentation (show features)
- [ ] Document known limitations (post-MVP features)
- [ ] Create video walkthrough (optional)
- [ ] Schedule demo meeting with client
- [ ] Prepare feedback collection mechanism

---

## Deployment Strategy

### Infrastructure Overview

**Your VPS with Coolify:**
```
┌─────────────────────────────────────────────┐
│           Your VPS (Coolify)                │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Caddy/Traefik (Reverse Proxy)       │  │
│  │  - SSL/TLS termination               │  │
│  │  - tasks.jewelryshop.com             │  │
│  └──────────┬───────────────────────────┘  │
│             │                               │
│  ┌──────────▼──────────┐  ┌──────────────┐ │
│  │  Next.js Frontend   │  │   FastAPI    │ │
│  │  (Docker Container) │  │   Backend    │ │
│  │  Port: 3000         │  │   Port: 8000 │ │
│  └─────────────────────┘  └──────┬───────┘ │
│                                   │         │
│  ┌────────────────────────────────▼──────┐ │
│  │     PostgreSQL Database              │ │
│  │     (Docker Container or Native)     │ │
│  │     Port: 5432                       │ │
│  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Deployment Steps with Coolify

**1. Prepare Docker Compose Configuration**

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: jewelry-backend
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: jewelry-frontend
    env_file: .env
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://api.tasks.jewelryshop.com
    restart: unless-stopped

  db:
    image: postgres:15
    container_name: jewelry-db
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped

volumes:
  postgres_data:
```

**2. Push to Git Repository**
- Push your code to GitHub/GitLab
- Ensure `.env` is in `.gitignore`

**3. Deploy via Coolify**
- In Coolify dashboard, create new project
- Connect to your Git repository
- Coolify auto-detects docker-compose.yml
- Set environment variables in Coolify UI
- Deploy!

**4. Configure Domains**
- Frontend: `tasks.jewelryshop.com`
- Backend API: `api.tasks.jewelryshop.com`
- Coolify automatically provisions SSL certificates

**5. Set Up Telegram Webhook**
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://api.tasks.jewelryshop.com/api/telegram/webhook"
```

### Environment Variables (.env)

```bash
# Database
DB_HOST=db
DB_PORT=5432
DB_NAME=jewelry_tasks
DB_USER=jewelry_admin
DB_PASSWORD=<strong_password>

# Backend
SECRET_KEY=<generate_random_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Telegram
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_OWNER_CHAT_ID=<owner_telegram_user_id>

# Frontend
NEXT_PUBLIC_API_URL=https://api.tasks.jewelryshop.com

# Timezone
TZ=Asia/Kolkata
```

### Backup Strategy

**Automated Daily Backup (Cron Job):**
```bash
# Add to VPS crontab
0 2 * * * docker exec jewelry-db pg_dump -U jewelry_admin jewelry_tasks > /backups/db_backup_$(date +\%Y\%m\%d).sql
```

**Backup Rotation:**
- Keep daily backups for 7 days
- Weekly backups for 4 weeks
- Monthly backups for 6 months

**Restoration Test:**
- Test backup restoration monthly

---

## Security Considerations

### Backend Security

**1. Authentication & Authorization**
- JWT tokens with short expiry (30 minutes access, 7 days refresh)
- Password hashing with bcrypt (cost factor 12)
- Role-based access control (owner, admin, employee)
- No sensitive data in JWT payload

**2. API Security**
- Rate limiting (100 requests per 15 minutes per IP)
- CORS configured for frontend domain only
- Input validation on all endpoints (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- No raw SQL queries

**3. Telegram Bot Security**
- Verify webhook requests from Telegram (check X-Telegram-Bot-Api-Secret-Token header)
- Validate user IDs against database
- Never expose database IDs in Telegram messages
- Rate limit bot commands per user

**4. Environment & Secrets**
- Never commit .env to Git
- Use strong random secrets (minimum 32 characters)
- Separate credentials for dev/staging/production
- Rotate secrets periodically

### Database Security

- Database not exposed to public internet (Docker internal network)
- Strong password (16+ characters, alphanumeric + special)
- Regular backups with encryption
- Separate database user with limited privileges for application

### Frontend Security

- No sensitive data in localStorage (use httpOnly cookies for tokens)
- HTTPS only (enforced by Coolify)
- XSS prevention (React escapes by default, but sanitize user inputs)
- CSRF protection for API calls
- Content Security Policy headers

---

## Testing Checklist

### Backend Tests

**Unit Tests:**
- [ ] Task creation and assignment logic
- [ ] Recurrence pattern generation (daily/weekly/monthly)
- [ ] Overdue detection algorithm
- [ ] Subtask dependency blocking
- [ ] Attendance auto-marking after 8 hours

**Integration Tests:**
- [ ] Authentication flow (login, token refresh)
- [ ] Task CRUD operations
- [ ] Employee-task assignment
- [ ] Routine task generation
- [ ] Telegram webhook handling
- [ ] Report generation

**API Tests (with Postman/Bruno):**
- [ ] All endpoints return correct status codes
- [ ] Error responses are properly formatted
- [ ] Validation errors return helpful messages
- [ ] Pagination works correctly
- [ ] Filtering and sorting work

### Frontend Tests

**Manual Testing:**
- [ ] Login and logout work
- [ ] Dashboard displays correct data
- [ ] Task creation and assignment flow
- [ ] Routine creation and editing
- [ ] Employee management
- [ ] Reports display correctly
- [ ] All forms validate inputs
- [ ] Error messages are user-friendly
- [ ] Loading states show properly

**Responsive Testing:**
- [ ] Test on mobile (375px width)
- [ ] Test on tablet (768px width)
- [ ] Test on desktop (1920px width)
- [ ] All modals are usable on mobile

### Telegram Bot Tests

**Command Tests:**
- [ ] /start registers employee correctly
- [ ] /help displays commands
- [ ] /tasks shows assigned tasks
- [ ] /attendance allows manual marking

**Workflow Tests:**
- [ ] Attendance reminder sent at 8:00 AM
- [ ] Task notifications sent after attendance
- [ ] Inline buttons work correctly
- [ ] Reply-to-message creates comments/subtasks
- [ ] Completion updates database
- [ ] Owner receives notifications

**Edge Case Tests:**
- [ ] Employee not registered tries to use bot
- [ ] Multiple button presses (prevent duplicate actions)
- [ ] Network errors during bot operation
- [ ] Telegram API rate limits

### End-to-End Tests

**Complete User Journeys:**
1. **New Employee Onboarding:**
   - Owner creates employee in dashboard
   - Employee starts bot with /start
   - System links Telegram ID to employee
   - ✅ Success criteria: Employee can receive tasks

2. **Daily Routine Flow:**
   - 8:00 AM: Attendance reminder sent
   - Employee marks present
   - System delivers all tasks for the day
   - Employee completes tasks throughout day
   - 9:00 PM: Owner receives end-of-day report
   - ✅ Success criteria: All tasks tracked, report accurate

3. **Issue Reporting Flow:**
   - Employee receives task
   - Encounters problem, presses "Report Issue"
   - Types issue description
   - System creates subtask for owner
   - Owner sees subtask in dashboard
   - Owner resolves and marks subtask complete
   - Employee notified, completes original task
   - ✅ Success criteria: Task blocked correctly, resolution notifies employee

4. **Overdue Task Handling:**
   - Task not completed by due time
   - System marks as overdue
   - 3:00 PM reminder sent
   - 9:00 PM reminder sent
   - Task carries forward to next day
   - Owner receives overdue report
   - ✅ Success criteria: Reminders sent, task visible next day

---

## Post-MVP Enhancement Roadmap

### Phase 2 Features (3-4 months)

**1. Automatic Task Assignment Engine**
- Implement rule-based assignment algorithm:
  - Match task labels with employee labels
  - Check attendance status
  - Calculate workload (open tasks count)
  - Round-robin tiebreaker
- Owner can override auto-assignments
- Assignment history and audit log

**2. Photo Upload for Task Completion**
- Allow employees to upload photos via Telegram
- Store photos in VPS or cloud storage (S3/Cloudinary)
- Display photos in task history
- Owner can view completion proof

**3. WhatsApp Business API Integration**
- Set up Meta Business account
- Implement WhatsApp message templates
- Dual-channel support (Telegram + WhatsApp)
- Employee can choose preferred platform

**4. Advanced Analytics**
- Employee performance trends (charts)
- Task completion rate over time
- Bottleneck identification (most overdue tasks)
- Predictive analytics (forecast busy periods)
- Export reports to PDF/Excel

**5. Mobile App for Owner**
- React Native app for iOS/Android
- Push notifications for urgent subtasks
- Quick task assignment on-the-go
- Approve/reject employee requests

### Phase 3 Features (6-12 months)

**6. AI-Powered Features**
- Smart task priority recommendation
- Predictive workload balancing
- Natural language task creation ("Create a task to clean shelves tomorrow at 6 PM")
- Sentiment analysis on employee comments (detect frustration)

**7. Multi-Shop Support**
- Support multiple jewelry shops under one account
- Per-shop employee management
- Cross-shop task assignment
- Consolidated reporting

**8. Advanced Scheduling**
- Shift management for employees
- Task assignment based on shift hours
- Overtime tracking
- Leave management

**9. Integration Ecosystem**
- Google Calendar sync (owner sees tasks as calendar events)
- Slack notifications (for enterprises)
- Zapier webhooks for custom automations
- REST API for third-party integrations

**10. Gamification & Incentives**
- Employee leaderboards
- Task completion streaks
- Badges and achievements
- Performance bonuses based on metrics

---

## Known Limitations (MVP)

**Explicitly Excluded from MVP:**
1. Photo/file uploads (text-only)
2. WhatsApp integration (Telegram only)
3. Automatic assignment (manual only)
4. Advanced analytics (basic reports only)
5. Mobile app (web-only for owner)
6. Multi-shop support (single shop)
7. Shift management
8. Leave management system
9. Employee app login (owner-only dashboard)
10. Multi-language support (English only)

**Technical Debt to Address Post-MVP:**
1. Add comprehensive test coverage (unit + integration tests)
2. Implement proper logging and monitoring (Sentry, Grafana)
3. Set up CI/CD pipeline (GitHub Actions)
4. Add API rate limiting per user
5. Implement WebSocket for real-time dashboard updates
6. Optimize database queries (add missing indexes)
7. Add Redis for caching frequently accessed data
8. Implement proper error recovery for Telegram bot

---

## Risk Mitigation

### Technical Risks

**Risk: Telegram API downtime or rate limits**
- Mitigation: Implement message queue (Celery + Redis) for async delivery
- Fallback: SMS notifications via Twilio (post-MVP)

**Risk: Database corruption or data loss**
- Mitigation: Automated daily backups with off-site storage
- Test restoration monthly

**Risk: VPS downtime**
- Mitigation: Set up uptime monitoring with instant alerts
- Document restoration procedures
- Consider managed database (post-MVP) for critical data

**Risk: Telegram bot webhook failures**
- Mitigation: Implement retry logic with exponential backoff
- Log all failed webhook calls for manual review

### User Adoption Risks

**Risk: Employees resist using Telegram**
- Mitigation: Onboarding session with owner + employees
- Show benefits: no more missed tasks, clear communication
- Owner mandate: "Official communication channel"

**Risk: Owner finds dashboard too complex**
- Mitigation: Focus on simplicity (functional, not fancy)
- Provide 1-hour training session
- Create video tutorials

**Risk: Client rejects MVP**
- Mitigation: Regular check-ins during development (show progress)
- Gather feedback early (after Week 4)
- Be flexible with scope adjustments

---

## Success Metrics (Demo Phase)

**For Client Demo:**
1. Owner can create and assign 5 tasks in under 3 minutes
2. Employees receive task notifications within 10 seconds
3. Task completion flow works end-to-end (assign → notify → complete → report)
4. Daily reports delivered on time (8 AM, 3 PM, 9 PM)
5. Zero crashes during 30-minute demo
6. All core features demonstrated successfully

**Post-Launch (First Month):**
1. 80%+ task completion rate
2. 90%+ daily attendance marking rate
3. Average task completion time < 24 hours
4. Owner spends <30 minutes daily on task management (vs 2+ hours manually)
5. Zero critical bugs reported

---

## Budget & Resource Estimates

### Development Time (Solo Developer)
- **Full-time (40 hrs/week):** 7-8 weeks
- **Part-time (20 hrs/week):** 14-16 weeks

### Infrastructure Costs (Monthly)
- VPS with Coolify: $10-30 (depending on provider)
- Domain + SSL: $12/year (~$1/month)
- Telegram Bot: $0 (free)
- **Total MVP cost:** ~$15-35/month

### Post-MVP Costs (if scaling)
- WhatsApp Business API: ~$50-100/month (conversation-based pricing)
- Cloud storage for photos: $5-10/month (S3/Cloudinary)
- Monitoring tools (Sentry): $0-29/month (free tier available)

---

## Development Principles for This Project

**1. Keep It Simple (KISS)**
- Don't over-engineer
- Choose simple solutions over clever ones
- Avoid premature optimization

**2. Make It Work First, Then Make It Good**
- Get end-to-end flow working first
- Refactor after seeing patterns
- Polish UI in final weeks

**3. Test Early, Test Often**
- Don't wait until end to test Telegram bot
- Test with real phone numbers during development
- Catch integration issues early

**4. Documentation As You Go**
- Document API endpoints when creating them
- Write inline comments for complex logic
- Keep this plan updated if scope changes

**5. Client Communication**
- Show progress every 2 weeks
- Be transparent about challenges
- Underpromise, overdeliver

---

## Final Checklist Before Client Demo

### Technical Readiness
- [ ] All core features working on production
- [ ] Database populated with realistic demo data
- [ ] Telegram bot responding reliably
- [ ] Dashboard accessible via clean URL
- [ ] No console errors or warnings
- [ ] All loading states implemented
- [ ] Error messages user-friendly

### Demo Preparation
- [ ] Demo script prepared (step-by-step)
- [ ] Demo account credentials ready
- [ ] 5 demo employees registered in Telegram
- [ ] 20 tasks pre-created (various statuses)
- [ ] 10 routines configured
- [ ] Test demo flow 2-3 times before meeting
- [ ] Backup plan if internet fails (video recording)

### Documentation
- [ ] User guide for owner (PDF)
- [ ] Bot command reference for employees
- [ ] Known limitations documented
- [ ] Post-MVP roadmap prepared
- [ ] Pricing for Phase 2 features (if applicable)

### Post-Demo
- [ ] Collect client feedback systematically
- [ ] Document requested changes
- [ ] Prioritize feedback for quick wins
- [ ] Schedule follow-up meeting

---

## Conclusion

This implementation plan provides a comprehensive roadmap to build a fully functional MVP of your jewelry shop task management system in 6-8 weeks. The plan prioritizes:

1. **Rapid Value Delivery:** Core features working in 4 weeks
2. **User-Centric Design:** Simple, functional UI focused on owner and employee needs
3. **Technical Soundness:** Scalable architecture that supports future growth
4. **Risk Management:** Clear mitigation strategies for common pitfalls

**Next Steps:**
1. Review this plan and confirm alignment
2. Set up development environment (Week 1, Day 1)
3. Begin Phase 1: Foundation
4. Schedule weekly check-ins to track progress

This system will transform your client's shop operations, eliminating manual task tracking and ensuring accountability. The Telegram-first approach reduces friction for employees, while the web dashboard gives the owner complete control and visibility.

**Let's build this! 🚀**

Questions or need clarification on any section? I'm here to help refine and adapt this plan as we go.
