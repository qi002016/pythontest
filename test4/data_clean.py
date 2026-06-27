# data_clean.py
import pandas as pd

# 1. 读取原始数据
df = pd.read_csv("movie_raw.csv", encoding="utf-8-sig")

# 2. 基础信息查看
print("数据形状：", df.shape)
print("\n缺失值统计：")
print(df.isnull().sum())

# 3. 数据清洗

# ① 检查重复行并去重
df = df.drop_duplicates(subset=["movie_name"])
# ② 新增评分等级列
def get_level(s):
    if s >= 9.6:
        return "顶级佳作"
    elif s >= 9.4:
        return "高分佳片"
    else:
        return "优秀影片"

df["level"] = df["score"].apply(get_level)

# 4. 保存清洗后数据
df.to_csv("movie_clean.csv", index=False, encoding="utf-8-sig")
print("\n清洗完成，数据保存为 movie_clean.csv")
print(df.head())