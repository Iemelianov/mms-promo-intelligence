# Product Requirements Document (PRD)
## Promo Scenario Co-Pilot

**Version**: 1.0  
**Date**: 2024-10-20  
**Status**: In Development

---

## 1. Executive Summary

### 1.1 Product Vision

Promo Scenario Co-Pilot is an AI-powered system that transforms promotional campaign planning from an ad-hoc, spreadsheet-driven process into a data-driven, intelligent workflow. It enables promotional leads to quickly identify opportunities, model multiple scenarios, optimize for business impact, and generate creative assets—all within a unified interface.

### 1.2 Problem Statement

**Current State**:
- Promotional leads manually test only a few scenarios due to time constraints
- External factors (weather, events) are underutilized
- Impact on sales, margin, and EBIT is uncertain
- Creative asset generation is time-consuming and inconsistent
- No systematic learning from past campaigns

**Pain Points**:
1. **Speed**: Takes days to manually model scenarios
2. **Quality**: Limited scenario exploration leads to suboptimal decisions
3. **Consistency**: Ad-hoc spreadsheets lack standardization
4. **Context**: External factors not systematically considered
5. **Execution**: Creative briefs created from scratch each time

### 1.3 Solution Overview

An AI-powered co-pilot that:
1. **Discovers** opportunities through automated data analysis
2. **Models** multiple scenarios with automated KPI calculation
3. **Optimizes** scenarios for maximum business impact
4. **Generates** creative briefs and asset specifications
5. **Learns** from post-campaign performance to improve accuracy

---

## 2. Target Users

### 2.1 Primary User: Promotional Lead

**Profile**:
- Role: Marketing/Promotions Manager
- Experience: 3-10 years in retail/promotions
- Technical Level: Intermediate (comfortable with data, not coding)
- Goals: Close gaps vs targets, maximize promotional ROI

**Needs**:
- Quick scenario modeling
- Data-backed recommendations
- Clear KPI visualization
- Creative asset support

### 2.2 Secondary Users

- **Marketing Director**: Strategic oversight, approval
- **Finance Manager**: Margin and EBIT validation
- **Creative Team**: Asset generation support

---

## 3. User Stories

### 3.1 Discovery

**As a** promotional lead  
**I want to** see my current gap vs target and identified opportunities  
**So that** I can quickly understand what needs to be addressed

**Acceptance Criteria**:
- Display gap vs target chart for selected month
- Show identified opportunities with estimated potential
- Include contextual factors (weather, events)
- Allow filtering by department/channel

### 3.2 Scenario Modeling

**As a** promotional lead  
**I want to** create and compare multiple promotional scenarios  
**So that** I can choose the best approach

**Acceptance Criteria**:
- Create scenario from brief or manual input
- Compare 2-3 scenarios side-by-side
- See KPIs (sales, margin, EBIT, units) for each
- View breakdown by channel, department, segment
- Get validation feedback

### 3.3 Optimization

**As a** promotional lead  
**I want to** find optimal scenarios that balance sales and margin  
**So that** I can maximize business impact

**Acceptance Criteria**:
- Generate optimized scenarios based on objectives
- See efficient frontier (trade-offs)
- Rank scenarios by business impact
- Get recommendations with rationale

### 3.4 Creative Generation

**As a** promotional lead  
**I want to** generate creative briefs and asset copy from scenarios  
**So that** I can quickly brief the creative team

**Acceptance Criteria**:
- Generate structured creative brief
- Create copy for key assets (homepage hero, banners, in-store)
- Adapt messaging for different segments
- Export brief and assets

### 3.5 Data Processing

**As a** system administrator  
**I want to** process XLSB files and load them into the database  
**So that** the system has up-to-date data for analysis

**Acceptance Criteria**:
- Upload/process multiple XLSB files
- Merge files by date ranges
- Clean and validate data
- Generate data quality report
- Store in database for other agents

---

## 4. Functional Requirements

### 4.1 Data Processing Module

**FR-1.1**: System must process XLSB files (Web and Stores data)

**FR-1.2**: System must clean and standardize data formats:
- Dates in ISO format (YYYY-MM-DD)
- Channels: "online" or "offline"
- Departments: standardized list
- Numeric values: non-negative, proper types

**FR-1.3**: System must merge multiple files handling:
- Date range overlaps
- Duplicate records
- Missing values

**FR-1.4**: System must validate data quality:
- Completeness checks
- Accuracy validation
- Consistency checks
- Timeliness verification

