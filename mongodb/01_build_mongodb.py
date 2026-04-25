import json
import os
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "outputs" / "mongodb"

DATE_COLUMNS = {
    "customers": ["signup_date"],
    "orders": ["order_created_at"],
    "deliveries": ["dispatch_time", "delivery_completed_at"],
    "incidents": ["reported_at"],
    "complaints": ["created_at"],
    "app_events": ["event_timestamp"],
}



def load_table(table_name):
    file_path = ROOT_DIR / f"{table_name}.csv"
    data_frame = pd.read_csv(file_path)

    for column_name in DATE_COLUMNS.get(table_name, []):
        data_frame[column_name] = pd.to_datetime(data_frame[column_name], errors="coerce")

    return data_frame



def safe_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value



def row_to_dict(row, columns):
    return {column: safe_value(row[column]) for column in columns if column in row.index}



def build_documents():
    customers = load_table("customers")
    orders = load_table("orders")
    deliveries = load_table("deliveries")
    complaints = load_table("complaints")
    incidents = load_table("incidents")
    app_events = load_table("app_events")
    drivers = load_table("drivers")
    vehicles = load_table("vehicles")
    hubs = load_table("hubs")

    customer_lookup = customers.set_index("customer_id")
    delivery_lookup = deliveries.set_index("order_id")
    driver_lookup = drivers.set_index("driver_id")
    vehicle_lookup = vehicles.set_index("vehicle_id")
    hub_lookup = hubs.set_index("hub_id")

    documents = []

    for _, order_row in orders.iterrows():
        order_id = order_row["order_id"]
        customer_id = order_row["customer_id"]

        customer_row = customer_lookup.loc[customer_id] if customer_id in customer_lookup.index else None
        delivery_row = delivery_lookup.loc[order_id] if order_id in delivery_lookup.index else None

        if delivery_row is not None:
            delivery_id = delivery_row["delivery_id"]
            driver_id = delivery_row["driver_id"]
            vehicle_id = delivery_row["vehicle_id"]
            hub_id = delivery_row["hub_id"]
        else:
            delivery_id = None
            driver_id = None
            vehicle_id = None
            hub_id = None

        driver_row = driver_lookup.loc[driver_id] if driver_id in driver_lookup.index else None
        vehicle_row = vehicle_lookup.loc[vehicle_id] if vehicle_id in vehicle_lookup.index else None
        hub_row = hub_lookup.loc[hub_id] if hub_id in hub_lookup.index else None

        order_complaints = complaints[complaints["order_id"] == order_id].sort_values("created_at")
        order_events = app_events[app_events["order_id"] == order_id].sort_values("event_timestamp")
        order_incidents = incidents[incidents["delivery_id"] == delivery_id].sort_values("reported_at") if delivery_id else incidents.iloc[0:0]

        document = {
            "_id": order_id,
            "customer": row_to_dict(
                customer_row,
                [
                    "customer_id",
                    "age",
                    "home_zone",
                    "customer_type",
                    "signup_date",
                    "loyalty_score",
                    "app_engagement_score",
                    "preferred_channel",
                    "account_status",
                ],
            ) if customer_row is not None else None,
            "order": row_to_dict(
                order_row,
                [
                    "order_id",
                    "service_type",
                    "order_created_at",
                    "promised_window_hours",
                    "pickup_zone",
                    "dropoff_zone",
                    "priority_level",
                    "order_value",
                    "booking_channel",
                    "special_handling_flag",
                ],
            ),
            "delivery": row_to_dict(
                delivery_row,
                [
                    "delivery_id",
                    "driver_id",
                    "vehicle_id",
                    "hub_id",
                    "dispatch_time",
                    "delivery_completed_at",
                    "delivery_status",
                    "route_distance_km",
                    "manual_route_override_count",
                    "proof_of_completion_missing",
                    "customer_rating_post_delivery",
                    "fuel_or_charge_cost",
                ],
            ) if delivery_row is not None else None,
            "driver": row_to_dict(
                driver_row,
                [
                    "driver_id",
                    "base_zone",
                    "employment_type",
                    "years_experience",
                    "training_score",
                    "driver_rating",
                    "shift_preference",
                    "active_flag",
                ],
            ) if driver_row is not None else None,
            "vehicle": row_to_dict(
                vehicle_row,
                [
                    "vehicle_id",
                    "vehicle_type",
                    "assigned_zone",
                    "commission_date",
                    "battery_health_pct",
                    "odometer_km",
                    "maintenance_status",
                    "telematics_version",
                ],
            ) if vehicle_row is not None else None,
            "hub": row_to_dict(
                hub_row,
                ["hub_id", "hub_name", "zone", "hub_type", "capacity_score"],
            ) if hub_row is not None else None,
            "complaints": [
                row_to_dict(
                    complaint_row,
                    [
                        "complaint_id",
                        "complaint_type",
                        "channel",
                        "severity",
                        "created_at",
                        "status",
                        "resolution_days",
                        "compensation_amount",
                    ],
                )
                for _, complaint_row in order_complaints.iterrows()
            ],
            "incidents": [
                row_to_dict(
                    incident_row,
                    [
                        "incident_id",
                        "incident_type",
                        "reported_at",
                        "severity",
                        "resolution_status",
                        "resolved_hours",
                    ],
                )
                for _, incident_row in order_incidents.iterrows()
            ],
            "app_events": [
                row_to_dict(
                    event_row,
                    [
                        "event_id",
                        "event_timestamp",
                        "event_type",
                        "session_id",
                        "device_type",
                        "zone_context",
                        "api_latency_ms",
                        "success_flag",
                    ],
                )
                for _, event_row in order_events.iterrows()
            ],
        }

        document["risk_flags"] = {
            "late_or_failed": document["delivery"] is not None and document["delivery"].get("delivery_status") in ["Delayed", "Failed"],
            "has_complaint": len(document["complaints"]) > 0,
            "has_incident": len(document["incidents"]) > 0,
            "manual_override_used": document["delivery"] is not None and (document["delivery"].get("manual_route_override_count") or 0) > 0,
        }

        documents.append(document)

    return documents



def export_jsonl(documents):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "order_cases.jsonl"

    with output_path.open("w", encoding="utf-8") as file_handle:
        for document in documents:
            file_handle.write(json.dumps(document, ensure_ascii=False) + "\n")

    print(f"Saved MongoDB-ready documents to {output_path}")



def upload_to_mongodb(documents):
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("MONGODB_URI not set, so upload is skipped.")
        return

    from pymongo import MongoClient, ReplaceOne

    database_name = os.getenv("MONGODB_DB", "northstar")
    client = MongoClient(mongo_uri)
    collection = client[database_name]["order_cases"]

    operations = [ReplaceOne({"_id": document["_id"]}, document, upsert=True) for document in documents]
    if operations:
        collection.bulk_write(operations)

    collection.create_index("customer.customer_id")
    collection.create_index("order.service_type")
    collection.create_index("delivery.delivery_status")
    collection.create_index("hub.zone")
    collection.create_index("risk_flags.late_or_failed")

    print(f"Uploaded {len(documents)} documents to MongoDB database '{database_name}'.")



def main():
    documents = build_documents()
    export_jsonl(documents)
    upload_to_mongodb(documents)
    print(f"Built {len(documents)} order case documents.")


if __name__ == "__main__":
    main()
