# main.py
import subprocess
import sys

def run_script(script_name):
    """运行单个脚本，返回是否成功"""
    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=False,
        text=True
    )
    return result.returncode == 0

def main():
    print("豆瓣电影评分数据处理流水线\n")

    steps = [
        ("data_prepare.py", "准备数据: MySQL → movie_raw.csv"),
        ("data_clean.py",   "清洗数据: movie_raw.csv → movie_clean.csv"),
        ("data_visual.py",  "可视化:   生成图表"),
    ]

    for script, desc in steps:
        print(f"{'='*40}")
        print(f">>> {desc}")
        print(f"{'='*40}")
        if not run_script(script):
            print(f"\n[✗] 流程中断于: {script}")
            return

    print(f"\n{'='*40}")
    print("流水线执行完毕！")

if __name__ == "__main__":
    main()
