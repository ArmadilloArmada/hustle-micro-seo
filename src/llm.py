from __future__ import annotations

import json
import os
import re
from typing import Any

from .templates import render_all_templates


SYSTEM = """You are a careful local-SEO copy assistant for small service businesses.
Write helpful, specific drafts from the provided NAP and reviews only.
Do not invent licenses, awards, prices, or reviews.
Do not claim Google rankings.
Flag anything that needs human verification.
Avoid keyword stuffing and hype.
Output must be valid for the requested format."""


def openai_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY", "").strip())


def _client():
    from openai import OpenAI

    return OpenAI()


def _chat(prompt: str, *, json_mode: bool = False) -> str:
    kwargs: dict[str, Any] = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = _client().chat.completions.create(**kwargs)
    return (resp.choices[0].message.content or "").strip()


def enhance_with_openai(cfg: dict[str, Any]) -> dict[str, str]:
    """Rewrite template drafts with OpenAI; fall back per-file on failure."""
    base = render_all_templates(cfg)
    out = dict(base)

    biz = cfg.get("business") or {}
    context = json.dumps(
        {
            "business": biz,
            "services": cfg.get("services"),
            "reviews": cfg.get("reviews"),
            "content": cfg.get("content"),
        },
        indent=2,
    )

    try:
        blog = _chat(
            "Rewrite this local SEO blog draft. Keep markdown structure, meta fields, "
            "editor checklist, and all NAP facts accurate. Improve clarity and local specificity.\n\n"
            f"BUSINESS CONTEXT:\n{context}\n\nDRAFT:\n{base['blog-draft.md']}\n\n"
            "Return only the markdown article."
        )
        if len(blog) > 400:
            blog = re.sub(
                r"\*\*Draft mode:\*\* template.*",
                "**Draft mode:** openai (human edit still required)",
                blog,
                count=1,
            )
            out["blog-draft.md"] = blog if blog.endswith("\n") else blog + "\n"
    except Exception as exc:  # noqa: BLE001 — CLI should still emit templates
        out["blog-draft.md"] = (
            base["blog-draft.md"]
            + f"\n\n<!-- OpenAI blog rewrite failed: {exc}; template kept -->\n"
        )

    try:
        gbp = _chat(
            "Rewrite these Google Business Profile post drafts. Keep four posts, practical tone, "
            "include phone/NAP where useful, and remind that a human must paste manually.\n\n"
            f"BUSINESS CONTEXT:\n{context}\n\nDRAFT:\n{base['gbp-posts.md']}\n\n"
            "Return only the markdown document."
        )
        if len(gbp) > 200:
            gbp = gbp.replace(
                "Mode: template (optional OPENAI_API_KEY for rewrite)",
                "Mode: openai (human edit still required)",
            )
            out["gbp-posts.md"] = gbp if gbp.endswith("\n") else gbp + "\n"
    except Exception as exc:  # noqa: BLE001
        out["gbp-posts.md"] = (
            base["gbp-posts.md"]
            + f"\n\n<!-- OpenAI GBP rewrite failed: {exc}; template kept -->\n"
        )

    try:
        faq_raw = _chat(
            "Produce a JSON-LD FAQPage object for this local business. Include @context, @type FAQPage, "
            "and mainEntity Question/Answer pairs grounded only in the context. "
            "Add a _meta object with business name, mode='openai', and a note that humans must verify.\n\n"
            f"BUSINESS CONTEXT:\n{context}\n\nTEMPLATE JSON:\n{base['faq-schema.json']}",
            json_mode=True,
        )
        parsed = json.loads(faq_raw)
        if parsed.get("@type") == "FAQPage" and parsed.get("mainEntity"):
            meta = parsed.setdefault("_meta", {})
            meta.setdefault("mode", "openai")
            meta.setdefault("note", "Human must verify answers before embedding.")
            out["faq-schema.json"] = json.dumps(parsed, indent=2, ensure_ascii=False) + "\n"
    except Exception as exc:  # noqa: BLE001
        # Keep valid template JSON; annotate via sibling comment file is awkward — append is invalid JSON.
        # Instead leave template and stash error in _meta by re-parsing template.
        try:
            tmpl = json.loads(base["faq-schema.json"])
            tmpl.setdefault("_meta", {})["openai_error"] = str(exc)
            out["faq-schema.json"] = json.dumps(tmpl, indent=2, ensure_ascii=False) + "\n"
        except json.JSONDecodeError:
            out["faq-schema.json"] = base["faq-schema.json"]

    return out
