from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .generate import generate_pack
from .llm import openai_available


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hustle-micro-seo",
        description=(
            "Generate a human-approve micro-SEO content pack "
            "(blog draft, GBP posts, FAQ schema) from local business NAP + reviews."
        ),
    )
    p.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to YAML config (default: ./config.yaml)",
    )
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        default=Path("out"),
        help="Output directory (default: ./out)",
    )
    p.add_argument(
        "--template-only",
        action="store_true",
        help="Skip OpenAI even if OPENAI_API_KEY is set",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    mode = "template"
    if openai_available() and not args.template_only:
        mode = "openai"

    written = generate_pack(cfg, args.out, force_template=args.template_only)
    biz = (cfg.get("business") or {}).get("name", "business")
    print(f"Generated micro-SEO pack for {biz} [{mode}]")
    for name, path in written.items():
        print(f"  {name} -> {path}")
    print("Human review required before any publish. This tool does not post to WordPress or GBP.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
