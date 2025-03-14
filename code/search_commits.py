import requests
import json
import time
import config


rest_url = "https://api.github.com/search/commits?q=\"chat.openai.com/share\""
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
    current_amount = -100
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




results = []
try:
    results += get_all_pages(rest_url)
except Exception as e:
    print(e)
finally:
    with open(f"./search_results/commits_search_results.json", encoding='utf-8', mode='w') as f:
        json.dump(results, f, indent=4)
    print(f"Type: commits; SearchResultCount:{len(results)}")