#! /usr/bin/env python3

import argparse
import requests
import time

from subprocess import call

parser = argparse.ArgumentParser(description='Wait for pushes to Bitcoin COre and then build docs')
parser.add_argument('--skip-first-build', action="store_true", help='Skip the first build')
args = parser.parse_args()

def BuildDocSite():
    call(['git', 'pull'], cwd='../bitcoin')
    call(['make', 'docs'], cwd='../bitcoin')
    call(['cp', '-r', 'doc/doxygen/html', '../bitcoin-docs-gen'], cwd='../bitcoin')
    call(['git', 'add', 'html/'])
    call(['git', 'commit', '-m', 'Update docs'])
    call(['git', 'push'])
    print("Finished build\n\n")

# On start, update repo, build, and push to github
if not args.skip_first_build:
    print("Doing first build")
    BuildDocSite()

r = requests.get('https://api.github.com/networks/bitcoin/bitcoin/events')
data = r.json()
best_id = data[0]['id']
etag = r.headers['etag']
poll_time = int(r.headers['X-Poll-Interval'])

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
    poll_time = int(r.headers['X-Poll-Interval'])
