# -*- coding: utf-8 -*-
import logging
import secrets

import webapp2
from webapp2_extras import auth, sessions, jinja2
from jinja2.runtime import TemplateNotFound

from simpleauth import SimpleAuthHandler

import tweepy
import random
from tweepy.error import TweepError

# Consumer keys and access tokens, used for OAuth
consumer_key = secrets.consumer_key
consumer_secret = secrets.consumer_secret


class BaseRequestHandler(webapp2.RequestHandler):
  def dispatch(self):
    # Get a session store for this request.
    self.session_store = sessions.get_store(request=self.request)

    try:
      # Dispatch the request.
      webapp2.RequestHandler.dispatch(self)
    finally:
      # Save all sessions.
      self.session_store.save_sessions(self.response)

  @webapp2.cached_property
  def jinja2(self):
    """Returns a Jinja2 renderer cached in the app registry"""
    return jinja2.get_jinja2(app=self.app)

  @webapp2.cached_property
  def session(self):
    """Returns a session using the default cookie key"""
    return self.session_store.get_session()

  @webapp2.cached_property
  def auth(self):
      return auth.get_auth()

  @webapp2.cached_property
  def current_user(self):
    """Returns currently logged in user"""
    user_dict = self.auth.get_user_by_session()
    return self.auth.store.user_model.get_by_id(user_dict['user_id'])

  @webapp2.cached_property
  def logged_in(self):
    """Returns true if a user is currently logged in, false otherwise"""
    return self.auth.get_user_by_session() is not None


  def render(self, template_name, template_vars={}):
    # Preset values for the template
    values = {
      'url_for': self.uri_for,
      'logged_in': self.logged_in,
      'flashes': self.session.get_flashes()
    }

    # Add manually supplied template values
    values.update(template_vars)

    # read the template or 404.html
    try:
      self.response.write(self.jinja2.render_template(template_name, **values))
    except TemplateNotFound:
      self.abort(404)

  def head(self, *args):
    """Head is used by Twitter. If not there the tweet button shows 0"""
    pass


class RootHandler(BaseRequestHandler):
  def get(self):
    """Handles default landing page"""
    if self.logged_in:
        self.render('home.html', {
        'user': self.current_user,
        'session': self.auth.get_user_by_session()
      })
    else:
        self.render('home.html')

class ProfileHandler(BaseRequestHandler):
  def get(self):
    """Handles GET /profile"""
    if self.logged_in:
      self.render('profile.html', {
        'user': self.current_user,
        'session': self.auth.get_user_by_session()
      })
    else:
      self.redirect('/')

class FollowersHandler(BaseRequestHandler):
  def get(self):
    """Handles GET /followers"""
    if self.logged_in:
      user = self.current_user

      # OAuth process, using the keys and tokens
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
      auth.set_access_token(user.access_token, user.access_token_secret)

      # Creation of the actual interface, using authentication
      api = tweepy.API(auth)

      followers = list()
      incomplete_list = False
      try:
          # the maximum per request is 200 according to
          # https://dev.twitter.com/rest/reference/get/followers/list
          for follower in tweepy.Cursor(api.followers,count=200).items():
              followers.append(follower)
      except TweepError as e:
          logging.error(e)
          limits = api.rate_limit_status('statuses')
          logging.info(limits)
          incomplete_list = True

      winner = False
      if len(followers) > 0:
        random_number = random.randint(0, len(followers)-1)
        winner = followers[random_number]

      self.render('followers.html', {
        'user': user,
        'session': self.auth.get_user_by_session(),
        'followers': followers,
        'winner': winner,
        'incomplete_list': incomplete_list,
      })
    else:
      self.redirect('/')

class RetweetsHandler(BaseRequestHandler):
  def get(self):
    """Handles GET /retweets"""
    if self.logged_in:
      user = self.current_user
      tweet_id = self.request.get("id")

      # OAuth process, using the keys and tokens
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
      auth.set_access_token(user.access_token, user.access_token_secret)

      # Creation of the actual interface, using authentication
      api = tweepy.API(auth)

      if not tweet_id:
          retweets_list = list()
          for tweet in api.retweets_of_me():
              retweets_list.append(tweet)

          self.render('retweets.html', {
            'user': user,
            'session': self.auth.get_user_by_session(),
            'retweets': retweets_list,
          })
      else:
          retweet = api.get_status(tweet_id)
          retweeters = api.retweeters(tweet_id)
          random_number = random.randint(0, len(retweeters)-1)
          winner = api.get_user(retweeters[random_number])

          self.render('retweets.html', {
            'user': user,
            'session': self.auth.get_user_by_session(),
            'winner': winner,
            'retweet': retweet,
          })
    else:
      self.redirect('/')

