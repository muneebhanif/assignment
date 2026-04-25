# What to put in your notebooks

This guide is for turning the NorthStar assignment into clear Google Colab notebooks.

## Best notebook structure

It is better to use 4 notebooks instead of putting everything into one long notebook.

### Notebook 1: Python cleaning and feature creation

Use this notebook to show how you prepared the data.

Put these sections inside:

1. Title and aim
   - short title
   - 3 to 5 lines explaining what this notebook does

2. Install and import packages
   - pandas
   - matplotlib
   - pathlib

3. Load the CSV files
   - read the raw datasets
   - show a few rows from each important table

4. Data quality checks
   - missing values
   - duplicate rows
   - messy zone names
   - wrong date values
   - strange delivery times

5. Cleaning steps
   - standardise zone names
   - fix text labels
   - parse dates
   - create cleaned columns

6. Join the data
   - combine orders, deliveries, customers, drivers, vehicles, hubs, complaints, incidents, and app events

7. Feature engineering
   - `delivery_hours`
   - `was_late_or_failed`
   - `has_complaint`
   - `has_incident`
   - `manual_override_flag`
   - `needs_attention`

8. Simple outputs
   - zone summary
   - hub summary
   - service summary
   - attention orders table

9. Charts
   - delay or fail rate by hub zone
   - route overrides vs rating

10. Short findings
   - write 3 to 5 bullet points in simple business language

## Notebook 2: SQL in R

Use this notebook to show structured querying.

Put these sections inside:

1. Title and aim
   - explain that this notebook uses SQL inside R to answer business questions

2. Install and import packages
   - DBI
   - RSQLite
   - readr
   - dplyr

3. Load CSV files into SQLite tables
   - show that each CSV becomes one table

4. Run SQL queries
   - zone performance query
   - high-risk drivers query
   - customer friction query

5. Show SQL outputs
   - print result tables
   - maybe show top 10 rows only for readability

6. Explain the meaning
   - what zones are weak
   - what drivers look risky
   - what customer groups face more friction

## Notebook 3: R analytics and charts

Use this notebook to build report-ready charts.

Put these sections inside:

1. Title and aim
   - explain that this notebook explores patterns and trends visually

2. Install and import packages
   - readr
   - dplyr
   - ggplot2

3. Load cleaned output
   - use the merged file from the Python work

4. Create summary tables
   - delay rate by zone
   - complaint rate by service type
   - average rating by zone or hub

5. Create charts
   - bar chart for delay rate by zone
   - bar chart for complaint rate by service type
   - optional extra chart for ratings or incidents

6. Write chart interpretation
   - after every chart, add 2 to 4 lines explaining what it means

## Notebook 4: MongoDB Atlas design

Use this notebook to explain the NoSQL part.

Put these sections inside:

1. Title and aim
   - explain why MongoDB is useful for this case

2. Why relational tables are not enough
   - app events are flexible
   - complaint and incident history grows over time
   - case-level history is easier in a document model

3. Proposed document design
   - one order case document
   - nested customer data
   - nested delivery data
   - complaints array
   - incidents array
   - app events array
   - risk flags

4. Show sample document
   - include one small example document

5. Explain indexes
   - customer id index
   - service type index
   - delivery status index

6. Explain business value
   - easier case tracking
   - easier exception investigation
   - better support for changing semi-structured data

7. If possible, show upload code
   - connect to MongoDB Atlas
   - insert or upsert documents

## What every notebook should include

Every notebook should have these things:

- a clear title
- a short aim section
- small code blocks
- outputs shown under the code
- short explanations after tables and charts
- a final findings section

## Good writing style for the notebook

Keep the notebook simple.

Use this style:

- first say what you will do
- then show the code
- then show the output
- then explain what the output means

## What your marker wants to see

Your notebooks should show:

- that you understood the business problem
- that you cleaned and joined the data properly
- that you asked useful analytical questions
- that you explained the findings clearly
- that you designed a MongoDB solution for the semi-structured data

## Simple notebook template for each section

You can follow this pattern again and again:

1. Markdown heading
2. Short explanation
3. Code cell
4. Output
5. Short interpretation

## Suggested notebook names

Use simple file names like these:

- 01_python_cleaning.ipynb
- 02_sql_in_r.ipynb
- 03_r_analytics.ipynb
- 04_mongodb_atlas.ipynb

## Final reminder

The brief says:

- use Google Colab notebooks
- store the notebooks in GitHub
- include the GitHub repository link in the final submission

So the safe plan is:

1. finish the work locally
2. move it into Colab notebooks
3. keep the notebooks clean and well explained
4. upload to GitHub
5. submit the GitHub link
