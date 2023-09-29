import requests
import json
import time
import datetime
import os
import sys


import multiprocessing
import threading
import concurrent.futures
import asyncio

headers = {
    'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
}

Pay = 0

def select_file():
    folder_path = 'cookie'
    files = [os.path.splitext(file)[0] for file in os.listdir(folder_path)]
    print("可选择的cookie:")
    for i, file in enumerate(files):
        name = requests.get(f'https://api.vc.bilibili.com/account/v1/user/cards?uids={file}').json()['data'][0][
        'name']
        print(f"{i+1}. {file} - {name}")

    file_index = int(input("请选择文件编号: \n")) - 1
    selected_file = os.listdir(folder_path)[file_index]
    file_path = os.path.join(folder_path, selected_file)

    return file_path


def get_cookie(filepath):
    global accesskey, SESSDATA, appkey
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


def check():
    cookies = {
        'SESSDATA': SESSDATA,
    }
    response = requests.get(f'https://api.bilibili.com/x/garb/user/wallet', cookies=cookies, headers=headers).json()
    if response['code'] != 0:
        print('cookie有问题,退出')
        exit()
    else:
        print('B币余额：', response['data']['bcoin_balance'])


def getlist():
    lists = {}
    response = requests.get('https://api.bilibili.com/x/garb/card/subject/list?subject_id=42').json()['data'][
        'subject_card_list']
    for item in response:
        # print(item['act_name'], item['act_id'], item['lottery_id'])
        lists[item['act_id']] = [item['act_name'], item['lottery_id']]
    return lists


def info(actid):
    try:
        cookies = {
            'SESSDATA': SESSDATA,
        }
        response = requests.get(f'https://api.bilibili.com/x/vas/dlc_act/act/basic?act_id={actid}', cookies=cookies,
                                headers=headers).json()['data']
        for item in response['lottery_list']:
            if item['start_time'] > response['cur_time']:
                name = "{} {}".format(response['act_title'], item['lottery_name'])
                price = item['discount']['price'] if item['discount'] else item['price']
                return name, actid, item['lottery_id'], item['goods_id'], price, item['start_time']
    except:
        return None


def infos(actid):
    try:
        result = []
        cookies = {
            'SESSDATA': SESSDATA,
        }
        response = requests.get(f'https://api.bilibili.com/x/vas/dlc_act/act/basic?act_id={actid}', cookies=cookies,
                                headers=headers).json()['data']
        for item in response['lottery_list']:
            name = "{} {}".format(response['act_title'], item['lottery_name'])
            price = item['discount']['price'] if item['discount'] else item['price']
            result.append((name, actid, item['lottery_id'], item['goods_id'], price, item['start_time']))
        return result
    except:
        return None


def buy(actid, lotteryid, goodid, price, buy_num=1):
    global Pay
    if Pay:
        return
    extra = {'activity_id': actid, 'lottery_id': lotteryid}

    data = {
        'access_key': accesskey,
        'biz_extra': json.dumps(extra, ensure_ascii=False),
        'context_id': '0',
        'context_type': '103',
        'goods_id': goodid,
        'goods_num': buy_num,
        'pay_bp': price,
        'platform': 'android',
    }
    response = requests.post('https://api.live.bilibili.com/xlive/revenue/v1/order/createOrder', headers=headers,
                             data=data).json()
    if response['code'] == 0:
        Pay = 1
    sys.stdout = open('output.txt', 'a+')
    response = json.dumps(response, ensure_ascii=False)
    print("时间", time.time())
    print(response)
    #print(response['data']['item_list'])
    sys.stdout = sys.__stdout__


def draw(actid, lotteryid, lottery_num=1):
    if Pay != 1:
        time.sleep(0.35)
    # if lottery_num == 0:
    #     return
    data = {
        'access_key': accesskey,
        'act_id': actid,
        'lottery_id': lotteryid,
        'appkey': appkey,
        'lottery_num': lottery_num,
        'platform': 'android',
    }

    response = requests.post('https://api.bilibili.com/x/vas/dlc_act/lottery/draw_item', headers=headers, data=data).json()
    sys.stdout = open('output.txt', 'a+')
    response = json.dumps(response, ensure_ascii=False)
    print(response)
    #print(response['data']['item_list'])
    sys.stdout = sys.__stdout__


