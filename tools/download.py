# import os
# import json
# import csv
# import hashlib
# from datetime import datetime
# from urllib.request import Request, urlopen
# from urllib.error import URLError, HTTPError


# # ============================================================
# # CONFIGURATION
# # ============================================================

# BASE_DIR = os.path.dirname(
#     os.path.dirname(os.path.abspath(__file__))
# )

# DATA_DIR = os.path.join(
#     BASE_DIR,
#     "data"
# )

# RAW_DIR = os.path.join(
#     DATA_DIR,
#     "raw"
# )

# CATALOG_FILE = os.path.join(
#     RAW_DIR,
#     "NIST_SP-800-53_rev5_catalog.json"
# )

# CONTROLS_FILE = os.path.join(
#     DATA_DIR,
#     "controls.json"
# )

# MANIFEST_FILE = os.path.join(
#     DATA_DIR,
#     "manifest.csv"
# )

# # Official NIST OSCAL repository
# CATALOG_URL = (
#     "https://raw.githubusercontent.com/"
#     "usnistgov/oscal-content/main/"
#     "nist.gov/SP800-53/rev5/json/"
#     "NIST_SP-800-53_rev5_catalog.json"
# )


# # ============================================================
# # CREATE DIRECTORIES
# # ============================================================

# def create_directories():

#     os.makedirs(
#         DATA_DIR,
#         exist_ok=True
#     )

#     os.makedirs(
#         RAW_DIR,
#         exist_ok=True
#     )


# # ============================================================
# # DOWNLOAD FILE
# # ============================================================

# def download_catalog():

#     print()
#     print("=" * 70)
#     print("DOWNLOADING NIST SP 800-53 REV 5 CATALOG")
#     print("=" * 70)

#     print()
#     print("Source:")
#     print(CATALOG_URL)

#     print()
#     print("Destination:")
#     print(CATALOG_FILE)

#     request = Request(
#         CATALOG_URL,
#         headers={
#             "User-Agent":
#                 "ControlMap/1.0 Educational Project"
#         }
#     )

#     try:

#         with urlopen(
#             request,
#             timeout=60
#         ) as response:

#             data = response.read()

#         with open(
#             CATALOG_FILE,
#             "wb"
#         ) as file:

#             file.write(data)

#         print()
#         print("[SUCCESS] Catalog downloaded")

#         print(
#             f"[SIZE] {len(data):,} bytes"
#         )

#         return data

#     except HTTPError as e:

#         print()
#         print(
#             f"[ERROR] HTTP error: {e.code}"
#         )

#         return None

#     except URLError as e:

#         print()
#         print(
#             f"[ERROR] URL error: {e.reason}"
#         )

#         return None

#     except Exception as e:

#         print()
#         print(
#             f"[ERROR] {e}"
#         )

#         return None


# # ============================================================
# # CALCULATE SHA256
# # ============================================================

# def calculate_sha256(data):

#     return hashlib.sha256(
#         data
#     ).hexdigest()


# # ============================================================
# # LOAD CATALOG
# # ============================================================

# def load_catalog():

#     print()
#     print("=" * 70)
#     print("LOADING CATALOG")
#     print("=" * 70)

#     try:

#         with open(
#             CATALOG_FILE,
#             "r",
#             encoding="utf-8"
#         ) as file:

#             catalog = json.load(file)

#         print(
#             "[SUCCESS] JSON loaded successfully"
#         )

#         return catalog

#     except json.JSONDecodeError as e:

#         print()
#         print(
#             f"[ERROR] Invalid JSON: {e}"
#         )

#         return None

#     except Exception as e:

#         print()
#         print(
#             f"[ERROR] {e}"
#         )

#         return None


# # ============================================================
# # GET PROPERTY
# # ============================================================

# def get_property(properties, name):

#     for prop in properties:

#         if prop.get("name") == name:

#             return prop.get(
#                 "value",
#                 ""
#             )

#     return ""


# # ============================================================
# # EXTRACT TEXT FROM PARTS
# # ============================================================

# def extract_part_text(parts):

