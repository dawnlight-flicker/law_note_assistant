# online_fetcher.py
import requests
from bs4 import BeautifulSoup
import re


class OnlineFetcher:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch(self, keyword, law_name=None):
        """抓取元典智库搜索结果（示例）"""
        # 构造搜索URL（以元典智库为例）
        print(f"尝试抓取: {keyword}")
        search_url = f"https://www.yuandianzk.com/search?q={keyword}"
        try:
            resp = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            print(f"状态码: {resp.status_code}")
            if resp.status_code != 200:
                return None
            # 打印前500字符，看返回了什么
            print(resp.text[:500])
            resp = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, 'html.parser')
            # 解析：找到第一条结果的链接和内容（具体选择器需要根据网站调整）
            first_result = soup.select_one('.result-item a')  # 假设类名
            if not first_result:
                return None
            detail_url = first_result.get('href')
            if not detail_url.startswith('http'):
                detail_url = 'https://www.yuandianzk.com' + detail_url

            # 进入详情页
            detail_resp = requests.get(detail_url, headers=self.headers, timeout=self.timeout)
            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
            # 假设正文在 .law-content 中
            content_div = detail_soup.select_one('.law-content')
            if not content_div:
                return None
            article_text = content_div.get_text(strip=True)
            # 提取法条编号（从页面标题或URL）
            number_match = re.search(r'第(\d+)条', article_text)
            article_number = number_match.group(0) if number_match else keyword

            return {
                "id": -1,
                "law_name": law_name or "民法典",
                "article_number": article_number,
                "article_text": article_text,
                "judicial_interpretations": [],
                "exam_points": [],
                "source": "元典智库（实时抓取）"
            }
        except Exception as e:
            print(f"抓取失败: {e}")
            return None