**FR-1.5**: System must store processed data in database:
- Daily aggregation by channel and department
- Promo flag identification
- Indexing for fast queries

### 4.2 Discovery Module

**FR-2.1**: System must calculate baseline forecasts:
- Day-of-week patterns
- Seasonal adjustments
- Trend analysis

**FR-2.2**: System must identify gaps vs targets:
- Sales value gap
- Margin percentage gap
- Units gap

**FR-2.3**: System must gather contextual data:
- Weather forecasts
- Events and holidays
- Seasonality factors

**FR-2.4**: System must generate opportunities:
- Identify high-potential departments
- Estimate promotional potential
- Rank by priority

### 4.3 Scenario Lab Module

**FR-3.1**: System must create scenarios from:
- Natural language briefs
- Manual parameter input
- Template-based generation

**FR-3.2**: System must calculate scenario KPIs:
- Total sales, margin, EBIT, units
- Breakdown by channel
- Breakdown by department
- Breakdown by segment

**FR-3.3**: System must compare scenarios:
- Side-by-side KPI comparison
- Visual charts
- Trade-off analysis

**FR-3.4**: System must validate scenarios:
- Discount limits
- Margin thresholds
- KPI plausibility
- Brand compliance

### 4.4 Optimization Module

**FR-4.1**: System must generate optimized scenarios:
- Based on objectives (maximize sales/margin/EBIT)
- Respecting constraints
- Multiple candidate scenarios

**FR-4.2**: System must calculate efficient frontier:
- Trade-offs between objectives
- Pareto-optimal solutions
- Visualization

**FR-4.3**: System must rank scenarios:
- By weighted objective function
- With recommendations
- Including rationale

### 4.5 Creative Module

**FR-5.1**: System must generate creative briefs:
- Objectives and messaging
- Target audience
- Tone and style
- Mandatory elements

**FR-5.2**: System must generate asset copy:
- Homepage hero
- Category banners
- In-store sheets
- Email headers

**FR-5.3**: System must adapt messaging:
- By customer segment
- By channel (online/offline)
- By department focus

### 4.6 Post-Mortem Module

**FR-6.1**: System must analyze actual vs forecast:
- Calculate error percentages
- Identify root causes
- Generate insights

**FR-6.2**: System must detect effects:
- Post-promo dip
- Cannibalization
- Halo effects

**FR-6.3**: System must update models:
- Adjust uplift coefficients
- Improve forecast accuracy
- Learn from patterns

### 4.7 Chat Co-Pilot

**FR-7.1**: System must provide conversational interface:
- Answer "why" questions
- Explain calculations
- Provide what-if analysis

**FR-7.2**: System must be context-aware:
- Know current screen
- Understand active scenarios
- Access relevant data

---

## 5. Non-Functional Requirements

### 5.1 Performance

**NFR-1.1**: Scenario creation: < 5 seconds  
**NFR-1.2**: KPI calculation: < 3 seconds  
**NFR-1.3**: Data processing: < 5 minutes for 1M records  
**NFR-1.4**: Page load: < 2 seconds  
**NFR-1.5**: API response time (p95): < 1 second

### 5.2 Scalability

**NFR-2.1**: Support 100 concurrent users  
**NFR-2.2**: Handle 10M+ sales records  
**NFR-2.3**: Process 10+ XLSB files simultaneously

### 5.3 Reliability

**NFR-3.1**: System uptime: 99.5%  
**NFR-3.2**: Data processing success rate: > 99%  
**NFR-3.3**: Error recovery: automatic retry for transient failures

### 5.4 Security

**NFR-4.1**: Authentication required for all endpoints  
**NFR-4.2**: API keys with expiration  
**NFR-4.3**: Data encryption at rest and in transit  
**NFR-4.4**: Audit trail for all decisions

### 5.5 Usability

**NFR-5.1**: Intuitive UI requiring minimal training  
**NFR-5.2**: Responsive design (desktop and tablet)  
**NFR-5.3**: Accessibility: WCAG 2.1 AA compliance  
**NFR-5.4**: Help documentation available in-app

### 5.6 Observability

**NFR-6.1**: All LLM calls traced via Phoenix  
**NFR-6.2**: Performance metrics tracked  
**NFR-6.3**: Error logging and alerting

---

## 6. Technical Constraints

### 6.1 Technology Stack

- **Backend**: Python 3.10+, LangChain, FastAPI
- **Frontend**: React 18+, TypeScript, Tailwind CSS
- **Database**: PostgreSQL (production), DuckDB (local)
- **Observability**: Phoenix Arize
- **UI Components**: ReactBits.dev

