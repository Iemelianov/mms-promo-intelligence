# Promo Scenario Co-Pilot Frontend

React + TypeScript frontend for the Promo Scenario Co-Pilot application.

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm preview
```

## Environment Variables

- Скопіюй `.env.example` → `.env` у `frontend/`.
- Мінімум: `VITE_API_URL=http://localhost:8000` (або інший бекенд URL).

## Project Structure

```
frontend/
├── src/
│   ├── components/     # Reusable React components
│   ├── screens/         # Main application screens
│   ├── services/        # API client (axios) with typed endpoints
│   ├── store/           # Global UI store (Zustand)
│   ├── types.ts         # Shared domain/API types
│   └── App.tsx          # Main app component
├── public/              # Static assets
└── package.json         # Dependencies and scripts
```

## API Client & Data

- API клієнт: `src/services/api.ts` (axios, unwrap .data, базовий лог).
- Спільні типи домену/API: `src/types.ts` синхронізовані з `docs/data-models.md` та бекенд `models/schemas.py`.
- Стан запитів: React Query (`src/main.tsx`), глобальний UI: Zustand (`src/store/useUIStore.ts`).

## Features

- **Discovery Screen**: View opportunities and gap analysis
- **Scenario Lab**: Create and compare promotional scenarios
- **Optimization**: Generate optimized scenarios and view efficient frontier
- **Creative**: Generate creative briefs and asset specifications

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query (React Query)
- Axios
