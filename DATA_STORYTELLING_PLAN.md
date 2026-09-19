# Wildfire, PM2.5, and Mental Health in Thailand

## Project Goal

This project explores whether wildfire activity is connected with air pollution and mental health outcomes across Thai provinces over time.

The final output can become an interactive Tableau or Power BI dashboard showing:

- where wildfire activity is highest
- how PM2.5 changes across provinces and years
- which health regions have higher mental health case rates
- whether wildfire, PM2.5, and health indicators appear to move together

## Data Files

| File | Main Use |
| --- | --- |
| `Fire_area_prep_province.xlsx` | Annual wildfire events and burned area by province |
| `PM25_YEARLY.csv` | Annual PM2.5 values by province |
| `Psychi_cases.xlsx` | Mental health case counts by province and year |
| `health_region.xlsx` | Province, health region, English province name, population |
| `province_area.xlsx` | Province area by year |
| `wildfire_causes.xlsx` | Wildfire causes by year |
| `Dataset_description.xlsx` | Data dictionary |

## Core Data Story

### 1. Wildfire Pressure

Start by showing how wildfire activity changes over time.

Key questions:

- Which years had the largest burned area?
- Which provinces had the most wildfire events?
- Are wildfire impacts concentrated in northern Thailand?

Suggested visuals:

- line chart: total wildfire area by year
- bar chart: top 10 provinces by wildfire area
- map: wildfire area by province
- heatmap: province by year, colored by burned area

### 2. Air Pollution Exposure

Connect wildfire activity to PM2.5 exposure.

Key questions:

- Which provinces have the highest average PM2.5?
- Do high-wildfire provinces also show high PM2.5?
- Which years show the strongest PM2.5 spikes?

Suggested visuals:

- line chart: PM2.5 by year
- map: PM2.5 by province
- scatter plot: wildfire area vs PM2.5
- filter: province or health region

### 3. Population and Health Context

Add population and health region context so comparisons are fair.

Key questions:

- Which health regions are most exposed?
- How many people live in high-wildfire or high-PM2.5 provinces?
- Are raw health case counts driven mainly by population size?

Suggested visuals:

- bar chart: population by health region
- map: population-adjusted wildfire events
- KPI cards: total population, total wildfire events, average PM2.5

### 4. Mental Health Patterns

Analyze mental health indicators as rates, not only raw counts.

Recommended calculated fields:

```text
case_rate_per_100k = cases / population * 100000
wildfire_events_per_100k = number_of_wildfire / population * 100000
wildfire_area_sqkm = total_area * 0.0016
wildfire_area_percent = wildfire_area_sqkm / province_area_sqkm * 100
```

Key questions:

- Which mental health indicators changed most over time?
- Which provinces or health regions have high case rates?
- Do high PM2.5 or high wildfire years align with changes in case rates?

Suggested visuals:

- line chart: selected mental health rate by year
- map: depression or anxiety rate by province
- scatter plot: PM2.5 vs selected mental health rate
- small multiples: health indicators by year

### 5. Wildfire Causes

Use wildfire causes as a supporting story.

Key questions:

- What are the leading wildfire causes?
- Did causes change from 2015 to 2023?
- Are some causes increasing or decreasing?

Suggested visuals:

- stacked bar chart: wildfire cause area by year
- ranked bar chart: total area by cause
- line chart: selected causes over time

## Recommended Cleaned Tables

### Main Province-Year Table

Create one cleaned table for most dashboards:

```text
province
province_en
year
health_region
population
province_area_sqkm
number_of_wildfire
wildfire_area_rai
wildfire_area_sqkm
wildfire_area_percent
pm25_avg
pm25_total_count
dementia
alcoholism
amphetamine
addict_substance
schizophrenia
bipolar
depression
anxiety
suicide
other_disease
```

### Wildfire Causes Table

Create a separate long-format table:

```text
year
cause
area_rai
```

## Data Cleaning Checklist

- Convert Buddhist years to Gregorian years where needed: `year - 543`
- Standardize province names across Thai and English sources
- Remove `CHANGWAT` prefix from PM2.5 province names
- Convert numeric text with commas into numbers
- Keep only valid province-year rows
- Check duplicate province-year records
- Use rates per 100,000 population for health comparisons
- Keep raw counts and calculated rates in the final dataset

## Best Time Range for Analysis

Use these ranges depending on the question:

| Analysis | Best Year Range |
| --- | --- |
| Wildfire + health | 2015-2023 |
| Wildfire + PM2.5 + health | 2016-2022 |
| Wildfire + PM2.5 + health + province area | 2018-2022 |

For the main dashboard, `2016-2022` is the best balance because wildfire, PM2.5, and health data overlap.

## Dashboard Plan

### Page 1: Executive Overview

Purpose: give a quick national summary.

Visuals:

- KPI cards: total wildfire events, total burned area, average PM2.5, population
- map: province colored by wildfire area or PM2.5
- line chart: wildfire area and PM2.5 by year
- filter: year, province, health region

### Page 2: Wildfire Hotspots

Purpose: identify where wildfire pressure is highest.

Visuals:

- top 10 provinces by burned area
- heatmap by province and year
- map by wildfire area percent
- line chart for selected province

### Page 3: PM2.5 Exposure

Purpose: connect air pollution with wildfire activity.

Visuals:

- map by PM2.5
- scatter plot: wildfire area vs PM2.5
- trend line by year
- province ranking table

### Page 4: Health Region Impact

Purpose: compare health regions using population-adjusted rates.

Visuals:

- bar chart: selected mental health rate by health region
- line chart: selected indicator over time
- map by selected health indicator
- scatter plot: PM2.5 vs health rate

### Page 5: Wildfire Causes

Purpose: explain possible drivers behind wildfire activity.

Visuals:

- stacked bar chart by year and cause
- ranked cause totals
- line chart for selected cause

## Suggested Tableau or Power BI Interactions

- Year range filter
- Province filter
- Health region filter
- Metric selector: wildfire area, PM2.5, depression rate, anxiety rate, suicide rate
- Tooltip with province, year, wildfire area, PM2.5, population, selected health rate
- Drill-down from health region to province

## Possible Headline

Wildfire pressure in Thailand is uneven across provinces and years, with northern areas showing repeated hotspots. By combining wildfire activity, PM2.5 exposure, population, and mental health records, this project helps identify where environmental pressure and public health vulnerability overlap.

## Notes and Limits

- This analysis can show patterns and relationships, but it should not claim wildfire or PM2.5 directly causes mental health outcomes without stronger statistical modeling.
- Province-level annual data may hide short-term smoke exposure events.
- PM2.5 names must be mapped carefully to Thai province names before joining.
- Case counts should be compared as rates per 100,000 population.

## Next Step

Prepare cleaned CSV files:

- `clean_province_year.csv`
- `clean_wildfire_causes_long.csv`
- `data_dictionary_cleaned.csv`

These files will be ready to import into Tableau or Power BI.
