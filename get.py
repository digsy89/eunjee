# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import urllib
from datetime import datetime
import time
import json
import sys
from random import random

query = " ".join(sys.argv[1:])

# 기본 URL
url="https://twitter.com/i/search/timeline"

# TOEKN 비슷한거
token="BD1UO2FFu9QAAAAAAAAETAAAAAcAAAASAAAAAAAAAAAAAAAgAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAQAAAAAAAAAAA"

# unix timestamp to Date Class
def dt(ts):
  return datetime.fromtimestamp(int(ts))

def get(mp=None):
  ts = int(time.time())

  # 파라미터
  params = {
    "vertical":"default",
    "q":query,
    "src":"typd",
    "include_available_features":1,
    "include_entities":1,
    "last_note_ts":str(ts),
    "f":"tweets"
  }

  # max_position 파라미터가 있는경우, 두번째 request 
  if mp is not None:
    params['max_position']=mp
    params['reset_error_state']='false'

  # Requesst 헤더
  headers = {
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36',
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language":"ko-KR,ko; q=0.4",
    "X-Requeted-With":"XMLHttpRequest"
  }

  # 파라미터 URL 인코드
  p = urllib.urlencode(params)

  # 전체 URL
  _url = url + "?" + p
  print _url

  # Request 생성
  req = urllib2.Request(_url, headers=headers)

  # Request
  res = urllib2.urlopen(req).read()

  # JSON 파싱
  data=json.loads(res)

  """
    response json key 목록
    1. has_more_items
    2. focused_refresh_interval
    3. items_html -> 트윗 html
    4. new_latent_count
  """

  has_more = data['has_more_items']
  print has_more
  print data.keys()
  if data.has_key('min_position'):
    print data['min_position']

  
  # 트윗 html 파싱
  soup = BeautifulSoup(data['items_html'], 'lxml')

  # 트윗 목록
  twl = soup.select('li.stream-item')

  tweet_list = []
  print "get %d number of tweet"%(len(twl))
  
  # t <- li.stream-item
  for t in twl:
    # span._timestamp ELEMENT의 data-time ATTRIBUTE 
    ts=t.find('span', class_="_timestamp")['data-time']
    _time = dt(ts)
    _id = t['data-item-id']
    txt = t.find('p', class_="tweet-text").text
    tweet_list += [{'ts':ts, 'dt':_time, 'text':txt, 'id':_id}]

  return tweet_list

first = None
last = None
cnt = 0
zero_cnt=0

while True:
  # 랜덤 sleep
  sleeptime = random() + 1.0
  try:
    if first is None:
      twl = get()
    else:
      """
      두 번째부터 max-position 파라미터 설정
      max-position = TWEET-<first tweet id>-<last tweet id>-<token>
      <first tweet id> = 가장 예전 tweet id
      <last tweet id> = 가장 최근 tweet id
      <token> = query 에 따라 달라지는 듯
      """
      twl = get("TWEET-%s-%s-%s"%(first,last,token))

    cnt += len(twl)

    if len(twl) == 0:
      zero_cnt+=1
      time.sleep(sleeptime)
      continue

    for i in twl:
      print i['id'], i['ts'], i['dt']
      print i['text'].encode('utf-8')

    # 두번째 트윗을 last ID 로 설정  
    if last is None:
      last = twl[1]['id']
    # request 마다 제일 예전 트윗을 first로 갱신
    first = twl[-1]['id']
    time.sleep(sleeptime)
  except:
    print "searched %d tweets"%(cnt)
    exit()
