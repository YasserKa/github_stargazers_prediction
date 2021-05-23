[Dask](https://docs.dask.org/en/latest/) is used to ensure parallelization
during training the ML models.

## Hosting the application in OpenStack
```
    "identifier": "my_instances",
    "flavor": "medium",
    "private_net": "Network",
    "image_id": "123-123-123",
    "key_name": "key-pair",
    "number_of_dask_workers": 3
```

#### Tasks

- Make sure to update cloud-cfg.txt by inserting your public key
- Make sure to have OpenStack packages installed, check the instructions for Ubuntu [here](https://docs.openstack.org/install-guide/environment-packages-ubuntu.html).
- You need to source  your **v3** Runtime Configuration (RC) file, before running
`start_instances.py`. You can get it from the SSC site (Top left frame Project
-> API Access -> Download OpenStack RC File).
- If you haven't set a password for your API, you can set it
[here](https:///cloud.snic.se/), Left frame, under Services "Set your API
password".
- Now you can create the instances by
```
python3 start_instances 
```


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
"alexZajac/react-native-skeleton-content-nonexpo": {
      "owner": "alexZajac",
      "name": "react-native-skeleton-content-nonexpo",
      "id": "id_200399711",
      "full_name": "alexZajac/react-native-skeleton-content-nonexpo",
      "contributors_count": 8,
      "watchers": 2,
      "fork_count": 31,
      "amount_repos_owner_have": 53,
      "is_verified_organization": 0,
      "memebers_with_roles_in_organization": 0,
      "commits_comments_for_user": 0,
      "follower_for_user": 46,
      "main_language": "JavaScript",
      "created_at": "2019-08-03T16:54:24Z",
      "last_commit": "2021-05-22T07:54:33Z",
      "assigned_to_issues": 1,
      "stargazer_count": 113,
      "closed_pull_requests_count": 3,
      "merged_pull_requests_count": 17,
      "open_pull_requests_count": 1,
      "branches": 1,
      "tags": 11,
      "labels": 10,
      "open_issues_count": 4,
      "closed_issues_count": 12,
      "commits_since_one_year": 57,
      "mentionableUsers": 5,
      "disk_usage_in_kbs": 1087,
      "total_commits": 106,
      "readme_size": 8050
},
```
