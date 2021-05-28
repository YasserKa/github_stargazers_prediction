A containerized approach to setup production and developer servers while using [Dask](https://docs.dask.org/en/latest/) to ensure parallelization during training the ML models. 

The application focuses on training a model that predicts the number of stars
for a repository while extracting the information about the repositories using
Github's GraphQL.


# Setup

Copy the configuration template file:

```
cp .config.json.template .config.json
```

## Hosting the application in OpenStack

Update relevant information in `config.json`

```
    "identifier": "my_instances",
    "flavor": "medium",
    "private_net": "Network",
    "image_id": "123-123-123",
    "key_name": "key-pair",
    "number_of_workers": 3
```



#### Creating instances

- To enable the client to communicate with other hosts, an ssh key pair is
    created.
```
mkdir -p ~/.ssh/cluster-keys
ssh-keygen -t rsa -f ~/.ssh/cluster-keys/cluster_rsa
```
- Update `openstack-client/cloud-cfg.txt` by inserting the cluster's public key
- Install OpenStack packages. Check the instructions for Ubuntu [here](https://docs.openstack.org/install-guide/environment-packages-ubuntu.html).
- Source  your **v3** Runtime Configuration (RC) file, before running
`start_instances.py`. You can get it from the SSC site (Top left frame Project
-> API Access -> Download OpenStack RC File).
- If you haven't set a password for your API, you can set it
[here](https:///cloud.snic.se/), Left frame, under Services "Set your API
password".
- Create the instances by
```
python3 start_instances 
```

### Setting up Ansible

- install ansible using pip 
```
pip3 install ansible
```
Note that `start_instances.py` generates an `inventory.ini` that contains the
host files for the ansible playbook.
- run playbook in `openstack-client` directory
```
ansible-playbook -i inventory.ini deploy_swarm.yml \
       --private-key=/home/ubuntu/.ssh/cluster-keys/id_rsa
```

You can access the dask dashboard via http://devserver:8787/status
and the application http://pubserver:5100

Also, you can access jupyter notebook that uses the dask cluster http://devserver:8888/status . To get the token, you need to login to the notebook container in the swarm and type:
```
jupyter server list
```


## Getting repositories
- Login to the dev server and update the configuration file for repository extraction.
```
{
    "git_token": "my_token",
    "least_stargazers": 50,
    "number_of_repos_to_extract": 1000
    "fetch_contributors": true
}
```

Run `extract_repositories.py` to fetch the repositories data.

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

Executing `train_model.py` will use the dask cluster to train a model generating
a pickled model. Put the pickled model in `~/my_project` and push it to
production `git push production master`, a git-hook will replace the old model
by the new one.

# TODO

- [ ] automate the tasks for setting up the client instance
- [ ] Make the fronted scalable  by introducing it to the swarm
- [ ] Include a cron job that trains and pushes the model to production server
- [ ] Add repositories instead of replacing them (Use a DB)
