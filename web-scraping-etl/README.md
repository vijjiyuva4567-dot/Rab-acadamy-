# Automated Web Scraping & Data Extraction Pipeline

## Project Overview

This project implements an automated ETL web scraping pipeline using Python, Requests, and BeautifulSoup.

The pipeline extracts structured book information from the public website:

https://books.toscrape.com/

The extracted information is transformed into structured records and exported into CSV and JSON files.

An automated analytical summary report is also generated after each execution.

---

## Features

- Automated web scraping
- Requests-based HTTP client
- BeautifulSoup HTML parsing
- Custom HTTP headers
- Rate limiting
- Automatic retry logic
- Timeout handling
- Error handling
- Duplicate removal
- Data transformation
- CSV export
- JSON export
- Summary statistics
- Execution logging

---

## Target Dataset

The project uses:

**Books to Scrape**

Website:

https://books.toscrape.com/

The website provides sample book data for web scraping practice.

The scraper extracts:

- Book title
- Price
- Rating
- Availability
- Product URL
- Image URL
- Source page

---

## Technologies Used

- Python
- Requests
- BeautifulSoup
- CSV
- JSON
- urllib3
- Logging

---

## ETL Architecture

The project follows an ETL architecture:

### 1. Extract

Requests downloads the HTML pages from the target website.

### 2. Transform

BeautifulSoup parses the HTML.

The extracted values are cleaned and converted into structured Python dictionaries.

Prices are converted from strings into floating-point numbers.

Ratings are converted from text values into numerical values.

Duplicate records are removed.

### 3. Load

The transformed data is saved as:

```text
data/books.csv
data/books.json