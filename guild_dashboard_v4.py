import streamlit as st
import pandas as pd
import json
import os

# 設定網頁標題與排版
st.set_page_config(page_title="公會資訊管理系統 v4", page_icon="⚔️", layout="wide")

DB_FILE = "guild_members_v3.json"
ADMIN_PASSWORD = "11234"  # 💡 請在這裡修改你想要的幹部密碼

# --- 定義遊戲職業選項 ---
JOB_OPTIONS = [
    "制裁者", "幻影神兵", "執行者", "操靈師", 
    "無畏艦", "匠師", "仲裁者", "毀滅"
]

# --- 函式：讀取與儲存 JSON 資料 ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
    ]

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初始化 Session State
if "guild_list" not in st.session_state:
    st.session_state.guild_list = load_data()

st.title("⚔️ 公會資訊自動化管理與即時更新系統 v4")

# ==========================================
# 🔑 權限控制中心 (開放瀏覽權限)
# ==========================================
st.sidebar.title("🔐 訪問權限驗證")
role_choice = st.sidebar.radio("選擇您的身分：", ["一般成員 (僅限瀏覽)", "公會幹部 (可更新資訊)"])

is_admin = False
if role_choice == "公會幹部 (可更新資訊)":
    password_input = st.sidebar.text_input("請輸入管理密碼：", type="password")
    if password_input == ADMIN_PASSWORD:
        st.sidebar.success("🔑 密碼正確！已解鎖更新權限。")
        is_admin = True
    elif password_input != "":
        st.sidebar.error("❌ 密碼錯誤，請重新輸入。")
else:
    st.sidebar.info("ℹ️ 當前為「一般成員瀏覽模式」，無法修改內容。")

# ==========================================
# 📝 區域一：資料維護管理（僅限幹部模式顯示）
# ==========================================
if is_admin:
    st.subheader("📝 成員與多重職業資料隨時更新 (幹部專區)")
    
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = -1

    if st.session_state.edit_index != -1:
        current_item = st.session_state.guild_list[st.session_state.edit_index]
        default_name = current_item["角色名稱"]
        default_jobs = [j for j in current_item["職業"] if j in JOB_OPTIONS] if isinstance(current_item["職業"], list) else []
        default_power = int(current_item["戰力"])
        default_gear = current_item["裝備"]
        button_label = "💾 儲存修改資訊"
    else:
        default_name = ""
        default_jobs = []
        default_power = 0
        default_gear = ""
        button_label = "➕ 新增公會成員"

    with st.form(key="member_form_v4", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4) 
        with col1:
            name_input = st.text_input("角色名稱", value=default_name)
        with col2:
            jobs_input = st.multiselect("職業選項 (可多選)", options=JOB_OPTIONS, default=default_jobs)
        with col3:
            power_input = st.number_input("目前戰力", min_value=0, step=1000, value=default_power)
        with col4:
            gear_input = st.text_input("核心裝備描述", value=default_gear, placeholder="例如：天神之翼 +15")
        
        submit_button = st.form_submit_button(label=button_label, type="primary")

    if submit_button:
        if not name_input.strip():
            st.error("❌ 角色名稱不能為空！")
        elif not jobs_input:
            st.error("❌ 請至少選擇一個職業！")
        else:
            new_member = {"角色名稱": name_input.strip(), "職業": jobs_input, "戰力": power_input, "裝備": gear_input}
            
            if st.session_state.edit_index == -1:
                st.session_state.guild_list.append(new_member)
                st.toast(f"✅ 已成功新增成員：{name_input}")
            else:
                st.session_state.guild_list[st.session_state.edit_index] = new_member
                st.toast(f"🔄 已成功更新成員：{name_input}")
                st.session_state.edit_index = -1
                
            save_data(st.session_state.guild_list)
            st.rerun()

    if st.session_state.edit_index != -1:
        if st.button("❌ 取消修改"):
            st.session_state.edit_index = -1
            st.rerun()

# ==========================================
# 📊 區域二：自動化整理與即時排行榜（全權限開放瀏覽）
# ==========================================
st.subheader("📊 自動化整理：最新戰力排行榜")

if st.session_state.guild_list:
    df = pd.DataFrame(st.session_state.guild_list)
    df = df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
    df["排名"] = df.index + 1
    df["戰力(排名)"] = df.apply(lambda r: f"{int(r['戰力']):,} (#{r['排名']})", axis=1)
    df["職業顯示"] = df["職業"].apply(lambda x: "、".join(x) if isinstance(x, list) else x)
    
    display_df = df[["排名", "角色名稱", "職業顯示", "戰力(排名)", "裝備"]]
    display_df.columns = ["排名", "角色名稱", "職業", "戰力(排名)", "裝備"]
    
    # 所有人打開網頁都能直接看見這個排行榜表格！
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # ==========================================
    # 🔧 區域三：操作快捷鍵（僅限幹部模式顯示）
    # ==========================================
    if is_admin:
        st.write("🔧 **成員管理快捷鍵：**")
        for idx, row in df.iterrows():
            orig_idx = next(i for i, x in enumerate(st.session_state.guild_list) if x["角色名稱"] == row["角色名稱"])
            
            c1, col_space, c2, c3 = st.columns([6, 2, 1, 1]) # 調優按鈕對齊
            with c1:
                st.write(f"【#{row['排名']}】 **{row['角色名稱']}** ｜ 職業：`{row['職業顯示']}` ｜ (戰力: {int(row['戰力']):,})")
            with c2:
                if st.button("✏️ 修改", key=f"edit_{orig_idx}"):
                    st.session_state.edit_index = orig_idx
                    st.rerun()
            with c3:
                if st.button("🗑️ 刪除", key=f"del_{orig_idx}"):
                    del st.session_state.guild_list[orig_idx]
                    save_data(st.session_state.guild_list)
                    st.toast(f"🗑️ 已刪除成員資訊")
                    st.rerun()
else:
    st.info("目前公會暫無成員資訊。")
