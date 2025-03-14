import json

types = ["code", "commits", "discussion", "issues", "pullrequests"]
results = []

links_count = 0
links_available_count = 0


for type in types:
    statistics_data = dict()
    statistics_data["type"] = type
    filename = "./cleaned/" + type + "_sharings.json" # note that the data source is the cleaned data
    with open(filename, mode="r", encoding="utf-8") as f:
        content = json.load(f)
    sources = content.get("Source")
    statistics_data["source_length"] = len(sources)
    visitable = 0
    unvisitable = 0

    open_links = 0
    close_links = 0
    open_available = 0
    close_available = 0 # the four ones are only used for type issues

    for source in sources:
        sharings = source["ChatgptSharing"]
        if sharings is None:
            continue
        for sharing in sharings:
            if type == "issues":
                state = source["State"]
                if state == "open":
                    open_links += 1
                else:
                    close_links += 1

            if sharing["Status"] != 200:
                unvisitable += 1
            else:
                visitable += 1

                if type == "issues":
                    state = source["State"]
                    if state == "open":
                        open_available += 1
                    else:
                        close_available += 1

    statistics_data["links_count"] = unvisitable + visitable
    statistics_data["visitable"] = visitable
    statistics_data["unvisitable"] = unvisitable
    if type == "issues":
        statistics_data["open_links"] = open_links
        statistics_data["close_links"] = close_links
        statistics_data["open_available"] = open_available
        statistics_data["close_available"] = close_available

    results.append(statistics_data)
    
    links_count += unvisitable + visitable
    links_available_count += visitable

print(results)

print(f"In total:\nlinks:{links_count}\nlinks_available: {links_available_count}")