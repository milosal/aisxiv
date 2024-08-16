import requests
import xml.etree.ElementTree as ET
import google.generativeai as genai
import os
import ast
import re
import json

class ParsingError(Exception):
    pass

API_KEY = os.environ["API_KEY"]

NUM=30
START=0
CATEGORY= "cs.CY"
#"cs.CY" - Computers and Society
#"xxx" - Artificial Intelligence

print(API_KEY)

def get_last_n_papers(num_res, start=0):
    url = "http://export.arxiv.org/api/query"

    params = {
        'search_query': f'cat:{CATEGORY}',  # cs.CY is the category code for "Computers and Society"
        'start': start,                    # start at the first result
        'max_results': num_res,             # return only 10 results
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

            papers.append(f"Title: {title}, Date: {published}, Summary: {summary}")

    return papers

def get_safety_papers_from_n_recent(num_res=20, start=0):
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

    papers = get_last_n_papers(num_res, start=start)
    pass_str = '\n'.join(papers)

    full_query = "You are being used for a filtering process. All of your responses should only be python lists, in the format ['Title 1', 'Title 2', 'Title 3', ...].\nPlease return a python list that contains only the papers from this list which are relevant to AI safety, particularly with potential applications to existential risk from AI. These are likely to be papers on the topics of interpretability, red teaming, jailbreaking, AI governance, etc. I am NOT interested in bias, misinformation, social effects, financial applications, medical applications, etc.\nPlease format your response as a python list (e.g., ['Title 1', 'Title 2', 'Title 3', 'Title 4', ...]) and ONLY include the article titles. Please only include relevant articles, but include as many as are relevant. Take a deep breath and think carefully to find the right papers.\n\n" + pass_str

    response = model.generate_content(full_query)
    return response.text

def convert_to_list(papers_str):
    print(papers_str)
    match = re.search(r"\[.*\]", papers_str)
    if match:
        rel_str = match.group()
        rel_str = rel_str.replace("'", '"')
        rel_str = rel_str.replace('," "', '", "')
        lst = ast.literal_eval(rel_str)
        return lst
    else:
        raise ParsingError("No list found in model response")


res = get_safety_papers_from_n_recent(NUM, START)
papers_list = convert_to_list(res)

final_papers = []

for title in papers_list:
    retitle = title.replace("\n  ", "").strip().lower()
    final_papers.append(retitle)

print(final_papers)

if input("Looks good? ") == "y":
    with open('papers_db.json', 'r') as file:
        data = json.load(file)

    for paper in final_papers:
        if paper not in data["papers"]:
            data["papers"].append(paper)
    
    with open('papers_db.json', 'w') as file:
        json.dump(data, file, indent=4)