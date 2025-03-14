import utils
import config
from bs4 import BeautifulSoup
import requests
import json
import datetime
import re
import base64

fake_dict = dict()

class Conversation:
    def __init__(self, prompt, answer):
        self.Prompt = prompt
        self.Answer = answer
        self.ListOfCode = list()
        self.code_replace()

    # extract codes from given prompt and answer
    def code_replace(self):
        replace_count = 0

        prompt_codes = utils.code_pattern.findall(self.Prompt)
        for prompt_code in prompt_codes:
            replace_string = config.code_replace_template.format(str(replace_count))
            self.Prompt.replace(prompt_code, replace_string)
            tmp = dict()
            tmp["ReplaceString"] = replace_string
            tmp["Type"], tmp["Content"] = utils.extract_code_type_and_content(prompt_code)
            self.ListOfCode.append(tmp)
            replace_count += 1

        answer_codes = utils.code_pattern.findall(self.Answer)
        for answer_code in answer_codes:
            replace_string = config.code_replace_template.format(str(replace_count))
            self.Answer.replace(answer_code, replace_string)
            tmp = dict()
            tmp["ReplaceString"] = replace_string
            tmp["Type"], tmp["Content"] = utils.extract_code_type_and_content(answer_code)
            self.ListOfCode.append(tmp)
            replace_count += 1



class ChatgptSharing:

    def __init__(self, url, mention):
        self.URL = url
        self.Mention = mention
        self.Status = 0
        self.DateOfConversation = ""
        self.DateOfAccess = ""
        self.Title = ""
        self.NumberOfPrompts = 0
        self.TokensOfPrompts = 0
        self.TokensOfAnswers = 0
        self.Model = ""
        self.Conversations = None # list of conversations
        self.HTMLContent = ""
        self.extract_share()

    # fufill self.Conversations and some other attributes
    def extract_share(self):
        openai_resp = requests.get(self.URL)
        self.Status = openai_resp.status_code
        self.DateOfAccess = str(datetime.datetime.now())
        if openai_resp.status_code != 200:
            return
        self.HTMLContent = openai_resp.text
        soup = BeautifulSoup(self.HTMLContent, 'lxml')
        try:    # try to get the linear conversations
            o = soup.find(id="__NEXT_DATA__")
            j = json.loads(o.text)
            props = j["props"]
            page_props = props["pageProps"]
            server_response = page_props["serverResponse"]
            dataload = server_response["data"]

            self.Title = dataload["title"]
            self.Model = dataload.get("model", fake_dict).get("slug")
            linear_conversation = dataload["linear_conversation"]
            self.DateOfConversation = str(datetime.datetime.fromtimestamp(linear_conversation[-1]["message"]["create_time"]))    # The timestamp of the creation of the last message.
            self.Conversations = utils.extract_conversations(linear_conversation)
        except Exception as e: # if any of the keys does not exist, let the error throws, and proceed as the share_link don't have a valid conversation record
            print(e)
            return
        
        self.NumberOfPrompts = len(self.Conversations)
        # calculate the tokens
        self.TokensOfPrompts = sum([utils.token_cal(self.Model, conversation.Prompt) for conversation in self.Conversations])
        self.TokensOfAnswers = sum([utils.token_cal(self.Model, conversation.Answer) for conversation in self.Conversations])
        # A value less than 0 indicates that the model is temporarily unable to calculate using tiktoken; set it to 0.
        if self.TokensOfPrompts < 0:
            self.TokensOfPrompts = 0
        if self.TokensOfAnswers < 0:
           self.TokensOfAnswers = 0   
        
        

        

class githubCode:
    error_record = {"Code" : []}
    def __init__(self):
        self.Type = "code"
        self.URL = None
        self.ObjectSha = None
        self.FileName = None
        self.FilePath = None
        self.Author = None
        self.Content = None
        self.RepoName = None
        self.RepoLanguage = None
        self.CommitSha = None
        self.CommitMessage = None
        self.AuthorAt = None
        self.CommitAt = None
        self.ChatgptSharing = None


    def handle(self, search_result):
        try:
            self.URL = search_result["html_url"]
            self.ObjectSha = search_result["sha"]
            self.FileName = search_result["name"]
            self.FilePath = search_result["path"]
            self.RepoName = search_result["repository"]["full_name"]
            url = search_result["url"]
            url_resp = requests.get(url, headers=config.headers_rest_api)
            if url_resp.status_code != 200:
                print(f"fetch {url} error!")
                return
            file = json.loads(url_resp.text)
            content_base64 = file["content"]
            self.Content = base64.b64decode(content_base64).decode()
            share_links = utils.get_matches(config.target_regex, self.Content)

            splited_url = self.URL.split("/")
            repo_owner = splited_url[3]
            repo_name = splited_url[4]
            self.RepoName = f"{repo_owner}/{repo_name}"
            self.RepoLanguage = utils.get_repo_languages(self.RepoName)

            mention = {"MentionedURL": self.URL,"MentionedProperty": "code file",
                        "MentionedAuthor": self.Author,"MentionedText": self.Content}
            self.ChatgptSharing = utils.get_ChatgptSharings(share_links, mention)
        except Exception as e:
            githubCode.error_record["Code"].append({"Source_url":self.URL, "latent_error_urls":share_links, "error_discribe":str(e)})
            print(e)
            return

