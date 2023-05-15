
from enum import Enum
import re
import nltk
import numpy as np
from nltk import word_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')

"""{
   "tokens": {
      "api_key":"veOiakdoYZayInWUQiDyIdcfA",
      "api_key_secret": "bVlVORrXH0X1GmPTtJDaafxJZCSkbzNMRDf8OnOQuJ2qImWSHK",
      "bearer_token": "AAAAAAAAAAAAAAAAAAAAAMLLjgEAAAAArPcmG%2BjsI4%2B5LxauwEoxgOmcCYk%3DxsKI6KaD3Mhs9JU0XKbIZOWVMLzibi7wqgGSzdWAhzGWK88gLt",
      "access_token": "4375117036-HY70RTJOo0ArEmb8wAfEsd9hgjOqvW2sTDAnkji",
      "access_token_secret": "n1xJFaP0FfsxxRTT5pp9eYJnbyok86NUjTBYiQtUPA9eL"
   },
   "trends": {
      "target_location": "Turkey",
      "woeid": null,
      "test": false ,
      "start_now": true,
      "start_time": "2.12.22 14:20:00",
      "time_inc_hours": 5,
      "time_inc_minutes": 0,
      "time_inc_days": 0,
      "end_time": "22.04.23 20:00:00"
   },
   "tweets": {
      "expansions": ["author_id", "entities.mentions.username","attachments.media_keys", "attachments.poll_ids", "referenced_tweets.id"],
      "max_results": 100,
      "media_fields": ["media_key","preview_image_url","url", "type"],
      "next_token": "None",
      "place_fields": ["id", "full_name", "country", "country_code", "geo", "place_type", "contained_within"],
      "poll_fields": ["duration_minutes","end_datetime","id","options","voting_status"],
      "since_id" : "None",
      "sort_order": "recency",
      "tweet_fields": ["entities","created_at", "text", "attachments", "lang","geo", "possibly_sensitive", "source", "context_annotations"],
      "until_id": "None",
      "user_fields": ["id","name", "url","username", "location", "verified", "description", "profile_image_url", "entities"],
      "user_auth": false,
      "api_settings": {
         "query_parameters": " -is:retweet -is:reply -has:media lang:tr",
         "time_inc_minutes": 3,
         "time_inc_hour": 0,
         "time_inc_day": 0,
         "time_inc_seconds": 0,
         "start_before_day": 0,
         "start_before_hour": 8,
         "start_before_minutes": 0,
         "start_before_seconds": 0,
         "tweet_count": 1200000
      },
      "saved_tw_object": {
         "text": true,
         "tw_id": true,
         "author_id": true,
         "created_at": true
      }
   },
   "data": {
      "excel_node_list_upper_bound": 2,
      "threshold_num_tweets": 200,
      "total_num_tweets": null,
      "target_num_hashtag": null,
      "maks_tw_per_hashtag": null
   },
   "abuser_detection": {
      "same_tweet_upper_bound": 1,
      "Same_tweet_hour_time_difference_bound": 1,
      "selected_candidate_num_upper_bound": 100
   },
   "bertopic": {
      "language": "turkish"
   }
}"""

def get_stop_words():
    stop_words_tr = stopwords.words("turkish")
    with open('turkce-stop-words.txt', encoding="utf-8") as f:
        lines = f.read().splitlines()

    new_words = list()
    # Strips the newline character
    for line in lines:
        new_words.append(line)
    
    stop_words_tr.extend(new_words)

    return np.unique(np.array(stop_words_tr)).tolist()


def clean_text(x):
    x = str(x)
    x = x.lower()
    x = re.sub(r'#[A-Za-zğüşıöçĞÜŞİÖÇ0-9-_]*', '', x, flags=re.IGNORECASE | re.UNICODE)
    x = re.sub(r'https*://.*', '', x)
    x = re.sub(r'@[A-Za-zğüşıöçĞÜŞİÖÇ0-9-_]+', '', x, flags=re.IGNORECASE | re.UNICODE)
    tokens = word_tokenize(x)
    x = ' '.join([w for w in tokens if not w.lower() in get_stop_words()])
    x = re.sub(r'[%s]' % re.escape('!"#$%&\()*+,-./:;<=>?@[\\]^_`{|}~“…”’'), ' ', x)
    x = re.sub(r'\d+', ' ', x)
    x = re.sub(r'\n+', ' ', x)
    x = re.sub(r'\s{2,}', ' ', x)
    return x


class RetValue(Enum):
    TotalTweetCountIsEnough = 2,
    TotalTweetCountIsNotEnough = 3,
    Success = 0,
    Fail = 1
