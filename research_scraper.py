import requests
import csv
import time

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
ORCID_API_BASE = "https://pub.orcid.org/v3.0"


def get_researchers(field, num_researchers):
    """
    Fetch researchers from Semantic Scholar using the author search endpoint.
    We include the word 'researcher' in the query to target people working in the field.
    Returns a dictionary mapping researcher names to their Semantic Scholar author IDs.
    """
    query = f"{field} researcher"
    url = f"{SEMANTIC_SCHOLAR_BASE}/author/search?query={query}&limit={num_researchers}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error fetching researchers from Semantic Scholar")
        return {}

    data = response.json()
    researchers = {}
    for author in data.get("data", []):
        name = author.get("name")
        author_id = author.get("authorId")
        if name and author_id:
            # Avoid duplicates by using the researcher's name as key.
            researchers[name] = author_id
    return researchers


def get_orcid(author_id):
    """
    Fetch the ORCID ID for a given Semantic Scholar author using the author details endpoint.
    """
    url = f"{SEMANTIC_SCHOLAR_BASE}/author/{author_id}?fields=externalIds"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return data.get("externalIds", {}).get("ORCID")


def get_email(orcid_id):
    """
    Use the ORCID public API to fetch the researcher's email.
    (Note: Most ORCID emails are private; only public emails are returned.)
    """
    if not orcid_id:
        return None

    url = f"{ORCID_API_BASE}/{orcid_id}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    emails = data.get("person", {}).get("emails", {}).get("email", [])
    for email_obj in emails:
        if email_obj.get("verified", False):  # Prefer verified emails
            return email_obj.get("email")
    return None


def save_to_csv(name, email, filename="researcher_emails.csv"):
    """
    Append the researcher’s name and email to a CSV file.
    """
    with open(filename, "a", newline="") as file:
        csv.writer(file).writerow([name, email])
    print(f"Saved: {name} - {email}")


def main():
    field = input("Enter research field: ")
    try:
        num_researchers = int(input("Enter number of researchers to search: "))
    except ValueError:
        print("Invalid number provided.")
        return

    # Get researchers using the author search endpoint.
    researchers = get_researchers(field, num_researchers)
    if not researchers:
        print("No researchers found.")
        return

    # Prepare CSV file (overwrite if it exists)
    with open("researcher_emails.csv", "w", newline="") as file:
        csv.writer(file).writerow(["Researcher Name", "Email"])

    for name, author_id in researchers.items():
        print(f"\nProcessing researcher: {name}")
        orcid_id = get_orcid(author_id)
        if not orcid_id:
            print(f"No ORCID ID found for {name}")
            continue
        print(f"Found ORCID for {name}: {orcid_id}")
        email = get_email(orcid_id)
        if email:
            print(f"Email found for {name}: {email}")
            save_to_csv(name, email)
        else:
            print(f"No public email found for {name}")
        # Small delay to respect API rate limits
        time.sleep(1)


if __name__ == "__main__":
    main()
