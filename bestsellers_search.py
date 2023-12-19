import requests
from bs4 import BeautifulSoup

def scrape_amazon_categories(region, url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to access {url}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    categories = []

    # 选取具有特定类名和角色属性的div元素
    category_group = soup.select_one('div._p13n-zg-nav-tree-all_style_zg-browse-group__88fbz[role="group"]')
    if not category_group:
        print("No category group found")
        return []

    # 选取直接子元素中的链接
    category_elements = category_group.select('div[role="treeitem"] > a')
    for element in category_elements:
        categories.append({
            'name': element.get_text().strip(),
            'url': f"https://www.amazon.{region}{element['href']}"
        })

    return categories

def get_categories(region='it', specific_url=None):
    if not specific_url:
        url = f"https://www.amazon.{region}/gp/bestsellers"
    else:
        url = specific_url
    
    return scrape_amazon_categories(region, url)

# 示例使用
if __name__ == '__main__':
    region = 'it'
    specific_url = 'https://www.amazon.it/gp/bestsellers/grocery/ref=zg_bs_unv_grocery_1_6377950031_1'
    categories = get_categories(region=region, specific_url=specific_url)
    for category in categories:
        print(category)
