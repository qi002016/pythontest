import requests
from lxml import etree
import pymysql

class XpathPoetryCrawler:
    def __init__(self):
        self.url = "https://www.gushiwen.cn/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0.0.0 Safari/537.36"
        }
        self.db_config = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "123456",
            "database": "test",
            "charset": "utf8mb4"
        }

    def get_html(self):
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[✗] 请求失败: {e}")
            return None

    def parse_by_xpath(self, html):
        tree = etree.HTML(html)
        item_list = tree.xpath('//div[@class="sons"]')
        data_list = []
        for item in item_list:
            title_nodes = item.xpath('.//div[@class="cont"]//p/a/b/text()')
            if not title_nodes:
                title_nodes = item.xpath('.//div[@class="cont"]//p[1]/a/text()')
            author_nodes = item.xpath('.//p[@class="source"]/a[1]/text()')
            content_nodes = item.xpath('.//div[@class="contson"]//text()')
            title = title_nodes[0].strip() if title_nodes else ""
            author = author_nodes[0].strip() if author_nodes else ""
            content = "".join(t.strip() for t in content_nodes if t.strip())
            if title:
                data_list.append((title, author, content))
        return data_list

    def save_to_mysql(self, data):
        if not data:
            print("[!] 没有数据需要插入")
            return
        try:
            conn = pymysql.connect(**self.db_config)
            cur = conn.cursor()
            sql = "INSERT INTO poetry (title, author, content) VALUES (%s, %s, %s)"
            cur.executemany(sql, data)
            conn.commit()
            print(f"成功插入 {len(data)} 条数据到MySQL")
        except pymysql.err.OperationalError as e:
            print(f"[✗] MySQL连接失败: {e}")
            print("  请确认: 1)MySQL已启动 2)数据库test已创建 3)poetry表已建")
        except Exception as e:
            print(f"[✗] 插入失败: {e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

    def run(self):
        html = self.get_html()
        if not html:
            print("[✗] 未获取到页面内容，爬取终止")
            return
        poem_data = self.parse_by_xpath(html)
        print(f"解析到 {len(poem_data)} 条诗词")
        self.save_to_mysql(poem_data)



