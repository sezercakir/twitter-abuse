from datetime import datetime, timedelta
from pathlib import Path

import geocoder
import geocoder.api
import pause
import tweepy

from model.Settings import Settings
from model.fetch.Tweet import Twitter


class Trend(Settings):
    """

    """

    def __init__(self):
        super().__init__()
        self.trends = None
        self.tweets_per_trend = {}

        self.twiter_obj = Twitter()
        self.twitter_api = self.get_api()

    def get_api(self):
        auth = tweepy.OAuthHandler(self.api_key, self.api_key_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth)

    def get_trend_topics(self):
        """

        :return:
        """
        woeid = self.woeid
        if woeid is None:
            g = geocoder.api.osm(self.target_location)
            closest_loc = self.twitter_api.closest_trends(g.lat, g.lng)
            woeid = closest_loc[0]["woeid"]

        self.trends = self.twitter_api.get_place_trends(woeid)[0]