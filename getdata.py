from ttrss.client import TTRClient
import os

summary = {}
feeds = {}


def get_client():
    ttrss_url = os.getenv('TTRSS_URL')
    ttrss_user = os.getenv('TTRSS_USER')
    ttrss_passwd = os.getenv('TTRSS_PASSWORD')
    # ttrss_url = 'http://URL'
    # ttrss_user = 'USERNSAME'
    # ttrss_passwd = 'PASSWORD'
    client = TTRClient(ttrss_url, ttrss_user, ttrss_passwd)
    return client


def get_summary():
    client = get_client()
    client.login()
    summary['feed_count'] = client.get_feed_count()
    summary['unread_count'] = client.get_unread_count()
    summary['label'] = len(client.get_labels())
    summary['categories'] = client.get_categories()
    for cat in summary['categories']:
        for f in cat.feeds():
            feeds[f.id] = f
    client.logout()

    return summary


def get_cat_info(catid: int):
    client = get_client()
    client.login()
    info = {}
    feeds = client.get_feeds(cat_id=catid)
    info['feeds'] = feeds
    try:
        for cat in summary['categories']:
            if cat.id == catid:
                info['cat'] = cat
        # info['cat'] = summary['categories'][catid]
    except:
        info['cat'] = 'Something went wrong...'
    client.logout()
    return info


def get_feed_info(feedid: int):
    # client=get_client()
    # client.login()
    # client.feed
    print(feeds[feedid].title)
    return feeds[feedid]


def get_freq_list_for_feed(feedid: int):
    # l=[]
    client = get_client()
    client.login()
    headlines = client.get_headlines(feed_id=feedid)
    titles = []
    for h in headlines:
        titles.append(h.title)
    client.logout()

    l = split(titles)
    re = []
    for i in l:
        # print(l)
        re.append({'x': i[0], 'value': i[-1]})
    if len(re) > 100:
        return re[:70]
    return re


def get_titles():
    from ttrss.client import TTRClient
    # client = TTRClient(ttrss_url, ttrss_user, ttrss_passwd)
    client = get_client()
    client.login()
    cats = client.get_categories()
    cat = cats[0]
    feeds = cat.feeds()
    feed = feeds[0]
    headlines = feed.headlines()
    titles = []
    for h in headlines:
        titles.append(h.title)
    client.logout()

    return titles


def split(titles: list):
    import jieba
    words = []
    freq_map = {}
    for t in titles:
        for tt in jieba.lcut(t):
            words.append(tt)
    for w in words:
        if len(w) > 1:
            freq_map[w] = freq_map.get(w, 0) + 1
    freq_list = list(freq_map.items())
    # print(freq_list)
    freq_list.sort(key=lambda x: x[1], reverse=True)
    # return freq_map
    return freq_list

