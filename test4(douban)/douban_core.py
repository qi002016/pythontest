import requests
import pymysql
import time
from parsel import Selector


class DoubanTop250Crawler:
    """爬取豆瓣电影 Top 250 完整信息"""

    def __init__(self):
        self.base_url = "https://movie.douban.com/top250"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/126.0.0.0 Safari/537.36"
        }

        # MySQL 配置
        self.db_config = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "123456",
            "database": "test",
            "charset": "utf8mb4"
        }

    # ────────────────── 网络请求 ──────────────────
    def fetch_page(self, start):
        """获取单页 HTML（每页 25 部）"""
        params = {"start": start, "filter": ""}
        try:
            resp = requests.get(self.base_url, params=params,
                                headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[✗] 第 {start // 25 + 1} 页请求失败: {e}")
            return None

    # ────────────────── 数据解析 ──────────────────
    def parse_page(self, html):
        """解析单页 HTML，提取每部电影的 9 个字段"""
        sel = Selector(text=html)
        items = sel.css('ol.grid_view div.item')
        result = []

        for item in items:
            # ① 排名
            rank = item.css('div.pic em::text').get('').strip()

            # ② 电影链接
            url = item.css('div.pic a::attr(href)').get('')

            # ③ 片名（第一个 span.title）
            title = item.css('div.hd a span.title::text').get('').strip()

            # ④ 评分
            rating = item.css('span.rating_num::text').get('').strip()

            # ⑤⑥⑦⑧ 导演 / 演员 / 年份 / 国家 / 电影类型
            # <p> 结构：
            #   文本节点1: "导演: XXX   主演: YYY /..."
            #   <br>
            #   文本节点2: "1994&nbsp;/&nbsp;美国&nbsp;/&nbsp;犯罪 剧情"
            p_texts = item.css('div.bd > p:first-of-type').xpath('.//text()').getall()

            director = ''
            actors = ''
            year = ''
            country = ''
            genre = ''

            # 第一行：导演 + 演员
            if len(p_texts) >= 1:
                line1 = p_texts[0].strip()
                if '主演:' in line1:
                    parts = line1.split('主演:', 1)
                    director = parts[0].replace('导演:', '').strip()
                    actors = parts[1].strip()
                elif '导演:' in line1:
                    director = line1.replace('导演:', '').strip()

            # 第二行：年份 / 国家 / 类型
            if len(p_texts) >= 2:
                line2 = p_texts[1].strip()
                parts = line2.split('\xa0/\xa0')   # &nbsp;/&nbsp;
                if len(parts) >= 1:
                    year = parts[0].strip()
                    # 部分电影有多个上映年份（如"1961 / 1964 / 1978"），只取首个
                    if ' / ' in year:
                        year = year.split(' / ')[0]
                if len(parts) >= 2:
                    country = parts[1].strip()
                if len(parts) >= 3:
                    genre = parts[2].strip()

            result.append((rank, title, director, actors,
                           year, genre, country, rating, url))
            print(f"  {rank}. {title}  ★{rating}")

        return result

    # ────────────────── 数据持久化 ──────────────────
    def save_to_mysql(self, all_data):
        """建表并批量插入"""
        if not all_data:
            print("[!] 没有数据需要插入")
            return
        try:
            conn = pymysql.connect(**self.db_config)
            cur = conn.cursor()

            # 建表（先删后建，确保字段与代码一致）
            cur.execute("DROP TABLE IF EXISTS douban_top250")
            cur.execute("""
                CREATE TABLE douban_top250 (
                    id        INT AUTO_INCREMENT PRIMARY KEY,
                    `rank`    INT           COMMENT '排名',
                    title     VARCHAR(200)  COMMENT '片名',
                    director  VARCHAR(500)  COMMENT '导演',
                    actors    VARCHAR(2000) COMMENT '演员',
                    `year`    VARCHAR(100)  COMMENT '年份',
                    genre     VARCHAR(200)  COMMENT '电影类型',
                    country   VARCHAR(200)  COMMENT '国家',
                    rating    DECIMAL(3,1)  COMMENT '评分',
                    url       VARCHAR(500)  COMMENT '电影链接'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                COMMENT='豆瓣电影Top250'
            """)

            sql = ("INSERT INTO douban_top250 "
                   "(`rank`, title, director, actors, `year`, "
                   "genre, country, rating, url) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
            cur.executemany(sql, all_data)
            conn.commit()
            print(f"\n✓ 成功插入 {len(all_data)} 条数据到 MySQL")

        except pymysql.err.OperationalError as e:
            print(f"[✗] MySQL 连接失败: {e}")
            print("  请确认: ① MySQL 已启动  ② 数据库 test 已创建")
        except Exception as e:
            print(f"[✗] 插入失败: {e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

    # ────────────────── 主流程 ──────────────────
    def run(self):
        """爬取全部 10 页共 250 部电影"""
        all_data = []

        for page in range(10):
            start = page * 25
            print(f"\n{'='*50}")
            print(f"  正在爬取第 {page + 1}/10 页 (start={start})")
            print(f"{'='*50}")

            html = self.fetch_page(start)
            if not html:
                print(f"[✗] 第 {page + 1} 页获取失败，跳过")
                continue

            page_data = self.parse_page(html)
            all_data.extend(page_data)
            print(f"  → 本页抓取 {len(page_data)} 部 | 累计 {len(all_data)} 部")

            # 礼貌等待，避免被封
            if page < 9:
                time.sleep(2)

        print(f"\n{'='*50}")
        print(f"  爬取完毕！共 {len(all_data)} 部电影")
        print(f"{'='*50}")

        if all_data:
            self.save_to_mysql(all_data)

