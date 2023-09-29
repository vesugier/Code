import requests
import json
import time
import datetime
import os

import multiprocessing
import threading
import concurrent.futures
import asyncio

act_id = 4
pool = 2 #指定上下池,1为上2为下 与抽卡pool无关
target_time = 1695366000 #预计开始时间

headers = {
    'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
}

signature = 0
bcoin = 0


def select_file():
    folder_path = 'cookie'
    files = [os.path.splitext(file)[0] for file in os.listdir(folder_path)]
    print("可选择的cookie:")
    for i, file in enumerate(files):
        name = requests.get(f'https://api.vc.bilibili.com/account/v1/user/cards?uids={file}').json()['data'][0][
            'name']
        print(f"{i + 1}. {file} - {name}")

    file_index = int(input("请选择文件编号: \n")) - 1
    selected_file = os.listdir(folder_path)[file_index]
    file_path = os.path.join(folder_path, selected_file)

    return file_path


def get_cookie(filepath):
    global accesskey, SESSDATA, appkey, bili_jct, params
    with open(filepath, 'r') as file:
        cookie = json.loads(file.read())

        accesskey = cookie['accessKey']
        if 'appkey' in cookie:
            appkey = cookie['appkey']
        else:
            appkey = '1d8b6e7d45233436'
        for pair in cookie['cookie'].split(";"):
            key, value = pair.strip().split("=")
            if key == "SESSDATA":
                SESSDATA = value
            if key == "bili_jct":
                bili_jct = value
        params = {
            'access_key': accesskey,
            'appkey': appkey,
            'act_id': act_id
        }


def check():
    global bcoin
    cookies = {
        'SESSDATA': SESSDATA,
    }
    response = requests.get(f'https://api.bilibili.com/x/garb/user/wallet', cookies=cookies, headers=headers).json()
    if response['code'] != 0:
        print('cookie有问题,退出')
        exit()
    else:
        bcoin = response['data']['bcoin_balance']
        print('B币余额：', bcoin)


def getinfo():
    try:
        response = requests.get(f'https://api.bilibili.com/x/vas/uni_lottery_act/pool_data', params=params).json()['data']['list']
        item = response[pool - 1]
        time = item['start_time']
        button = 1 #0为单抽 1为五连
        id = item['button'][button]['product_id']
        pool_id = item['pool_id']
        if item['button'][button]['special_lottery_price'] != 0:
            price = item['button'][button]['special_lottery_price']
            discount = item['button'][button]['discount_rights_tid']
        else:
            price = item['button'][button]['lottery_price']
            discount = item['button'][button]['discount_rights_tid']
    except:
        return None
    return pool_id, time, id, price, discount


def nowtime():
    bilitime = requests.get('https://api.bilibili.com/x/report/click/now').json()['data']['now']
    # print(bilitime)
    # print(time.time())
    return bilitime


def buy(pool_id, goods_id, price, discount):
    global signature
    extra = {"activity_id": act_id, "pool_id": pool_id, "discount_rights_tid": discount}
    price = price * 1000

    data = {
        'access_key': accesskey,
        'biz_extra': json.dumps(extra, ensure_ascii=False),
        'context_id': act_id,
        'context_type': '51',
        'goods_id': goods_id,
        'goods_num': '5',
        'pay_bp': price,
        'platform': 'android',
    }
    response = requests.post('https://api.live.bilibili.com/xlive/revenue/v1/order/createOrder', headers=headers,
                             data=data)
    print(response.text)
    if response.json()['code'] == 0 or response.json()['code'] == 20005:
        signature = 1


def draw(pool_id):
    if signature == 0:
        time.sleep(0.35)
    data = {
        'access_key': accesskey,
        'appkey': appkey,
        'act_id': act_id,
        'lottery_num': 5,
        'platform': 'android',
        'mobi_app': 'android',
        'pool_id': pool_id,
    }

    response = requests.post('https://api.bilibili.com/x/vas/uni_lottery_act/draw_lottery', headers=headers, data=data)
    print(response.text)


