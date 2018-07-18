# Gitrax - GitHub Username Search

## Introduction
This script is a tool for searching GitHub usernames via the GitHub API and returning data on that username. This is particularly helpful when Analysts come across GitHub accounts containing potentially malicious tools. The data returned helps fingerprint a GitHub user and their connections.

## Prerequisites
The python script run on python3 (preferably python3.6) and uses [requests](http://docs.python-requests.org/en/master/).

```
$ pip3 install requests
or
$ pip3 install -r requirements.txt
```

## Usage
This script takes numerous flags as arguments. If no flag is provided, the script will lookup all email addresses associated with a GitHub username.
```
$ python3 gitrax.py -h
usage: gitrax.py [-h] [-a] [-e] [-f] [-F] [-g] [-i] [-o] [-O] [-r] [-s] [-S]
                 [-t TOKEN] username

Search GitHub for User data

positional arguments:
  username              The GitHub username to search

optional arguments:
  -h, --help            show this help message and exit
  -a, --all             Gather all informaiton for GitHub username
  -e, --email           Find email(s) for GitHub username. This is the default lookup.
  -f, --followers       List followers for GitHub username
  -F, --following       List following for GitHub username
  -g, --gists           List gists for GitHub username
  -i, --info            List info for GitHub username
  -o, --organizations   List organizations for GitHub username
  -O, --outfile         Save results to file
  -r, --repos           List repos for GitHub username
  -s, --starred         List starred for GitHub username
  -S, --subscriptions   List subscriptions for GitHub username
  -t TOKEN, --token TOKEN
                        Use GitHub Personal Access Token. format: -t
                        user:token
```
The default behavior prints the results to screen. If you want to save the results to file, pass the `-O` flag.  The following example will lookup all emails and gists for a username, and then print the output to screen as well as saving it to a json file.
```
$ python3 gitrax -e -g -O username
```
The most common usage is to lookup all the fields using the `-a` flag. This will lookup all emails, followers, following, gists, organizations, repos, starred, and subscriptions for a GitHub username.  This flag will output results to your screen and save them in a json file.
```
$ python3 gitrax.py -a username
```

## Authentication
GitHub API [rate limits](https://developer.github.com/v3/?#rate-limiting) unauthenticated users to 60 requests/hour. If you wish to authenticate for 5000 requests/hour, you can provide your username:password or username:token (Personal Access Token) with the `-t user:token` flag. Authenticating also allows you to directly query for the username email address. If email address is `null`, we will check public events for any related email addresses.
```
$ python3 gitrax -a -t myuser:mypass username
```

## Email Results
A quick note about email addresses found. The script first tries to directly grab the username's email address. If no authentication is passed or the value for email is `null`, the script then searches public events for a specific username. It grabs all emails found in the public events. While this will most likely capture the email tied to the username, it will also grab the emails of all authors that have contributed to the user's repos. If you need to dig into it a bit more, you can search the user's public events at `https://api.github.com/users/<insert username here>/events/public`
