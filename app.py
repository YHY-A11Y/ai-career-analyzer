import streamlit as st
import urllib.request
import json

API_KEY = "AIzaSyDQh62ieTFXv-4dAPnnpynyej7Fgms0_0Y"

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
                st.success("分析完成！")
                st.markdown(结果)
            except Exception as e:
                st.error(f"连接失败：{e}")
    else:
        st.warning("请填写所有信息！")