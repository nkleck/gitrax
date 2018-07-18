"""
Overview

Lookup GitHub username data.
get started with:
$ python3 gitrax -h
"""

import argparse
import requests
import json


class GitLookup(object):
    def do_all(self, username, auth):
        result = {}
        result.update(self.info_lookup(username, auth))
        result.update(self.email_lookup(username, auth))
        result.update(self.misc_lookup(username, auth, 'followers'))
        result.update(self.misc_lookup(username, auth, 'following'))
        result.update(self.misc_lookup(username, auth, 'organizations'))
        result.update(self.repos_lookup(username, auth))
        result.update(self.gists_lookup(username, auth))
        result.update(self.misc_lookup(username, auth, 'starred'))
        result.update(self.misc_lookup(username, auth, 'subscriptions'))
        self.outfile_save(args.username, result)
        return result

    def info_lookup(self, username, auth):
        # grab info about account directly
        url = "https://api.github.com/users/{}"
        response = requests.get(url.format(username), auth=auth)
        instance = {}
        if response.status_code == 200:
            json_data = response.json()
            instance['name'] = json_data['name']
            instance['login'] = json_data['login']
            instance['email'] = json_data['email']
            instance['created_at'] = json_data['created_at']
            instance['html_url'] = json_data['html_url']
            instance['company'] = json_data['company']
            instance['bio'] = json_data['bio']
            instance['blog'] = json_data['blog']
            instance['followers'] = json_data['followers']
            instance['following'] = json_data['following']
            instance['public_gists'] = json_data['public_gists']
            instance['public_repos'] = json_data['public_repos']
        # make dict
        results = {"info": instance}
        return results

    def email_lookup(self, username, auth):
        # set email list we append to
        email_list = []
        if auth:
            # we'll gry grabbing email directly first, with auth
            url = "https://api.github.com/users/{}"
            response = requests.get(url.format(username), auth=auth)
            if response.status_code == 200:
                json_data = response.json()
                # check if value for email, otherwise its null
                if json_data['email']:
                    # append email to email list
                    email_list.append(json_data['email'])
                    # make dict
                    results = {"email": email_list}
                    return results
        # trying public events, no auth passed or null email value
        # set public events url
        events_url = "https://api.github.com/users/{}/events/public?page={}"
        # make request to github public events endpoint
        # endpoint supports pagination 0-9
        count = 0
        while count < 10:
            response = requests.get(events_url.format(username, count), auth=auth)
            if response.status_code == 200:
                json_data = response.json()
                # check page returned data, if not exit loop
                if len(json_data) > 0:
                    # outer is a list
                    for event in json_data:
                        for k, v in event.items():
                            # find json containing emails
                            if k == "payload":
                                for sk, sv in v.items():
                                    # within json is a list: commits
                                    if sk == "commits":
                                        # iterate list and pull emails
                                        for item in sv:
                                            email = item["author"]["email"]
                                            email_list.append(email)
                else:
                    # exiting loop
                    count = count + 10
            count = count + 1
        # remove duplicates
        email_list = list(set(email_list))
        # make dict
        results = {"email": email_list}
        return results

    def misc_lookup(self, username, auth, lookup_type):
        # set url and nested key
        if lookup_type == 'followers':
            url = 'https://api.github.com/users/{}/followers'
            key = 'login'
        elif lookup_type == 'following':
            url = 'https://api.github.com/users/{}/following'
            key = 'login'
        elif lookup_type == 'organizations':
            url = 'https://api.github.com/users/{}/orgs'
            key = 'login'
        elif lookup_type == 'starred':
            url = 'https://api.github.com/users/{}/starred'
            key = 'html_url'
        elif lookup_type == 'subscriptions':
            url = 'https://api.github.com/users/{}/subscriptions'
            key = 'html_url'
        # make request to github followers endpoint
        misc_list = []
        response = requests.get(url.format(username), auth=auth)
        if response.status_code == 200:
            json_data = response.json()
            for item in json_data:
                misc_list.append(item[key])
            # remove duplicates
            misc_list = list(set(misc_list))
        results = {lookup_type: misc_list}
        return results

    def gists_lookup(self, username, auth):
        # set url
        url = 'https://api.github.com/users/{}/gists?page={}&per_page=100'
        # make request to github gists endpoint
        gists_list = []
        # endpoint supports pagination and page length
        count = 1
        while count < 30:
            response = requests.get(url.format(username, count), auth=auth)
            if response.status_code == 200:
                json_data = response.json()
                # check page returned data, if not exit loop
                if len(json_data) > 0:
                    for item in json_data:
                        instance = {}
                        instance['html_url'] = item['html_url']
                        instance['description'] = item['description']
                        gists_list.append(instance)
                else:
                    # exiting loop
                    count = count + 30
            count = count + 1
        results = {"gists": gists_list}
        return results

    def repos_lookup(self, username, auth):
        # set url
        url = 'https://api.github.com/users/{}/repos?page={}&per_page=100'
        # make request to github gists endpoint
        repos_list = []
        # endpoint supports pagination and page length
        count = 1
        while count < 30:
            response = requests.get(url.format(username, count), auth=auth)
            if response.status_code == 200:
                json_data = response.json()
                # check page returned data, if not exit loop
                if len(json_data) > 0:
                    for item in json_data:
                        instance = {}
                        instance['repo_name'] = item['full_name']
                        instance['description'] = item['description']
                        instance['url'] = item['html_url']
                        repos_list.append(instance)
                else:
                    # exiting loop
                    count = count + 30
            count = count + 1
        results = {"repos": repos_list}
        return results

    def outfile_save(self, username, json_data):
        with open('{}.json'.format(username), 'w') as outfile:
            json.dump(json_data, outfile, indent=4, sort_keys=True)


