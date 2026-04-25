# NorthStar assignment starter
# Part 1: run SQL inside R in a simple way

load_or_install <- function(package_name) {
  if (!require(package_name, character.only = TRUE)) {
    install.packages(package_name, repos = "https://cloud.r-project.org")
    library(package_name, character.only = TRUE)
  }
}

load_or_install("DBI")
load_or_install("RSQLite")
load_or_install("readr")
load_or_install("dplyr")

root_dir <- normalizePath(".")
out_dir <- file.path(root_dir, "outputs", "sql")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

db_path <- file.path(out_dir, "northstar.sqlite")
con <- dbConnect(RSQLite::SQLite(), db_path)

csv_files <- c(
  "customers",
  "drivers",
  "vehicles",
  "hubs",
  "orders",
  "deliveries",
  "incidents",
  "complaints",
  "app_events"
)

for (table_name in csv_files) {
  csv_path <- file.path(root_dir, paste0(table_name, ".csv"))
  data_frame <- readr::read_csv(csv_path, show_col_types = FALSE)
  dbWriteTable(con, table_name, data_frame, overwrite = TRUE)
}

zone_performance_sql <- "
SELECT
    h.zone AS hub_zone,
    COUNT(d.delivery_id) AS total_deliveries,
    SUM(CASE WHEN d.delivery_status IN ('Delayed', 'Failed') THEN 1 ELSE 0 END) AS delayed_or_failed,
    ROUND(AVG(CASE WHEN d.delivery_status IN ('Delayed', 'Failed') THEN 1.0 ELSE 0 END), 3) AS delay_rate,
    ROUND(AVG(d.customer_rating_post_delivery), 2) AS avg_rating,
    COUNT(DISTINCT c.complaint_id) AS complaint_count
FROM deliveries d
LEFT JOIN hubs h
    ON d.hub_id = h.hub_id
LEFT JOIN complaints c
    ON d.order_id = c.order_id
GROUP BY h.zone
ORDER BY delay_rate DESC, complaint_count DESC;
"

high_risk_driver_sql <- "
SELECT
    d.driver_id,
    dr.base_zone,
    COUNT(*) AS total_jobs,
    ROUND(AVG(d.manual_route_override_count), 2) AS avg_route_overrides,
    SUM(CASE WHEN d.delivery_status IN ('Delayed', 'Failed') THEN 1 ELSE 0 END) AS bad_outcomes,
    COUNT(i.incident_id) AS incident_count,
    ROUND(AVG(d.customer_rating_post_delivery), 2) AS avg_rating
FROM deliveries d
LEFT JOIN drivers dr
    ON d.driver_id = dr.driver_id
LEFT JOIN incidents i
    ON d.delivery_id = i.delivery_id
GROUP BY d.driver_id, dr.base_zone
HAVING COUNT(*) >= 3
ORDER BY bad_outcomes DESC, incident_count DESC, avg_route_overrides DESC;
"

customer_friction_sql <- "
SELECT
    cu.customer_type,
    cu.home_zone,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.complaint_id) AS total_complaints,
    COUNT(DISTINCT a.event_id) AS total_app_events,
    ROUND(COUNT(DISTINCT c.complaint_id) * 1.0 / NULLIF(COUNT(DISTINCT o.order_id), 0), 3) AS complaints_per_order
FROM customers cu
LEFT JOIN orders o
    ON cu.customer_id = o.customer_id
LEFT JOIN complaints c
    ON o.order_id = c.order_id
LEFT JOIN app_events a
    ON o.order_id = a.order_id
GROUP BY cu.customer_type, cu.home_zone
HAVING COUNT(DISTINCT o.order_id) > 0
ORDER BY complaints_per_order DESC, total_complaints DESC;
"

zone_performance <- dbGetQuery(con, zone_performance_sql)
high_risk_drivers <- dbGetQuery(con, high_risk_driver_sql)
customer_friction <- dbGetQuery(con, customer_friction_sql)

readr::write_csv(zone_performance, file.path(out_dir, "zone_performance.csv"))
readr::write_csv(high_risk_drivers, file.path(out_dir, "high_risk_drivers.csv"))
readr::write_csv(customer_friction, file.path(out_dir, "customer_friction.csv"))

print("Saved SQL query outputs to outputs/sql")
print(zone_performance)

dbDisconnect(con)
