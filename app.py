from jinja2 import Template
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import getdata

app = Flask(__name__)
bootstrap = Bootstrap(app)


@app.route('/hello')
def hello_world():
    return render_template('hello.html')


@app.route('/')
def homepage():
    s = getdata.get_summary()
    return render_template('homepage.html', summary=s)


@app.route('/cat/<int:catid>')
def cat_info(catid: int):
    info = getdata.get_cat_info(catid)
    return render_template('category.html', catinfo=info)


@app.route('/feed/<int:feedid>')
def feed_info(feedid: int):
    f = getdata.get_feed_info(feedid)
    return render_template('feed.html', feedid=feedid, feedinfo=f)


@app.route('/api/get-freq-list-for-feed/<int:feedid>')
def get_freq_list(feedid: int):
    import json
    return json.dumps(getdata.get_freq_list_for_feed(feedid))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
