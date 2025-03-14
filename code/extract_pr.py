from models import githubPR
import utils
import json

with open("./search_results/pullrequests_search_results.json") as f:
    results = json.load(f)


pr_extract = []
count = 1
print(f"Extract type pr, {len(results)} search results in total.")
try:
    for result in results:
        obj = githubPR()
        obj.handle(result)
        pr_extract.append(obj)
        print(f"No.{count} of {len(results)} done")
        count+=1
finally: 
    with open(f"./data/pullrequests_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump({"Source": pr_extract}, f, cls=utils.MyEncoder, indent=4)
    with open(f"./data/errors_pullrequests_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump(githubPR.error_record, f, cls=utils.MyEncoder, indent=4)