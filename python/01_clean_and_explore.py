"""Simple starter analysis for the NorthStar assignment.

This script does four small jobs:
1. load the CSV files
2. clean a few messy values
3. build one joined order and delivery view
4. save simple tables, charts, and notes for the report
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "outputs" / "python"
CHART_DIR = ROOT_DIR / "outputs" / "python_charts"

ZONE_MAP = {
    "airport": "Airport",
    "central": "Central",
    "ctr": "Central",
    "east": "East",
    "north": "North",
    "south": "South",
    "west": "West",
    "riverside": "Riverside",
}

DATE_COLUMNS = {
    "customers": ["signup_date"],
    "orders": ["order_created_at"],
    "deliveries": ["dispatch_time", "delivery_completed_at"],
    "incidents": ["reported_at"],
    "complaints": ["created_at"],
    "app_events": ["event_timestamp"],
    "vehicles": ["commission_date"],
}

TEXT_COLUMNS_TO_TITLE = {
    "deliveries": ["delivery_status"],
    "incidents": ["severity", "resolution_status"],
    "complaints": ["channel", "severity", "status"],
}


def clean_zone(value):
    """Turn messy zone values into one consistent label."""
    if pd.isna(value):
        return pd.NA

    zone_text = str(value).strip().lower().replace(" ", "")
    return ZONE_MAP.get(zone_text, str(value).strip().title())


def clean_title_text(value):
    """Trim text and make the wording consistent."""
    if pd.isna(value):
        return pd.NA

    return str(value).strip().title()


def load_table(table_name):
    """Read one CSV file and parse any known date columns."""
    file_path = ROOT_DIR / f"{table_name}.csv"
    data_frame = pd.read_csv(file_path)

    for column_name in DATE_COLUMNS.get(table_name, []):
        data_frame[column_name] = pd.to_datetime(data_frame[column_name], errors="coerce")

    return data_frame


def clean_basic_text_columns(data_frame, table_name):
    """Standardise a few simple text columns."""
    for column_name in TEXT_COLUMNS_TO_TITLE.get(table_name, []):
        if column_name in data_frame.columns:
            data_frame[column_name] = data_frame[column_name].apply(clean_title_text)

    return data_frame


def add_clean_zone_column(data_frame, source_column, new_column):
    """Add one extra column with cleaned zone values."""
    if source_column in data_frame.columns:
        data_frame[new_column] = data_frame[source_column].apply(clean_zone)

    return data_frame


def prepare_tables():
    """Load all source files and apply small cleaning steps."""
    tables = {
        "customers": load_table("customers"),
        "drivers": load_table("drivers"),
        "vehicles": load_table("vehicles"),
        "hubs": load_table("hubs"),
        "orders": load_table("orders"),
        "deliveries": load_table("deliveries"),
        "incidents": load_table("incidents"),
        "complaints": load_table("complaints"),
        "app_events": load_table("app_events"),
    }

    for table_name, data_frame in tables.items():
        clean_basic_text_columns(data_frame, table_name)

    add_clean_zone_column(tables["customers"], "home_zone", "home_zone_clean")
    add_clean_zone_column(tables["drivers"], "base_zone", "base_zone_clean")
    add_clean_zone_column(tables["vehicles"], "assigned_zone", "assigned_zone_clean")
    add_clean_zone_column(tables["hubs"], "zone", "hub_zone_clean")
    add_clean_zone_column(tables["orders"], "pickup_zone", "pickup_zone_clean")
    add_clean_zone_column(tables["orders"], "dropoff_zone", "dropoff_zone_clean")
    add_clean_zone_column(tables["app_events"], "zone_context", "zone_context_clean")

    return tables


def build_order_delivery_view(tables):
    """Create one merged table that is easy to analyse later."""
    complaints_summary = (
        tables["complaints"]
        .groupby("order_id", dropna=False)
        .agg(
            complaint_count=("complaint_id", "count"),
            complaint_compensation_total=("compensation_amount", "sum"),
            latest_complaint_status=("status", "last"),
        )
        .reset_index()
    )

    incidents_summary = (
        tables["incidents"]
        .assign(high_severity=lambda df: df["severity"].astype(str).str.lower().isin(["high", "critical"]))
        .groupby("delivery_id", dropna=False)
        .agg(
            incident_count=("incident_id", "count"),
            high_severity_incident_count=("high_severity", "sum"),
        )
        .reset_index()
    )

    app_event_summary = (
        tables["app_events"]
        .dropna(subset=["order_id"])
        .groupby("order_id", dropna=False)
        .agg(
            app_event_count=("event_id", "count"),
            avg_api_latency_ms=("api_latency_ms", "mean"),
            failed_app_events=("success_flag", lambda values: (values == 0).sum()),
        )
        .reset_index()
    )

    order_delivery_view = (
        tables["orders"]
        .merge(tables["customers"], on="customer_id", how="left")
        .merge(tables["deliveries"], on="order_id", how="left")
        .merge(tables["drivers"], on="driver_id", how="left")
        .merge(tables["vehicles"], on="vehicle_id", how="left")
        .merge(tables["hubs"], on="hub_id", how="left")
        .merge(complaints_summary, on="order_id", how="left")
        .merge(app_event_summary, on="order_id", how="left")
        .merge(incidents_summary, on="delivery_id", how="left")
    )

    order_delivery_view["delivery_hours"] = (
        order_delivery_view["delivery_completed_at"] - order_delivery_view["dispatch_time"]
    ).dt.total_seconds() / 3600

    order_delivery_view["was_late_or_failed"] = order_delivery_view["delivery_status"].isin(["Delayed", "Failed"]).astype(int)
    order_delivery_view["has_complaint"] = order_delivery_view["complaint_count"].fillna(0).gt(0).astype(int)
    order_delivery_view["has_incident"] = order_delivery_view["incident_count"].fillna(0).gt(0).astype(int)
    order_delivery_view["manual_override_flag"] = order_delivery_view["manual_route_override_count"].fillna(0).gt(0).astype(int)
    order_delivery_view["timing_issue_flag"] = order_delivery_view["delivery_hours"].lt(0).astype(int)

    order_delivery_view["needs_attention"] = (
        (order_delivery_view["was_late_or_failed"] == 1)
        | (order_delivery_view["has_complaint"] == 1)
        | (order_delivery_view["has_incident"] == 1)
        | (order_delivery_view["timing_issue_flag"] == 1)
    ).astype(int)

    return order_delivery_view


def build_summaries(order_delivery_view):
    """Create a few small summary tables for the report."""
    zone_summary = (
        order_delivery_view
        .groupby("hub_zone_clean", dropna=False)
        .agg(
            total_orders=("order_id", "count"),
            delay_rate=("was_late_or_failed", "mean"),
            complaint_rate=("has_complaint", "mean"),
            timing_issue_rate=("timing_issue_flag", "mean"),
            avg_rating=("customer_rating_post_delivery", "mean"),
            avg_order_value=("order_value", "mean"),
        )
        .reset_index()
        .sort_values(["delay_rate", "complaint_rate"], ascending=False)
    )

    hub_summary = (
        order_delivery_view
        .groupby(["hub_id", "hub_name", "hub_zone_clean"], dropna=False)
        .agg(
            total_orders=("order_id", "count"),
            failed_or_delayed=("was_late_or_failed", "sum"),
            total_incidents=("incident_count", "sum"),
            total_complaints=("complaint_count", "sum"),
            timing_issues=("timing_issue_flag", "sum"),
            avg_rating=("customer_rating_post_delivery", "mean"),
        )
        .reset_index()
        .sort_values(["failed_or_delayed", "total_complaints"], ascending=False)
    )

    service_summary = (
        order_delivery_view
        .groupby("service_type", dropna=False)
        .agg(
            total_orders=("order_id", "count"),
            avg_order_value=("order_value", "mean"),
            delay_rate=("was_late_or_failed", "mean"),
            complaint_rate=("has_complaint", "mean"),
        )
        .reset_index()
        .sort_values("complaint_rate", ascending=False)
    )

    return zone_summary, hub_summary, service_summary


def build_data_quality_summary(tables, order_delivery_view):
    """Show the size and quality of each dataset in one table."""
    summary_rows = []
    all_tables = dict(tables)
    all_tables["order_delivery_view"] = order_delivery_view

    for table_name, data_frame in all_tables.items():
        total_cells = len(data_frame.index) * len(data_frame.columns)
        missing_cells = int(data_frame.isna().sum().sum())

        summary_rows.append(
            {
                "table_name": table_name,
                "row_count": len(data_frame.index),
                "column_count": len(data_frame.columns),
                "missing_cells": missing_cells,
                "missing_share": round(missing_cells / total_cells, 4) if total_cells else 0,
                "duplicate_rows": int(data_frame.duplicated().sum()),
            }
        )

    return pd.DataFrame(summary_rows).sort_values(["missing_share", "duplicate_rows"], ascending=False)


def build_attention_orders(order_delivery_view):
    """Keep a short list of orders that look risky or messy."""
    columns_to_keep = [
        "order_id",
        "customer_id",
        "service_type",
        "hub_name",
        "hub_zone_clean",
        "delivery_status",
        "delivery_hours",
        "timing_issue_flag",
        "complaint_count",
        "incident_count",
        "manual_route_override_count",
        "customer_rating_post_delivery",
        "needs_attention",
    ]

    attention_orders = order_delivery_view[order_delivery_view["needs_attention"] == 1].copy()
    attention_orders = attention_orders[[column for column in columns_to_keep if column in attention_orders.columns]]

    return attention_orders.sort_values(
        ["timing_issue_flag", "complaint_count", "incident_count", "manual_route_override_count"],
        ascending=False,
    )


def save_charts(zone_summary, order_delivery_view):
    """Save two simple charts for the report."""
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    zone_chart = zone_summary.dropna(subset=["hub_zone_clean"]).copy()
    zone_chart = zone_chart.sort_values("delay_rate", ascending=True)

    plt.figure(figsize=(8, 5))
    plt.barh(zone_chart["hub_zone_clean"], zone_chart["delay_rate"], color="steelblue")
    plt.title("Delay or fail rate by hub zone")
    plt.xlabel("Delay or fail rate")
    plt.ylabel("Hub zone")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "delay_rate_by_hub_zone.png")
    plt.close()

    scatter_data = order_delivery_view.dropna(subset=["manual_route_override_count", "customer_rating_post_delivery"])
    plt.figure(figsize=(8, 5))
    plt.scatter(
        scatter_data["manual_route_override_count"],
        scatter_data["customer_rating_post_delivery"],
        alpha=0.5,
        color="tomato",
    )
    plt.title("Route overrides vs customer rating")
    plt.xlabel("Manual route override count")
    plt.ylabel("Customer rating")
    plt.tight_layout()
    plt.savefig(CHART_DIR / "route_override_vs_rating.png")
    plt.close()


def save_outputs(
    tables,
    order_delivery_view,
    zone_summary,
    hub_summary,
    service_summary,
    data_quality_summary,
    attention_orders,
):
    """Write CSV outputs to disk."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for table_name, data_frame in tables.items():
        data_frame.to_csv(OUTPUT_DIR / f"cleaned_{table_name}.csv", index=False)

    order_delivery_view.to_csv(OUTPUT_DIR / "order_delivery_view.csv", index=False)
    zone_summary.to_csv(OUTPUT_DIR / "zone_summary.csv", index=False)
    hub_summary.to_csv(OUTPUT_DIR / "hub_summary.csv", index=False)
    service_summary.to_csv(OUTPUT_DIR / "service_summary.csv", index=False)
    data_quality_summary.to_csv(OUTPUT_DIR / "data_quality_summary.csv", index=False)
    attention_orders.to_csv(OUTPUT_DIR / "attention_orders.csv", index=False)


