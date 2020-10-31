# Twitter Winner

Use your Twitter data to randomly pick a winner. Useful for conducting contests and giveaways.

## Test

1. `~/bin/google_appengine/dev_appserver.py twitter-winner/`

## Deploy

1. Check current version: `gcloud app versions list`
1. Deploy new version to test URL: `gcloud app deploy --no-promote --version X`
1. Test new version.
1. Deploy new version to production URL: `gcloud app deploy --version X`

## Secrets

This app requires that you create a `secrets.py` file with the following contents. For security, the file is ignored by git.

```
# This is a session secret key used by webapp2 framework.
# Get 'a random and long string' from here:
# http://clsc.net/tools/random-string-generator.php
# or execute this from a python shell: import os; os.urandom(64)
SESSION_KEY = ""

# Create Twitter application at https://developer.twitter.com/apps
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

TWITTER_CONSUMER_KEY = consumer_key
TWITTER_CONSUMER_SECRET = consumer_secret

AUTH_CONFIG = {
  'twitter'     : (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET),
}
```
