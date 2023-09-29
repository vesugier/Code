import requests
from PIL import Image
from io import BytesIO
import threading

def download_image(url):
    try:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        print("图片下载失败：", str(e))
        return None

def compress_and_save_image(image, output_path, quality):
    try:
        image.save(output_path, optimize=True, quality=quality)
    except Exception as e:
        print("图片保存失败：", str(e))

def get_nft_list(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        nft_list = data['data']['nft_list']
        total = data['data']['total']
        return nft_list, total
    except Exception as e:
        print("获取NFT列表失败：", str(e))
        return [], 0

def optimize_images(url, page_num):
    nft_list, total = get_nft_list(url.format(page_num))
    count = 0
    for item in nft_list:
        count += 1
        print(f"正在下载第{page_num}页第{count}/100张图片...")
        image = download_image(item['image'])
        if image:
            quality = 20
            output_path = f"{item['item_name']}/{item['token_id']}.png"
            compress_and_save_image(image, output_path, quality)

def main():
    url = "https://baselabs.bilibili.com/x/gallery/nft/collect/list?item_id=1739&pn={}&ps=100"
    total_pages = 0
    try:
        response = requests.get(url.format(1))
        response.raise_for_status()
        data = response.json()
        total_pages = data['data']['total'] // 100 + 1
    except Exception as e:
        print("获取总页数失败：", str(e))
        return

    threads = []
    for page_num in range(1, total_pages + 1):
        print(f"正在处理第{page_num}/{total_pages}页...")
        thread = threading.Thread(target=optimize_images, args=(url, page_num))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()