#     text = []

#     for part in parts:

#         prose = part.get(
#             "prose",
#             ""
#         )

#         if prose:

#             text.append(
#                 prose
#             )

#         nested_parts = part.get(
#             "parts",
#             []
#         )

#         if nested_parts:

#             text.extend(
#                 extract_part_text(
#                     nested_parts
#                 )
#             )

#     return text


# # ============================================================
# # EXTRACT CONTROLS
# # ============================================================

# def extract_controls(catalog):

#     print()
#     print("=" * 70)
#     print("EXTRACTING CONTROLS")
#     print("=" * 70)

#     controls = []

#     groups = catalog.get(
#         "catalog",
#         {}
#     ).get(
#         "groups",
#         []
#     )

#     print(
#         f"[INFO] Groups found: {len(groups)}"
#     )

#     for group in groups:

#         group_id = group.get(
#             "id",
#             ""
#         )

#         group_title = group.get(
#             "title",
#             ""
#         )

#         print()
#         print(
#             f"[GROUP] {group_id.upper()} - "
#             f"{group_title}"
#         )

#         group_controls = group.get(
#             "controls",
#             []
#         )

#         print(
#             f"Controls: {len(group_controls)}"
#         )

#         for control in group_controls:

#             control_id = control.get(
#                 "id",
#                 ""
#             )

#             title = control.get(
#                 "title",
#                 ""
#             )

#             properties = control.get(
#                 "props",
#                 []
#             )

#             label = get_property(
#                 properties,
#                 "label"
#             )

#             parts = control.get(
#                 "parts",
#                 []
#             )

#             statements = extract_part_text(
#                 parts
#             )

#             control_text = " ".join(
#                 statements
#             )

#             parameters = control.get(
#                 "params",
#                 []
#             )

#             related_controls = control.get(
#                 "links",
#                 []
#             )

#             control_data = {

#                 "control_id":
#                     control_id.upper(),

#                 "group_id":
#                     group_id.upper(),

#                 "group_title":
#                     group_title,

#                 "title":
#                     title,

#                 "label":
#                     label,

#                 "statement":
#                     control_text,

#                 "parameters":
#                     parameters,

#                 "related_controls":
#                     related_controls,

#                 "raw":
#                     control
#             }

#             controls.append(
#                 control_data
#             )

#             # ------------------------------------------------
#             # DISPLAY PROGRESS
#             # ------------------------------------------------

#             print(
#                 f"  ✓ {control_id.upper()} - {title}"
#             )

#     return controls


# # ============================================================
# # SAVE CONTROLS
# # ============================================================

# def save_controls(controls):

#     print()
#     print("=" * 70)
#     print("SAVING STRUCTURED CONTROLS")
#     print("=" * 70)

#     with open(
#         CONTROLS_FILE,
#         "w",
#         encoding="utf-8"
#     ) as file:

#         json.dump(
#             controls,
#             file,
#             indent=2,
#             ensure_ascii=False
#         )

#     print()
#     print(
#         f"[SUCCESS] Saved {len(controls)} controls"
#     )

#     print(
#         f"[FILE] {CONTROLS_FILE}"
#     )


# # ============================================================
# # SAVE MANIFEST
# # ============================================================

# def save_manifest(
#     data,
#     controls
# ):

#     sha256 = calculate_sha256(
#         data
#     )

#     file_exists = os.path.exists(
#         MANIFEST_FILE
#     )

#     with open(
#         MANIFEST_FILE,
#         "a",
#         newline="",
#         encoding="utf-8"
#     ) as file:

#         writer = csv.writer(file)

#         if not file_exists:

#             writer.writerow([
#                 "file",
#                 "source_url",
#                 "download_date",
#                 "size",
#                 "sha256",
#                 "control_count"
#             ])

#         writer.writerow([
#             os.path.basename(
#                 CATALOG_FILE
#             ),

#             CATALOG_URL,

#             datetime.now().isoformat(),

#             len(data),

#             sha256,

#             len(controls)
#         ])

