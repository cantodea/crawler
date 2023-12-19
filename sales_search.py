import requests

def estimate_sales(rank, category, store):
    url = f"https://d2ogs1k0ty8acr.cloudfront.net/sales?rank={rank}&category={category}&store={store}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,it;q=0.8,en-US;q=0.7,en;q=0.6",
        "Origin": "https://www.junglescout.cn",
        "Referer": "https://www.junglescout.cn/",
        "Sec-Ch-Ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", {})
    else:
        return "请求失败，状态码：" + str(response.status_code)

# 示例调用
rank = 1212
category = "Baby"
store = "us"
sales_estimate = estimate_sales(rank, category, store)
print(sales_estimate)
