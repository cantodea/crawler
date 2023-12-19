import requests
from bs4 import BeautifulSoup

def get_product_info_by_asin(asin, region='it'):
    url = f"https://www.amazon.{region}/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        product_info = extract_product_details(soup, asin)
        return product_info
    else:
        return {"error": "无法获取页面"}

def extract_product_details(soup, asin):
    title = soup.find(id="productTitle").get_text().strip() if soup.find(id="productTitle") else "标题不可用"
    price_span = soup.find("span", class_="aok-offscreen")
    price = price_span.get_text().strip() if price_span else "价格不可用"
    rating = soup.find(class_="a-icon-alt").get_text().strip() if soup.find(class_="a-icon-alt") else "评分不可用"
    brand = soup.find(id="bylineInfo").get_text().strip() if soup.find(id="bylineInfo") else "品牌不可用"
    description = soup.find(id="feature-bullets").get_text().strip() if soup.find(id="feature-bullets") else "描述不可用"
    main_image = soup.find(id="landingImage")['src'] if soup.find(id="landingImage") else "主图链接不可用"
    bullet_points = extract_bullet_points(soup)
    max_stock = extract_stock_info(soup)
    category, rank = extract_category_and_rank(soup)

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "brand": brand,
        "description": description,
        "main_image": main_image,
        "bullet_points": bullet_points,
        "asin": asin,
        "max_stock": max_stock,
        "category": category,
        "rank": rank
    }

def extract_category_and_rank(soup):
    # 定位包含排名信息的 <th> 元素
    rank_header = soup.find("th", text=lambda x: "Posizione nella classifica Bestseller di Amazon" in x if x else False)
    if not rank_header:
        return "分类和排名信息不可用", "分类和排名信息不可用"

    # 获取相邻的 <td> 元素
    rank_data_td = rank_header.find_next_sibling("td")
    if not rank_data_td:
        return "分类和排名信息不可用", "分类和排名信息不可用"

    # 提取分类和排名信息
    rank_texts = rank_data_td.find_all("span")
    if not rank_texts:
        return "分类和排名信息不可用", "分类和排名信息不可用"

    # 假设第一个 <span> 包含所需的排名和分类信息
    rank_info = rank_texts[0].get_text()
    category = None
    rank = None

    # 将信息分割并提取
    if ' in ' in rank_info:
        parts = rank_info.split(' in ')
        rank = parts[0].strip().split(' ')[1]  # 提取排名数字
        category = parts[1].split('(')[0].strip()  # 提取分类

    if not category or not rank:
        return "分类信息不可用", "排名信息不可用"

    return category, rank

def extract_stock_info(soup):
    quantity_select = soup.find(id="quantity")
    if not quantity_select:
        return "库存信息不可用"

    quantity_options = quantity_select.find_all("option")
    quantities = [int(option['value']) for option in quantity_options if option['value'].isdigit()]
    if not quantities:
        return "库存信息不可用"

    max_stock = max(quantities)
    return max_stock

def extract_bullet_points(soup):
    bullet_points = []
    bullets = soup.find_all("span", class_="a-list-item")
    for bullet in bullets:
        text = bullet.get_text().strip()
        if text:
            bullet_points.append(text)
    return bullet_points

# 示例使用
if __name__ == '__main__':
    asin = 'B09T9BHCLM'  # 在这里输入实际的ASIN
    region = 'it'  # 在这里输入实际的区域代码
    product_info = get_product_info_by_asin(asin, region)
    print(product_info)
