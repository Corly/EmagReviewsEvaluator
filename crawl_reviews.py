import requests
import json
import time

def get_reviews_from_page(url, offset):
    headers = {
        'authority': 'www.emag.ro',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,ro-RO;q=0.8,ro;q=0.7',
        'referer': "https://www.emag.ro/" + url,
        'sec-ch-device-memory': '8',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="111.0.5563.65", "Not(A:Brand";v="8.0.0.0", "Chromium";v="111.0.5563.65"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        'x-request-source': 'www',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'source_id': '7',
        'page[limit]': '10',
        'page[offset]': str(offset),
        'sort[created]': 'desc',
    }

    response = requests.get(
        "https://www.emag.ro/product-feedback/" + url + "reviews/list",
        params=params,
        headers=headers,
    )

    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def get_all_the_reviews(url):
    offset = 0
    reviews = []
    while True:
        time.sleep(60)
        print(f"Dowloading reviews from offset {offset}...")
        json_response = get_reviews_from_page(url, offset)
        if not json_response:
            break
        else:
            reviews += json_response["reviews"]["items"]
            if len(json_response["reviews"]["items"]) < 10:
                break
            else:
                offset += 10
    return reviews


def get_all_reviews_and_save_them_to_file(url, file_name):
    reviews = get_all_the_reviews(url)
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(reviews, file, indent=4, ensure_ascii=False)
    

if __name__ == "__main__":
    get_all_reviews_and_save_them_to_file('laptop-gaming-lenovo-ideapad-3-15ach6-cu-procesor-amd-ryzentm-5-5600h-pana-la-4-20-ghz-15-6-full-hd-ips-8gb-512gb-ssd-nvidia-geforce-gtx-1650-4gb-no-os-shadow-black-82k2007brm/pd/D7YGGPMBM/', 'lenovo_ideapad_3.json')
