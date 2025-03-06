# Researcher Email Fetcher

This Python script, `research_scraper.py`, is a tool designed to scrape web pages and collect email addresses of researchers in a specific field. It processes links, filters irrelevant ones, and extracts emails for storage in a CSV file, enabling efficient access to contact information.



---

## Features

### 1. **Web Scraping**
- The script fetches and parses HTML content from a user-defined starting URL.
- Utilizes the `BeautifulSoup` library to analyze the structure of web pages and extract relevant content.

### 2. **Email Extraction**
- Uses advanced regular expressions to locate and extract email addresses embedded in web page content.
- Handles duplicates by ensuring only unique email addresses are saved.

### 3. **Link Filtering**
- Filters out irrelevant links (e.g., links containing terms like "helpful links" or "IT support") to optimize processing.
- Ensures focus remains on researcher-related pages.

### 4. **Error Handling**
- Implements retry logic with exponential backoff using the `backoff` library to handle transient network issues gracefully.
- Logs errors for debugging and ensures the script doesn’t crash on encountering minor issues.

### 5. **Output Management**
- Collected email addresses are saved to a structured CSV file for easy access and integration into other tools.
- File is named `researcher_emails.csv` by default, but you can modify the script to set a custom name.



---

## Requirements

To use this script, ensure you have the following installed:

- Python 3.6+
- Required Python libraries:  
  ```bash
  pip install -r requirements.txt

The requirements.txt file includes:

requests: For making HTTP requests.

beautifulsoup4: For parsing HTML content.

backoff: For retry logic on network failures.



---

## How to Use

#### Step 1: Clone the Repository

Clone this repository to your local machine using:

git clone https://github.com/delbyte/fetcher-script.git
cd fetcher-script

#### Step 2: Set the Target URL

Open research_scraper.py and update the TARGET_URL variable with the starting URL for scraping. For example:

TARGET_URL = "https://example.com/researchers"

#### Step 3: Run the Script

Execute the script:

python research_scraper.py

#### Step 4: Review Output

After successful execution:

A CSV file named researcher_emails.csv will be created in the working directory.

The file will contain a list of unique email addresses extracted from the target URL and its relevant links.



---

## Advanced Options

### Customizing Link Filtering

Modify the IRRELEVANT_TERMS list to include or exclude specific keywords that determine if a link is relevant. For example:

IRRELEVANT_TERMS = ["careers", "contact us", "support", "terms"]

### Adjusting Delays

The script includes randomized delays to prevent overloading servers. You can adjust this in the main scraping loop to match your use case:

time.sleep(random.uniform(1, 3))



---

## Considerations and Best Practices

### Respect Website Policies:

Always ensure you have permission to scrape a website.

Adhere to the website's terms of service and avoid scraping if prohibited.


### Handle Ethical Concerns:

Use the data responsibly and comply with data privacy laws like GDPR.

Inform website owners if you intend to use the data commercially.


### Avoid Server Overloading:

Do not scrape large amounts of data in short periods.

Use appropriate delays between requests, as included in the script.




---
##TODO

-[ ] Make a simple UI for inputting the field and number of researchers. 
-[ ] Find a way to make the results faster. 
-[ ] Find a way to make sure the same results are not acquired if you run the same field multiple times. 
-[ ] Make some sort of implementation where multiple people could use the app at the same time and get distinct responses (webdev part)



---

## Troubleshooting

### Common Errors:

Network Errors: Ensure your internet connection is stable. The script retries failed requests using exponential backoff.

Invalid URLs: Double-check that the TARGET_URL is correct and accessible.

Empty CSV File: This can occur if:

No emails were found on the target page.

The page structure has changed. In such cases, inspect the HTML structure and update the script accordingly.




---

## License

This project is licensed under the MIT License. See the LICENSE file for details.


---

## Disclaimer

This script is for educational purposes only. Unauthorized web scraping can violate website policies or laws. Always obtain proper permissions before scraping data.



