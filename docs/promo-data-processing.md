# Promo Data Processing Guide

## Overview

The system processes promotional catalog data from XLSB files (e.g., `Promo_October-September_FY25.xlsb`) to extract promotional campaign information for use in uplift modeling and scenario planning.

## File Structure

Promo XLSB files typically contain:
- Date information
- Department/category data
- Channel information (online/offline)
- Discount percentages
- Sales data during promotional periods

## Processing Workflow

### 1. File Reading

The `XLSBReaderTool` reads the XLSB file:

```python
from tools import XLSBReaderTool

reader = XLSBReaderTool()
df = reader.read_file("Data/Promo_October-September_FY25.xlsb")
```

### 2. Data Cleaning

Standardize formats and clean data:

```python
from tools import DataCleaningTool

cleaner = DataCleaningTool()
df_clean = cleaner.clean_dataframe(df)
```

### 3. Campaign Extraction

Extract promotional campaigns from the data:

```python
from tools import PromoCatalogTool

promo_tool = PromoCatalogTool()
campaigns = promo_tool.process_promo_dataframe(df_clean)
```

The tool identifies campaigns by:
- **Promo Name**: If a `promo_name` or `campaign` column exists
- **Date Ranges**: Consecutive days with discounts are grouped as campaigns

### 4. Quality Validation

Validate data quality:

```python
from tools import DataValidationTool

validator = DataValidationTool()
quality_report = validator.validate_data_quality(df_clean)
```

### 5. Database Storage

Load processed data to database:

```python
from tools import DatabaseLoaderTool

loader = DatabaseLoaderTool(database_url)
loader.load_dataframe(df_clean, table_name='promo_catalog')
```

## Using PromoProcessor

The `PromoProcessor` class provides a complete workflow:

```python
from tools import PromoProcessor

processor = PromoProcessor(database_url="duckdb:///data/promo.db")

result = processor.process_promo_file(
    file_path="Data/Promo_October-September_FY25.xlsb",
    load_to_db=True
)

print(f"Campaigns extracted: {result['campaigns_extracted']}")
print(f"Records processed: {result['records_processed']}")
```

## Campaign Data Structure

Each extracted campaign contains:

```python
{
    "id": "promo_period_1_2024-10-01",
    "promo_name": "Promo Period 1",
    "date_start": "2024-10-01",
    "date_end": "2024-10-07",
    "departments": ["TV", "Gaming"],
    "channels": ["online", "offline"],
    "avg_discount_pct": 20.5,
    "mechanics": {}
}
```

## Integration with Uplift Engine

The extracted campaigns are used by the Uplift & Elasticity Engine to:

1. **Calculate Historical Uplift**: Compare sales during promo vs non-promo periods
2. **Build Uplift Model**: Create coefficients by department/channel/discount band
3. **Validate Scenarios**: Check if proposed scenarios match historical patterns

## Example: Complete Processing

```python
from pathlib import Path
from tools import PromoProcessor

# Initialize processor
data_dir = Path("Data")
database_url = "duckdb:///data/promo.db"
processor = PromoProcessor(database_url)

# Process promo file
promo_file = data_dir / "Promo_October-September_FY25.xlsb"
result = processor.process_promo_file(str(promo_file), load_to_db=True)

# Access extracted campaigns
campaigns = result['campaigns']
for campaign in campaigns[:5]:  # Show first 5
    print(f"{campaign['promo_name']}: {campaign['date_start']} to {campaign['date_end']}")
    print(f"  Departments: {', '.join(campaign['departments'])}")
    print(f"  Avg Discount: {campaign['avg_discount_pct']:.1f}%")
```

## Troubleshooting

### Issue: No campaigns extracted

**Possible causes**:
- File structure doesn't match expected format
- No discount data found
- Date column missing or invalid

**Solution**: Inspect the file structure first:
```python
from tools import XLSBReaderTool

reader = XLSBReaderTool()
metadata = reader.inspect_file("Data/Promo_October-September_FY25.xlsb")
print(f"Columns: {metadata['columns']}")
```

### Issue: Quality validation fails

**Check**:
- Missing required columns (date, channel, department)
- Invalid date formats
- Negative or unrealistic discount values

**Solution**: Review quality report:
```python
quality_report = result['quality_report']
for issue in quality_report['issues']:
    print(f"{issue['severity']}: {issue['message']}")
```

## Best Practices

1. **Process promo files separately** from sales data files
2. **Validate quality** before using in uplift calculations
3. **Cache campaigns** for performance
4. **Store source file path** for traceability
5. **Handle date range overlaps** when processing multiple files

## Next Steps

After processing promo data:
1. Use `PromoCatalogTool.get_past_promos()` to query campaigns
2. Feed to Uplift Engine for model building
3. Use in scenario validation
4. Reference in post-mortem analysis

