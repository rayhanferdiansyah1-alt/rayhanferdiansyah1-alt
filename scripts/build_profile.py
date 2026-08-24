#!/usr/bin/env python3
"""Build a dependency-free SVG dashboard from GitHub's API."""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "live-dashboard.svg"
USERNAME = os.getenv("PROFILE_USERNAME") or os.getenv("GITHUB_REPOSITORY_OWNER") or "rayhanferdiansyah1-alt"
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or ""


def request_json(url: str, *, token: str = "", body: dict | None = None) -> dict | list:
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "rayhan-profile-dashboard",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=payload, headers=headers, method="POST" if body is not None else "GET")
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def graphql_data() -> dict:
    if not TOKEN:
        raise RuntimeError("GH_TOKEN is unavailable")

    now = datetime.now(timezone.utc)
    query = """
    query Profile($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: [OWNER], privacy: PUBLIC, isFork: false) {
          totalCount
          nodes {
            stargazerCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges { size node { name color } }
            }
          }
        }
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar { totalContributions }
        }
      }
    }
    """
    payload = {
        "query": query,
        "variables": {
            "login": USERNAME,
            "from": f"{now.year}-01-01T00:00:00Z",
            "to": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }
    response = request_json("https://api.github.com/graphql", token=TOKEN, body=payload)
    if not isinstance(response, dict) or response.get("errors"):
        raise RuntimeError(f"GraphQL request failed: {response.get('errors', 'unknown response')}")

    user = response["data"]["user"]
    repos = user["repositories"]
    language_totals: dict[str, int] = defaultdict(int)
    language_colors: dict[str, str] = {}
    stars = 0
    for repo in repos["nodes"]:
        stars += int(repo["stargazerCount"] or 0)
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            language_totals[name] += int(edge["size"] or 0)
            language_colors[name] = edge["node"].get("color") or "#64748b"

    return {
        "repositories": int(repos["totalCount"]),
        "stars": stars,
        "followers": int(user["followers"]["totalCount"]),
        "contributions": int(user["contributionsCollection"]["contributionCalendar"]["totalContributions"]),
        "languages": normalize_languages(language_totals, language_colors),
        "year": now.year,
        "source": "GitHub GraphQL API",
    }


def rest_fallback() -> dict:
    user = request_json(f"https://api.github.com/users/{USERNAME}", token=TOKEN)
    repos = request_json(f"https://api.github.com/users/{USERNAME}/repos?type=owner&sort=updated&per_page=100", token=TOKEN)
    if not isinstance(user, dict) or not isinstance(repos, list):
        raise RuntimeError("Unexpected REST response")

    language_totals: dict[str, int] = defaultdict(int)
    language_colors = {
        "PHP": "#4F5D95",
        "JavaScript": "#f1e05a",
        "HTML": "#e34c26",
        "CSS": "#663399",
        "Python": "#3572A5",
        "Blade": "#f7523f",
        "Shell": "#89e051",
    }
    owned = [repo for repo in repos if not repo.get("fork")]
    for repo in owned:
        language = repo.get("language")
        if language:
            language_totals[language] += max(int(repo.get("size") or 1), 1)

    return {
        "repositories": len(owned),
        "stars": sum(int(repo.get("stargazers_count") or 0) for repo in owned),
        "followers": int(user.get("followers") or 0),
        "contributions": None,
        "languages": normalize_languages(language_totals, language_colors),
        "year": datetime.now(timezone.utc).year,
        "source": "GitHub REST API",
    }


def normalize_languages(totals: dict[str, int], colors: dict[str, str]) -> list[dict]:
    total = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:5]
    return [
        {
            "name": name,
            "percent": round(value / total * 100, 1),
            "color": colors.get(name, "#64748b"),
        }
        for name, value in ranked
    ]


def fixture_data() -> dict | None:
    raw = os.getenv("PROFILE_DATA_JSON")
    if not raw:
        return None
    if raw.lstrip().startswith(("{", "[")):
        return json.loads(raw)
    candidate = Path(raw)
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(raw)


def safe(value: object) -> str:
    return html.escape(str(value), quote=True)


def metric_card(x: int, label: str, value: object, accent: str) -> str:
    return f"""
    <g transform="translate({x} 72)">
      <rect width="216" height="96" rx="16" class="card"/>
      <rect width="4" height="96" rx="2" fill="{accent}"/>
      <text x="22" y="31" class="label">{safe(label)}</text>
      <text x="22" y="70" class="value">{safe(value)}</text>
    </g>"""


