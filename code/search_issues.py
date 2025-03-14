# The search for issues can be segmented by time, but commits cannot.
import requests
import json
from bs4 import BeautifulSoup
import time
import config

rest_url_template = "https://api.github.com/search/issues?q=chat.openai.com+created:{}..{}"
fetch_rest_time = 60 / config.others_search_rate_limit_per_min

# Return the items for a specific page, along with the total number of results under the current search criteria 
# so that search_all_pages can determine whether to continue searching the next page.
def send_search_request(query, page: int):
    rest_url = query + f"&per_page=100&page={str(page)}"
    resp = requests.get(rest_url, headers=config.headers_rest_api)
    if resp.status_code != 200:
        return [], 0
    else:
        resp_json = json.loads(resp.text)
        return resp_json["items"], resp_json["total_count"]


def get_all_pages(query):
    page = 1
    total_count = 1    # suppose at least one search result, this will be changed in loop
    current_amount = 0
    ret = list() # prevent from inconsistent results due to time
    while current_amount < total_count:
        page_items, total_count = send_search_request(query, page)
        if total_count == 0:    # No search results exist for this query.
            return ret
        current_amount += len(page_items)
        ret += page_items
        page += 1
        time.sleep(fetch_rest_time)
    
    return ret

def search_time_slice(slice):
    query = rest_url_template.format(slice[0], slice[1])
    return get_all_pages(query)


results = []
try:
    for slice in config.time_slices:
        slice_result = search_time_slice(slice)
        results += slice_result
except Exception as e:
    print(e)
finally:
    with open(f"./search_results/issues_search_results.json", encoding='utf-8', mode='w') as f:
        json.dump(results, f, indent=4)
    print(f"Type: issues; SearchResultCount:{len(results)}")