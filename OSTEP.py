#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from pathlib import Path
from pypdf import PdfWriter, PdfReader

BASE_PAGE = "https://pages.cs.wisc.edu/~remzi/OSTEP/"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def get_chapter_links():
    print("Fetching chapter list...")
    resp = requests.get(BASE_PAGE)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    chapters = {}

    for td in soup.find_all("td"):
        small_tag = td.find("small")
        link_tag = td.find("a")

        if not small_tag or not link_tag:
            continue

        try:
            chapter_num = int(small_tag.get_text().strip())
        except ValueError:
            continue

        href = link_tag.get("href")
        if href and href.endswith(".pdf"):
            chapters[chapter_num] = BASE_PAGE + href

    return dict(sorted(chapters.items()))


def download_chapters(chapters):
    print("Downloading chapters...")
    for num, url in chapters.items():
        filename = OUTPUT_DIR / f"{num:02d}-{url.split('/')[-1]}"
        if filename.exists():
            print(f"Skipping {filename.name} (already exists)")
            continue

        print(f"Downloading {filename.name}")
        r = requests.get(url, timeout=60)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)


def merge_pdfs():
    print("Merging PDFs...")

    writer = PdfWriter()
    pdf_files = sorted(OUTPUT_DIR.glob("*.pdf"))

    for pdf in pdf_files:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)

    with open("OSTEP-Book.pdf", "wb") as f:
        writer.write(f)

    print("Merged into OSTEP-Book.pdf")

def main():
    chapters = get_chapter_links()
    download_chapters(chapters)
    merge_pdfs()


if __name__ == "__main__":
    main()