#     print()
#     print(
#         f"[SUCCESS] Manifest updated"
#     )


# # ============================================================
# # CREATE SEARCH DATA
# # ============================================================

# def create_search_data(controls):

#     print()
#     print("=" * 70)
#     print("CREATING SEARCH DATA")
#     print("=" * 70)

#     search_data = []

#     for control in controls:

#         search_text = (
#             control.get(
#                 "control_id",
#                 ""
#             )
#             + " "
#             + control.get(
#                 "title",
#                 ""
#             )
#             + " "
#             + control.get(
#                 "statement",
#                 ""
#             )
#         )

#         search_item = {

#             "control_id":
#                 control.get(
#                     "control_id",
#                     ""
#                 ),

#             "group_id":
#                 control.get(
#                     "group_id",
#                     ""
#                 ),

#             "title":
#                 control.get(
#                     "title",
#                     ""
#                 ),

#             "statement":
#                 control.get(
#                     "statement",
#                     ""
#                 ),

#             "search_text":
#                 search_text
#         }

#         search_data.append(
#             search_item
#         )

#     search_file = os.path.join(
#         DATA_DIR,
#         "search_data.json"
#     )

#     with open(
#         search_file,
#         "w",
#         encoding="utf-8"
#     ) as file:

#         json.dump(
#             search_data,
#             file,
#             indent=2,
#             ensure_ascii=False
#         )

#     print(
#         f"[SUCCESS] Search data created"
#     )

#     print(
#         f"[FILE] {search_file}"
#     )


# # ============================================================
# # PRINT SUMMARY
# # ============================================================

# def print_summary(
#     catalog,
#     controls
# ):

#     metadata = catalog.get(
#         "catalog",
#         {}
#     ).get(
#         "metadata",
#         {}
#     )

#     print()
#     print()
#     print("=" * 70)
#     print("CONTROLMap DATA DOWNLOAD COMPLETE")
#     print("=" * 70)

#     print()

#     print(
#         "Title:"
#     )

#     print(
#         metadata.get(
#             "title",
#             "N/A"
#         )
#     )

#     print()

#     print(
#         "Version:"
#     )

#     print(
#         metadata.get(
#             "version",
#             "N/A"
#         )
#     )

#     print()

#     print(
#         "OSCAL Version:"
#     )

#     print(
#         metadata.get(
#             "oscal-version",
#             "N/A"
#         )
#     )

#     print()

#     print(
#         "Total Groups:"
#     )

#     groups = catalog.get(
#         "catalog",
#         {}
#     ).get(
#         "groups",
#         []
#     )

#     print(
#         len(groups)
#     )

#     print()

#     print(
#         "Total Controls:"
#     )

#     print(
#         len(controls)
#     )

#     print()

#     print(
#         "Raw Catalog:"
#     )

#     print(
#         CATALOG_FILE
#     )

#     print()

#     print(
#         "Structured Controls:"
#     )

#     print(
#         CONTROLS_FILE
#     )

#     print()

#     print(
#         "Search Data:"
#     )

#     print(
#         os.path.join(
#             DATA_DIR,
#             "search_data.json"
#         )
#     )

#     print()

#     print(
#         "Manifest:"
#     )

#     print(
#         MANIFEST_FILE
#     )

#     print()

#     print("=" * 70)


# # ============================================================
# # MAIN
# # ============================================================

# def main():

#     print()
#     print("=" * 70)
#     print("CONTROLMap - NIST DATA FETCHER")
#     print("=" * 70)

#     # --------------------------------------------------------
#     # STEP 1
#     # --------------------------------------------------------

#     create_directories()

#     # --------------------------------------------------------
#     # STEP 2
#     # --------------------------------------------------------

#     data = download_catalog()

#     if data is None:

#         print(
#             "[ERROR] Download failed."
#         )

#         return

#     # --------------------------------------------------------
#     # STEP 3
#     # --------------------------------------------------------

#     catalog = load_catalog()

#     if catalog is None:

#         return

#     # --------------------------------------------------------
#     # STEP 4
#     # --------------------------------------------------------

