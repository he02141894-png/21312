import streamlit as st
import pandas as pd
import json
import os

# 設定網頁標題與排版
st.set_page_config(page_title="公會資訊管理系統 v5", page_icon="⚔️", layout="wide")

DB_FILE = "guild_members_v3.json"

# ==========================================
# 🔑 密碼隱藏安全機制 (從 Streamlit 雲端保險箱讀取)
# ==========================================
# 如果是在本地測試，可以在程式碼同目錄下建立 .streamlit/secrets.toml
# 內容寫入：
# job_password = "job123"
# admin_password = "admin123"
JOB_PASSWORD = st.secrets.get("job_password", "job123")      # 💡 職業維護專用密碼
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")  # 💡 最高幹部管理密碼

# --- 定義遊戲職業選項 ---
JOB_OPTIONS = [
    "狂戰士", "聖騎士", "暗殺者", "神射手", 
    "大賢者", "死靈法師", "魔劍士", "吟遊詩人"
]

# --- 函式：讀取與儲存 JSON 資料 ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [
        {"角色名稱": "傲視群雄_X", "職業": ["狂戰士", "魔劍士"], "戰力": 1250000, "裝備": "天神之翼 +15, 不滅聖劍 +15"},
        {"角色名稱": "影之刃_凱", "職業": ["暗殺者"], "戰力": 1180000, "裝備": "弒神雙刃 +15, 夜幕皮甲 +14"}
    ]

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初始化 Session State
if "guild_list" not in st.session_state:
    st.session_state.guild_list = load_data()

st.title("⚔️ 公會資訊自動化管理系統 v5 (職權分離安全版)")

# ==========================================
# 🔐 權限控制中心 (三階段身分切換)
# ==========================================
st.sidebar.title("🔐 身分與權限驗證")
role_choice = st.sidebar.radio(
    "請選擇您的存取權限：", 
    ["一般成員 (僅限瀏覽)", "職業負責人 (僅限變更職業)", "最高幹部 (擁有全部權限)"]
)

is_admin = False
is_job_updater = False

if role_choice == "最高幹部 (擁有全部權限)":
    pwd = st.sidebar.text_input("請輸入最高管理密碼：", type="password", key="admin_pwd")
    if pwd == ADMIN_PASSWORD:
        st.sidebar.success("👑 最高權限已解鎖！")
        is_admin = True
    elif pwd != "":
        st.sidebar.error("❌ 密碼錯誤！")

elif role_choice == "職業負責人 (僅限變更職業)":
    pwd = st.sidebar.text_input("請輸入職業專用密碼：", type="password", key="job_pwd")
    if pwd == JOB_PASSWORD:
        st.sidebar.success("🛡️ 職業修改權限已解鎖！")
        is_job_updater = True
    elif pwd != "":
        st.sidebar.error("❌ 密碼錯誤！")
else:
    st.sidebar.info("ℹ️ 當前為「公開瀏覽模式」。")


# ==========================================
# 📝 權限 A：最高幹部專屬區（新增成員與全面修改）
# ==========================================
if is_admin:
    st.subheader("📝 成員全面資料維護 (最高幹部專區)")
    
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

    with st.form(key="admin_member_form", clear_on_submit=True):
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
# 📝 權限 B：職業負責人專屬區（單獨開放職業權限）
# ==========================================
elif is_job_updater:
    st.subheader("🛡️ 職業標籤即時更新 (職業負責人專區)")
    st.caption("💡 在此模式下，您只能調整成員的職業設定，無法修改角色名稱、戰力、裝備或刪除隊員。")
    
    # 建立一個簡便的單獨修改職業表單
    member_names = [m["角色名稱"] for m in st.session_state.guild_list]
    
    if member_names:
        with st.form(key="job_only_form"):
            c_select, c_job = st.columns(2)
            with c_select:
                selected_name = st.selectbox("請選擇要更新職業的角色：", options=member_names)
            
            # 抓出該角色目前的職業作為預設值
            target_idx = next(i for i, x in enumerate(st.session_state.guild_list) if x["角色名稱"] == selected_name)
            current_jobs = st.session_state.guild_list[target_idx].get("職業", [])
            
            with c_job:
                updated_jobs = st.multiselect("重新設定該角色的職業 (可複選)：", options=JOB_OPTIONS, default=current_jobs)
                
            job_submit = st.form_submit_button("💾 僅儲存職業變更", type="primary")
            
        if job_submit:
            if not updated_jobs:
                st.error("❌ 角色至少需要保留一個職業！")
            else:
                st.session_state.guild_list[target_idx]["職業"] = updated_jobs
                save_data(st.session_state.guild_list)
                st.success(f"✅ 成功更新【{selected_name}】的職業資訊！")
                st.rerun()
    else:
        st.info("目前系統內無成員資料可供修改。")


# ==========================================
# 📊 核心排行榜（全權限開放瀏覽，內建職業篩選器）
# ==========================================
st.subheader("📊 自動化整理：最新戰力排行榜")

if st.session_state.guild_list:
    df = pd.DataFrame(st.session_state.guild_list)
    df = df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
    df["排名"] = df.index + 1
    
    # 📊 貼心小功能：開放所有人使用的「職業公開篩選器」
    filter_job = st.selectbox("🔍 依職業篩選排行榜 (可選填)：", ["顯示全部職業"] + JOB_OPTIONS)
    if filter_job != "顯示全部職業":
        # 篩選出列表中有包含該職業的列
        df = df[df["職業"].apply(lambda x: filter_job in x if isinstance(x, list) else False)].reset_index(drop=True)
        # 重新計算篩選後的局部排名
        df["排名"] = df.index + 1

    df["戰力(排名)"] = df.apply(lambda r: f"{int(r['戰力']):,} (#{r['排名']})", axis=1)
    df["職業顯示"] = df["職業"].apply(lambda x: "、".join(x) if isinstance(x, list) else x)
    
    display_df = df[["排名", "角色名稱", "職業顯示", "戰力(排名)", "裝備"]]
    display_df.columns = ["排名", "角色名稱", "職業", "戰力(排名)", "裝備"]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # ==========================================
    # 🔧 快捷管理鍵（僅限最高幹部顯示）
    # ==========================================
    if is_admin:
        st.write("🔧 **最高幹部管理快捷鍵：**")
        for idx, row in df.iterrows():
            orig_idx = next(i for i, x in enumerate(st.session_state.guild_list) if x["角色名稱"] == row["角色名稱"])
            
            c1, col_space, c2, c3 = st.columns()
            with c1:
                st.write(f"【#{row['排名']}】 **{row['角色名稱']}** ｜ 職業：`{row['職業顯示']}` ｜ (戰力: {int(row['戰力']):,})")
            with c2:
                if st.button("✏️ 全面修改", key=f"edit_{orig_idx}"):
                    st.session_state.edit_index = orig_idx
                    st.rerun()
            with c3:
                if st.button("🗑️ 刪除成員", key=f"del_{orig_idx}"):
                    del st.session_state.guild_list[orig_idx]
                    save_data(st.session_state.guild_list)
                    st.toast(f"🗑️ 已刪除成員資訊")
                    st.rerun()
else:
    st.info("目前公會暫無成員資訊。")
