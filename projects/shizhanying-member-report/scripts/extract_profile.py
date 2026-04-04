#!/usr/bin/env python3
"""
自我介绍信息提取脚本
从用户输入的自我介绍文本中提取关键字段，并追加写入 CSV 文件。

依赖安装：
    pip install openai
"""

import csv
import json
import os
import sys
from datetime import datetime

from openai import OpenAI

# ── 配置 ──────────────────────────────────────────────────────────────────────
API_KEY  = os.getenv("OPENAI_API_KEY", "your-api-key-here")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")  # 兼容接口可在此修改
MODEL    = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
CSV_FILE = "profiles.csv"

FIELDS = ["姓名", "年龄", "城市", "职业", "技能", "兴趣", "目标", "录入时间"]

SYSTEM_PROMPT = """你是一个信息提取助手。从用户提供的自我介绍文本中提取以下字段，以 JSON 格式返回，不要包含任何额外说明。

字段说明：
- 姓名：真实姓名或网名
- 年龄：数字或年龄段，未提及填"未知"
- 城市：所在城市，未提及填"未知"
- 职业：职业或行业，未提及填"未知"
- 技能：技能或专长，多个用顿号（、）分隔，未提及填"未知"
- 兴趣：兴趣爱好，多个用顿号（、）分隔，未提及填"未知"
- 目标：个人目标或诉求（如求职、找合作、交朋友等），未提及填"未知"

返回格式示例：
{"姓名": "王芳", "年龄": "未知", "城市": "上海", "职业": "产品经理", "技能": "未知", "兴趣": "摄影、爬山", "目标": "交朋友"}"""
# ─────────────────────────────────────────────────────────────────────────────


def extract_profile(text: str) -> dict:
    """调用 AI 接口提取自我介绍中的关键字段。"""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    # 确保所有字段都存在，缺失的填"未知"
    profile = {field: data.get(field, "未知") for field in FIELDS[:-1]}
    profile["录入时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return profile


def save_to_csv(profile: dict) -> None:
    """将提取结果追加写入 CSV，首次运行自动创建表头。"""
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(profile)


def print_profile(profile: dict) -> None:
    """格式化打印提取结果。"""
    print("\n── 提取结果 " + "─" * 40)
    labels = {
        "姓名": "姓名", "年龄": "年龄", "城市": "城市",
        "职业": "职业", "技能": "技能", "兴趣": "兴趣",
        "目标": "目标", "录入时间": "录入时间",
    }
    for field in FIELDS:
        print(f"  {labels[field]}: {profile[field]}")
    print("─" * 52 + "\n")


def main():
    if API_KEY == "your-api-key-here":
        print("错误：请设置环境变量 OPENAI_API_KEY，或直接修改脚本中的 API_KEY 变量。")
        sys.exit(1)

    print("=== 自我介绍信息提取工具 ===")
    print("请输入自我介绍文本（输入完成后按 Enter）：\n")

    try:
        text = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n已取消。")
        sys.exit(0)

    if not text:
        print("输入为空，退出。")
        sys.exit(0)

    print("\n正在提取信息，请稍候...")

    try:
        profile = extract_profile(text)
    except Exception as e:
        print(f"提取失败：{e}")
        sys.exit(1)

    print_profile(profile)
    save_to_csv(profile)
    print(f"已追加写入 {CSV_FILE}")


if __name__ == "__main__":
    main()