#     controls = extract_controls(
#         catalog
#     )

#     # --------------------------------------------------------
#     # STEP 5
#     # --------------------------------------------------------

#     save_controls(
#         controls
#     )

#     # --------------------------------------------------------
#     # STEP 6
#     # --------------------------------------------------------

#     create_search_data(
#         controls
#     )

#     # --------------------------------------------------------
#     # STEP 7
#     # --------------------------------------------------------

#     save_manifest(
#         data,
#         controls
#     )

#     # --------------------------------------------------------
#     # STEP 8
#     # --------------------------------------------------------

#     print_summary(
#         catalog,
#         controls
#     )


# # ============================================================
# # RUN
# # ============================================================

# if __name__ == "__main__":

#     main()


import csv
import hashlib
import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

RAW_DIR = os.path.join(
    DATA_DIR,
    "raw",
    "sp800"
)

METADATA_DIR = os.path.join(
    DATA_DIR,
    "metadata",
    "sp800"
)

PUBLICATIONS_FILE = os.path.join(
    DATA_DIR,
    "sp800_publications.json"
)

MANIFEST_FILE = os.path.join(
    DATA_DIR,
    "sp800_manifest.csv"
)

FAILED_FILE = os.path.join(
    DATA_DIR,
    "sp800_failed_downloads.json"
)

LISTING_URL = "https://csrc.nist.gov/publications/sp800"

REQUEST_TIMEOUT = 60

DOWNLOAD_DELAY = 1.5

MAX_RETRIES = 3

EXPECTED_PUBLICATIONS = 230


# ============================================================
# DIRECTORY SETUP
# ============================================================

def create_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)


# ============================================================
# HTTP SESSION
# ============================================================

def create_session():

    session = requests.Session()

    retry_strategy = Retry(
        total=MAX_RETRIES,
        connect=MAX_RETRIES,
        read=MAX_RETRIES,
        status=MAX_RETRIES,
        backoff_factor=2,

        status_forcelist=[
            429,
            500,
            502,
            503,
            504
        ],

        allowed_methods=[
            "GET"
        ],

        raise_on_status=False
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount(
        "https://",
        adapter
    )

    session.mount(
        "http://",
        adapter
    )

    session.headers.update({

        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/156.0.0.0 "
            "Safari/537.36"
        ),

        "Accept": (
            "application/pdf,"
            "application/octet-stream,"
            "text/html,"
            "application/xhtml+xml,"
            "*/*;q=0.8"
        ),

        "Accept-Language": "en-US,en;q=0.9",

        "Accept-Encoding": "gzip, deflate",

        "Connection": "keep-alive"

    })

    return session


# ============================================================
# FETCH WEB PAGE
# ============================================================

def fetch_page(session, url):

    try:

        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        return response.text

    except requests.RequestException as error:

        print(
            f"[ERROR] Failed to fetch page:\n"
            f"{url}\n"
            f"{error}"
        )

        return None


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# EXTRACT SP NUMBER
# ============================================================

