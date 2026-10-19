from __future__ import annotations

from pathlib import Path
from typing import Any

from .llm import enhance_with_openai, openai_available
from .templates import render_all_templates

OUTPUT_NAMES = ("blog-draft.md", "gbp-posts.md", "faq-schema.json")


def generate_pack(cfg: dict[str, Any], out_dir: Path, *, force_template: bool = False) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    use_llm = openai_available() and not force_template
    artifacts = enhance_with_openai(cfg) if use_llm else render_all_templates(cfg)

    written: dict[str, Path] = {}
    for name in OUTPUT_NAMES:
        path = out_dir / name
        path.write_text(artifacts[name], encoding="utf-8")
        written[name] = path
    return written
