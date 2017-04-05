from flask import Flask, request, render_template, flash
import os

from time import time
from datetime import datetime

from bokeh.charts import Bar
from bokeh.embed import components
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import PanTool, WheelZoomTool, HoverTool, ResetTool, TapTool, LassoSelectTool
from bokeh.models import CustomJS
from bokeh import layouts
from bokeh.models.ranges import Range1d

import io
import simplejson as json
from requests_oauthlib import OAuth1
import requests
import pandas
import numpy

from nltk.tokenize import TweetTokenizer
import string
# from nltk.corpus import stopwords
from collections import Counter

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'flask flash requires session cookies which in turn require a secret key'

# set up twitter access token #
with(open('config.txt','r')) as config:
    secrets = json.loads(config.read())

my_auth = OAuth1(
    secrets["api_key"],
    secrets["api_secret"],
    secrets["access_token"],
    secrets["access_token_secret"]
)

####################################

# read saved tweets from previous searches
# each json block represents one previous search
# 'search_metadata' is the search result head
# 'statuses' is a list of tweets in json format
tweet_data = []
with io.open('tweets.txt','rt',encoding='utf-8') as tweet_file:
    for line in tweet_file:
        tweet_data.append(json.loads(line))

tweet_list = []
for item in tweet_data:
    tweet_list.extend(item['statuses'])


# read saved embed code from previous searches
# 'html' stores the blockquote code
embed_dict = {}
with io.open('embed_code.txt','rt',encoding='utf-8') as embed_file:
    embed_dict = json.loads(embed_file.read())

##################################################

# tweet tags (topic, popularity, similarity)
tweet_tags = pandas.DataFrame(numpy.random.rand(len(tweet_list), 2), columns={'x','y'})
tweet_tags['tweet_id'] = [item['id_str'] for item in tweet_list]

# build the plot
plot_source = ColumnDataSource(data=dict(x=tweet_tags['x'], y=tweet_tags['y'], tid=tweet_tags['tweet_id']))
hover = HoverTool(tooltips=[('index','$index'),('tweet_id','@tid')])
p = figure(plot_width=500, tools=[PanTool(), WheelZoomTool(), hover, ResetTool(), TapTool(), LassoSelectTool()])
p.circle('x','y',source=plot_source)
scr, di = components(p)

# scr, di = components(p)

#plot_source2 = ColumnDataSource(data=dict(x=[], y=[]))
#p2 = figure(plot_width=500, x_range=(0,1),y_range=(0,1))
#p2.circle('x','y',source=plot_source2)
# scr2, di2 = components(p)

#p3 = layouts.column(p, p2)


#plot_source.callback = CustomJS(args=dict(s2=plot_source2), code="""
#    var inds = cb_obj.selected['1d'].indices;
#    var d1 = cb_obj.data;
#    var d2 = s2.data;
#    d2['x'] = []
#    d2['y'] = []
#    for (i=0; i<inds.length; i++) {
#        d2['x'].push(d1['x'][inds[i]])
#        d2['y'].push(d1['y'][inds[j]])
#    }
#    s2.trigger('change');
#""")
                     
# plot_source.on_change('selected',flash_selected)

###############################################################

# given tweet index in tweet_list, return the tweet blockquote embed code
def get_tweet_blockquote(tweet_index):
    tweet_id = tweet_list[tweet_index]['id_str']
    user_id = tweet_list[tweet_index]['user']['id_str']

    if tweet_id not in embed_dict:
        tweet_url = 'url=https://twitter.com/' + user_id + '/status/' + tweet_id
        embed_code = requests.get('https://publish.twitter.com/oembed?' + tweet_url)
        embed_dict[tweet_id] = embed_code.json()
        tweet_blockquote = embed_code.json()['html']
        with io.open('embed_code.txt',mode='w',encoding='utf-8') as embed_file:
            embed_file.write(json.dumps(embed_dict, ensure_ascii=False))
    else:
        tweet_blockquote = embed_dict[tweet_id]['html']

    return tweet_blockquote

################################################################


#def flash_selected(attr, old, new):
#    flash('got a point')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_query():

    # get the query from the form
    tweet_query_keyword = request.form['tweet_query']

    # query twitter
    # tweet_query_result = requests.get('https://api.twitter.com/1.1/search/tweets.json',
    #                                auth=my_auth,
    #                                params={'q': tweet_query_keyword,
    #                                        'count': '100'}
    #                                )
    # tweet_list = tweet_query_result.json()['statuses']

    tweet_n = numpy.random.randint(0, len(tweet_list))
    tweet_blockquote = get_tweet_blockquote(tweet_n)
        
    return render_template('index.html',
                           plot_script=scr,
                           plot_div=di,
                           tweet_blockquote = tweet_blockquote)
    
    #if len(tweet_list) == 0:
    #    flash('something went wrong, no tweets acquired')
    #    
    #else:
    #    flash(str(len(tweet_list)) + ' tweets acquired')

    #    tweet_data = pandas.DataFrame()

    #    for tweet in tweet_query_result.json()['statuses']:
    #        select_data = pandas.Series([tweet['entities']['hashtags'],
    #                       tweet['favorite_count'],
    #                       tweet['retweet_count'],
    #                       tweet['text']])
    #        tweet_data = tweet_data.append(select_data, ignore_index=True)

    #    tweet_data.columns=['hashtags',
    #                        'favorite_count',
    #                        'retweet_count',
    #                        'text']

    #    English_stopwords = []
    #    with open('English_stopwords.txt','r') as English_stop_file:
    #        for line in English_stop_file:
    #            English_stopwords.append(line.strip())

    #    exclude_words = English_stopwords + \
    #                    list(string.punctuation) + \
    #                    ['rt', 'via', 'https']

    #    tweet_text_tokenize = TweetTokenizer(preserve_case=False,
    #                                         strip_handles=True,
    #                                         reduce_len=True)

    #    text_token_list = []
    #    for item in tweet_data['text']:
    #        try:
    #            text_token_list.append([word for word in tweet_text_tokenize.tokenize(item)
    #                                    if word not in exclude_words])
    #        except:
    #            text_token_list.append([])
    #    tweet_data['text_token'] = text_token_list

    #    text_token_count = Counter()
    #    for item in tweet_data['text_token']:
    #        text_token_count.update(item)
            
    #    text_token_100 = [item[0] for item in text_token_count.most_common(100)]
    #    text_token_100_count = [item[1] for item in text_token_count.most_common(100)]
        
    #    p = Bar(text_token_100_count[:20], legend=False)

        # obtain the script and div components and insert them in index.html
    #    scr, di = components(p)
    #    return render_template('index.html',
    #                           plot_script=scr,
    #                           plot_div=di)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host = '0.0.0.0', port = port)
    # app.run()
