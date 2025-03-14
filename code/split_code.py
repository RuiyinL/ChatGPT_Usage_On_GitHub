import json
single_file_length = 300

with open("./cleaned/code_sharings.json", mode="r", encoding="utf-8") as f:
    content = json.load(f)

sources = content["Source"]
sources_len = len(sources)
file_count = 1
while file_count <= 5:
    with open(f"./code_sharings_0{str(file_count)}.json", mode="w", encoding="utf-8") as f:
        json.dump({"Source": sources[(file_count-1)*single_file_length : (file_count*single_file_length)]}, f, indent=4)
    file_count += 1
with open("./code_sharings_06.json", mode="w", encoding="utf-8") as f:
        json.dump({"Source": sources[1500:]}, f,indent=4)