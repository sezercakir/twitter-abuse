import sys
from datetime import timedelta, datetime

import pandas as pd
import pause
import tweepy
import iso8601

from model.utils import RetValue, clean_text
from model.Settings import Settings

class Twitter(Settings):
    def __init__(self):
        super().__init__()
        self.total_tweet_count = 0
        self.tweet_num_is_enough = False
        self.frames_list = list()
        self.frames_list_orinet_record = list()
        self.frames_dict = dict()
        self.one_frame = None
        self.abuser_list = list()
        self.one_frame_with_orient = None
        self.abusers_from_selection1 = None
        self.detected_abuser_num = 0
        self.tw_api_client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)

    def read_tweets_from_trend(self, trend_request_responses, as_of):
        """
        Extract the trend name as string from the response dict and iterate over the
        hashtag to read and write the tweets to the file.

        :param trend_request_responses:
        :param trend_req_responses:   Response of Twitter api for trend topic reqeust.
        :return:    void
        """

        for trend_request_response in trend_request_responses:
            if self.read_tweets_from_topic(trend_request_response['name'], as_of) \
                    is RetValue.TotalTweetCountIsEnough:
                break

        self.one_frame = pd.concat(self.frames_list)
        self.one_frame_with_orient = sum(self.frames_list_orinet_record, [])

        return [item for sublist in self.abuser_list for item in sublist]

    def read_tweets_from_topic(self, h_tag, trends_as_of):
        """
        Algorithm sends request to Twitter api with trend topic time and updated request time
        amount of the tw api settings writen in the json file.

        end_time , parameter of search_recent_tweets function specifies request time.

        Argument of search_recent_tweets function is filled in here. Request response is parsed
        tweet_keys and stored the list data structure. At the end of the time interval tweets are writen.

        :param trends_as_of:    Request response time for each trend topic.
        :param h_tag:           Hashtag as string

        :return:
        """
        # The as_of field contains the timestamp when the list of trends was created.
        # Because end_time must be prior min ten seconds from request time, seconds parameter is 15.
        curr_time = iso8601.parse_date(trends_as_of) - timedelta(seconds=15)

        finish_time = curr_time - timedelta(days=self.tweet_api_start_before_day,
                                            hours=self.tweet_api_start_before_hour,
                                            minutes=self.tweet_api_start_before_minutes,
                                            seconds=self.tweet_api_start_before_seconds)

        tweet_list_to_write = []

        query = h_tag + self.tweet_api_query_parameters
        tweet_keys = ['text', 'tw_id', 'author_id', 'created_at']
        i = 0 #TODO delete i
        print(h_tag)
        while curr_time >= finish_time and i < 10:
            pause.seconds(1)
            returned_tweets = self.tw_api_client.search_recent_tweets(query=query,
                                                                      end_time=curr_time,
                                                                      media_fields=self.tweet_media_fields,
                                                                      place_fields=self.tweet_place_fields,
                                                                      poll_fields=self.tweet_poll_fields,
                                                                      sort_order=self.tweet_sort_order,
                                                                      tweet_fields=self.tweet_tweet_fields,
                                                                      user_fields=self.tweet_user_fields,
                                                                      max_results=self.tweet_max_results,
                                                                      expansions=self.tweet_expansion
                                                                      )
            print(i)
            i+=1
            curr_time -= timedelta(days=self.tweet_api_time_inc_day,
                                   hours=self.tweet_api_time_inc_hour,
                                   minutes=self.tweet_api_time_inc_minutes,
                                   seconds=self.tweet_api_time_inc_seconds)

            # sometimes because of short time interval response returns with None data
            if returned_tweets.data is None:
                continue
            for a_tweet in returned_tweets[0]:
                tweet_values = [a_tweet['text'], a_tweet['id'], a_tweet['author_id'], str(a_tweet['created_at']),
                                h_tag]

                tweet_list_to_write.append(tweet_values)

        # whole tweets for one topic
        tweet_keys.append("Topic")
        df = pd.DataFrame(data=tweet_list_to_write, columns=tweet_keys)
        df = df.drop_duplicates(subset='tw_id', keep='first')
        # add abuser column as completely not abuser
        abuser_list = [False] * df.shape[0]
        df['abuser'] = abuser_list
        print("End Hashtag")
        if df.shape[0] > self.lower_bound_tw_num:

            ################ ! ###################
            self.detect_abuser_selection1(df)
            ################ ! ###################
            df['clean_text'] = df.text.apply(clean_text)
            self.frames_dict[h_tag] = df
            self.frames_list.append(df)
            self.frames_list_orinet_record.append(df.to_dict(orient='record'))
            self.total_tweet_count += df.shape[0]
            if self.total_tweet_count > self.tweet_api_tweet_count:
                return RetValue.TotalTweetCountIsEnough

        return RetValue.Success

    def detect_abuser_selection1(self, df):
        """

        :param df:
        :return:
        """
        ############################## ABUSER DETECTION - SELECTION I #################################
        ####################################### ATTENTION #############################################

        df['abuser'] = df.groupby(['text', 'author_id'], sort=False).transform('count')['tw_id'] > \
                                                                            self.same_tweet_upper_bound
        # ABUSER
        abusers = df[df['abuser'] == True]['author_id'].tolist()
        if not len(abusers) == 0:
            print("Abuser DETECTED 1", file=sys.stderr)
            self.detected_abuser_num += len(abusers)
            self.abuser_list.append(abusers)

