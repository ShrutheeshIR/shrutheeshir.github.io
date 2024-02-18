#!/usr/bin/env python3

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase
import os
import glob

complete_entries = []
all_bibs = glob.glob('content/publications/bibfiles/*.bib')

for filename in all_bibs:

    parser = bibtexparser.bparser.BibTexParser(common_strings=True)
    with open(filename, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

    filename = os.path.basename(filename)
    if filename == 'publications.bib':
        continue
    entries = bib_database.entries

    for entry in entries:
        if('conf-papers' in filename):
            entry['category'] = 'Conference'
        elif 'thesis' in filename:
            entry['category'] = 'Thesis'
        elif ('articles' in filename) or ('journal-issues' in filename):
            entry['category'] = 'Journal'
        elif('reports' in filename):
            entry['category'] = 'Report'
        else:
            print("Unknown filename! ", filename)
            break

    complete_entries.extend(entries)

output_entries = []
for entry in complete_entries:
    if int(entry['year']) >= 2017:
        output_entries.append(entry)

db = BibDatabase()
db.entries = output_entries

writer = BibTexWriter()
writer.order_entries_by = ('author')



with open('content/publications/bibfiles/publications.bib', 'w', encoding='utf-8') as bibfile:
    bibtexparser.dump(db, bibfile, writer)