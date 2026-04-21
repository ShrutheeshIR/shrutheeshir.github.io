#!/usr/bin/env python3

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment issue
    raise SystemExit("PyYAML is required to generate publication front matter.") from exc


ROOT = Path(__file__).resolve().parents[1]
BIB_DIR = ROOT / "content" / "publication" / "bibfiles"
PUBLICATION_DIR = ROOT / "content" / "publication"


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(character for character in normalized if not unicodedata.combining(character))


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    text = str(value).strip()
    text = re.sub(r"^\{+|\}+$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def slugify(value: str) -> str:
    text = normalize_text(clean_text(value)).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def normalize_lookup(value: str) -> str:
    return slugify(value).replace("-", "")


def parse_front_matter(path: Path) -> tuple[dict, str]:
    if not path.exists():
        return {}, ""

    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not match:
        return {}, content

    front_matter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return front_matter, body


def format_author(name: str) -> str:
    name = clean_text(name)
    if "," in name:
        parts = [part.strip() for part in name.split(",") if part.strip()]
        if len(parts) >= 2:
            first = " ".join(parts[1:])
            last = parts[0]
            return clean_text(f"{first} {last}")
    return name


def parse_authors(author_field: str | list | None) -> list[str]:
    if not author_field:
        return []
    if isinstance(author_field, list):
        authors = author_field
    else:
        authors = re.split(r"\s+and\s+", str(author_field), flags=re.IGNORECASE)
    return [format_author(author) for author in authors if clean_text(author)]


def parse_month(month_value: str | None) -> int | None:
    if not month_value:
        return None
    month_text = clean_text(month_value).lower()
    month_text = re.sub(r"[^a-z]", "", month_text)
    if not month_text:
        return None
    return MONTHS.get(month_text) or MONTHS.get(month_text[:3])


def parse_date(entry: dict) -> str | None:
    year_value = entry.get("year")
    if not year_value:
        return None

    try:
        year = int(str(year_value).strip())
    except ValueError:
        return None

    month = parse_month(entry.get("month")) or 1
    return f"{year:04d}-{month:02d}-01"


def publication_type_id(entry_type: str) -> str:
    entry_type = (entry_type or "").lower()
    if entry_type in {"phdthesis", "mastersthesis", "thesis"}:
        return "7"
    if entry_type == "article":
        return "2"
    return "1"


def derived_publication(entry: dict) -> str:
    entry_type = (entry.get("ENTRYTYPE") or entry.get("entrytype") or "").lower()
    if entry_type == "article":
        return clean_text(entry.get("journal"))
    if entry_type in {"inproceedings", "incollection"}:
        return clean_text(entry.get("booktitle"))
    if entry_type in {"phdthesis", "mastersthesis", "thesis"}:
        return clean_text(entry.get("school"))

    for candidate in ("booktitle", "journal", "school", "note"):
        value = clean_text(entry.get(candidate))
        if value:
          return value
    return ""


def derived_pdf_url(entry: dict) -> str:
    for candidate in ("pdf", "url"):
        value = clean_text(entry.get(candidate))
        if not value:
            continue
        lowered = value.lower()
        if candidate == "pdf":
            return value
        if lowered.endswith(".pdf") or "arxiv.org/pdf" in lowered or "doi/pdf" in lowered:
            return value
    return ""


def derived_project_url(entry: dict) -> str:
    for candidate in ("website", "url_source", "url_project", "project", "homepage"):
        value = clean_text(entry.get(candidate))
        if value:
            return value

    url_value = clean_text(entry.get("url"))
    if not url_value:
        return ""

    lowered = url_value.lower()
    if lowered.endswith(".pdf") or "arxiv.org/pdf" in lowered or "doi/pdf" in lowered:
        return ""
    return url_value


def derived_code_url(entry: dict) -> str:
    for candidate in ("code", "url_code"):
        value = clean_text(entry.get(candidate))
        if value:
            return value
    return ""


def derived_video_url(entry: dict) -> str:
    for candidate in ("video", "url_video"):
        value = clean_text(entry.get(candidate))
        if value:
            return value
    return ""


def title_to_folder_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for index_file in PUBLICATION_DIR.glob("*/index.md"):
        if index_file.parent.name == "bibfiles":
            continue
        front_matter, _ = parse_front_matter(index_file)
        title = clean_text(front_matter.get("title"))
        if title:
            mapping[normalize_lookup(title)] = index_file.parent.name
    return mapping


def folder_from_entry(entry: dict, existing_titles: dict[str, str]) -> str:
    entry_key = clean_text(entry.get("ID") or entry.get("id") or entry.get("key"))
    title = clean_text(entry.get("title"))
    for candidate in (title, entry_key):
        if not candidate:
            continue
        lookup = normalize_lookup(candidate)
        if lookup in existing_titles:
            return existing_titles[lookup]
    return slugify(title or entry_key)


def merge_front_matter(existing: dict, generated: dict) -> dict:
    merged: dict = {}
    preferred_order = [
        "title",
        "date",
        "authors",
        "publication_types",
        "abstract",
        "featured",
        "publication",
        "publication_short",
        "url_project",
        "url_pdf",
        "url_code",
        "url_video",
        "doi",
        "author_notes",
    ]

    for key in preferred_order:
        value = generated.get(key)
        if value not in (None, "", [], {}):
            merged[key] = value

    for key, value in existing.items():
        if key not in merged:
            merged[key] = value

    for key, value in generated.items():
        if key not in merged and value not in (None, "", [], {}):
            merged[key] = value

    return merged


def write_markdown(path: Path, front_matter: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered_front_matter = yaml.safe_dump(
        front_matter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()
    output = f"---\n{rendered_front_matter}\n---\n"
    if body.strip():
        output += body.lstrip("\n")
        if not output.endswith("\n"):
            output += "\n"
    path.write_text(output, encoding="utf-8")


def write_cite_bib(path: Path, entry: dict) -> None:
    database = BibDatabase()
    database.entries = [entry]
    writer = BibTexWriter()
    writer.order_entries_by = ()
    with path.open("w", encoding="utf-8") as handle:
        bibtexparser.dump(database, handle, writer)


def main() -> None:
    source_bibs = sorted(path for path in BIB_DIR.glob("*.bib") if path.name != "publications.bib")
    if not source_bibs:
        raise SystemExit(f"No bib files found in {BIB_DIR}")

    existing_titles = title_to_folder_map()
    parser = bibtexparser.bparser.BibTexParser(common_strings=True)

    merged_entries: list[dict] = []
    generated_entries: list[dict] = []

    for bib_path in source_bibs:
        with bib_path.open(encoding="utf-8") as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file, parser=parser)

        for entry in bib_database.entries:
            if int(entry.get("year", 0) or 0) < 2017:
                continue

            merged_entries.append(entry)

            folder_name = folder_from_entry(entry, existing_titles)
            bundle_dir = PUBLICATION_DIR / folder_name
            index_path = bundle_dir / "index.md"

            existing_front_matter, existing_body = parse_front_matter(index_path)

            generated_front_matter = {
                "title": clean_text(entry.get("title")),
                "date": parse_date(entry),
                "authors": parse_authors(entry.get("author")),
                "publication_types": [publication_type_id(entry.get("ENTRYTYPE", ""))],
                "abstract": clean_text(entry.get("abstract")) if existing_front_matter.get("abstract") else "",
                "featured": existing_front_matter.get("featured", False),
                "publication": clean_text(existing_front_matter.get("publication")) or derived_publication(entry),
                "publication_short": clean_text(existing_front_matter.get("publication_short")),
                "url_project": derived_project_url(entry),
                "url_pdf": derived_pdf_url(entry),
                "url_code": derived_code_url(entry),
                "url_video": derived_video_url(entry),
                "doi": clean_text(entry.get("doi")),
            }

            if existing_front_matter.get("author_notes"):
                generated_front_matter["author_notes"] = existing_front_matter.get("author_notes")

            if existing_front_matter.get("slug"):
                generated_front_matter["slug"] = existing_front_matter.get("slug")

            merged_front_matter = merge_front_matter(existing_front_matter, generated_front_matter)
            write_markdown(index_path, merged_front_matter, existing_body)

            cite_path = bundle_dir / "cite.bib"
            write_cite_bib(cite_path, entry)

            generated_entries.append(entry)

    merged_database = BibDatabase()
    merged_database.entries = merged_entries
    writer = BibTexWriter()
    writer.order_entries_by = ("author",)
    with (BIB_DIR / "publications.bib").open("w", encoding="utf-8") as bibfile:
        bibtexparser.dump(merged_database, bibfile, writer)

    print(f"Generated {len(generated_entries)} publication bundles from {len(source_bibs)} bib file(s).")


if __name__ == "__main__":
    main()