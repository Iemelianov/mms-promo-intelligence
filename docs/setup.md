# Setup Guide

## Quick Start (Hackathon)

For a quick setup during hackathon, follow these steps:

### 1. Prerequisites Check

```bash
# Check Python version
python --version  # Should be 3.10+

# Check Node.js version
node --version  # Should be 18+

# Check if PostgreSQL is installed (optional for local)
psql --version
```

### 2. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd MMS

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 3. Configure Environment

**Backend** (`backend/.env`):
```bash
# Minimum required for hackathon
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=duckdb:///data/promo.db  # Use DuckDB for local
ENVIRONMENT=development
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_URL=http://localhost:8000
```

### 4. Load Sample Data

```bash
cd backend
python scripts/load_sample_data.py
```

This will:
- Create database schema
- Load sample sales data (CSV)
- Load mock CDP segments
- Create sample promotional catalog

### 5. Run Application

**Terminal 1 - Backend**:
```bash
cd backend
source venv/bin/activate
uvicorn api.main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Terminal 3 - Phoenix (Optional)**:
```bash
phoenix serve
```

### 6. Verify Setup

1. Open browser: `http://localhost:5173` (or port shown in terminal)
2. Check backend: `http://localhost:8000/docs` (FastAPI docs)
3. Check Phoenix: `http://localhost:6006` (if running)

## Full Production Setup

### Database Setup (PostgreSQL)

```bash
# Create database
createdb promo_co_pilot

# Run migrations
cd backend
alembic upgrade head

# Load initial data
python scripts/load_sample_data.py
```

### Environment Variables (Production)

**Backend**:
```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional

# Database
DATABASE_URL=postgresql://user:password@host:5432/promo_co_pilot

# Observability
PHOENIX_API_KEY=...
PHOENIX_ENDPOINT=https://phoenix.yourdomain.com

# External APIs
# Open-Meteo API (free, no API key required)
# WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
CDP_API_URL=https://cdp.yourdomain.com

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://yourdomain.com

# App
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Frontend**:
```bash
VITE_API_URL=https://api.yourdomain.com
VITE_PHOENIX_ENDPOINT=https://phoenix.yourdomain.com
```

### Docker Setup

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes Setup

See `k8s/` directory for Kubernetes manifests.

## Data Preparation

### Converting XLSB to CSV

For hackathon, convert historical data:

```bash
cd data
python scripts/convert_xlsb_to_csv.py input.xlsb output.csv
```

The script extracts:
- Date
- Channel (web/store)
- Department
- Sales value
- Margin value
- Units
- Promo flag
- Discount percentage

### Sample Data Structure

**sales_aggregated.csv**:
```csv
date,channel,department,promo_flag,discount_pct,sales_value,margin_value,units
2024-01-01,online,TV,false,0,50000,12500,100
2024-01-02,online,TV,true,20,75000,15000,150
...
```

**segments.json**:
```json
[
  {
    "segment_id": "LOYAL_HIGH_VALUE",
    "name": "Loyal High Value",
    "share_of_customers": 0.18,
    "share_of_revenue": 0.42,
    "avg_basket_value": 320,
    "fav_categories": ["TV", "Audio", "Gaming"],
    "discount_sensitivity": "low"
  }
]
```

## Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend builds and runs
- [ ] Database connection works
- [ ] Sample data loaded
- [ ] API endpoints respond
- [ ] LLM API key configured
- [ ] Phoenix tracing works (optional)
- [ ] Can create a scenario
- [ ] Can generate creative brief

## Troubleshooting

### Backend Issues

**Import errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Database connection errors**:
```bash
# For DuckDB, ensure directory exists
mkdir -p data
# Database file will be created automatically

# For PostgreSQL, check connection
psql $DATABASE_URL -c "SELECT 1;"
```

**LLM API errors**:
- Verify API key is correct
- Check rate limits
- Ensure sufficient credits

### Frontend Issues

**Build errors**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API connection errors**:
- Verify `VITE_API_URL` in `.env`
- Check CORS settings in backend
- Ensure backend is running

**Port conflicts**:
- Change port in `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 3000  // Change to available port
  }
})
```

## Next Steps

After setup:
1. Review [Architecture Documentation](./architecture.md)
2. Read [Development Guide](./development.md)
3. Explore [API Documentation](./api/README.md)
4. Check [UI Specifications](./ui-specs.md)

## Support

For issues:
1. Check logs in `backend/logs/`
2. Review browser console
3. Check Phoenix traces
4. Review test cases for examples

