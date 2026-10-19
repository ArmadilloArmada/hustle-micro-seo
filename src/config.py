from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}. Copy config.example.yaml to config.yaml first."
        )
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if "business" not in data:
        raise ValueError("config must include a top-level 'business' block with NAP fields")
    return data


def nap_block(cfg: dict[str, Any]) -> dict[str, Any]:
    biz = cfg["business"]
    addr = biz.get("address") or {}
    return {
        "name": biz.get("name", ""),
        "owner": biz.get("owner", ""),
        "phone": biz.get("phone", ""),
        "email": biz.get("email", ""),
        "website": biz.get("website", ""),
        "street": addr.get("street", ""),
        "city": addr.get("city", ""),
        "region": addr.get("region", ""),
        "postal_code": addr.get("postal_code", ""),
        "country": addr.get("country", "US"),
        "hours": biz.get("hours", ""),
        "license_note": biz.get("license_note", ""),
        "years_in_business": biz.get("years_in_business"),
        "categories": biz.get("categories") or [],
        "service_area": biz.get("service_area") or [],
        "geo": biz.get("geo") or {},
    }


def full_address(nap: dict[str, Any]) -> str:
    parts = [
        nap.get("street", ""),
        f"{nap.get('city', '')}, {nap.get('region', '')} {nap.get('postal_code', '')}".strip(),
    ]
    return ", ".join(p for p in parts if p)
