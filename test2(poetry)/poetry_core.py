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
        # 实际DOM结构: div.sons > div.cont > div.yizhu(注音/赏析)
        #                            > div#zhengwen > p > a > b(标题)
        #                                          > p.source > a(作者) a(朝代)
        #                                          > div.contson(正文, 可能含<p>标签)
        items = sel.css("div.sons")
        result = []
        for item in items:
            # 只处理含有 div.yizhu 的诗词条目（过滤名句、常识等非诗词内容）
            if not item.css("div.cont div.yizhu"):
                continue

            # 提取标题
            title = item.css(".cont p a b::text").get()
            if not title:
                title = item.css(".cont p:first-child a::text").get()
            if not title:
                continue

            # 提取作者：获取 p.source 下第一个 <a> 的所有文本（处理含<img>的情况）
            first_author_a = item.css("p.source a:nth-child(1)")
            if first_author_a:
                author_texts = first_author_a.css("::text").getall()
                author = "".join(a.strip() for a in author_texts if a.strip())
            else:
                author = ""

            # 提取正文：使用 *::text 获取所有后代文本节点（处理<p>嵌套的情况）
            content_parts = item.css("div.contson *::text").getall()
            if not content_parts:
                # 兜底：直接文本节点
                content_parts = item.css("div.contson::text").getall()
            content = "".join(c.strip() for c in content_parts if c.strip())

            result.append({
                "title": title.strip(),
                "author": author if author else "佚名",
                "content": content if content else ""
            })
        return result

    def save_to_file(self, data):
        with open(self.save_path, "w", encoding="utf-8") as f:
            for poem in data:
                f.write(f"标题：{poem['title']}\n")
                f.write(f"作者：{poem['author']}\n")
                f.write(f"正文：{poem['content']}\n")
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


