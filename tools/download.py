import os
import json
import csv
import hashlib
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

RAW_DIR = os.path.join(
    DATA_DIR,
    "raw"
)

CATALOG_FILE = os.path.join(
    RAW_DIR,
    "NIST_SP-800-53_rev5_catalog.json"
)

CONTROLS_FILE = os.path.join(
    DATA_DIR,
    "controls.json"
)

MANIFEST_FILE = os.path.join(
    DATA_DIR,
    "manifest.csv"
)

# Official NIST OSCAL repository
CATALOG_URL = (
    "https://raw.githubusercontent.com/"
    "usnistgov/oscal-content/main/"
    "nist.gov/SP800-53/rev5/json/"
    "NIST_SP-800-53_rev5_catalog.json"
)


# ============================================================
# CREATE DIRECTORIES
# ============================================================

def create_directories():

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    os.makedirs(
        RAW_DIR,
        exist_ok=True
    )


# ============================================================
# DOWNLOAD FILE
# ============================================================

def download_catalog():

    print()
    print("=" * 70)
    print("DOWNLOADING NIST SP 800-53 REV 5 CATALOG")
    print("=" * 70)

    print()
    print("Source:")
    print(CATALOG_URL)

    print()
    print("Destination:")
    print(CATALOG_FILE)

    request = Request(
        CATALOG_URL,
        headers={
            "User-Agent":
                "ControlMap/1.0 Educational Project"
        }
    )

    try:

        with urlopen(
            request,
            timeout=60
        ) as response:

            data = response.read()

        with open(
            CATALOG_FILE,
            "wb"
        ) as file:

            file.write(data)

        print()
        print("[SUCCESS] Catalog downloaded")

        print(
            f"[SIZE] {len(data):,} bytes"
        )

        return data

    except HTTPError as e:

        print()
        print(
            f"[ERROR] HTTP error: {e.code}"
        )

        return None

    except URLError as e:

        print()
        print(
            f"[ERROR] URL error: {e.reason}"
        )

        return None

    except Exception as e:

        print()
        print(
            f"[ERROR] {e}"
        )

        return None


# ============================================================
# CALCULATE SHA256
# ============================================================

def calculate_sha256(data):

    return hashlib.sha256(
        data
    ).hexdigest()


# ============================================================
# LOAD CATALOG
# ============================================================

def load_catalog():

    print()
    print("=" * 70)
    print("LOADING CATALOG")
    print("=" * 70)

    try:

        with open(
            CATALOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            catalog = json.load(file)

        print(
            "[SUCCESS] JSON loaded successfully"
        )

        return catalog

    except json.JSONDecodeError as e:

        print()
        print(
            f"[ERROR] Invalid JSON: {e}"
        )

        return None

    except Exception as e:

        print()
        print(
            f"[ERROR] {e}"
        )

        return None


# ============================================================
# GET PROPERTY
# ============================================================

def get_property(properties, name):

    for prop in properties:

        if prop.get("name") == name:

            return prop.get(
                "value",
                ""
            )

    return ""


# ============================================================
# EXTRACT TEXT FROM PARTS
# ============================================================

def extract_part_text(parts):

    text = []

    for part in parts:

        prose = part.get(
            "prose",
            ""
        )

        if prose:

            text.append(
                prose
            )

        nested_parts = part.get(
            "parts",
            []
        )

        if nested_parts:

            text.extend(
                extract_part_text(
                    nested_parts
                )
            )

    return text


# ============================================================
# EXTRACT CONTROLS
# ============================================================

def extract_controls(catalog):

    print()
    print("=" * 70)
    print("EXTRACTING CONTROLS")
    print("=" * 70)

    controls = []

    groups = catalog.get(
        "catalog",
        {}
    ).get(
        "groups",
        []
    )

    print(
        f"[INFO] Groups found: {len(groups)}"
    )

    for group in groups:

        group_id = group.get(
            "id",
            ""
        )

        group_title = group.get(
            "title",
            ""
        )

        print()
        print(
            f"[GROUP] {group_id.upper()} - "
            f"{group_title}"
        )

        group_controls = group.get(
            "controls",
            []
        )

        print(
            f"Controls: {len(group_controls)}"
        )

        for control in group_controls:

            control_id = control.get(
                "id",
                ""
            )

            title = control.get(
                "title",
                ""
            )

            properties = control.get(
                "props",
                []
            )

            label = get_property(
                properties,
                "label"
            )

            parts = control.get(
                "parts",
                []
            )

            statements = extract_part_text(
                parts
            )

            control_text = " ".join(
                statements
            )

            parameters = control.get(
                "params",
                []
            )

            related_controls = control.get(
                "links",
                []
            )

            control_data = {

                "control_id":
                    control_id.upper(),

                "group_id":
                    group_id.upper(),

                "group_title":
                    group_title,

                "title":
                    title,

                "label":
                    label,

                "statement":
                    control_text,

                "parameters":
                    parameters,

                "related_controls":
                    related_controls,

                "raw":
                    control
            }

            controls.append(
                control_data
            )

            # ------------------------------------------------
            # DISPLAY PROGRESS
            # ------------------------------------------------

            print(
                f"  ✓ {control_id.upper()} - {title}"
            )

    return controls


# ============================================================
# SAVE CONTROLS
# ============================================================

def save_controls(controls):

    print()
    print("=" * 70)
    print("SAVING STRUCTURED CONTROLS")
    print("=" * 70)

    with open(
        CONTROLS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            controls,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        f"[SUCCESS] Saved {len(controls)} controls"
    )

    print(
        f"[FILE] {CONTROLS_FILE}"
    )


# ============================================================
# SAVE MANIFEST
# ============================================================

def save_manifest(
    data,
    controls
):

    sha256 = calculate_sha256(
        data
    )

    file_exists = os.path.exists(
        MANIFEST_FILE
    )

    with open(
        MANIFEST_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "file",
                "source_url",
                "download_date",
                "size",
                "sha256",
                "control_count"
            ])

        writer.writerow([
            os.path.basename(
                CATALOG_FILE
            ),

            CATALOG_URL,

            datetime.now().isoformat(),

            len(data),

            sha256,

            len(controls)
        ])

    print()
    print(
        f"[SUCCESS] Manifest updated"
    )


