# NorthStar assignment - next steps

## What is already started

This starter pack gives you four simple building blocks:

- [python/01_clean_and_explore.py](python/01_clean_and_explore.py) cleans the messy CSV files and builds one joined delivery view.
- [r/01_sql_in_r.R](r/01_sql_in_r.R) shows how to run SQL inside R with SQLite.
- [r/02_r_analytics.R](r/02_r_analytics.R) creates a few simple charts and summary tables in R.
- [mongodb/01_build_mongodb.py](mongodb/01_build_mongodb.py) reshapes the data into MongoDB-ready order case documents.

## Best order to work in

1. Run the Python cleaning script first.
2. Run the SQL in R script.
3. Run the R analytics script.
4. Run the MongoDB build script.
5. Use the saved outputs to write your report.

## Suggested report structure

### 1. Business problem
Explain the main pain points you found:
- delay and failed deliveries
- repeated complaints
- heavy route overrides
- weak zones or hubs
- possible fleet or maintenance pressure

### 2. SQL in R section
Use the outputs from [outputs/sql](outputs/sql) and explain:
- which zones perform badly
- which drivers show high operational risk
- which customer groups report the most friction

### 3. R analytics section
Use the charts from [outputs/r_charts](outputs/r_charts) and explain:
- where delay rates are high
- which service types create more complaints
- whether low ratings connect with more route overrides

### 4. Python data processing section
Use the outputs from [outputs/python](outputs/python) and explain:
- how you cleaned messy values
- how you joined the files
- what new features you created
- what patterns appear in the merged data

### 5. MongoDB section
Use [mongodb/01_build_mongodb.py](mongodb/01_build_mongodb.py) and explain:
- why an order case document is useful
- how complaints, incidents, and app events sit together in one document
- what indexes you created
- how this design supports faster case-level investigation

## Good analysis questions to answer next

- Which hub zones have the highest delayed or failed delivery rate?
- Do manual route overrides connect with poor customer ratings?
- Which service types create the most complaints?
- Are failed deliveries linked with specific hubs, drivers, or vehicle conditions?
- Do complaint-heavy orders also show more app events or incidents?

## Before final submission

- Move the scripts into Google Colab notebooks if your lecturer wants notebook-based work only.
- Save screenshots of charts and important outputs.
- Add short explanations below every query, chart, and table.
- Put everything into a GitHub repository with clear folder names.
- Add your GitHub link inside the final report.
