
import csv
import hashlib
import os
import re
import time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
MANIFEST_FILE = os.path.join(DATA_DIR, "manifest.csv")
DISCOVERED_FILE = os.path.join(DATA_DIR, "discovered_publications.csv")
FAILED_FILE = os.path.join(DATA_DIR, "failed_urls.txt")

START_URL = "https://csrc.nist.gov/publications/sp800"

ALLOWED_HOSTS = {
    "csrc.nist.gov",
    "nvlpubs.nist.gov",
    "nvlpubs.nist.gov",
    "nvlpubs.nist.gov",
}

USER_AGENT = "ControlMapStudentResearch/1.0"

HEADERS = {
    "User-Agent": USER_AGENT
}

REQUEST_TIMEOUT = 45
DELAY_SECONDS = 2
MAX_RETRIES = 3

# Safety limits. Increase after checking the first run.
MAX_PUBLICATION_PAGES = 1000
MAX_PUBLICATION_DETAILS = 2000
MAX_PDFS = 2000

# Include drafts as well as final publications.
# Set False if you only want final publications.
INCLUDE_DRAFTS = True

# Only follow links that appear to be publication detail pages.
PUBLICATION_PATH_MARKERS = (
    "/pubs/sp/800/",
    "/publications/",
)

PDF_EXTENSIONS = (".pdf",)


# ============================================================
# GLOBAL STATE
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)

robots_cache = {}
visited_listing_pages = set()
visited_detail_pages = set()
discovered_publications = {}
discovered_pdfs = {}


# ============================================================
# DIRECTORY SETUP
# ============================================================

def setup_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)


# ============================================================
# URL HELPERS
# ============================================================

def normalize_url(url):
    url, _ = urldefrag(url)
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    if not parsed.netloc:
        return None

    return url


def is_allowed_host(url):
    host = (urlparse(url).hostname or "").lower()

    return (
        host in ALLOWED_HOSTS
        or host.endswith(".nist.gov")
    )


def is_pdf_url(url):
    path = urlparse(url).path.lower()
    return path.endswith(PDF_EXTENSIONS)


def safe_filename(value):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", "_", value.strip())
    value = re.sub(r"_+", "_", value)
    return value[:180] or "nist_document"


def publication_number(text):
    match = re.search(
        r"\bSP\s*[- ]?\s*800[- ]?[\w.-]+",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        return re.sub(r"\s+", " ", match.group(0)).upper()

    return ""


# ============================================================
# ROBOTS.TXT
# ============================================================

def can_fetch(url):
    parsed = urlparse(url)
    root = f"{parsed.scheme}://{parsed.netloc}"

    if root not in robots_cache:
        parser = RobotFileParser()
        parser.set_url(root + "/robots.txt")

        try:
            parser.read()
            robots_cache[root] = parser
        except Exception as exc:
            # Fail closed: do not crawl when the site's
            # robots policy cannot be checked.
            print(f"[ROBOTS ERROR] {root}: {exc}")
            robots_cache[root] = False

    parser = robots_cache[root]

    if parser is False:
        return False

    try:
        return parser.can_fetch(USER_AGENT, url)
    except Exception:
        return False


# ============================================================
# HTTP REQUEST WITH RETRIES
# ============================================================

def get_response(url, stream=False):
    if not is_allowed_host(url):
        print(f"[BLOCKED HOST] {url}")
        return None

    if not can_fetch(url):
        print(f"[ROBOTS BLOCKED] {url}")
        return None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                stream=stream,
            )

            if response.status_code == 429:
                wait_time = int(
                    response.headers.get("Retry-After", 10)
                )
                print(f"[RATE LIMITED] Waiting {wait_time}s")
                time.sleep(wait_time)
                continue

            if response.status_code in (500, 502, 503, 504):
                print(
                    f"[SERVER ERROR] HTTP {response.status_code}; "
                    f"attempt {attempt}"
                )
                time.sleep(attempt * 3)
                continue

            response.raise_for_status()

            final_url = normalize_url(response.url)

            if not final_url or not is_allowed_host(final_url):
                response.close()
                print("[BLOCKED REDIRECT] Final destination is not allowed")
                return None

            if final_url != url and not can_fetch(final_url):
                response.close()
                print(f"[ROBOTS BLOCKED REDIRECT] {final_url}")
                return None

            return response

        except requests.RequestException as exc:
            print(f"[REQUEST ERROR] {url}: {exc}")
            time.sleep(attempt * 3)

    return None


