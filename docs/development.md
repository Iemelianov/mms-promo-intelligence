# Development Guide

## Getting Started

### Prerequisites

- **Python 3.10+**: Backend development
- **Node.js 18+**: Frontend development
- **PostgreSQL 14+**: Production database (or DuckDB for local)
- **Git**: Version control

### Initial Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd MMS
```

2. **Backend setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend setup**
```bash
cd ../frontend
npm install
```

4. **Environment configuration**
```bash
# Copy example env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit with your configuration
# See Configuration section below
```

5. **Database setup**
```bash
# For local development with DuckDB
cd backend
python scripts/setup_db.py

# Or for PostgreSQL
createdb promo_co_pilot
psql promo_co_pilot < scripts/schema.sql
```

## Project Structure

```
MMS/
├── backend/
│   ├── agents/              # LangChain agents
│   │   ├── discovery_agent.py
│   │   ├── scenario_lab_agent.py
│   │   ├── optimization_agent.py
│   │   ├── creative_agent.py
│   │   ├── postmortem_agent.py
│   │   └── validation_agent.py
│   ├── engines/            # Business logic
│   │   ├── context_engine.py
│   │   ├── forecast_engine.py
│   │   ├── uplift_engine.py
│   │   ├── scenario_evaluation_engine.py
│   │   ├── scenario_optimization_engine.py
│   │   ├── validation_engine.py
│   │   ├── creative_engine.py
│   │   ├── postmortem_engine.py
│   │   └── learning_engine.py
│   ├── tools/              # Data access
│   │   ├── sales_data_tool.py
│   │   ├── promo_catalog_tool.py
│   │   ├── cdp_tool.py
│   │   ├── context_data_tool.py
│   │   ├── weather_tool.py
│   │   └── targets_tool.py
│   ├── models/             # Data models
│   │   ├── schemas.py       # Pydantic models
│   │   └── database.py     # SQLAlchemy models
│   ├── api/                # FastAPI endpoints
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── discovery.py
│   │   │   ├── scenarios.py
│   │   │   ├── optimization.py
│   │   │   ├── creative.py
│   │   │   └── postmortem.py
│   │   └── middleware.py
│   ├── scripts/            # Utility scripts
│   │   ├── setup_db.py
│   │   ├── load_sample_data.py
│   │   └── migrate_data.py
│   ├── tests/               # Tests
│   │   ├── test_agents/
│   │   ├── test_engines/
│   │   └── test_api/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   │   ├── layout/
│   │   │   ├── charts/
│   │   │   ├── forms/
│   │   │   └── common/
│   │   ├── screens/         # Main screens
│   │   │   ├── Discovery/
│   │   │   ├── ScenarioLab/
│   │   │   ├── Optimization/
│   │   │   ├── Creative/
│   │   │   └── PostMortem/
│   │   ├── services/        # API clients
│   │   │   └── api.ts
│   │   ├── hooks/           # Custom hooks
│   │   ├── store/           # State management
│   │   ├── types/           # TypeScript types
│   │   └── utils/           # Utilities
│   ├── public/
│   ├── package.json
│   └── .env.example
│
├── data/                    # Sample data
│   ├── sales_aggregated.csv
│   ├── promo_catalog.csv
│   └── segments.json
│
└── docs/                    # Documentation
```

## Development Workflow

### Running Locally

**Terminal 1: Backend**
```bash
cd backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```

**Terminal 3: Observability (optional)**
```bash
# Start Phoenix server for LLM tracing
phoenix serve
```

### Code Style

**Python**:
- Follow PEP 8
- Use Black for formatting
- Use mypy for type checking
- Maximum line length: 100

```bash
# Format code
black backend/

# Type check
mypy backend/

# Lint
flake8 backend/
```

**TypeScript/React**:
- Use ESLint + Prettier
- Follow React best practices
- Use functional components with hooks

```bash
# Format code
npm run format

# Lint
npm run lint

# Type check
npm run type-check
```

## Testing

### Backend Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=agents --cov=engines --cov=tools --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test

# With coverage
npm test -- --coverage
```

### Integration Tests

```bash
# Run full integration test suite
pytest tests/integration/
```

## Adding New Features

### Adding a New Agent

1. Create agent file in `backend/agents/`
2. Inherit from base agent class
3. Implement required methods
4. Add LangChain tools
5. Create API endpoint
6. Add tests

Example:
```python
# backend/agents/my_agent.py
from langchain.agents import AgentExecutor
from backend.engines.my_engine import MyEngine

class MyAgent:
    def __init__(self, llm, tools):
        self.engine = MyEngine()
        self.agent = AgentExecutor.from_agent_and_tools(
            agent=self._create_agent(llm),
            tools=tools
        )
    
    def process(self, input_data):
        # Agent logic
        result = self.engine.compute(input_data)
        return result
```

