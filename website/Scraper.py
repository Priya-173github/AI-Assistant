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
        url = entry.id.text.strip()

        abstracts.append((title, abstract,url))

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

def get_event_details(event_url):
    details = {}
    try:
        resp = requests.get(event_url, timeout=10)
        if resp.status_code != 200:
            print("Failed to fetch detail page:", event_url)
            return details
        soup = BeautifulSoup(resp.text, "html.parser")
        detail_table = soup.find("table", attrs={"cellpadding": "3"})
        if not detail_table:
            return details
        rows = detail_table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            label = cols[0].get_text(strip=True).rstrip(":").lower()
            value = cols[1].get_text(strip=True)
            if label in ["when", "where", "deadline"]:
                details[label] = value
        return details
    except Exception as e:
        print(f"Error fetching details from {event_url}: {e}")
        return details

def get_conferences_by_topic(topic, pages_to_scrape=3):
    all_results = []
    topic_encoded = topic.replace(" ", "+")
    for page_number in range(1, pages_to_scrape + 1):
        url = f"http://www.wikicfp.com/cfp/call?conference={topic_encoded}&page={page_number}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print("Failed to fetch WikiCFP page:", url)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            container = soup.find("div", class_="contsec")
            if not container:
                continue

            table = container.find("table")
            if not table:
                continue

            rows = table.find_all("tr")

            i = 0
            while i < len(rows) - 1:
                row1 = rows[i]
                row2 = rows[i + 1]

                link_tag = row1.find("a")
                if not link_tag:
                    i += 1
                    continue

                title = link_tag.get_text(strip=True)
                link_href = link_tag.get("href", "")
                if "/cfp/" not in link_href:
                    i += 2
                    continue

                link = "http://www.wikicfp.com" + link_href

                cols2 = row2.find_all("td")
                if len(cols2) >= 3:
                    event_date = cols2[0].get_text(strip=True)
                    location = cols2[1].get_text(strip=True)
                    deadline = cols2[2].get_text(strip=True)
                else:
                    event_date = location = deadline = ""

                all_results.append({
                    "title": title,
                    "date": event_date,
                    "location": location,
                    "deadline": deadline,
                    "link": link,
                    "topic": topic
                })

                i += 2

        except Exception as e:
            print(f"Error scraping page {url}: {e}")
            continue

    if not all_results:
        return [{
            "title": f"No conferences found for topic: {topic}",
            "date": "",
            "deadline": "",
            "location": "",
            "link": "#",
            "topic": topic
        }]

    return all_results  

# def save_abstracts_to_pdf(abstracts, filename="abstracts.pdf"):
#     html_content = "<html><body>"
#     for title, abstract in abstracts:
#         html_content += f"<h2>{title}</h2><p>{abstract}</p><hr>"
#     html_content += "</body></html>"

#     # Assuming wkhtmltopdf is installed and accessible system-wide
#     pdfkit.from_string(html_content, filename)
