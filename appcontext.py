from model.fetch.Trend import Trend


def main():
    tw_app = Trend()
    tw_app.get_trend_topics()
    print(tw_app.trends)
    abusers_from_1 = tw_app.twiter_obj.read_tweets_from_trend(tw_app.trends['trends'], tw_app.trends['as_of'])



if __name__ == '__main__':
    main()