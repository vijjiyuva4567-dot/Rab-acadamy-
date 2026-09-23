import csv
import json
import logging
import os
import re
import statistics
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# Configuration
# ============================================================

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

OUTPUT_DIR = "data"
REPORT_DIR = "reports"

CSV_FILE = os.path.join(OUTPUT_DIR, "books.csv")
JSON_FILE = os.path.join(OUTPUT_DIR, "books.json")
REPORT_FILE = os.path.join(REPORT_DIR, "summary_report.txt")
LOG_FILE = "scraper.log"

MAX_PAGES = 50
RATE_LIMIT_SECONDS = 1.0
REQUEST_TIMEOUT = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# HTTP Session
# ============================================================

def create_session():
    """
    Create a requests session with retry support.
    """

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session = requests.Session()

    session.headers.update(HEADERS)

    session.mount(
        "http://",
        adapter
    )

    session.mount(
        "https://",
        adapter
    )

    return session


# ============================================================
# Utility Functions
# ============================================================

def clean_text(value):
    """
    Clean unnecessary whitespace from text.
    """

    if not value:
        return ""

    return " ".join(
        value.strip().split()
    )


def convert_price(price_text):
    """
    Convert a price such as '£51.77' into 51.77.
    """

    if not price_text:
        return 0.0

    match = re.search(
        r"£\s*(\d+(?:\.\d{2})?)",
        price_text
    )

    if match:
        try:
            return float(
                match.group(1)
            )
        except ValueError:
            return 0.0

    return 0.0


def extract_rating(rating_element):
    """
    Convert rating words into numeric values.

    One   -> 1
    Two   -> 2
    Three -> 3
    Four  -> 4
    Five  -> 5
    """

    if not rating_element:
        return 0

    classes = rating_element.get(
        "class",
        []
    )

    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    for class_name in classes:
        if class_name in rating_map:
            return rating_map[class_name]

    return 0


def ensure_directories():
    """
    Create output directories if they do not exist.
    """

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )


# ============================================================
# Fetch Page
# ============================================================

def fetch_page(session, page_number):
    """
    Download one catalogue page.
    """

    url = BASE_URL.format(page_number)

    logger.info(
        "Fetching page %s: %s",
        page_number,
        url
    )

    try:
        response = session.get(
            url,
            timeout=REQUEST_TIMEOUT
        )

        response.raise_for_status()

        logger.info(
            "Successfully fetched page %s",
            page_number
        )

        return response.text

    except requests.RequestException as error:

        logger.error(
            "Failed to fetch page %s: %s",
            page_number,
            error
        )

        return None


# ============================================================
# Parse Books
# ============================================================

