# hustle-micro-seo

Micro-SEO **content pack** CLI for one local service business. Feed NAP + review blurbs in YAML; get a blog draft, Google Business Profile post drafts, and FAQ JSON-LD. Then **human-approve** and export a **client delivery pack** for paste into WordPress / GBP.

Part of Project Hustle Tier 0 §5 — barter → paid local SEO help **without auto-posting**.

## Pipeline

```text
config.yaml → generate drafts → human edit → approve → export client-pack
                                                      ↘ zip for handoff
```

| Step | Command | Result |
|------|---------|--------|
| 1. Generate | `python -m src --template-only` | `out/blog-draft.md`, `out/gbp-posts.md`, `out/faq-schema.json` |
| 2. Approve | `python -m src approve` | `out/APPROVAL.json` (gate; no publish) |
| 3. Export | `python -m src export` | `out/export/client-pack/` + `out/export/client-pack.zip` |

**No auto-publish** to WordPress, Google Business Profile, or anywhere else. A human pastes from the pack.

## What it produces

| File | Purpose |
|------|---------|
| `out/blog-draft.md` | Local blog article + meta fields + editor checklist |
| `out/gbp-posts.md` | Four GBP post drafts (paste manually) |
| `out/faq-schema.json` | FAQPage JSON-LD (verify before embedding) |
| `out/APPROVAL.json` | Human-approve record (required before export) |
| `out/export/client-pack/` | Paste-ready folder + `PASTE-INTO-WP-GBP.md` |
| `out/export/client-pack.zip` | Same pack zipped for client handoff |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp config.example.yaml config.yaml
# edit NAP / services / reviews for your client

python -m src --config config.yaml --out out
```

### Dry-run (demo plumber, template mode)

```bash
cp config.example.yaml config.yaml
python -m src --template-only
python -m src approve --note "Demo dry-run review"
python -m src export
```

Hand the folder or zip to a human:

- `out/export/client-pack/`
- `out/export/client-pack.zip`

Open `PASTE-INTO-WP-GBP.md` inside the pack for WordPress / GBP paste steps.

Optional LLM rewrite (still requires human edit + approve):

```bash
export OPENAI_API_KEY=sk-...
# optional: export OPENAI_MODEL=gpt-4o-mini
python -m src generate
python -m src approve
python -m src export
```

Without `OPENAI_API_KEY`, the CLI writes **full template drafts** (not empty stubs) from the config facts.

Export without approval is blocked unless you pass `--force` (not recommended).

## Config

`config.example.yaml` includes a **fictional** Austin plumber (Clearflow Plumbing Co.) with NAP, services, and sample review blurbs. Replace with real client intake before any live use. Never invent licenses, awards, or testimonials.

## Compliance / E-E-A-T caution

- **Google spam policies:** Thin, scaled, or unedited AI pages can hurt the site and the GBP. Publish only after a human edit with real experience signals (photos, specifics, accurate NAP).
- **E-E-A-T:** Experience, Expertise, Authoritativeness, Trust — AI drafts are a starting point. Add original photos, verified credentials, and client-approved quotes before anything goes live.
- **Reviews:** Only use testimonials the business is allowed to republish. Do not fabricate ratings.
- **No review gating / keyword stuffing** in GBP posts.
- **FAQ JSON-LD:** Strip the tooling `_meta` object before embedding; validate answers with the owner.
- **Delivery:** The export pack is for **manual paste**. This repo never calls WordPress or GBP APIs.

## Layout

```
config.example.yaml
requirements.txt
pyproject.toml
src/
  cli.py
  config.py
  generate.py
  approve.py
  export_pack.py
  llm.py
  templates.py
out/
  .gitkeep
  export/client-pack/   # created by `python -m src export`
```

## License

MIT — see `LICENSE`.
