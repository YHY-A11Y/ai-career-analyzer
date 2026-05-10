import streamlit as st
import urllib.request
import json
import os
import hashlib
from datetime import datetime

API_KEY = st.secrets["API_KEY"]

# 文件路径
用户文件 = "users.json"
历史文件 = "history.json"

# ===== 用户系统 =====
def 加密密码(密码):
    return hashlib.sha256(密码.encode()).hexdigest()

def 读取用户():
    if os.path.exists(用户文件):
        with open(用户文件, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def 保存用户(用户数据):
    with open(用户文件, "w", encoding="utf-8") as f:
        json.dump(用户数据, f, ensure_ascii=False, indent=2)

def 注册(用户名, 密码):
    用户数据 = 读取用户()
    if 用户名 in 用户数据:
        return False, "用户名已存在！"
    用户数据[用户名] = {
        "密码": 加密密码(密码),
        "注册时间": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    保存用户(用户数据)
    return True, "注册成功！"

def 登录(用户名, 密码):
    用户数据 = 读取用户()
    if 用户名 not in 用户数据:
        return False, "用户名不存在！"
    if 用户数据[用户名]["密码"] != 加密密码(密码):
        return False, "密码错误！"
    return True, "登录成功！"

# ===== 历史记录 =====
def 读取历史(用户名):
    if os.path.exists(历史文件):
        with open(历史文件, "r", encoding="utf-8") as f:
            全部历史 = json.load(f)
            return [h for h in 全部历史 if h.get("用户") == 用户名]
    return []

def 保存历史(用户名, 名字, 年龄, 技能, 行业, 结果):
    全部历史 = []
    if os.path.exists(历史文件):
        with open(历史文件, "r", encoding="utf-8") as f:
            全部历史 = json.load(f)
    全部历史.append({
        "用户": 用户名,
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "姓名": 名字,
        "年龄": 年龄,
        "技能": 技能,
        "行业": 行业,
        "分析": 结果
    })
    with open(历史文件, "w", encoding="utf-8") as f:
        json.dump(全部历史, f, ensure_ascii=False, indent=2)

# ===== AI分析 =====
def AI职业分析(名字, 年龄, 技能, 行业):
    提示词 = f"""
    请用中文分析以下用户的职业发展建议：
    姓名：{名字}，年龄：{年龄}，技能：{技能}，目标行业：{行业}
    
    请给出：
    1. 优势分析
    2. 当前最大的挑战
    3. 未来6个月的具体行动计划
    4. 适合的AI创业方向
    
    最后单独输出JSON（不要加代码块）：
    {{"技能匹配度": 85, "市场需求": 90, "创业潜力": 75, "发展速度": 80}}
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
        return json.loads(文本[start:end])
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

# ===== 登录/注册界面 =====
def 显示登录界面():
    st.title("🤖 AI职业分析器")
    st.write("请登录或注册以继续使用")
    
    tab登录, tab注册 = st.tabs(["🔑 登录", "📝 注册"])
    
    with tab登录:
        用户名 = st.text_input("用户名", key="login_user")
        密码 = st.text_input("密码", type="password", key="login_pass")
        if st.button("登录", use_container_width=True, key="login_btn"):
            if 用户名 and 密码:
                成功, 消息 = 登录(用户名, 密码)
                if 成功:
                    st.session_state.已登录 = True
                    st.session_state.当前用户 = 用户名
                    st.rerun()
                else:
                    st.error(消息)
            else:
                st.warning("请填写用户名和密码！")
    
    with tab注册:
        新用户名 = st.text_input("用户名", key="reg_user")
        新密码 = st.text_input("密码", type="password", key="reg_pass")
        确认密码 = st.text_input("确认密码", type="password", key="reg_pass2")
        if st.button("注册", use_container_width=True, key="reg_btn"):
            if 新用户名 and 新密码 and 确认密码:
                if 新密码 != 确认密码:
                    st.error("两次密码不一致！")
                elif len(新密码) < 6:
                    st.error("密码至少6位！")
                else:
                    成功, 消息 = 注册(新用户名, 新密码)
                    if 成功:
                        st.success("注册成功！请登录")
                    else:
                        st.error(消息)
            else:
                st.warning("请填写所有信息！")

# ===== 主程序 =====
st.markdown("""
<style>
.stButton > button {
    background: linear-gradient(90deg, #6C63FF, #3ECFCF);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

if "已登录" not in st.session_state:
    st.session_state.已登录 = False

if not st.session_state.已登录:
    显示登录界面()
else:
    用户名 = st.session_state.当前用户
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🤖 AI职业分析器")
    with col2:
        st.write(f"👤 {用户名}")
        if st.button("退出"):
            st.session_state.已登录 = False
            st.rerun()

    tab1, tab2 = st.tabs(["📝 开始分析", "📋 历史记录"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            名字 = st.text_input("姓名")
            技能 = st.text_input("技能")
        with col2:
            年龄 = st.text_input("年龄")
            行业 = st.text_input("目标行业")

        if st.button("开始分析 🚀", use_container_width=True):
            if 名字 and 年龄 and 技能 and 行业:
                with st.spinner("AI正在分析，请稍等..."):
                    try:
                        结果 = AI职业分析(名字, 年龄, 技能, 行业)
                        保存历史(用户名, 名字, 年龄, 技能, 行业, 结果)
                        st.success(f"✅ {名字}的分析报告生成完成！")
                        评分 = 解析评分(结果)
                        显示评分(评分)
                        st.divider()
                        st.write("### 📋 详细分析")
                        文字部分 = 结果[:结果.rfind("{")]
                        st.markdown(文字部分)
                    except Exception as e:
                        st.error(f"连接失败：{e}")
            else:
                st.warning("请填写所有信息！")

    with tab2:
        st.write("### 我的历史记录")
        历史 = 读取历史(用户名)
        if not 历史:
            st.info("还没有历史记录！")
        else:
            st.write(f"共分析了 **{len(历史)}** 次")
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