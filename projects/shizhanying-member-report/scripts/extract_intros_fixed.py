#!/usr/bin/env python3
"""
修复版自我介绍信息提取脚本
修复问题：
1. 姓名提取错误（季元、彭松、郑奕淳年等）
2. 学校/年级/城市提取带冒号
3. 介绍卡片字段为空
4. 昵称→真名映射（Dustdream=高欣雨等）
"""
import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'C:/Users/weirui/Desktop/claude/.claude-attachments/群聊_【👊冲6000】IP×轻发售 实战营总群.jsonl'

# ========== 昵称→真名映射表 ==========
NICKNAME_TO_NAME = {
    'Dustdream': '高欣雨',
    'Dust dream': '高欣雨',
    '争气机': '陈子湘',
}

# ========== 学校关键词库 ==========
SCHOOL_KEYWORDS = [
    '大学', '学院', '学校', '研究院', '研究所',
    '职业技术学院', '职业学院', '职业技术大学', '高职'
]

# 读取消息
messages = []
with open(filepath, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if obj.get('_type') == 'message' and obj.get('type') == 0:
            messages.append({
                'sender': obj.get('sender', ''),
                'accountName': obj.get('accountName', ''),
                'timestamp': obj.get('timestamp', 0),
                'content': obj.get('content', '').strip()
            })

messages.sort(key=lambda x: x['timestamp'])

# 合并连续消息
merged = []
for msg in messages:
    if merged and merged[-1]['sender'] == msg['sender']:
        merged[-1]['content'] += '\n' + msg['content']
    else:
        merged.append(dict(msg))

# 筛选自我介绍消息
intro_keywords = ['姓名', '学校', '坐标', '年级', '大学', '学院', '大一', '大二', '大三', '大四',
                  '研究生', '硕士', '博士', '本科', '专科', '成就事件', '实战期待', '实战目标',
                  '期待和目标', '竞选岗位', '就读于']

intro_messages = []
seen_senders = set()
for m in merged:
    c = m['content']
    hit = sum(1 for kw in intro_keywords if kw in c)
    if hit >= 2 and m['sender'] not in seen_senders:
        intro_messages.append(m)
        seen_senders.add(m['sender'])

print(f'总自我介绍数: {len(intro_messages)}')

# ========== 提取函数 ==========

def clean_text(s):
    """清理文本中的多余符号"""
    if not s:
        return ''
    s = re.sub(r'^[：:\s【】\n\r]+', '', s)
    s = re.sub(r'[：:\s【】\n\r]+$', '', s)
    return s.strip()

def extract_name(text, account_name):
    """提取姓名 - 增强版"""
    if account_name in NICKNAME_TO_NAME:
        return NICKNAME_TO_NAME[account_name]
    
    patterns = [
        r'【姓名[^】]*】\s*[:：]?\s*([^\n\r【】]{1,10})',
        r'姓名[：:]\s*([^\n\r【】]{1,10})',
        r'姓名\s*[:：]?\s*([^\n\r【】]{1,10})',
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            name = clean_text(m.group(1))
            if name:
                if re.match(r'^[\u4e00-\u9fa5]+$', name):
                    if 2 <= len(name) <= 4:
                        return name
                elif len(name) <= 10:
                    return name
    
    lines = text.strip().split('\n')
    for line in lines[:10]:
        line = line.strip()
        line_clean = re.sub(r"[【】（）()《》\"""''，,。.！!？?\s\-:：]+", '', line)
        if 2 <= len(line_clean) <= 4 and re.match(r'^[\u4e00-\u9fa5]+$', line_clean):
            exclude_words = ['大家好', '我是', '我的', '学校', '坐标', '年级', '成就', '目标', '期望', '申请']
            if not any(w in line_clean for w in exclude_words):
                return line_clean
    
    if re.match(r'^[\u4e00-\u9fa5]{2,4}$', account_name):
        return account_name
    
    return account_name

def extract_school_and_grade(text):
    """提取学校和年级"""
    school = '未知'
    grade = '未知'
    
    lines = text.strip().split('\n')
    for line in lines[:3]:
        line = line.strip()
        simple_pattern = r'^([\u4e00-\u9fa5]+(?:大学|学院|学校))\s*[/\\\s]?\s*(大一|大二|大三|大四|大五|202\d级|20\d\d级)'
        m = re.search(simple_pattern, line)
        if m:
            school = m.group(1)
            grade = m.group(2)
            return school, grade
    
    patterns = [
        r'【学校/年级[^】]*】\s*[:：]?\s*([^\n\r【】]{2,40})',
        r'【学校[^】]*】\s*[:：]?\s*([^\n\r【】]{2,40})',
        r'学校/年级[：:]\s*([^\n\r【】]{2,40})',
        r'学校[：:]\s*([^\n\r【】]{2,40})',
        r'就读于\s*[:：]?\s*([^\n\r【】]{2,40})',
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            content = clean_text(m.group(1))
            grade_patterns = [
                r'(大一|大二|大三|大四|大五|研一|研二|研三|202\d级|20\d\d级|研究生|硕士|博士|专科|本科)',
            ]
            for gp in grade_patterns:
                gm = re.search(gp, content)
                if gm:
                    grade = gm.group(1)
                    school_part = content.replace(grade, '').strip()
                    school_part = re.sub(r'^[\/\s,，]+', '', school_part)
                    school_part = re.sub(r'[\/\s,，]+$', '', school_part)
                    if school_part and any(kw in school_part for kw in SCHOOL_KEYWORDS):
                        school = school_part
                    break
            else:
                if any(kw in content for kw in SCHOOL_KEYWORDS):
                    school = content
            break
    
    if grade == '未知':
        grade_patterns = [
            r'【年级[^】]*】\s*[:：]?\s*(大一|大二|大三|大四|大五|研一|研二|研三|202\d级|20\d\d级|研究生|硕士|博士|专科)',
            r'年级[：:]\s*(大一|大二|大三|大四|大五|研一|研二|研三|202\d级|20\d\d级|研究生|硕士|博士|专科)',
        ]
        for pattern in grade_patterns:
            m = re.search(pattern, text)
            if m:
                grade = clean_text(m.group(1))
                break
    
    if school == '未知':
        school_patterns = [
            r'就读于\s*[:：]?\s*([^\n\r【】]{2,20})',
            r'目前就读于\s*[:：]?\s*([^\n\r【】]{2,20})',
        ]
        for pattern in school_patterns:
            m = re.search(pattern, text)
            if m:
                content = clean_text(m.group(1))
                if any(kw in content for kw in SCHOOL_KEYWORDS):
                    school = content
                    break
    
    return school, grade

def extract_city(text):
    """提取城市"""
    patterns = [
        r'【坐标[^】]*】\s*[:：]?\s*([^\n\r【】]{2,20})',
        r'坐标[：:]\s*([^\n\r【】]{2,20})',
        r'坐标\s*[:：]?\s*([^\n\r【】]{2,20})',
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            city = clean_text(m.group(1))
            if city and len(city) >= 2:
                city = re.sub(r'市.*$', '', city)
                city = re.sub(r'省.*$', '', city)
                city = re.sub(r'自治区.*$', '', city)
                if ' ' in city:
                    parts = city.split()
                    for part in parts:
                        if any(kw in part for kw in ['北京', '上海', '广州', '深圳', '杭州', '南京', '武汉', '成都', '西安', '重庆']):
                            return part[:10]
                    return parts[-1][:10]
                return city[:10]
    
    return '未知'

def extract_achievement(text):
    """提取成就事件"""
    patterns = [
        r'【成就事件[^】]*】\s*[:：]?\s*([^\n\r【】]{5,100})',
        r'成就事件[：:]\s*([^\n\r【】]{5,100})',
        r'成就[：:]\s*([^\n\r【】]{5,100})',
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            achievement = clean_text(m.group(1))
            if achievement and len(achievement) >= 5:
                return achievement[:50]
    
    return '无'

def extract_goal(text):
    """提取实战目标"""
    patterns = [
        r'【本次实战[^】]*】\s*[:：]?\s*([^\n\r【】]{5,100})',
        r'【本次实战目标[^】]*】\s*[:：]?\s*([^\n\r【】]{5,100})',
        r'实战目标[：:]\s*([^\n\r【】]{5,100})',
        r'核心目标[：:]\s*([^\n\r【】]{5,100})',
        r'目标[：:]\s*([^\n\r【】]{5,100})',
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            goal = clean_text(m.group(1))
            if goal and len(goal) >= 5:
                return goal[:50]
    
    return '未知'

def extract_ai_exp(text):
    """提取AI经验水平"""
    yes_strong = [
        'ai创新赛', 'ai赛', 'ai辅助', 'ai工具.*熟练', '熟练.*ai', 'ai使用（熟练）',
        'chatgpt', 'gemini', 'midjourney', 'stable diffusion', 'claude.*工具',
        'ai新媒体', 'ai设计', '用ai完成', 'ai变现', 'ai赋能', 'ai提效'
    ]
    
    for kw in yes_strong:
        if re.search(kw, text, re.IGNORECASE):
            learn_too = any(lkw in text for lkw in ['学会AI', '学习AI', '想用AI', '掌握AI'])
            if learn_too:
                return '初步'
            return '是'
    
    has_ai_use = bool(re.search(r'用AI|使用AI|AI.*工具|AI.*能力|AI.*帮助|AI.*提效', text, re.IGNORECASE))
    want_learn = any(kw in text for kw in ['学会AI', '学习AI', '想学AI', '掌握AI', '了解AI', '提升AI'])
    
    if has_ai_use and want_learn:
        return '初步'
    if has_ai_use:
        return '初步'
    if want_learn:
        return '否'
    
    return '否'

def extract_position(text):
    """提取竞选岗位"""
    patterns = [
        r'【[^】]*(岗位|竞选)[^】]*】\s*[:：]?\s*([^\n\r【】]{1,30})',
        r'竞选岗位[：:]\s*([^\n\r【】]{1,30})',
        r'想竞选的岗位[：:]\s*([^\n\r【】]{1,30})',
    ]
    
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            pos = clean_text(m.group(1) if m.lastindex == 1 else m.group(2) if m.lastindex > 1 else m.group(1))
            if pos and pos not in ['无', '暂无', '']:
                return pos[:25]
    
    return '无'

def classify_edu(school, grade):
    """分类学历层次"""
    if '985' in school:
        return '985'
    if '211' in school:
        return '211'
    
    s985 = ['北京大学', '清华大学', '复旦大学', '上海交通大学', '浙江大学', '南京大学', 
            '中国科学技术大学', '哈尔滨工业大学', '西安交通大学', '中国人民大学',
            '北京航空航天大学', '北京理工大学', '北京师范大学', '南开大学', '天津大学',
            '大连理工大学', '吉林大学', '同济大学', '东南大学', '厦门大学', '山东大学',
            '武汉大学', '华中科技大学', '中南大学', '国防科技大学', '中山大学', '四川大学',
            '电子科技大学', '重庆大学', '西北工业大学', '兰州大学', '东北大学', '湖南大学',
            '西北农林科技大学', '华东师范大学', '华南理工大学', '中国海洋大学', '中央民族大学']
    
    s211 = ['合肥工业大学', '西南交通大学', '武汉理工大学', '华中师范大学', '南京师范大学',
            '陕西师范大学', '华南师范大学', '湖南师范大学', '东北师范大学', '西南大学',
            '暨南大学', '上海大学', '苏州大学', '郑州大学', '云南大学', '贵州大学',
            '广西大学', '海南大学', '西藏大学', '青海大学', '宁夏大学', '新疆大学',
            '石河子大学', '内蒙古大学', '延边大学', '东北林业大学', '东北农业大学',
            '四川农业大学', '西南财经大学', '中南财经政法大学', '上海财经大学',
            '对外经济贸易大学', '中央财经大学', '中国政法大学', '北京邮电大学',
            '北京交通大学', '北京科技大学', '北京化工大学', '北京工业大学', '北京林业大学',
            '华北电力大学', '中国矿业大学', '中国地质大学', '中国石油大学', '河海大学',
            '江南大学', '南京农业大学', '中国药科大学', '南京理工大学', '南京航空航天大学',
            '上海外国语大学', '上海大学', '东华大学', '长安大学', '西安电子科技大学',
            '西北大学', '第四军医大学', '第二军医大学', '太原理工大学', '辽宁大学',
            '大连海事大学', '安徽大学', '福州大学', '南昌大学', '湖南师范大学',
            '华南师范大学', '暨南大学', '西南交通大学', '西南财经大学', '四川农业大学']
    
    for s in s985:
        if s in school:
            return '985'
    for s in s211:
        if s in school:
            return '211'
    
    overseas_keywords = ['香港', '澳门', '台湾', 'University', 'College', 'Institute', '新加坡', '英国', '美国', '澳大利亚', '加拿大']
    if any(kw.lower() in school.lower() for kw in overseas_keywords):
        return '海外/港澳台'
    
    if any(kw in school for kw in ['职业技术学院', '职业学院', '职业技术大学', '高职', '技师学院']):
        return '专科'
    if grade == '专科':
        return '专科'
    
    if '研究生' in grade or '硕士' in grade or '博士' in grade:
        return '研究生'
    
    if school == '未知':
        return '未知'
    
    return '普通本科'

def extract_intro_card(text):
    """提取介绍卡片内容"""
    lines = text.strip().split('\n')
    content_lines = [l.strip() for l in lines if l.strip() and len(l.strip()) > 3]
    intro = '\n'.join(content_lines[:10])
    if len(intro) > 300:
        intro = intro[:300] + '...'
    return intro if intro else '暂无介绍'

# ========== 主处理流程 ==========
persons = []
for m in intro_messages:
    text = m['content']
    account = m['accountName']
    
    name = extract_name(text, account)
    school, grade = extract_school_and_grade(text)
    city = extract_city(text)
    achievement = extract_achievement(text)
    goal = extract_goal(text)
    ai_exp = extract_ai_exp(text)
    position = extract_position(text)
    edu = classify_edu(school, grade)
    intro_card = extract_intro_card(text)
    
    persons.append({
        'name': name,
        'accountName': account,
        'school': school,
        'grade': grade,
        'city': city,
        'achievement': achievement,
        'goal': goal,
        'ai_exp': ai_exp,
        'position': position,
        'edu': edu,
        'intro_card': intro_card,
    })

print(f'\n提取到人员: {len(persons)}')
print()

for i, p in enumerate(persons[:20]):
    print(f'[{i+1:3d}] {p["name"][:8]:8s} | {p["accountName"][:10]:10s} | {p["school"][:15]:15s} | {p["grade"]:8s} | {p["city"][:8]:8s} | {p["edu"]:6s} | AI:{p["ai_exp"]:3s} | 岗位:{p["position"][:12]}')

edu_counts = {}
for p in persons:
    edu_counts[p['edu']] = edu_counts.get(p['edu'], 0) + 1
print('\n=== 学历统计 ===')
for k, v in sorted(edu_counts.items(), key=lambda x: -x[1]):
    print(f'  {k}: {v}人')

ai_counts = {}
for p in persons:
    ai_counts[p['ai_exp']] = ai_counts.get(p['ai_exp'], 0) + 1
print('\n=== AI经验统计 ===')
for k, v in ai_counts.items():
    print(f'  {k}: {v}人')

output_path = r'C:/Users/weirui/Desktop/claude/persons_fixed.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(persons, f, ensure_ascii=False, indent=2)

print(f'\n已保存到: {output_path}')

print('\n=== 可能的问题数据 ===')
for p in persons:
    issues = []
    if len(p['name']) > 5 or len(p['name']) < 2:
        issues.append(f'姓名异常({p["name"]})')
    if p['school'] == '未知':
        issues.append('学校未知')
    if p['grade'] == '未知':
        issues.append('年级未知')
    if p['city'] == '未知':
        issues.append('城市未知')
    if '：' in p['school'] or ':' in p['school']:
        issues.append(f'学校含冒号({p["school"]})')
    if '：' in p['city'] or ':' in p['city']:
        issues.append(f'城市含冒号({p["city"]})')
    
    if issues:
        print(f"  {p['name'][:8]:8s} ({p['accountName'][:10]}): {', '.join(issues)}")
