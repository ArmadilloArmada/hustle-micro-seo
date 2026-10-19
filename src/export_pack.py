"""Export human-approved drafts into a client delivery pack (folder + zip).

No WordPress or GBP API calls — paste-ready files only.
"""

from __future__ import annotations

import shutil
import zipfile
from datetime import date
from pathlib import Path

from .approve import APPROVAL_FILENAME, is_approved, load_approval, missing_or_empty, required_paths

CLIENT_PACK_DIRNAME = "client-pack"
EXPORT_ROOT = "export"
MANIFEST_NAME = "MANIFEST.md"
PASTE_GUIDE_NAME = "PASTE-INTO-WP-GBP.md"


def _paste_guide() -> str:
    return f"""# Paste guide — WordPress + Google Business Profile

Generated: {date.today().isoformat()}

**This pack does not auto-publish.** A human pastes each file after a final edit.

## Before you paste (E-E-A-T)

- Verify NAP, license, hours, and every testimonial with the business owner.
- Add original job photos and specific local details — thin AI pages hurt trust and rankings.
- Remove demo/fictional claims if this pack still contains sample data.
- Follow [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies) and GBP misrepresentation rules.

## 1. Blog → WordPress

1. Open `blog-draft.md` in an editor.
2. Copy the article body (skip or convert the meta block as needed).
3. In WordPress: **Posts → Add New** (or your page builder).
4. Paste title, body, meta title / description into Yoast / Rank Math / core fields.
5. Attach real photos; set featured image; preview on mobile.
6. Publish only after human sign-off.

## 2. GBP posts → Google Business Profile

1. Open `gbp-posts.md`.
2. For each **Post N**, copy the body text.
3. In Google Business Profile Manager → **Posts** → create a new update.
4. Paste, add a real photo when possible, and publish manually.
5. Do not keyword-stuff or gate reviews.

## 3. FAQ schema → site

1. Open `faq-schema.json`.
2. Remove the `_meta` object before embedding (it is tooling metadata, not schema.org).
3. Validate answers against real client facts.
4. Embed as JSON-LD in the page `<head>` or via your SEO plugin’s custom schema field.
5. Test with Rich Results / schema validators after deploy.

## Files in this pack

| File | Paste target |
|------|----------------|
| `blog-draft.md` | WordPress post / page |
| `gbp-posts.md` | Google Business Profile posts |
| `faq-schema.json` | Site FAQ JSON-LD |
| `APPROVAL.json` | Internal record only — do not publish |
| `{PASTE_GUIDE_NAME}` | This guide |
| `{MANIFEST_NAME}` | Pack checklist |
"""


def _manifest(out_dir: Path, pack_dir: Path) -> str:
    approval = load_approval(out_dir) or {}
    lines = [
        f"# Client pack manifest — {date.today().isoformat()}",
        "",
        f"- Pack folder: `{pack_dir.as_posix()}`",
        f"- Approved at: `{approval.get('approved_at', 'unknown')}`",
        f"- Auto-publish: **false** (manual paste only)",
        "",
        "## Included drafts",
        "",
    ]
    for name in required_paths(out_dir):
        path = pack_dir / name
        size = path.stat().st_size if path.is_file() else 0
        lines.append(f"- `{name}` ({size} bytes)")
    lines.extend(
        [
            "",
            "## Human checklist",
            "",
            "- [ ] Owner verified all facts",
            "- [ ] Testimonials cleared for republish",
            "- [ ] Original photos attached in WP / GBP",
            "- [ ] `_meta` stripped from FAQ JSON-LD before embed",
            "- [ ] Pasted manually — no automation ran",
            "",
        ]
    )
    return "\n".join(lines)


def export_client_pack(out_dir: Path, *, require_approval: bool = True) -> dict[str, Path]:
    """Copy approved drafts to out/export/client-pack/ and zip the folder."""
    problems = missing_or_empty(out_dir)
    if problems:
        raise FileNotFoundError(
            "Cannot export — drafts missing. Run generate (and approve) first. "
            + "; ".join(problems)
        )
    if require_approval and not is_approved(out_dir):
        raise PermissionError(
            f"Human approve required before export. Run: python -m src approve "
            f"(creates {out_dir / APPROVAL_FILENAME})"
        )

    export_root = out_dir / EXPORT_ROOT
    pack_dir = export_root / CLIENT_PACK_DIRNAME
    if pack_dir.exists():
        shutil.rmtree(pack_dir)
    pack_dir.mkdir(parents=True, exist_ok=True)

    written: dict[str, Path] = {"pack_dir": pack_dir}

    for name, src in required_paths(out_dir).items():
        dest = pack_dir / name
        shutil.copy2(src, dest)
        written[name] = dest

    approval_src = out_dir / APPROVAL_FILENAME
    if approval_src.is_file():
        dest = pack_dir / APPROVAL_FILENAME
        shutil.copy2(approval_src, dest)
        written[APPROVAL_FILENAME] = dest

    guide_path = pack_dir / PASTE_GUIDE_NAME
    guide_path.write_text(_paste_guide(), encoding="utf-8")
    written[PASTE_GUIDE_NAME] = guide_path

    manifest_path = pack_dir / MANIFEST_NAME
    manifest_path.write_text(_manifest(out_dir, pack_dir), encoding="utf-8")
    written[MANIFEST_NAME] = manifest_path

    zip_path = export_root / f"{CLIENT_PACK_DIRNAME}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack_dir.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=f"{CLIENT_PACK_DIRNAME}/{path.relative_to(pack_dir).as_posix()}")
    written["zip"] = zip_path
    return written
