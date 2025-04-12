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

# def save_abstracts_to_pdf(abstracts, filename="abstracts.pdf"):
#     html_content = "<html><body>"
#     for title, abstract in abstracts:
#         html_content += f"<h2>{title}</h2><p>{abstract}</p><hr>"
#     html_content += "</body></html>"

#     # Assuming wkhtmltopdf is installed and accessible system-wide
#     pdfkit.from_string(html_content, filename)
