# Twitter Winner
# Based on Python CLI application by Alex Eames http://raspi.tv/?p=5281
# http://www.billthelizard.com/2013/12/creating-twitter-bot-on-google-app.html

from google.appengine.ext import webapp
from webapp2 import Route

import tweepy
import random
import secrets

# Consumer keys and access tokens, used for OAuth
consumer_key = secrets.consumer_key
consumer_secret = secrets.consumer_secret

access_token = secrets.access_token
access_token_secret = secrets.access_token_secret

# webapp2 config
app_config = {
  'webapp2_extras.sessions': {
    'cookie_name': '_simpleauth_sess',
    'secret_key': secrets.SESSION_KEY
  },
  'webapp2_extras.auth': {
    'user_attributes': []
  }
}

routes = [
  Route('/', handler='handlers.RootHandler'),
  Route('/followers', handler='handlers.FollowersHandler'),
  Route('/retweets', handler='handlers.RetweetsHandler'),
  Route('/searches', handler='handlers.SearchesHandler'),
  Route('/profile', handler='handlers.ProfileHandler', name='profile'),

  Route('/logout', handler='handlers.AuthHandler:logout', name='logout'),
  Route('/auth/<provider>',
    handler='handlers.AuthHandler:_simple_auth', name='auth_login'),
  Route('/auth/<provider>/callback',
    handler='handlers.AuthHandler:_auth_callback', name='auth_callback'),
]

application = webapp.WSGIApplication(routes, config=app_config, debug=True)
