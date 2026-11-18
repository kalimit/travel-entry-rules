"""Copy the Declaroad visa table and entry rules into data/.

Run nightly by .github/workflows/sync.yml. Standard library only.
Writes:
  data/visas.csv            one row per destination and passport (English)
  data/visas/{lang}.jsonl   the same with the explanation in each language
  data/rules/{lang}.jsonl   every rule in force, once each, in each language
  data/VERSION              the ruleset version the files were copied from
"""

import csv
import json
import os
import time
import urllib.request

API = os.environ.get("DECLAROAD_API", "https://declaroad.com")
HEADERS = {"User-Agent": "declaroad-dataset-sync", "Accept": "application/json"}


def fetch(path):
    for attempt in range(4):
        try:
            req = urllib.request.Request(API + path, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


VERSION = None


def get(path):
    """Fetch, and refuse an answer from another ruleset than the run began on:
    a copy mixing two versions under one VERSION would be wrong without a
    trace. The job fails, nothing is committed, and the next night retries."""
    body = fetch(path)
    if body["ruleset_version"] != VERSION:
        raise SystemExit(f"the data changed during the copy ({VERSION} -> {body['ruleset_version']}); try again later")
    return body


def write_jsonl(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    global VERSION
    meta = fetch("/v1/meta")
    VERSION = meta["ruleset_version"]
    langs = meta["content_languages"]
    countries = [c["code"] for c in meta["countries"] if c["has_rules"]]

    for lang in langs:
        visas = get(f"/v1/visas?lang={lang}")["visas"]
        for v in visas:
            v.pop("known", None)
        write_jsonl(f"data/visas/{lang}.jsonl", visas)
        if lang == "en":
            with open("data/visas.csv", "w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["destination", "passport", "status", "max_stay_days", "label",
                            "source_url", "verified_at", "unverified", "change_from", "change_label"])
                for v in visas:
                    ch = v.get("change") or {}
                    w.writerow([v["country"], v["passport"], v["status"], v.get("days") or "",
                                v["label"], v.get("source_url", ""), v.get("verified_at", ""),
                                "yes" if v.get("unverified") else "", ch.get("from", ""), ch.get("label", "")])

        # A union's rule (Schengen, EAEU) is served with each member country;
        # the dataset keeps it once.
        rules = {}
        for cc in countries:
            for r in get(f"/v1/countries/{cc}/rules?lang={lang}")["rules"]:
                rules[r["id"]] = r
            time.sleep(0.2)
        write_jsonl(f"data/rules/{lang}.jsonl", sorted(rules.values(), key=lambda r: r["id"]))

    with open("data/VERSION", "w") as f:
        f.write(VERSION + "\n")


if __name__ == "__main__":
    main()
