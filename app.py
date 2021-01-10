from flask import Flask, render_template
from flask_bootstrap import Bootstrap

import getdata

App = Flask(__name__)
Bootstrap = Bootstrap(App)


@App.route('/hello')
def hello_world():
    return render_template('hello.html')


@App.route('/')
def homepage():
    summaries = getdata.get_summary()
    return render_template('homepage.html', summary=summaries)


@App.route('/cat/<cat_id>')
def cat_info(cat_id: int):
    info = getdata.get_cat_info(cat_id)
    return render_template('category.html', catinfo=info)


@App.route('/feed/<feed_id>')
def feed_info(feed_id: int):
    info = getdata.get_feed_info(feed_id)
    return render_template('feed.html', feedid=feed_id, feedinfo=info)


@App.route('/api/get-freq-list-for-feed/<feed_id>')
def get_freq_list(feed_id: int):
    import json
    return json.dumps(getdata.get_freq_list_for_feed(feed_id))


if __name__ == '__main__':
    App.run(host='0.0.0.0')
