import streamlit as st
import pandas as pd
import json
import os

# 設定網頁標題與排版
st.set_page_config(page_title="公會資訊管理系統 v14", page_icon="⚔️", layout="wide")

DB_FILE = "guild_members_v7.json"  # 💡 更新職業規格，使用全新乾淨的資料庫防止與舊檔案結構衝突

# ==========================================
# 🔑 密碼隱藏安全機制
# ==========================================
JOB_PASSWORD = st.secrets.get("job_password", "job123")      # 💡 職業維護專用密碼
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")  # 💡 最高幹部管理密碼

# --- 💡【職業體系全面正名】精準定義你要求的 8 大核心職業選項 ---
JOB_OPTIONS = [
    "制裁者", "幻影神兵", "執行者", "操靈師", 
    "無畏艦", "匠師", "仲裁者", "毀滅"
]

# --- 定義 16 格裝備欄位 ---
GEAR_FIELDS = [
    "主武", "二武", "三武", "四武", 
    "頸部", "上身", "手臂", "下身", 
    "腿部", "頭冠", "耳環", "項鍊", 
    "手環","戒指", "驅動器", "觀測儀", 
    "偏轉器"
]

# --- 函式：讀取與儲存 JSON 資料 ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 建立全新職業與 16 格裝備的初始預設資料
    default_gears = {field: "無" for field in GEAR_FIELDS}
    default_gears["主武"] = "究極終焉劍 +15"
    default_gears["二武"] = "弒神之刃 +14"
    default_gears["驅動器"] = "量子核心 Mk-III"
    return [
        {"角色名稱": "傲視群雄_X", "職業": ["制裁者", "毀滅"], "戰力": 1250000, "裝備": default_gears},
        {"角色名稱": "影之刃_凱", "職業": ["幻影神兵"], "戰力": 1180000, "裝備": {field: "無" for field in GEAR_FIELDS}}
    ]

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初始化 Session State
if "guild_list" not in st.session_state:
    st.session_state.guild_list = load_data()

st.title("⚔️ 公會資訊自動化管理系統 v14 (全新八大職業正名版)")

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
    st.sidebar.info("ℹ️ 當前為「公開瀏覽模式」，前五名大佬的戰力已被單獨遮蔽。")


# ==========================================
# 📝 權限 A：最高幹部專屬區 (全面資料維護)
# ==========================================
if is_admin:
    st.subheader("📝 成員全面資料維護 (最高幹部專區)")
    
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = -1

    if st.session_state.edit_index != -1:
        current_item = st.session_state.guild_list[st.session_state.edit_index]
        default_name = current_item["角色名稱"]
        
        raw_jobs = current_item.get("職業", [])
        if isinstance(raw_jobs, str):
            raw_jobs = [raw_jobs]
        default_jobs = [j for j in raw_jobs if j in JOB_OPTIONS]
        
        default_power = int(current_item["戰力"])
        saved_gears = current_item.get("裝備", {})
        if isinstance(saved_gears, str):
            saved_gears = {"主武": saved_gears}
        default_gears = {field: saved_gears.get(field, "無") for field in GEAR_FIELDS}
        button_label = "💾 儲存修改資訊"
    else:
        default_name = ""
        default_jobs = []
        default_power = 0
        default_gears = {field: "無" for field in GEAR_FIELDS}
        button_label = "➕ 新增公會成員"

    with st.form(key="admin_member_form", clear_on_submit=True):
        st.markdown("##### 📌 基礎基本資訊")
        col1, col2, col3 = st.columns(3)
        with col1:
            name_input = st.text_input("角色名稱", value=default_name)
        with col2:
            jobs_input = st.multiselect("職業選項 (可多選)", options=JOB_OPTIONS, default=default_jobs)
        with col3:
            power_input = st.number_input("目前戰力", min_value=0, step=1000, value=default_power)
        
        st.write("---")
        st.markdown("##### 🛡️ 16 格核心裝備細項面板")
        
        gear_inputs = {}
        st.markdown("**第一組：武器**")
        g_col1, g_col2, g_col3, g_col4 = st.columns(4)
        with g_col1:
            gear_inputs["主武"] = st.text_input("主武", value=default_gears["主武"])
        with g_col2:
            gear_inputs["二武"] = st.text_input("二武", value=default_gears["二武"])
        with g_col3:
            gear_inputs["三武"] = st.text_input("三武", value=default_gears["三武"])
        with g_col4:
            gear_inputs["四武"] = st.text_input("四武", value=default_gears["四武"])

        st.markdown("**第二組：防具**")
        g_col5, g_col6, g_col7, g_col8, g_col9 = st.columns(5)
        with g_col5:
            gear_inputs["頸部"] = st.text_input("頸部", value=default_gears["頸部"])
        with g_col6:
            gear_inputs["上身"] = st.text_input("上身", value=default_gears["上身"])
        with g_col7:
            gear_inputs["手臂"] = st.text_input("手臂", value=default_gears["手臂"])
        with g_col8:
            gear_inputs["下身"] = st.text_input("下身", value=default_gears["下身"])
        with g_col9:
            gear_inputs["腿部"] = st.text_input("腿部", value=default_gears["腿部"])

        st.markdown("**第三組：飾品**")
        g_co20, g_co21, g_co22, g_co23, g_co24 = st.columns(5)
        with g_co20:
            gear_inputs["頭冠"] = st.text_input("頭冠", value=default_gears["頭冠"])
        with g_co21:
            gear_inputs["耳環"] = st.text_input("耳環", value=default_gears["耳環"])
        with g_co22:
            gear_inputs["項鍊"] = st.text_input("項鍊", value=default_gears["項鍊"])
        with g_co23:
            gear_inputs["手環"] = st.text_input("手環", value=default_gears["手環"])
        with g_co24:
            gear_inputs["戒指"] = st.text_input("戒指", value=default_gears["戒指"])

        st.markdown("**第三組：擴充**")
        g_co25, g_co26, g_co27= st.columns(3)
        with g_co25:
            gear_inputs["驅動器"] = st.text_input("驅動器", value=default_gears["驅動器"])
        with g_co26:
            gear_inputs["觀測儀"] = st.text_input("觀測儀", value=default_gears["觀測儀"])
        with g_co27:
            gear_inputs["偏轉器"] = st.text_input("偏轉器", value=default_gears["偏轉器"])
        
        submit_button = st.form_submit_button(label=button_label, type="primary")

    if submit_button:
        if not name_input.strip():
            st.error("❌ 角色名稱不能為空！")
        elif not jobs_input:
            st.error("❌ 請至少選擇一個職業！")
        else:
            new_member = {
                "角色名稱": name_input.strip(), 
                "職業": jobs_input, 
                "戰力": power_input, 
                "裝備": gear_inputs
            }
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
# 📝 權限 B：職業負責人專屬區
# ==========================================
elif is_job_updater:
    st.subheader("🛡️ 職業標籤即時更新 (職業負責人專區)")
    st.caption("💡 提示：此模式下您可以修改【全公會所有人】的職業，但無法更動或看見前五名的戰力。")
    
    member_names = [m["角色名稱"] for m in st.session_state.guild_list]
    
    if member_names:
        with st.form(key="job_only_form"):
            c_select, c_job = st.columns(2) 
            with c_select:
                selected_name = st.selectbox("請選擇要更新職業的角色：", options=member_names)
            
            target_idx = next(i for i, x in enumerate(st.session_state.guild_list) if x["角色名稱"] == selected_name)
            raw_current_jobs = st.session_state.guild_list[target_idx].get("職業", [])
            if isinstance(raw_current_jobs, str):
                raw_current_jobs = [raw_current_jobs]
            valid_current_jobs = [j for j in raw_current_jobs if j in JOB_OPTIONS]
            
            with c_job:
                updated_jobs = st.multiselect("重新設定該角色的職業 (可複選)：", options=JOB_OPTIONS, default=valid_current_jobs)
                
            job_submit = st.form_submit_button("💾 僅儲存職業變更", type="primary")
            
        if job_submit:
            if not updated_jobs:
                st.error("❌ 角色至少需要保留一個職業！")
            else:
                st.session_state.guild_list[target_idx]["職業"] = updated_jobs
                save_data(st.session_state.guild_list)
                st.success(f"✅ 成功更新【{selected_name}】的職業資訊！")
                st.rerun()


