# 从同目录的 RegexCrawler 模块导入爬虫类
from RegexCrawler import RegexCrawler

def main():
    # 配置目标网址
    TARGET_URL = "https://news.sina.com.cn"
    # 实例化爬虫并执行
    crawler = RegexCrawler(TARGET_URL)
    crawler.run()

# 程序入口
if __name__ == "__main__":
    main()