def build_svg(data: dict) -> str:
    languages = data.get("languages") or []
    if not languages:
        languages = [{"name": "Building data", "percent": 100, "color": "#2dd4bf"}]

    metrics = [
        ("PUBLIC REPOS", data.get("repositories", 0), "#2dd4bf"),
        ("STARS EARNED", data.get("stars", 0), "#60a5fa"),
        ("FOLLOWERS", data.get("followers", 0), "#a78bfa"),
        (f"CONTRIBUTIONS {data.get('year', '')}", data.get("contributions") if data.get("contributions") is not None else "—", "#fbbf24"),
    ]
    cards = "".join(metric_card(28 + index * 236, label, value, accent) for index, (label, value, accent) in enumerate(metrics))

    bar_x = 180
    bar_width = 735
    rows = []
    for index, language in enumerate(languages):
        y = 216 + index * 29
        percent = max(0.0, min(float(language.get("percent", 0)), 100.0))
        width = round(bar_width * percent / 100, 1)
        rows.append(
            f"""
            <text x="28" y="{y + 11}" class="language">{safe(language.get('name', 'Unknown'))}</text>
            <rect x="{bar_x}" y="{y}" width="{bar_width}" height="12" rx="6" class="track"/>
            <rect x="{bar_x}" y="{y}" width="{width}" height="12" rx="6" fill="{safe(language.get('color') or '#64748b')}"/>
            <text x="972" y="{y + 11}" text-anchor="end" class="percent">{percent:.1f}%</text>"""
        )

    updated = datetime.now(timezone.utc).strftime("%d %b %Y · %H:%M UTC")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390" role="img" aria-labelledby="title desc">
  <title id="title">GitHub engineering signal for {safe(USERNAME)}</title>
  <desc id="desc">Public repositories, stars, followers, yearly contributions, and top languages.</desc>
  <style>
    .surface {{ fill: #0b1220; stroke: #25324a; }}
    .card {{ fill: #111b2e; stroke: #25324a; }}
    .title {{ fill: #f8fafc; font: 700 18px Inter,Segoe UI,Arial,sans-serif; }}
    .subtitle,.label,.percent,.footer {{ fill: #8da2bf; font-family: Inter,Segoe UI,Arial,sans-serif; }}
    .subtitle {{ font-size: 12px; }} .label {{ font-size: 11px; font-weight: 700; letter-spacing: 1px; }}
    .value {{ fill: #f8fafc; font: 800 30px Inter,Segoe UI,Arial,sans-serif; }}
    .language {{ fill: #dbe7f6; font: 600 13px Inter,Segoe UI,Arial,sans-serif; }}
    .percent {{ font-size: 12px; }} .footer {{ font-size: 10px; }} .track {{ fill: #1e293b; }}
    @media (prefers-color-scheme: light) {{
      .surface {{ fill: #f8fafc; stroke: #d8e0eb; }} .card {{ fill: #ffffff; stroke: #d8e0eb; }}
      .title,.value {{ fill: #0f172a; }} .subtitle,.label,.percent,.footer {{ fill: #64748b; }}
      .language {{ fill: #24324a; }} .track {{ fill: #e5eaf1; }}
    }}
  </style>
  <rect x="1" y="1" width="998" height="388" rx="20" class="surface"/>
  <text x="28" y="34" class="title">LIVE ENGINEERING SIGNAL</text>
  <text x="972" y="34" text-anchor="end" class="subtitle">SELF-UPDATING · NO THIRD-PARTY STATS SERVICE</text>
  {cards}
  <text x="28" y="199" class="label">LANGUAGE DISTRIBUTION ACROSS OWNED PUBLIC REPOSITORIES</text>
  {''.join(rows)}
  <text x="28" y="370" class="footer">Source: {safe(data.get('source', 'GitHub API'))}</text>
  <text x="972" y="370" text-anchor="end" class="footer">Updated {safe(updated)}</text>
</svg>
"""


def main() -> int:
    data = fixture_data()
    if data is None:
        try:
            data = graphql_data()
        except (RuntimeError, KeyError, TypeError, urllib.error.URLError) as graphql_error:
            print(f"GraphQL unavailable ({graphql_error}); using REST fallback.", file=sys.stderr)
            data = rest_fallback()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_svg(data), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
