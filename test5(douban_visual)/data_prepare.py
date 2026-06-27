# data_prepare.py
import pymysql
import pandas as pd

# MySQL 配置（与 douban_core.py 一致）
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "test",
    "charset": "utf8mb4"
}

try:
    # 1. 连接 MySQL
    conn = pymysql.connect(**db_config)
    print("[√] MySQL 连接成功")

    # 2. 查询 douban_movie 表
    sql = "SELECT movie_name, score FROM douban_movie"
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["movie_name", "score"])
    print(f"[√] 读取到 {len(df)} 条数据")

    # 3. 快速预览
    print("\n数据预览：")
    print(df.head())
    print(f"\n数据形状：{df.shape}")

    # 4. 保存为 CSV（供 data_clean.py 使用）
    df.to_csv("movie_raw.csv", index=False, encoding="utf-8-sig")
    print("\n[√] 数据已保存为 movie_raw.csv")

except pymysql.err.OperationalError as e:
    print(f"[✗] MySQL 连接失败: {e}")
    print("  请确认: 1)MySQL已启动 2)数据库test已创建 3)douban_movie表已建")
except Exception as e:
    print(f"[✗] 出错: {e}")
finally:
    try:
        conn.close()
    except:
        pass
