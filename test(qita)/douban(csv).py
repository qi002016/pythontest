import requests
import time
import csv
from parsel import Selector


class DoubanTop250Crawler:
    """爬取豆瓣电影 Top 250 保存为本地CSV文件"""

    def __init__(self):
        self.base_url = "https://movie.douban.com/top250"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/126.0.0.0 Safari/537.36"
        }
        # 保存到当前目录下的文件
        self.csv_path = "豆瓣Top250电影数据.csv"
        # 表头
        self.headers_row = ["排名", "片名", "导演", "演员", "年份", "类型", "国家", "评分", "链接"]

    def fetch_page(self, start):
        """获取单页 HTML"""
        params = {"start": start, "filter": ""}
        try:
            resp = requests.get(self.base_url, params=params,
                                headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[✗] 第 {start // 25 + 1} 页请求失败: {e}")
            return None

    def parse_page(self, html):
        """解析页面数据"""
        sel = Selector(text=html)
        items = sel.css('ol.grid_view div.item')
        result = []

        for item in items:
            rank = item.css('div.pic em::text').get('').strip()
            url = item.css('div.pic a::attr(href)').get('')
            title = item.css('div.hd a span.title::text').get('').strip()
            rating = item.css('span.rating_num::text').get('').strip()

            p_texts = item.css('div.bd > p:first-of-type').xpath('.//text()').getall()

            director = ''
            actors = ''
            year = ''
            country = ''
            genre = ''

            if len(p_texts) >= 1:
                line1 = p_texts[0].strip()
                if '主演:' in line1:
                    parts = line1.split('主演:', 1)
                    director = parts[0].replace('导演:', '').strip()
                    actors = parts[1].strip()
                elif '导演:' in line1:
                    director = line1.replace('导演:', '').strip()

            if len(p_texts) >= 2:
                line2 = p_texts[1].strip()
                parts = line2.split('\xa0/\xa0')
                if len(parts) >= 1:
                    year = parts[0].strip()
                    if ' / ' in year:
                        year = year.split(' / ')[0]
                if len(parts) >= 2:
                    country = parts[1].strip()
                if len(parts) >= 3:
                    genre = parts[2].strip()

            row = [rank, title, director, actors, year, genre, country, rating, url]
            result.append(row)
            print(f"  {rank}. {title}  ★{rating}")
        return result

    def save_to_csv(self, all_data):
        """写入CSV文件，utf-8带BOM，Excel打开不乱码"""
        if not all_data:
            print("[!] 无数据可保存")
            return
        with open(self.csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(self.headers_row)
            writer.writerows(all_data)
        print(f"\n✓ 数据已保存到：{self.csv_path}，共{len(all_data)}条")

    def run(self):
        all_data = []
        for page in range(10):
            start = page * 25
            print(f"\n{'='*50}")
            print(f"  正在爬取第 {page + 1}/10 页 (start={start})")
            print(f"{'='*50}")

            html = self.fetch_page(start)
            if not html:
                continue
            page_data = self.parse_page(html)
            all_data.extend(page_data)
            print(f"  → 本页抓取 {len(page_data)} 部 | 累计 {len(all_data)} 部")

            if page < 9:
                time.sleep(2)

        self.save_to_csv(all_data)


if __name__ == '__main__':
    spider = DoubanTop250Crawler()
    spider.run()