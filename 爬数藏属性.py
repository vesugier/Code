import csv
import requests
import threading
import time


def get_total_pages(url):
    try:
        response = requests.get(url.format(1))
        response.raise_for_status()
        data = response.json()
        total_pages = data['data']['total'] // 100 + 1
        return total_pages
    except Exception as e:
        print("获取总页数失败：", str(e))
        return 0


def process_page(url, page_num, csv_writer):
    try:
        response = requests.get(url.format(page_num))
        response.raise_for_status()
        data = response.json()
        if 'data' in data and 'nft_list' in data['data']:
            nft_list = data['data']['nft_list']
            for nft in nft_list:
                response = requests.get(f"https://baselabs.bilibili.com/x/gallery/nft_detail?id={nft['nft_id']}")
                data = response.json()
                if 'data' in data and 'attributes' in data['data']:
                    attributes = data['data']['attributes']
                    attribute_values = [attribute['value'] for attribute in attributes]
                    attribute_values.insert(0, data['data']['serial_number'])
                    attribute_values.insert(1, data['data']['owner']['mid'])
                    csv_writer.writerow(attribute_values)
                else:
                    print(f"处理第{page_num}页失败：页面数据格式不匹配")
                time.sleep(0.1)
        else:
            print(f"处理第{page_num}页失败：页面数据格式不匹配")
    except Exception as e:
        print(f"处理第{page_num}页失败：", str(e))


def main():
    url = "https://baselabs.bilibili.com/x/gallery/nft/collect/list?item_id=1757&pn={}&ps=100"
    total_pages = get_total_pages(url)
    if total_pages == 0:
        return

    with open("nft_data.csv", "w", newline="", encoding="utf-8") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['编号', 'UID', '背景', '素体', '五官', '外观1', '外观2', '装饰', '道具'])

        threads = []
        for page_num in range(1, total_pages + 1):
            print(f"正在处理第{page_num}/{total_pages}页...")
            thread = threading.Thread(target=process_page, args=(url, page_num, csv_writer))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    main()