def extract_sp_number(text):

    if not text:
        return ""

    patterns = [

        r"SP\s*800[-\s]?(\d+[A-Za-z]?)",

        r"Special Publication\s*800[-\s]?(\d+[A-Za-z]?)"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return (
                "SP 800-"
                + match.group(1).upper()
            )

    return ""


# ============================================================
# EXTRACT TITLE
# ============================================================

def extract_title(soup):

    title_tag = soup.find("h1")

    if title_tag:

        title = clean_text(
            title_tag.get_text(
                " ",
                strip=True
            )
        )

        if title:
            return title

    if soup.title:

        title = clean_text(
            soup.title.get_text(
                " ",
                strip=True
            )
        )

        title = re.sub(
            r"\s*\|\s*NIST.*$",
            "",
            title,
            flags=re.IGNORECASE
        )

        return title

    return ""


# ============================================================
# EXTRACT DOWNLOAD URL
# ============================================================

def extract_download_url(
    soup,
    page_url
):

    # --------------------------------------------------------
    # Method 1:
    # Find an anchor containing "Download"
    # --------------------------------------------------------

    for link in soup.find_all("a"):

        text = clean_text(
            link.get_text(
                " ",
                strip=True
            )
        )

        href = link.get("href")

        if not href:
            continue

        if "download" in text.lower():

            return urljoin(
                page_url,
                href
            )

    # --------------------------------------------------------
    # Method 2:
    # Look for NIST PDF links
    # --------------------------------------------------------

    for link in soup.find_all("a"):

        href = link.get("href")

        if not href:
            continue

        absolute_url = urljoin(
            page_url,
            href
        )

        if (
            "nvlpubs.nist.gov" in absolute_url.lower()
            and ".pdf" in absolute_url.lower()
        ):

            return absolute_url

    # --------------------------------------------------------
    # Method 3:
    # Any PDF link
    # --------------------------------------------------------

    for link in soup.find_all("a"):

        href = link.get("href")

        if not href:
            continue

        absolute_url = urljoin(
            page_url,
            href
        )

        if ".pdf" in absolute_url.lower():

            return absolute_url

    return ""


# ============================================================
# EXTRACT DOI
# ============================================================

def extract_doi(soup):

    page_text = soup.get_text(
        " ",
        strip=True
    )

    match = re.search(
        r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+",
        page_text
    )

    if match:

        return match.group(0).rstrip(
            ".,)"
        )

    return ""


# ============================================================
# EXTRACT PUBLICATION DATE
# ============================================================

def extract_publication_date(soup):

    text = soup.get_text(
        " ",
        strip=True
    )

    patterns = [

        r"Published\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})",

        r"Publication Date\s*:?\s*"
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})",

        r"Date\s*:?\s*"
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

    return ""


# ============================================================
# EXTRACT AUTHORS
# ============================================================

def extract_authors(soup):

    text = soup.get_text(
        "\n",
        strip=True
    )

    lines = [
        clean_text(line)
        for line in text.splitlines()
    ]

    for index, line in enumerate(lines):

        if line.lower() in [
            "author",
            "authors",
            "author(s)"
        ]:

            authors = []

            for next_line in lines[
                index + 1:index + 10
            ]:

                if not next_line:
                    continue

                if len(next_line) > 200:
                    break

                if next_line.lower() in [
                    "abstract",
                    "keywords",
                    "publication date",
                    "status"
                ]:
                    break

                authors.append(
                    next_line
                )

            if authors:

                return "; ".join(
                    authors
                )

    return ""


# ============================================================
# EXTRACT STATUS
# ============================================================

def extract_status(soup):

    text = soup.get_text(
        " ",
        strip=True
    )

    status_keywords = [

        "Final",

        "Initial Public Draft",

        "Public Draft",

        "Draft",

        "Errata",

        "Update"

    ]

    for keyword in status_keywords:

        if re.search(
            rf"\b{re.escape(keyword)}\b",
            text,
            re.IGNORECASE
        ):

            return keyword

    return ""


# ============================================================
# EXTRACT METADATA
# ============================================================

def extract_metadata(
    session,
    page_url
):

    print()
    print("[PAGE]")
    print(page_url)

    html = fetch_page(
        session,
        page_url
    )

    if not html:

        return None

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title = extract_title(
        soup
    )

    page_text = soup.get_text(
        " ",
        strip=True
    )

    sp_number = extract_sp_number(
        page_text
    )

    download_url = extract_download_url(
        soup,
        page_url
    )

    doi = extract_doi(
        soup
    )

    publication_date = extract_publication_date(
        soup
    )

    authors = extract_authors(
        soup
    )

    status = extract_status(
        soup
    )

    metadata = {

        "sp_number": sp_number,

        "title": title,

        "publication_date":
            publication_date,

        "authors":
            authors,

        "status":
            status,

        "doi":
            doi,

        "detail_url":
            page_url,

        "download_url":
            download_url,

        "source":
            "NIST SP 800 Series",

        "retrieved_at":
            datetime.utcnow().isoformat()
            + "Z"

    }

    return metadata