class githubCommit:
    error_record = {"Commit":[]}
    def __init__(self):
        self.Type = "commit"
        self.URL = None
        self.Author = None
        self.RepoName = None
        self.RepoLanguage = None
        self.Sha = None
        self.Message = None
        self.AuthorAt = None
        self.CommitAt = None
        self.ChatgptSharing = None

    def handle(self, result):
        try:
            self.URL = result.get("html_url")
            author = result.get("author", fake_dict)
            if author is not None:
                self.Author = author.get("login")
            self.RepoName = result.get("repository", fake_dict).get("name")
            if self.RepoName is not None:
                repo_owner = result.get("repository", fake_dict).get("owner",fake_dict).get("login")
                if repo_owner is not None:
                    self.RepoName = f"{repo_owner}/{self.RepoName}"
                    self.RepoLanguage = utils.get_repo_languages(self.RepoName)
            self.Sha = result.get("sha")
            self.Message = result.get("commit", fake_dict).get("message")
            self.AuthorAt = result.get("commit", fake_dict).get("author",fake_dict).get("date")
            self.CommitAt = result.get("commit", fake_dict).get("committer",fake_dict).get("date")

            # Links have two sources: messages and comments. 
            # In theory, messages should not be left empty, whereas comments are usually empty in most cases.
            self.ChatgptSharing = list()
            share_links = list()
            if self.Message is not None:
                links = utils.get_matches(config.target_regex, self.Message)
                share_links += links
                mention = {
                            "MentionedURL": self.URL,
                            "MentionedProperty": "message",
                            "MentionedAuthor": self.Author,
                            "MentionedText": self.Message
                        }

                self.ChatgptSharing += utils.get_ChatgptSharings(links, mention)


            if result.get("commit", fake_dict).get("comment_count", 0) !=0:
                comments_url = result.get("comments_url")
                comments_resp = requests.get(comments_url, config.headers_rest_api)
                if comments_resp.status_code == 200:
                    comments = json.loads(comments_resp.text)
                else:
                    comments = []
                for comment in comments:
                    comment_content = comment.get("body")
                    links = utils.get_matches(config.target_regex, comment_content)
                    share_links += links
                    mention = {
                            "MentionedURL": self.URL,
                            "MentionedProperty": "comments.body",
                            "MentionedAuthor": comment.get("user", fake_dict).get("login"),
                            "MentionedText": comment_content
                        }
                    self.ChatgptSharing += utils.get_ChatgptSharings(links, mention)
        except Exception as e:
            githubCommit.error_record["Commit"].append({"Source_url":self.URL, "latent_error_urls":share_links, "error_discribe":str(e)})
            return



class githubIssue:
    error_record = {"Issue":[]}
    def __init__(self):
        self.Type = "issue"
        self.URL = None
        self.Author = None
        self.RepoName = None
        self.RepoLanguage = None
        self.Number = None
        self.Title = None
        self.Body = None
        self.AuthorAt = None
        self.ClosedAt = None
        self.UpdateAt = None
        self.State = None
        self.ChatgptSharing = None

    def handle(self, search_result):
        try:
            self.URL = search_result.get("html_url")
            self.Author = search_result.get("user",fake_dict).get("login")

            url_splited = self.URL.split("/")   #like: ['https:', '', 'github.com', 'FlorianREGAZ', 'Python-Tls-Client', 'issues', '79']
            self.RepoName = url_splited[-3]
            repo_owner = url_splited[-4]
            self.RepoName = f"{repo_owner}/{self.RepoName}"
            self.RepoLanguage = utils.get_repo_languages(self.RepoName)

            self.Number = search_result.get("number")
            self.Title = search_result.get("title")
            self.Body = search_result.get("body")

            rest_url = search_result.get("url")
            rest_resp = requests.get(rest_url, headers=config.headers_rest_api)
            if rest_resp.status_code != 200:
                print(f"url: {self.URL} fetch error!")
                return
            issues_content = json.loads(rest_resp.text)
            self.AuthorAt = issues_content.get("created_at")
            self.ClosedAt = issues_content.get("closed_at")
            self.UpdateAt = issues_content.get("updated_at")
            self.State = issues_content.get("state")
    
            # Links have two sources: body and comments, and the body may be empty.
            self.ChatgptSharing = list()
            share_links = list()

            if self.Body is not None:
                links = utils.get_matches(config.target_regex, self.Body)
                share_links += links
                mention = {
                            "MentionedURL": self.URL,
                            "MentionedProperty": "body",
                            "MentionedAuthor": self.Author,
                            "MentionedText": self.Body
                        }

                self.ChatgptSharing += utils.get_ChatgptSharings(links, mention)


            if issues_content.get("comments", 0) !=0:
                comments_url = issues_content.get("comments_url")
                comments_resp = requests.get(comments_url, config.headers_rest_api)
                if comments_resp.status_code == 200:
                    comments = json.loads(comments_resp.text)
                else:
                    comments = []
                for comment in comments:
                    comment_content = comment.get("body")
                    links = utils.get_matches(config.target_regex, comment_content)
                    share_links += links
                    mention = {
                            "MentionedURL": self.URL,
                            "MentionedProperty": "comments.body",
                            "MentionedAuthor": comment.get("user", fake_dict).get("login"),
                            "MentionedText": comment_content
                        }
                    self.ChatgptSharing += utils.get_ChatgptSharings(links, mention)
        except Exception as e:
            githubIssue.error_record["Issue"].append({"Source_url":self.URL, "latent_error_urls":share_links, "error_discribe":str(e)})
            return 

