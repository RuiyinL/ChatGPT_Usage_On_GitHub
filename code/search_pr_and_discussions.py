import requests
import json
from bs4 import BeautifulSoup
import time
import config

webpage_url_template = "https://github.com/search?q=chat.openai.com%2Fshare&type={}&p={}"


def parse_result(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    data = soup.find(attrs = {"type":"application/json", "data-target": "react-app.embeddedData"})
    if data is None or len(data)!=1:
        return
    j = json.loads(data.contents[0])
    return j


types = ["pullrequests","discussions"]
for type in types:
    results = []
    page = 1
    try:
        while True:
            resp = requests.get(webpage_url_template.format(type, str(page)), headers=config.headers_webpage)
            if resp.status_code != 200:
                print(f"error {resp.status_code}! {type} in Page is {str(page)}\n{str(len(results))} in total.")
                break
            j = parse_result(resp.content)
            items = j["payload"]["results"]
            results += items
            page += 1
            time.sleep(1)
    finally:
        with open(f"./search_results/{type}_search_results.json", encoding='utf-8', mode='w') as f:
            json.dump(results, f, indent=4)
        print(f"Type: {type}; SearchResultCount:{len(results)}")