def parse_books(html, page_number):
    """
    Parse book information from one catalogue page.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    books = []

    product_cards = soup.select(
        "article.product_pod"
    )

    for book in product_cards:

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title_element = book.select_one(
            "h3 a"
        )

        if title_element:
            title = clean_text(
                title_element.get("title", "")
            )
        else:
            title = ""

        # ----------------------------------------------------
        # Product URL
        # ----------------------------------------------------

        if title_element:
            product_url = urljoin(
                "https://books.toscrape.com/catalogue/",
                title_element.get(
                    "href",
                    ""
                )
            )
        else:
            product_url = ""

        # ----------------------------------------------------
        # Price
        # ----------------------------------------------------

        price_element = book.select_one(
            ".price_color"
        )

        if price_element:
            price_text = clean_text(
                price_element.get_text()
            )
        else:
            price_text = ""

        # First attempt
        price_gbp = convert_price(
            price_text
        )

        # ----------------------------------------------------
        # Fallback Price Extraction
        # ----------------------------------------------------

        if price_gbp == 0.0:

            price_match = re.search(
                r"£\s*(\d+(?:\.\d{2})?)",
                str(book)
            )

            if price_match:

                try:
                    price_gbp = float(
                        price_match.group(1)
                    )

                except ValueError:
                    price_gbp = 0.0

        # ----------------------------------------------------
        # Rating
        # ----------------------------------------------------

        rating_element = book.select_one(
            ".star-rating"
        )

        rating = extract_rating(
            rating_element
        )

        # ----------------------------------------------------
        # Availability
        # ----------------------------------------------------

        availability_element = book.select_one(
            ".availability"
        )

        if availability_element:
            availability = clean_text(
                availability_element.get_text()
            )
        else:
            availability = ""

        # ----------------------------------------------------
        # Image URL
        # ----------------------------------------------------

        image_element = book.select_one(
            "img"
        )

        if image_element:

            image_url = image_element.get(
                "src",
                ""
            )

            image_url = urljoin(
                "https://books.toscrape.com/",
                image_url
            )

        else:
            image_url = ""

        # ----------------------------------------------------
        # Book Record
        # ----------------------------------------------------

        book_data = {
            "title": title,
            "price_gbp": price_gbp,
            "rating": rating,
            "availability": availability,
            "product_url": product_url,
            "image_url": image_url,
            "source_page": page_number,
        }

        books.append(
            book_data
        )

    logger.info(
        "Page %s contains %s books",
        page_number,
        len(books)
    )

    return books


# ============================================================
# Save CSV
# ============================================================

def save_csv(books):
    """
    Save scraped books to CSV.
    """

    fieldnames = [
        "title",
        "price_gbp",
        "rating",
        "availability",
        "product_url",
        "image_url",
        "source_page",
    ]

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            books
        )

    logger.info(
        "CSV saved: %s",
        CSV_FILE
    )


# ============================================================
# Save JSON
# ============================================================

def save_json(books):
    """
    Save scraped books to JSON.
    """

    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            books,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        "JSON saved: %s",
        JSON_FILE
    )


# ============================================================
# Generate Summary Report
# ============================================================

def generate_report(
    books,
    pages_scraped,
    execution_time
):
    """
    Generate summary statistics report.
    """

    prices = [
        book["price_gbp"]
        for book in books
        if book["price_gbp"] > 0
    ]

    ratings = [
        book["rating"]
        for book in books
        if book["rating"] > 0
    ]

    # --------------------------------------------------------
    # Price Statistics
    # --------------------------------------------------------

    if prices:

        average_price = statistics.mean(
            prices
        )

        minimum_price = min(
            prices
        )

        maximum_price = max(
            prices
        )

    else:

        average_price = 0.0
        minimum_price = 0.0
        maximum_price = 0.0

    # --------------------------------------------------------
    # Rating Distribution
    # --------------------------------------------------------

    rating_distribution = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
    }

    for rating in ratings:

        if rating in rating_distribution:
            rating_distribution[rating] += 1

    # --------------------------------------------------------
    # Availability
    # --------------------------------------------------------

    availability_distribution = {}

    for book in books:

        availability = book[
            "availability"
        ]

        availability_distribution[
            availability
        ] = availability_distribution.get(
            availability,
            0
        ) + 1

    # --------------------------------------------------------
    # Report Content
    # --------------------------------------------------------

    report_lines = [

        "==========================================",
        "AUTOMATED WEB SCRAPING ETL REPORT",
        "==========================================",
        "",
        "Source",
        "------------------------------------------",
        "Books to Scrape",
        "https://books.toscrape.com/",
        "",
        f"Pages Scraped      : {pages_scraped}",
        f"Total Books        : {len(books)}",
        f"Execution Time     : {execution_time:.2f} seconds",
        "",
        "PRICE STATISTICS",
        "------------------------------------------",
        f"Average Price      : £{average_price:.2f}",
        f"Minimum Price      : £{minimum_price:.2f}",
        f"Maximum Price      : £{maximum_price:.2f}",
        "",
        "RATING DISTRIBUTION",
        "------------------------------------------",
        f"1 Star             : {rating_distribution[1]} books",
        f"2 Star             : {rating_distribution[2]} books",
        f"3 Star             : {rating_distribution[3]} books",
        f"4 Star             : {rating_distribution[4]} books",
        f"5 Star             : {rating_distribution[5]} books",
        "",
        "AVAILABILITY",
        "------------------------------------------",
    ]

    for status, count in sorted(
        availability_distribution.items()
    ):
        report_lines.append(
            f"{status}: {count}"
        )

    report_lines.extend(
        [
            "",
            "OUTPUT FILES",
            "------------------------------------------",
            f"CSV  : {CSV_FILE}",
            f"JSON : {JSON_FILE}",
            f"REPORT : {REPORT_FILE}",
            "",
            "==========================================",
        ]
    )

    report_content = "\n".join(
        report_lines
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            report_content
        )

    logger.info(
        "Summary report saved: %s",
        REPORT_FILE
    )

    return (
        average_price,
        minimum_price,
        maximum_price,
        rating_distribution,
        availability_distribution,
    )


# ============================================================
# Main Scraper
# ============================================================

def main():

    print()
    print(
        "=========================================="
    )
    print(
        "Automated Web Scraping ETL Pipeline"
    )
    print(
        "=========================================="
    )
    print()

    ensure_directories()

    session = create_session()

    all_books = []

    pages_scraped = 0

    start_time = time.time()

    # --------------------------------------------------------
    # Scrape Pages
    # --------------------------------------------------------

    for page_number in range(
        1,
        MAX_PAGES + 1
    ):

        print(
            f"Scraping page {page_number}/{MAX_PAGES}..."
        )

        html = fetch_page(
            session,
            page_number
        )

        if html is None:

            print(
                f"Failed to scrape page {page_number}"
            )

            continue

        books = parse_books(
            html,
            page_number
        )

        if books:

            all_books.extend(
                books
            )

            pages_scraped += 1

        # ----------------------------------------------------
        # Rate Limiting
        # ----------------------------------------------------

        if page_number < MAX_PAGES:

            time.sleep(
                RATE_LIMIT_SECONDS
            )

    # --------------------------------------------------------
    # Execution Time
    # --------------------------------------------------------

    execution_time = (
        time.time() - start_time
    )

    # --------------------------------------------------------
    # Save Data
    # --------------------------------------------------------

    save_csv(
        all_books
    )

    save_json(
        all_books
    )

    # --------------------------------------------------------
    # Generate Report
    # --------------------------------------------------------

    (
        average_price,
        minimum_price,
        maximum_price,
        rating_distribution,
        availability_distribution,
    ) = generate_report(
        all_books,
        pages_scraped,
        execution_time
    )

    # --------------------------------------------------------
    # Console Summary
    # --------------------------------------------------------

    print()
    print(
        "=========================================="
    )
    print(
        "SCRAPING COMPLETED"
    )
    print(
        "=========================================="
    )

    print(
        f"Pages Scraped      : {pages_scraped}"
    )

    print(
        f"Total Books        : {len(all_books)}"
    )

    print(
        f"Execution Time     : {execution_time:.2f} seconds"
    )

    print(
        f"Average Price      : £{average_price:.2f}"
    )

    print(
        f"Minimum Price      : £{minimum_price:.2f}"
    )

    print(
        f"Maximum Price      : £{maximum_price:.2f}"
    )

    print()
    print(
        "Rating Distribution:"
    )

    for rating in range(
        1,
        6
    ):

        print(
            f"  {rating} Star : "
            f"{rating_distribution[rating]} books"
        )

    print()
    print(
        "Availability:"
    )

    for status, count in sorted(
        availability_distribution.items()
    ):

        print(
            f"  {status}: {count}"
        )

    print()
    print(
        "Output Files:"
    )

    print(
        f"  CSV    : {CSV_FILE}"
    )

    print(
        f"  JSON   : {JSON_FILE}"
    )

    print(
        f"  Report : {REPORT_FILE}"
    )

    print(
        f"  Log    : {LOG_FILE}"
    )

    print(
        "=========================================="
    )


# ============================================================
# Program Entry Point
# ============================================================

if __name__ == "__main__":
    main()