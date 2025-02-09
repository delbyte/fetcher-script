import requests
import csv
import re
from bs4 import BeautifulSoup
import time


def get_authors_from_semantic_scholar(field, num_authors=10):
    """Fetch author names from Semantic Scholar based on a research field."""
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={field}&fields=authors&limit={num_authors}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching data from Semantic Scholar")
        return []

    data = response.json()
    authors = set()
    for paper in data.get("data", []):
        for author in paper.get("authors", []):
            authors.add(author.get("name", "Unknown"))

    return list(authors)


def search_orcid_profiles(author_name, delay):
    """Search for an author's ORCID profile via Google Search scraping."""
    query = f"{author_name} ORCID site:orcid.org"
    search_url = f"https://www.google.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    time.sleep(delay)  # Adaptive delay to avoid detection
    response = requests.get(search_url, headers=headers)

    if response.status_code == 429:
        print("Too many requests! Increasing delay...")
        return "retry"
    elif response.status_code == 200:
        return response
    return None


def fetch_emails_from_orcid(orcid_url):
    """Extract email from an ORCID profile page if available."""
    response = requests.get(orcid_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", soup.text)
    return email_match.group(0) if email_match else None


def save_emails_to_csv(emails, filename="researcher_emails.csv"):
    """Save collected emails to a CSV file without duplicates."""
    emails = list(set(emails))  # Remove duplicates
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Author Name", "Email"])
        writer.writerows(emails)
    print(f"Saved {len(emails)} emails to {filename}")


def main():
    field = input("Enter research field: ")
    num_authors = int(input("Enter number of researchers: "))

    authors = get_authors_from_semantic_scholar(field, num_authors)
    if not authors:
        print("No authors found.")
        return

    emails = []
    delay = 2  # Initial delay in seconds
    min_delay = 2
    max_delay = 10

    for author in authors:
        print(f"Searching for {author}'s ORCID profile...")
        while True:
            response = search_orcid_profiles(author, delay)
            if response == "retry":
                delay = min(delay * 2, max_delay)  # Increase delay but cap it
                print(f"Increasing delay to {delay} seconds...")
                continue
            elif response:
                delay = max(delay / 1.5, min_delay)  # Reduce delay but keep a minimum
            break

        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                url = link["href"]
                if "orcid.org" in url:
                    orcid_url = url.split("&")[0]  # Extract clean ORCID link
                    print(f"Found ORCID: {orcid_url}. Searching for email...")
                    email = fetch_emails_from_orcid(orcid_url)
                    if email:
                        emails.append((author, email))
                    break

    if emails:
        save_emails_to_csv(emails)
    else:
        print("No emails found.")


if __name__ == "__main__":
    main()
