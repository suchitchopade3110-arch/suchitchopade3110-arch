#!/usr/bin/env python3
"""Fetch the last year of contributions into data/contributions.json.

Uses the GitHub GraphQL API. Inside GitHub Actions the built-in GITHUB_TOKEN
is enough; locally, export a personal token as GITHUB_TOKEN first.
If the request fails the old file is kept, so the cards never go blank.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"
LOGIN = json.loads((ROOT / "data" / "profile.json").read_text())["login"]

QUERY = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-cards"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            payload = json.load(r)
        cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    except Exception as e:  # keep the last good data
        print(f"warning: fetch failed ({e}); keeping existing {OUT.name}")
        return
    days = {d["date"]: d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"] if d["contributionCount"]}
    last = max(d["date"] for w in cal["weeks"] for d in w["contributionDays"])
    OUT.write_text(json.dumps({"login": LOGIN, "fetched": last, "total": cal["totalContributions"], "days": days}, indent=1) + "\n")
    print(f"{cal['totalContributions']} contributions, {len(days)} active days, up to {last}")


if __name__ == "__main__":
    main()
