# Groww AI Frontend

Next.js (App Router) + TypeScript + Tailwind UI for the Mutual Fund FAQ assistant.

Design reference: [`../screens/GrowwRAGScreen.png`](../screens/GrowwRAGScreen.png).

## Prerequisites

- Node.js 20+
- FastAPI backend running at `http://127.0.0.1:8000` (see project root)

## Setup

```bash
cd frontend
cp .env.example .env.local   # edit BACKEND_URL if needed
npm install
npm run dev                  # http://localhost:3000
```

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Local development (Turbopack) |
| `npm run build` | Production build |
| `npm start` | Serve the production build |
| `npm run lint` | ESLint |

## Architecture

- Browser talks only to Next.js same-origin routes:
  - `POST /api/query` → FastAPI `POST /query`
  - `GET /api/stats` → FastAPI `GET /stats`
- Chat history, feedback and saved answers live in `localStorage`
- Multi-question answers from the backend are parsed into headings, prose and source links in `lib/answer.ts`
