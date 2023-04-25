from flask import Flask, request, redirect, url_for, render_template
from requests_oauthlib import OAuth1Session
from decouple import config

app = Flask(__name__)

# Replace these with your own Twitter API credentials
consumer_key = config('TWITTER_CLIENT_ID')
consumer_secret = config('TWITTER_CLIENT_SECRET')
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAAT3mgEAAAAAQV4dFSFrk%2BQSTYocvYRWZl5i61U%3DYhpcSZSgvb8hlnw2zNKeqc3o8c1H3Zz0oYFy9akzXrVJj3qVEe'
# This is the callback URL that Twitter will redirect to after the user grants permission
callback_url = config('TWITTER_CALLBACK_URL')
session = dict()


@app.route('/')
def home():
    return render_template("home.html", title="Home")


# This route starts the OAuth flow by redirecting the user topip install requests Twitter's authorization endpoint
@app.route('/authorize')
def authorize():
    twitter = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=callback_url)
    request_token = twitter.fetch_request_token('https://api.twitter.com/oauth/request_token')
    auth_url = twitter.authorization_url('https://api.twitter.com/oauth/authorize')
    session['request_token'] = request_token
    return redirect(auth_url)


# This route is the callback URL that Twitter redirects to after the user grants permission
@app.route('/callback')
def callback():
    request_token = session['request_token']
    twitter = OAuth1Session(consumer_key, client_secret=consumer_secret,
                            resource_owner_key=request_token['oauth_token'],
                            resource_owner_secret=request_token['oauth_token_secret'],
                            verifier=request.args['oauth_verifier'])
    access_token = twitter.fetch_access_token('https://api.twitter.com/oauth/access_token')
    # Store the access token and access token secret for future use
    access_token_key = access_token['oauth_token']
    access_token_secret = access_token['oauth_token_secret']
    # Use the access token and access token secret to post tweets on behalf of the user
    # You can use a library like Tweepy or make raw API calls using a library like Requests
    # Example: post a tweet
    tweet = "Hello, Twitter!"
    tweet_url = "https://api.twitter.com/1.1/statuses/update.json"
    tweet_data = {"status": tweet}
    tweet_auth = OAuth1Session(consumer_key, client_secret=consumer_secret, resource_owner_key=access_token_key,
                               resource_owner_secret=access_token_secret)
    tweet_auth.post(tweet_url, data=tweet_data)

    """api = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    user = api.get_users(ids=id_)"""


if __name__ == '__main__':
    app.run(debug=True)