# ============================================================
# CREATE SEARCH DATA
# ============================================================

def create_search_data(controls):

    print()
    print("=" * 70)
    print("CREATING SEARCH DATA")
    print("=" * 70)

    search_data = []

    for control in controls:

        search_text = (
            control.get(
                "control_id",
                ""
            )
            + " "
            + control.get(
                "title",
                ""
            )
            + " "
            + control.get(
                "statement",
                ""
            )
        )

        search_item = {

            "control_id":
                control.get(
                    "control_id",
                    ""
                ),

            "group_id":
                control.get(
                    "group_id",
                    ""
                ),

            "title":
                control.get(
                    "title",
                    ""
                ),

            "statement":
                control.get(
                    "statement",
                    ""
                ),

            "search_text":
                search_text
        }

        search_data.append(
            search_item
        )

    search_file = os.path.join(
        DATA_DIR,
        "search_data.json"
    )

    with open(
        search_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            search_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"[SUCCESS] Search data created"
    )

    print(
        f"[FILE] {search_file}"
    )


# ============================================================
# PRINT SUMMARY
# ============================================================

def print_summary(
    catalog,
    controls
):

    metadata = catalog.get(
        "catalog",
        {}
    ).get(
        "metadata",
        {}
    )

    print()
    print()
    print("=" * 70)
    print("CONTROLMap DATA DOWNLOAD COMPLETE")
    print("=" * 70)

    print()

    print(
        "Title:"
    )

    print(
        metadata.get(
            "title",
            "N/A"
        )
    )

    print()

    print(
        "Version:"
    )

    print(
        metadata.get(
            "version",
            "N/A"
        )
    )

    print()

    print(
        "OSCAL Version:"
    )

    print(
        metadata.get(
            "oscal-version",
            "N/A"
        )
    )

    print()

    print(
        "Total Groups:"
    )

    groups = catalog.get(
        "catalog",
        {}
    ).get(
        "groups",
        []
    )

    print(
        len(groups)
    )

    print()

    print(
        "Total Controls:"
    )

    print(
        len(controls)
    )

    print()

    print(
        "Raw Catalog:"
    )

    print(
        CATALOG_FILE
    )

    print()

    print(
        "Structured Controls:"
    )

    print(
        CONTROLS_FILE
    )

    print()

    print(
        "Search Data:"
    )

    print(
        os.path.join(
            DATA_DIR,
            "search_data.json"
        )
    )

    print()

    print(
        "Manifest:"
    )

    print(
        MANIFEST_FILE
    )

    print()

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("CONTROLMap - NIST DATA FETCHER")
    print("=" * 70)

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    create_directories()

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    data = download_catalog()

    if data is None:

        print(
            "[ERROR] Download failed."
        )

        return

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    catalog = load_catalog()

    if catalog is None:

        return

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    controls = extract_controls(
        catalog
    )

    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    save_controls(
        controls
    )

    # --------------------------------------------------------
    # STEP 6
    # --------------------------------------------------------

    create_search_data(
        controls
    )

    # --------------------------------------------------------
    # STEP 7
    # --------------------------------------------------------

    save_manifest(
        data,
        controls
    )

    # --------------------------------------------------------
    # STEP 8
    # --------------------------------------------------------

    print_summary(
        catalog,
        controls
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()