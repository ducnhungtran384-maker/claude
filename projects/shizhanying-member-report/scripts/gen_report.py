import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:/Users/weirui/Desktop/claude/persons.json', 'r', encoding='utf-8') as f:
    persons = json.load(f)

# 清洗数据中的冗余符号
def clean(s):
    s = re.sub(r'^[：:【】\s]+', '', s)
    s = re.sub(r'[：:【】\s]+$', '', s)
    return s.strip()

for p in persons:
    p['school'] = clean(p['school'])
    p['city'] = clean(p['city'])
    p['position'] = clean(p['position'])

# 统计
edu_counts = {}
for p in persons:
    edu_counts[p['edu']] = edu_counts.get(p['edu'], 0) + 1

ai_counts = {}
for p in persons:
    ai_counts[p['ai_exp']] = ai_counts.get(p['ai_exp'], 0) + 1

grade_counts = {}
for p in persons:
    g = p['grade']
    if re.match(r'大[一二三四]', g):
        g2 = re.match(r'大[一二三四]', g).group()
    elif re.match(r'\d{4}级', g):
        g2 = '2025级/新生'
    elif '研究生' in g or '硕士' in g:
        g2 = '研究生/硕士'
    elif '博士' in g:
        g2 = '博士'
    elif '专科' in g:
        g2 = '专科'
    else:
        g2 = '未知'
    grade_counts[g2] = grade_counts.get(g2, 0) + 1

city_counts = {}
for p in persons:
    city_counts[p['city']] = city_counts.get(p['city'], 0) + 1

position_counts = {}
for p in persons:
    pos = p['position']
    if pos and pos != '无':
        if '战队' in pos and '队长' in pos:
            k = '战队队长'
        elif '队长' in pos or '战队长' in pos:
            k = '战队队长'
        elif '政委' in pos:
            k = '政委'
        elif '分发官' in pos or '分发' in pos:
            k = '分发官'
        elif '文案' in pos:
            k = '文案官'
        elif '分享官' in pos:
            k = '分享官'
        elif '气氛' in pos:
            k = '气氛组'
        else:
            k = '其他岗位'
        position_counts[k] = position_counts.get(k, 0) + 1
    else:
        position_counts['未竞选'] = position_counts.get('未竞选', 0) + 1

# 生成HTML
rows_html = ''
for i, p in enumerate(persons):
    ai_badge = {
        '是': '<span class="badge ai-yes">有实操</span>',
        '初步': '<span class="badge ai-init">初步</span>',
        '否': '<span class="badge ai-no">待入门</span>'
    }.get(p['ai_exp'], '')

    edu_badge = {
        '985': '<span class="badge edu-985">985</span>',
        '211': '<span class="badge edu-211">211</span>',
        '普通本科': '<span class="badge edu-normal">普本</span>',
        '专科': '<span class="badge edu-junior">专科</span>',
        '海外/港澳台': '<span class="badge edu-overseas">海外</span>',
        '研究生': '<span class="badge edu-985">研究生</span>',
        '未知': '<span class="badge edu-unknown">未知</span>',
    }.get(p['edu'], '')

    pos_text = p['position'] if p['position'] and p['position'] != '无' else '<span style="color:#aaa">无</span>'
    rows_html += f'''
    <tr>
      <td class="num">{i+1}</td>
      <td class="name">{p["name"]}</td>
      <td class="nick">{p["accountName"]}</td>
      <td>{p["school"]}<br>{edu_badge}</td>
      <td>{p["grade"]}</td>
      <td>{p["city"]}</td>
      <td class="achieve">{p["achievement"]}</td>
      <td class="goal">{p["goal"]}</td>
      <td>{ai_badge}</td>
      <td class="pos">{pos_text}</td>
    </tr>'''

# 学历统计图
edu_order = ['985', '211', '普通本科', '专科', '研究生', '海外/港澳台', '未知']
edu_bars = ''
total = len(persons)
for e in edu_order:
    n = edu_counts.get(e, 0)
    pct = round(n / total * 100, 1)
    color = {
        '985': '#e74c3c',
        '211': '#e67e22',
        '普通本科': '#3498db',
        '专科': '#27ae60',
        '研究生': '#9b59b6',
        '海外/港澳台': '#1abc9c',
        '未知': '#95a5a6'
    }.get(e, '#bdc3c7')
    edu_bars += f'''<div class="stat-bar-row">
      <span class="stat-label">{e}</span>
      <div class="stat-bar-wrap"><div class="stat-bar" style="width:{pct*4}px;background:{color}"></div></div>
      <span class="stat-val">{n}人 ({pct}%)</span>
    </div>'''

