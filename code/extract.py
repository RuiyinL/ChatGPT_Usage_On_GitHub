import pandas as pd
import json

def get_date(date):
    if date == "":
        return ""
    return date.split("T")[0]

def length_limit(string):
    if len(string) > 32767:
        return "The Content is too long for a single excel unit, please visit the original page."
    else:
        return string


def get_common_info(type, source):
    # for each type, return the required fields.
    # e.g.: type code needs URL,ObjectSha,FileName and FilePath
    ret = dict()
    ret["URL"] = source["URL"]
    match type:
        case "code":
            ret["ObjectSha"] = source["ObjectSha"]
            ret["FileName"] = source["FileName"]
            ret["FilePath"] = source["FilePath"]
            ret["Content"] = "[CODE SNIPPETS]"
        case "commit":
            ret["Sha"] = source["Sha"]
            ret["Message"] = length_limit(source["Message"])
            ret["RepoName"] = source["RepoName"]
            ret["CommitAt"] = get_date(source["CommitAt"])
        case "discussion":
            ret["Title"] = source["Title"]
            ret["Body"] = length_limit(source["Body"])
            ret["AuthorAt"] = get_date(source["AuthorAt"])
            ret["Closed"] = source["Closed"]
        case "issue":
            ret["Title"] = source["Title"]
            ret["Body"] = length_limit(source["Body"])
            ret["AuthorAt"] = get_date(source["AuthorAt"])
            ret["State"] = source["State"]
        case "pull request":
            ret["Title"] = source["Title"]
            ret["Body"] = length_limit(source["Body"])
            ret["CreatedAt"] = get_date(source["CreatedAt"])
            ret["State"] = source["State"]
    return ret

def get_sharing_info(sharing):
    ret = dict()
    ret["ChatgptSharing_URL"] = sharing["URL"]

    try:
        ret["ChatgptSharing_DateOfConversation"] = sharing["DateOfConversation"].split(" ")[0]
    except:
        print("Time split error: ", sharing["DateOfConversation"])
        ret["ChatgptSharing_DateOfConversation"] = "Error"
    
    ret["ChatgptSharing_Title"] = sharing["Title"]
    ret["ChatgptSharing_NumberOfPrompts"] = sharing["NumberOfPrompts"]

    return ret


filenames = ["code_sharings_01", "code_sharings_02",
             "code_sharings_03", "code_sharings_04",
             "code_sharings_05", "code_sharings_06",
             "commits_sharings", "discussion_sharings",
             "issues_sharings", "pullrequests_sharings"]



for filename in filenames:
    file = ".\\cleaned\\" + filename + ".json"   # note that you should change the path to fit your setting
    with open(file, mode="r", encoding="utf-8") as f:
        sources = json.load(f).get("Source")
    
    selected = list()
    type_field = sources[0].get("Type")
    for source in sources:
        common_info = get_common_info(type_field, source)
        sharings = source.get("ChatgptSharing")
        for sharing in sharings:
            if sharing.get("Status") == 404:
                continue
            to_add = dict()
            to_add.update(common_info)
            to_add.update(get_sharing_info(sharing))
            selected.append(to_add)

    df = pd.DataFrame(selected, index=list(range(1,len(selected)+1)))
    df.to_excel(f"./extracted/extracted_{filename}.xlsx", sheet_name="Sheet1",index=True, index_label="No")