# ==========================================
# 📊 核心排行榜 (自動對齊最新職業)
# ==========================================
st.subheader("📊 自動化整理：最新公會全裝備名單")

if st.session_state.guild_list:
    df = pd.DataFrame(st.session_state.guild_list)
    df = df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
    df["真實排名"] = df.index + 1
    
    df["職業顯示"] = df["職業"].apply(lambda x: "、".join(x) if isinstance(x, list) else (x if pd.notna(x) else "未設定"))

    # 🔒 戰力精準遮蔽前五名
    if not is_admin:
        st.warning("🔒 戰力安全防護：目前權限下，系統已自動遮蔽公會前 5名 大佬的【戰力數字】與【真實排名】。")
        df["戰力(排名)"] = df.apply(
            lambda r: f"🔒 資訊保密" if r["真實排名"] <= 5 else f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1
        )
        df["排名顯示"] = df["真實排名"].apply(lambda x: "🎖️ 大佬" if x <= 5 else str(x))
    else:
        df["戰力(排名)"] = df.apply(lambda r: f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1)
        df["排名顯示"] = df["真實排名"].astype(str)

    # 展開 16 格裝備字典
    for field in GEAR_FIELDS:
        df[field] = df["裝備"].apply(lambda x: x.get(field, "無") if isinstance(x, dict) else "無")

    display_cols = ["排名顯示", "角色名稱", "職業顯示", "戰力(排名)"] + GEAR_FIELDS
    display_df = df[display_cols]
    
    rename_dict = {"排名顯示": "排名", "職業顯示": "職業", "戰力(排名)": "戰力(排名)"}
    display_df = display_df.rename(columns=rename_dict)
    
    # 🔍 全體職業篩選器（💡 自動與最新制裁者、幻影神兵等選單對齊）
filter_job = st.selectbox("🔍 依職業篩選現有排行榜 (可選填)：", ["顯示全部職業"] + JOB_OPTIONS)
if filter_job != "顯示全部職業":
    # 💡 請在這一行的最前面，手動補上 4 個英文空格（或者刪掉原本的空白，按一下 Tab 鍵）！
    display_df = display_df[display_df["職業"].apply(lambda x: filter_job in x if isinstance(x, str) else False)].reset_index(drop=True)