class githubPR:
    error_record = {"PR":[]}
    def __init__(self):
        self.Type = "pull request"
        self.URL = None
        self.Author = None
        self.RepoName = None
        self.RepoLanguage = None
        self.Number = None
        self.Title = None
        self.Body = None
        self.CreatedAt = None
        self.ClosedAt = None
        self.MergedAt = None
        self.UpdatedAt = None
        self.State = None
        self.Additions = None
        self.Deletions = None
        self.ChangedFiles = None
        self.CommitsTotalCount = None
        self.CommitSha = None
        self.ChatgptSharing = None

    def handle(self, result):
        pr_number = result["number"]
        repo_owner = result["repo"]["repository"]["owner_login"]
        repo_name = result["repo"]["repository"]["name"]

        pr_url_restapi = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
        self.URL = f"https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}"
        resp = requests.get(pr_url_restapi, headers=config.headers_rest_api)
        if resp.status_code != 200:
            print(f"url:{self.URL} fetch error")
            return
        else:
            dataload = json.loads(resp.text)
        try:
            self.Author = dataload.get("user", fake_dict).get("login")
            self.RepoName = f"{repo_owner}/{repo_name}"
            self.RepoLanguage = utils.get_repo_languages(self.RepoName)
            self.Number = dataload.get("number")
            self.Title = dataload.get("title")
            self.Body = dataload.get("body")
            self.CreatedAt = dataload.get("created_at")
            self.ClosedAt = dataload.get("closed_at")
            self.MergedAt = dataload.get("merged_at")
            self.UpdatedAt = dataload.get("updated_at")
            self.State = dataload.get("state")
            self.Additions = dataload.get("additions")
            self.Deletions = dataload.get("deletions")
            self.ChangedFiles = dataload.get("changed_files")
            self.CommitsTotalCount = dataload.get("commits")
            # In theory, each should have a commits SHA field, as at least one commit is required to send a PR. 
            # However, in "20230727_195927_pr_sharings.json," the first entry, which has only one commit, lacks the commits SHA field.
            commits_rest_url = dataload.get("commits_url")
            commits_resp = requests.get(commits_rest_url, headers=config.headers_rest_api)
            if commits_resp.status_code == 200:
                self.CommitSha = list()
                commits = json.loads(commits_resp.text)
                for commit in commits:
                    self.CommitSha.append(commit["sha"])
            else:
                self.CommitSha = None
            
            # Links have two sources: the body and comments, and the body may be empty.
            self.ChatgptSharing = list()
            share_links = list()

            if self.Body is not None:
                links = utils.get_matches(config.target_regex, self.Body)
                share_links += links
                mention = {
                            "MentionedURL": self.URL,
                            "MentionedProperty": "body",
                            "MentionedAuthor": self.Author,
                            "MentionedText": self.Body
                        }

                self.ChatgptSharing += utils.get_ChatgptSharings(links, mention)


            if dataload.get("comments", 0) !=0:
                comments_url = dataload.get("comments_url")
                comments_resp = requests.get(comments_url, config.headers_rest_api)
                if comments_resp.status_code == 200:
                    comments = json.loads(comments_resp.text)
                else:
                    comments = []
                for comment in comments:
                    comment_content = comment.get("body")
                    links = utils.get_matches(config.target_regex, comment_content)
                    share_links += links
                    mention = {
                            "MentionedURL": self.URL,
                            "MentionedProperty": "comments.body",
                            "MentionedAuthor": comment.get("user", fake_dict).get("login"),
                            "MentionedText": comment_content
                        }
                    self.ChatgptSharing += utils.get_ChatgptSharings(links, mention)

        except Exception as e:
            githubPR.error_record["PR"].append({"Source_url":self.URL, "latent_error_urls":share_links, "error_discribe":str(e)})
            return



