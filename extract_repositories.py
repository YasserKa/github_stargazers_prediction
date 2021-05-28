#!/bin/python
import requests
from datetime import datetime, timedelta
from github import Github
from github.GithubException import GithubException
import os
import sys
import json


REPO_PER_PAGE = 100

config = {}
headers = {}


def load_config():
    global config, headers

    if not os.path.isfile('.config.json'):
        print(
            ".config.json is needed at the root of the project, check .config.json.template")
        exit()

    with open('.config.json') as json_file:
        config = json.load(json_file)['git_extraction_script']
    headers["Authorization"] = f"token {config['git_token']}"


# fetche repo full_name and contributors_count
def get_repos():
    g = Github(config['git_token'])
    g.per_page = REPO_PER_PAGE

    repos_json = {}
    repo_index = 0
    page_num = 0
    last_repos_page = None

    query = f"stars:>={config['least_stargazers']}"

    while True:
        print(f"Fetching page {page_num}")
        try:
            # sort updated () is used to have a pseudo-random sample of the repos
            # instead of the repos that have most stargazers
            repos_page = g.search_repositories(
                query=query, sort="updated").get_page(page_num)
        except GithubException:
            if sys.exc_info()[1].status == 422:
                page_num = 0
                date = last_repos_page[-1].pushed_at.isoformat()
                query = f"stars:>={config['least_stargazers']} pushed:<{date}"
                continue
            else:
                print("API rate exceeded")
                return repos_json

        for repo in repos_page:
            if repo_index >= config['number_of_repos_to_extract']:
                return repos_json

            # skip if the repo already exists
            if repo.full_name in repos_json:
                continue

            print(f"Fetching repo {repo_index}")

            repos_json[repo.full_name] = {
                'owner': repo.owner.login,
                'name': repo.name,
                'id': "id_" + str(repo.id),
                'full_name': repo.full_name,
            }

            # they take a request each
            if config['fetch_contributors']:
                try:
                    contributors_count = repo.get_contributors(
                        anon='true').totalCount
                except GithubException:
                    #  if the contributor list is too large, the API won't fetch
                    #  the list
                    contributors_count = 5000
                repos_json[repo.full_name]['contributors_count'] = contributors_count

            repo_index += 1
        page_num += 1
        last_repos_page = repos_page


def add_repos_details_using_graphql(repos_json):
    url = "https://api.github.com/graphql"

    count_repos = 0
    # It might timeout more often if you request for more
    repos_per_request = 20
    while True:
        query_string = "{"
        end_index = count_repos + repos_per_request
        # end_index = count_repos + 10
        if end_index >= len(repos_json):
            targeted_repos = list(repos_json.values())[count_repos:]
        else:
            targeted_repos = list(repos_json.values())[count_repos:end_index]

        print(f"Fetching page from graphql from index {count_repos} till "
              f"{end_index-1}")
        for repo in targeted_repos:
            name = repo['name']
            owner = repo['owner']
            repo_id = repo['id']
            query_string += get_repo_graphql_query(repo_id, owner, name)

        query_string += "}"

        data = {"query": query_string}
        r = requests.post(url, headers=headers, json=data)
        try:
            for repo_json in r.json()['data'].values():
                full_name = f"{repo_json['owner']['login']}/{repo_json['name']}"
                filter_graphql_json(repo_json)
                repos_json[full_name].update(repo_json)
        except Exception:
            print("request timeout, redoing")
            continue

        # we finished with all repos
        if end_index >= len(repos_json):
            break

        count_repos += repos_per_request


# move values to top level keys
def filter_graphql_json(repo_json):
    for key, value in repo_json.items():
        while True:
            value_type = type(value)
            if value_type == dict:
                if value:
                    value = list(value.values())[0]
                else:
                    value = 0
            elif value_type == list:
                if len(value) == 0:
                    value = 0
                else:
                    value = value[0]
            else:
                repo_json[key] = value
                break


def get_repo_graphql_query(repo_id, owner, name):
    query_string = f"""{repo_id}: repository(owner: "{owner}", name:
        "{name}")""" \
    """{
    name
    watchers {
        totalCount
    }
    fork_count: forkCount
    amount_repos_owner_have: owner {
    repositories {
      totalCount
    }
  }
    readme_content_master: object(expression: "master:README.md") {
      ... on Blob {
        text
      }
    }
    readme_content_main: object(expression: "main:README.md") {
      ... on Blob {
        text
      }
    }
   is_verified_organization: owner {
    ... on Organization {
     isVerified

    }
  }
  memebers_with_roles_in_organization: owner {
    ... on Organization {
      membersWithRole {
        totalCount
      }
    }
  }
    commits_comments_for_user: owner {
      ... on User {
     commitComments {
      totalCount
    }

    }

  }
      follower_for_user: owner {
      ... on User {
     followers {
      totalCount
    }

    }
  }
    main_language: languages(first:1) {
      edges {
        node {
          name
        }
      }
    }
    owner {
    login
    }
    created_at: createdAt
    last_commit: defaultBranchRef {
      target {
        ... on Commit {
        history(first:1) {
        nodes{
        pushedDate
        }
        }
        }
      }
      }
    assigned_to_issues: assignableUsers {
    totalCount
    }
    stargazer_count: stargazerCount
    closed_pull_requests_count: pullRequests(states:[CLOSED]) {
    totalCount
    }
    merged_pull_requests_count: pullRequests(states:[MERGED]) {
    totalCount
    }
    open_pull_requests_count: pullRequests(states:[OPEN]) {
    totalCount
    }
    branches: refs(refPrefix:"refs/heads/") {
    totalCount
    }
    tags: refs(refPrefix:"refs/tags/") {
    totalCount
    }
    labels {
    totalCount
    }
    open_issues_count:
        issues(filterBy: { states:[OPEN] }) {
            totalCount
    }
    closed_issues_count:
        issues(filterBy: { states:[CLOSED] }) {
            totalCount
    }
    commits_since_one_year: defaultBranchRef {
      target {
        ... on Commit {
        """
    since_date = (datetime.now() - timedelta(days=365)).isoformat()
    query_string += f"""history(since:"{since_date}")"""
    query_string += """{
        totalCount
        }
        }
      }
    }
    mentionableUsers {
    totalCount
    }
    disk_usage_in_kbs: diskUsage
    total_commits: defaultBranchRef {
      target {
        ... on Commit {
        history {
        totalCount
        }
        }
      }
    }
  }
"""

    return query_string


def update_repos_content(repos):
    for repo_name in repos:
        size = 0

        if repos[repo_name]['readme_content_main'] is not None:
            size = len(repos[repo_name]['readme_content_main'])

        if repos[repo_name]['readme_content_master'] is not None:
            size = len(repos[repo_name]['readme_content_master'])

        repos[repo_name]['readme_size'] = size

        del repos[repo_name]['readme_content_master']
        del repos[repo_name]['readme_content_main']


def main():
    repos = get_repos()

    add_repos_details_using_graphql(repos)
    update_repos_content(repos)

    with open('repos.json', mode='w') as _file:
        json.dump(repos, _file, indent=6)


if __name__ == '__main__':
    load_config()
    main()
