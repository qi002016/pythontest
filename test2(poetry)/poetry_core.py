import requests
import os
from parsel import Selector

class PoetryCrawler:
    def __init__(self):
        self.url = "https://www.gushiwen.cn/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # 保存到脚本所在目录
        self.save_path = os.path.join(os.path.dirname(__file__), "古诗文.txt")

    def get_html(self):
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[✗] 请求失败: {e}")
            return None

    def parse_data(self, html):
        sel = Selector(html)
        # 实际DOM结构: div.sons > div.cont > p > a > b(标题)
        #                                    p.source > a(作者) a(朝代)
        #                                    div.contson(正文)
        items = sel.css("div.sons")
        result = []
        for item in items:
            title = item.css(".cont p a b::text").get()
            if not title:
                title = item.css(".cont p:first-child a::text").get()
            author = item.css("p.source a:first-of-type::text").get()
            # 提取纯文本正文，过滤掉 <br> 带来的多余空白
            content_parts = item.css("div.contson::text").getall()
            content = "".join(c.strip() for c in content_parts if c.strip())
            if not title:
                continue
            result.append({
                "title": title.strip(),
                "author": author.strip() if author else "佚名",
                "content": content if content else ""
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
        self.save_to_file(poem_data)
        print(f"采集完毕，共{len(poem_data)}首诗词")


# 程序入口
if __name__ == "__main__":
    crawler = PoetryCrawler()
    crawler.run()


