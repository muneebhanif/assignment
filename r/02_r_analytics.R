# NorthStar assignment starter
# Part 2: simple analytics and charts in R

load_or_install <- function(package_name) {
  if (!require(package_name, character.only = TRUE)) {
    install.packages(package_name, repos = "https://cloud.r-project.org")
    library(package_name, character.only = TRUE)
  }
}

load_or_install("readr")
load_or_install("dplyr")
load_or_install("ggplot2")

root_dir <- normalizePath(".")
python_output <- file.path(root_dir, "outputs", "python", "order_delivery_view.csv")
chart_dir <- file.path(root_dir, "outputs", "r_charts")
dir.create(chart_dir, recursive = TRUE, showWarnings = FALSE)

if (!file.exists(python_output)) {
  stop("Run python/01_clean_and_explore.py first so the merged file exists.")
}

orders_view <- readr::read_csv(python_output, show_col_types = FALSE)

zone_summary <- orders_view %>%
  group_by(hub_zone_clean) %>%
  summarise(
    total_orders = n(),
    delay_rate = mean(was_late_or_failed, na.rm = TRUE),
    avg_rating = mean(customer_rating_post_delivery, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(desc(delay_rate))

service_summary <- orders_view %>%
  group_by(service_type) %>%
  summarise(
    total_orders = n(),
    avg_order_value = mean(order_value, na.rm = TRUE),
    complaint_rate = mean(has_complaint, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(desc(complaint_rate))

readr::write_csv(zone_summary, file.path(chart_dir, "zone_summary_from_r.csv"))
readr::write_csv(service_summary, file.path(chart_dir, "service_summary_from_r.csv"))

zone_plot <- ggplot(zone_summary, aes(x = reorder(hub_zone_clean, delay_rate), y = delay_rate)) +
  geom_col(fill = "steelblue") +
  coord_flip() +
  labs(
    title = "Delay rate by hub zone",
    x = "Hub zone",
    y = "Delay or fail rate"
  ) +
  theme_minimal()

ggsave(
  filename = file.path(chart_dir, "delay_rate_by_zone.png"),
  plot = zone_plot,
  width = 8,
  height = 5
)

service_plot <- ggplot(service_summary, aes(x = reorder(service_type, complaint_rate), y = complaint_rate)) +
  geom_col(fill = "tomato") +
  coord_flip() +
  labs(
    title = "Complaint rate by service type",
    x = "Service type",
    y = "Complaint rate"
  ) +
  theme_minimal()

ggsave(
  filename = file.path(chart_dir, "complaint_rate_by_service.png"),
  plot = service_plot,
  width = 8,
  height = 5
)

print("Saved R analytics outputs to outputs/r_charts")
print(zone_summary)
print(service_summary)
