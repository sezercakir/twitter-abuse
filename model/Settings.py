import json
import os
from pathlib import Path


class Settings:

    def __init__(self):
        self.json_file = self.read_settings_json()
        # tokens
        self.api_key = self.json_file['tokens']['api_key']
        self.api_key_secret = self.json_file['tokens']['api_key_secret']
        self.bearer_token = self.json_file['tokens']['bearer_token']
        self.access_token = self.json_file['tokens']['access_token']
        self.access_token_secret = self.json_file['tokens']['access_token_secret']
        # trend request
        self.target_location = self.json_file['trends']['target_location']
        self.woeid = self.json_file['trends']['woeid']
        self.start_now = True
        self.target_location = self.json_file['trends']['target_location']
        self.trend_time_inc_hours = self.json_file['trends']['time_inc_hours']
        self.trend_time_inc_minutes = self.json_file['trends']['time_inc_minutes']
        self.trend_time_inc_days = self.json_file['trends']['time_inc_days']
        # tweet request
        self.tweet_expansion = self.json_file['tweets']['expansions']
        self.tweet_max_results = self.json_file['tweets']['max_results']
        self.tweet_media_fields = self.json_file['tweets']['media_fields']
        self.tweet_place_fields = self.json_file['tweets']['place_fields']
        self.tweet_poll_fields = self.json_file['tweets']['poll_fields']
        self.tweet_since_id = self.json_file['tweets']['since_id']
        self.tweet_sort_order = self.json_file['tweets']['sort_order']
        self.tweet_tweet_fields = self.json_file['tweets']['tweet_fields']
        self.tweet_until_id = self.json_file['tweets']['until_id']
        self.tweet_user_fields = self.json_file['tweets']['user_fields']
        self.tweet_user_auth = self.json_file['tweets']['user_auth']
        self.tweet_api_query_parameters = self.json_file['tweets']['api']['query_parameters']
        self.tweet_api_lang = self.json_file['tweets']['api']['lang']
        self.tweet_api_query_parameters = self.tweet_api_query_parameters + " " + self.tweet_api_lang
        self.tweet_api_time_inc_minutes = self.json_file['tweets']['api']['time_inc_minutes']
        self.tweet_api_time_inc_hour = self.json_file['tweets']['api']['time_inc_hour']
        self.tweet_api_time_inc_day = self.json_file['tweets']['api']['time_inc_day']
        self.tweet_api_time_inc_seconds = self.json_file['tweets']['api']['time_inc_seconds']
        self.tweet_api_start_before_day = self.json_file['tweets']['api']['start_before_day']
        self.tweet_api_start_before_hour = self.json_file['tweets']['api']['start_before_hour']
        self.tweet_api_start_before_minutes = self.json_file['tweets']['api']['start_before_minutes']
        self.tweet_api_start_before_seconds = self.json_file['tweets']['api']['start_before_seconds']
        self.tweet_api_tweet_count = self.json_file['tweets']['api']['tweet_count']
        self.saved_tw_object = self.json_file['tweets']['saved_tw_object']
        self.lower_bound_tw_num = self.json_file['tweets']['lower_bound_tw_num']
        # abuser detection settings
        self.same_tweet_upper_bound = self.json_file['abuser_detection']['same_tweet_upper_bound']
        self.Same_tweet_hour_time_difference_bound = self.json_file['abuser_detection'][
            'Same_tweet_hour_time_difference_bound']
        self.selected_candidate_num_upper_bound = self.json_file['abuser_detection'][
            'selected_candidate_num_upper_bound']
        # bert settings
        self.bertopic_lang = self.json_file['bertopic']['language']

    @classmethod
    def read_settings_json(cls):
        """
       Read json file return as dict
       :return:    json_file
       """
        root_dir = Path(__file__).parent.parent
        json_path = os.path.join(root_dir, 'settings.json')

        assert os.path.exists(json_path)

        f = open(json_path)
        json_file = json.load(f)

        return json_file