def nowtime():
    bilitime = requests.get('https://api.bilibili.com/x/report/click/now').json()['data']['now']
    # print(bilitime)
    # print(time.time())
    return bilitime


def choose(lists):
    results = []
    for index, key in enumerate(lists):
        result = info(key)
        if index >= 8:
            break
        if result is None:
            continue
        results.append(result)
    if len(results) == 0:
        print('当前无合适数藏集')
        exit()
    elif len(results) == 1:
        print(results[0][0])
        return results[0]
    elif len(results) > 1:
        print('当前有多个合适数藏集')
        for i, result in enumerate(results):
            print(f"{i + 1}. {result[0]}")
        index = int(input("请选择藏集编号: \n")) - 1

        return results[index]


def chooses(lists):
    results = []
    for key in lists:
        result = infos(key)
        for item in result:
            results.append(item)

    for i, result in enumerate(results):
        print(f"{i + 1}. {result[0]}")
    index = int(input("请选择藏集编号: \n")) - 1

    return results[index]


def card_result():
    cookies = {
            'SESSDATA': SESSDATA,
    }
    response = requests.get('https://api.bilibili.com/x/garb/user/asset/list?part=card_bg&pn=1&ps=3', cookies=cookies).json()['data']['list']
    for item in response:
        print(f"{item['item']['name']}, NO.{item['card_bg']['bg_no']}(LV.{item['card_bg']['level']})")


def rub_card(result):
    global Pay
    actid, lotteryid, goodid, pay_bp, start_time = result
    buy_num = int(input("输入抽取次数：\n"))
    if buy_num < 10:
        draw_num = 1
    else:
        draw_num = 10
    price = buy_num*9900 - (9900-pay_bp)

    if start_time - nowtime() < 0:
        buy(actid, lotteryid, goodid, price, buy_num)
        draw(actid, lotteryid, draw_num)
        draw(actid, lotteryid, draw_num)
        draw(actid, lotteryid, draw_num)
        exit()

    delay = float(input("输入延时时间：\n"))

    # start_time = nowtime() + 5
    # Pay = 1

    while True:
        diff_time = start_time - nowtime()
        if diff_time > 2:
            time.sleep(1)
            print('距离开始：', datetime.timedelta(seconds=diff_time))
            continue
            # print(datetime.datetime.now().strftime('%H:%M:%S'), '等待中')
        elif diff_time <= -3:
            print('已结束，自动退出')
            break

        if -1 <= start_time - nowtime() <= 2:
            # time.sleep(delay)
            thread_buy = threading.Thread(target=buy, args=(actid, lotteryid, goodid, price, buy_num))
            thread_draw = threading.Thread(target=draw, args=(actid, lotteryid, draw_num))
            thread_buy.start()
            thread_draw.start()


def main():
    filepath = select_file()
    get_cookie(filepath)
    check()

    lists = getlist()

    choice = int(input("请选择：\n1. 抢前排  2. 选目标  其他. 指定收藏集 \n"))

    if choice == 1:
        result = choose(lists)
    elif choice == 2:
        result = chooses(lists)
    elif choice >= 3:
        results = infos(choice)
        if len(results) != 1:
            for i, result in enumerate(results):
                print(f"{i + 1}. {result[0]}")
            index = int(input("请选择藏集编号: \n")) - 1
            result = results[index]
        else:
            result = results[0]
        print(f'已指定ID为: {choice},名字为 {result[0]} 的收藏集')

    else:
        print("无效的选择")
        
    sys.stdout = open('output.txt', 'a+')
    names = ('名字', '数藏集ID', '抽奖ID', '货品ID', '价格', '开始时间')
    print('\n——信息——')
    for name, value in zip(names, result):
        print(f'{name}: {value}')
    print('——信息——\n')
    sys.stdout = sys.__stdout__
    
    result = result[1:]
    
    print(result)

    rub_card(result)
    card_result()





if __name__ == '__main__':
    main()
