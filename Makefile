.PHONY: pubs serve build

pubs:
	python3 scripts/bib_to_json.py

serve: pubs
	zola serve

build: pubs
	zola build
