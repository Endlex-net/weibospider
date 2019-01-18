from urllib import parse as url_parse
import datetime
import time
import itertools

from logger import crawler
from .workers import app
from page_get import get_page
from config import get_max_search_page
from page_parse import search as parse_search
from db.dao import (
    KeywordsOper, KeywordsDataOper, WbDataOper)


# This url is just for original weibos.
# If you want other kind of search, you can change the url below
# But if you change this url, maybe you have to rewrite some part of the parse code
URL = 'http://s.weibo.com/weibo/{}&scope=ori&suball=1&page={}'
MAX_URL = 'https://s.weibo.com/weibo?q={}&page={}&typeall=1&suball=1&timescope=custom:{}&Refer=g'
# Use this if results are too little
# URL = 'http://s.weibo.com/weibo/{}&nodup=1&page={}'
LIMIT = get_max_search_page() + 1

BEGIN_DATE = "2018-01-01"


def getBetweenDay(begin_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d',time.localtime(time.time())), "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list

DATE_LIST = getBetweenDay(BEGIN_DATE)
TIME_LIIT = list(range(0, 23))
SEARCH_TIME_LIST = ["{}-{}:{}-{}".format(d, t, d, t+1) for d, t in itertools.product(DATE_LIST, TIME_LIIT)]

@app.task(ignore_result=True)
def search_keyword(keyword, keyword_id):
    for s_time in SEARCH_TIME_LIST:
        crawler.info('We are searching keyword "{}", {}'.format(keyword, s_time))
        cur_page = 1
        encode_keyword = url_parse.quote(keyword)
        while cur_page < LIMIT:
            cur_url = MAX_URL.format(encode_keyword, cur_page, s_time)
            # current only for login, maybe later crawling page one without login
            search_page = get_page(cur_url, auth_level=2)
            if "您可以尝试更换关键词，再次搜索" in search_page:
                break
            if not search_page:
                crawler.warning('No search result for keyword {}, the source page is {}'.format(keyword, search_page))
                cur_page += 1
                continue
                # return

            search_list = parse_search.get_search_info(search_page)

            if cur_page == 1:
                cur_page += 1
            elif 'noresult_tit' not in search_page:
                cur_page += 1
            else:
                crawler.info('Keyword {} has been crawled in this turn'.format(keyword))
                return

            # Because the search results are sorted by time, if any result has been stored in mysql,
            # We don't need to crawl the same keyword in this turn
            for wb_data in search_list:
                #print(wb_data)
                rs = WbDataOper.get_wb_by_mid(wb_data.weibo_id)
                KeywordsDataOper.insert_keyword_wbid(keyword_id, wb_data.weibo_id)
                # todo incremental crawling using time
                if rs:
                    crawler.info('Weibo {} has been crawled, skip it.'.format(wb_data.weibo_id))
                    continue
                else:
                    WbDataOper.add_one(wb_data)
                    # todo: only add seed ids and remove this task
                    app.send_task('tasks.user.crawl_person_infos', args=(wb_data.uid,), queue='user_crawler',
                                  routing_key='for_user_info')

@app.task(ignore_result=True)
def execute_search_task():
    keywords = KeywordsOper.get_search_keywords()
    for each in keywords:
        app.send_task('tasks.search.search_keyword', args=(each[0], each[1]), queue='search_crawler',
                      routing_key='for_search_info')