### Adding a New Engine

1. Create engine file in `backend/engines/`
2. Implement computation logic
3. Add caching if needed
4. Add tests

Example:
```python
# backend/engines/my_engine.py
from functools import lru_cache

class MyEngine:
    def compute(self, input_data):
        # Engine logic
        result = self._calculate(input_data)
        return result
    
    @lru_cache(maxsize=128)
    def _calculate(self, data):
        # Cached computation
        pass
```

### Adding a New API Endpoint

1. Create route file in `backend/api/routes/`
2. Define endpoint with FastAPI
3. Add request/response models
4. Integrate with agents/engines
5. Add error handling
6. Add tests

Example:
```python
# backend/api/routes/my_endpoint.py
from fastapi import APIRouter, HTTPException
from backend.models.schemas import MyRequest, MyResponse
from backend.agents.my_agent import MyAgent

router = APIRouter(prefix="/api/v1/my-endpoint", tags=["my"])

@router.post("/", response_model=MyResponse)
async def my_endpoint(request: MyRequest):
    try:
        agent = MyAgent()
        result = agent.process(request)
        return MyResponse(data=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Adding a New UI Screen

1. Create screen directory in `frontend/src/screens/`
2. Create main component
3. Add route in router
4. Create child components
5. Add API integration
6. Add tests

Example:
```typescript
// frontend/src/screens/MyScreen/MyScreen.tsx
import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';

export const MyScreen = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['myData'],
    queryFn: () => api.getMyData()
  });

  if (isLoading) return <Loading />;

  return (
    <div>
      {/* Screen content */}
    </div>
  );
};
```

## Database Migrations

### Using Alembic (PostgreSQL)

```bash
# Create migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Using DuckDB (Local)

DuckDB doesn't require migrations. Schema is created on first run.

## Observability

### Phoenix Arize Integration

All LLM calls are automatically traced:

```python
from phoenix.otel import register

# In main.py
register()
```

View traces at: `http://localhost:6006`

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Processing scenario", extra={
    "scenario_id": scenario.id,
    "user_id": user.id
})
```

## Environment Variables

### Backend (.env)

```bash
# API
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional

# Database
DATABASE_URL=postgresql://user:pass@localhost/promo_co_pilot
# Or for DuckDB:
# DATABASE_URL=duckdb:///data/promo.db

# Observability
PHOENIX_API_KEY=...
PHOENIX_ENDPOINT=http://localhost:6006

# External APIs
# Open-Meteo API (free, no key required)
# WEATHER_API_URL=https://api.open-meteo.com/v1/forecast
CDP_API_URL=http://localhost:8080  # Mock for hackathon

# App
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:8000
VITE_PHOENIX_ENDPOINT=http://localhost:6006
```

## Debugging

### Backend

```python
# Use Python debugger
import pdb; pdb.set_trace()

# Or use VS Code debugger
# Create .vscode/launch.json
```

### Frontend

```typescript
// Use React DevTools
// Use browser DevTools
console.log('Debug:', data);

// Use React Query DevTools
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
```

## Performance Optimization

### Backend

- Use caching for expensive computations
- Batch database queries
- Use async/await for I/O operations
- Profile with `cProfile`

```python
import cProfile
profiler = cProfile.Profile()
profiler.enable()
# Your code
profiler.disable()
profiler.dump_stats('profile.stats')
```

### Frontend

- Use React.memo for expensive components
- Lazy load routes
- Optimize bundle size
- Use React Query caching

```typescript
// Lazy load
const MyScreen = lazy(() => import('./screens/MyScreen'));

// Memoize
const ExpensiveComponent = memo(({ data }) => {
  // Component
});
```

## Deployment

### Backend (Production)

```bash
# Build Docker image
docker build -t promo-co-pilot-backend ./backend

# Run with Docker Compose
docker-compose up -d
```

### Frontend (Production)

```bash
# Build
npm run build

# Serve with nginx or similar
# Or deploy to Vercel/Netlify
```

## Troubleshooting

### Common Issues

1. **Import errors**: Check Python path and virtual environment
2. **Database connection**: Verify DATABASE_URL
3. **LLM API errors**: Check API keys and rate limits
4. **CORS errors**: Configure CORS in FastAPI
5. **Port conflicts**: Change ports in .env files

### Getting Help

- Check logs: `backend/logs/` and browser console
- Review Phoenix traces for LLM issues
- Check API documentation
- Review test cases for examples

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes
3. Write tests
4. Run tests and linting
5. Commit: `git commit -m "feat: add my feature"`
6. Push: `git push origin feature/my-feature`
7. Create pull request

### Commit Message Format

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code refactoring
- `docs:` Documentation
- `test:` Tests
- `chore:` Maintenance

