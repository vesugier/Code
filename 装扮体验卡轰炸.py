import requests
import json
import os
import re
from time import sleep


def load_setting():
    if os.path.exists('setting.json'):
        with open('setting.json', 'r') as f:
            result = json.load(f)

        # if 'uid' not in result:
        #     uid = input('输入对方uid:\n')
        # else:
        #     uid = result['uid']

        if 'cookie' not in result:
            cookie = input('输入cookie:\n')
        else:
            cookie = result['cookie']
    else:
        # uid = input('输入对方uid:\n')
        cookie = input('输入cookie:\n')

    result = {
        'cookie': cookie
    }
    uid = input('输入对方uid:\n')

    with open('setting.json', 'w') as f:
        json.dump(result, f)

    return uid, cookie


def parse_cookie(cookie):
    SESSDATA = None
    csrf = None
    myuid = None

    for pair in cookie.split(";"):
        # 拆分键值对
        key, value = pair.split("=")
        # 去除空格
        key = key.strip()
        value = value.strip()
        # 判断是否为SESSDATA字段
        if key == "SESSDATA":
            SESSDATA = value
        elif key == "bili_jct":
            csrf = value
        elif key == "DedeUserID":
            myuid = value

    return SESSDATA, csrf, myuid


def get_garbage_list(myuid):
    url = "https://app.bilibili.com/x/v2/space/garb/list?pn={}&ps=150&vmid={}"

    data_list = []
    for i in range(30):
        response = requests.request("GET", url.format(i + 1, myuid)).json()['data']
        if response['count'] != 0:
            for item in response['list']:
                data_list.append(item)
        else:
            break
    outlist = []
    for data in data_list:
        garb_title = data["garb_title"]
        url = data["button"]["uri"]
        match = re.search(r'id=(\d+)', url).group(1)

        outlist.append({garb_title: match})

    return outlist


def fuzzy_search(keyword, data):
    results = []
    pattern = re.compile(keyword, re.IGNORECASE)
    for item in data:
        for key in item:
            if pattern.search(key):
                results.append(item)
                break
    return results


def main():
    uid, cookie = load_setting()
    url = "https://api.bilibili.com/x/web-interface/card?mid=" + uid
    response = requests.request("GET", url).json()['data']['card']['name']
    print(f"对方昵称:{response}")
    SESSDATA, csrf, myuid = parse_cookie(cookie)
    data_list1 = get_garbage_list(myuid)
    data_list2 = get_garbage_list(uid)
    data_list = [item for item in data_list1 if item not in data_list2]
    print(data_list)

    with open('save.json', 'w') as f:
        json.dump(data_list, f)

    keyword = input("请输入关键词：\n")

    if keyword == "":
        print(data_list)
    # results = fuzzy_search(keyword, data_list)
    # print(results)

    suit_ids = []
    for char in keyword:
        found = False
        for item in data_list:
            for key, value in item.items():
                if char == key[0]:
                    suit_ids.append(value)
                    found = True
                    break
            if found:
                break
    print(suit_ids)

    # suit_id = input("请输入装扮id：\n")

    url1 = "https://api.bilibili.com/x/garb/user/trial/present"
    url2 = "https://api.bilibili.com/x/garb/user/trial/share/cancel"

    headers = {
        'Host': 'api.bilibili.com',
        'cookie': 'SESSDATA=' + SESSDATA,
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    n = int(input("请输入循环次数："))
    for i in range(n):
        for suit_id in suit_ids:
            text1 = f'suit_id={suit_id}&to_mid={uid}&csrf={csrf}'
            response = requests.request("POST", url1, headers=headers, data=text1).json()

            if response["data"]["share_token"]:
                print("赠送成功")
            sleep(0.2)

            share_token = response["data"]["share_token"]
            text2 = f'share_token={share_token}&csrf={csrf}'
            requests.request("POST", url2, headers=headers, data=text2)
            # sleep(0.6)


if __name__ == "__main__":
    main()
