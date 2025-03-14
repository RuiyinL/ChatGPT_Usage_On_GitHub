from models import githubCode
import utils
import json

with open("./search_results/code_search_results.json") as f:
    results = json.load(f)


code_extract = []
count = 1
print(f"Extract type code, {len(results)} search results in total.")
try:
    for result in results:
        obj = githubCode()
        obj.handle(result)
        code_extract.append(obj)
        print(f"No.{count} of {len(results)} done")
        count+=1
finally: 
    with open(f"./data/code_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump({"Source": code_extract}, f, cls=utils.MyEncoder, indent=4)
    with open(f"./data/errors_code_sharings.json", encoding='utf-8', mode='w') as f:
        json.dump(githubCode.error_record, f, cls=utils.MyEncoder, indent=4)