import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlparse, parse_qs

# 生成随机User-Agent
def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        # 添加更多的User-Agent字符串
    ]
    return random.choice(user_agents)

# 使用requests.Session
session = requests.Session()

def search_amazon_products_by_keyword(keyword, region='it'):
    print("开始搜索亚马逊产品...")
    base_url = f"https://www.amazon.{region}/s"
    
    all_products = []

    for page in range(1, 5):
        # 增加随机延迟
        time.sleep(random.uniform(2, 5))
        headers = {"User-Agent": random_user_agent()}
        params = {"k": keyword, "page": page}
        request_url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        print(f"正在请求: {request_url}")

        try:
            response = session.get(request_url, headers=headers)
            print(f"请求页面 {page}，状态码: {response.status_code}")

            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            all_products.extend(extract_product_info(soup, region))
        except requests.RequestException as e:
            print(f"请求过程中出现异常: {e}")

    return all_products
    





def extract_product_info(soup, region):
    products = []
    results = soup.findAll("div", {"data-component-type": "s-search-result"})
    
    if not results:
        print("未找到搜索结果元素。检查页面内容和选择器。")

    for item in results:
        title_element = item.find("span", {"class": "a-size-base-plus a-color-base a-text-normal"})
        title = title_element.text.strip() if title_element else "标题不可用"

        url_element = item.find("a", {"class": "a-link-normal"})
        url = f"https://www.amazon.{region}" + url_element['href'] if url_element else "URL不可用"
        asin = extract_asin_from_url(url)

        price = extract_price(item)
        rating = extract_rating(item)
        products.append({"title": title, "url": url, "price": price, "rating": rating, "asin": asin})

    return products

def extract_asin_from_url(url):
    if '/dp/' in url:
        return url.split('/dp/')[1].split('/')[0]
    elif 'url=' in url:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'url' in query_params:
            inner_url = query_params['url'][0]
            if '/dp/' in inner_url:
                return inner_url.split('/dp/')[1].split('/')[0]
            elif '/%2Fdp%2F' in inner_url:
                return inner_url.split('/%2Fdp%2F')[1].split('%2F')[0]
    return "ASIN不可用"

def extract_price(item):
    price_span = item.find("span", class_="a-offscreen")
    return price_span.get_text().strip() if price_span else "价格不可用"

def extract_rating(item):
    rating_span = item.find("span", class_="a-icon-alt")
    return rating_span.get_text().strip() if rating_span else "评分不可用"

# 示例关键词查询
if __name__ == '__main__':
    keyword = "iphone"  # 示例关键词
    region = 'it'  # 示例地区代码
    products = search_amazon_products_by_keyword(keyword, region)
    print(f"找到 {len(products)} 个产品")
    for product in products:
        print(product)
