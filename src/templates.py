from __future__ import annotations

import json
from datetime import date
from typing import Any

from .config import full_address, nap_block


def _services(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    return list(cfg.get("services") or [])


def _reviews(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    return list(cfg.get("reviews") or [])


def _content(cfg: dict[str, Any]) -> dict[str, Any]:
    return dict(cfg.get("content") or {})


def render_blog_draft(cfg: dict[str, Any]) -> str:
    nap = nap_block(cfg)
    content = _content(cfg)
    services = _services(cfg)
    reviews = _reviews(cfg)
    city = content.get("primary_city") or nap.get("city") or "your city"
    neighborhood = content.get("primary_neighborhood") or city
    topic = content.get("blog_topic") or f"Common plumbing problems in {city}"
    biz = nap["name"]
    owner = nap.get("owner") or "our lead plumber"
    phone = nap.get("phone") or ""
    addr = full_address(nap)
    service_lines = "\n".join(
        f"- **{s.get('name', 'Service')}** — useful for searches like "
        f"{', '.join((s.get('keywords') or [])[:2]) or s.get('name', '')}."
        for s in services
    ) or "- Emergency repair, drain cleaning, and fixture work."

    review_pull = ""
    if reviews:
        r = reviews[0]
        review_pull = (
            f'\n> “{r.get("text", "").strip()}”\n>\n> — {r.get("author", "Customer")}, '
            f'{r.get("rating", 5)}★ review\n'
        )

    years = nap.get("years_in_business")
    years_bit = f" With {years} years serving {city}," if years else ""

    return f"""# {topic}

**Meta title (≤60 chars):** Stop a Small Leak Before It Floods Your Kitchen | {city}
**Meta description (≤155 chars):** Practical steps for {neighborhood} homeowners when a pipe starts dripping — plus when to call {biz} at {phone}.
**Primary intent:** Informational + local service
**Suggested slug:** stop-small-plumbing-leak-{city.lower().replace(' ', '-')}-kitchen
**Draft mode:** template (set OPENAI_API_KEY for LLM rewrite)
**Generated:** {date.today().isoformat()}

---

## Who this is for

Homeowners in {neighborhood} and nearby {city} who notice a drip under a sink, a wet cabinet base, or a hissing supply line — and want to limit damage before a pro arrives.

## Quick answer

Shut off the nearest valve, catch the water, photograph the source, and call a licensed plumber if the leak is at a joint, behind a wall, or won’t stop with the fixture valve closed. Do not ignore a “small” leak overnight: cabinetry and subfloors swell fast in humid kitchens.

## Step-by-step before you call

1. **Locate the shutoff.** Under-sink angle stops usually turn clockwise. If those fail, use the home’s main water shutoff.
2. **Relieve pressure.** Open the faucet after shutoff so residual water drains into a bowl instead of onto the floor.
3. **Contain the mess.** Towels + a shallow pan beat a shop-vac later. Move dry goods out of the cabinet.
4. **Document.** One clear photo of the fitting and one of the water meter (if spinning with fixtures off) helps the tech arrive prepared.
5. **Skip DIY torch work.** Soldering or “temporary epoxy” on pressurized copper without experience often turns a $200 repair into a ceiling tear-out.

## When a DIY patch is not enough

Call same-day help if you see active spraying, discoloration on the ceiling below, moldy odor in the cabinet, or a water heater weeping at the tank. Those are not “watch it” problems.

## How {biz} handles kitchen leaks

{biz} is a local plumbing contractor based at {addr}.{years_bit} {owner} and the crew focus on clear pricing, clean work areas, and explaining whether a repair or replacement is the smarter spend.

Services we draft content around for this pack:

{service_lines}
{review_pull}
## Local note for {neighborhood}

Older homes south of downtown often share aging supply stops and galvanized stubs under kitchen sinks. If your shutoff valve spins without stopping flow, say so when you book — techs bring stop-replacement parts so one visit can finish the job.

## Soft CTA (human: edit voice before publish)

Need a licensed eye on a leak in {city}? Call {biz} at {phone} or visit {nap.get('website', '')}. Hours: {nap.get('hours', 'see website')}. Ask about camera inspection when drains are involved.

---

### Editor checklist (human)

- [ ] Verify every claim against real client facts (license #, years, hours)
- [ ] Replace demo reviews with approved testimonials or remove quotes
- [ ] Add original photos from a real job (E-E-A-T)
- [ ] Publish only after human edit — do not auto-post
"""


def render_gbp_posts(cfg: dict[str, Any]) -> str:
    nap = nap_block(cfg)
    content = _content(cfg)
    services = _services(cfg)
    reviews = _reviews(cfg)
    city = content.get("primary_city") or nap.get("city") or "town"
    neighborhood = content.get("primary_neighborhood") or city
    biz = nap["name"]
    phone = nap.get("phone") or ""
    today = date.today().isoformat()

    svc_names = [s.get("name", "plumbing") for s in services] or [
        "emergency repair",
        "drain cleaning",
        "water heater work",
    ]

    review_line = ""
    if reviews:
        r = reviews[min(1, len(reviews) - 1)]
        snippet = (r.get("text") or "")[:140].rstrip(".")
        review_line = f' Recent neighbor feedback: “{snippet}…”'

    posts = [
        {
            "title": "Seasonal tip — kitchen leak triage",
            "body": (
                f"Spot a drip under the sink in {neighborhood}? Shut the angle stop, "
                f"catch the water, and photograph the fitting before it soaks the cabinet base. "
                f"{biz} handles emergency leak repair across {city}. Call {phone} — "
                f"human-reviewed post, not auto-published."
            ),
        },
        {
            "title": f"Service spotlight — {svc_names[0]}",
            "body": (
                f"This week we’re highlighting {svc_names[0].lower()} for {city} homeowners. "
                f"We explain options before we open walls, and we leave the work area cleaner than we found it. "
                f"Questions? {phone}.{review_line}"
            ),
        },
        {
            "title": "Offer — drain check with camera (demo copy)",
            "body": (
                f"Clogs that keep coming back usually need more than a chemical dump. "
                f"Ask {biz} about camera-assisted drain cleaning in {neighborhood}. "
                f"Mention this Google post when you book: {phone}. "
                f"(Edit price/offer before posting — this is draft copy only.)"
            ),
        },
        {
            "title": "Trust signal — hours & service area",
            "body": (
                f"{biz} · {full_address(nap)} · {phone}. "
                f"Hours: {nap.get('hours', 'see profile')}. "
                f"Service area: {', '.join(nap.get('service_area') or [city])}. "
                f"{nap.get('license_note', '')} "
                f"We do not auto-post to Google Business Profile — paste only after human review."
            ),
        },
    ]

    lines = [
        f"# Google Business Profile post drafts — {biz}",
        "",
        f"Generated: {today}",
        "Mode: template (optional OPENAI_API_KEY for rewrite)",
        "Action: human edits → paste into GBP manually. No API publish in this tool.",
        "",
        "---",
        "",
    ]
    for i, post in enumerate(posts, 1):
        lines.extend(
            [
                f"## Post {i}: {post['title']}",
                "",
                post["body"],
                "",
                f"_Approx. characters: {len(post['body'])}_",
                "",
                "---",
                "",
            ]
        )
    lines.append(
        "Compliance: avoid keyword stuffing, fake urgency, or review gating. "
        "Follow Google Business Profile spam and misrepresentation policies."
    )
    return "\n".join(lines)


def render_faq_schema(cfg: dict[str, Any]) -> str:
    nap = nap_block(cfg)
    content = _content(cfg)
    services = _services(cfg)
    city = content.get("primary_city") or nap.get("city") or "the area"
    neighborhood = content.get("primary_neighborhood") or city
    biz = nap["name"]
    phone = nap.get("phone") or ""
    hours = nap.get("hours") or "see website"
    svc = (services[0].get("name") if services else "emergency plumbing")

    faqs = [
        {
            "question": f"Who do I call for a kitchen leak in {neighborhood}?",
            "answer": (
                f"{biz} serves {neighborhood} and greater {city}. Call {phone} for "
                f"{svc.lower()} and related plumbing work. A tech can walk you through "
                f"shutting water off safely before arrival."
            ),
        },
        {
            "question": f"What are {biz}'s hours?",
            "answer": f"{hours}. Confirm holiday coverage when you book.",
        },
        {
            "question": "Should I use chemical drain cleaner before calling a plumber?",
            "answer": (
                "Usually no. Harsh chemicals can damage pipes and make a later camera inspection "
                "harder. Try a plunger on fixture traps; if the clog returns, schedule professional "
                f"drain cleaning with {biz}."
            ),
        },
        {
            "question": f"Where is {biz} located?",
            "answer": (
                f"{biz} is listed at {full_address(nap)}. Service area includes "
                f"{', '.join(nap.get('service_area') or [city])}."
            ),
        },
        {
            "question": "Do you provide upfront pricing?",
            "answer": (
                f"Draft answer for human edit: {biz} explains likely repair vs replacement paths "
                f"before major work begins. Ask for a written estimate when you call {phone}."
            ),
        },
    ]

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
            for item in faqs
        ],
        "_meta": {
            "business": biz,
            "generated": date.today().isoformat(),
            "mode": "template",
            "note": "Human must verify answers before embedding. Not auto-published.",
        },
    }
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def render_all_templates(cfg: dict[str, Any]) -> dict[str, str]:
    return {
        "blog-draft.md": render_blog_draft(cfg),
        "gbp-posts.md": render_gbp_posts(cfg),
        "faq-schema.json": render_faq_schema(cfg),
    }
