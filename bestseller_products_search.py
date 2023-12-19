import requests
from bs4 import BeautifulSoup
import random

def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        # 可以继续添加更多的User-Agent字符串
    ]
    return random.choice(user_agents)

def extract_asin_from_link(link):
    if '/dp/' in link:
        return link.split('/dp/')[1].split('/')[0]
    elif '/product/' in link:
        return link.split('/product/')[1].split('/')[0]
    return "ASIN不可用"

def scrape_bestseller_products(region, category_url):
    headers = {"User-Agent": random_user_agent()}
    response = requests.get(category_url, headers=headers)
    if response.status_code != 200:
        print(f"Error accessing URL: {category_url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    product_items = soup.select('div#gridItemRoot')
    for item in product_items:
        rank = item.select_one('.zg-bdg-text').get_text(strip=True) if item.select_one('.zg-bdg-text') else 'N/A'
        image = item.select_one('img')['src'] if item.select_one('img') else 'N/A'
        title = item.select_one('a.a-link-normal > span').get_text(strip=True) if item.select_one('a.a-link-normal > span') else 'N/A'
        rating = item.select_one('i.a-icon-star-small > span.a-icon-alt').get_text(strip=True) if item.select_one('i.a-icon-star-small > span.a-icon-alt') else 'N/A'
        reviews = item.select_one('a.a-link-normal > span.a-size-small').get_text(strip=True) if item.select_one('a.a-link-normal > span.a-size-small') else 'N/A'
        price = item.select_one('span._cDEzb_p13n-sc-price_3mJ9Z').get_text(strip=True) if item.select_one('span._cDEzb_p13n-sc-price_3mJ9Z') else 'N/A'
        
        # 提取产品链接
        link_element = item.select_one('a.a-link-normal')
        link = f"https://www.amazon.{region}{link_element['href']}" if link_element else 'N/A'

        # 提取ASIN
        asin = extract_asin_from_link(link)

        products.append({
            'rank': rank,
            'image': image,
            'title': title,
            'rating': rating,
            'reviews': reviews,
            'price': price,
            'link': link,
            'asin': asin
        })

    return products

if __name__ == "__main__":
    region = 'it'
    category_url = "https://www.amazon.it/gp/bestsellers/grocery/ref=zg_bs_unv_grocery_1_6377950031_1"  # 输入的URL

    print(f"Scraping products from: {category_url}")
    products = scrape_bestseller_products(region, category_url)
    for product in products:
        print(product)