def reward(pool_id):
    params1 = params
    params1['relate_id'] = pool_id
    response = requests.get("https://api.bilibili.com/x/vas/uni_lottery_act/accumulative_data", headers=headers, params=params1).json()['data']
    params1['accumulative_id'] = response['accumulative_id']
    own_num = response['user_own_num']
    if own_num < 5:
        return
    for item in response['list']:
        print(item)
        if item['status'] != 0:
            params1['task_id'] = item['task_id']
            response = requests.get("https://api.bilibili.com/x/vas/uni_lottery_act/accumulative_receive", headers=headers, params=params1).json()['data']
            print(response)


def exchange():
    if signature == 0:
        time.sleep(0.35)

    response = requests.get('https://api.bilibili.com/x/vas/uni_lottery_act/exchange_data', headers=headers, params=params).json()['data']['own_reward_list']
    # print(response)
    for item in response:
        print(item['reward_name'], item['own_reward_num'])
        if item['own_reward_num'] == 0:
            return

    data = {
        'access_key': accesskey,
        'appkey': appkey,
        'act_id': act_id,
        'platform': 'android',
        'mobi_app': 'android'
    }
    response = requests.post('https://api.bilibili.com/x/vas/uni_lottery_act/exchange', headers=headers, data=data).json()
    print(response)


def redeem():# 三合一
    kuji_id = 23
    url = f"https://api.bilibili.com/x/garb/kuji/v4/user/box/list?access_key={accesskey}&appkey={appkey}&kuji_act_id={kuji_id}&state=0"
    response = requests.get(url).json()['data']['list']
    lists = []
    for items in response:
        if items['level'] >= 300:
            for item in items['list']:
                lists.append(item)
    touple = []
    for i in lists:
        touple.append(f'{i["id"]}')

    data = {
        'access_key': accesskey,
        'appkey': appkey,
        'kuji_act_id': kuji_id,
        'reward_ids': ",".join(touple[:3])
    }
    response = requests.post("https://api.bilibili.com/x/garb/kuji/v4/user/reward/compose", data=data)
    print(response.text)


def check_wallet(diff):
    while True:
        cookies = {
            'SESSDATA': SESSDATA,
        }
        coin = requests.get(f'https://api.bilibili.com/x/garb/user/wallet', cookies=cookies, headers=headers).json()['data']['bcoin_balance']
        if bcoin - coin >= diff:
            os._exit(0)
        else:
            time.sleep(0.5)


def main():
    ltime = 0
    filepath = select_file()
    get_cookie(filepath)
    check()
    diff = int(input("输入消耗多少钱后停止：\n"))
    if diff != 0:
        check_thread = threading.Thread(target=check_wallet, args=(diff,))
        check_thread.start()
    while True:
        result = getinfo()
        if result is not None:
            break
        print('等待信息中', datetime.datetime.now().strftime('%H:%M:%S'))

        if time.time() + 2 < target_time:
            time.sleep(1)
        else:
            time.sleep(0.1)
    print(result)
    pool_id, start_time, goods_id, price, discount = result

    while True:
        ntime = nowtime()
        if start_time <= ntime <= start_time + 3:
            if signature and ntime-ltime >= 1:
                pool_id, start_time, goods_id, price = getinfo()
                ltime = ntime
            buy_thread = threading.Thread(target=buy, args=(pool_id, goods_id, price, discount,))
            draw_thread = threading.Thread(target=draw, args=(pool_id,))
            reward_thread = threading.Thread(target=reward, args=(pool_id,))
            exchange_thread = threading.Thread(target=exchange)
            redeem_thread = threading.Thread(target=redeem)

            buy_thread.start()
            draw_thread.start()
            reward_thread.start()
            exchange_thread.start()
            redeem_thread.start()

        # print(time.time())

        diff_time = start_time - ntime
        if diff_time > 5:
            time.sleep(1)
            print('距离开始：', datetime.timedelta(seconds=diff_time))
            # print(datetime.datetime.now().strftime('%H:%M:%S'), '等待中')
        elif diff_time <= -3:
            print('已结束，自动退出')
            break


if __name__ == '__main__':
    main()
