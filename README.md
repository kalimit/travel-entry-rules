---
license: cc-by-4.0
pretty_name: Declaroad travel entry rules and visa table
language: [en, ru, de, fr, es]
tags: [travel, visa, customs, immigration, law]
size_categories: [n<1K]
configs:
  - config_name: visas
    data_files: data/visas.csv
    default: true
  - config_name: rules
    data_files: data/rules/en.jsonl
---

# Declaroad: travel entry rules and visa table

What a traveller needs to know before crossing a border, with the official
source of every entry: visa regimes, customs and cash limits, medicines,
drones, registration, local laws that carry fines or prison.

Copied every night from [declaroad.com](https://declaroad.com/en), where each
pair of destination and passport has its own page.

## Files

| File | What |
|---|---|
| `data/visas.csv` | one row per destination and passport: status, maximum stay, source, date checked |
| `data/visas/{lang}.jsonl` | the same pairs, with the label and a short explanation (`note`, absent where none is written in that language) in en, ru, de, fr or es; named as in the API (`country` for the destination, `days`, `change` as an object) |
| `data/rules/{lang}.jsonl` | every rule the site shows: customs, currency, medication, drones, registration, conduct… |
| `data/VERSION` | the ruleset version the files were copied from |

Visa `status` is one of `visa_free`, `visa_on_arrival`, `evisa` (an eVisa or an
electronic travel authorisation such as ESTA or K-ETA) and `visa_required`
(a visa obtained in advance). `max_stay_days` is empty when no limit is
confirmed. `change_from` and `change_label` announce a status change within the
next 90 days.

A rule has its official `source` (address, type, and the date of the act where
known; `corroboration` lists secondary pages that say the same), `verified_at`, a
`severity` from 1 to 5 and an `enforcement`: what follows a breach (`none`,
`fine`, `confiscation`, `entry_refusal`, `deportation`, `criminal` and others). `predicate` says whom it concerns: items carried, purpose of the
trip, length of stay, passports.

## How it is made and how far to trust it

The rules are found and written by language models from official sources
(government and regulator pages, laws), then checked automatically: a second
model reads the source again, and a rule the source no longer supports is
marked and then removed. A pair marked `unverified` rests on secondary data
whose official source is not yet confirmed.

It covers the destinations and passports the site keeps (see
[the API](https://declaroad.com/v1/meta)), not the whole world. It is a
reference, not legal advice: check the source before you rely on a rule.

## Licence and attribution

[CC BY 4.0](LICENSE). Please credit **Declaroad** with a link to
https://declaroad.com.

The live data is also available as a JSON API (`https://declaroad.com/v1/meta`) and
as an MCP server for AI assistants (`https://declaroad.com/mcp`, POST only; how to call both is in `https://declaroad.com/llms.txt`).

