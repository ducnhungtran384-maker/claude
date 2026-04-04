#!/usr/bin/env python3
"""
修正 persons.json 中错误提取的姓名
基于对 intros_output.txt 原始文本的逐条核查
"""
import json, re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# accountName -> 正确姓名映射表
# 只修正有确凿原文依据的条目
NAME_FIXES = {
    # 账号名称         正确姓名          依据说明
    "DeDDDD":         "邓宏泽",         # 原文【姓名】邓宏泽 | 工业设计... 被截断错误
    "初沐":           "刘宇轩",         # 原文 name 字段被提取成"姓名刘宇轩"
    "食既":           "徐文珊",         # 原文【姓名】徐文珊，英文名Vanco
    "千里自同风":     "杨溢",           # 原文"大家好，我叫杨溢"
    "ambition":       "郭雷",           # 原文"👋 姓名：郭雷"
    "元元":           "刘艳",           # 原文"1.姓名：刘艳"
    "Lenwiang":       "刘志涛",         # 原文"鄙人刘志涛"
    "GMD":            "莫展",           # 原文"我叫莫展"
    "emmmm":          "张科润",         # 原文"姓名：张科润"
    "浮生一日":       "刘宇翔",         # 原文"姓名：刘宇翔"（注意是翔不是轩）
    "Cash  Mage":     "姚凤雨",         # 原文"姓名：姚凤雨"
    "安&咪":          "谢旭婷",         # 原文"#谢旭婷"
    "ki":             "吕培琪",         # 原文"姓名：吕培琪"
    "苍雨":           "林伟翔",         # 原文"姓名：林伟翔"
    "必不挠北~":      "计佳良",         # 原文"姓名：计佳良"
    "1个凡人A":       "杨星宇",         # 原文"姓名：杨星宇"
    "菻":             "黄郸霖",         # 原文"◇个人介绍：黄郸霖"
    "休":             "周鹏睿",         # 原文"姓名：周鹏睿"
    "孑城":           "伍林辉",         # 原文"姓名：伍林辉"
    # 以下昵称=真名，经原文核实确实是真实姓名
    # 任赟琪、程冰慧、依杨、郑斯与、王睿雨、陈春继、包俊、汪奕辰、李乐佳
    # 陈欣源、刘梓沛、何泽、吴昊泽、黄冠杰、赵禹乐、李海鸣、孙鸿祥 均为真名
    # 杨光、郑斯与 等亦为真名
    # 以下暂无法确认（intros中查不到）：
    # 争气机、Dust dream、陈子湘（是管理员消息非自我介绍）、子淇（只写了昵称）
}

# 读取
with open('persons.json', encoding='utf-8') as f:
    data = json.load(f)

print(f"总计 {len(data)} 条记录")
fixed_count = 0
fix_log = []

for person in data:
    account = person.get('accountName', '')
    if account in NAME_FIXES:
        old_name = person['name']
        new_name = NAME_FIXES[account]
        if old_name != new_name:
            person['name'] = new_name
            fix_log.append(f"  [修正] accountName={account} : '{old_name}' -> '{new_name}'")
            fixed_count += 1
        else:
            fix_log.append(f"  [跳过] accountName={account} 名字已正确: '{old_name}'")

print(f"\n修正 {fixed_count} 条记录：")
for log in fix_log:
    print(log)

# 写回
with open('persons.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 已写回 persons.json")
