import requests
import os
from parsel import Selector

class PoetryCrawler:
    def __init__(self):
        self.url = "https://www.gushiwen.cn/"
        # 完善请求头，模拟真实浏览器，绕过基础反爬
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Referer": "https://www.gushiwen.cn/",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        self.save_path = os.path.join(os.path.dirname(__file__), "古诗文.txt")

    def get_html(self, target_url=None):
        target_url = target_url if target_url else self.url
        try:
            resp = requests.get(target_url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            # 自动识别页面编码，不再强制utf-8
            resp.encoding = resp.apparent_encoding
            # 调试：打印页面前500字符，确认是否拿到完整网页
            print("页面返回片段：", resp.text[:500])
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[✗] 请求失败 {target_url}: {e}")
            return None

    def parse_data(self, html):
        sel = Selector(html)
        # 放宽选择器，全局匹配所有诗文卡片
        items = sel.css("div.sons")
        print(f"本次匹配到卡片数量：{len(items)}")
        result = []
        for item in items:
            # 标题兼容两种标签结构
            title = item.css("div.cont p a b::text").get()
            if not title:
                title = item.css("div.cont p a::text").get()
            if not title:
                continue
            title = title.strip()

            # 作者、朝代提取
            source_text = item.css("p.source").get()
            author = "佚名"
            if source_text:
                author_all = item.css("p.source a::text").getall()
                if author_all:
                    author = " ".join([i.strip() for i in author_all])

            # 正文清洗、保留换行
            text_list = item.css("div.contson ::text").getall()
            clean_text = []
            for t in text_list:
                t_clean = t.strip()
                if t_clean:
                    clean_text.append(t_clean)
            content = "\n".join(clean_text) if clean_text else "无正文"

            result.append({
                "title": title,
                "author": author,
                "content": content
            })
        return result

    def save_to_file(self, data, append=False):
        mode = "a" if append else "w"
        with open(self.save_path, mode=mode, encoding="utf-8") as f:
            for poem in data:
                f.write(f"标题：{poem['title']}\n")
                f.write(f"作者：{poem['author']}\n")
                f.write(f"正文：\n{poem['content']}\n")
                f.write("-" * 40 + "\n")

    def run(self):
        html = self.get_html()
        if not html:
            print("[✗] 未获取到页面内容，爬取终止")
            return
        poem_data = self.parse_data(html)
        if len(poem_data) == 0:
            print("[✗] 未解析到任何诗文数据，请检查网站结构或网络")
            return
        self.save_to_file(poem_data)
        print(f"✅ 采集完毕，本次共获取{len(poem_data)}首诗文，保存路径：{self.save_path}")
