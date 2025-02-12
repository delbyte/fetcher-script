import csv
import requests
import logging
import time
import re
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of irrelevant terms to filter out
IRRELEVANT_TERMS = [
    "helpful links", "service catalog", "information technology", "about us",
    "student portal", "email services", "contact us", "administrative offices",
    "calendar", "admissions", "resources", "support", "apply",
    "default.aspx", "faq", "news", "policies", "support team",
    "directions", "services", "external links", "university email",
    "technology services", "quick links", "campus map", "departments",
    "staff directory", "student life", "faculty support", "events",
    "user agreement", "privacy policy", "disclaimer", "legal information",
    "terms of service", "login", "create account", "newsletter",
    "job openings", "career opportunities", "volunteer", "partners",
    "sponsors", "press releases", "media contact", "homepage",
    "university rankings", "academic programs", "research labs", "syllabus",
    "alumni", "testimonials", "case studies", "webinar", "podcast",
    "technical support", "ticket system", "open positions", "complaints",
    "copyright", "financial aid", "scholarships", "conference schedule"
]


# Function to check if a name or term is irrelevant
def is_irrelevant(name):
    name_lower = name.lower()
    return any(term in name_lower for term in IRRELEVANT_TERMS)


# Function to scrape emails from a given URL
def scrape_emails(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Extract potential email addresses
        emails = set(re.findall(r'[\w.-]+@[\w.-]+\.\w+', text))
        return {email for email in emails if not is_irrelevant(email)}
    except HTTPError as http_err:
        logging.warning(f"HTTP error occurred while fetching {url}: {http_err}")
    except Exception as err:
        logging.warning(f"Error occurred while fetching {url}: {err}")
    return set()


# Function to search for author names and scrape emails
def find_author_emails(field, num_emails):
    logging.info(f"Searching for author emails in the field: {field}")

    search_urls = [
        f"https://scholar.google.com/scholar?q={field}",
        f"https://pubmed.ncbi.nlm.nih.gov/?term={field}",
        f"https://www.researchgate.net/search/publication?q={field}"
    ]

    found_emails = set()

    for search_url in search_urls:
        if len(found_emails) >= num_emails:
            break

        logging.info(f"Fetching search results from: {search_url}")
        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract author profile links or publication links
            links = [a['href'] for a in soup.find_all('a', href=True) if not is_irrelevant(a.text)]

            for link in links:
                if len(found_emails) >= num_emails:
                    break

                # Build the full URL if it's relative
                full_url = link if link.startswith(
                    'http') else f"{search_url.split('/')[0]}//{search_url.split('/')[2]}{link}"
                logging.info(f"Scraping potential profile: {full_url}")

                # Scrape emails from the profile or publication page
                emails = scrape_emails(full_url)
                found_emails.update(emails)

        except HTTPError as http_err:
            logging.warning(f"HTTP error occurred while accessing {search_url}: {http_err}")
        except Exception as err:
            logging.warning(f"Error occurred while processing {search_url}: {err}")

    return list(found_emails)[:num_emails]


# Function to save emails to a CSV file
def save_emails_to_csv(emails, filename="emails.csv"):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Email"])
            for email in emails:
                writer.writerow([email])
        logging.info(f"Emails successfully saved to {filename}")
    except Exception as err:
        logging.error(f"Error occurred while saving emails to CSV: {err}")


# Main script
def main():
    field = input("Enter the field of research (e.g., 'machine learning'): ")
    num_emails = int(input("Enter the number of emails you want to find: "))

    emails = find_author_emails(field, num_emails)

    if emails:
        logging.info("Found the following emails:")
        for email in emails:
            print(email)
        save_emails_to_csv(emails)
    else:
        logging.warning("No emails found.")


if __name__ == "__main__":
    main()
