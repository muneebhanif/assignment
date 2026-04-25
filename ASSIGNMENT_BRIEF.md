# NorthStar assignment brief

## What this assignment is about

This case study is about a company called NorthStar Urban Mobility and Logistics.

The company has data in many places and the data does not connect well. Because of that, management cannot clearly explain:

- why some zones perform worse than others
- why delays and failed deliveries keep happening
- why complaints are increasing
- whether drivers, hubs, routes, or vehicles are causing the biggest problems
- how the company should redesign its data setup for better decisions

So the assignment is not only about making charts. It is about finding the real business problems, using evidence from the data, and then proposing a better data design.

## What technologies the brief expects us to use

The brief says the work should combine these parts into one solution:

- SQL within R
- R analytics
- Python data processing
- MongoDB Atlas NoSQL database design

That means we should show one connected workflow, not four unrelated tasks.

## Is Google Colab required?

Yes.

The assignment brief says that students are required to implement their analytical workflows using Google Colab notebooks.

So yes, this is written in the assignment.

## Is GitHub also required?

Yes.

The brief also says that all notebooks must be stored in a structured GitHub repository, and that the repository link must be included in the final submission.

## Practical meaning for our work

We can still start the work locally because it is faster for building and testing.

Then we can move the final work into Google Colab notebooks for submission.

That gives us a simple workflow:

1. build and test the logic locally
2. copy the cleaned final workflow into Colab notebooks
3. keep the notebooks in GitHub
4. put the GitHub link in the final assignment submission

## Simple plan for the Colab version

We can turn this project into four notebooks:

1. Python cleaning and feature creation
2. SQL in R analysis
3. R charts and interpretation
4. MongoDB Atlas document design and loading

## Suggested questions to answer in the report

- Which hub zones have the highest delay or failure rate?
- Which service types create the most complaints?
- Do route overrides connect with lower customer ratings?
- Which hubs or drivers show repeated operational risk?
- How should complaint, incident, and app-event history be remodelled in MongoDB?

## What has already been started in this project

- python/01_clean_and_explore.py builds a cleaned joined dataset and saves charts
- r/01_sql_in_r.R runs SQL inside R
- r/02_r_analytics.R creates simple charts in R
- mongodb/01_build_mongodb.py creates MongoDB-ready order case documents

## Next steps

1. Run the Python script and review the saved outputs.
2. Write a few short findings from the Python summary tables.
3. Run the SQL in R script and save the key query results.
4. Run the R analytics script and keep the charts for the report.
5. Build or test the MongoDB Atlas part.
6. Move the final workflow into Google Colab notebooks.
7. Push the notebooks to GitHub.
8. Write the final report around the evidence.