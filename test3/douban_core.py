import requests
import pymysql


class DoubanMovieCrawler:
    def __init__(self):
        # 豆瓣排行榜 API（无需 Cookie）
        self.api_url = "https://movie.douban.com/j/chart/top_list"
        self.params = {
            "type": 11,              # 电影类型（11=剧情，可改）
            "interval_id": "100:90",
            "action": "",
            "start": 0,
            "limit": 20             # 一次取 20 条
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36"
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

    def fetch_data(self):
        """请求豆瓣 API 获取 JSON 数据"""
        try:
            resp = requests.get(self.api_url, params=self.params,
                                headers=self.headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"[✗] 请求失败: {e}")
            return None

    def parse_data(self, json_data):
        """从 JSON 中提取电影名和评分"""
        result = []
        for movie in json_data:
            title = movie.get("title", "")
            score = movie.get("score", "")
            if title:
                result.append((title, score))
                print(f"{title} --- {score}")
        return result

    def save_to_mysql(self, data):
        if not data:
            print("[!] 没有数据需要插入")
            return
        try:
            conn = pymysql.connect(**self.db_config)
            cur = conn.cursor()
            sql = "INSERT INTO douban_movie (movie_name, score) VALUES (%s, %s)"
            cur.executemany(sql, data)
            conn.commit()
            print(f"成功插入 {len(data)} 条数据到MySQL")
        except pymysql.err.OperationalError as e:
            print(f"[✗] MySQL连接失败: {e}")
            print("  请确认: 1)MySQL已启动 2)数据库test已创建 3)douban_movie表已建")
        except Exception as e:
            print(f"[✗] 插入失败: {e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass

    def run(self):
        json_data = self.fetch_data()
        if not json_data:
            print("[✗] 未获取到数据，爬取终止")
            return
        data = self.parse_data(json_data)
        if data:
            self.save_to_mysql(data)
            print(f"\n共抓取到 {len(data)} 部电影，保存完成！")
        else:
            print("\n[!] 未能解析出电影数据")