# ============================================================
# DISCOVER PUBLICATIONS
# ============================================================

def discover_publications(
    session
):

    print()
    print("=" * 70)
    print("DISCOVERING NIST SP 800 PUBLICATIONS")
    print("=" * 70)

    print()
    print(
        f"[LISTING]\n{LISTING_URL}"
    )

    html = fetch_page(
        session,
        LISTING_URL
    )

    if not html:

        return []

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    publication_urls = set()

    for link in soup.find_all("a"):

        href = link.get("href")

        if not href:
            continue

        absolute_url = urljoin(
            LISTING_URL,
            href
        )

        absolute_url = (
            absolute_url
            .split("#")[0]
        )

        absolute_lower = (
            absolute_url.lower()
        )

        # Current NIST publication URL
        if (
            "/pubs/sp/800/" in absolute_lower
        ):

            publication_urls.add(
                absolute_url
            )

    publication_urls = sorted(
        publication_urls
    )

    print()
    print(
        f"[FOUND] "
        f"{len(publication_urls)} "
        f"publication detail links"
    )

    if len(publication_urls) != EXPECTED_PUBLICATIONS:

        print()
        print(
            "[WARNING] Expected "
            f"{EXPECTED_PUBLICATIONS} "
            "publications."
        )

        print(
            f"[WARNING] Found "
            f"{len(publication_urls)}."
        )

        print(
            "[WARNING] Continuing with "
            "the discovered links."
        )

    return publication_urls


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_filename(
    sp_number,
    title
):

    if not sp_number:

        sp_number = "unknown"

    filename = sp_number

    if title:

        clean_title = re.sub(
            r"[<>:\"/\\|?*]",
            "",
            title
        )

        clean_title = re.sub(
            r"\s+",
            "_",
            clean_title
        )

        clean_title = clean_title[
            :100
        ]

        filename += "_" + clean_title

    return filename


# ============================================================
# SHA256
# ============================================================

