# Twitter Winner
# Based on Python CLI application by Alex Eames http://raspi.tv/?p=5281
# http://www.billthelizard.com/2013/12/creating-twitter-bot-on-google-app.html

from google.appengine.ext import webapp

import tweepy
import random
import secrets

# Consumer keys and access tokens, used for OAuth
consumer_key = secrets.consumer_key
consumer_secret = secrets.consumer_secret
access_token = secrets.access_token
access_token_secret = secrets.access_token_secret

def pick_winner():
    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    
    # Creation of the actual interface, using authentication
    api = tweepy.API(auth)

    print "Retweets: ([enter] to select, any key to see next retweet)"
    winning_rewtweet = None
    for retweet in tweepy.Cursor(api.retweets_of_me).items():
        print "(%ix) %s" % (retweet.retweet_count, retweet.text)
        if str(raw_input('? ')) == '':
            winning_rewtweet = retweet
            break
            
    if not winning_rewtweet:
        print "You must select a retweet to pick a winner from"
        return
        
    retweets = api.retweets(winning_rewtweet.id)
    
    random_number = random.randint(0, len(retweets)-1)
    winner = retweets[random_number].user
    print "The winner is @%s !" % (winner.screen_name)


class MainPage(webapp.RequestHandler):
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')


application = webapp.WSGIApplication([('/', MainPage)], debug=True)

