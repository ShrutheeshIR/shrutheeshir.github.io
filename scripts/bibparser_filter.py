#!/usr/bin/env python3

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


filename = 'publications.bib'
parser = bibtexparser.bparser.BibTexParser(common_strings=True)
with open(filename, encoding='utf-8') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file, parser=parser)

entries = bib_database.entries
out_entries = []
for entry in entries:
    print(entry, dir(entry))


db = BibDatabase()
db.entries = complete_entries

writer = BibTexWriter()
writer.order_entries_by = ('author')

with open('publications.bib', 'w', encoding='utf-8') as bibfile:
    bibtexparser.dump(db, bibfile, writer)