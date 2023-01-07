import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from threading import Thread
# from pprint import pprint
import os
import time


class TrumpTwitter:
    def __init__(self, date1, date2):
        self.date1 = date1
        self.date2 = date2
        self.headers = {
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        }
        self.twitter_text = []

    def get_token(self):
        '''
        获取token，以正常访问目标url
        :return:
        '''
        base_url = 'https://twitter.com/search?q=(from%3ArealDonaldTrump)%20until%3A{}%20since%3A{}&src=typed_query'.format(
            self.date1, self.date2)
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get(base_url)
        cookies = driver.get_cookies()
        # pprint(cookies)
        for i in cookies:
            if i['name'] == 'gt':
                self.token = i['value']
        driver.close()

    def get_start_info(self):
        self.json_url = 'https://api.twitter.com/2/search/adaptive.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&send_error_codes=true&simple_quoted_tweet=true&q=(from%3ArealDonaldTrump)%20until%3A{}%20since%3A{}&tweet_search_mode=live&count=20&query_source=typed_query&pc=1&spelling_corrections=1&ext=mediaStats%2ChighlightedLabel'.format(
            self.date1, self.date2)
        self.headers['x-guest-token'] = self.token
        # pprint(self.headers)
        r = requests.get(self.json_url, headers=self.headers)
        # pprint(r.text)
        r_json = r.json()
        self.judge = len(r_json)
        self.cursor = r_json['timeline']['instructions'][0]['addEntries']['entries'][-1]['content']['operation']['cursor']['value']
        twitters = r_json['globalObjects']['tweets']
        for index, twitter in twitters.items():
            if twitter['user_id'] == 25073877:
                self.twitter_text.append(twitter['full_text'])

    def get_rest_info(self):
        flag = True
        while flag:
            new_json_url = self.json_url + '&cursor=' + self.cursor
            new_r = requests.get(new_json_url, headers=self.headers)
            new_r_json = new_r.json()
            self.judge = len(new_r_json)
            # print(self.judge)
            if self.judge == 2:
                # 判断该搜索日期内是否爬虫完毕，以cursor作为判断，因为最后一个url返回的新cursor和上一个cursor是一样的
                if self.cursor == new_r_json['timeline']['instructions'][2]['replaceEntry']['entry']['content']\
                        ['operation']['cursor']['value']:
                    flag = False  # 跳出while循环
                else:
                    # 如果不相等获取新的cursor，继续循环
                    self.cursor = new_r_json['timeline']['instructions'][2]['replaceEntry']['entry']['content']\
                        ['operation']['cursor']['value']
                    # print(self.cursor)
                # 包含所有推文信息的字典
                twitters = new_r_json['globalObjects']['tweets']
                for index, twitter in twitters.items():
                    try:
                        # 判断推文是否为川普发出的，以川普推特的user_id:25073877来判断
                        if twitter['user_id'] == 25073877:
                            # 单独存放推文内容
                            self.twitter_text.append(twitter['full_text'])
                    except:
                        continue
            else:
                self.get_token()
                # print(self.token)
                self.headers['x-guest-token'] = self.token

    def data_output(self):
        with open('./temp/TrumpTwitter(form {} to {}).txt'.format(self.date1, self.date2), 'w', encoding='utf-8') as f:
            for text in self.twitter_text:
                f.write('{}\n'.format(text))


def multiThread(func):
    '''
    多线程异步方法执行封装
    :param func:
    :return:
    '''
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()
    return wrapper



if __name__ == '__main__':
    @multiThread
    def run_spider(date1, date2):
        print('Trump\'s twitter from {} to {}, loading...'.format(date1, date2))
        t = TrumpTwitter(date1, date2)
        t.get_token()
        # print(t.token)
        t.get_start_info()
        t.get_rest_info()
        t.data_output()
        print('Trump\'s twitter from {} to {}, done!'.format(date1, date2))
        if len(os.listdir('./temp')) == 4:
            print('Integrating...')
            with open('C:\\Users\\ZYQ\\Desktop\\TrumpTwitter.txt', 'w', encoding='utf-8') as f:
                for i in os.listdir('./temp'):
                    with open(i, 'r', encoding='utf-8') as f1:
                        f.write(f1.read())
            print('TrumpTwitter.txt is generated, ALL IS WELL!')


    date_list = [('2017-12-31', '2017-01-20'),
                 ('2018-12-31', '2018-01-01'),
                 ('2019-12-31', '2019-01-01'),
                 ('2020-12-31', '2020-01-01'), ]

    for date1, date2 in date_list:
        run_spider(date1, date2)

