# Twitter Hashtag Abuse

The project aims to detect and state the trending tweets that abuse the trend topics and hashtags.
Twitter *[Elevated Access](https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api)
level is used in this project. 

## Algorithm
- Get Trends
- Get Tweets belonged each trend
- Convert tweets data to graph.
- Run detection algorithms on data
  - Text Based <br> If the minimum three words in the tweet are in
the top five tfidf scores in a topic suggested by
BERTopic, this is not an abuser
  - Topic Based <br>
  If the standard deviation of the distribution of
the topics of the tweet among the topics
suggested by BERTopic is less than 0.44, it
means that the topics are homogeneously
distributed. This ensures that the real topics
are almost equally distributed in different
topics within the BERT, and the tweet's topics
are interpreted as unrelated to each other. It
is abuser. <br>
  If the number of the tweet's topics is less than
75% of the distribution in the BERTopic
suggestions, it means that the tweet’s topics
are very widely distributed in BERT and it is
abuser. <br>
  If the number of actual tweet topics in the
BERTopic statement is greater than or equal
to half of the total number of tweets, it is not
an abuser. Topics are stacked on a BERT
proposition.
  - Send notifications email that contains abusers

## Usage 
Azure VM is used for deployment. It can run on your local with following command.
```
python app.py
```
## Project Arguments

Arguments stored in the settings.json [file](settings.json).

- tokens: Tokens key in the json file stores the necessary tokens for accesing the twitter api.
- trends: Trends key keeps the information about the getting trend topics.
  - test: Test value only runs once for testing, default value **false**.
  - start_now: Start_now value represent that whether program is desired to start now or not, default value is **true**.
  - start_time: Start_time represent program start time. Program wait until the start time. 
  - end_time: End_time represent last request time for trending. It **must** be set.
  - time_inc_hours: Increments time an hour for requesting the api for getting trends.
  - time_inc_minutes: Increments time a minutes for requesting the api for getting trends.
  - time_inc_days: Increments time a day for requesting the api for getting trends.

- tweets: It contains the settings about tweets read from Twitter api and its request information.
- Expansions and other fields of tweets are parameters of *[search_recent_tweets](https://docs.tweepy.org/en/stable/client.html#tweepy.Client.search_recent_tweets)*
- function. For more information about field and expansion [->](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)
  - api_settings: It contains the request information for access the tweets has specific trend topic.
    - time_inc_minutes: Increment request end time that is the newest, most recent UTC timestamp to which the Tweets will be provided.
    - time_inc_hour: Increment request end time as amount as hour like time_inc_minutes.
    - time_inc_second: Increment request end time as amount as second like time_inc_minutes.
    - time_inc_day: Increment request end time as amount as day like time_inc_minutes.
    - start_before_day: The algorithm pulls the data backwards from the time the request was made. Start_before_day is used
    for setting the last request time.
    - start_before_hour, start_before_minutes, start_before_seconds: It is used same as start_before_day. 
    - query_parameters: It consists the main body of the query. For more information [->](https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query)
  - saved_tw_object: It represents that which tweet fields will be saved to file. 



