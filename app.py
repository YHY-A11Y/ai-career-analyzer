import streamlit as st
import urllib.request
import json
import os
from datetime import datetime

API_KEY = st.secrets["API_KEY"]

历史文件 = "history.json"

def 读取历史():
    if os.path.exists(历史文件):
        with open(历史文件, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def 保存历史(名字, 年龄, 技能, 行业, 结果):
    历史 = 读取历史()
    历史.append({
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "姓名": 名字,
        "年龄": 年龄,
        "技能": 技能,
        "行业": 行业,
        "分析": 结果
    })
    with open(历史文件, "w", encoding="utf-8") as f:
        json.dump(历史, f, ensure_ascii=False, indent=2)

def AI职业分析(名字, 年龄, 技能, 行业):
    提示词 = f"""
    请用中文分析以下用户的职业发展建议，并在最后用JSON格式输出评分：
    姓名：{名字}
    年龄：{年龄}
    技能：{技能}
    目标行业：{行业}
    
    请给出：
    1. 优势分析
    2. 当前最大的挑战
    3. 未来6个月的具体行动计划
    4. 适合的AI创业方向
    
    最后在文章末尾单独输出以下JSON（不要加代码块）：
    {{"技能匹配度": 85, "市场需求": 90, "创业潜力": 75, "发展速度": 80}}
    数字根据实际分析给出0-100的分数。
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    data = json.dumps({
        "contents": [{"parts": [{"text": 提示词}]}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]

def 解析评分(文本):
    try:
        start = 文本.rfind("{")
        end = 文本.rfind("}") + 1
        json_str = 文本[start:end]
        return json.loads(json_str)
    except:
        return {"技能匹配度": 80, "市场需求": 75, "创业潜力": 70, "发展速度": 75}

def 显示评分(评分):
    st.write("### 📊 综合评分")
    col1, col2 = st.columns(2)
    items = list(评分.items())
    for i, (指标, 分数) in enumerate(items):
        with col1 if i % 2 == 0 else col2:
            st.metric(指标, f"{分数}分")
            st.progress(分数 / 100)

# 网页界面
st.title("🤖 AI职业分析器")

tab1, tab2 = st.tabs(["📝 开始分析", "📋 历史记录"])

with tab1:
    st.write("输入你的信息，获取专属职业发展建议！")
    
    col1, col2 = st.columns(2)
    with col1:
        名字 = st.text_input("姓名")
        技能 = st.text_input("技能（如：数据科学、编程）")
    with col2:
        年龄 = st.text_input("年龄")
        行业 = st.text_input("目标行业（如：AI创业、金融）")

    if st.button("开始分析 🚀", use_container_width=True):
        if 名字 and 年龄 and 技能 and 行业:
            with st.spinner("AI正在分析，请稍等..."):
                try:
                    结果 = AI职业分析(名字, 年龄, 技能, 行业)
                    保存历史(名字, 年龄, 技能, 行业, 结果)
                    st.success(f"✅ {名字}的分析报告生成完成！")
                    
                    # 显示评分图表
                    评分 = 解析评分(结果)
                    显示评分(评分)
                    
                    st.divider()
                    st.write("### 📋 详细分析")
                    # 去掉末尾JSON部分只显示文字
                    文字部分 = 结果[:结果.rfind("{")]
                    st.markdown(文字部分)
                    
                except Exception as e:
                    st.error(f"连接失败：{e}")
        else:
            st.warning("请填写所有信息！")

with tab2:
    st.write("### 历史分析记录")
    历史 = 读取历史()
    if not 历史:
        st.info("还没有历史记录，去分析第一个人吧！")
    else:
        st.write(f"共分析了 **{len(历史)}** 个人")
        for 记录 in reversed(历史):
            with st.expander(f"🧑 {记录['姓名']} | {记录['时间']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**年龄：** {记录['年龄']}")
                    st.write(f"**技能：** {记录['技能']}")
                with col2:
                    st.write(f"**行业：** {记录['行业']}")
                st.divider()
                st.markdown(记录['分析'])