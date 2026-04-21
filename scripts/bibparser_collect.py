#!/usr/bin/env python3

from __future__ import annotations

import re
import unicodedata
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
BIB_SOURCE = BIB_DIR / "publications.bib"


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


def parse_notes(note_field: str | list | None) -> list[str]:
    if not note_field:
        return []
    if isinstance(note_field, list):
        notes = note_field
    else:
        notes = re.split(r"\s*,\s*", str(note_field))
    return [clean_text(note) for note in notes if clean_text(note)]


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


def resolve_bib_string(value: str | None, string_map: dict[str, str] | None = None) -> str:
    cleaned_value = clean_text(value)
    if not cleaned_value:
        return ""
    if not string_map:
        return cleaned_value
    return string_map.get(cleaned_value.lower(), cleaned_value)


def derived_publication(entry: dict, string_map: dict[str, str] | None = None) -> str:
    entry_type = (entry.get("ENTRYTYPE") or entry.get("entrytype") or "").lower()
    if entry_type == "article":
        return resolve_bib_string(entry.get("journal"), string_map)
    if entry_type in {"inproceedings", "incollection"}:
        return resolve_bib_string(entry.get("booktitle"), string_map)
    if entry_type in {"phdthesis", "mastersthesis", "thesis"}:
        return resolve_bib_string(entry.get("school"), string_map)

    for candidate in ("booktitle", "journal", "school"):
        value = clean_text(entry.get(candidate))
        if value:
            return resolve_bib_string(value, string_map)
    return ""


def derived_preview(entry: dict) -> str:
    return clean_text(entry.get("preview"))


def derived_note(entry: dict) -> str:
    return clean_text(entry.get("note"))


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


def folder_from_entry(entry: dict) -> str:
    slug_value = clean_text(entry.get("slug"))
    if slug_value:
        return slugify(slug_value)

    entry_key = clean_text(entry.get("ID") or entry.get("id") or entry.get("key"))
    title = clean_text(entry.get("title"))
    return slugify(entry_key or title)


def write_markdown(path: Path, front_matter: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered_front_matter = yaml.safe_dump(
        front_matter,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    ).strip()
    path.write_text(f"---\n{rendered_front_matter}\n---\n", encoding="utf-8")


def write_cite_bib(path: Path, entry: dict) -> None:
    database = BibDatabase()
    database.entries = [entry]
    writer = BibTexWriter()
    writer.order_entries_by = ()
    with path.open("w", encoding="utf-8") as handle:
        bibtexparser.dump(database, handle, writer)


def main() -> None:
    if not BIB_SOURCE.exists():
        raise SystemExit(f"Missing source bibliography: {BIB_SOURCE}")

    parser = bibtexparser.bparser.BibTexParser(common_strings=True)

    with BIB_SOURCE.open(encoding="utf-8") as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    string_map = {
        key.lower(): clean_text(value)
        for key, value in getattr(bib_database, "strings", {}).items()
        if clean_text(value)
    }

    generated_entries: list[dict] = []

    for index, entry in enumerate(bib_database.entries):
        if int(entry.get("year", 0) or 0) < 2017:
            continue

        year_value = int(str(entry.get("year", 0) or 0).strip())
        weight_value = -(year_value * 1000) + index

        folder_name = folder_from_entry(entry)
        bundle_dir = PUBLICATION_DIR / folder_name
        index_path = bundle_dir / "index.md"

        generated_front_matter = {
            "title": clean_text(entry.get("title")),
            "date": parse_date(entry),
            "authors": parse_authors(entry.get("author")),
            "publication_types": [publication_type_id(entry.get("ENTRYTYPE", ""))],
            "abstract": "",
            "featured": False,
            "publication": derived_publication(entry, string_map),
            "publication_short": clean_text(entry.get("publication_short")),
            "note": derived_note(entry),
            "weight": weight_value,
            "url_project": derived_project_url(entry),
            "url_pdf": derived_pdf_url(entry),
            "url_code": derived_code_url(entry),
            "url_video": derived_video_url(entry),
            "doi": clean_text(entry.get("doi")),
            "preview": derived_preview(entry),
        }

        author_notes = parse_notes(entry.get("author_notes"))
        if author_notes:
            generated_front_matter["author_notes"] = author_notes

        if clean_text(entry.get("slug")):
            generated_front_matter["slug"] = slugify(entry.get("slug"))

        write_markdown(index_path, generated_front_matter)

        cite_path = bundle_dir / "cite.bib"
        write_cite_bib(cite_path, entry)

        generated_entries.append(entry)

    print(f"Generated {len(generated_entries)} publication bundles from {BIB_SOURCE.name}.")


if __name__ == "__main__":
    main()