def parse_args():
    parser = argparse.ArgumentParser(description='Search GitHub for User data')
    # Add optional arguments to parser
    parser.add_argument('-a', '--all', action="store_true", help='Gather all informaiton for GitHub username')
    parser.add_argument('-e', '--email', action="store_true", help='Find email(s) for GitHub username. This is the default lookup.')
    parser.add_argument('-f', '--followers', action="store_true", help='List followers for GitHub username')
    parser.add_argument('-F', '--following', action="store_true", help='List following for GitHub username')
    parser.add_argument('-g', '--gists', action="store_true", help='List gists for GitHub username')
    parser.add_argument('-i', '--info', action="store_true", help='List info for GitHub username')
    parser.add_argument('-o', '--organizations', action="store_true", help='List organizations for GitHub username')
    parser.add_argument('-O', '--outfile', action="store_true", help='Save results to file')
    parser.add_argument('-r', '--repos', action="store_true", help='List repos for GitHub username')
    parser.add_argument('-s', '--starred', action="store_true", help='List starred for GitHub username')
    parser.add_argument('-S', '--subscriptions', action="store_true", help='List subscriptions for GitHub username')
    parser.add_argument('-t', '--token', type=str, help='Use GitHub Personal Access Token. format: -t user:token')
    # set required argument
    parser.add_argument('username', type=str, help='The GitHub username to search')
    # set args
    args = parser.parse_args()
    return args


def main(args):
    # make args a dict
    myargs = vars(args)
    # check for OAuth2 token
    if myargs['token']:
        auth = (myargs['token'].split(':')[0], myargs['token'].split(':')[1])
    else:
        auth = None
    # instantiate lookups
    lookup = GitLookup()
    # set dict we will append to
    json_result = {}
    # if all flag set, skip the rest
    if myargs['all']:
        # do all the lookups
        json_result.update(lookup.do_all(args.username, auth))
    else:
        # go through flags and do appropiate lookups
        if myargs['info']:
            json_result.update(lookup.info_lookup(args.username, auth))
        if myargs['email']:
            json_result.update(lookup.email_lookup(args.username, auth))
        if myargs['followers']:
            json_result.update(lookup.misc_lookup(args.username, auth, 'followers'))
        if myargs['following']:
            json_result.update(lookup.misc_lookup(args.username, auth, 'following'))
        if myargs['organizations']:
            json_result.update(lookup.misc_lookup(args.username, auth, 'organizations'))
        if myargs['repos']:
            json_result.update(lookup.repos_lookup(args.username, auth))
        if myargs['gists']:
            json_result.update(lookup.gists_lookup(args.username, auth))
        if myargs['starred']:
            json_result.update(lookup.misc_lookup(args.username, auth, 'starred'))
        if myargs['subscriptions']:
            json_result.update(lookup.misc_lookup(args.username, auth, 'subscriptions'))
    if not json_result:
        # no flags passed, default to email lookup
        json_result = lookup.email_lookup(args.username, auth)
    if myargs['outfile']:
        # save output to file flag was passed.
        lookup.outfile_save(args.username, json_result)

    # print results to console
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("Searched Username: {}".format(args.username))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    for lookup, result in json_result.items():
        print("Section: {}".format(lookup.upper()))
        if lookup == 'info':
            for k, v in result.items():
                print("{}: {}".format(k, v))
        elif lookup == 'repos' or lookup == 'gists':
            for entry in result:
                for k, v in entry.items():
                    print("{}: {}".format(k, v))
                print('\n')
        else:
            for item in result:
                print(item)
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


if __name__ == '__main__':
    args = parse_args()
    main(args)
