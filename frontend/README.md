# Jewelry Shop Task Manager - Frontend

Next.js frontend application for the jewelry shop task management system.

## Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui
- **State Management:** TanStack Query (React Query)
- **HTTP Client:** Axios
- **Form Handling:** React Hook Form + Zod validation

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create environment file:

```bash
cp .env.example .env.local
```

3. Update `.env.local` with your API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Build for production:

```bash
npm run build
```

### Start Production Server

```bash
npm run start
```

## Project Structure

```
frontend/
├── app/                    # Next.js app router
│   ├── (auth)/            # Auth layout group
│   │   └── login/         # Login page
│   ├── (dashboard)/       # Dashboard layout group
│   │   ├── dashboard/     # Dashboard home
│   │   ├── employees/     # Employee management
│   │   ├── tasks/         # Task management
│   │   └── routines/      # Routine management
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page (redirects to login)
│   └── globals.css        # Global styles
├── components/
│   ├── ui/               # shadcn/ui components
│   ├── layout/           # Layout components (Header, Sidebar)
│   ├── employees/        # Employee-specific components
│   ├── tasks/            # Task-specific components
│   └── routines/         # Routine-specific components
├── lib/
│   ├── api/              # API client and endpoints
│   │   ├── client.ts     # Axios instance with interceptors
│   │   ├── auth.ts       # Authentication API
│   │   ├── employees.ts  # Employee API
│   │   ├── tasks.ts      # Task API
│   │   ├── routines.ts   # Routine API
│   │   ├── attendance.ts # Attendance API
│   │   └── dashboard.ts  # Dashboard stats API
│   ├── auth/             # Authentication context
│   ├── providers.tsx     # React Query provider
│   └── utils.ts          # Utility functions
├── types/
│   └── index.ts          # TypeScript type definitions
└── public/               # Static assets
```

## Authentication

The application uses JWT-based authentication with HTTP-only cookies:

- Login credentials are sent to `/api/auth/login`
- Access tokens are stored in HTTP-only cookies
- Automatic token refresh on 401 responses
- Protected routes redirect to login if not authenticated

Default login:
- Username: `admin`
- Password: `admin123`

## Features

### Implemented
- Authentication (login, logout, protected routes)
- API client with cookie-based auth
- TypeScript types for all API models
- React Query setup for data fetching

### To Be Implemented
- Login page UI
- Dashboard layout (sidebar, header)
- Dashboard home page
- Employee management (CRUD)
- Task management (create, assign, view)
- Routine management (CRUD)
- Attendance tracking
- Reports and analytics

## API Integration

The frontend communicates with the FastAPI backend through REST endpoints:

- `GET/POST /api/auth/*` - Authentication
- `GET/POST /api/employees` - Employee management
- `GET/POST /api/tasks` - Task management
- `GET/POST /api/routines` - Routine management
- `GET /api/attendance/*` - Attendance tracking
- `GET /api/dashboard/stats` - Dashboard statistics

## Development Notes

- All API calls use the centralized `apiClient` from `lib/api/client.ts`
- Authentication state is managed via `AuthContext`
- Protected routes use the `ProtectedRoute` wrapper
- Forms use React Hook Form + Zod for validation
- UI components follow shadcn/ui patterns

## Deployment

See the main project README for Docker deployment instructions.
