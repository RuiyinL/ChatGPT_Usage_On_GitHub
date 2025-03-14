from models import githubIssue
import utils
import json


with open("./search_results/issues_seperated_from_issues_rest_api.json") as f:
    results = json.load(f)


issues_extract = []
count = 1
print(f"Extract type issues, {len(results)} search results in total.")
try:
    for result in results:
        obj = githubIssue()
        obj.handle(result)
        issues_extract.append(obj)
        print(f"No.{count} of {len(results)} done")
        count+=1
finally: 
    with open(f"./data/issues_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump({"Source": issues_extract}, f, cls=utils.MyEncoder, indent=4)
    with open(f"./data/errors_issues_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump(githubIssue.error_record, f, cls=utils.MyEncoder, indent=4)