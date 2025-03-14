import models
import config
import requests
import json
import re
import tiktoken
import time


# return the rest time between two search api calls
def get_search_rest(search_type):
    if search_type == 'code':
        return 60 / config.code_search_rate_limit_per_min
    else:
        return 60 / config.others_search_rate_limit_per_min

def send_search_request(query, search_type, page: int):
    resp = requests.get(config.url_template.format(search_type, query, str(config.per_page), str(page)), headers=config.headers)
    if resp.status_code != 200:
        return [], 0
    else:
        resp_json = json.loads(resp.text)
        return resp_json["items"], resp_json["total_count"]

# note that code can be searched 10 times per minute；others can 30 times per minute
def search_all_pages(query, search_type):
    rest_time = get_search_rest(search_type)
    page = 1
    total_count = 1    # suppose at least one search result, this will be changed in loop
    current_amount = 0
    ret = list() # prevent from inconsistent results due to time
    while current_amount < total_count:
        page_items, total_count = send_search_request(query, search_type, page)
        if total_count == 0:   
            return ret
        current_amount += len(page_items)
        ret += page_items
        page += 1
        time.sleep(rest_time)
    
    return ret

# construct time slice query string
def search_time_slice(query, search_type, time_slice):
    query_time_filtered = query + f" created:{time_slice[0]}..{time_slice[1]}" # example: cats created:2016-04-30..2016-07-04
    return search_all_pages(query_time_filtered, search_type)

def search_language_slice(query, language):
    query_language_flitered = query + f" language:{language}"
    return search_all_pages(query_language_flitered, search_type="code")

 

def get_obj_from_search_type(search_type):
    if search_type not in config.search_types:
        print('error!')
        exit()
    model_name = config.github_types[search_type]
    return eval(model_name)()


# replace the json default encoder
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.__dict__
    

def get_matches(pattern, string):
    try:
        compiled_regex = re.compile(pattern)
    except:
        return []
    return compiled_regex.findall(string)

def get_page_content(source_url,headers=None):
    page = requests.get(source_url,headers=headers)
    if page.status_code != 200:
        print(f"error in fetching {source_url}")
        return ""
    return page.text

# Return all share links found within the same GitHub search result item;
# only one mention is needed since these links originate from the same source.
def get_ChatgptSharings(sharing_links: list, mention):
    return [models.ChatgptSharing(sharing_link, mention) for sharing_link in sharing_links]

def get_next_prompt(conversation):
    if len(conversation)==0:
        return None, []
    while len(conversation) != 0 and conversation[0].get("message", None) is None:
        conversation = conversation[1:]
    if len(conversation) == 0:
        return None, []
    while len(conversation) != 0 and conversation[0]["message"]["author"]["role"] != "user":
        conversation = conversation[1:]
    if len(conversation) == 0:
        return None, []
    else:
        return conversation[0]["message"]["content"]["parts"][0], conversation[1:]    # 返回user prompt以及剩下的线性对话

# There are two types of system roles: system and assistant.
def get_next_answer(conversation):
    if len(conversation)==0:
        return None, []
    while len(conversation) != 0 and conversation[0].get("message", None) is None:
        conversation = conversation[1:]
    if len(conversation) == 0:
        return None, []
    while len(conversation) != 0 and (conversation[0]["message"]["author"]["role"] != "assistant"):
        conversation = conversation[1:]
    if len(conversation) == 0:
        return None, []
    while len(conversation) != 0 and conversation[0]["message"]["content"].get("parts") is None:
        conversation = conversation[1:]
    if len(conversation) == 0:
        return None, []
    else:
        return conversation[0]["message"]["content"]["parts"][0], conversation[1:]    # Return the GPT answer along with the remaining linear conversation.


def extract_conversations(linear_conversation):
    ret = list()
    while True:
        prompt, linear_conversation = get_next_prompt(linear_conversation)
        if prompt is None:
            break
        else:
            answer, linear_conversation = get_next_answer(linear_conversation)
            if answer is None:
                break
            conversation = models.Conversation(prompt, answer)
            ret.append(conversation)
    return ret
    


code_pattern = re.compile(config.code_regex, re.DOTALL)
language_pattern = re.compile(config.language_type_regex)


def extract_code_type_and_content(code):
    found = language_pattern.findall(code)
    if len(found) != 1:
        return None, code[3:-3] # The type was not recognized, so return without the enclosing backticks.
    else:
        return found[0][3:-1], code.replace(found[0],"")[:-3]       # Return the language type and remove the type information and backticks.
    

def token_cal(model, content):
    try:    # Attempt to access the model's tokenizer.
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(content))
    except: # return -1 if fail
        return -1
    



def get_repo_info(repo_id):
    repo_url = f'https://api.github.com/repositories/{repo_id}'
    response = requests.get(repo_url, headers=config.headers_rest_api)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code} - {response.json()}')
        return None

def get_repo_languages(repo_full_name):
    languages_url = f'https://api.github.com/repos/{repo_full_name}/languages'
    response = requests.get(languages_url, headers=config.headers_rest_api)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code} - {response.json()}')
        return None
    

