import requests
from bs4 import BeautifulSoup
import pdfkit

def fetch_arxiv_abstracts(query, max_results=15):
    """
    Fetch abstracts from arXiv for a given query.
    """
    search_url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"

    response = requests.get(search_url)

    if response.status_code != 200:
        print("Failed to fetch data")
        return []

    soup = BeautifulSoup(response.content, 'xml')

    entries = soup.find_all('entry')

    abstracts = []
    for entry in entries:
        title = entry.title.text.strip()
        abstract = entry.summary.text.strip()

        abstracts.append((title, abstract))

    return abstracts

# def get_upcoming_conferences():
#     url = 'https://conferenceindex.org/conferences/artificial-intelligence'
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     conferences = []
#     for card in soup.select('.event'):
#         try:
#             title = card.select_one('.title').text.strip()
#             date = card.select_one('.date').text.strip()
#             location = card.select_one('.location').text.strip()
#             link = 'https://conferenceindex.org' + card.select_one('a')['href']
#             conferences.append({
#                 'title': title,
#                 'date': date,
#                 'location': location,
#                 'link': link
#             })
#         except Exception as e:
#             continue  # skip any broken structure

#     return conferences

# def get_upcoming_conferences():
#     return [
#         {
#             "title": "AI Conference 2025",
#             "date": "June 10, 2025",
#             "location": "San Francisco, USA",
#             "link": "https://example.com/conf1"
#         },
#         {
#             "title": "NLP Summit Europe",
#             "date": "July 22, 2025",
#             "location": "Berlin, Germany",
#             "link": "https://example.com/conf2"
#         }
#     ]


from playwright.sync_api import sync_playwright

import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

def get_upcoming_conferences(pages_to_scrape=5):
    all_results = []
    
    for page_number in range(1, pages_to_scrape + 1):
        url = f"http://www.wikicfp.com/cfp/call?conference=ai&page={page_number}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print("Failed to fetch WikiCFP page:", url)
                continue  # Skip to the next page instead of returning early

            soup = BeautifulSoup(response.text, "html.parser")
            container = soup.find("div", class_="contsec")
            if not container:
                continue

            table = container.find("table")
            if not table:
                continue

            rows = table.find_all("tr")

            for row in rows:
                # Skip header rows or navigation rows
                if row.find("th"):
                    continue
                
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue
                
                # Check for valid <a> link in the first column
                link_tag = cols[0].find("a")
                if not link_tag:
                    continue
                link_href = link_tag.get("href", "")
                # Only accept real CFP links
                if "/cfp/" not in link_href or "servlet" in link_href:
                    continue

                # Extract data
                title = link_tag.get_text(strip=True)
                link = "http://www.wikicfp.com" + link_href
                date_str = cols[1].get_text(strip=True)
                location = cols[2].get_text(strip=True)
                deadline = cols[3].get_text(strip=True)

                all_results.append({
                    "title": title,
                    "date": date_str,
                    "deadline": deadline,
                    "location": location,
                    "link": link
                })

        except Exception as e:
            print(f"Error scraping page {url}: {e}")
            # continue with other pages

    # If still no results after scraping multiple pages, return fallback
    if not all_results:
        return [{
            "title": "No conferences found on WikiCFP",
            "date": "",
            "deadline": "",
            "location": "",
            "link": "#"
        }]

    return all_results

# def save_abstracts_to_pdf(abstracts, filename="abstracts.pdf"):
#     html_content = "<html><body>"
#     for title, abstract in abstracts:
#         html_content += f"<h2>{title}</h2><p>{abstract}</p><hr>"
#     html_content += "</body></html>"

#     # Assuming wkhtmltopdf is installed and accessible system-wide
#     pdfkit.from_string(html_content, filename)
