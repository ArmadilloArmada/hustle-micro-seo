from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .approve import APPROVAL_FILENAME, approve_pack
from .config import load_config
from .export_pack import export_client_pack
from .generate import generate_pack
from .llm import openai_available


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hustle-micro-seo",
        description=(
            "Generate → human-approve → export a micro-SEO client pack "
            "(blog draft, GBP posts, FAQ schema). Never auto-publishes."
        ),
    )
    p.add_argument(
        "command",
        nargs="?",
        default="generate",
        choices=("generate", "approve", "export"),
        help="generate (default) | approve | export",
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
        help="Skip OpenAI even if OPENAI_API_KEY is set (generate)",
    )
    p.add_argument(
        "--note",
        default="",
        help=f"Optional note stored in {APPROVAL_FILENAME} (approve)",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Export without APPROVAL.json (not recommended)",
    )
    return p


def _cmd_generate(args: argparse.Namespace) -> int:
    try:
        cfg = load_config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    template_only = bool(args.template_only)
    mode = "openai" if openai_available() and not template_only else "template"

    written = generate_pack(cfg, args.out, force_template=template_only)
    biz = (cfg.get("business") or {}).get("name", "business")
    print(f"Generated micro-SEO pack for {biz} [{mode}]")
    for name, path in written.items():
        print(f"  {name} -> {path}")
    print("Next: edit drafts, then `python -m src approve`, then `python -m src export`.")
    print("Human review required before any publish. This tool does not post to WordPress or GBP.")
    return 0


def _cmd_approve(args: argparse.Namespace) -> int:
    try:
        path = approve_pack(args.out, note=args.note)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Approved drafts → {path}")
    print("No publish performed. Next: `python -m src export` for out/export/client-pack/.")
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    try:
        written = export_client_pack(args.out, require_approval=not args.force)
    except (FileNotFoundError, PermissionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print("Exported client delivery pack (manual paste only — no auto-publish):")
    print(f"  folder -> {written['pack_dir']}")
    print(f"  zip    -> {written['zip']}")
    for key in ("blog-draft.md", "gbp-posts.md", "faq-schema.json", "PASTE-INTO-WP-GBP.md"):
        if key in written:
            print(f"  {key} -> {written[key]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "approve":
        return _cmd_approve(args)
    if args.command == "export":
        return _cmd_export(args)
    return _cmd_generate(args)


if __name__ == "__main__":
    raise SystemExit(main())
