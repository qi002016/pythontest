import os
# 缓存重定向，彻底避开C盘丢失的文件夹
os.environ['MPLCONFIGDIR'] = os.path.join(os.getcwd(), "matplotlib_cache")

import matplotlib
# 只保留中文设置，不再操作C盘文件夹
matplotlib.rcParams["font.sans-serif"] = ["SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("whitegrid")
# 二次锁定字体，防止被样式覆盖
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("movie_clean.csv", encoding="utf-8-sig")

plt.figure(figsize=(14, 10))

plt.subplot(2, 2, 1)
sns.histplot(df["score"], bins=5, kde=True, color="#3498db")
plt.title("电影评分分布")
plt.xlabel("评分")

plt.subplot(2, 2, 2)
sns.countplot(x="level", data=df, color="#3498db")
plt.title("各评分等级影片数量")

plt.subplot(2, 2, 3)
sns.boxplot(y="score", data=df, color="#2ecc71")
plt.title("评分区间箱线图")

plt.subplot(2, 2, 4)
sns.barplot(x="score", y="movie_name", data=df, color="#e74c3c")
plt.title("豆瓣高分电影排行")
plt.xlim(9.2, 9.8)

plt.tight_layout()
plt.savefig("douban_movie_chart.png", dpi=150, bbox_inches="tight")
plt.show()