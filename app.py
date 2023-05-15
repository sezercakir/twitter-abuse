from datetime import datetime
from time import sleep

from flask import Flask, request, redirect, url_for, render_template, current_app
from flask_mail import Mail, Message
from requests_oauthlib import OAuth1Session
from decouple import config
from bertopic import BERTopic
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process

from model.fetch.Trend import Trend
from model.Settings import Settings
from model.process.Bert import Bert

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

@app.route('/detect_abusers', methods=['POST', 'GET'])
def test():

    executor.submit(run_algorithm(request.form['email']))
    executor.submit(some_long_task1())
    executor.submit(some_long_task2, 'hello', 123)
    return render_template("final.html")


def some_long_task1():
    print("Task #1 started!")
    sleep(30)
    print("Task #1 is done!")

def some_long_task2(arg1, arg2):
    print("Task #2 started with args: %s %s!" % (arg1, arg2))
    sleep(5)
    print("Task #2 is done!")

@app.route('/', methods=['POST', 'GET'])
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

def run_algorithm(target_mail):

    with app.app_context():
        try:
                tw_app = Trend()
                tw_app.get_trend_topics()
                #TODO
                tw_app.trends['trends'] = tw_app.trends['trends'][:2]
                abusers_from_1 = tw_app.twiter_obj.read_tweets_from_trend(tw_app.trends['trends'], tw_app.trends['as_of'])
                bert = Bert()
                bert.construct_graph(tw_app.twiter_obj.frames_dict.keys(),
                                     tw_app.twiter_obj.one_frame,
                                     tw_app.twiter_obj.one_frame_with_orient)

                abusers_from_2 = bert.detect_abuser_selection2()

                #TODO appyl beart
                ids = list(set(abusers_from_1 + abusers_from_2))
                fields = ["id", "name", "username", "url"]
                users = tw_app.twiter_obj.tw_api_client.get_users(ids=ids, user_fields=fields).data

                #TODO link bozuk
                msg = Message('Abusers Blocked', sender="szrckrrr@gmail.com", recipients=[target_mail])
                email_content = render_template('email_template.html', users=users, date=datetime.now())
                msg.html = email_content

                # Send email
                mail.send(msg)
        except Exception as e:
            print(e)
            msg = Message('Test Email', sender='szrckrrr@gmail.com',
                          recipients=['cakirta18@itu.edu.tr'])  # Update sender and recipients
            email_content = render_template('email_template_error.html', date=datetime.now())
            msg.html = email_content

            # Send email
            mail.send(msg)


@app.route('/detect_abuser', methods=['POST'])
def detect_abuser():
    try:
        to_email = request.form['email']
        p = Process(target=run_algorithm, args=(to_email,))
        p.start()

        return render_template("final.html", title="Error Musk")
    except Exception as e:
        return render_template("error.html", title="Error Musk")


if __name__ == '__main__':
    app.run(debug=True)
