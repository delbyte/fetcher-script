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
        print("Too many requests! Increasing backoff...")
        return "retry"
    elif response.status_code == 200:
        return response
    return None


def fetch_emails_from_orcid(orcid_url):
    """Extract email from an ORCID profile page if available."""
    if not orcid_url.startswith("http"):
        orcid_url = "https://orcid.org" + orcid_url  # Ensure full URL

    response = requests.get(orcid_url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", soup.text)
    return email_match.group(0) if email_match else None


def save_email_to_csv(author, email, filename="researcher_emails.csv"):
    """Append a collected email to a CSV file dynamically."""
    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([author, email])
    print(f"Saved: {author} - {email}")


def main():
    field = input("Enter research field: ")
    num_authors = int(input("Enter number of researchers: "))

    authors = get_authors_from_semantic_scholar(field, num_authors)
    if not authors:
        print("No authors found.")
        return

    delay = 2  # Initial delay in seconds
    min_delay = 2
    max_delay = 60  # Maximum delay limit
    consecutive_failures = 0  # Track consecutive failures

    with open("researcher_emails.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Author Name", "Email"])

    for author in authors:
        print(f"Searching for {author}'s ORCID profile...")
        while True:
            response = search_orcid_profiles(author, delay)
            if response == "retry":
                consecutive_failures += 1
                delay = min(delay * 2, max_delay)  # Exponential backoff
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                if consecutive_failures >= 3:
                    print("Multiple failures detected. Stopping execution. Try again later.")
                    return
                continue
            elif response:
                consecutive_failures = 0  # Reset failure count on success
                delay = max(delay / 1.5, min_delay)  # Reduce delay but keep a minimum
            break

        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.find_all("a", href=True):
                url = link["href"]
                if "orcid.org" in url:
                    orcid_url = url.split("&")[0]  # Extract clean ORCID link
                    if not orcid_url.startswith("http"):
                        orcid_url = "https://orcid.org" + orcid_url  # Ensure full URL
                    print(f"Found ORCID: {orcid_url}. Searching for email...")
                    email = fetch_emails_from_orcid(orcid_url)
                    if email:
                        print(f"Email found: {email}")
                        save_email_to_csv(author, email)
                    else:
                        print(f"No email found for {author}")
                    break


if __name__ == "__main__":
    main()
