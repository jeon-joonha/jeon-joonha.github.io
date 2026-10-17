#!/usr/bin/env python3
"""
Sync publications from ORCID Public API and write BibTeX entries into _bibliography/papers.bib.
ORCID ID is retrieved from _data/socials.yml.
"""

import os
import sys
import json
import urllib.request
import re

def load_orcid_id():
    config_file = "_data/socials.yml"
    if not os.path.exists(config_file):
        return "0000-0002-8006-6733"
    with open(config_file, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("orcid_id:"):
                val = line.split(":", 1)[1].split("#")[0].strip()
                return val
    return "0000-0002-8006-6733"

def fetch_orcid_works(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return (data or {}).get("group", []) or []
    except Exception as e:
        print(f"Error fetching ORCID works: {e}")
        return []

def fetch_work_detail(orcid_id, put_code):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/work/{put_code}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode()) or {}
    except Exception as e:
        print(f"Error fetching work detail for put-code {put_code}: {e}")
        return None

def generate_bibtex_key(title, year, existing_keys):
    words = re.findall(r'\w+', (title or "").lower())
    first_word = "work"
    for w in words:
        if w not in ["a", "an", "the", "on", "in", "of", "for", "is", "by", "to", "and"]:
            first_word = w
            break
    yr = str(year) if year else "nd"
    base_key = f"jeon{yr}{first_word}"

    key = base_key
    counter = 1
    while key in existing_keys:
        key = f"{base_key}_{counter}"
        counter += 1
    return key

def format_work_to_bibtex(detail, existing_keys):
    title_obj = (detail.get('title') or {}).get('title') or {}
    title = title_obj.get('value', 'Untitled')

    pub_date = detail.get('publication-date') or {}
    year_obj = pub_date.get('year') or {}
    year = year_obj.get('value', '')

    work_type = (detail.get('type') or 'article').lower()

    journal_obj = detail.get('journal-title') or {}
    journal = journal_obj.get('value', '')

    # Contributors / Authors
    contributors_obj = detail.get('contributors') or {}
    contributors = contributors_obj.get('contributor') or []
    author_list = []
    for c in contributors:
        c_name_obj = (c or {}).get('credit-name') or {}
        c_name = c_name_obj.get('value')
        if c_name:
            author_list.append(c_name)
    if not author_list:
        author_list = ["Jeon, Joonha"]
    authors_str = " and ".join(author_list)

    # DOI / URL
    doi = ""
    ext_ids_obj = detail.get('external-ids') or {}
    ext_ids = ext_ids_obj.get('external-id') or []
    for ext_id in ext_ids:
        if (ext_id or {}).get('external-id-type') == 'doi':
            doi = ext_id.get('external-id-value', '')
            break

    entry_type = "article"
    if "conference" in work_type or "proceeding" in work_type:
        entry_type = "inproceedings"
    elif "book" in work_type:
        entry_type = "book"

    bib_key = generate_bibtex_key(title, year, existing_keys)

    bib = f"@{entry_type}{{{bib_key},\n"
    bib += f"  title={{{title}}},\n"
    bib += f"  author={{{authors_str}}},\n"
    if journal:
        bib += f"  journal={{{journal}}},\n"
    if year:
        bib += f"  year={{{year}}},\n"
    if doi:
        bib += f"  doi={{{doi}}},\n"
    bib = bib.rstrip(",\n") + "\n}\n"
    return bib_key, bib

def main():
    orcid_id = load_orcid_id()
    print(f"Syncing publications for ORCID ID: {orcid_id}")
    groups = fetch_orcid_works(orcid_id)
    print(f"Fetched {len(groups)} publication group(s) from ORCID.")

    bib_entries = {}
    seen_titles = set()

    for g in groups:
        try:
            summaries = (g or {}).get('work-summary') or []
            if not summaries:
                continue
            summary = summaries[0] or {}
            put_code = summary.get('put-code')
            if not put_code:
                continue
            detail = fetch_work_detail(orcid_id, put_code)
            if not detail:
                continue

            title_obj = (detail.get('title') or {}).get('title') or {}
            title = title_obj.get('value', '')
            if title.lower() in seen_titles:
                continue
            seen_titles.add(title.lower())

            bib_key, bib_code = format_work_to_bibtex(detail, set(bib_entries.keys()))
            bib_entries[bib_key] = bib_code
        except Exception as e:
            print(f"Warning: Failed to process publication group: {e}")
            continue

    bib_file_path = "_bibliography/papers.bib"
    if bib_entries:
        header = "---\n---\n\n@string{aps = {American Physical Society,}}\n\n"
        with open(bib_file_path, "w") as f:
            f.write(header)
            for k, code in bib_entries.items():
                f.write(code + "\n")
        print(f"Updated {bib_file_path} with {len(bib_entries)} entry/entries from ORCID.")

if __name__ == "__main__":
    main()
