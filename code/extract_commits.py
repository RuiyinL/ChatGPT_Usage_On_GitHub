from models import githubCommit
import utils
import json


with open("./search_results/commits_search_results.json", mode="r", encoding="utf-8") as f:
    results = json.load(f)


commits_extract = []
count = 1
print(f"Extract type commits, {len(results)} search results in total.")
try:
    for result in results:
        obj = githubCommit()
        obj.handle(result)
        commits_extract.append(obj)
        print(f"No.{count} of {len(results)} done")
        count+=1
finally: 
    with open(f"./data/commits_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump({"Source": commits_extract}, f, cls=utils.MyEncoder, indent=4)
    with open(f"./data/errors_commits_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump(githubCommit.error_record, f, cls=utils.MyEncoder, indent=4)