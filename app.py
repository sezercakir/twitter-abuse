from datetime import datetime

import tweepy
from flask import Flask, request, redirect, render_template
from flask_mail import Mail, Message
from requests_oauthlib import OAuth1Session
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

from db.db import check_from_db
from model.fetch.Trend import Trend
from model.Settings import Settings
from model.process.Bert import Bert
from model.utils import RetValue, EarlyRequestException

callback_url = 'http://localhost:5000/email'
session = dict()
app = Flask(__name__)
executor = ThreadPoolExecutor()

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'szrckrrr@gmail.com'  # Update with your email
app.config['MAIL_PASSWORD'] = 'hdhkocaljelunwoc'  # Update with your email password

mail = Mail(app)


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template("home.html", title="Home")


# This route starts the OAuth flow by redirecting the user topip install requests Twitter's authorization endpoint
@app.route('/authorize')
def authorize():
    settings = Settings()
    twitter = OAuth1Session(client_key=settings.api_key, client_secret=settings.api_key_secret,
                            callback_uri=callback_url)
    request_token = twitter.fetch_request_token('https://api.twitter.com/oauth/request_token')
    auth_url = twitter.authorization_url('https://api.twitter.com/oauth/authorize')
    session['request_token'] = request_token
    return redirect(auth_url)


# This route is the callback URL that Twitter redirects to after the user grants permission
@app.route('/email')
def callback():
    return render_template('email.html')


def run_algorithm(target_mail, action):
    with app.app_context():
        while True:
            try:
                tw_app = Trend()

                me = tw_app.twiter_obj.tw_api_client.get_me().data
                ret = check_from_db(me['id'], me['username'], target_mail)

                if ret[0] != RetValue.Success:
                    raise EarlyRequestException(me['username'])
                tw_app.get_trend_topics()

                tw_app.trends['trends'] = tw_app.trends['trends']
                abusers_from_1 = tw_app.twiter_obj.read_tweets_from_trend(tw_app.trends['trends'], tw_app.trends['as_of'])
                bert = Bert()
                bert.construct_graph(tw_app.twiter_obj.frames_dict.keys(),
                                     tw_app.twiter_obj.one_frame,
                                     tw_app.twiter_obj.one_frame_with_orient)

                abusers_from_2 = bert.detect_abuser_selection2()
                abusers_from_bert = bert.apply_bertopic()

                ids = list(set(abusers_from_1 + abusers_from_2 + abusers_from_bert))
                users = tw_app.twiter_obj.tw_api_client.get_users(ids=ids).data

                '''
                for user in users:
                    if action == "block":
                        tw_app.twitter_api.create_block(user_id=user.id)
                    else:
                        tw_app.twitter_api.create_mute(user_id=user.id)
                '''
                action = "Blocked" if action == "block" else "Muted"
                msg = Message("Abusers Listed", sender="szrckrrr@gmail.com", recipients=[target_mail])
                email_content = render_template('email_template.html', users=users,
                                                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user=me['name'])
                msg.html = email_content

                # Send email
                mail.send(msg)
            except tweepy.errors.TwitterServerError as e:
                print(e)
                continue
            except EarlyRequestException as e:
                msg = Message("Unsuccessful Request", sender="szrckrrr@gmail.com", recipients=[target_mail])
                email_content = render_template("email_template_fail.html", user=me['username'], hours=ret[1],
                                                date=datetime.now(), minutes=ret[2], seconds=ret[3])
                msg.html = email_content
                mail.send(msg)
                break
            except Exception as e:
                print(e)
                msg = Message('Unsuccessful Request', sender='szrckrrr@gmail.com',
                              recipients=['cakirta18@itu.edu.tr'])  # Update sender and recipients
                email_content = render_template('email_template_error.html', date=datetime.now())
                msg.html = email_content
                mail.send(msg)
                break
            break

@app.route('/detect_abuser', methods=['POST'])
def detect_abuser():
    try:
        to_email = request.form['email']
        action = request.form.get('action')

        p = Process(target=run_algorithm, args=(to_email, action,))
        p.start()

        return render_template("final.html", title="Error Musk")
    except Exception as e:
        return render_template("error.html", title="Error Musk")


if __name__ == '__main__':
    app.run(host='20.250.35.51', port=5000)


