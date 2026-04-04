import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'C:/Users/weirui/Desktop/claude/.claude-attachments/群聊_【👊冲6000】IP×轻发售 实战营总群.jsonl'

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
merged = []
for msg in messages:
    if merged and merged[-1]['sender'] == msg['sender']:
        merged[-1]['content'] += '\n' + msg['content']
    else:
        merged.append(dict(msg))

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

def extract_name(text, account_name):
    m = re.search(r'【姓名[^】]*】\s*[\n\r]*([^\n\r【]{1,15})', text)
    if m:
        name = m.group(1).strip()
        name_clean = re.sub(r'[^\u4e00-\u9fa5a-zA-Z]', '', name)
        if name_clean and len(name_clean) <= 10:
            return name_clean[:6]
    lines = text.strip().split('\n')
    for line in lines[:5]:
        line = line.strip()
        line_clean = re.sub(r"[【】（）()《》\"""''，,。.！!？?\s\-]", '', line)
        if 2 <= len(line_clean) <= 5 and re.match(r'^[\u4e00-\u9fa5]+$', line_clean):
            return line_clean
    return account_name

def extract_school(text):
    m = re.search(r'【学校[^】]*】\s*[\n\r]*([^\n\r【]{2,40})', text)
    if m:
        s = m.group(1).strip()
        s = re.sub(r'\s*(大[一二三四]|[0-9]{4}级?|本科|专科|研究生|硕士|博士|\d年级).*', '', s)
        s = re.sub(r'[/／].*', '', s)
        s = s.strip()
        if s:
            return s[:20]
    patterns = [
        r'就读于([^\s，,。\n]{3,20}(?:大学|学院|学校))',
        r'([^\n，,。\s]{2,20}(?:大学|学院))[^\n]*(?:大[一二三四]|[0-9]{4}级)',
    ]
    for p in patterns:
        m2 = re.search(p, text)
        if m2:
            s = m2.group(1).strip()
            s = re.sub(r'\s*(大[一二三四]|[0-9]{4}级?).*', '', s)
            return s.strip()[:20]
    return '未知'

def extract_grade(text):
    m = re.search(r'【学校[^】]*】[^\n]*([大本][一二三四]|[0-9]{4}级?|研究生|硕士|博士|专科)', text)
    if m:
        return m.group(1).strip()
    m = re.search(r'(大[一二三四]|[0-9]{4}级|研究生\d?年?级?|硕士\d?年?|博士|专科)', text)
    if m:
        return m.group(1).strip()
    return '未知'

def extract_city(text):
    m = re.search(r'【坐标[^】]*】\s*[\n\r]*([^\n\r【]{2,25})', text)
    if m:
        c = m.group(1).strip()
        city_m = re.search(r'([^\s，,省市区县]+市)', c)
        if city_m:
            return city_m.group(1)
        c2 = re.sub(r'^[\u4e00-\u9fa5]{1,3}省', '', c)
        c2 = c2.strip()
        if c2:
            return c2[:12]
        return c[:12]
    patterns = [
        r'坐标[：:]\s*([^\n，,]{2,15})',
    ]
    for p in patterns:
        m2 = re.search(p, text)
        if m2:
            return m2.group(1).strip()[:15]
    return '未知'

def extract_achievement(text):
    m = re.search(r'【成就事件[^】]*】\s*[\n\r]*([^\n\r【]{5,})', text)
    if m:
        a = m.group(1).strip()
        return a[:30]
    m = re.search(r'成就事件[：:]\s*([^\n]{5,})', text)
    if m:
        a = m.group(1).strip()
        return a[:30]
    return '无'

