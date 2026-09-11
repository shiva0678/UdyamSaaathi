import json
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb

from app.database import create_tables, get_connection

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_json(filename: str) -> Any:
    with (DATA_DIR / filename).resolve().open(encoding="utf-8") as data_file:
        return json.load(data_file)


def json_value(value: Any, json_fields: set[str], field: str) -> Any:
    return Jsonb(value) if field in json_fields else value


def upsert_records(
    connection: Any,
    table: str,
    records: list[dict[str, Any]],
    json_fields: set[str],
) -> None:
    if not records:
        return

    fields = list(records[0].keys())
    field_sql = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))
    updates = ", ".join(f"{field} = EXCLUDED.{field}" for field in fields if field != "id")
    query = (
        f"INSERT INTO {table} ({field_sql}) VALUES ({placeholders}) "
        f"ON CONFLICT (id) DO UPDATE SET {updates}"
    )

    values = [
        tuple(json_value(record[field], json_fields, field) for field in fields)
        for record in records
    ]
    with connection.cursor() as cursor:
        cursor.executemany(query, values)


def seed_database() -> None:
    create_tables()
    businesses = load_json("businesses.json")
    schemes = load_json("schemes.json")
    approvals = load_json("approvals.json")
    market_data = load_json("market_data.json")
    demo_user = load_json("demo_user.json")

    with get_connection() as connection:
        upsert_records(connection, "users", [demo_user], {"skills", "resources"})
        upsert_records(connection, "businesses", businesses, {"required_skills"})
        upsert_records(
            connection,
            "schemes",
            schemes,
            {"eligibility", "required_documents"},
        )
        upsert_records(
            connection,
            "approvals",
            approvals,
            {"documents", "process_steps"},
        )
        upsert_records(connection, "market_data", market_data, set())
        connection.commit()

    print(
        "Seed complete: "
        f"{len(businesses)} businesses, {len(schemes)} schemes, "
        f"{len(approvals)} approvals, {len(market_data)} market records, "
        "1 demo user."
    )


if __name__ == "__main__":
    try:
        seed_database()
    except psycopg.OperationalError as error:
        raise SystemExit(
            "Supabase connection failed. Copy the Session pooler URL from "
            "Supabase Connect > Postgres into backend/.env as DATABASE_URL. "
            f"Original error: {error}"
        ) from error
