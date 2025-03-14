token = "xxxxxx"  # Your personal github token, replace xxxxxx with it.
# see https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
target = "\"chat.openai.com/share\"" # Conduct a strict search to avoid obtaining numerous loosely matched results. 
target_regex = r"https:\/\/chat\.openai\.com\/share\/[a-zA-Z0-9-]{36}"
per_page = 100  # Set the number of result items to be retrieved with each fetch

headers_rest_api = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
           'Accept': 'application/vnd.github+json',
           'Authorization': f'Bearer {token}',
           'X-GitHub-Api-Version':'2022-11-28'}

search_types = ['code', 'commits', 'issues', 'pullrequests', 'discussions']

# map search_type to model name
github_types = {'code':'githubCode', 'commits':'githubCommit', 'issues':'githubIssue','pullrequests':'githubPR', 'discussions':'githubDiscussion'}

code_search_rate_limit_per_min = 5
others_search_rate_limit_per_min = 30

"""
    1：search type
    2：search question
    3：the number of result items in each page
    4：which page
"""
url_template = "https://api.github.com/search/{}?q={}&per_page={}&page={}"

code_replace_template = "[CODE_BLOCK_{}]"   # replace the real code blocks
code_regex = r'```.*?```|~~~.*?~~~' # Identify code segments enclosed in triple backticks.
language_type_regex = r"```.+\n"    # Identify the language used in the code block within Markdown.



# from：https://madnight.github.io/githut/#/pull_requests/2024/1
languages_top_50 = ['Python', 'Java', 'Go', 'JavaScript', 'C++', 'TypeScript', 
                    'PHP', 'Ruby', 'C', 'C#', 'Nix', 'Shell', 'Rust', 'Scala', 'Kotlin', 'Swift', 'Dart', 
                    'Groovy', 'Perl', 'Lua', 'DM', 'SystemVerilog', 'Objective-C', 'Elixir', 'CodeQL', 'OCaml', 
                    'Haskell', 'PowerShell', 'Erlang', 'Emacs Lisp', 'Julia', 'Clojure', 'R', 'CoffeeScript', 
                    'F#', 'Verilog', 'WebAssembly', 'MLIR', 'Bicep', 'Fortran', 'Cython', 'GAP', 'MATLAB', 'Puppet', 
                    'Sass', 'JetBrains MPS', 'Smalltalk', 'Vala', 'Haxe', 'Pascal']

time_slices = [("2023-05-21", "2023-6-20"), ("2023-06-21","2023-07-20"), ("2023-07-21", "2023-08-20"),
               ("2023-08-21", "2023-09-20"),("2023-09-21", "2023-10-20"), ("2023-10-21", "2023-11-20"),
               ("2023-11-21", "2023-12-20"), ("2023-12-21", "2024-1-20"), ("2024-01-21","2024-02-20"),
               ("2024-02-21", "2024-03-20"), ("2024-03-21", "2023-04-20"),("2024-04-21", "2024-05-25"),("2024-05-26", "2024-06-07")]

cookie = "_octo=GH1.1.89709404.1714271906; _device_id=f5fd00d0765500b27340efbca3584d20; saved_user_sessions=31219380%3ANKAYnn8m5tkCDR5SkbCoT0ZD5ASa2MMyM5gqez7a_tGbB6VO; user_session=NKAYnn8m5tkCDR5SkbCoT0ZD5ASa2MMyM5gqez7a_tGbB6VO; __Host-user_session_same_site=NKAYnn8m5tkCDR5SkbCoT0ZD5ASa2MMyM5gqez7a_tGbB6VO; logged_in=yes; dotcom_user=WhitenWhiten; has_recent_activity=1; color_mode=%7B%22color_mode%22%3A%22auto%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; preferred_color_mode=light; tz=Asia%2FHong_Kong; _gh_sess=qPgdF0B8%2BkJBV5Kq4ruGp5r6U%2FbB2Rj7X3qb03yxc8CMfaRQx%2Bkd%2B%2FiLrehjoBE6lxLN3RqWg9OHpXj9hxE5nLiaflAw27SAYuNcshWkeCnY4YL0pv3ZJnArJmqlND4yUzq5i%2FcRT0nV1PtZxgK50g6g0Qms6n3hrKi11iDTlwN0vMzc%2BpoPsN0cPd%2Fn%2FDHgzrL8Xor4R6HcGQWmxfC2prmvrYiA0uZqr%2FLAXLK3%2BL6pGV3yF2TDox%2BgSEoEvc0rMYKkjFIKM8ilUJFaQnquUWLiubOabNO%2FeDrhYWK8qFdlAG6w4H6tX6BSvz8cEWng7YQ%2FFoAXpkTUaqYt%2FGlbaRT9b2jWwBMU%2B1qIiCRZzMt2vJoQb6l%2BVbGSce7N5wxD--Qjxh6wf62i66sTJ3--0roPNFxbbmSV5WiC%2FqeV9w%3D%3D"

headers_webpage = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
           "Accept-Encoding": "gzip, deflate, br, zstd",
           "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
           "Cache-Control": "no-cache",
           "Cookie":f"{cookie}",
           "Pragma":"no-cache",
           "Priority":"u=0, i",
           "Sec-Ch-Ua":"\"Microsoft Edge\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
           "Sec-Ch-Ua-Mobile": "?0",
           "Sec-Ch-Ua-Platform":"\"Windows\"",
           "Sec-Fetch-Dest":"document",
           "Sec-Fetch-Mode": "navigate",
           "Sec-Fetch-Site": "same-origin",
           "Sec-Fetch-User": "?1",
           "Upgrade-Insecure-Requests":"1",
           "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"}