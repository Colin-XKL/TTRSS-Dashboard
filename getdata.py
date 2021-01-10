import os
from ttrss.client import TTRClient

Summary = {}
Feeds = {}


def get_client():
    ttrss_url = os.getenv('TTRSS_URL')
    ttrss_user = os.getenv('TTRSS_USER')
    ttrss_passwd = os.getenv('TTRSS_PASSWORD')
    # ttrss_url = 'http://URL'
    # ttrss_user = 'USERNAME'
    # ttrss_passwd = 'PASSWORD'
    client = TTRClient(ttrss_url, ttrss_user, ttrss_passwd)
    return client


def get_summary():
    client = get_client()
    client.login()
    Summary['feed_count'] = client.get_feed_count()
    Summary['unread_count'] = client.get_unread_count()
    Summary['label'] = len(client.get_labels())
    Summary['categories'] = client.get_categories()
    for cat in Summary['categories']:
        for feed in cat.Feeds():
            Feeds[feed.id] = feed
    client.logout()

    return Summary


def get_cat_info(cat_id: int):
    client = get_client()
    client.login()
    info = {}
    feeds = client.get_feeds(cat_id=cat_id)
    info['Feeds'] = feeds
    try:
        for cat in Summary['categories']:
            if cat.id == cat_id:
                info['cat'] = cat
    except:
        info['cat'] = 'Something went wrong...'
    client.logout()
    return info


def get_feed_info(feed_id: int):
    return Feeds[feed_id]


def get_freq_list_for_feed(feed_id: int):
    client = get_client()
    client.login()
    headlines = client.get_headlines(feed_id=feed_id)
    titles = []
    for headline in headlines:
        titles.append(headline.title)
    client.logout()

    split_result = split(titles)
    result = []
    for i in split_result:
        result.append({'x': i[0], 'value': i[-1]})
    if len(result) > 100:
        return result[:70]
    return result


def get_titles():
    client = get_client()
    client.login()
    cats = client.get_categories()
    cat = cats[0]
    feeds = cat.Feeds()
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
    for title in titles:
        for tmp_var in jieba.lcut(title):
            words.append(tmp_var)
    for word in words:
        if len(word) > 1:
            freq_map[word] = freq_map.get(word, 0) + 1
    freq_list = list(freq_map.items())
    freq_list.sort(key=lambda x: x[1], reverse=True)
    return freq_list