def percent_text(value):
    """Format a numeric rate in a friendly way."""
    if pd.isna(value):
        return "not available"

    return f"{value:.1%}"


def write_summary_markdown(order_delivery_view, zone_summary, hub_summary, service_summary):
    """Save a plain-English note that can be reused in the report."""
    summary_path = OUTPUT_DIR / "python_summary.md"

    top_zone = zone_summary.dropna(subset=["hub_zone_clean"]).head(1)
    top_hub = hub_summary.dropna(subset=["hub_name"]).head(1)
    top_service = service_summary.dropna(subset=["service_type"]).head(1)

    total_orders = int(order_delivery_view["order_id"].nunique())
    total_attention_orders = int(order_delivery_view["needs_attention"].sum())
    total_timing_issues = int(order_delivery_view["timing_issue_flag"].sum())
    total_complaints = int(order_delivery_view["complaint_count"].fillna(0).sum())
    total_incidents = int(order_delivery_view["incident_count"].fillna(0).sum())

    lines = [
        "# Python summary",
        "",
        "This note was created by python/01_clean_and_explore.py.",
        "",
        "## What this script did",
        "- Loaded the raw CSV files.",
        "- Cleaned messy zone labels and a few text fields.",
        "- Joined customers, orders, deliveries, complaints, incidents, app events, drivers, vehicles, and hubs.",
        "- Created simple risk flags and saved report-ready files.",
        "",
        "## Quick findings",
        f"- Total orders in the merged view: {total_orders}",
        f"- Orders needing attention: {total_attention_orders}",
        f"- Possible timing issues: {total_timing_issues}",
        f"- Total linked complaints: {total_complaints}",
        f"- Total linked incidents: {total_incidents}",
    ]

    if not top_zone.empty:
        lines.append(
            f"- Highest delay or fail zone: {top_zone.iloc[0]['hub_zone_clean']} ({percent_text(top_zone.iloc[0]['delay_rate'])})"
        )

    if not top_hub.empty:
        lines.append(
            f"- Hub with the most delayed or failed orders: {top_hub.iloc[0]['hub_name']} ({int(top_hub.iloc[0]['failed_or_delayed'])} cases)"
        )

    if not top_service.empty:
        lines.append(
            f"- Service type with the highest complaint rate: {top_service.iloc[0]['service_type']} ({percent_text(top_service.iloc[0]['complaint_rate'])})"
        )

    lines.extend(
        [
            "",
            "## Files created",
            "- outputs/python/order_delivery_view.csv",
            "- outputs/python/zone_summary.csv",
            "- outputs/python/hub_summary.csv",
            "- outputs/python/service_summary.csv",
            "- outputs/python/data_quality_summary.csv",
            "- outputs/python/attention_orders.csv",
            "- outputs/python_charts/delay_rate_by_hub_zone.png",
            "- outputs/python_charts/route_override_vs_rating.png",
        ]
    )

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    print("Loading raw files...")
    tables = prepare_tables()

    print("Building one joined view for orders and deliveries...")
    order_delivery_view = build_order_delivery_view(tables)

    print("Creating summary tables...")
    zone_summary, hub_summary, service_summary = build_summaries(order_delivery_view)
    data_quality_summary = build_data_quality_summary(tables, order_delivery_view)
    attention_orders = build_attention_orders(order_delivery_view)

    print("Saving files and charts...")
    save_outputs(
        tables,
        order_delivery_view,
        zone_summary,
        hub_summary,
        service_summary,
        data_quality_summary,
        attention_orders,
    )
    save_charts(zone_summary, order_delivery_view)
    write_summary_markdown(order_delivery_view, zone_summary, hub_summary, service_summary)

    print("Done.")
    print("Main output:", OUTPUT_DIR / "order_delivery_view.csv")
    print("Top zones by delay rate:")
    print(zone_summary.head(5))


if __name__ == "__main__":
    main()