### 6.2 Data Sources

- XLSB files (Web and Stores sales data)
- Weather API: Open-Meteo (free, no API key required)
- CDP (mock for hackathon, real API for production)
- Targets and configuration (internal)

### 6.3 Integration Requirements

- Must integrate with existing data warehouse
- Must support export to Excel/CSV
- Must support webhook notifications

---

## 7. Success Metrics

### 7.1 User Adoption

- **Target**: 80% of promotional leads use system within 3 months
- **Measure**: Monthly active users (MAU)

### 7.2 Time Savings

- **Target**: 70% reduction in scenario modeling time
- **Measure**: Average time to create scenario (before: 4 hours, after: 1 hour)

### 7.3 Decision Quality

- **Target**: 20% improvement in promotional ROI
- **Measure**: Actual vs forecast accuracy, margin impact

### 7.4 User Satisfaction

- **Target**: NPS > 50
- **Measure**: Quarterly user surveys

---

## 8. MVP Scope

### 8.1 Included

- Data processing (XLSB → database)
- Baseline forecast calculation
- Scenario creation and comparison (3 scenarios)
- KPI calculation and validation
- Creative brief generation
- Chat co-pilot (basic)
- Discovery screen
- Scenario Lab screen

### 8.2 Excluded (Future)

- Advanced ML models for uplift
- Real-time optimization
- Image generation for creatives
- Multi-tenant support
- Advanced post-mortem analytics
- Mobile app

---

## 9. User Flows

### 9.1 Primary Flow: Create and Compare Scenarios

1. User opens Discovery screen
2. System shows gap vs target for October
3. User describes problem in chat: "We're -3M vs target, need promo 22-27 Oct for TVs & Gaming"
4. System generates 3 scenarios (Conservative, Balanced, Aggressive)
5. User views comparison table with KPIs
6. User selects "Balanced" scenario
7. User adjusts parameters (max discount = 20%)
8. System recalculates KPIs
9. User clicks "Generate Creative Pack"
10. System generates brief and asset copy
11. User exports and shares with creative team

### 9.2 Data Processing Flow

1. Admin uploads XLSB files
2. System queues processing job
3. Data Analyst Agent processes files:
   - Reads XLSB files
   - Cleans and standardizes
   - Merges by date ranges
   - Validates quality
4. System stores in database
5. System generates quality report
6. Other agents can now access data

---

## 10. Risk Assessment

### 10.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| LLM API rate limits | High | Medium | Cache responses, use cheaper models |
| Data quality issues | High | Medium | Robust validation, error handling |
| Performance with large datasets | Medium | Low | Optimize queries, use indexes |
| Integration complexity | Medium | Medium | Phased integration, fallbacks |

### 10.2 Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|------------|------------|
| Low user adoption | High | Low | Training, support, clear value prop |
| Forecast inaccuracy | High | Medium | Continuous learning, model updates |
| Data privacy concerns | Medium | Low | Compliance, encryption, access control |

---

## 11. Timeline

### Phase 1: MVP (Hackathon - 14 hours)
- Core data processing
- Basic scenario modeling
- Simple UI screens
- Chat co-pilot

### Phase 2: Beta (4 weeks)
- Full feature set
- Production data integration
- User testing and feedback
- Performance optimization

### Phase 3: Production (8 weeks)
- Production deployment
- User training
- Monitoring and support
- Iterative improvements

---

## 12. Dependencies

### 12.1 External

- LLM API access (OpenAI/Anthropic)
- Weather API
- CDP API (for production)
- Data warehouse access

### 12.2 Internal

- Historical sales data (XLSB files)
- Targets and configuration
- Brand guidelines
- User access management

---

## 13. Open Questions

1. Should we support multi-currency?
2. How to handle regional variations?
3. Integration with existing promo planning tools?
4. Real-time data updates or batch processing?
5. Approval workflow for scenarios?

---

## 14. Appendix

### 14.1 Glossary

- **Baseline**: Forecast without promotions
- **Uplift**: Increase in sales due to promotion
- **Scenario**: A specific promotional campaign configuration
- **KPI**: Key Performance Indicator (sales, margin, EBIT, units)
- **Post-Mortem**: Analysis after campaign completion

### 14.2 References

- Architecture Documentation
- API Specification
- Database Schema
- System Prompts

---

**Document Owner**: Product Team  
**Last Updated**: 2024-10-20  
**Next Review**: 2024-11-20