def calculate_sha256(
    filepath
):

    sha256 = hashlib.sha256()

    with open(
        filepath,
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(
                chunk
            )

    return sha256.hexdigest()


# ============================================================
# CHECK EXISTING FILE
# ============================================================

def is_valid_pdf(
    filepath
):

    if not os.path.exists(
        filepath
    ):

        return False

    if os.path.getsize(
        filepath
    ) < 1000:

        return False

    try:

        with open(
            filepath,
            "rb"
        ) as file:

            header = file.read(
                5
            )

        return header == b"%PDF-"

    except OSError:

        return False


# ============================================================
# DOWNLOAD PDF
# ============================================================

def download_file(
    session,
    metadata,
    index,
    total
):

    download_url = metadata.get(
        "download_url",
        ""
    )

    if not download_url:

        print(
            "[SKIP] No PDF download URL"
        )

        return {
            "success": False,
            "error": "No download URL"
        }

    sp_number = metadata.get(
        "sp_number",
        ""
    )

    title = metadata.get(
        "title",
        ""
    )

    filename = safe_filename(
        sp_number,
        title
    )

    filename += ".pdf"

    output_path = os.path.join(
        RAW_DIR,
        filename
    )

    # --------------------------------------------------------
    # Already downloaded?
    # --------------------------------------------------------

    if is_valid_pdf(
        output_path
    ):

        print()
        print(
            "[EXISTS] "
            + output_path
        )

        sha256 = calculate_sha256(
            output_path
        )

        return {

            "success": True,

            "status": "already_exists",

            "filepath": output_path,

            "sha256": sha256,

            "size": os.path.getsize(
                output_path
            )

        }

    print()
    print("[DOWNLOAD]")
    print(download_url)

    # --------------------------------------------------------
    # Use detail page as Referer
    # --------------------------------------------------------

    detail_url = metadata.get(
        "detail_url",
        LISTING_URL
    )

    headers = {

        "Referer": detail_url,

        "Accept": (
            "application/pdf,"
            "application/octet-stream,"
            "*/*;q=0.8"
        ),

        "Accept-Language":
            "en-US,en;q=0.9",

        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/156.0.0.0 "
            "Safari/537.36"
        )

    }

    temporary_path = (
        output_path
        + ".part"
    )

    try:

        response = session.get(
            download_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            stream=True,
            allow_redirects=True
        )

        status_code = (
            response.status_code
        )

        print(
            f"[HTTP] {status_code}"
        )

        # ----------------------------------------------------
        # Handle HTTP errors
        # ----------------------------------------------------

        if status_code != 200:

            print(
                "[ERROR] Download failed: "
                f"HTTP {status_code}"
            )

            response.close()

            return {

                "success": False,

                "error":
                    f"HTTP {status_code}",

                "status_code":
                    status_code,

                "url":
                    download_url

            }

        # ----------------------------------------------------
        # Check content type
        # ----------------------------------------------------

        content_type = (
            response.headers.get(
                "Content-Type",
                ""
            )
            .lower()
        )

        print(
            f"[CONTENT-TYPE] "
            f"{content_type}"
        )

        # ----------------------------------------------------
        # Save response
        # ----------------------------------------------------

        with open(
            temporary_path,
            "wb"
        ) as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):

                if chunk:

                    file.write(
                        chunk
                    )

        response.close()

        # ----------------------------------------------------
        # Validate PDF
        # ----------------------------------------------------

        if not is_valid_pdf(
            temporary_path
        ):

            print(
                "[ERROR] Response is "
                "not a valid PDF."
            )

            try:
                os.remove(
                    temporary_path
                )
            except OSError:
                pass

            return {

                "success": False,

                "error":
                    "Downloaded content is not a valid PDF",

                "content_type":
                    content_type,

                "url":
                    download_url

            }

        # ----------------------------------------------------
        # Rename .part -> .pdf
        # ----------------------------------------------------

        os.replace(
            temporary_path,
            output_path
        )

        # ----------------------------------------------------
        # Calculate hash
        # ----------------------------------------------------

        sha256 = calculate_sha256(
            output_path
        )

        file_size = os.path.getsize(
            output_path
        )

        print(
            f"[SUCCESS] "
            f"{file_size:,} bytes"
        )

        print(
            f"[SHA256] "
            f"{sha256}"
        )

        return {

            "success": True,

            "status": "downloaded",

            "filepath": output_path,

            "sha256": sha256,

            "size": file_size,

            "content_type":
                content_type

        }

    except requests.RequestException as error:

        print(
            "[ERROR] Download failed:"
        )

        print(
            error
        )

        try:

            if os.path.exists(
                temporary_path
            ):

                os.remove(
                    temporary_path
                )

        except OSError:
            pass

        return {

            "success": False,

            "error":
                str(error),

            "url":
                download_url

        }


# ============================================================
# SAVE JSON
# ============================================================

def save_json(
    filepath,
    data
):

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# SAVE MANIFEST
# ============================================================

