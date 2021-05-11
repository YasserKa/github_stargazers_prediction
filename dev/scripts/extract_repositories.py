#!/bin/python
import requests
from github import Github
from github.GithubException import GithubException
import os
import json

NUMBER_REPOS = 1000
REPO_PER_PAGE = 100

if not os.path.isfile('.config.json'):
    print(".config.json is needed, put an empty token, if you don't want to take"
          "advantage of the authorized")
    exit()

with open('.config.json') as json_file:
    CONFIG = json.load(json_file)


def get_repos():
    pages = max(1, int(NUMBER_REPOS / REPO_PER_PAGE))
    g = Github(CONFIG['git_token'])

    repos = {}
    repo_index = 0
    headers = {
        "Authorization": f"token {CONFIG['git_token']}"
    }

    for page in range(0, pages):
        try:
            repos_page = g.search_repositories(
                query="stars:>=50").get_page(page)
        except GithubException:
            print("API rate exceeded")
            exit()

        for repo in repos_page:
            if repo_index >= NUMBER_REPOS:
                break
            url = f"https://api.github.com/repos/{repo.full_name}"
            r = requests.get(url, headers=headers)
            repos[repo.full_name] = r.json()
            repo_index += 1

    with open('repos.json', mode='w') as _file:
        json.dump(repos, _file, indent=6)


def main():
    get_repos()


if __name__ == '__main__':
    main()
