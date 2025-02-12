import os
import logging
from dotenv import load_dotenv
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
import re
import time
import csv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
load_dotenv()

# Get API key and CSE ID from environment variables
API_KEY = os.getenv('GOOGLE_API_KEY')
CSE_ID = os.getenv('GOOGLE_CSE_ID')


def google_search(query):
    """
    Perform a Google search using the Custom Search API.

    :param query: Search query.
    :return: List of URLs.
    """
    service = build("customsearch", "v1", developerKey=API_KEY)
    try:
        res = service.cse().list(q=query, cx=CSE_ID).execute()
        return [item['link'] for item in res.get('items', [])]
    except Exception as e:
        logging.warning(f"Error during Google search: {e}")
        return []


def scrape_author_names(url):
    """
    Scrape author names from a given URL.

    :param url: URL of the webpage to scrape.
    :return: List of author names.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.warning(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    author_names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', soup.get_text())

    return author_names


def scrape_emails(url, author_name):
    """
    Scrape emails from a given URL.

    :param url: URL of the webpage to scrape.
    :param author_name: Name of the author to look for.
    :return: List of emails found.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.warning(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())

    # Filter emails to include only those related to the author
    filtered_emails = [email for email in emails if author_name.lower() in email.lower()]

    return filtered_emails


def save_to_csv(emails, filename):
    """
    Save emails to a CSV file.

    :param emails: List of emails.
    :param filename: Name of the CSV file.
    """
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for email in emails:
            writer.writerow({'Email': email})


def main():
    field = input("Enter the field of research (e.g., 'machine learning'): ")
    num_emails = int(input("Enter the number of emails you want to find: "))

    # Construct search query to find author names
    search_query = f"site:edu {field} researchers"

    # Find URLs with author names
    urls = google_search(search_query)

    author_names = []
    emails = []

    for url in urls:
        if len(author_names) >= num_emails * 3:  # Fetch extra author names for redundancy
            break

        logging.info(f"Searching for authors on {url}...")
        names = scrape_author_names(url)
        if names:
            author_names.extend(names)
        else:
            logging.warning(f"No author names found on {url}.")

    if not author_names:
        logging.error("No author names found. Exiting.")
        return

    for author_name in author_names:
        if len(emails) >= num_emails:
            break

        logging.info(f"Looking for {author_name}'s email...")
        search_query = f"site:edu {author_name} email"
        urls = google_search(search_query)

        for url in urls:
            if len(emails) >= num_emails:
                break

            found_emails = scrape_emails(url, author_name)
            if found_emails:
                emails.extend(found_emails)
                logging.info(f"Found {len(found_emails)} emails for {author_name} on {url}.")
            else:
                logging.warning(f"No emails found for {author_name} on {url}.")

    if emails:
        logging.info(f"Total emails found: {len(emails)}")
        save_to_csv(emails, 'researcher_emails.csv')
        logging.info("Emails saved to 'researcher_emails.csv'.")
    else:
        logging.error("No emails found.")


if __name__ == "__main__":
    main()

