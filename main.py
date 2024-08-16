import requests
import xml.etree.ElementTree as ET


url = "http://export.arxiv.org/api/query"

params = {
    'search_query': 'cat:cs.CY',  # cs.CY is the category code for "Computers and Society"
    'start': 0,                    # start at the first result
    'max_results': 100,             # return only 10 results
    'sortBy': 'submittedDate',     # sort by submission date
    'sortOrder': 'descending',     # most recent first
}

res = requests.get(url, params)

papers = []

if res.status_code == 200:
    root = ET.fromstring(res.content)
    entries = root.findall('{http://www.w3.org/2005/Atom}entry')

    # Extract information from each entry
    for entry in entries:
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text

        papers.append((title, published, summary))

print(papers)