class SearchesHandler(BaseRequestHandler):
  def get(self):
    """Handles GET /searches"""
    if self.logged_in:
      user = self.current_user
      search_id = self.request.get("id")

      # OAuth process, using the keys and tokens
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
      auth.set_access_token(user.access_token, user.access_token_secret)

      # Creation of the actual interface, using authentication
      api = tweepy.API(auth)

      if not search_id:
          searches_list = list()
          incomplete_list = False
          try:
            for search in api.saved_searches():
                searches_list.append(search)
          except TweepError as e:
            logging.error(e)
            limits = api.rate_limit_status('statuses')
            logging.info(limits)
            incomplete_list = True

          self.render('searches.html', {
            'user': user,
            'session': self.auth.get_user_by_session(),
            'searches': searches_list,
            'incomplete_list': incomplete_list,
          })
      else:
          search = api.get_saved_search(search_id)
          print search.query
          statuses = list()
          tweeters = list()
          # max 100 https://dev.twitter.com/rest/reference/get/search/tweets
          for status in api.search(q=search.query, count=100):
            statuses.append(status)
            tweeters.append(status.user)
          random_number = random.randint(0, len(tweeters)-1)
          winner = tweeters[random_number]

          self.render('searches.html', {
            'user': user,
            'session': self.auth.get_user_by_session(),
            'winner': winner,
            'tweet': statuses[random_number],
          })
    else:
      self.redirect('/')

class AuthHandler(BaseRequestHandler, SimpleAuthHandler):
  """Authentication handler for OAuth 2.0, 1.0(a) and OpenID."""

  # Enable optional OAuth 2.0 CSRF guard
  OAUTH2_CSRF_STATE = True

  USER_ATTRS = {
    'facebook' : {
      'id'     : lambda id: ('avatar_url',
        'http://graph.facebook.com/{0}/picture?type=large'.format(id)),
      'name'   : 'name',
      'link'   : 'link'
    },
    'google'   : {
      'picture': 'avatar_url',
      'name'   : 'name',
      'profile': 'link'
    },
    'windows_live': {
      'avatar_url': 'avatar_url',
      'name'      : 'name',
      'link'      : 'link'
    },
    'twitter'  : {
      'profile_image_url': 'avatar_url',
      'screen_name'      : 'name',
      'link'             : 'link'
    },
    'linkedin' : {
      'picture-url'       : 'avatar_url',
      'first-name'        : 'name',
      'public-profile-url': 'link'
    },
    'linkedin2' : {
      'picture-url'       : 'avatar_url',
      'first-name'        : 'name',
      'public-profile-url': 'link'
    },
    'foursquare'   : {
      'photo'    : lambda photo: ('avatar_url', photo.get('prefix') + '100x100' + photo.get('suffix')),
      'firstName': 'firstName',
      'lastName' : 'lastName',
      'contact'  : lambda contact: ('email',contact.get('email')),
      'id'       : lambda id: ('link', 'http://foursquare.com/user/{0}'.format(id))
    },
    'openid'   : {
      'id'      : lambda id: ('avatar_url', '/img/missing-avatar.png'),
      'nickname': 'name',
      'email'   : 'link'
    }
  }

  def _on_signin(self, data, auth_info, provider):
    """Callback whenever a new or existing user is logging in.
     data is a user info dictionary.
     auth_info contains access token or oauth token and secret.
    """
    auth_id = '%s:%s' % (provider, data['id'])
    logging.info('Looking for a user with id %s', auth_id)

    user = self.auth.store.user_model.get_by_auth_id(auth_id)
    _attrs = self._to_user_model_attrs(data, self.USER_ATTRS[provider])

    if user:
      logging.info('Found existing user to log in')
      # Existing users might've changed their profile data so we update our
      # local model anyway. This might result in quite inefficient usage
      # of the Datastore, but we do this anyway for demo purposes.
      #
      # In a real app you could compare _attrs with user's properties fetched
      # from the datastore and update local user in case something's changed.
      user.populate(**_attrs)
      user.access_token = auth_info['oauth_token']
      user.access_token_secret = auth_info['oauth_token_secret']
      user.put()
      self.auth.set_session(
        self.auth.store.user_to_dict(user))

    else:
      # check whether there's a user currently logged in
      # then, create a new user if nobody's signed in,
      # otherwise add this auth_id to currently logged in user.

      if self.logged_in:
        logging.info('Updating currently logged in user')

        u = self.current_user
        u.populate(**_attrs)
        user.access_token = auth_info['oauth_token']
        user.access_token_secret = auth_info['oauth_token_secret']
        # The following will also do u.put(). Though, in a real app
        # you might want to check the result, which is
        # (boolean, info) tuple where boolean == True indicates success
        # See webapp2_extras.appengine.auth.models.User for details.
        u.add_auth_id(auth_id)

      else:
        logging.info('Creating a brand new user')
        ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
        if ok:
          user.access_token = auth_info['oauth_token']
          user.access_token_secret = auth_info['oauth_token_secret']
          user.put()
          self.auth.set_session(self.auth.store.user_to_dict(user))

    # Remember auth data during redirect, just for this demo. You wouldn't
    # normally do this.
    #self.session.add_flash(data, 'data - from _on_signin(...)')
    #self.session.add_flash(auth_info, 'auth_info - from _on_signin(...)')

    self.redirect('/')

  def logout(self):
    self.auth.unset_session()
    self.redirect('/')

  def handle_exception(self, exception, debug):
    logging.error(exception)
    self.render('error.html', {'exception': exception})

  def _callback_uri_for(self, provider):
    return self.uri_for('auth_callback', provider=provider, _full=True)

  def _get_consumer_info_for(self, provider):
    """Returns a tuple (key, secret) for auth init requests."""
    return secrets.AUTH_CONFIG[provider]

  def _to_user_model_attrs(self, data, attrs_map):
    """Get the needed information from the provider dataset."""
    user_attrs = {}
    for k, v in attrs_map.iteritems():
      attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
      user_attrs.setdefault(*attr)

    return user_attrs
