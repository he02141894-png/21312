import streamlit as st
import pandas as pd
import json
import os

# 設定網頁標題與排版
st.set_page_config(page_title="公會資訊管理系統 v11", page_icon="⚔️", layout="wide")

DB_FILE = "guild_members_v4.json"  # 升級裝備結構，更換資料庫檔名避免衝突

# ==========================================
# 🔑 密碼隱藏安全機制
# ==========================================
JOB_PASSWORD = st.secrets.get("job_password", "job123")      # 💡 職業維護專用密碼
ADMIN_PASSWORD = st.secrets.get("admin_password", "admin123")  # 💡 最高幹部管理密碼

# --- 定義遊戲職業選項 ---
JOB_OPTIONS = [
    "制裁者", "幻影神兵", "執行者", "操靈師", 
    "無畏艦", "匠師", "仲裁者", "毀滅"
]

# --- 定義 16 格裝備欄位 ---
GEAR_FIELDS = [
"主武器","副武器"
"頸部","上身","下身","腿部","護腿",
"頭冠","耳環","項鍊","手環","戒指"
"驅動器","觀測儀","偏轉器"
]

# --- 函式：讀取與儲存 JSON 資料 ---
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 預設初始資料 (改為 16 格字典結構)
    default_gears = {field: "無" for field in GEAR_FIELDS}
    default_gears["武器"] = "不滅聖劍 +15"
    default_gears["盔甲"] = "諸神黃昏鎧甲"
    
    return [
        {"角色名稱": "傲視群雄_X", "職業": ["狂戰士", "魔劍士"], "戰力": 1250000, "裝備": default_gears},
        {"角色名稱": "影之刃_凱", "職業": ["暗殺者"], "戰力": 1180000, "裝備": {field: "無" for field in GEAR_FIELDS}}
    ]

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初始化 Session State
if "guild_list" not in st.session_state:
    st.session_state.guild_list = load_data()

st.title("⚔️ 公會資訊自動化管理系統 v11 (16格裝備分類版)")

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
# 📝 權限 A：最高幹部專屬區 (包含 16 格裝備細項填寫)
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
        # 確保讀取時有完整的 16 格字典
        saved_gears = current_item.get("裝備", {})
        if isinstance(saved_gears, str):  # 兼容舊格式文字
            saved_gears = {"武器": saved_gears}
        default_gears = {field: saved_gears.get(field, "無") for field in GEAR_FIELDS}
        button_label = "💾 儲存修改資訊"
    else:
        default_name = ""
        default_jobs = []
        default_power = 0
        default_gears = {field: "無" for field in GEAR_FIELDS}
        button_label = "➕ 新增公會成員"

    with st.form(key="admin_member_form", clear_on_submit=True):
        # 基礎資訊
        st.markdown("##### 📌 基礎基本資訊")
        c1, c2, c3 = st.columns(3)
        with c1:
            name_input = st.text_input("角色名稱", value=default_name)
        with c2:
            jobs_input = st.multiselect("職業選項 (可多選)", options=JOB_OPTIONS, default=default_jobs)
        with c3:
            power_input = st.number_input("目前戰力", min_value=0, step=1000, value=default_power)
        
        st.write("---")
        st.markdown("##### 🛡️ 16 格核心裝備細項面板")
        
        # 將 16 格裝備切分成四個美觀的區塊填寫
        gear_inputs = {}
        
        st.markdown("**[1] 主戰裝備 & [2] 防具飾品**")
        g_col1, g_col2, g_col3, g_col4 = st.columns(4)
        with g_col1:
            gear_inputs["武器"] = st.text_input("武器", value=default_gears["武器"])
            gear_inputs["護肩"] = st.text_input("護肩", value=default_gears["護肩"])
        with g_col2:
            gear_inputs["副手"] = st.text_input("副手", value=default_gears["副手"])
            gear_inputs["手套"] = st.text_input("手套", value=default_gears["手套"])
        with g_col3:
            gear_inputs["盔甲"] = st.text_input("盔甲", value=default_gears["盔甲"])
            gear_inputs["鞋子"] = st.text_input("鞋子", value=default_gears["鞋子"])
        with g_col4:
            gear_inputs["頭盔"] = st.text_input("頭盔", value=default_gears["頭盔"])
            gear_inputs["披風"] = st.text_input("披風", value=default_gears["披風"])
            
        st.markdown("**[3] 首飾配件 & [4] 特殊寶物**")
        g_col5, g_col6, g_col7, g_col8 = st.columns(4)
        with g_col5:
            gear_inputs["項鍊"] = st.text_input("項鍊", value=default_gears["項鍊"])
            gear_inputs["徽章"] = st.text_input("徽章", value=default_gears["徽章"])
        with g_col6:
            gear_inputs["戒指1"] = st.text_input("戒指1", value=default_gears["戒指1"])
            gear_inputs["腰帶"] = st.text_input("腰帶", value=default_gears["腰帶"])
        with g_col7:
            gear_inputs["戒指2"] = st.text_input("戒指2", value=default_gears["戒指2"])
            gear_inputs["手鐲"] = st.text_input("手鐲", value=default_gears["手鐲"])
        with g_col8:
            gear_inputs["耳環"] = st.text_input("耳環", value=default_gears["耳環"])
            gear_inputs["護符"] = st.text_input("護符", value=default_gears["護符"])

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
# 📊 核心排行榜 (16 格裝備整合顯示與精準戰力遮蔽)
# ==========================================
st.subheader("📊 自動化整理：最新公會全裝備名單")

if st.session_state.guild_list:
    df = pd.DataFrame(st.session_state.guild_list)
    df = df.sort_values(by="戰力", ascending=False).reset_index(drop=True)
    df["真實排名"] = df.index + 1
    
    df["職業顯示"] = df["職業"].apply(lambda x: "、".join(x) if isinstance(x, list) else (x if pd.notna(x) else "未設定"))

    # 💡 戰力安全防護 (遮蔽前五名數字)
    if not is_admin:
        st.warning("🔒 戰力安全防護：目前權限下，系統已自動遮蔽公會前 5 名大佬的【戰力數字】與【真實排名】。")
        df["戰力(排名)"] = df.apply(
            lambda r: f"🔒 資訊保密" if r["真實排名"] <= 5 else f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1
        )
        df["排名顯示"] = df["真實排名"].apply(lambda x: "🎖️ 大佬" if x <= 5 else str(x))
    else:
        df["戰力(排名)"] = df.apply(lambda r: f"{int(r['戰力']):,} (#{r['真實排名']})", axis=1)
        df["排名顯示"] = df["真實排名"].astype(str)

    # 展開 16 格裝備字典，使其在表格中獨立成欄
    for field in GEAR_FIELDS:
        df[field] = df["裝備"].apply(lambda x: x.get(field, "無") if isinstance(x, dict) else "無")

    # 建立最終展示的大表格欄位
    display_cols = ["排名顯示", "角色名稱", "職業顯示", "戰力(排名)"] + GEAR_FIELDS
    display_df = df[display_cols]
    
    # 更改標頭名稱使其優雅
    rename_dict = {"排名顯示": "排名", "職業顯示": "職業", "戰力(排名)": "戰力(排名)"}
    display_df = display_df.rename(columns=rename_dict)
    
    # 🔍 全體職業篩選器
    filter_job = st.selectbox("🔍 依職業篩選現有排行榜 (可選填)：", ["顯示全部職業"] + JOB_OPTIONS)
    if filter_job != "顯示全部職業":