def extract_goal(text):
    patterns = [
        r'【本次实战[^】]*】\s*[\n\r]*([^\n\r【]{5,})',
        r'实战目标[：:]\s*([^\n]{5,})',
        r'【本次实战目标[^】]*】\s*[\n\r]*([^\n\r【]{5,})',
        r'核心目标[：:]\s*([^\n]{5,})',
        r'目标[：:]\s*([^\n]{5,})',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            g = m.group(1).strip()
            return g[:30]
    return '未知'

def extract_ai_exp(text):
    yes_strong = [
        'AI创新赛', 'AI赛', 'AI辅助', 'AI工具.*熟练', '熟练.*AI', 'AI使用（熟练）',
        'ChatGPT', 'Gemini', 'Midjourney', 'Stable Diffusion', 'Claude.*工具',
        'AI新媒体', 'AI设计', '用AI完成', 'AI变现', 'AI赋能'
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
    m = re.search(r'【[^】]*(岗位|竞选)[^】]*】\s*[\n\r]*([^\n\r【]{1,30})', text)
    if m:
        pos = m.group(2).strip()
        if pos and pos not in ['无', '暂无', '']:
            return pos[:25]
    m = re.search(r'(?:竞选|申请|意向)[^：:\n]*[：:]\s*([^\n]{1,30})', text)
    if m:
        pos = m.group(1).strip()
        if pos:
            return pos[:25]
    m = re.search(r'我想竞选的岗位[^\n]*\n([^\n【]{1,30})', text)
    if m:
        pos = m.group(1).strip()
        if pos:
            return pos[:25]
    return '无'

def classify_edu(school, grade):
    c985 = ['北京大学','清华大学','复旦大学','上海交通大学','浙江大学','南京大学','中国科学技术大学',
            '哈尔滨工业大学','西安交通大学','北京航空航天大学','北京理工大学','中国人民大学',
            '北京师范大学','武汉大学','华中科技大学','天津大学','大连理工大学','吉林大学',
            '东南大学','厦门大学','山东大学','华南理工大学','中山大学','四川大学','同济大学',
            '重庆大学','兰州大学','中南大学','湖南大学','西北工业大学','电子科技大学',
            '中国农业大学','中央民族大学','国防科技大学','东北大学','南开大学']
    c211 = ['上海外国语大学','北京外国语大学','对外经济贸易大学','中央财经大学','东北财经大学',
            '南京农业大学','华中农业大学','南京信息工程大学','合肥工业大学','中国矿业大学',
            '华东交通大学','郑州大学','华南农业大学','北京工业大学','北京化工大学',
            '北京邮电大学','首都师范大学','中国地质大学','中国石油大学','中国海洋大学',
            '海南大学','广西大学','贵州大学','云南大学','西藏大学','新疆大学','延边大学',
            '石河子大学','宁夏大学','青海大学','内蒙古大学','河海大学','南京理工大学',
            '南京航空航天大学','苏州大学','扬州大学','江南大学','江苏大学','安徽大学',
            '华中师范大学','武汉理工大学','中南财经政法大学','华东师范大学','上海大学',
            '上海财经大学','上海理工大学','东华大学','暨南大学','汕头大学','深圳大学',
            '中国矿业大学（北京）','东北财经大学']

    if any(s in school for s in c985):
        return '985'
    if any(s in school for s in c211):
        return '211'

    overseas_keywords = ['university', 'college', 'school', '香港', '澳门', '台湾']
    if any(kw.lower() in school.lower() for kw in overseas_keywords):
        return '海外/港澳台'

    if any(kw in school for kw in ['职业技术学院', '职业学院', '职业技术大学', '高职', '技师学院']):
        return '专科'
    if grade in ['专科']:
        return '专科'
    if '研究生' in grade or '硕士' in grade or '博士' in grade:
        return '研究生'
    if school == '未知':
        return '未知'
    return '普通本科'

persons = []
for m in intro_messages:
    text = m['content']
    account = m['accountName']
    name = extract_name(text, account)
    school = extract_school(text)
    grade = extract_grade(text)
    city = extract_city(text)
    achievement = extract_achievement(text)
    goal = extract_goal(text)
    ai_exp = extract_ai_exp(text)
    position = extract_position(text)
    edu = classify_edu(school, grade)

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
    })

print(f'\n提取到人员: {len(persons)}')
print()
for i, p in enumerate(persons):
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

city_counts = {}
for p in persons:
    city_counts[p['city']] = city_counts.get(p['city'], 0) + 1
print('\n=== 城市TOP15 ===')
for k, v in sorted(city_counts.items(), key=lambda x: -x[1])[:15]:
    print(f'  {k}: {v}人')

with open(r'C:/Users/weirui/Desktop/claude/persons.json', 'w', encoding='utf-8') as f:
    json.dump(persons, f, ensure_ascii=False, indent=2)
print('\n数据已保存到 persons.json')
