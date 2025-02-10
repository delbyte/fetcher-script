import requests
from bs4 import BeautifulSoup
import re
import time
import csv
from googleapiclient.discovery import build
import random

# Google Custom Search API setup
API_KEY = 'YOUR_GOOGLE_API_KEY'
CSE_ID = 'YOUR_GOOGLE_CSE_ID'


def google_search(query, max_retries=5):
    """
    Perform a Google search using the Custom Search API with exponential backoff.

    :param query: Search query.
    :param max_retries: Maximum number of retries.
    :return: List of URLs.
    """
    service = build("customsearch", "v1", developerKey=API_KEY)
    retry_count = 0
    backoff_time = 1  # Initial backoff time in seconds

    while retry_count < max_retries:
        try:
            res = service.cse().list(q=query, cx=CSE_ID).execute()
            return [item['link'] for item in res.get('items', [])]
        except Exception as e:
            print(f"Error fetching search results: {e}")
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time + random.uniform(0, 1))
            backoff_time *= 2  # Exponential backoff
            retry_count += 1

    print("Max retries reached. Unable to fetch search results.")
    return []


def scrape_emails(url, author_name, max_retries=5):
    """
    Scrape emails from a given URL with exponential backoff.

    :param url: URL of the webpage to scrape.
    :param author_name: Name of the author to look for.
    :param max_retries: Maximum number of retries.
    :return: List of emails found.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    retry_count = 0
    backoff_time = 1  # Initial backoff time in seconds

    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            print(f"Error fetching the URL {url}: {e}")
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time + random.uniform(0, 1))
            backoff_time *= 2  # Exponential backoff
            retry_count += 1

    if retry_count == max_retries:
        print(f"Max retries reached. Unable to fetch {url}.")
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
    field = input("Enter the field of research: ")
    num_emails = int(input("Enter the number of emails you want to find: "))
    author_name = input("Enter the author's name to look for: ")

    # Construct search query
    search_query = f"site:edu {field} researchers"

    emails = []
    while len(emails) < num_emails:
        urls = google_search(search_query)
        if not urls:
            print("No more URLs to search. Stopping.")
            break

        for url in urls:
            print(f"Looking for {author_name}'s email on {url}...")
            found_emails = scrape_emails(url, author_name)
            if found_emails:
                emails.extend(found_emails)
                print(f"Found {len(found_emails)} emails on {url}.")
            else:
                print(f"No emails found on {url}.")

            if len(emails) >= num_emails:
                break

        if len(emails) >= num_emails:
            break

    if emails:
        print(f"Total emails found: {len(emails)}")
        save_to_csv(emails, 'researcher_emails.csv')
        print("Emails saved to 'researcher_emails.csv'.")
    else:
        print("No emails found.")


if __name__ == "research_scraper.py":
    main()