class githubDiscussion:
    error_record = {"Discussion":[]}
    def __init__(self, discussion_url):
        self.Type = "discussion"
        self.URL = discussion_url
        self.Author = None
        self.RepoName = None
        self.RepoLanguage = None
        self.Number = None
        self.Title = None
        self.Body = None
        self.AuthorAt = None
        self.ClosedAt = None
        self.UpdatedAt = None
        self.Closed = None
        self.UpvoteCount = None
        self.ChatgptSharing = None

    def handle(self, search_result):
        discussion_webage_content = utils.get_page_content(self.URL, config.headers_webpage)
        self.Author = search_result.get("user_login", "")
        self.RepoName = search_result.get("repo", fake_dict).get("repository", fake_dict).get("name", "")
        self.Number = search_result.get("number", 0)
        self.Title = search_result.get("title", "")
        self.Body = search_result.get("body", "")
        self.AuthorAt = search_result.get("created", "")
        self.UpdatedAt = search_result.get("updated", "")

 
        find_closed = discussion_webage_content.find("Status: Closed as outdated")  # if closed, the return value is a positive number
        self.Closed = (find_closed != -1)  
        if self.Closed:
            regex_pattern = """<span class=\"color-fg-muted\"><relative-time tense=\"past\" format=\"micro\" datetime=\"(.+)\" data-view-component=\"true\">"""   #closedAt 就是datatime里面的内容
            matched = re.findall(regex_pattern, discussion_webage_content)
            if len(matched) == 1:
                self.ClosedAt = matched[0]   
        else:    
            self.ClosedAt = None
        

        # Analyze the discussion post, dividing it into the main post and the comments section.
        bs = BeautifulSoup(discussion_webage_content, 'lxml')
        main_div = bs.find(class_="TimelineItem pt-0 js-comment-container discussion-timeline-item ml-0")
        comment_divs = bs.find_all(class_="js-timeline-item js-timeline-progressive-focus-container js-quote-selection-container")
        
        # main post
        main_inner = main_div.find(class_="d-block color-fg-default comment-body markdown-body js-comment-body")
        if main_inner is not None:
            main_text = main_inner.text
        else:
            main_text = ""
        main_links = utils.get_matches(config.target_regex, main_text)
        # main post upvotes
        self.UpvoteCount = None
        self.ChatgptSharing = list()
        for link in main_links:
            try:
                self.ChatgptSharing.append(ChatgptSharing(link, mention={"MentionedURL": self.URL,"MentionedProperty": "discussion",
                        "MentionedAuthor": self.Author,"MentionedText": main_text, "MentionedUpvoteCount": self.UpvoteCount}))
            except Exception as e:
                githubDiscussion.error_record["Discussion"].append({"Source_url":self.URL, "error_url":link, "error_discribe":str(e)})


        # comments
        for comment_div in comment_divs:
            comment_inner = comment_div.find(class_="d-block color-fg-default comment-body markdown-body js-comment-body")
            if comment_inner is not None:
                comment_text = comment_inner.text
            else:
                comment_text = ""
            links = utils.get_matches(config.target_regex, comment_text)
            share_links += links
            comment_author = comment_div.find(class_="Truncate-text text-bold")
            if comment_author is not None:
                comment_author = comment_author.text
        
            # comments' upvotes
            mentioned_upvote_count = None
            try: 
                comment_data_url = comment_div.find(class_="discussions-timeline-scroll-target js-targetable-element").get("data-url", None)
                comment_id = comment_data_url.split('/')[-1]
                upvote_post_body = {"items[items-0][comment_id]":comment_id, "_method":"GET"}
            except:
                mentioned_upvote_count = None

            comment_mention = {"MentionedURL": self.URL,"MentionedProperty": "discussion",
                    "MentionedAuthor": comment_author,"MentionedText": comment_text, 
                    "MentionedUpvoteCount": mentioned_upvote_count}
            if True is False:#is marked as answer
                comment_mention["MentionedIsAnswer"] = True
            else:
                comment_mention["MentionedIsAnswer"] = False
            for link in links:
                try:
                    self.ChatgptSharing.append(ChatgptSharing(link, mention=comment_mention))
                except Exception as e:
                    githubDiscussion.error_record["Discussion"].append({"Source_url":self.URL, "error_url":link, "error_discribe":str(e)})

