"""Human-approve gate for micro-SEO drafts. Never publishes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .generate import OUTPUT_NAMES

APPROVAL_FILENAME = "APPROVAL.json"


def required_paths(out_dir: Path) -> dict[str, Path]:
    return {name: out_dir / name for name in OUTPUT_NAMES}


def missing_or_empty(out_dir: Path) -> list[str]:
    problems: list[str] = []
    for name, path in required_paths(out_dir).items():
        if not path.is_file():
            problems.append(f"missing: {name}")
        elif path.stat().st_size == 0:
            problems.append(f"empty: {name}")
    return problems


def load_approval(out_dir: Path) -> dict[str, Any] | None:
    path = out_dir / APPROVAL_FILENAME
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def is_approved(out_dir: Path) -> bool:
    data = load_approval(out_dir)
    if not data or data.get("status") != "approved":
        return False
    files = data.get("files") or {}
    for name, path in required_paths(out_dir).items():
        if name not in files:
            return False
        if not path.is_file() or path.stat().st_size == 0:
            return False
    return True


def approve_pack(out_dir: Path, *, note: str = "") -> Path:
    """Mark existing drafts as human-approved. Does not publish anywhere."""
    problems = missing_or_empty(out_dir)
    if problems:
        raise FileNotFoundError(
            "Cannot approve until drafts exist. Run generate first. Problems: "
            + "; ".join(problems)
        )

    files_meta: dict[str, Any] = {}
    for name, path in required_paths(out_dir).items():
        files_meta[name] = {
            "bytes": path.stat().st_size,
            "path": str(path.as_posix()),
        }

    payload = {
        "status": "approved",
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "approver": "human",
        "note": note.strip()
        or "Human reviewed drafts. Ready for manual paste into WordPress / GBP only.",
        "files": files_meta,
        "publish": {
            "auto_publish": False,
            "wordpress": "manual paste only",
            "google_business_profile": "manual paste only",
        },
        "caution": (
            "E-E-A-T: add real photos, verified credentials, and client-approved quotes "
            "before publish. Thin or unedited AI pages risk Google spam policy hits."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / APPROVAL_FILENAME
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
