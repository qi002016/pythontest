# jisuan.py
# 计算平均分
def avg(score_list):
    return sum(score_list) / len(score_list)
# 求最高分
def max_score(score_list):
    return max(score_list)
# 求最低分
def min_score(score_list):
    return min(score_list)
# 录入5名学生姓名与成绩
name_list = []
score_list = []
for i in range(5):
    name = input(f"请输入第{i+1}名学生姓名：")
    score = float(input(f"请输入第{i+1}名学生成绩："))
    name_list.append(name)
    score_list.append(score)
# 调用模块中的函数
average = avg(score_list)
high = max_score(score_list)
low = min_score(score_list)
# 输出结果
print(f"平均分：{average:.2f}")
print(f"最高分：{high}")
print(f"最低分：{low}")