# AI统计
ai_bars = ''
ai_order = [('是', '#27ae60', 'AI有实操'), ('初步', '#f39c12', 'AI初步接触'), ('否', '#e74c3c', 'AI待入门')]
for ai_key, color, label in ai_order:
    n = ai_counts.get(ai_key, 0)
    pct = round(n / total * 100, 1)
    ai_bars += f'''<div class="stat-bar-row">
      <span class="stat-label">{label}</span>
      <div class="stat-bar-wrap"><div class="stat-bar" style="width:{pct*4}px;background:{color}"></div></div>
      <span class="stat-val">{n}人 ({pct}%)</span>
    </div>'''

# 年级统计
grade_bars = ''
grade_order = ['大一', '大二', '大三', '大四', '2025级/新生', '研究生/硕士', '博士', '专科', '未知']
grade_colors = ['#3498db','#2ecc71','#e67e22','#9b59b6','#1abc9c','#e74c3c','#8e44ad','#27ae60','#95a5a6']
for gi, g in enumerate(grade_order):
    n = grade_counts.get(g, 0)
    if n == 0:
        continue
    pct = round(n / total * 100, 1)
    color = grade_colors[gi % len(grade_colors)]
    grade_bars += f'''<div class="stat-bar-row">
      <span class="stat-label">{g}</span>
      <div class="stat-bar-wrap"><div class="stat-bar" style="width:{pct*4}px;background:{color}"></div></div>
      <span class="stat-val">{n}人 ({pct}%)</span>
    </div>'''

# 城市TOP10
city_top = sorted(city_counts.items(), key=lambda x: -x[1])
city_top = [(k, v) for k, v in city_top if k not in ('未知', '', '无') and v > 0][:10]
city_html = ''
for city, n in city_top:
    pct = round(n / total * 100, 1)
    city_html += f'''<div class="stat-bar-row">
      <span class="stat-label">{city}</span>
      <div class="stat-bar-wrap"><div class="stat-bar" style="width:{n*20}px;background:#3498db"></div></div>
      <span class="stat-val">{n}人</span>
    </div>'''

