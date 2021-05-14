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
      "googleapis/google-api-java-client-services": {
            "owner": "googleapis",
            "name": "google-api-java-client-services",
            "id": "id_147399159",
            "full_name": "googleapis/google-api-java-client-services",
            "contributors_count": 15,
            "graph_ql": {
                  "name": "google-api-java-client-services",
                  "watchers": {
                        "totalCount": 43
                  },
                  "fork_count": 217,
                  "owner": {
                        "login": "googleapis"
                  },
                  "created_at": "2018-09-04T19:11:33Z",
                  "last_commit": {
                        "target": {
                              "history": {
                                    "nodes": [
                                          {
                                                "pushedDate": "2021-05-14T11:14:16Z"
                                          }
                                    ]
                              }
                        }
                  },
                  "assigned_to_issues": {
                        "totalCount": 121
                  },
                  "stargazer_count": 246,
                  "closed_pull_requests_count": {
                        "totalCount": 1229
                  },
                  "merged_pull_requests_count": {
                        "totalCount": 6128
                  },
                  "open_pull_requests_count": {
                        "totalCount": 61
                  },
                  "branches": {
                        "totalCount": 82
                  },
                  "tags": {
                        "totalCount": 0
                  },
                  "labels": {
                        "totalCount": 212
                  },
                  "open_issues_count": {
                        "totalCount": 46
                  },
                  "closed_issues_count": {
                        "totalCount": 695
                  },
                  "commits_since_one_year": {
                        "target": {
                              "history": {
                                    "totalCount": 3143
                              }
                        }
                  },
                  "mentionableUsers": {
                        "totalCount": 130
                  },
                  "disk_usage_in_kbs": 96017,
                  "total_commits": {
                        "target": {
                              "history": {
                                    "totalCount": 6162
                              }
                        }
                  }
            }
      },

```
