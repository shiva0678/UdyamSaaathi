from typing import Any


def format_approvals(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "id": row["id"],
            "business_id": row["business_id"],
            "registration": row["registration"],
            "license": row["license"],
            "documents": row["documents"],
            "authority": row["authority"],
            "process_steps": row["process_steps"],
        }
        for row in rows
    ]
