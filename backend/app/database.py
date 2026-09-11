import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users (
	id TEXT PRIMARY KEY,
	name TEXT NOT NULL,
	location TEXT NOT NULL,
	capital NUMERIC NOT NULL,
	land NUMERIC NOT NULL,
	water TEXT NOT NULL,
	skills JSONB NOT NULL,
	resources JSONB NOT NULL,
	experience TEXT NOT NULL,
	goal TEXT NOT NULL,
	profile_type TEXT NOT NULL
);

ALTER TABLE users ADD COLUMN IF NOT EXISTS resources JSONB NOT NULL DEFAULT '[]'::jsonb;

CREATE TABLE IF NOT EXISTS businesses (
	id TEXT PRIMARY KEY,
	name TEXT NOT NULL,
	category TEXT NOT NULL,
	location TEXT NOT NULL,
	minimum_capital NUMERIC NOT NULL,
	maximum_capital NUMERIC NOT NULL,
	required_land NUMERIC NOT NULL,
	water_required TEXT NOT NULL,
	required_skills JSONB NOT NULL,
	experience_level TEXT NOT NULL,
	monthly_cost NUMERIC NOT NULL,
	monthly_revenue NUMERIC NOT NULL,
	demand_level TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS schemes (
	id TEXT PRIMARY KEY,
	name TEXT NOT NULL,
	target_group TEXT NOT NULL,
	sector TEXT NOT NULL,
	location TEXT NOT NULL,
	minimum_capital NUMERIC NOT NULL,
	support_type TEXT NOT NULL,
	maximum_support NUMERIC NOT NULL,
	eligibility JSONB NOT NULL,
	required_documents JSONB NOT NULL,
	source_type TEXT NOT NULL,
	verification_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approvals (
	id TEXT PRIMARY KEY,
	business_id TEXT NOT NULL REFERENCES businesses(id),
	registration TEXT NOT NULL,
	license TEXT NOT NULL,
	documents JSONB NOT NULL,
	authority TEXT NOT NULL,
	process_steps JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS market_data (
	id TEXT PRIMARY KEY,
	location TEXT NOT NULL,
	business_category TEXT NOT NULL,
	demand_level TEXT NOT NULL,
	competition_level TEXT NOT NULL,
	market_score NUMERIC NOT NULL
);
"""


def get_connection() -> psycopg.Connection:
	if not DATABASE_URL:
		raise RuntimeError("DATABASE_URL is not configured")
	return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def create_tables() -> None:
	with get_connection() as connection:
		with connection.cursor() as cursor:
			cursor.execute(TABLES_SQL)
		connection.commit()


def check_database_connection() -> bool:
	with get_connection() as connection:
		with connection.cursor() as cursor:
			cursor.execute("SELECT 1")
			return bool(cursor.fetchone())