def save_manifest(
    records
):

    fieldnames = [

        "sp_number",

        "title",

        "publication_date",

        "status",

        "detail_url",

        "download_url",

        "filepath",

        "size",

        "sha256",

        "download_status",

        "error"

    ]

    with open(
        MANIFEST_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for record in records:

            writer.writerow({

                "sp_number":
                    record.get(
                        "sp_number",
                        ""
                    ),

                "title":
                    record.get(
                        "title",
                        ""
                    ),

                "publication_date":
                    record.get(
                        "publication_date",
                        ""
                    ),

                "status":
                    record.get(
                        "status",
                        ""
                    ),

                "detail_url":
                    record.get(
                        "detail_url",
                        ""
                    ),

                "download_url":
                    record.get(
                        "download_url",
                        ""
                    ),

                "filepath":
                    record.get(
                        "filepath",
                        ""
                    ),

                "size":
                    record.get(
                        "size",
                        ""
                    ),

                "sha256":
                    record.get(
                        "sha256",
                        ""
                    ),

                "download_status":
                    record.get(
                        "download_status",
                        ""
                    ),

                "error":
                    record.get(
                        "error",
                        ""
                    )

            })


# ============================================================
# MAIN
# ============================================================

def main():

    create_directories()

    session = create_session()

    # ========================================================
    # STEP 1
    # DISCOVER PUBLICATIONS
    # ========================================================

    publication_urls = discover_publications(
        session
    )

    if not publication_urls:

        print()
        print(
            "[ERROR] "
            "No publication links found."
        )

        return

    # ========================================================
    # STEP 2
    # EXTRACT METADATA
    # ========================================================

    print()
    print("=" * 70)
    print("EXTRACTING PUBLICATION METADATA")
    print("=" * 70)

    publications = []

    total = len(
        publication_urls
    )

    for index, page_url in enumerate(
        publication_urls,
        start=1
    ):

        print()
        print(
            f"[{index}/{total}]"
        )

        metadata = extract_metadata(
            session,
            page_url
        )

        if metadata:

            publications.append(
                metadata
            )

        time.sleep(
            DOWNLOAD_DELAY
        )

    # ========================================================
    # SAVE METADATA
    # ========================================================

    save_json(
        PUBLICATIONS_FILE,
        publications
    )

    print()
    print(
        "=" * 70
    )

    print(
        f"[SUCCESS] Saved metadata for "
        f"{len(publications)} publications"
    )

    print(
        f"[FILE] "
        f"{PUBLICATIONS_FILE}"
    )

    print(
        "=" * 70
    )

    # ========================================================
    # STEP 3
    # DOWNLOAD PUBLICATIONS
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "DOWNLOADING PUBLICATIONS"
    )

    print(
        "=" * 70
    )

    manifest_records = []

    failed_downloads = []

    total = len(
        publications
    )

    successful = 0

    failed = 0

    skipped = 0

    for index, metadata in enumerate(
        publications,
        start=1
    ):

        print()
        print(
            "=" * 70
        )

        print(
            f"[{index}/{total}]"
        )

        print(
            metadata.get(
                "sp_number",
                "Unknown"
            )
        )

        print(
            metadata.get(
                "title",
                ""
            )
        )

        print(
            "=" * 70
        )

        result = download_file(
            session,
            metadata,
            index,
            total
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        metadata["download_status"] = (
            "success"
            if result.get("success")
            else "failed"
        )

        if result.get(
            "success"
        ):

            if result.get(
                "status"
            ) == "already_exists":

                skipped += 1

            else:

                successful += 1

            metadata["filepath"] = (
                result.get(
                    "filepath",
                    ""
                )
            )

            metadata["sha256"] = (
                result.get(
                    "sha256",
                    ""
                )
            )

            metadata["size"] = (
                result.get(
                    "size",
                    ""
                )
            )

        else:

            failed += 1

            metadata["error"] = (
                result.get(
                    "error",
                    "Unknown error"
                )
            )

            failed_downloads.append(
                metadata.copy()
            )

        manifest_records.append(
            metadata
        )

        # ----------------------------------------------------
        # Save progress after every file
        # ----------------------------------------------------

        save_json(
            PUBLICATIONS_FILE,
            publications
        )

        save_manifest(
            manifest_records
        )

        if result.get(
            "success"
        ):

            pass

        time.sleep(
            DOWNLOAD_DELAY
        )

    # ========================================================
    # SAVE FAILED DOWNLOADS
    # ========================================================

    save_json(
        FAILED_FILE,
        failed_downloads
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print()
    print(
        "=" * 70
    )

    print(
        "DOWNLOAD COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Total publications : {total}"
    )

    print(
        f"Downloaded          : {successful}"
    )

    print(
        f"Already existed     : {skipped}"
    )

    print(
        f"Failed              : {failed}"
    )

    print()
    print(
        f"Metadata            : "
        f"{PUBLICATIONS_FILE}"
    )

    print(
        f"Manifest            : "
        f"{MANIFEST_FILE}"
    )

    print(
        f"Failed downloads    : "
        f"{FAILED_FILE}"
    )

    print(
        f"PDF directory       : "
        f"{RAW_DIR}"
    )

    print(
        "=" * 70
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()