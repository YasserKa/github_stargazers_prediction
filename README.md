## Getting repositories
```
{
    "git_token": "my_token",
    "least_stargazers": 50,
    "number_of_repos_to_extract": 1000
    "fetch_contributors": true
}
```
Using a [token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token) will allow you to do more requests to gitHub's REST API.

[Github GraphQL API](https://docs.github.com/en/graphql) is used to fetch most
of the information about the repositories to reduce the amount of requests
needed.

Since the [contributors count can't be extracted from graphql](https://github.community/t/graphql-get-repository-contributors/14422), it will require a single API request for each repo to get this detail. Setting `fetch_contributors` to false, will skip this variable.

If the contributors list is too big, th API will not return the list; in this
case, 5000 will be used.

An example of what you might get for each repository:

```
      "flight-recorder/health-report": {
            "owner": "flight-recorder",
            "name": "health-report",
            "id": "id_255951864",
            "full_name": "flight-recorder/health-report",
            "contributors_count": 1,
            "watchers": 7,
            "fork_count": 10,
            "created_at": "2020-04-15T15:02:17Z",
            "last_commit": "2021-05-15T09:56:45Z",
            "assigned_to_issues": 2,
            "stargazer_count": 60,
            "closed_pull_requests_count": 0,
            "merged_pull_requests_count": 0,
            "open_pull_requests_count": 1,
            "branches": 1,
            "tags": 0,
            "labels": 9,
            "open_issues_count": 0,
            "closed_issues_count": 0,
            "commits_since_one_year": 10,
            "mentionableUsers": 1,
            "disk_usage_in_kbs": 43,
            "total_commits": 20
      },
```
