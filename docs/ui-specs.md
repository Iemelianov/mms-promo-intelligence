# UI/UX Specifications

## Design System

### Technology Stack

- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS
- **Components**: [ReactBits.dev](http://reactbits.dev/) components
- **State Management**: React Query + Zustand
- **Forms**: React Hook Form
- **Charts**: Recharts or Chart.js
- **Icons**: Lucide React

### Design Principles

1. **Clarity First**: Complex data presented in digestible formats
2. **Progressive Disclosure**: Show summary, allow drill-down
3. **Contextual Help**: Chat co-pilot available on every screen
4. **Responsive**: Works on desktop and tablet
5. **Accessible**: WCAG 2.1 AA compliance

## Color Palette

```css
/* Primary */
--primary-50: #f0f9ff;
--primary-500: #0ea5e9;
--primary-600: #0284c7;
--primary-700: #0369a1;

/* Success */
--success-500: #10b981;
--success-600: #059669;

/* Warning */
--warning-500: #f59e0b;
--warning-600: #d97706;

/* Error */
--error-500: #ef4444;
--error-600: #dc2626;

/* Neutral */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-500: #6b7280;
--gray-900: #111827;
```

## Component Library

### Layout Components

#### MainLayout

Full-page layout with sidebar and header.

```tsx
<MainLayout>
  <Sidebar />
  <Header />
  <MainContent>{children}</MainContent>
  <ChatWidget />
</MainLayout>
```

#### Sidebar

Navigation sidebar with:
- Logo
- Navigation items (Discovery, Scenario Lab, Optimization, Creative, Post-Mortem)
- User menu

#### Header

Top header with:
- Breadcrumbs
- Search (optional)
- Notifications
- User profile

### Screen Components

## 1. Discovery Screen

**Purpose**: Overview of current situation and opportunities

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Header: "Discovery - October 2024"                      │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│ │ Month        │  │ Geo          │  │ Refresh      │  │
│ │ Selector     │  │ Selector     │  │ Button       │  │
│ └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ Gap vs Target Chart                                │ │
│ │ [Line chart: Actual vs Target by day]             │ │
│ └────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│ │ Department   │  │ Context      │  │ Opportunities│  │
│ │ Heatmap      │  │ Widget       │  │ List         │  │
│ │              │  │              │  │              │  │
│ │ [Heatmap]    │  │ Weather:     │  │ • Opp 1      │  │
│ │              │  │ Rainy        │  │ • Opp 2      │  │
│ │              │  │              │  │ • Opp 3      │  │
│ │              │  │ Events:      │  │              │  │
│ │              │  │ None         │  │              │  │
│ └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
│ Chat Widget (floating, right side)                      │
└─────────────────────────────────────────────────────────┘
```

### Components

#### GapVsTargetChart

Line chart showing:
- Actual sales (line)
- Target sales (line)
- Gap area (shaded)

**Props**:
```typescript
interface GapVsTargetChartProps {
  data: {
    date: string;
    actual: number;
    target: number;
  }[];
  month: string;
}
```

#### DepartmentHeatmap

Heatmap showing gap by department.

**Props**:
```typescript
interface DepartmentHeatmapProps {
  data: {
    department: string;
    gap_pct: number;
    sales_value: number;
  }[];
}
```

#### ContextWidget

Shows weather, events, seasonality.

**Props**:
```typescript
interface ContextWidgetProps {
  context: PromoContext;
}
```

#### OpportunitiesList

List of identified opportunities.

**Props**:
```typescript
interface OpportunitiesListProps {
  opportunities: PromoOpportunity[];
  onSelect: (opp: PromoOpportunity) => void;
}
```

## 2. Scenario Lab Screen

**Purpose**: Create, edit, and compare scenarios

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Header: "Scenario Lab"                                  │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐  ┌────────────────────────────────┐ │
│ │ Scenario        │  │ Scenario Comparison Table    │ │
│ │ Configuration   │  │                               │ │
│ │                 │  │ [Table with KPIs]            │ │
│ │ [Form/Table]    │  │                               │ │
│ │                 │  │ A | B | C                    │ │
│ │ • Dates         │  │ Sales: ...                    │ │
│ │ • Departments   │  │ Margin: ...                   │ │
│ │ • Discounts     │  │ EBIT: ...                     │ │
│ │ • Segments      │  │                               │ │
│ │                 │  │ [Validation indicators]       │ │
│ │ [Add Scenario]  │  │                               │ │
│ └──────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ Selected Scenario Details                          │ │
│ │ ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │
│ │ │ KPI      │  │ Channel │  │ Segment │           │ │
│ │ │ Breakdown│  │ Split   │  │ Impact  │           │ │
│ │ │          │  │         │  │          │           │ │
│ │ │ [Charts] │  │ [Chart] │  │ [Table] │           │ │
│ │ └──────────┘  └──────────┘  └──────────┘           │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Components

#### ScenarioConfigForm

Form for configuring scenario parameters.

**Props**:
```typescript
interface ScenarioConfigFormProps {
  scenario?: PromoScenario;
  brief: PromoBrief;
  onSubmit: (scenario: PromoScenario) => void;
  onCancel: () => void;
}
```

**Fields**:
- Date range picker
- Department multi-select
- Discount sliders (by department)
- Channel checkboxes
- Segment selection

#### ScenarioComparisonTable

Table comparing multiple scenarios.

**Props**:
```typescript
interface ScenarioComparisonTableProps {
  scenarios: {
    scenario: PromoScenario;
    kpi: ScenarioKPI;
    validation: ValidationReport;
  }[];
  onSelect: (scenarioId: string) => void;
  selectedId?: string;
}
```

**Columns**:
- Scenario name
- Sales value
- Margin %
- EBIT
- Units
- Validation status (icon)
- Actions (Edit, Delete, Generate Creative)

#### KPIBreakdown

Detailed KPI breakdown for selected scenario.

**Props**:
```typescript
interface KPIBreakdownProps {
  kpi: ScenarioKPI;
  baseline: BaselineForecast;
}
```

**Tabs**:
- Overview (total KPIs)
- By Channel (online/offline split)
- By Department
- By Segment
- Validation Issues

#### ValidationIndicator

Visual indicator for validation status.

**Props**:
```typescript
interface ValidationIndicatorProps {
  status: "PASS" | "WARN" | "BLOCK";
  issues?: ValidationIssue[];
}
```

**Visual**:
- Green checkmark (PASS)
- Yellow warning icon (WARN)
- Red X (BLOCK)
- Tooltip with issue details

## 3. Optimization Screen

**Purpose**: Find optimal scenarios

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Header: "Optimization"                                   │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐  ┌────────────────────────────────┐ │
│ │ Objectives &     │  │ Efficient Frontier Chart      │ │
│ │ Constraints      │  │                               │ │
│ │                  │  │ [Scatter plot: Sales vs Margin]│ │
│ │ Maximize:        │  │                               │ │
│ │ [Sales/Margin/  │  │ • Scenario A                  │ │
│ │  EBIT]          │  │ • Scenario B                  │ │
│ │                  │  │ • Scenario C                  │ │
│ │ Constraints:     │  │                               │ │
│ │ Min Margin: [%] │  │ [Pareto frontier line]        │ │
│ │ Max Discount: [%]│  │                               │ │
│ │                  │  │                               │ │
│ │ [Generate]       │  │                               │ │
│ └──────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ Recommended Scenarios                               │ │
│ │ [Scenario cards with KPIs and recommendations]     │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Components

#### ObjectivesForm

Form for setting optimization objectives.

**Props**:
```typescript
interface ObjectivesFormProps {
  brief: PromoBrief;
  onSubmit: (objectives: OptimizationObjectives) => void;
}
```

#### EfficientFrontierChart

Scatter plot showing trade-offs.

**Props**:
```typescript
interface EfficientFrontierChartProps {
  scenarios: {
    id: string;
    label: string;
    sales: number;
    margin: number;
    ebit: number;
  }[];
  xAxis: "sales" | "margin" | "ebit";
  yAxis: "sales" | "margin" | "ebit";
  onPointClick: (scenarioId: string) => void;
}
```

#### RecommendedScenarios

List of ranked scenarios with recommendations.

**Props**:
```typescript
interface RecommendedScenariosProps {
  scenarios: {
    scenario: PromoScenario;
    kpi: ScenarioKPI;
    rank: number;
    score: number;
    recommendation: string;
  }[];
  onSelect: (scenarioId: string) => void;
}
```

## 4. Creative Companion Screen

**Purpose**: Generate and view creative briefs

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Header: "Creative Companion"                            │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────────┐  ┌────────────────────────────────┐ │
│ │ Selected        │  │ Creative Brief                 │ │
│ │ Scenarios       │  │                               │ │
│ │                 │  │ Objectives: ...                │ │
│ │ [Checkboxes]    │  │ Target: ...                    │ │
│ │ • Scenario A ✓  │  │ Messages: ...                 │ │
│ │ • Scenario B    │  │ Tone: ...                      │ │
│ │                 │  │                               │ │
│ │ Asset Types:    │  │ [Full brief text]             │ │
│ │ [Multi-select]  │  │                               │ │
│ │                 │  │                               │ │
│ │ [Generate]      │  │                               │ │
│ └──────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ Generated Assets                                   │ │
│ │ ┌──────────┐  ┌──────────┐  ┌──────────┐         │ │
│ │ │ Homepage │  │ Category │  │ In-Store │         │ │
│ │ │ Hero     │  │ Banner   │  │ Sheet    │         │ │
│ │ │          │  │          │  │          │         │ │
│ │ │ Headline │  │ Headline │  │ Headline │         │ │
│ │ │ Subhead  │  │ Subhead  │  │ Subhead  │         │ │
│ │ │ CTA      │  │ CTA      │  │ CTA      │         │ │
│ │ │          │  │          │  │          │         │ │
│ │ │ [Copy]   │  │ [Copy]   │  │ [Copy]   │         │ │
│ │ └──────────┘  └──────────┘  └──────────┘         │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Components

#### CreativeBriefView

Displays the full creative brief.

**Props**:
```typescript
interface CreativeBriefViewProps {
  brief: CreativeBrief;
  onExport: () => void;
}
```

#### AssetCard

Card for individual creative asset.

**Props**:
```typescript
interface AssetCardProps {
  asset: AssetSpec;
  onCopy: () => void;
  onEdit: () => void;
}
```

**Features**:
- Copy to clipboard
- Edit (opens modal)
- Export as PDF/Word

## 5. Post-Mortem Screen

**Purpose**: Analyze completed campaigns

### Layout

```
┌─────────────────────────────────────────────────────────┐
│ Header: "Post-Mortem Analysis"                         │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ Forecast vs Actual Chart                           │ │
│ │ [Line chart: Forecast vs Actual over time]        │ │
│ └────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│ │ Accuracy     │  │ Post-Promo   │  │ Insights     │  │
│ │ Metrics      │  │ Dip Analysis │  │ & Learning   │  │
│ │              │  │              │  │              │  │
│ │ Sales: -3.1% │  │ [Chart]      │  │ • Uplift     │  │
│ │ Margin: -2.8%│  │              │  │   over-      │  │
│ │ EBIT: -4.4%  │  │              │  │   estimated  │  │
│ │              │  │              │  │ • Gaming     │  │
│ │              │  │              │  │   performed  │  │
│ │              │  │              │  │   well       │  │
│ └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ Learning Memo                                       │ │
│ │ [Text report with recommendations]                  │ │
│ └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Components

#### ForecastVsActualChart

Comparison chart.

**Props**:
```typescript
interface ForecastVsActualChartProps {
  forecast: ScenarioKPI;
  actual: {
    total: {
      sales_value: number;
      margin_value: number;
      ...
    };
  };
  period: {
    start: string;
    end: string;
  };
}
```

#### AccuracyMetrics

Shows forecast accuracy.

**Props**:
```typescript
interface AccuracyMetricsProps {
  vs_forecast: {
    sales_value_error_pct: number;
    margin_value_error_pct: number;
    ebit_error_pct: number;
  };
}
```

#### LearningMemo

Text report with insights.

**Props**:
```typescript
interface LearningMemoProps {
  report: PostMortemReport;
}
```

## Chat Widget (Co-Pilot)

Floating chat widget available on all screens.

### Features

- Context-aware responses
- What-if analysis
- Explanations of calculations
- Suggestions for improvements

### Component

```tsx
<ChatWidget
  context={{
    screen: "scenario_lab",
    activeScenarios: ["scenario_A", "scenario_B"],
    userTask: "comparing_scenarios"
  }}
  onMessage={(message) => {
    // Send to API
  }}
/>
```

## Responsive Design

### Breakpoints

- **Mobile**: < 640px (not primary, but functional)
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px (primary)

### Adaptations

- Sidebar collapses to icon-only on tablet
- Tables become cards on mobile
- Charts adjust to available width
- Chat widget becomes bottom sheet on mobile

## Accessibility

- Keyboard navigation for all interactive elements
- ARIA labels for charts and complex components
- Focus indicators
- Screen reader support
- Color contrast compliance (WCAG AA)

## Performance Targets

- Initial load: < 2s
- Screen transitions: < 300ms
- Chart rendering: < 500ms
- API responses: < 1s (p95)

## Component Examples from ReactBits.dev

Use modern components from ReactBits.dev for:
- Cards
- Tables
- Forms
- Buttons
- Modals
- Charts wrappers
- Loading states



