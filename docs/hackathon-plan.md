# Hackathon Build Plan

## Timeline: 14 Hours

### Phase 1: Setup & Data Preparation (2 hours)

**Tasks**:
- [ ] Project structure setup
- [ ] Environment configuration
- [ ] Convert XLSB to CSV
- [ ] Load sample data
- [ ] Basic API endpoints

**Deliverables**:
- Working backend with sample data
- Basic frontend structure
- Database with historical sales

### Phase 2: Core Engines (3 hours)

**Tasks**:
- [ ] Context Engine (weather, events)
- [ ] Forecast & Baseline Engine
- [ ] Uplift Engine (simplified rules)
- [ ] Scenario Evaluation Engine

**Deliverables**:
- Engines can compute baseline and uplift
- Basic scenario KPI calculation works

### Phase 3: Agents (3 hours)

**Tasks**:
- [ ] Discovery Agent (basic)
- [ ] Scenario Lab Agent
- [ ] Optimization Agent (template-based)
- [ ] Chat Co-Pilot (basic)

**Deliverables**:
- Can create scenarios from brief
- Can compare scenarios
- Chat interface functional

### Phase 4: UI Screens (4 hours)

**Tasks**:
- [ ] Discovery screen
- [ ] Scenario Lab screen
- [ ] Optimization screen (basic)
- [ ] Creative Companion screen (basic)

**Deliverables**:
- All main screens render
- Can create and view scenarios
- Charts display data

### Phase 5: Integration & Polish (2 hours)

**Tasks**:
- [ ] Connect all components
- [ ] Fix bugs
- [ ] Add error handling
- [ ] Improve UI/UX
- [ ] Prepare demo script

**Deliverables**:
- End-to-end flow works
- Demo-ready application

## MVP Scope

### Must Have

1. **Data Loading**
   - Load CSV sales data
   - Mock CDP segments
   - Basic promo catalog

2. **Baseline Forecast**
   - Simple day-of-week average
   - Gap calculation vs target

3. **Scenario Generation**
   - 3 template scenarios (Conservative/Balanced/Aggressive)
   - KPI calculation
   - Basic validation

4. **UI**
   - Discovery screen with gap chart
   - Scenario Lab with comparison table
   - Creative Companion with brief

5. **Chat**
   - Basic Q&A
   - Scenario explanations

### Nice to Have

- Weather integration
- Advanced optimization
- Post-mortem analysis
- Segment-specific scenarios
- Advanced creative generation

## Demo Script

### Step 1: Discovery (2 min)

1. Open app on Oct 20, 2024
2. Show gap vs target chart
3. Show identified opportunities
4. Explain context (weather, events)

### Step 2: Scenario Creation (3 min)

1. User describes problem in chat:
   "We're -3M vs target, need promo 22-27 Oct for TVs & Gaming"
2. System generates 3 scenarios
3. Show comparison table
4. Explain KPIs

### Step 3: Optimization (2 min)

1. Show efficient frontier chart
2. Explain trade-offs
3. Select "Balanced" scenario
4. Adjust parameters (e.g., max discount)

### Step 4: Creative Generation (2 min)

1. Click "Generate Creative Pack"
2. Show creative brief
3. Show sample assets (homepage hero, category banner)
4. Explain how it helps marketing

### Step 5: Summary (1 min)

- Show full journey
- Highlight key benefits
- Mention future enhancements

## Technical Decisions for Hackathon

### Simplifications

1. **Uplift Model**: Use simple rules instead of ML
   - TVs -20% → +X% lift (from historical average)
   - Gaming -15% → +Y% lift

2. **Baseline**: Day-of-week average, no complex seasonality

3. **Optimization**: Template-based, not true optimization

4. **CDP**: Mock data, not real API

5. **Weather**: Open-Meteo API (free, no API key required) - fully integrated

### Data Requirements

- Minimum 3-6 months of sales data
- At least 10-20 promo examples
- 3-4 departments (TV, Gaming, Audio, Accessories)
- Online and offline channels

## Risk Mitigation

### High Risk Items

1. **LLM API Rate Limits**
   - Solution: Cache responses, use cheaper models for simple tasks

2. **Data Quality**
   - Solution: Pre-process and validate data before hackathon

3. **Integration Issues**
   - Solution: Test integrations early, have fallbacks

4. **Time Constraints**
   - Solution: Prioritize core flow, simplify non-essential features

## Success Criteria

- [ ] Can create scenario from natural language
- [ ] Can compare 3 scenarios with KPIs
- [ ] Can generate creative brief
- [ ] Chat co-pilot answers basic questions
- [ ] Demo runs smoothly end-to-end

## Post-Hackathon Enhancements

- Real ML models for uplift
- Advanced optimization algorithms
- Real CDP integration
- Image generation for creatives
- Post-mortem analytics
- Multi-tenant support

