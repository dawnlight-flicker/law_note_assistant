# data_manager.py
import json
import os
import sys

import law_api
from online_fetcher import OnlineFetcher


class DataManager:
    def __init__(self, json_path="data.json"):
        # 处理打包后的路径
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        self.json_path = os.path.join(base_path, json_path)
        self.local_data = self._load_local()
        self.fetcher = OnlineFetcher()

    def _load_local(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def search(self, keyword, law_name=None):
        """
        返回 (results, source)
        results: list of law dict
        source: 'local' 或 'online' 或 None
        """
        # 1. 本地查找
        local_results = []
        for item in self.local_data:
            if law_name and item.get('law_name') != law_name:
                continue
            if keyword in item.get('article_number', ''):
                local_results.append(item)
        if local_results:
            return local_results, 'local'


        else:
            # 本地没有，尝试在线API
            print("本地无结果，尝试调用在线API...")
            online_result = law_api.search_law_via_api_sdk(keyword, law_name)
            if online_result:
                return [online_result], 'online'  # 返回API结果
            else:
                return [], None  # API也失败了
        return results, 'local'

    def add_to_local(self, law_dict):
        """将用户确认过的数据加入本地库（可选功能）"""
        self.local_data.append(law_dict)
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(self.local_data, f, ensure_ascii=False, indent=2)