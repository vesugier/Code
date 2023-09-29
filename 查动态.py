import requests
import json
import datetime
import re
from urllib.parse import quote
from time import sleep

blacklist = 615286

defaultkey = "真爱粉，靓号在手，走路带风，解锁专属粉丝卡片，使用专属粉丝装扮，你也来生成你的专属秀起来吧！"

key = "我是#乃琳个性装扮2.0#"
key = defaultkey
target = "000"
access_key = ""

result = []
payload={}
headers = {
   'User-Agent': 'apifox/1.0.0 (https://www.apifox.cn)',
   'Accept': '*/*',
   'Host': 'api.vc.bilibili.com',
   'Connection': 'keep-alive',
   'Cookie': 'l=v'
}

for num in range(0, 300):
   url = f"https://api.vc.bilibili.com/search_svr/v1/Search/list_all?access_key={access_key}&appkey=1d8b6e7d45233436&build=6340400&mobi_app=android&page_no={num}&page_size=50&word={quote(key)}&sign=af9ba9a2c1e7ffceb5cbd1924a33ba51"

   try:
      response = requests.request("GET", url, headers=headers, data=payload)
      resp = response.json()['data']['dynamic_cards']
      for out in resp:
         desp = json.loads(out['card'])['item']['description']
         NO = re.search(r"NO\.\d{6}", desp).group(0)
         if out['desc']['uid'] != blacklist and NO.find(target) != -1:
            print(f"UID:{out['desc']['uid']},{out['display']['attach_card']['title']},{NO},{datetime.datetime.fromtimestamp(out['desc']['timestamp'])}")
            result.append(f"UID:{out['desc']['uid']},{out['display']['attach_card']['title']},{NO},{datetime.datetime.fromtimestamp(out['desc']['timestamp'])}")
            with open(f'动态结果/{key}_{target}.txt', 'a', encoding='gbk') as f:
                f.write(f"UID:{out['desc']['uid']},{out['display']['attach_card']['title']},{NO},{datetime.datetime.fromtimestamp(out['desc']['timestamp'])}\n")
   except:
      continue
   print("page:"+str(num))
   sleep(0.5)
print("\n".join(result))