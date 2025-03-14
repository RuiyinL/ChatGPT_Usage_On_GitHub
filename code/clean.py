import json
import re
from emoji import demojize  # delete all emojis for english only encoding
# e.g., demojize("Hello World!😊") --> "Hello World!:smiling_face_with_smiling_eyes:"

types = ["code", "commits", "discussion", "issues", "pullrequests"]



def contains_non_english(text):
    if text is None:
        return True
    return bool(re.search(r'[^\x00-\x7F]', demojize(text)))

def get_text(source):
    match source["Type"]:
        case "code":
            return source["Content"]
        case "commit":
            return source["Message"]
        case "issue":
            return source["Body"]
        case "discussion":
            return source["Body"]
        case "pull request":
            return source["Body"]
        case _:
            return ""

total_source_count = 0
valid_source_count = 0

for type in types:
    no_sharing_filed = 0
    non_english_encoding = 0    # count how they fail

    filename = "./data/" + type + "_sharings.json"
    with open(filename, mode="r", encoding="utf-8") as f:
        content = json.load(f)
    sources = content["Source"]
    total_source_count += len(sources)
    valid_sources = []
    invalids = []
    for source in sources:
        if source["ChatgptSharing"] is None:
            no_sharing_filed += 1
            continue
        text = get_text(source, type)
        flag =  not contains_non_english(text)  # if contains only english
        if not flag:
            non_english_encoding += 1
            invalids.append(source)
            continue
        if len(source["ChatgptSharing"]) == 0:
            no_sharing_filed += 1
            invalids.append(source)
            continue
        
        valid_sources.append(source)

    valid_source_count += len(valid_sources)
    print(f"type: {type}\ntotal_source:{len(sources)}\nvalid_source:{len(valid_sources)}\n")
    print(f"type: {type}\nno_sharing_field: {no_sharing_filed}\nnon_english_encoding: {non_english_encoding}\n")

    with open(f"cleaned/{type}_sharings.json", mode='w', encoding='utf-8') as f:
        json.dump({"Source": valid_sources}, f,indent=4)
    with open(f"cleaned/invalid_samples_{type}_sharings.json", mode='w', encoding='utf-8') as f:
        json.dump({"Source": invalids}, f, indent=4)

print(f"In total:\nsources: {total_source_count}\nvalid_source_count: {valid_source_count}")