"""
通用正则爬虫核心类 —— 提取邮箱、手机号、新闻标题/链接、图片链接
"""
import requests
import re
import os
import json
from datetime import datetime
from urllib.parse import urljoin


class RegexCrawler:
    """基于正则表达式的通用信息爬虫"""

    def __init__(self, url, save_dir=None):
        if save_dir is None:
            save_dir = os.path.join(os.path.dirname(__file__), "output")
        self.url = url
        self.save_dir = save_dir
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/126.0.0.0 Safari/537.36"
        }
        # 自动创建文件夹
        os.makedirs(self.save_dir, exist_ok=True)

    # ==================== 正则表达式定义 ====================
    # 1. 邮箱地址
    EMAIL_PATTERN = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )

    # 2. 中国大陆手机号码（零宽断言避免数字粘连）
    PHONE_PATTERN = re.compile(
        r'(?<!\d)1[3-9]\d{9}(?!\d)'
    )

    # 3. 新闻标题正则组（统一两分组：(链接, 标题)）
    NEWS_TITLE_PATTERNS = [
        # h1~h6标题栏内a标签
        re.compile(
            r'<h[1-6][^>]*>.*?<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>',
            re.DOTALL | re.IGNORECASE
        ),
        # 带标题class的a标签（class关键词设为非捕获组）
        re.compile(
            r'<a[^>]*class=["\'][^"\']*(?:title|headline|news-title|article-title|post-title)'
            r'[^"\']*["\'][^>]*href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>',
            re.DOTALL | re.IGNORECASE
        ),
        # a标签含title属性：(链接, title属性值作为标题)
        re.compile(
            r'<a[^>]*href=["\']([^"\']+)["\'][^>]*title=["\']([^"\']{5,})["\']',
            re.IGNORECASE
        ),
    ]

    # 4. 图片链接（精准后缀匹配）
    IMG_PATTERN = re.compile(
        r'<img[^>]+src=["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp|svg|bmp)(?:\?[^"\']*)?)["\']',
        re.IGNORECASE
    )
    # 兜底宽松匹配
    IMG_PATTERN_LOOSE = re.compile(
        r'<img[^>]+src=["\']([^"\']+)["\']',
        re.IGNORECASE
    )

    # ==================== 核心网络请求 ====================
    def fetch_page(self):
        """请求网页，返回 HTML 文本"""
        print(f"[*] 正在请求: {self.url}")
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=15)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            print(f"[✓] 请求成功，状态码: {resp.status_code}，页面大小: {len(resp.text)} 字符")
            return resp.text
        except requests.exceptions.RequestException as e:
            print(f"[✗] 请求异常: {e}")
            return None

    # ==================== 信息提取函数 ====================
    def extract_emails(self, html):
        """提取邮箱，自动去重"""
        raw = self.EMAIL_PATTERN.findall(html)
        results = sorted(list(set(raw)))
        print(f"[✓] 提取到 {len(results)} 个邮箱地址")
        return results

    def extract_phones(self, html):
        """提取手机号，自动去重"""
        raw = self.PHONE_PATTERN.findall(html)
        results = sorted(list(set(raw)))
        print(f"[✓] 提取到 {len(results)} 个手机号码")
        return results

    def extract_news(self, html):
        """提取新闻标题+链接，去重+补全URL"""
        results = []
        seen_key = set()

        for pat in self.NEWS_TITLE_PATTERNS:
            matches = pat.findall(html)
            for item in matches:
                # 分组全部统一为两分组 (链接, 标题)
                if len(item) >= 2:
                    link_raw, title_raw = item[0], item[1]
                else:
                    continue

                # 清除html标签 + 首尾空格
                title = re.sub(r'<.+?>', '', title_raw).strip()
                link_raw = link_raw.strip()

                if len(title) < 2 or not link_raw:
                    continue

                # 组合唯一键去重
                unique_key = f"{title}|{link_raw}"
                if unique_key in seen_key:
                    continue
                seen_key.add(unique_key)

                # 使用urljoin智能拼接相对地址
                full_link = urljoin(self.url, link_raw)
                results.append({"title": title, "link": full_link})

        print(f"[✓] 提取到 {len(results)} 条新闻标题/链接")
        return results

    def extract_images(self, html):
        """提取图片链接，补全相对路径并去重"""
        raw_links = self.IMG_PATTERN.findall(html)
        if not raw_links:
            raw_links = self.IMG_PATTERN_LOOSE.findall(html)

        full_links = set()
        for src in raw_links:
            full_src = urljoin(self.url, src.strip())
            full_links.add(full_src)

        results = sorted(list(full_links))
        print(f"[✓] 提取到 {len(results)} 张图片链接")
        return results

    # ==================== 文件保存 ====================
    def save_results(self, data, filename):
        """通用保存方法"""
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    f.write(json.dumps(data, ensure_ascii=False, indent=2))
                else:
                    f.write("\n".join(data))
            else:
                f.write(str(data))
        print(f"[💾] 已保存: {filepath}")

    def save_summary(self, all_data):
        """生成汇总文本报告"""
        content = [
            f"爬取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"目标网址：{self.url}",
            "-" * 60,
            f"邮箱数量：{len(all_data['emails'])}",
            f"手机号数量：{len(all_data['phones'])}",
            f"新闻条目：{len(all_data['news'])}",
            f"图片链接：{len(all_data['images'])}",
            "-" * 60,
        ]
        report_path = os.path.join(self.save_dir, "爬取汇总报告.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        print(f"[💾] 汇总报告已保存至：{report_path}\n")
        print("\n".join(content))

    def run(self):
        """整体执行入口"""
        print("=" * 50)
        print("通用正则信息爬虫开始运行")
        print("=" * 50)

        html = self.fetch_page()
        if not html:
            return

        data = {
            "emails": self.extract_emails(html),
            "phones": self.extract_phones(html),
            "news": self.extract_news(html),
            "images": self.extract_images(html)
        }

        # 分别保存文件
        self.save_results(data["emails"], "邮箱地址.txt")
        self.save_results(data["phones"], "手机号码.txt")
        self.save_results(data["news"], "新闻标题及链接.json")
        self.save_results(data["images"], "图片链接.txt")
        self.save_summary(data)

        print("[✓] 所有信息抓取保存完毕！")