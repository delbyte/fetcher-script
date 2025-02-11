import os
import time
import csv
import random
import logging
import requests
import re
from dotenv import load_dotenv
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Get API key and CSE ID from environment variables
API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def google_search(query, max_retries=5):
    """
    Perform a Google search using the Custom Search API with exponential backoff.
    """
    service = build("customsearch", "v1", developerKey=API_KEY)
    retry_count, backoff_time = 0, 1

    while retry_count < max_retries:
        try:
            res = service.cse().list(q=query, cx=CSE_ID).execute()
            return [item['link'] for item in res.get('items', [])]
        except Exception as e:
            logging.warning(f"Error fetching search results: {e}. Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
            backoff_time *= 2
            retry_count += 1

    logging.error("Max retries reached. Unable to fetch search results.")
    return []


def scrape_author_names(url, proxies=None):
    """
    Scrape author names from a given URL.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    author_regex = r'\b[A-Z][a-z]+(?: [A-Z]\.)? [A-Z][a-z]+(?:-[A-Z][a-z]+)?\b'
    author_names = re.findall(author_regex, soup.get_text())
    return list(set(author_names))


def scrape_emails(url, max_retries=5, proxies=None):
    """
    Scrape emails from a given URL with exponential backoff.
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    retry_count, backoff_time = 0, 1

    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers, proxies=proxies)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            logging.warning(f"Error fetching {url}: {e}. Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
            backoff_time *= 2
            retry_count += 1

    if retry_count == max_retries:
        logging.error(f"Max retries reached for {url}.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
    return list(set(emails))


def save_to_csv(emails, filename='researcher_emails.csv'):
    """Save emails to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Email'])
        writer.writerows([[email] for email in emails])


def main():
    field = input("Enter the field of research (e.g., 'machine learning'): ")
    num_emails = int(input("Enter the number of emails you want to find: "))

    search_query = f"site:edu {field} researchers"
    urls = google_search(search_query)

    author_names, emails = [], []
    max_author_names = 3 * num_emails

    for url in urls:
        if len(author_names) >= max_author_names:
            break
        logging.info(f"Searching for authors on {url}...")
        author_names.extend(scrape_author_names(url))
        time.sleep(random.uniform(2, 5))

    if not author_names:
        logging.error("No author names found. Exiting.")
        return

    for author_name in author_names:
        if len(emails) >= num_emails:
            break
        search_query = f"site:edu {author_name} email"
        for url in google_search(search_query):
            if len(emails) >= num_emails:
                break
            emails.extend(scrape_emails(url))
            time.sleep(random.uniform(2, 5))

    if emails:
        logging.info(f"Total emails found: {len(emails)}")
        save_to_csv(emails)
        logging.info("Emails saved to 'researcher_emails.csv'.")
    else:
        logging.warning("No emails found.")


if __name__ == "__main__":
    main()
