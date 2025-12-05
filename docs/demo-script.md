# Demo Script (5–7 minutes)

Use this script to run the full demo quickly. Assumes you already ran `python backend/data/seed.py`.

## 0) Prep
- Backend: `cd backend && uvicorn api.main:app --reload`
- Frontend: `cd frontend && npm run dev`
- Base URLs: API `http://localhost:8000`, UI `http://localhost:5173`

## 1) Discovery (gap + context)
- Screen: Discovery
- Inputs: Month `2024-10`, Geo `DE`
- What to show:
  - Gap vs Target chart populates from `/api/v1/data/baseline` + `/api/v1/discovery/gaps`
  - Department heatmap from opportunities
  - Context card from `/api/v1/discovery/context`
- Backup cURL:
```bash
curl "http://localhost:8000/api/v1/discovery/opportunities?month=2024-10&geo=DE"
curl "http://localhost:8000/api/v1/discovery/gaps?month=2024-10&geo=DE"
```

## 2) Scenario Lab (create/evaluate/compare)
- Screen: Scenario Lab
- Auto-fetches optimized scenarios via `/api/v1/optimization/generate`
- Click a row to show KPI breakdown.
- Backup cURL:
```bash
curl -X POST http://localhost:8000/api/v1/optimization/generate \
  -H "Content-Type: application/json" \
  -d '{"brief":"Find October promos for electronics","constraints":{"objectives":{"sales":0.6,"margin":0.4}}}'
```

## 3) Optimization (efficient frontier)
- Screen: Optimization
- Shows frontier from `/api/v1/optimization/frontier?brief_id=demo-brief`
- Point click = scenario highlight (static demo points).

## 4) Creative Companion
- Screen: Creative
- Uses `/api/v1/creative/generate` with `scenario_ids=["demo_scenario"]`
- Show brief + asset cards (homepage hero/category banner).

## 5) Post-Mortem (fast path)
- If you have a scenario id, run:
```bash
curl -X POST http://localhost:8000/api/v1/postmortem/analyze \
  -H "Content-Type: application/json" \
  -d '{"scenario_id":"demo_scenario","actual_data":{"sales_value":3100000,"margin_value":700000,"units":17500},"period":{"start":"2024-10-22","end":"2024-10-27"}}'
```
- Or show the Post-Mortem screen after selecting a scenario in Scenario Lab.

## 6) Data processing (optional)
- Endpoint: `/api/v1/data/process-xlsb` accepts multiple files.
- Ready-made data: `backend/data/sample_sales.csv`; load to DuckDB via `python backend/data/seed.py`.

## 7) Talking points
- Agents/engines map to docs (`docs/api/README.md`, `docs/ui-specs.md`).
- Auth is dev-friendly (bearer optional); rate limits stubbed.
- Observability hooks in place (Phoenix-ready).
