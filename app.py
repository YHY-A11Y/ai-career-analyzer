import streamlit as st
import urllib.request
import json
import os
from datetime import datetime

API_KEY = st.secrets["API_KEY"]

# 历史记录文件
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
    请用中文分析以下用户的职业发展建议：
    姓名：{名字}
    年龄：{年龄}
    技能：{技能}
    目标行业：{行业}
    
    请给出：
    1. 优势分析
    2. 当前最大的挑战
    3. 未来6个月的具体行动计划
    4. 适合的AI创业方向
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    data = json.dumps({
        "contents": [{"parts": [{"text": 提示词}]}]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["candidates"][0]["content"]["parts"][0]["text"]

# 网页界面
st.title("🤖 AI职业分析器")

# 两个标签页
tab1, tab2 = st.tabs(["📝 开始分析", "📋 历史记录"])

with tab1:
    st.write("输入你的信息，获取专属职业发展建议！")
    名字 = st.text_input("姓名")
    年龄 = st.text_input("年龄")
    技能 = st.text_input("技能（如：数据科学、编程、设计）")
    行业 = st.text_input("目标行业（如：AI创业、金融、教育）")

    if st.button("开始分析 🚀"):
        if 名字 and 年龄 and 技能 and 行业:
            with st.spinner("AI正在分析，请稍等..."):
                try:
                    结果 = AI职业分析(名字, 年龄, 技能, 行业)
                    保存历史(名字, 年龄, 技能, 行业, 结果)
                    st.success("分析完成！")
                    st.markdown(结果)
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
        for 记录 in reversed(历史):
            with st.expander(f"🧑 {记录['姓名']} | {记录['时间']}"):
                st.write(f"**年龄：** {记录['年龄']}")
                st.write(f"**技能：** {记录['技能']}")
                st.write(f"**行业：** {记录['行业']}")
                st.markdown(记录['分析'])