# ============================================================
# HTML FETCHING
# ============================================================

def fetch_html(url):
    response = get_response(url)

    if response is None:
        return None

    try:
        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "html" not in content_type:
            print(f"[NOT HTML] {url}")
            return None

        return response.text

    finally:
        response.close()


# ============================================================
# SAVE FAILED URL
# ============================================================

def record_failure(url, reason):
    with open(
        FAILED_FILE,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(
            f"{datetime.now(timezone.utc).isoformat()}\t"
            f"{reason}\t{url}\n"
        )


# ============================================================
# SAVE DISCOVERED PUBLICATION
# ============================================================

def save_discovered_publications():
    fields = [
        "title",
        "publication_number",
        "publication_page",
        "status",
    ]

    with open(
        DISCOVERED_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for item in discovered_publications.values():
            writer.writerow(item)


# ============================================================
# DISCOVER PDF LINKS
# ============================================================

def discover_pdf_links(page_url, soup, page_title):
    page_text = soup.get_text(" ", strip=True)

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()

        if not href:
            continue

        pdf_url = normalize_url(urljoin(page_url, href))

        if not pdf_url:
            continue

        if not is_pdf_url(pdf_url):
            continue

        if not is_allowed_host(pdf_url):
            continue

        anchor_text = anchor.get_text(" ", strip=True)

        context = (
            anchor_text + " " + page_title + " " + page_text[:1000]
        )

        pub_no = publication_number(context)

        title = page_title or anchor_text or pub_no or "NIST publication"

        # Use the original PDF URL as the unique key.
        discovered_pdfs[pdf_url] = {
            "title": title,
            "publication_number": pub_no,
            "publication_page": page_url,
            "pdf_url": pdf_url,
        }


# ============================================================
# FIND PUBLICATION DETAIL LINKS
# ============================================================

def is_publication_detail_url(url):
    parsed = urlparse(url)
    path = parsed.path.lower()

    if not any(marker in path for marker in PUBLICATION_PATH_MARKERS):
        return False

    if is_pdf_url(url):
        return False

    return True


def find_publication_links(page_url, soup):
    links = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()

        if not href:
            continue

        link = normalize_url(urljoin(page_url, href))

        if not link:
            continue

        if not is_allowed_host(link):
            continue

        if is_publication_detail_url(link):
            links.add(link)

    return links


# ============================================================
# FIND PAGINATION LINKS
# ============================================================

def find_pagination_links(page_url, soup):
    links = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href", "").strip()

        if not href:
            continue

        label = anchor.get_text(" ", strip=True).lower()
        rel = " ".join(anchor.get("rel", [])).lower()
        classes = " ".join(anchor.get("class", [])).lower()

        is_pagination = (
            "next" in label
            or "next" in rel
            or "pagination" in classes
            or "page=" in href.lower()
            or "pagenumber=" in href.lower()
        )

        if not is_pagination:
            continue

        link = normalize_url(urljoin(page_url, href))

        if link and is_allowed_host(link):
            links.add(link)

    return links


# ============================================================
# EXTRACT PUBLICATION TITLE AND STATUS
# ============================================================

def extract_page_metadata(soup, page_url):
    title_tag = soup.find("title")

    title = (
        title_tag.get_text(" ", strip=True)
        if title_tag
        else ""
    )

    if not title:
        heading = soup.find("h1")

        if heading:
            title = heading.get_text(" ", strip=True)

    text = soup.get_text(" ", strip=True)

    status = "Unknown"

    if "initial public draft" in text.lower():
        status = "Initial Public Draft"
    elif "public draft" in text.lower():
        status = "Public Draft"
    elif "final" in text.lower():
        status = "Final"

    return {
        "title": title,
        "publication_number": publication_number(
            title + " " + text[:2000]
        ),
        "publication_page": page_url,
        "status": status,
    }


# ============================================================
# LOAD EXISTING MANIFEST
# ============================================================

def load_existing_manifest():
    downloaded = {}

    if not os.path.exists(MANIFEST_FILE):
        return downloaded

    with open(
        MANIFEST_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            pdf_url = row.get("pdf_url", "")
            filename = row.get("filename", "")

            if pdf_url and filename:
                file_path = os.path.join(RAW_DIR, filename)

                if os.path.isfile(file_path):
                    downloaded[pdf_url] = filename

    return downloaded


# ============================================================
# DOWNLOAD A PDF
# ============================================================

def download_pdf(item, existing_downloads):
    pdf_url = item["pdf_url"]

    if pdf_url in existing_downloads:
        print(f"[ALREADY DOWNLOADED] {pdf_url}")
        return None

    print()
    print("-" * 70)
    print(f"[PDF] {item['title']}")
    print(f"[URL] {pdf_url}")

    response = get_response(pdf_url, stream=True)

    if response is None:
        record_failure(pdf_url, "Fetch failed or robots disallowed")
        return None

    try:
        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        # Validate file using both URL and response signature.
        first_chunk = next(response.iter_content(64 * 1024), b"")

        if not first_chunk.startswith(b"%PDF-"):
            print(f"[NOT A PDF] {pdf_url}")
            record_failure(pdf_url, "Response is not a PDF")
            return None

        path_name = os.path.basename(
            urlparse(pdf_url).path
        )

        if not path_name.lower().endswith(".pdf"):
            path_name = "nist_publication.pdf"

        stem = safe_filename(
            item["publication_number"] or
            os.path.splitext(path_name)[0]
        )

        filename = stem + ".pdf"
        output_path = os.path.join(RAW_DIR, filename)

        counter = 1

        while os.path.exists(output_path):
            # Avoid overwriting an unrelated document.
            filename = f"{stem}_{counter}.pdf"
            output_path = os.path.join(RAW_DIR, filename)
            counter += 1

        digest = hashlib.sha256()
        total_size = 0

        with open(output_path, "wb") as output:
            output.write(first_chunk)
            digest.update(first_chunk)
            total_size += len(first_chunk)

            for chunk in response.iter_content(64 * 1024):
                if not chunk:
                    continue

                output.write(chunk)
                digest.update(chunk)
                total_size += len(chunk)

        if total_size < 1000:
            os.remove(output_path)
            record_failure(pdf_url, "PDF response too small")
            return None

        record = {
            "filename": filename,
            "title": item["title"],
            "publication_number": item["publication_number"],
            "publication_page": item["publication_page"],
            "pdf_url": pdf_url,
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": total_size,
            "sha256": digest.hexdigest(),
            "content_type": content_type,
        }

        print(f"[SUCCESS] {filename}")
        print(f"[SIZE] {total_size:,} bytes")

        return record

    except Exception as exc:
        print(f"[DOWNLOAD ERROR] {exc}")
        record_failure(pdf_url, str(exc))
        return None

    finally:
        response.close()


# ============================================================
# SAVE DOWNLOAD MANIFEST
# ============================================================

def append_manifest(record):
    fields = [
        "filename",
        "title",
        "publication_number",
        "publication_page",
        "pdf_url",
        "downloaded_at",
        "size_bytes",
        "sha256",
        "content_type",
    ]

    file_exists = os.path.exists(MANIFEST_FILE)

    with open(
        MANIFEST_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        if not file_exists or os.path.getsize(MANIFEST_FILE) == 0:
            writer.writeheader()

        writer.writerow(record)


# ============================================================
# CRAWL THE MAIN PUBLICATIONS LIST
# ============================================================

def crawl_listing_pages():
    queue = [START_URL]

    while queue and len(visited_listing_pages) < MAX_PUBLICATION_PAGES:
        current_url = queue.pop(0)

        if current_url in visited_listing_pages:
            continue

        visited_listing_pages.add(current_url)

        print()
        print("=" * 70)
        print(
            f"[LISTING {len(visited_listing_pages)}]"
        )
        print(current_url)
        print("=" * 70)

        html = fetch_html(current_url)

        if not html:
            record_failure(current_url, "Listing page fetch failed")
            continue

        soup = BeautifulSoup(html, "html.parser")

        # The main list may directly expose PDF links.
        title = (
            soup.title.get_text(" ", strip=True)
            if soup.title
            else "NIST SP 800 publication listing"
        )

        discover_pdf_links(current_url, soup, title)

        # Collect publication detail pages.
        for link in find_publication_links(current_url, soup):
            if link not in visited_detail_pages:
                discovered_publications.setdefault(
                    link,
                    {
                        "title": "",
                        "publication_number": "",
                        "publication_page": link,
                        "status": "Unknown",
                    }
                )

        # Follow next/page links.
        for link in find_pagination_links(current_url, soup):
            if link not in visited_listing_pages and link not in queue:
                queue.append(link)

        save_discovered_publications()
        time.sleep(DELAY_SECONDS)


# ============================================================
# CRAWL PUBLICATION DETAIL PAGES
# ============================================================

def crawl_publication_pages():
    queue = list(discovered_publications.keys())

    while (
        queue
        and len(visited_detail_pages) < MAX_PUBLICATION_DETAILS
    ):
        current_url = queue.pop(0)

        if current_url in visited_detail_pages:
            continue

        visited_detail_pages.add(current_url)

        print()
        print("=" * 70)
        print(
            f"[PUBLICATION {len(visited_detail_pages)}]"
        )
        print(current_url)
        print("=" * 70)

        html = fetch_html(current_url)

        if not html:
            record_failure(current_url, "Publication page fetch failed")
            continue

        soup = BeautifulSoup(html, "html.parser")

        metadata = extract_page_metadata(soup, current_url)

        if (
            not INCLUDE_DRAFTS
            and "draft" in metadata["status"].lower()
        ):
            print("[SKIP] Draft publication")
            continue

        discovered_publications[current_url] = metadata

        discover_pdf_links(
            current_url,
            soup,
            metadata["title"]
        )

        # Keep listing information up to date.
        save_discovered_publications()

        time.sleep(DELAY_SECONDS)


# ============================================================
# DOWNLOAD ALL DISCOVERED PDFS
# ============================================================

def download_all_pdfs():
    existing_downloads = load_existing_manifest()

    print()
    print("=" * 70)
    print(f"PDF LINKS DISCOVERED: {len(discovered_pdfs)}")
    print("=" * 70)

    downloaded_count = 0
    skipped_count = 0

    for index, item in enumerate(
        discovered_pdfs.values(),
        start=1
    ):
        if index > MAX_PDFS:
            print("[STOP] MAX_PDFS reached")
            break

        print(f"\n[PROGRESS] {index}/{min(len(discovered_pdfs), MAX_PDFS)}")

        record = download_pdf(
            item,
            existing_downloads
        )

        if record:
            append_manifest(record)

            existing_downloads[item["pdf_url"]] = record["filename"]
            downloaded_count += 1
        else:
            skipped_count += 1

        time.sleep(DELAY_SECONDS)

    return downloaded_count, skipped_count


# ============================================================
# SUMMARY
# ============================================================

def print_summary(downloaded_count, skipped_count):
    print()
    print("=" * 70)
    print("CONTROLMAP NIST PDF COLLECTION SUMMARY")
    print("=" * 70)

    print(f"Listing pages visited: {len(visited_listing_pages)}")
    print(f"Publication pages visited: {len(visited_detail_pages)}")
    print(f"Publication records found: {len(discovered_publications)}")
    print(f"PDF links discovered: {len(discovered_pdfs)}")
    print(f"PDFs downloaded this run: {downloaded_count}")
    print(f"PDFs skipped/failed: {skipped_count}")

    print()
    print(f"PDF folder: {RAW_DIR}")
    print(f"Manifest: {MANIFEST_FILE}")
    print(f"Publication list: {DISCOVERED_FILE}")
    print(f"Failed URL log: {FAILED_FILE}")

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():
    setup_directories()

    print()
    print("=" * 70)
    print("CONTROLMAP - NIST SP 800 PDF COLLECTOR")
    print("=" * 70)

    print(f"Starting URL: {START_URL}")
    print(f"Include drafts: {INCLUDE_DRAFTS}")
    print(f"Maximum listing pages: {MAX_PUBLICATION_PAGES}")
    print(f"Maximum detail pages: {MAX_PUBLICATION_DETAILS}")
    print(f"Maximum PDFs: {MAX_PDFS}")

    # Step 1: Discover the publication listing pages.
    crawl_listing_pages()

    # Step 2: Visit each publication page and find its PDFs.
    crawl_publication_pages()

    # Step 3: Download all discovered PDFs.
    downloaded, skipped = download_all_pdfs()

    # Step 4: Print collection summary.
    print_summary(downloaded, skipped)


if __name__ == "__main__":
    main()
