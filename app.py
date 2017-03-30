from flask import Flask, request, render_template, flash
import os

from time import time
from datetime import datetime

from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models.ranges import Range1d

import simplejson as json
from requests_oauthlib import OAuth1
import requests
import pandas
from nltk.tokenize import TweetTokenizer
import string
# from nltk.corpus import stopwords
from collections import Counter

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'flask flash requires session cookies which in turn require a secret key'


with(open('config.txt','r')) as config:
    secrets = json.loads(config.read())

my_auth = OAuth1(
    secrets["api_key"],
    secrets["api_secret"],
    secrets["access_token"],
    secrets["access_token_secret"]
)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_query():

    # get the query from the form
    tweet_query_keyword = request.form['tweet_query']

    # query twitter
    tweet_query_result = requests.get('https://api.twitter.com/1.1/search/tweets.json',
                                    auth=my_auth,
                                    params={'q': 'los angeles',
                                            'count': '100'}
                                    )
    tweet_list = tweet_query_result.json()['statuses']

    if len(tweet_list) == 0:
        flash('something went wrong, no tweets acquired')
        
    else:
        flash(str(len(tweet_list)) + ' tweets acquired')

        tweet_data = pandas.DataFrame()

        for tweet in tweet_query_result.json()['statuses']:
            select_data = pandas.Series([tweet['entities']['hashtags'],
                           tweet['favorite_count'],
                           tweet['retweet_count'],
                           tweet['text']])
            tweet_data = tweet_data.append(select_data, ignore_index=True)

        tweet_data.columns=['hashtags',
                            'favorite_count',
                            'retweet_count',
                            'text']

        English_stopwords = []
        with open('English_stopwords.txt','r') as English_stop_file:
            for line in English_stop_file:
                English_stopwords.append(line.strip())

        exclude_words = English_stopwords + \
                        list(string.punctuation) + \
                        ['rt', 'via', 'https']

        tweet_text_tokenize = TweetTokenizer(preserve_case=False,
                                             strip_handles=True,
                                             reduce_len=True)

        text_token_list = []
        for item in tweet_data['text']:
            try:
                text_token_list.append([word for word in tweet_text_tokenize.tokenize(item)
                                        if word not in exclude_words])
            except:
                text_token_list.append([])
        tweet_data['text_token'] = text_token_list

        text_token_count = Counter()
        for item in tweet_data['text_token']:
            text_token_count.update(item)
            
        text_token_100 = [item[0] for item in text_token_count.most_common(100)]
        text_token_100_count = [item[1] for item in text_token_count.most_common(100)]
        
        p = Bar(text_token_100_count[:20], legend=False)

        # obtain the script and div components and insert them in index.html
        scr, di = components(p)
        return render_template('index.html',
                               plot_script=scr,
                               plot_div=di)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port = port)
    # app.run()