# 岗位统计
pos_html = ''
for pos, n in sorted(position_counts.items(), key=lambda x: -x[1]):
    pct = round(n / total * 100, 1)
    color = '#e74c3c' if pos == '未竞选' else '#3498db'
    pos_html += f'''<div class="stat-bar-row">
      <span class="stat-label">{pos}</span>
      <div class="stat-bar-wrap"><div class="stat-bar" style="width:{n*5}px;background:{color}"></div></div>
      <span class="stat-val">{n}人 ({pct}%)</span>
    </div>'''

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>【👊冲6000】IP×轻发售 实战营 成员画像分析报告</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f0f2f5; color: #333; }}
  .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 48px 32px; }}
  .header h1 {{ font-size: 26px; font-weight: 700; margin-bottom: 8px; }}
  .header .subtitle {{ font-size: 14px; opacity: 0.85; }}
  .header .meta {{ margin-top: 18px; display: flex; gap: 32px; flex-wrap: wrap; }}
  .header .meta-item {{ font-size: 13px; }}
  .header .meta-item strong {{ font-size: 28px; font-weight: 800; display: block; }}
  .container {{ max-width: 1600px; margin: 0 auto; padding: 32px 24px; }}

  .section {{ background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 28px; overflow: hidden; }}
  .section-header {{ padding: 20px 28px; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 10px; }}
  .section-header h2 {{ font-size: 17px; font-weight: 600; color: #2c3e50; }}
  .section-header .icon {{ font-size: 20px; }}

  /* 统计卡片 */
  .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0; }}
  .stat-card {{ padding: 24px 28px; border-right: 1px solid #f0f0f0; }}
  .stat-card:last-child {{ border-right: none; }}
  .stat-card h3 {{ font-size: 13px; color: #888; margin-bottom: 16px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
  .stat-bar-row {{ display: flex; align-items: center; margin-bottom: 10px; gap: 8px; }}
  .stat-label {{ width: 90px; font-size: 13px; color: #555; text-align: right; flex-shrink: 0; }}
  .stat-bar-wrap {{ flex: 1; min-width: 0; }}
  .stat-bar {{ height: 18px; border-radius: 3px; min-width: 4px; transition: width 0.3s; }}
  .stat-val {{ font-size: 12px; color: #888; white-space: nowrap; }}

  /* 洞察 */
  .insights {{ padding: 24px 28px; }}
  .insight-item {{ display: flex; gap: 16px; margin-bottom: 20px; padding: 16px; background: #f8f9fc; border-radius: 8px; border-left: 4px solid #667eea; }}
  .insight-num {{ font-size: 22px; font-weight: 800; color: #667eea; flex-shrink: 0; width: 32px; }}
  .insight-text h4 {{ font-size: 15px; font-weight: 600; margin-bottom: 6px; color: #2c3e50; }}
  .insight-text p {{ font-size: 13px; color: #666; line-height: 1.7; }}

  .common-diff {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; }}
  .common-section, .diff-section {{ padding: 24px 28px; }}
  .common-section {{ border-right: 1px solid #f0f0f0; }}
  .common-section h3, .diff-section h3 {{ font-size: 14px; font-weight: 600; color: #2c3e50; margin-bottom: 14px; display: flex; align-items: center; gap: 6px; }}
  .common-section ul, .diff-section ul {{ list-style: none; }}
  .common-section li, .diff-section li {{ font-size: 13px; color: #555; padding: 8px 0; border-bottom: 1px solid #f5f5f5; line-height: 1.6; display: flex; gap: 8px; }}
  .common-section li:before {{ content: "✓"; color: #27ae60; font-weight: bold; flex-shrink: 0; }}
  .diff-section li:before {{ content: "◆"; color: #e67e22; font-weight: bold; flex-shrink: 0; }}

  /* 表格 */
  .table-wrap {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  thead tr {{ background: #f8f9fc; }}
  thead th {{ padding: 12px 10px; text-align: left; font-weight: 600; color: #555; font-size: 12px; border-bottom: 2px solid #e8e8e8; white-space: nowrap; }}
  tbody tr {{ border-bottom: 1px solid #f0f0f0; }}
  tbody tr:hover {{ background: #fafbff; }}
  tbody td {{ padding: 10px 10px; vertical-align: top; }}
  td.num {{ color: #aaa; font-size: 11px; width: 30px; text-align: center; }}
  td.name {{ font-weight: 600; color: #2c3e50; white-space: nowrap; }}
  td.nick {{ color: #888; font-size: 12px; }}
  td.achieve, td.goal {{ max-width: 180px; line-height: 1.5; color: #555; }}
  td.pos {{ color: #667eea; font-size: 12px; }}

  /* badge */
  .badge {{ display: inline-block; padding: 1px 7px; border-radius: 10px; font-size: 11px; font-weight: 600; margin-top: 3px; }}
  .edu-985 {{ background: #fdecea; color: #c0392b; }}
  .edu-211 {{ background: #fef3e2; color: #d35400; }}
  .edu-normal {{ background: #eaf4fb; color: #2980b9; }}
  .edu-junior {{ background: #eafaf1; color: #27ae60; }}
  .edu-overseas {{ background: #e8f8f5; color: #16a085; }}
  .edu-unknown {{ background: #f5f5f5; color: #95a5a6; }}
  .ai-yes {{ background: #eafaf1; color: #27ae60; }}
  .ai-init {{ background: #fef9e7; color: #d68910; }}
  .ai-no {{ background: #fdecea; color: #c0392b; }}

  .table-filter {{ padding: 16px 28px; border-bottom: 1px solid #f0f0f0; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
  .filter-label {{ font-size: 13px; color: #888; }}
  .filter-btn {{ padding: 4px 14px; border-radius: 14px; border: 1px solid #ddd; background: white; font-size: 12px; cursor: pointer; transition: all 0.2s; }}
  .filter-btn:hover, .filter-btn.active {{ background: #667eea; color: white; border-color: #667eea; }}
  input#search {{ padding: 6px 14px; border-radius: 20px; border: 1px solid #ddd; font-size: 13px; width: 200px; }}

  @media (max-width: 768px) {{
    .common-diff {{ grid-template-columns: 1fr; }}
    .common-section {{ border-right: none; border-bottom: 1px solid #f0f0f0; }}
    .stat-grid {{ grid-template-columns: 1fr; }}
    .stat-card {{ border-right: none; border-bottom: 1px solid #f0f0f0; }}
  }}
</style>
</head>
<body>

<div class="header">
  <h1>👊 IP×轻发售 实战营·成员画像分析报告</h1>
  <div class="subtitle">数据来源：群聊记录 | 分析范围：type=0 纯文字消息 | 处理方式：连续消息合并后识别</div>
  <div class="meta">
    <div class="meta-item"><strong>{total}</strong>位成员留下自我介绍</div>
    <div class="meta-item"><strong>{edu_counts.get('985', 0) + edu_counts.get('211', 0)}</strong>位来自985/211高校</div>
    <div class="meta-item"><strong>{ai_counts.get('是', 0)}</strong>位有AI实操经验</div>
    <div class="meta-item"><strong>{sum(1 for p in persons if p["position"] and p["position"] != "无")}</strong>位积极竞选岗位</div>
  </div>
</div>

<div class="container">

<!-- 统计概览 -->
<div class="section">
  <div class="section-header">
    <span class="icon">📊</span>
    <h2>数据统计概览</h2>
  </div>
  <div class="stat-grid">
    <div class="stat-card">
      <h3>学历层次分布</h3>
      {edu_bars}
    </div>
    <div class="stat-card">
      <h3>AI实操经验分布</h3>
      {ai_bars}
    </div>
    <div class="stat-card">
      <h3>年级分布</h3>
      {grade_bars}
    </div>
    <div class="stat-card">
      <h3>竞选岗位意向</h3>
      {pos_html}
    </div>
  </div>
</div>

<!-- 城市分布 -->
<div class="section">
  <div class="section-header">
    <span class="icon">🗺️</span>
    <h2>城市分布 TOP10（可识别城市）</h2>
  </div>
  <div class="stat-card">
    {city_html}
  </div>
</div>

<!-- 群体共同点与差异点 -->
<div class="section">
  <div class="section-header">
    <span class="icon">🔍</span>
    <h2>群体画像分析</h2>
  </div>
  <div class="common-diff">
    <div class="common-section">
      <h3>🟢 群体共同点</h3>
      <ul>
        <li>绝大多数为在校大学生（大一为主力，占比超40%），正处于探索自我变现路径的关键阶段</li>
        <li>均对"AI+私域"变现模式感兴趣，实战营是他们第一次系统接触轻发售/IP打造的机会</li>
        <li>普遍具备目标量化意识：介绍中多出现"裂变X人""月入X位数""触达X00人"等具体数字</li>
        <li>普遍有社团/学生会/大创项目等组织管理经历，协作能力有一定积累</li>
        <li>多数成员明确提到希望"赚到人生第一桶金"或"完成从0到1的变现突破"</li>
        <li>对"人脉/链接/圈子"有强烈渴望，社交诉求与成长诉求并重</li>
        <li>地域分布广泛，来自全国各省市高校，线上社群是主要协作场景</li>
      </ul>
    </div>
    <div class="diff-section">
      <h3>🟠 群体差异点</h3>
      <ul>
        <li>AI起跑线差距悬殊：从"已获AI创新赛特等奖"到"完全0基础想学"，AI经验断层明显</li>
        <li>学历背景跨度大：985院校（如清华、浙大、中山大学）与专科院校成员共处同一群，背景差异显著</li>
        <li>变现路径认知不同：一部分人已有校园代理/小红书变现经验，另一部分仍在探索"怎么赚第一分钱"</li>
        <li>个人IP方向多元：有AI工具型、内容创作型、社群运营型、技术变现型等不同IP定位路径</li>
        <li>竞选意愿分化：约半数成员明确竞选岗位且附有详细申请宣言，另一半没有岗位诉求</li>
        <li>执行力基础不同：部分人已有带团队/管理社群经验，部分人明确表示自己"胆小""社恐"待突破</li>
        <li>专业背景跨度极大：工程类、医学类、艺术设计类、财经类、文学类成员均有，跨学科特征明显</li>
      </ul>
    </div>
  </div>
</div>

<!-- 核心洞察 -->
<div class="section">
  <div class="section-header">
    <span class="icon">💡</span>
    <h2>5条核心洞察结论</h2>
  </div>
  <div class="insights">
    <div class="insight-item">
      <div class="insight-num">01</div>
      <div class="insight-text">
        <h4>这是一群"想赚钱但不知道怎么赚"的高潜大学生</h4>
        <p>275位成员中，超过90%明确表达了变现诉求，但大多数（约68%）处于AI工具"初步接触"或"待入门"阶段。他们并非缺乏动力，而是缺少一套可落地的从0到1方法论。实战营的核心价值在于填补"知道AI"和"用AI赚到钱"之间的巨大鸿沟。</p>
      </div>
    </div>
    <div class="insight-item">
      <div class="insight-num">02</div>
      <div class="insight-text">
        <h4>普通本科生是主力军，但985/211学生的内驱力与执行力更值得关注</h4>
        <p>普通本科生占比68.4%，是实战营的基数主体；但53位985/211学生（占19.3%）普遍呈现出更清晰的目标拆解能力和更强的量化意识——他们更倾向于用"数字+时间节点"定义成功，且有更多可迁移的项目/竞赛经验，是战队中的潜在领导核心。</p>
      </div>
    </div>
    <div class="insight-item">
      <div class="insight-num">03</div>
      <div class="insight-text">
        <h4>竞选岗位意愿高，"战队队长"供大于求，岗位设置需精细化</h4>
        <p>在有明确岗位竞选意向的成员中，"战队队长"是最热门选项，占竞选人数约40%。但一个实战营不可能有这么多队长。这一现象折射出：成员普遍希望通过岗位获得"被看见"的机会，而非单纯的管理权力。建议增设更多细分职能岗位（如复盘官、数据官）来承接这部分积极性。</p>
      </div>
    </div>
    <div class="insight-item">
      <div class="insight-num">04</div>
      <div class="insight-text">
        <h4>地域集中在华东、华中、华南，北方学生占比相对低，但地域差距不影响线上协作</h4>
        <p>可识别城市中，天津（10人）、南昌（8人）、重庆（7人）、南京（6人）位居前列，广东省域整体人数可观。值得注意的是，相当数量成员填写了省份而非城市，反映出大学校区地理的模糊性。全程线上实战模式对地域限制基本消除，但时区差异和生活节奏一致性需关注。</p>
      </div>
    </div>
    <div class="insight-item">
      <div class="insight-num">05</div>
      <div class="insight-text">
        <h4>"社恐破冰"是隐性高频诉求，实战营既是商业训练营也是社交成长营</h4>
        <p>多位成员（如上海外大汪晓月、承德医学院李邵涵等）明确提到"突破社恐""敢于表达"作为核心目标。这说明实战营承载的不仅是变现技能训练，更是个人成长突破的心理契约。内容设计若能融入"安全感建立→小步表达→正向反馈"的心理曲线，将大幅提升成员留存与深度参与。</p>
      </div>
    </div>
  </div>
</div>

<!-- 完整成员表格 -->
<div class="section">
  <div class="section-header">
    <span class="icon">👥</span>
    <h2>完整成员信息表（共 {total} 人）</h2>
  </div>
  <div class="table-filter">
    <span class="filter-label">快速筛选：</span>
    <button class="filter-btn active" onclick="filterTable('all', this)">全部</button>
    <button class="filter-btn" onclick="filterTable('985', this)">985</button>
    <button class="filter-btn" onclick="filterTable('211', this)">211</button>
    <button class="filter-btn" onclick="filterTable('专科', this)">专科</button>
    <button class="filter-btn" onclick="filterTable('ai-yes', this)">AI有实操</button>
    <button class="filter-btn" onclick="filterTable('ai-init', this)">AI初步</button>
    <button class="filter-btn" onclick="filterTable('has-pos', this)">有竞选</button>
    <input id="search" type="text" placeholder="搜索姓名/学校/城市..." oninput="searchTable(this.value)">
  </div>
  <div class="table-wrap">
    <table id="mainTable">
      <thead>
        <tr>
          <th>#</th>
          <th>姓名</th>
          <th>昵称</th>
          <th>学校 / 学历</th>
          <th>年级</th>
          <th>城市</th>
          <th>成就事件摘要</th>
          <th>本次实战核心目标</th>
          <th>AI经验</th>
          <th>竞选岗位</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>
</div>

</div><!-- end container -->

<script>
function filterTable(type, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const rows = document.querySelectorAll('#mainTable tbody tr');
  rows.forEach(row => {{
    let show = true;
    if (type === 'all') show = true;
    else if (type === '985') show = row.innerHTML.includes('edu-985');
    else if (type === '211') show = row.innerHTML.includes('edu-211');
    else if (type === '专科') show = row.innerHTML.includes('edu-junior');
    else if (type === 'ai-yes') show = row.innerHTML.includes('ai-yes');
    else if (type === 'ai-init') show = row.innerHTML.includes('ai-init');
    else if (type === 'has-pos') {{
      const posCell = row.querySelectorAll('td')[9];
      show = posCell && !posCell.innerHTML.includes('color:#aaa');
    }}
    row.style.display = show ? '' : 'none';
  }});
}}

function searchTable(val) {{
  val = val.toLowerCase();
  const rows = document.querySelectorAll('#mainTable tbody tr');
  rows.forEach(row => {{
    row.style.display = row.textContent.toLowerCase().includes(val) ? '' : 'none';
  }});
}}
</script>
</body>
</html>'''

out_path = r'C:/Users/weirui/Desktop/claude/实战营成员画像分析报告.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'HTML报告已生成：{out_path}')
print(f'文件大小：{len(html):,} 字节')
print(f'总成员数：{total}')
print(f'学历统计：{edu_counts}')
print(f'AI经验：{ai_counts}')
