# -*- coding: utf-8 -*-

# @Version : 1.0
# @Time    : 2019/09/16 18:12
# @Author  : lework
# @File    : check.py
# @Desc    : 用于检查指定开源软件的最新版本

import os
import sys
import json
import time
import requests
import threading
from datetime import datetime

source_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source.json')
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../static/data/data.json')
docs_data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../docs/static/data/data.json')

token = os.environ.get('GITHUB_TOKEN', '')
if token == '':
    print('[Error] not found token.')
    sys.exit(1)

headers = {"Content-Type": 'application/json; charset=utf-8', "Authorization": "token %s" % token}

result = {
    "updated_at": "",
    "total": 0,
    "data": []
}


def sort_time(stime):
    data = None
    try:
        data = datetime.strptime(stime, "%Y-%m-%dT%H:%M:%S%z")
    except Exception as e:
        print(stime, e)
        data = datetime.strptime("1970-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    return data


def get_github_latest_release(pro):
    data = {}
    resp = {}
    tag = False
    latest_url = "https://api.github.com/repos/%s/releases/latest" % pro['repo']

    if "version" in pro and pro['version'] == 'tag':
        tag = True
    else:
        resp = requests.get(latest_url, headers=headers)
        if resp.status_code == 404:
            tag = True

    if tag:
        graphql_url = "https://api.github.com/graphql"
        post_data = {
            "query": """
{
  repository(owner: "%s", name: "%s") {
    refs(refPrefix: "refs/tags/", first: 3, orderBy: {field: TAG_COMMIT_DATE, direction: DESC}) {
      edges {
        node {
          name
          target {
            commitUrl
            ... on Tag {
              message
              commitUrl
              tagger {
                date
              }
              target {
                ... on Commit {
                  message
                  commitUrl
                  committedDate
                }
              }
            }
          }
        }
      }
    }
  }
}""" % (pro['repo'].split('/')[0], pro['repo'].split('/')[1])}
        resp = requests.post(graphql_url, headers=headers, data=json.dumps(post_data))
        try:
            last_data = resp.json()['data']['repository']['refs']['edges'][0]['node']
            data['tag_name'] = last_data['name']
            if 'target' in last_data['target'] and last_data['target']['target']:
                commit_url = last_data['target']['target']['commitUrl'].replace('/github.com/','/api.github.com/repos/').replace('/commit/', '/commits/')
                data['created_at'] = last_data['target']['target']['committedDate']
                data['body'] = last_data['target']['target']['message']
                data['html_url'] = commit_url
            else:
                commit_url = last_data['target']['commitUrl'].replace('/github.com/', '/api.github.com/repos/').replace('/commit/', '/commits/')
                commit = requests.get(commit_url, headers=headers)
                commit_data = commit.json()

                if 'commit' in commit_data and commit.status_code == 200:
                    data['created_at'] = commit_data['commit']['committer']['date']
                    data['body'] = commit_data['commit']['message']
                    data['html_url'] = commit_data['html_url']
                else:
                    data['created_at'] = last_data['target']['tagger']['date']
                    data['body'] = last_data['target']['message']
                    data['html_url'] = commit_url
        except Exception as e:
            print(pro['repo'], e)
            print(json.dumps(resp.headers))
            print(json.dumps(resp.json()))
    else:
        data = resp.json()
    data['repo_url'] = "https://github.com/%s" % pro['repo']

    if 'message' in data:
        print(data)
        return None
    return data


def get_latest_release(pro):
    latest_data = {}
    print("[Repo] %s" % pro['project'])
    if pro['hosting'] == 'github':
        latest_data = get_github_latest_release(pro)

    if latest_data:
        data = {
            "name": latest_data.get('name', ''),
            "tag_name": latest_data.get('tag_name', ''),
            "html_url": latest_data.get('html_url', ''),
            "repo_url": latest_data.get('repo_url', ''),
            "body": latest_data.get('body', ''),
            "created_at": latest_data.get('created_at', '')
        }
        data.update(pro)
        result['data'].append(data)


threads = []
thread_num = 5
pos = -1
now = datetime.now()
print("[开始时间] %s" % now)

with open(source_file, 'r') as f:
    source_data = json.load(f)

print("[总数] %s" % len(source_data))

for i in source_data:
    pos += 1
    t = threading.Thread(target=get_latest_release,
                         args=(i,))
    threads.append(t)
    if len(threads) == thread_num or pos == len(source_data) - 1:
        for t in threads:
            # time.sleep(30)
            t.start()
        for t in threads:
            t.join()
        threads = []

result['data'].sort(key=lambda item: sort_time(item['created_at']), reverse=True)
result['total'] = len(result['data'])
result['updated_at'] = datetime.utcfromtimestamp(time.mktime(now.timetuple())).isoformat() + 'Z'

if result['data']:
    dumps_result = json.dumps(result)
    with open(data_file, 'w') as f:
        f.write(dumps_result)
    with open(docs_data_file, 'w') as f:
        f.write(dumps_result)

end = datetime.now()
print("[结束时间] %s" % end)
print("[程序耗时] %s" % str(end - now))
