from datetime import datetime

import tweepy
from flask import Flask, request, redirect, url_for, render_template
from flask_mail import Mail, Message
from requests_oauthlib import OAuth1Session
from decouple import config
from bertopic import BERTopic

from model.fetch.Trend import Trend
from model.Settings import Settings
from model.process.Bert import Bert

callback_url = 'http://localhost:5000/email'
session = dict()
app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'szrckrrr@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'hdhkocaljelunwoc'  # Update with your email password

mail = Mail(app)

@app.route('/')
def home():
    return render_template("home.html", title="Home")

# This route starts the OAuth flow by redirecting the user topip install requests Twitter's authorization endpoint
@app.route('/authorize')
def authorize():
    settings = Settings()
    twitter = OAuth1Session(client_key=settings.api_key, client_secret=settings.api_key_secret, callback_uri=callback_url)
    request_token = twitter.fetch_request_token('https://api.twitter.com/oauth/request_token')
    auth_url = twitter.authorization_url('https://api.twitter.com/oauth/authorize')
    session['request_token'] = request_token
    return redirect(auth_url)


# This route is the callback URL that Twitter redirects to after the user grants permission
@app.route('/email')
def callback():
    return render_template('email.html')


@app.route('/detect_abuser', methods=['POST'])
def detect_abuser():
    try:
        to_email = request.form['email']
        now = datetime.now()

        app = Trend()
        app.get_trend_topics()
        abusers_from_1 = app.twiter_obj.read_tweets_from_trend(app.trends['trends'], app.trends['as_of'])
        bert = Bert()
        bert.construct_graph(app.twiter_obj.frames_dict.keys(),
                             app.twiter_obj.one_frame,
                             app.twiter_obj.one_frame_with_orient)

        abusers_from_2 = bert.detect_abuser_selection2()
        abusers_from_3 = bert.apply_bertopic(app.twiter_obj.one_frame)
        ids = abusers_from_1 + abusers_from_2 + abusers_from_3
        # mute, block part
        # Authenticate to Twitter API
        users = app.twiter_obj.tw_api_client.get_users(ids=abusers_from_1 + abusers_from_2)
        """app.twiter_obj.tw_api_client.block(target_user_id=1234)

        user_fields = ['description', 'followers_count', 'url']  # Specify additional fields
        # mail notification about blocked accounts
        response_list = list()
        for id_ in ids:
            resp = app.twiter_obj.tw_api_client.get_user(id=id_, user_field=user_fields)
            response_list.append((id_, resp.screen_name, resp.url))


        ##### FINAL #####
        email_content = render_template('abusers.html', abusers=response_list)

        # Create email message
        msg = Message('Subj.', sender='szrckrrr@gmail.com',recipients=to_email)  # Update sender and recipients
        msg.html = email_content

        # Send email
        mail.send(msg)
    except Exception as e:
        return render_template("error.html", title="Error Musk")"""
    finally:
        pass


if __name__ == '__main__':
    app.run(debug=True)
