#!/usr/bin/env python3
"""Convert publications.bib into data/publications.json for Zola.

No third-party dependencies -- run with any python3.
Re-run whenever publications.bib changes (see `just pubs` / the deploy workflow).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB_PATH = ROOT / "publications.bib"
OUT_PATH = ROOT / "data" / "publications.json"


def strip_comment_lines(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("%")
    )


def find_matching_brace(text: str, open_idx: int) -> int:
    """Given the index of a '{', return the index of its matching '}'."""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f"Unbalanced braces starting at {open_idx}")


def split_top_level(body: str) -> list[str]:
    """Split a bib entry body on top-level commas (ignoring commas inside {} or "")."""
    parts = []
    depth = 0
    in_quotes = False
    current = []
    for ch in body:
        if ch == '"' and depth == 0:
            in_quotes = not in_quotes
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == "," and depth == 0 and not in_quotes:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if "".join(current).strip():
        parts.append("".join(current))
    return parts


def parse_value(raw: str, strings: dict) -> str:
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        return raw[1:-1].strip()
    if raw.startswith('"') and raw.endswith('"'):
        return raw[1:-1].strip()
    # bare token: a number, or an @string macro reference
    if raw in strings:
        return strings[raw]
    return raw


def parse_bib(text: str):
    text = strip_comment_lines(text)
    strings: dict[str, str] = {}
    entries = []

    i = 0
    while True:
        at = text.find("@", i)
        if at == -1:
            break
        brace_open = text.find("{", at)
        entry_type = text[at + 1 : brace_open].strip().lower()
        brace_close = find_matching_brace(text, brace_open)
        body = text[brace_open + 1 : brace_close]
        i = brace_close + 1

        if entry_type == "string":
            name, _, value = body.partition("=")
            strings[name.strip().lower()] = parse_value(value, strings)
            continue

        parts = split_top_level(body)
        if not parts:
            continue
        citekey = parts[0].strip()
        fields = {"entry_type": entry_type, "key": citekey}
        for part in parts[1:]:
            if "=" not in part:
                continue
            name, _, value = part.partition("=")
            fields[name.strip().lower()] = parse_value(value, strings)
        entries.append(fields)

    return entries


def to_record(fields: dict) -> dict:
    authors = [a.strip() for a in re.split(r"\s+and\s+", fields.get("author", "")) if a.strip()]
    venue = fields.get("booktitle") or fields.get("journal") or fields.get("school") or ""
    projects = [p.strip() for p in fields.get("projects", "").split(",") if p.strip()]

    year_raw = fields.get("year", "0")
    try:
        year = int(re.sub(r"[^0-9]", "", year_raw) or 0)
    except ValueError:
        year = 0

    return {
        "key": fields["key"],
        "entry_type": fields["entry_type"],
        "title": fields.get("title", ""),
        "authors": authors,
        "year": year,
        "venue": venue,
        "note": fields.get("note", ""),
        "abstract": fields.get("abstract", ""),
        "pdf": fields.get("pdf", ""),
        "code": fields.get("code", ""),
        "video": fields.get("video", ""),
        "website": fields.get("website", ""),
        "doi": fields.get("doi", ""),
        "abbr": fields.get("abbr", ""),
        "preview": fields.get("preview", ""),
        "projects": projects,
    }


def main():
    if not BIB_PATH.exists():
        print(f"error: {BIB_PATH} not found", file=sys.stderr)
        sys.exit(1)

    entries = parse_bib(BIB_PATH.read_text())
    records = [to_record(e) for e in entries]
    records.sort(key=lambda r: r["year"], reverse=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(records, indent=2) + "\n")
    print(f"wrote {len(records)} publications to {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
