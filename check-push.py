#! /usr/bin/env python3

import requests
import time

from subprocess import call

def BuildDocSite():
    call(['git', 'pull'], cwd='../bitcoin')
    call(['make', 'docs'], cwd='../bitcoin')
    call(['cp', 'doc/doxygen/html', '../bitcoin-docs-gen'], cwd='../bitcoin')
    call(['git', 'add', 'html/'])
    call(['git', 'commit', '-m', 'Update docs'])
    call(['git', 'push'])

# On start, update repo, build, and push to github
BuildDocSite()

r = requests.get('https://api.github.com/networks/bitcoin/bitcoin/events')
data = r.json()
best_id = data[0]['id']
etag = r.headers['etag']
poll_time = r.headers['X-Poll-Interval']

while True:
    # Wait for poll time
    time.sleep(poll_time)

    # Make requests in loop until we get new info
    r = requests.get('https://api.github.com/networks/bitcoin/bitcoin/events', headers={'If-None-Match' : etag})
    while r.status_code == 304:
        time.sleep(poll_time)
        r = requests.get('https://api.github.com/networks/bitcoin/bitcoin/events', headers={'If-None-Match' : etag})
    data = r.json()

    # Check if there was a PushEvent
    for event in data:
        if event['id'] == best_id:
            break
        if event['type'] == 'PushEvent':
            BuildDocSite()
            break
    best_id = data[0]['id']
    poll_time = r.headers['X-Poll-Interval']
