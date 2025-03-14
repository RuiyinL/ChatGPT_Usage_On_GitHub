from models import githubDiscussion
import utils
import json
import requests

with open("./search_results/discussions_search_results.json") as f:
    results = json.load(f)


discussion_extract = []
count = 1
print(f"Extract type discussion, {len(results)} search results in total.")
try:
    for result in results:
        discussion_url = "https://github.com" + result["url"]
        obj = githubDiscussion(discussion_url)
        obj.handle(result)
        discussion_extract.append(obj)
        print(f"No.{count} of {len(results)} done")
        count+=1
finally: 
    with open(f"./data/discussion_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump({"Source": discussion_extract}, f, cls=utils.MyEncoder, indent=4)
    with open(f"./data/errors_discussion_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump(githubDiscussion.error_record, f, cls=utils.MyEncoder, indent=4)